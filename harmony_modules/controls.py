# Harmony Link Plugin for VNGE
# (c) 2023 RuntimeRacer (runtimeracer@gmail.com)
#
# User Controls Module

# Import Backend base Module
from harmony_modules.common import *

# VNGE
from vngameengine import parseKeyCode
import unity_util
from UnityEngine import Input, KeyCode

import time


# ControlsHandler - module main class
class ControlsHandler(HarmonyClientModuleBase):
    def __init__(self, backend_connector, controls_keymap_config):
        # execute the base constructor
        HarmonyClientModuleBase.__init__(self, backend_connector=backend_connector)
        # Set config
        self.keymap_config = controls_keymap_config
        # Game Object reference
        self.game = None
        self.shutdown_func = None
        # Module References
        self.stt_module = None
        # Keymap
        self.controls_keymap = {}
        self.controls_executing = {}

    def setup_game_controls(self, game, shutdown_func, stt_module):
        # Link hard Game references
        self.game = game
        self.shutdown_func = shutdown_func
        # Link other modules
        self.stt_module = stt_module

        # Set Input Update Hooks to allowed
        self.game.event_reg_listener("update", self.on_input_update)

        # Basic Controls
        self.game.set_buttons(
            ["Record Microphone", ">> End Harmony Link Demo >>"],
            [self.toggle_record_microphone, self.shutdown_func]
        )

        # Hotkeys
        self.controls_keymap = {
            "toggle_microphone": {
                "key_codes": parseKeyCode(self.keymap_config["toggle_microphone"]),
                "call_functions": [self.toggle_record_microphone],
                "mode": "toggle"
            }
        }

        # TODO: Player face expression
        # TODO: Player movement & direct interaction

    def on_input_update(self, game, event_id, u_param):
        # Meta Keys
        ctrl, alt, shift = unity_util.metakey_state()
        # Process Keymap
        for action, rules in self.controls_keymap.items():
            # print commands, param
            (_, i_key, i_ctrl, i_alt, i_shift) = rules["key_codes"]
            if Input.GetKey(i_key):
                # Simple cooldown of 100ms, if time is later than last cooldown set new one and execute
                now = time.time()
                if action in self.controls_executing:
                    if self.controls_executing[action] > now:
                        if rules["mode"] == "toggle":
                            # toogle mode doesn't unlock as long as kept pressed
                            self.controls_executing[action] = now + 0.1
                        continue

                self.controls_executing[action] = now + 0.1

                print "Executing action: {0}".format(action)
                if ctrl == i_ctrl and alt == i_alt and shift == i_shift:
                    for fn in rules["call_functions"]:
                        fn(self.game)
                    break

    def toggle_record_microphone(self, game):
        if not self.stt_module:
            return

        if self.stt_module.is_recording_microphone:
            recording_aborted = self.stt_module.stop_listen()
            if not recording_aborted:
                print 'Harmony Link Plugin for VNGE: Failed to record from microphone.'
                return
            # Update Buttons
            self.game.set_buttons(
                ["Record Microphone", ">> End Harmony Link Demo >>"],
                [self.toggle_record_microphone, self.shutdown_func]
            )

        else:
            recording_started = self.stt_module.start_listen()
            if not recording_started:
                print 'Harmony Link Plugin for VNGE: Failed to record from microphone.'
                return
            # Update Buttons
            self.game.set_buttons(
                ["Stop Recording", ">> End Harmony Link Demo >>"],
                [self.toggle_record_microphone, self.shutdown_func]
            )