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

from koikaji_modules import backend, kajiwoto

# Define all used modules here
_backendModule = None
_kajiwotoModule = None


# start - VNGE game start hook
def start(game):
    global _backendModule, _kajiwotoModule

    # -------- some options we want to init for the engine ---------
    game.sceneDir = "koikaji/"  # dir for Koikaji scenes

    # game.btnNextText = "Next >>" # for localization and other purposes
    # game.isHideWindowDuringCameraAnimation = True # this setting hide game window during animation between cameras
    # game.isfAutoLipSync = True  # enable lip sync in framework

    # Actual Koikaji Initialization
    # Read Kajiwoto Credentials, Target Kaji and everything else needed from .ini file
    config = _load_config()

    # Initialize Koikaji modules
    _init_modules(config)

    # Login to Kajiwoto
    login_success = _kajiwotoModule.login()
    if not login_success:
        return

    # Fetch Kaji Details -> Needs to be a single, private Kaji at the beginning
    kaji = _kajiwotoModule.get_kaji_data()

    # TODO: Connect to Chat of the Kaji. Fetch Info on state, mood and last conversation

    # TODO: Initialize Player controls.

    # FIXME: Debug code
    game.load_scene("main.png")

    game.set_buttons(["End Koikaji Demo >>"], [shutdown])

    # ---------------------------
    # We can define additional characters (other than "s", system)
    # first param is an character ID, second - header text color (RRGGBB), third - name 
    # ---------------------------
    # game.register_char("player", "aa5555", kajiwoto.username)
    # game.register_char("kaji", "55aa55", kajiwoto.kajiname)

    # init face expressions
    # import vnlibfaceexpressions
    # vnlibfaceexpressions.init_faceexpressions(game)

    # ---------------------------
    # If we want to set a number of strict-story-line texts with "Next >" buttons (with no special choices), we can use construct "texts_next"
    # in array (1 param)
    # - 1 param - char ID
    # - 2 param - text
    # - 3 param (if exist) - function to call during text show
    # - 4 param (if exist) - function param
    # last param (2)
    # - function to move at end
    # ---------------------------
    # game.texts_next([
    #     ["me", "Hi! It's me.\nSo, as you can see, I do nothing in the college.", _load_scene, "scene1lipsync.png"],
    #     # loading scene
    #     ["me//angry_whatyousay", "Hey, what's going on?...."],
    #     ["teacher", "Is everybody here?\nI want to introduce our new transfer student...", _to_cam, 2],
    #     # move cam to teacher
    #     ["teacher//angry_whatyousay", "...Kawashima Morito"],
    #     ["teacher//normal", "Please, Morito, tell something to everyone.", _to_cam_animated, 3],
    #     # animated move cam to morito
    #     ["main", "Hi! My name is Morito, I'm a new transfer student from Tokyo."],
    #     ["main", "!...(what to say)..."],  # ! begins the silent construction
    #     ["main", "...m-m...I like cats..."],
    #     ["main", "...m-m...Glad to see everyone!"],
    #     ["me", "So, we have new cute transfer student. It may be interested... May be spy on she on break?", _to_cam,
    #      5],
    #     ["me", "..wait until break, and then..."],
    #     ["me", "..investigate the female toilet >"],
    #     ["me", "Wow... and this is so elegant and strict Morito-chan?", _load_scene, "scene2.png"]
    # ], shutdown)


# _init_modules initializes all the interfaces and handlers needed by koikaji_modules
def _init_modules(config):
    global _backendModule, _kajiwotoModule

    # Init comms module for interfacing with external helper binaries
    _backendModule = backend.KoikajiBackendHandler(endpoint=config.get('Backend', 'endpoint'))
    _backendModule.start()

    # Init Kajiwoto Module
    _kajiwotoModule = kajiwoto.KajiwotoHandler(backend_handler=_backendModule, kajiwoto_config=dict(config.items('Kajiwoto')))
    _kajiwotoModule.activate()

    # TODO: Init Module for Audio Recording / Streaming + Player Speech-To-Text

    # TODO: Init Module for Roleplay Options by the player -> Just very simple, no lew stuff

    # TODO: Init Module for Kaji Roleplay to Animation -> Just very simple for now

    # TODO: Init Module for Kaji Expression Handling -> Just very simple for now

    # TODO: Init Module for Kaji Response Handling: RP vs Speech -> Should literally just be a regex

    # TODO: Init Module for Kaji Voice Streaming + Audio-2-LipSync

    return None


def _shutdown_modules():
    global _backendModule, _kajiwotoModule

    _backendModule.stop()


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
