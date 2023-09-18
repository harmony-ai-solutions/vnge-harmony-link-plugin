# Harmony Link Plugin for VNGE
# (c) 2023 RuntimeRacer (runtimeracer@gmail.com)
#
# User Controls Module

# Import Backend base Module
from harmony_modules.common import *

# VNGE
from vngameengine import parseKeyCode, GData
import unity_util
from UnityEngine import GUI, GUILayout, Color
from UnityEngine import Input, KeyCode, Rect, Vector2
from skin_customwindow import SkinCustomWindow

import time
import traceback
import re

# Nonverbal UI Tabs
nonverbal_ui_general = "General"
nonverbal_ui_movement = "Movement"
nonverbal_ui_interaction = "Interaction"
nonverbal_ui_tabs = [
    nonverbal_ui_general,
    nonverbal_ui_movement,
    nonverbal_ui_interaction
]

# Nonverbal actions mapping
nonverbal_actions_general = {
    'Smile': 'smiles',
    'Grin': 'grins',
    'Chuckle': 'chuckles',
    'Giggle': 'giggles',
    'Laugh': 'laughs',
    'Shake head': 'shakes head',
    'Close Eyes': 'closes eyes',
    'Open Eyes': 'opens eyes',
    'Close Mouth': 'closes mouth',
    'Open Mouth': 'opens mouth',
    'Wink': 'winks',
    'Whisper': 'whispers',
    'Scream': 'screams',
}

nonverbal_actions_movement = {
    'Stand up': 'stands up',
    'Sit down': 'sits down',
    'Lay down': 'lays down',
    'Start walking': 'starts walking',
    'Stop walking': 'stops walking',
    'Open Door': 'opens the door',
    'Close Door': 'closes the door',
}

nonverbal_actions_interaction = {
    'Caress Cheek': 'caresses your cheek',
    'Caress Hand': 'caresses your hand',
    'Caress Head': 'caresses your head',
    'Kiss Cheek': 'kisses your cheek',
    'Kiss Hand': 'kisses your hand',
    'Kiss Head': 'kisses your head',
    'Kiss Forehead': 'kisses your forehead',
    'Kiss Lips': 'kisses your lips',
}


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
        # Button handling
        self.menu_buttons = {}
        # Keymap
        self.controls_keymap = {}
        self.controls_executing = {}
        # Chat GUI
        self.chat_gui_id = None
        self.chat_gui_data = None
        # Nonverbal Action GUI
        self.nonverbal_gui_id = None
        self.nonverbal_gui_data = None

    def handle_event(
            self,
            event  # HarmonyLinkEvent
    ):
        # Chat history update
        if event.event_type == EVENT_TYPE_CHAT_HISTORY and event.status == EVENT_STATE_DONE:
            self.chat_window_update_history(history_data=event.payload)

    def deactivate(self):
        HarmonyClientModuleBase.deactivate(self)
        # Hide Windows on Shutdown
        if self.chat_gui_id is not None:
            self.toggle_chat_input(self.game)
        if self.nonverbal_gui_id is not None:
            self.toggle_nonverbal_actions(self.game)

    def update_buttons(self):
        text_list = [None] * len(self.menu_buttons)
        action_list = [None] * len(self.menu_buttons)
        for button in self.menu_buttons.values():
            text_list[button["index"]] = button["text"]
            action_list[button["index"]] = button["action"]
        self.game.set_buttons(text_list, action_list)

    def setup_game_controls(self, game, shutdown_func, stt_module):
        # Link hard Game references
        self.game = game
        self.shutdown_func = shutdown_func
        # Link other modules
        self.stt_module = stt_module

        # Set Input Update Hooks to allowed
        self.game.event_reg_listener("update", self.on_input_update)

        # Basic Controls
        self.menu_buttons = {
            "chat_input": {
                "index": 0,
                "text": "Show Chat Input",
                "action": self.toggle_chat_input
            },
            "nonverbal_actions": {
                "index": 1,
                "text": "Show Nonverbal Actions",
                "action": self.toggle_nonverbal_actions
            },
            "microphone": {
                "index": 2,
                "text": "Record Microphone",
                "action": self.toggle_record_microphone
            },
            "shutdown": {
                "index": 3,
                "text": ">> End Harmony Link Demo >>",
                "action": self.shutdown_func
            }
        }
        self.update_buttons()

        # Hotkeys
        self.controls_keymap = {
            "toggle_microphone": {
                "key_codes": parseKeyCode(self.keymap_config["toggle_microphone"]),
                "call_functions": [self.toggle_record_microphone],
                "mode": "toggle"
            },
            "toggle_nonverbal_actions": {
                "key_codes": parseKeyCode(self.keymap_config["toggle_nonverbal_actions"]),
                "call_functions": [self.toggle_nonverbal_actions],
                "mode": "toggle"
            },
            "toggle_chat_input": {
                "key_codes": parseKeyCode(self.keymap_config["toggle_chat_input"]),
                "call_functions": [self.toggle_chat_input],
                "mode": "toggle"
            }
        }

        # Chat Input UI
        #self.setup_chat_input_gui()
        # Non-Verbal Actions UI
        #self.setup_nonverbal_actions_gui()

        # TODO: Player face expression
        # TODO: Player movement & direct interaction

    # skin setup func
    def nonverbal_actions_skin_setup(self, g):
        g.windowName = self.nonverbal_gui_data.wndNameNormal
        g.windowRect = self.nonverbal_gui_data.wndSizeNormal
        g.windowStyle = g.windowStyleDefault

    def chat_input_skin_setup(self, g):
        g.windowName = self.chat_gui_data.wndNameNormal
        g.windowRect = self.chat_gui_data.wndSizeNormal
        g.windowStyle = g.windowStyleDefault

    def setup_chat_input_gui(self):
        if self.chat_gui_id is not None:
            # Already exists
            return

        self.chat_gui_data = GData()
        self.chat_gui_data.gui_function = None
        self.chat_gui_data.wndNameNormal = "Chat Input Window"
        self.chat_gui_data.wndSizeNormal = Rect(150, 100, 400, 500)
        # self.chat_gui_data.actions_per_row = 3
        # self.chat_gui_data.current_tab = nonverbal_ui_general # TODO: Maybe later in case we support more than 1 character
        self.chat_gui_data.posRateX, self.chat_gui_data.posRateY = 0.01, 0.001
        self.chat_gui_data.sclRateX, self.chat_gui_data.sclRateY = 0.01, 0.001
        self.chat_gui_data.input_value = ''
        self.chat_gui_data.history = [''] * 6

        # Send Request for history to Backend
        get_history_event = HarmonyLinkEvent(
            event_id='update_history',  # This is an arbitrary dummy ID to conform the Harmony Link API
            event_type=EVENT_TYPE_CHAT_HISTORY,
            status=EVENT_STATE_NEW,
            payload=None
        )
        send_success = self.backend_connector.send_event(get_history_event)
        if send_success:
            print('Harmony Link: Fetching chat history records...')
        else:
            print('Harmony Link: Failed to fetch chat records.')

        # setup skin
        skin = SkinCustomWindow()
        skin.funcSetup = self.chat_input_skin_setup
        skin.funcWindowGUI = self.chat_input_gui_sub_window
        # skin.metadata = game.gdata.vnphy
        # skin.gui_data = self.nonverbal_gui_data

        # open sub-window
        self.chat_gui_id = self.game.new_extra_window_skin(skin)

    def chat_input_gui_sub_window(self, window_controller, window_id):
        ui_default_color = GUI.color

        try:
            # vnphy = baseController.skin.metadata
            if self.chat_gui_data.gui_function is not None:
                self.chat_gui_data.gui_function()
            else:
                self.chat_input_gui_main_window()
        except:
            traceback.print_exc()
            self.close_chat_input_gui()

        # close button
        close_button_rect = Rect(window_controller.windowRect.width - 16, 3, 13, 13)
        GUI.color = Color.red
        if GUI.Button(close_button_rect, ""):
            self.toggle_chat_input(self.game)
        GUI.color = ui_default_color

    def chat_window_update_history(self, history_data):
        start_idx = 0
        if len(history_data) < len(self.chat_gui_data.history):
            start_idx = len(self.chat_gui_data.history) - len(history_data)
        elif len(history_data) > len(self.chat_gui_data.history):
            history_data = history_data[(len(history_data)-len(self.chat_gui_data.history)):]

        for idx, value in enumerate(self.chat_gui_data.history):
            if idx >= start_idx:
                history_element = history_data[idx-start_idx]
                self.chat_gui_data.history[idx] = history_element['Name'] + ': ' + history_element['Message']
            else:
                self.chat_gui_data.history[idx] = ""

    def chat_input_gui_main_window(self):
        ui_default_color = GUI.color

        # Render chat history
        self.chat_input_gui_render_history()

        # Render default controls
        self.chat_input_gui_render_tab_default_controls()

    def chat_input_gui_render_history(self):
        self.chat_gui_data.scrollPos = Vector2.zero
        self.chat_gui_data.scrollPos = GUILayout.BeginScrollView(self.chat_gui_data.scrollPos, False, True)

        GUILayout.BeginVertical(GUILayout.Width(350))
        for idx, value in enumerate(self.chat_gui_data.history):
            GUILayout.Label(self.chat_gui_data.history[idx], GUILayout.Width(350))
        GUILayout.EndVertical()

        GUILayout.EndScrollView()
        GUILayout.FlexibleSpace()

    def chat_input_gui_render_tab_default_controls(self):
        # Add Label
        GUILayout.BeginHorizontal()
        GUILayout.FlexibleSpace()
        GUILayout.Label("Enter new chat message:", GUILayout.Width(150))
        GUILayout.FlexibleSpace()
        GUILayout.EndHorizontal()
        # with Input field at the bottom
        GUILayout.BeginHorizontal()
        GUILayout.FlexibleSpace()
        self.chat_gui_data.input_value = GUILayout.TextField(self.chat_gui_data.input_value, GUILayout.Width(350))
        GUILayout.FlexibleSpace()
        GUILayout.EndHorizontal()

        # Buttons to send independent from voice input and clear
        GUILayout.BeginHorizontal()
        if GUILayout.Button("Send"):
            if self.send_combined_interaction():
                self.clear_chat_interaction_field()
        if GUILayout.Button("Clear"):
            self.clear_chat_interaction_field()
        GUILayout.EndHorizontal()

    def close_chat_input_gui(self):
        if self.chat_gui_id is None:
            return
        wnd = self.game.get_extra_window(self.chat_gui_id)
        if wnd is not None:
            self.game.close_extra_window(self.chat_gui_id)
            self.chat_gui_id = None

    def setup_nonverbal_actions_gui(self):
        if self.nonverbal_gui_id is not None:
            # Already exists
            return

        self.nonverbal_gui_data = GData()
        self.nonverbal_gui_data.gui_function = None
        self.nonverbal_gui_data.wndNameNormal = "Non-Verbal Actions Shim"
        self.nonverbal_gui_data.wndSizeNormal = Rect(150, 400, 400, 500)
        self.nonverbal_gui_data.actions_per_row = 3
        self.nonverbal_gui_data.current_tab = nonverbal_ui_general
        self.nonverbal_gui_data.posRateX, self.nonverbal_gui_data.posRateY = 0.01, 0.001
        self.nonverbal_gui_data.sclRateX, self.nonverbal_gui_data.sclRateY = 0.01, 0.001
        self.nonverbal_gui_data.input_value = ''

        # setup skin
        skin = SkinCustomWindow()
        skin.funcSetup = self.nonverbal_actions_skin_setup
        skin.funcWindowGUI = self.nonverbal_actions_gui_sub_window
        # skin.metadata = game.gdata.vnphy
        # skin.gui_data = self.nonverbal_gui_data

        # open sub-window
        self.nonverbal_gui_id = self.game.new_extra_window_skin(skin)

    def nonverbal_actions_gui_sub_window(self, window_controller, window_id):
        ui_default_color = GUI.color

        try:
            # vnphy = baseController.skin.metadata
            if self.nonverbal_gui_data.gui_function is not None:
                self.nonverbal_gui_data.gui_function()
            else:
                self.nonverbal_actions_gui_main_window()
        except:
            traceback.print_exc()
            self.close_noverbal_actions_gui()

        # close button
        close_button_rect = Rect(window_controller.windowRect.width - 16, 3, 13, 13)
        GUI.color = Color.red
        if GUI.Button(close_button_rect, ""):
            self.toggle_nonverbal_actions(self.game)
        GUI.color = ui_default_color

    def nonverbal_actions_gui_main_window(self):
        ui_default_color = GUI.color

        # tab header
        GUILayout.BeginHorizontal()
        for tab_element in nonverbal_ui_tabs:
            tab_name = tab_element.strip()
            GUI.color = Color.green if tab_name == self.nonverbal_gui_data.current_tab else ui_default_color
            if GUILayout.Button(tab_element):
                self.nonverbal_gui_data.current_tab = tab_name
        GUI.color = ui_default_color

        if False and GUILayout.Button("?", GUILayout.ExpandWidth(False)):
            print("show some help")
        GUILayout.EndHorizontal()

        # Small spacer
        GUILayout.Space(30)

        # tab content
        if self.nonverbal_gui_data.current_tab == nonverbal_ui_general:
            self.nonverbal_actions_gui_render_tab_general()
        elif self.nonverbal_gui_data.current_tab == nonverbal_ui_movement:
            self.nonverbal_actions_gui_render_tab_movement()
        elif self.nonverbal_gui_data.current_tab == nonverbal_ui_interaction:
            self.nonverbal_actions_gui_render_tab_interaction()
        else:
            print 'Harmony Link - Controls: Invalid Tab selected: {0}'.format(self.nonverbal_gui_data.current_tab)
            self.nonverbal_gui_data.current_tab = nonverbal_ui_general
            self.nonverbal_actions_gui_render_tab_general()

    def nonverbal_actions_gui_render_tab_default_controls(self):
        # Add Label
        GUILayout.BeginHorizontal()
        GUILayout.FlexibleSpace()
        GUILayout.Label("Nonverbal Action:", GUILayout.Width(150))
        GUILayout.FlexibleSpace()
        GUILayout.EndHorizontal()
        # with Input field at the bottom
        GUILayout.BeginHorizontal()
        GUILayout.FlexibleSpace()
        GUILayout.Label("*", GUILayout.Width(5))
        self.nonverbal_gui_data.input_value = GUILayout.TextField(self.nonverbal_gui_data.input_value, GUILayout.Width(350))
        GUILayout.Label("*", GUILayout.Width(5))
        GUILayout.FlexibleSpace()
        GUILayout.EndHorizontal()

        # Buttons to send independent from voice input and clear
        GUILayout.BeginHorizontal()
        if GUILayout.Button("Send"):
            if self.send_independent_nonverbal_interaction():
                self.clear_nonverbal_interaction_field()
        if GUILayout.Button("Clear"):
            self.clear_nonverbal_interaction_field()
        GUILayout.EndHorizontal()

    def nonverbal_actions_gui_render_tab_general(self):
        # Add Buttons for building nonverbal interaction
        idx = 0
        GUILayout.BeginHorizontal()
        for label, text in nonverbal_actions_general.items():
            if idx == self.nonverbal_gui_data.actions_per_row:
                GUILayout.EndHorizontal()
                GUILayout.BeginHorizontal()
                idx = 0
            if GUILayout.Button(label):
                self.add_remove_to_nonverbal_action(text)
            idx += 1
        GUILayout.EndHorizontal()

        # Fill in Void until bottom - TODO: maybe we can reduce space usage here
        GUILayout.FlexibleSpace()
        # Render default controls
        self.nonverbal_actions_gui_render_tab_default_controls()

    def nonverbal_actions_gui_render_tab_movement(self):
        # Add Buttons for building nonverbal interaction
        idx = 0
        GUILayout.BeginHorizontal()
        for label, text in nonverbal_actions_movement.items():
            if idx == self.nonverbal_gui_data.actions_per_row:
                GUILayout.EndHorizontal()
                GUILayout.BeginHorizontal()
                idx = 0
            if GUILayout.Button(label):
                self.add_remove_to_nonverbal_action(text)
            idx += 1
        GUILayout.EndHorizontal()

        # Fill in Void until bottom - TODO: maybe we can reduce space usage here
        GUILayout.FlexibleSpace()
        # Render default controls
        self.nonverbal_actions_gui_render_tab_default_controls()

    def nonverbal_actions_gui_render_tab_interaction(self):
        # Add Buttons for building nonverbal interaction
        idx = 0
        GUILayout.BeginHorizontal()
        for label, text in nonverbal_actions_interaction.items():
            if idx == self.nonverbal_gui_data.actions_per_row:
                GUILayout.EndHorizontal()
                GUILayout.BeginHorizontal()
                idx = 0
            if GUILayout.Button(label):
                self.add_remove_to_nonverbal_action(text)
            idx += 1
        GUILayout.EndHorizontal()

        # Fill in Void until bottom - TODO: maybe we can reduce space usage here
        GUILayout.FlexibleSpace()
        # Render default controls
        self.nonverbal_actions_gui_render_tab_default_controls()

    def close_noverbal_actions_gui(self):
        if self.nonverbal_gui_id is None:
            return
        wnd = self.game.get_extra_window(self.nonverbal_gui_id)
        if wnd is not None:
            self.game.close_extra_window(self.nonverbal_gui_id)
            self.nonverbal_gui_id = None

    def add_remove_to_nonverbal_action(self, string):
        if string in self.nonverbal_gui_data.input_value:
            self.nonverbal_gui_data.input_value = self.nonverbal_gui_data.input_value.replace(string + " and", "")
            self.nonverbal_gui_data.input_value = self.nonverbal_gui_data.input_value.replace("and " + string, "")
            self.nonverbal_gui_data.input_value = self.nonverbal_gui_data.input_value.replace(string, "")
            self.nonverbal_gui_data.input_value = self.nonverbal_gui_data.input_value.strip()
        else:
            if len(self.nonverbal_gui_data.input_value) > 0:
                self.nonverbal_gui_data.input_value += " and " + string
            else:
                self.nonverbal_gui_data.input_value = string

    def send_independent_nonverbal_interaction(self):
        if len(self.nonverbal_gui_data.input_value) == 0:
            return

        print "Sending independent nonverbal Interaction: *{0}*".format(self.nonverbal_gui_data.input_value)
        event = HarmonyLinkEvent(
            event_id='new_nonverbal',  # This is an arbitrary dummy ID to conform the Harmony Link API
            event_type=EVENT_TYPE_USER_UTTERANCE,
            status=EVENT_STATE_NEW,
            payload={
                'type': UTTERANCE_NONVERBAL,
                'content': self.nonverbal_gui_data.input_value
            }
        )
        return self.backend_connector.send_event(event)

    def send_combined_interaction(self):
        if len(self.chat_gui_data.input_value) == 0:
            return

        # Check for Commands
        command = ""
        message = self.chat_gui_data.input_value
        match = re.match(r'^/(\w+)\s+(.*)', message)
        if match:
            command = match.group(1)
            message = match.group(2)

        if command == "say":
            print "Generating speech for text: {0}".format(message)
            event = HarmonyLinkEvent(
                event_id='generate_speech',  # This is an arbitrary dummy ID to conform the Harmony Link API
                event_type=EVENT_TYPE_TTS_GENERATE_SPEECH,
                status=EVENT_STATE_NEW,
                payload={
                    'type': UTTERANCE_VERBAL,
                    'content': message
                }
            )
            return self.backend_connector.send_event(event)
        elif len(command) > 0:
            print 'Unknown command entered: {0}'.format(command)
            return

        print "Sending independent Interaction: {0}".format(self.chat_gui_data.input_value)
        event = HarmonyLinkEvent(
            event_id='new_combined',  # This is an arbitrary dummy ID to conform the Harmony Link API
            event_type=EVENT_TYPE_USER_UTTERANCE,
            status=EVENT_STATE_NEW,
            payload={
                'type': UTTERANCE_COMBINED,
                'content': self.chat_gui_data.input_value
            }
        )
        return self.backend_connector.send_event(event)

    def update_delayed_nonverbal_interaction(self):
        if self.nonverbal_gui_id is None or len(self.nonverbal_gui_data.input_value) == 0:
            return

        print "Updating ongoing nonverbal Interaction: *{0}*".format(self.nonverbal_gui_data.input_value)
        event = HarmonyLinkEvent(
            event_id='update_nonverbal',  # This is an arbitrary dummy ID to conform the Harmony Link API
            event_type=EVENT_TYPE_USER_UTTERANCE,
            status=EVENT_STATE_NEW,
            payload={
                'type': UTTERANCE_NONVERBAL_DELAYED,
                'content': self.nonverbal_gui_data.input_value
            }
        )
        return self.backend_connector.send_event(event)

    def clear_nonverbal_interaction_field(self):
        self.nonverbal_gui_data.input_value = ''

    def clear_chat_interaction_field(self):
        self.chat_gui_data.input_value = ''

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
            self.menu_buttons["microphone"]["text"] = "Record Microphone"
            self.update_buttons()

        else:
            recording_started = self.stt_module.start_listen()
            if not recording_started:
                print 'Harmony Link Plugin for VNGE: Failed to record from microphone.'
                return
            # Update delayed nonverbal interaction if set
            self.update_delayed_nonverbal_interaction()
            # Update Buttons
            self.menu_buttons["microphone"]["text"] = "Stop Recording"
            self.update_buttons()

    def toggle_nonverbal_actions(self, game):
        if self.nonverbal_gui_id is not None:
            self.close_noverbal_actions_gui()
            # Update Buttons
            self.menu_buttons["nonverbal_actions"]["text"] = "Show Nonverbal Actions"
            self.update_buttons()
        else:
            # Create the GUI
            self.setup_nonverbal_actions_gui()
            # Update Buttons
            self.menu_buttons["nonverbal_actions"]["text"] = "Hide Nonverbal Actions"
            self.update_buttons()

    def toggle_chat_input(self, game):
        if self.chat_gui_id is not None:
            self.close_chat_input_gui()
            # Update Buttons
            self.menu_buttons["chat_input"]["text"] = "Show Chat Window"
            self.update_buttons()
        else:
            # Create the GUI
            self.setup_chat_input_gui()
            # Update Buttons
            self.menu_buttons["chat_input"]["text"] = "Hide Chat Window"
            self.update_buttons()