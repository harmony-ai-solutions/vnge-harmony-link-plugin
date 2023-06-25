# Harmony Link Plugin for VNGE
# (c) 2023 RuntimeRacer (runtimeracer@gmail.com)
#
# This file contains an individual implementation of Countenance handling based on Harmony Link AIState Events.
#
# At a later point it is intended to have Harmony Link calculate countenance params internally and clients
# just need to visualize these.
#
# However this is also a valid way to go in case the capabilities of the Event API are insufficient.

# Import Backend base Module
from harmony_modules.common import *

# VNGE
from vngameengine import vnge_game as game
from vnlibfaceexpressions import conf_neo_male, conf_neo_female
from vnactor import char_act_funcs

from threading import Thread
import time

# Custom expressions - Fork from vnlibfaceexpressions
expressions_default = conf_neo_male.copy()
expressions_male = expressions_default.copy()
expressions_female = expressions_default.copy()
expressions_female.update(conf_neo_female)
# Custom expressions
# TODO


# CountenanceHandler - module main class
class CountenanceHandler(HarmonyClientModuleBase):
    def __init__(self, backend_connector, countenance_config):
        # execute the base constructor
        HarmonyClientModuleBase.__init__(self, backend_connector=backend_connector)
        # Set config
        self.config = countenance_config

    def handle_event(
            self,
            event  # HarmonyLinkEvent
    ):
        # AI Status update
        if event.event_type == EVENT_TYPE_AI_STATUS and event.status == EVENT_STATE_DONE:
            self.update_ai_state(ai_state=event.payload)
            # Update face expression based on status context
            self.update_chara_from_state()

        if event.event_type == EVENT_TYPE_AI_SPEECH and event.status == EVENT_STATE_DONE:

            utterance_data = event.payload

            if utterance_data["type"] == "UTTERANCE_NONVERBAL" and len(utterance_data["content"]) > 0:
                # Update face expression based on nonverbal action context
                self.update_chara_from_action(utterance_data["content"])

        return

    def update_chara_from_state(self):
        if self.chara is None or self.ai_state is None:
            return

        # Step 1: Determine behavioural stance
        # Step 2: Determine Mood
        if self.ai_state.behaviour == "SAD":
            if self.ai_state.mood == "SAD":
                self.apply_expression(self.ai_state.gender, 'sad', True)
            else:  # "DEFAULT"
                self.apply_expression(self.ai_state.gender, 'unhappy', True)

        elif self.ai_state.behaviour == "SLEEP":
            if self.ai_state.mood == "SAD":
                self.apply_expression(self.ai_state.gender, 'unhappy_eyes_closed', True)
            else:  # "DEFAULT"
                self.apply_expression(self.ai_state.gender, 'sleeping', True)

        elif self.ai_state.behaviour == "ANGRY":
            if self.ai_state.mood == "ANGRY":
                self.apply_expression(self.ai_state.gender, 'very_angry', True)
            else:  # "DEFAULT"
                self.apply_expression(self.ai_state.gender, 'angry_whatyousay', True)

        else: # "DEFAULT"
            if self.ai_state.mood == "HAPPY":
                self.apply_expression(self.ai_state.gender, 'happy_smile', True)
            else: # "DEFAULT"
                self.apply_expression(self.ai_state.gender, 'normal', True)

    def update_chara_from_action(self, action):
        if self.chara is None or self.ai_state is None:
            return

    def apply_expression_delayed(self, gender, expression_name, update_base_expression=False, delay=5):
        time.sleep(delay)
        self.apply_expression(gender, expression_name, update_base_expression)

    def apply_expression(self, gender, expression_name, update_base_expression=False):
        expression = expressions_default[expression_name]
        if gender == "F" and expression_name in expressions_female:
            expression = expressions_female[expression_name]
        elif gender == "M" and expression_name in expressions_male:
            expression = expressions_male[expression_name]

        for function in expression:
            if function in char_act_funcs:
                char_act_funcs[function][0](self.chara.actor, expression[function])

        if update_base_expression:
            self.chara.current_base_expression = expression_name
        elif expression != self.chara.current_base_expression:
            # Revert timer
            revert_thread = Thread(target=self.apply_expression_delayed(
                gender,
                self.chara.current_base_expression,
                update_base_expression=True,
                delay=2
            ))
            revert_thread.start()
