#vngame;all;HarmonyAI

# Harmony Link Plugin for VNGE
# (c) 2023 RuntimeRacer (runtimeracer@gmail.com)
#
# This plugin aims at integrating fully AI controlled characters into IllusionSoft Games utilizing VNGE.
# It is interfacing between actions in the game and the actual conversation between an user and their AI Companion.
#
# For more Info on the project goals, see README.md
#

import ConfigParser
import os
import time
import threading

from vngameengine import get_engine_id2

from harmony_modules import connector, common, backend, countenance, text_to_speech, speech_to_text, controls, movement, \
    perception
from harmony_modules.common import EVENT_TYPE_INIT_ENTITY

# Config
_config = None

# Object, character & user controllers
_user_controlled_entity_id = None
_active_entities = {}
_registered_props = {}

# List of ready characters - this is used to synchronize characters finished initialization
_syncLock = threading.Lock()
_ready_entities = []
_failed_entities = []

# static actors in the scene, which may be relevant for movement or interactions
_static_actors = {}


# EntityInitHandler
class EntityInitHandler(common.HarmonyClientModuleBase):
    global _active_entities, _ready_entities, _failed_entities, _syncLock

    def __init__(self, entity_controller, entity_id, game):
        # execute the base constructor
        common.HarmonyClientModuleBase.__init__(self, entity_controller=entity_controller)
        # Set config
        self.entity_id = entity_id
        self.game = game

    def handle_event(
            self,
            event  # HarmonyLinkEvent
    ):
        # Wait for Events required for initialization
        if event.event_type == EVENT_TYPE_INIT_ENTITY:
            # Acquire lock to avoid concurrency issues
            _syncLock.acquire()
            if event.status == common.EVENT_STATE_DONE:
                _ready_entities.append(self.entity_id)
            else:
                _failed_entities.append(self.entity_id)

            # Check for init done condition
            self.check_init_done()
            # Release lock
            _syncLock.release()
            # Disable this handler, it is not needed anymore after init
            self.deactivate()

    def check_init_done(self):
        if len(_ready_entities) + len(_failed_entities) == len(_active_entities):
            if len(_failed_entities) == 0:
                # Load Game Scene - this is a bit weird, however seems to work if copy+paste from koifighter
                scene_config = self.game.scenedata.scene_config
                if scene_config["scene"] is not None:
                    self.game.load_scene(scene_config["scene"])
                    self.game.set_timer(0.5, _load_scene_start)
                else:
                    real_start(self.game)
            else:
                _error_abort(self.game, 'Harmony Link: Entity Initialization failed.')


# Chara - Internal representation for a chara actor
class Chara:
    def __init__(self, actor):
        self.actor = actor
        # Internal Handlers
        self.current_base_expression = None


class EntityController:  # TODO: Refactor this to use inheritance from base class with ActorEntity

    def __init__(self, entity_id, game, config):
        # Flow Control
        self.is_active = False
        # Important reference
        self.entity_id = entity_id
        self.game = game
        self.config = config
        self.chara = None
        # Mandatory Modules
        self.initHandler = None
        self.connector = None
        # Feature Modules
        self.backendModule = None
        self.countenanceModule = None
        self.ttsModule = None
        self.sttModule = None
        self.movementModule = None
        self.perceptionModule = None
        self.controlsModule = None

    def activate(self):
        if self.is_active:
            return

        # Set active
        print 'Starting ActorEntityController for entity \'{0}\'...'.format(self.entity_id)
        self.is_active = True

        # Initialize Character on Harmony Link
        init_event = common.HarmonyLinkEvent(
            event_id='init_entity',  # This is an arbitrary dummy ID to conform the Harmony Link API
            event_type=EVENT_TYPE_INIT_ENTITY,
            status=common.EVENT_STATE_NEW,
            payload={
                'entity_id': self.entity_id
            }
        )
        init_send_success = self.connector.send_event(init_event)
        if init_send_success:
            print 'Harmony Link: Initializing entity \'{0}\'...'.format(self.entity_id)
        else:
            raise RuntimeError('Harmony Link: Failed to sent entity initialize Event for entity \'{0}\'.'.format(self.entity_id))

    def is_active(self):
        return self.is_active

    # _init_modules initializes all the interfaces and handlers needed by harmony_modules
    def init_modules(self):

        # Init comms module for interfacing with external helper binaries
        self.connector = connector.ConnectorEventHandler(
            ws_endpoint=self.config.get('Connector', 'ws_endpoint'),
            ws_buffer_size=int(self.config.get('Connector', 'ws_buffer_size')),
            http_endpoint=self.config.get('Connector', 'http_endpoint'),
            http_listen_port=self.config.get('Connector', 'http_listen_port'),
            shutdown_func=shutdown,  # -> An Error with a single character should cause the whole plugin to shut down.
            game=self.game
        )
        self.connector.start()

        # Init Backend Module
        self.backendModule = backend.BackendHandler(
            entity_controller=self,
            backend_config=dict(self.config.items('Backend'))
        )
        self.backendModule.activate()

        # Init Module for Audio Recording / Streaming + Player Speech-To-Text
        self.sttModule = speech_to_text.SpeechToTextHandler(
            entity_controller=self,
            stt_config=dict(self.config.items('STT'))
        )

        # TODO: Init Module for Roleplay Options by the player -> Just very simple, no lewd stuff

        # Init Module for AI Expression Handling
        self.countenanceModule = countenance.CountenanceHandler(
            entity_controller=self,
            countenance_config=dict(self.config.items('Countenance'))
        )
        self.countenanceModule.activate()

        # Init Module for AI Voice Streaming + Audio-2-LipSync
        self.ttsModule = text_to_speech.TextToSpeechHandler(
            entity_controller=self,
            tts_config=dict(self.config.items('TTS'))
        )
        self.ttsModule.activate()

        # Init Module for AI Roleplay to Animation
        self.movementModule = movement.MovementHandler(
            entity_controller=self,
            movement_config=dict(self.config.items('Movement'))
        )
        self.movementModule.activate()

        # Init Module for AI Perception Handling
        self.perceptionModule = perception.PerceptionHandler(
            entity_controller=self,
            perception_config=dict(self.config.items('Perception'))
        )
        self.perceptionModule.activate()

        # Init User Controls Module
        self.controlsModule = controls.ControlsHandler(
            entity_controller=self,
            game=self.game,
            shutdown_func=shutdown,
            controls_keymap_config=dict(self.config.items('Controls.Keymap'))
        )

        return None

    def create_startup_handler(self):
        self.initHandler = EntityInitHandler(
            entity_controller=self,
            entity_id=self.entity_id,
            game=self.game
        )
        self.initHandler.activate()

    def update_chara(self, chara):
        self.chara = chara
        # Update in submodules
        self.backendModule.update_chara(self.chara)
        self.countenanceModule.update_chara(self.chara)
        self.ttsModule.update_chara(self.chara)
        self.sttModule.update_chara(self.chara)
        self.movementModule.update_chara(self.chara)

    def shutdown_modules(self):
        self.backendModule.deactivate()
        self.sttModule.deactivate()
        self.ttsModule.deactivate()
        self.countenanceModule.deactivate()
        self.movementModule.deactivate()
        self.controlsModule.deactivate()

        self.connector.stop()


# start - VNGE game start hook
def start(game):
    global _config

    # -------- some options we want to init for the engine ---------
    # Determine Game Engine ID
    # this is the sub folder in harmony where Chara studio will look for scenes for the game
    game.sceneDir = "harmony/{0}/".format(get_engine_id2())  # dir for Harmony Plugin scenes
    print("Initializing VNGE-Plugin for Harmony Link with scene dir: " + game.sceneDir)

    # game.btnNextText = "Next >>" # for localization and other purposes
    # game.isHideWindowDuringCameraAnimation = True # this setting hide game window during animation between cameras
    # game.isfAutoLipSync = True  # enable lip sync in framework

    # Actual Plugin Initialization
    # Read Config data from .ini file
    _config = load_config()
    game.scenedata.scene_config = dict(_config.items('Scene'))

    # select a scene or load scene from ini
    if len(game.scenedata.scene_config["scene"]) == 0:
        start_scene_select(game)
    else:
        start_harmony_ai(game)


# scene selector by @countd360 - Thanks for the support
def start_scene_select(game):
    # helper
    def select_scene(game, sfile):
        game.set_text("s", "")
        game.set_buttons([], [])
        game.scenedata.scene_config["scene"] = sfile
        start_harmony_ai(game)

    # select scene from folder
    harmony_scene_home = os.path.join(game.get_scene_dir(), "harmony", get_engine_id2())
    harmony_scene_names = ["<color=#00ffff>>> Skip load and continue with current scene <<</color>"]
    harmony_scene_actions = [(select_scene, None)]
    for sfile in os.listdir(harmony_scene_home):
        if sfile.lower().endswith(".png"):
            harmony_scene_names.append("<color=#00ff00>" + os.path.splitext(sfile)[0] + "</color>")
            harmony_scene_actions.append((select_scene, sfile))
    harmony_scene_names.append("<color=#ff0000>>> Cancel and Quit <<</color>")
    harmony_scene_actions.append([game.return_to_start_screen_clear])
    game.set_text("s", "Choose a harmony scene:")
    game.set_buttons(harmony_scene_names, harmony_scene_actions)


def start_harmony_ai(game):
    global _config, _user_controlled_entity_id, _active_entities
    scene_config = game.scenedata.scene_config

    # Determine user entities to be controlled
    if "user_entity_id" not in scene_config or len(scene_config["user_entity_id"]) == 0:
        _error_abort(game, 'Harmony Plugin: User entity id is invalid.')
        return

    # Determine character entities to be controlled
    if "character_entity_id" not in scene_config or len(scene_config["character_entity_id"]) == 0:
        _error_abort(game, 'Harmony Plugin: Character entity id/list is invalid.')
        return

    # Setup user entity
    user_entity_id = scene_config["user_entity_id"].strip()
    controller = EntityController(entity_id=user_entity_id, game=game, config=_config)
    # Initialize Client modules
    controller.init_modules()
    # Create Startup Init handler
    controller.create_startup_handler()
    # Add to character list
    _active_entities[user_entity_id] = controller
    _user_controlled_entity_id = user_entity_id

    # Setup character entities
    character_list = scene_config["character_entity_id"].split(",")
    for entity_id in character_list:
        # Create entity controller for characters
        entity_id = entity_id.strip()
        controller = EntityController(entity_id=entity_id, game=game, config=_config)
        # Initialize Client modules
        controller.init_modules()
        # Create Startup Init handler
        controller.create_startup_handler()
        # Add to character list
        _active_entities[entity_id] = controller

    # Warmup time to allow for the backend threads to connect to the websocket server
    warmup_time = int(_config.get('Harmony', 'start_warmup_time'))
    time.sleep(warmup_time)

    # Initialize Entities on Harmony Link
    for entity_id, controller in _active_entities.items():
        try:
            controller.activate()
        except RuntimeError as e:
            _error_abort(game, e.message)
            return


def _load_scene_start(game):
    game.set_timer(1.0, _load_scene_start2)


def _load_scene_start2(game):
    real_start(game)


def real_start(game):
    global _config, _user_controlled_entity_id, _active_entities, _registered_props

    game.scenedata.scene_config = dict(_config.items('Scene'))
    game.scenef_register_actorsprops()

    # Setup object props if they are defined
    props_list = game.scenef_get_all_props()
    for prop_id in props_list:
        prop_object = game.scenef_get_prop(prop_id)
        if prop_object is None:
            _error_abort(game, 'Harmony Link: Object for Prop "{0}" could not be loaded.'.format(prop_id))
            return
        # Add to list of object props
        _registered_props[prop_id] = prop_id

    # Link Props & Entities within game object
    game.scenedata.registered_props = _registered_props
    game.scenedata.active_entities = _active_entities
    game.scenedata.user_controlled_entity_id = _user_controlled_entity_id

    # Link Chara Actor in scene with Character controller
    for entity_id, controller in _active_entities.items():
        # Get list of character and user entities
        character_list = game.scenedata.scene_config["character_entity_id"].split(",")

        # Try to find actor for entity
        chara_actor = game.scenef_get_actor(entity_id)
        if chara_actor is None and entity_id in character_list:
            _error_abort(game, 'Harmony Link: Chara Actor for Entity "{0}" could not be loaded.'.format(entity_id))
            return
        elif chara_actor is not None:
            chara = Chara(actor=chara_actor)
            chara.actor.set_mouth_open(0)
            # Update all controller modules with new chara actor
            controller.update_chara(chara)

        # Initialize controls module and STT module if it's the user entity
        if entity_id == _user_controlled_entity_id:
            controller.controlsModule.activate()
            controller.sttModule.activate()

        # Inform Harmony Link that the scene finished loading for this Entity
        environment_loaded_event = common.HarmonyLinkEvent(
            event_id='environment_loaded',
            event_type=common.EVENT_TYPE_ENVIRONMENT_LOADED,
            status=common.EVENT_STATE_NEW,
            payload={}
        )
        send_success = controller.connector.send_event(environment_loaded_event)
        if send_success:
            print('Harmony Link: Scene Data finished loading for entity "{0}"'.format(entity_id))
        else:
            print('Harmony Link: Failed to transmit scene loading finished for entity "{0}"'.format(entity_id))


def _error_abort(game, error):
    print ("**** Error aborted ****\n>>" + error)
    shutdown(game)


def load_config():
    # read from .ini file
    config = ConfigParser.SafeConfigParser()
    config_path = os.path.splitext(__file__)[0] + '.ini'
    config.read(config_path)
    return config


def _load_scene(game, param):
    game.fake_lipsync_stop()  # required by framework - stop lipsynd if we has it
    game.load_scene(param)
    game.set_timer(0.2, _reg_framework)  # required by framework - we need actors and props after scene load


def _reg_framework(game):
    game.scenef_register_actorsprops()


def _to_cam(game, camera_id):
    # instant move to camera
    game.to_camera(camera_id)


def _to_cam_animated(game, camera_id, time=3, move_style="fast-slow3"):
    # animated move to camera - 3 seconds, with-fast-slow movement style
    game.anim_to_camera_num(time, camera_id, move_style)
    # game.anim_to_camera_num(3, param, {'style':"linear",'zooming_in_target_camera':6}) # cool camera move with zoom-out - zoom-in


def shutdown(game):
    global _active_entities

    # Shutdown all Characters
    for controller in _active_entities.values():
        controller.shutdown_modules()

    game.set_text("s", "Harmony Link Plugin for VNGE successfully stopped.")
    game.set_buttons(["Return to main screen >>"], [[game.return_to_start_screen_clear]])

