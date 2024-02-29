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

from harmony_modules import connector, common, backend, countenance, text_to_speech, speech_to_text, controls, movement

# Config
_config = None

# Character controllers
_active_characters = {}
# List of ready characters - this is used to synchronize characters finished initialization
_syncLock = threading.Lock()
_ready_characters = []
_failed_characters = []

# Main Connector & Controls Module
_connector = None
_controlsModule = None
_sttModule = None

# Event Types
EVENT_TYPE_INIT_CHARACTER = 'INIT_CHARACTER'


# HarmonyInitHandler
class HarmonyInitHandler(common.HarmonyClientModuleBase):
    global _active_characters, _ready_characters, _failed_characters, _syncLock

    def __init__(self, backend_connector, character_id, scene_config, game):
        # execute the base constructor
        common.HarmonyClientModuleBase.__init__(self, backend_connector=backend_connector)
        # Set config
        self.character_id = character_id
        self.scene_config = scene_config
        self.game = game

    def handle_event(
            self,
            event  # HarmonyLinkEvent
    ):
        # Wait for Events required for initialization
        if event.event_type == EVENT_TYPE_INIT_CHARACTER:
            # Acquire lock to avoid concurrency issues
            _syncLock.acquire()
            if event.status == common.EVENT_STATE_DONE:
                _ready_characters.append(self.character_id)
            else:
                _failed_characters.append(self.character_id)

            # Check for init done condition
            self.check_init_done()
            # Release lock
            _syncLock.release()
            # Disable this handler, it is not needed anymore after init
            self.deactivate()

    def check_init_done(self):
        if len(_ready_characters) + len(_failed_characters) == len(_active_characters):
            if len(_failed_characters) == 0:
                # Load Game Scene - this is a bit weird, however seems to work if copy+paste from koifighter
                if self.scene_config["scene"] is not None:
                    self.game.load_scene(self.scene_config["scene"])
                    self.game.set_timer(0.5, _load_scene_start)
                else:
                    real_start(self.game)
            else:
                _error_abort(self.game, 'Harmony Link: Character Initialization failed.')


# Chara - Internal representation for a chara actor
class Chara:
    def __init__(self, actor):
        self.actor = actor
        # Internal Handlers
        self.current_base_expression = None


class CharacterController:
    global _config

    def __init__(self, character_id, game, config):
        # Flow Control
        self.is_active = False
        # Important reference
        self.character_id = character_id
        self.game = game
        self.config = config
        self.chara = None
        # Mandatory Modules
        self.initHandler = None
        self.connector = None
        # Character Feature Modules
        self.backendModule = None
        self.countenanceModule = None
        self.ttsModule = None
        # self.sttModule = None
        self.movementModule = None

    def activate(self):
        if self.is_active:
            return

        # Set active
        print 'Starting CharacterController for character \'{0}\'...'
        self.is_active = True

        # Initialize Character on Harmony Link
        init_event = common.HarmonyLinkEvent(
            event_id='init_character',  # This is an arbitrary dummy ID to conform the Harmony Link API
            event_type=EVENT_TYPE_INIT_CHARACTER,
            status=common.EVENT_STATE_NEW,
            payload={
                'character_id': self.character_id
            }
        )
        init_send_success = _connector.send_event(init_event)
        if init_send_success:
            print ('Harmony Link: Initializing character \'{0}\'...'.format(self.character_id))
        else:
            raise RuntimeError('Harmony Link: Failed to sent character initialize Event for character \'{0}\'.'.format(self.character_id))

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
            backend_connector=_connector,
            backend_config=dict(self.config.items('Backend'))
        )
        self.backendModule.activate()

        # # Init Module for Audio Recording / Streaming + Player Speech-To-Text
        # self.sttModule = speech_to_text.SpeechToTextHandler(
        #     backend_connector=_connector,
        #     stt_config=dict(self.config.items('STT'))
        # )

        # TODO: Init Module for Roleplay Options by the player -> Just very simple, no lewd stuff

        # Init Module for AI Roleplay to Animation -> Just very simple for now
        self.movementModule = movement.MovementHandler(
            backend_connector=_connector,
            movement_config=dict(self.config.items('Movement'))
        )
        self.movementModule.activate()

        # Init Module for AI Expression Handling -> Just very simple for now
        self.countenanceModule = countenance.CountenanceHandler(
            backend_connector=_connector,
            countenance_config=dict(self.config.items('Countenance'))
        )
        self.countenanceModule.activate()

        # Init Module for AI Voice Streaming + Audio-2-LipSync
        self.ttsModule = text_to_speech.TextToSpeechHandler(
            backend_connector=_connector,
            tts_config=dict(self.config.items('TTS'))
        )
        self.ttsModule.activate()

        return None

    def create_startup_handler(self):
        scene_config = self.game.scenedata.scene_config
        self.initHandler = HarmonyInitHandler(
            backend_connector=self.connector,
            character_id=self.character_id,
            scene_config=scene_config,
            game=self.game
        )
        self.initHandler.activate()

    def update_chara(self, chara):
        self.chara = chara
        # Update in submodules
        self.backendModule.update_chara(self.chara)
        self.countenanceModule.update_chara(self.chara)
        self.ttsModule.update_chara(self.chara)
        # self.sttModule.update_chara(self.chara)
        self.movementModule.update_chara(self.chara)

    def shutdown_modules(self):
        self.backendModule.deactivate()
        # self.sttModule.deactivate()
        self.ttsModule.deactivate()
        self.countenanceModule.deactivate()
        self.movementModule.deactivate()

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
    global _config, _connector, _active_characters
    scene_config = game.scenedata.scene_config

    # Initialize global modules who need to operate independent from characters
    _init_base_modules(_config, game)

    # Determine characters to be controlled
    if "character_id" not in scene_config or type(scene_config["character_id"]) != "string":
        _error_abort(game, 'Harmony Plugin: Character list invalid.')
    character_list = scene_config["character_id"].split(",")
    for character_id in character_list:
        # Create character controller
        controller = CharacterController(character_id=character_id, game=game, config=_config)
        # Initialize Client modules
        controller.init_modules()
        # Create Startup Init handler
        controller.create_startup_handler()
        # Add to character list
        _active_characters[character_id] = controller

    # Sleep 1 second to allow for the backend threads to connect to the websocket server
    time.sleep(1)

    # Initialize Characters on Harmony Link
    for character_id, controller in _active_characters.items():
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
    global _config, _controlsModule, _active_characters

    game.scenef_register_actorsprops()

    # Link Chara Actor in scene with Character controller
    for character_id, controller in _active_characters.items():
        chara_actor = game.scenef_get_actor(character_id)
        if chara_actor is None:
            _error_abort(game, 'Harmony Link: Actor for Chara "{0}" could not be loaded.'.format(character_id))
            return

        chara = Chara(actor=chara_actor)
        chara.actor.set_mouth_open(0)
        # Update all controller modules with new chara actor
        controller.update_chara(chara)

    # Initialize Player controls.
    _controlsModule.setup_game_controls(game, shutdown, _sttModule)


# _init_modules initializes all the interfaces and handlers needed by harmony_modules
def _init_base_modules(config, game):
    global _connector, _controlsModule, _sttModule

    # Init comms module for interfacing with external helper binaries
    _connector = connector.ConnectorEventHandler(
        ws_endpoint=config.get('Connector', 'ws_endpoint'),
        ws_buffer_size=int(config.get('Connector', 'ws_buffer_size')),
        http_endpoint=config.get('Connector', 'http_endpoint'),
        http_listen_port=config.get('Connector', 'http_listen_port'),
        shutdown_func=shutdown,
        game=game
    )
    _connector.start()

    # Init Module for Audio Recording / Streaming + Player Speech-To-Text
    _sttModule = speech_to_text.SpeechToTextHandler(
        backend_connector=_connector,
        stt_config=dict(config.items('STT'))
    )

    # Init Player Controls Module
    _controlsModule = controls.ControlsHandler(
        backend_connector=_connector,
        controls_keymap_config=dict(config.items('Controls.Keymap'))
    )
    _controlsModule.activate()

    return None


def _shutdown_base_modules():
    global _connector, _controlsModule
    _controlsModule.deactivate()
    _connector.stop()


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
    global _active_characters

    # Shutdown all Characters
    for controller in _active_characters:
        controller.shutdown_modules()

    # Shutdown base Modules
    _shutdown_base_modules()

    game.set_text("s", "Harmony Link Plugin for VNGE successfully stopped.")
    game.set_buttons(["Return to main screen >>"], [[game.return_to_start_screen_clear]])

