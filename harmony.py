#vngame;charastudio;HarmonyAI

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

from harmony_modules import connector, common, backend, countenance, text_to_speech, speech_to_text

# Config
_config = None

# Init Handler - Special "Module"
_initHandler = None

# Define all used modules here
_connector = None
_backendModule = None
_countenanceModule = None
_ttsModule = None
_sttModule = None


# Event Types
EVENT_TYPE_INIT_CHARACTER = 'INIT_CHARACTER'


# HarmonyInitHandler
class HarmonyInitHandler(common.HarmonyClientModuleBase):
    def __init__(self, backend_connector, scene_config, game):
        # execute the base constructor
        common.HarmonyClientModuleBase.__init__(self, backend_connector=backend_connector)
        # Set config
        self.scene_config = scene_config
        self.game = game

    def handle_event(
            self,
            event  # HarmonyLinkEvent
    ):
        # Wait for Events required for initialization
        if event.event_type == EVENT_TYPE_INIT_CHARACTER:
            if event.status == common.EVENT_STATE_DONE:
                # Load Game Scene - this is a bit weird, however seems to work if copy+paste from koifighter
                self.game.load_scene(self.scene_config["scene"])
                self.game.set_timer(0.5, _load_scene_start)
            else:
                _error_abort(self.game, 'Harmony Link: Character Initialization failed.')

            # Disable this handler, it is not needed anymore after init
            self.deactivate()


# Chara - Internal representation for a chara actor
class Chara:
    def __init__(self, actor):
        self.actor = actor
        # Internal Handlers
        self.current_base_expression = None


# start - VNGE game start hook
def start(game):
    global _config, _connector, _initHandler

    # -------- some options we want to init for the engine ---------
    game.sceneDir = "harmony/"  # dir for Harmony Plugin scenes

    # game.btnNextText = "Next >>" # for localization and other purposes
    # game.isHideWindowDuringCameraAnimation = True # this setting hide game window during animation between cameras
    # game.isfAutoLipSync = True  # enable lip sync in framework

    # Actual Plugin Initialization
    # Read Config data from .ini file
    _config = _load_config()
    scene_config = dict(_config.items('Scene'))

    # Initialize Client modules
    _init_modules(_config)

    # Create Startup Init handler
    _initHandler = HarmonyInitHandler(backend_connector=_connector, scene_config=scene_config, game=game)
    _initHandler.activate()

    # Sleep 1 second to allow for the backend thread to connect to the websocket server
    time.sleep(1)

    # Initialize Character on Harmony Link
    init_event = common.HarmonyLinkEvent(
        event_id='start_listen',  # This is an arbitrary dummy ID to conform the Harmony Link API
        event_type=EVENT_TYPE_INIT_CHARACTER,
        status=common.EVENT_STATE_NEW,
        payload={
            'character_id': scene_config["character_id"]
        }
    )
    init_send_success = _connector.send_event(init_event)
    if init_send_success:
        print 'Harmony Link: Initializing character \'{0}\'...'.format(scene_config["character_id"])
    else:
        _error_abort(game, 'Harmony Link: Failed to sent character initialize Event.')
        return


def _load_scene_start(game):
    game.set_timer(1.0, _load_scene_start2)


def _load_scene_start2(game):
    real_start(game)


def real_start(game):
    global _config

    game.scenef_register_actorsprops()

    # Attach Character to Chara Actor
    scene_config = dict(_config.items('Scene'))
    chara_actor = game.scenef_get_actor(scene_config["character_id"])
    if chara_actor is None:
        _error_abort(game, 'Harmony Link: Actor for Chara "{0}" could not be loaded.'.format(scene_config["character_id"]))
        return

    _chara = Chara(actor=chara_actor)
    _chara.actor.set_mouth_open(0)
    # Update all modules with new chara actor
    _modules_update_chara(_chara)

    # Initialize Player controls.
    game.set_buttons(["Record Microphone", ">> End Harmony Link Demo >>"], [toggle_record_microphone, shutdown])
    # TODO: Hotkeys
    # TODO: Player face expression
    # TODO: Player movement & direct interaction


# _init_modules initializes all the interfaces and handlers needed by harmony_modules
def _init_modules(config):
    global _connector, _backendModule, _countenanceModule, _ttsModule, _sttModule

    # Init comms module for interfacing with external helper binaries
    _connector = connector.ConnectorEventHandler(endpoint=config.get('Connector', 'endpoint'), buffer_size=int(config.get('Connector', 'buffer_size')))
    _connector.start()

    # Init Backend Module
    _backendModule = backend.BackendHandler(backend_connector=_connector, backend_config=dict(config.items('Backend')))
    _backendModule.activate()

    # Init Module for Audio Recording / Streaming + Player Speech-To-Text
    _sttModule = speech_to_text.SpeechToTextHandler(backend_connector=_connector, stt_config=dict(config.items('STT')))

    # TODO: Init Module for Roleplay Options by the player -> Just very simple, no lewd stuff

    # TODO: Init Module for AI Roleplay to Animation -> Just very simple for now

    # Init Module for AI Expression Handling -> Just very simple for now
    _countenanceModule = countenance.CountenanceHandler(backend_connector=_connector, countenance_config=dict(config.items('Countenance')))
    _countenanceModule.activate()

    # Init Module for AI Voice Streaming + Audio-2-LipSync
    _ttsModule = text_to_speech.TextToSpeechHandler(backend_connector=_connector, tts_config=dict(config.items('TTS')))
    _ttsModule.activate()

    return None


def _modules_update_chara(chara):
    global _backendModule, _countenanceModule, _ttsModule, _sttModule

    _backendModule.update_chara(chara)
    _countenanceModule.update_chara(chara)
    _ttsModule.update_chara(chara)
    _sttModule.update_chara(chara)


def _shutdown_modules():
    global _connector

    _connector.stop()


def _error_abort(game, error):
    print error
    shutdown(game)


def _load_config():
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
    # Shutdown Modules
    _shutdown_modules()

    game.set_text("s", "Harmony Link Plugin for VNGE successfully stopped.")
    game.set_buttons(["Return to main screen >>"], game.return_to_start_screen_clear())


def toggle_record_microphone(game):
    global _sttModule

    if _sttModule.is_recording_microphone:
        recording_aborted = _sttModule.stop_listen()
        if not recording_aborted:
            print 'Harmony Link Plugin for VNGE: Failed to record from microphone.'
            return
        # Update Buttons
        game.set_buttons(["Record Microphone", ">> End Harmony Link Demo >>"], [toggle_record_microphone, shutdown])

    else:
        recording_started = _sttModule.start_listen()
        if not recording_started:
            print 'Harmony Link Plugin for VNGE: Failed to record from microphone.'
            return
        # Update Buttons
        game.set_buttons(["Stop Recording", ">> End Harmony Link Demo >>"], [toggle_record_microphone, shutdown])
