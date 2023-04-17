#vngame;charastudio;Koikaji

# Koikaji Prototype main script
# (c) 2023 RuntimeRacer (runtimeracer@gmail.com)
#
# This project aims at integrating Kajis from Kajiwoto into Koikatsu, by interfacing between actions in the game
# and the actual conversation between an user and their Kaji.
#
# For more Info on the project goals, see README.md
#

import ConfigParser
import os
import time

from koikaji_modules import backend, kajiwoto, countenance, text_to_speech, speech_to_text

# Config
_config = None

# Define all used modules here
_backendModule = None
_kajiwotoModule = None
_countenanceModule = None
_ttsModule = None
_sttModule = None


# Chara - Internal representation for a chara actor
class Chara:
    def __init__(self, actor, kaji_id=""):
        self.actor = actor
        self.kaji_id = kaji_id
        # Internal Handlers
        self.face_expression = None


# start - VNGE game start hook
def start(game):
    global _config, _backendModule, _kajiwotoModule

    # -------- some options we want to init for the engine ---------
    game.sceneDir = "koikaji/"  # dir for Koikaji scenes

    # game.btnNextText = "Next >>" # for localization and other purposes
    # game.isHideWindowDuringCameraAnimation = True # this setting hide game window during animation between cameras
    # game.isfAutoLipSync = True  # enable lip sync in framework

    # Actual Koikaji Initialization
    # Read Kajiwoto Credentials, Target Kaji and everything else needed from .ini file
    _config = _load_config()
    scene_config = dict(_config.items('Scene'))

    # Initialize Koikaji modules
    _init_modules(_config)

    # Login to Kajiwoto
    login_success = _kajiwotoModule.login()
    if not login_success:
        _error_abort(game, 'Koikaji: Failed to login to Kajiwoto.')
        return

    # Select Kaji Room from settings by ID -> Needs to be a single, private Kaji for now
    room_selected = _kajiwotoModule.select_room()
    if not room_selected:
        _error_abort(game, 'Koikaji: Failed to select Kaji room.')
        return

    # Connect to Chat of the Kaji. Backend will send info on state, mood and last conversation
    room_joined = _kajiwotoModule.join_room()
    if not room_joined:
        _error_abort(game, 'Koikaji: Failed to join Kaji room.')
        return

    # Load Game Scene - this is a bit weird, however seems to work if copy+paste from koifighter
    game.load_scene_immediately(scene_config["scene"])
    game.set_timer(0.5, _load_scene_start)


def _load_scene_start(game):
    game.set_timer(1.0, _load_scene_start2)


def _load_scene_start2(game):
    real_start(game)


def real_start(game):
    global _config

    game.scenef_register_actorsprops()

    # Attach Kaji to Chara Actor
    kaji_actor = game.scenef_get_actor("kaji")
    if kaji_actor is None:
        _error_abort(game, 'Koikaji: Actor for Chara "kaji" could not be loaded.')
        return

    kaji_chara = Chara(actor=kaji_actor, kaji_id=_kajiwotoModule.kaji.room_id)
    kaji_chara.actor.set_mouth_open(0)

    _modules_update_chara(_kajiwotoModule.kaji.room_id, kaji_chara)

    # Initialize Player controls.
    game.set_buttons(["Record Microphone", ">> End Koikaji Demo >>"], [toggle_record_microphone, shutdown])
    # TODO: Player face expression
    # TODO: Player movement & direct interaction


# _init_modules initializes all the interfaces and handlers needed by koikaji_modules
def _init_modules(config):
    global _backendModule, _kajiwotoModule, _countenanceModule, _ttsModule, _sttModule

    # Init comms module for interfacing with external helper binaries
    _backendModule = backend.KoikajiBackendHandler(endpoint=config.get('Backend', 'endpoint'))
    _backendModule.start()

    # Init Kajiwoto Module
    _kajiwotoModule = kajiwoto.KajiwotoHandler(backend_handler=_backendModule, kajiwoto_config=dict(config.items('Kajiwoto')))
    _kajiwotoModule.activate()

    # Init Module for Audio Recording / Streaming + Player Speech-To-Text
    _sttModule = speech_to_text.SpeechToTextHandler(backend_handler=_backendModule, stt_config=dict(config.items('STT')))

    # TODO: Init Module for Roleplay Options by the player -> Just very simple, no lewd stuff

    # TODO: Init Module for Kaji Roleplay to Animation -> Just very simple for now

    # Init Module for Kaji Expression Handling -> Just very simple for now
    _countenanceModule = countenance.CountenanceHandler(backend_handler=_backendModule, countenance_config=dict(config.items('Countenance')))
    _countenanceModule.activate()

    # TODO: Init Module for Kaji Response Handling: RP vs Speech -> Should literally just be a regex (currently handled async)

    # Init Module for Kaji Voice Streaming + Audio-2-LipSync
    _ttsModule = text_to_speech.TextToSpeechHandler(backend_handler=_backendModule, tts_config=dict(config.items('TTS')))
    _ttsModule.activate()

    return None


def _modules_update_chara(chara_id, chara):
    global _kajiwotoModule, _countenanceModule, _ttsModule, _sttModule

    _kajiwotoModule.update_chara(chara_id, chara)
    _countenanceModule.update_chara(chara_id, chara)
    _ttsModule.update_chara(chara_id, chara)
    _sttModule.update_chara(chara_id, chara)


def _shutdown_modules():
    global _backendModule

    _backendModule.stop()


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

    game.set_text("s", "Koikaji Module successfully stopped.")
    game.set_buttons(["Return to main screen >>"], game.return_to_start_screen_clear())


def toggle_record_microphone(game):
    global _sttModule

    if _sttModule.is_recording_microphone:
        recording_aborted = _sttModule.stop_listen("")
        if not recording_aborted:
            print 'Koikaji: Failed to record from microphone.'
            return
        # Update Buttons
        game.set_buttons(["Record Microphone", ">> End Koikaji Demo >>"], [toggle_record_microphone, shutdown])

    else:
        recording_started = _sttModule.start_listen("")
        if not recording_started:
            print 'Koikaji: Failed to record from microphone.'
            return
        # Update Buttons
        game.set_buttons(["Stop Recording", ">> End Koikaji Demo >>"], [toggle_record_microphone, shutdown])
