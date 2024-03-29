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

emotions_default = {
    'neutral': {'mouth': 1, 'mouth_open': 0.000, 'eyes': 0, 'eyes_open': 1.000, 'tear': 0},
    'angry': {'mouth': 5, 'eyes': 4, 'eyes_open': 1.000},
    'disgusted': {'eyes': 4, 'eyes_open': 1, 'mouth': 0, 'mouth_open': 0},
    'afraid': {'mouth': 1, 'mouth_open': 0.000, 'eyes': 0, 'eyes_open': 1.000, 'tear': 0},
    'happy': {'eyes': 3, 'eyes_open': 1, 'mouth': 1, 'mouth_open': 1},
    'sad': {'eyes': 5, 'eyes_open': 1, 'mouth': 0, 'mouth_open': 0, 'tear': 1},
    'surprised': {'eyes': 5, 'eyes_open': 1, 'mouth': 1, 'mouth_open': 1},
    'annoyed': {'eyes': 0, 'eyes_open': 1.000, 'mouth': 0, 'mouth_open': 0.000},
    'nervous': {'eyes': 4, 'eyes_open': 0, 'mouth': 1, 'mouth_open': 0},
    'confused': {'eyes': 0, 'eyes_open': 0.772, 'mouth': 0, 'mouth_open': 0.169},
}
emotions_male = emotions_default.copy()
emotions_female = emotions_default.copy()

# Custom expressions - Fork from vnlibfaceexpressions
expressions_default = {
    'normal': {'mouth': 1, 'mouth_open': 0.000, 'eyes': 0, 'eyes_open': 1.000, 'tear': 0, 'face_red': 0},
    'eyes_closed': {'mouth': 1, 'eyes': 0, 'eyes_open': 1.000},
    'angry_whatyousay': {'mouth': 5, 'eyes': 4, 'eyes_open': 1.000},
    'glare': {'eyes': 0, 'eyes_open': 1.000, 'mouth': 0, 'mouth_open': 0.000},
    'blank_stare': {'eyes': 0, 'eyes_open': 0.772, 'mouth': 0, 'mouth_open': 0.169},
    'tired_stare': {'eyes': 0, 'eyes_open': 0.478, 'mouth': 0, 'mouth_open': 0.426},
    'sleeping': {'eyes': 0, 'eyes_open': 0.051, 'mouth': 0, 'mouth_open': 0.721},
    'normal_smile': {'eyes': 0, 'eyes_open': 1, 'mouth': 1, 'mouth_open': 0},
    'happy_smile': {'eyes': 3, 'eyes_open': 1, 'mouth': 1, 'mouth_open': 1},
    'very_happy_smile': {'eyes': 3, 'eyes_open': 1, 'mouth': 2, 'mouth_open': 1},
    'kind_smile': {'eyes': 3, 'eyes_open': 1, 'mouth': 1, 'mouth_open': 0},
    'angry_smile': {'eyes': 4, 'eyes_open': 1, 'mouth': 1, 'mouth_open': 1},
    'evil_smile': {'eyes': 4, 'eyes_open': 1, 'mouth': 1, 'mouth_open': 0},
    'concentration': {'eyes': 4, 'eyes_open': 0.5, 'mouth': 1, 'mouth_open': 0},
    'unhappy': {'eyes': 4, 'eyes_open': 1, 'mouth': 0, 'mouth_open': 0},
    'unhappy_talking': {'eyes': 4, 'eyes_open': 1, 'mouth': 0, 'mouth_open': 0.8},
    'unhappy_eyes_closed': {'eyes': 4, 'eyes_open': 0, 'mouth': 0, 'mouth_open': 0},
    'surprise_smile': {'eyes': 5, 'eyes_open': 1, 'mouth': 1, 'mouth_open': 1},
    'stunned_smile': {'eyes': 5, 'eyes_open': 1, 'mouth': 1, 'mouth_open': 0},
    'stunned': {'eyes': 5, 'eyes_open': 1, 'mouth': 0, 'mouth_open': 0},
    'shocked': {'eyes': 5, 'eyes_open': 1, 'mouth': 0, 'mouth_open': 1},
    'sad': {'eyes': 5, 'eyes_open': 1, 'mouth': 0, 'mouth_open': 0, 'tear': 1},
    'sad_shocked': {'eyes': 5, 'eyes_open': 1, 'mouth': 0, 'mouth_open': 0.5},
    'laughing': {'eyes': 10, 'eyes_open': 1, 'mouth': 2, 'mouth_open': 1},
    'smiling_talking': {'eyes': 3, 'eyes_open': 1, 'mouth': 2, 'mouth_open': 0.5},
    'very_angry': {'eyes': 4, 'eyes_open': 1, 'mouth': 3, 'mouth_open': 0},
    'very_angry_talking': {'eyes': 4, 'eyes_open': 1, 'mouth': 3, 'mouth_open': 0.5},
    'very_angry_shouting': {'eyes': 4, 'eyes_open': 1, 'mouth': 3, 'mouth_open': 1},
    'crying': {'eyes': 3, 'eyes_open': 1, 'mouth': 3, 'mouth_open': 0.5, 'tear': 3},
    'serious': {'eyes': 0, 'eyes_open': 1, 'mouth': 3, 'mouth_open': 0},
    'serious_talking': {'eyes': 0, 'eyes_open': 1, 'mouth': 3, 'mouth_open': 0.5},
    'serious_shouting': {'eyes': 0, 'eyes_open': 1, 'mouth': 3, 'mouth_open': 1},
    'sexy_smile': {'eyes': 0, 'eyes_open': 0.8, 'mouth': 6, 'mouth_open': 0, 'face_red': 0.2},
    'thoughtful_smile': {'eyes': 3, 'eyes_open': 1, 'mouth': 7, 'mouth_open': 0},
    'silly_smile': {'eyes': 3, 'eyes_open': 1, 'mouth': 7, 'mouth_open': 0},
    'embarrassed': {'eyes': 3, 'eyes_open': 1, 'mouth': 2, 'mouth_open': 0, 'face_red': 0.5},
    'turned_on': {'eyes': 3, 'eyes_open': 1, 'mouth': 6, 'mouth_open': 0.3, 'face_red': 0.8},
    'slightly_embarassed': {'eyes': 5, 'eyes_open': 1, 'mouth': 1, 'mouth_open': 0, 'face_red': 0.3},
}
expressions_male = expressions_default.copy()
expressions_female = expressions_default.copy()
#expressions_female.update(conf_neo_female)
# Custom expressions
# TODO


# CountenanceHandler - module main class
class CountenanceHandler(HarmonyClientModuleBase):
    def __init__(self, entity_controller, countenance_config):
        # execute the base constructor
        HarmonyClientModuleBase.__init__(self, entity_controller=entity_controller)
        # Set config
        self.config = countenance_config

    def handle_event(
            self,
            event  # HarmonyLinkEvent
    ):
        # AI State update
        if event.event_type == EVENT_TYPE_AI_STATUS and event.status == EVENT_STATE_DONE:
            self.update_ai_state(ai_state=event.payload)
            # Update face expression based on status context
            self.update_chara_from_state()

        if event.event_type == EVENT_TYPE_AI_COUNTENANCE_UPDATE and event.status == EVENT_STATE_DONE:
            self.update_countenance_state(countenance_state=event.payload)
            # Update face expression based on status context
            self.update_chara_from_state()

        # if event.event_type == EVENT_TYPE_AI_SPEECH and event.status == EVENT_STATE_DONE:
        #
        #     utterance_data = event.payload
        #
        #     if utterance_data["type"] == "UTTERANCE_NONVERBAL" and len(utterance_data["content"]) > 0:
        #         # Update face expression based on nonverbal action context
        #         self.update_chara_from_action(utterance_data["content"])

        return

    def update_chara_from_state(self):
        if self.chara is None or self.countenance_state is None:
            return

        # Update Countenance
        self.countenance_update('', self.countenance_state.emotional_state, self.countenance_state.facial_expression)

    # def update_chara_from_action(self, action):
    #     if self.chara is None or self.ai_state is None:
    #         return

    # TODO: Below is 2x very duplicate-y code. Refactor this

    # def apply_expression_delayed(self, gender, expression_name, update_base_expression=False, delay=5):
    #     time.sleep(delay)
    #     self.apply_expression(gender, expression_name, update_base_expression)
    #
    # def apply_expression(self, gender, expression_name, update_base_expression=False):
    #     expression = expressions_default['normal']
    #     expression.update(expressions_default[expression_name])
    #
    #     # Check for gender specific expressions
    #     if gender == "F" and expression_name in expressions_female:
    #         expression = expressions_female['normal']
    #         expression.update(expressions_female[expression_name])
    #     elif gender == "M" and expression_name in expressions_male:
    #         expression = expressions_male['normal']
    #         expression.update(expressions_male[expression_name])
    #
    #     for function in expression:
    #         if function in char_act_funcs:
    #             char_act_funcs[function][0](self.chara.actor, expression[function])
    #
    #     if update_base_expression:
    #         self.chara.current_base_expression = expression_name
    #     elif expression != self.chara.current_base_expression:
    #         # Revert timer
    #         revert_thread = Thread(target=self.apply_expression_delayed(
    #             gender,
    #             self.chara.current_base_expression,
    #             update_base_expression=True,
    #             delay=2
    #         ))
    #         revert_thread.start()

    def countenance_update(self, gender, emotion_name, expression_name):
        emotion = emotions_default['neutral']
        if emotion_name in emotions_default:
            emotion.update(emotions_default[emotion_name])

        expression = expressions_default['normal']
        if expression_name in expressions_default:
            expression.update(expressions_default[expression_name])

        # Check for gender specific emotions
        if gender == "F" and emotion_name in emotions_female:
            emotion = emotions_female['neutral']
            if emotion_name in emotions_female:
                emotion.update(emotions_female[emotion_name])

            expression = expressions_female['normal']
            if expression_name in expressions_female:
                expression.update(expressions_female[expression_name])
        elif gender == "M" and emotion_name in emotions_male:
            emotion = emotions_male['neutral']
            if emotion_name in emotions_male:
                emotion.update(emotions_male[emotion_name])

            expression = expressions_male['normal']
            if expression_name in expressions_male:
                expression.update(expressions_male[expression_name])

        # Expression on top of emotion
        target_state = emotion
        target_state.update(expression)

        for function in target_state:
            if function in char_act_funcs:
                char_act_funcs[function][0](self.chara.actor, target_state[function])

