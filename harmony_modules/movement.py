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
from Studio import Info
from vngameengine import vnge_game as game
from vnlibfaceexpressions import conf_neo_male, conf_neo_female
from vnactor import char_act_funcs

from threading import Thread
import time
import json

#
registered_actions = [
    # Basic movement and interaction
    {
        'name': 'move',
        'description': 'normal walking',
        'examples': [

        ]
    },
    {
        'name': 'walk',
        'description': 'fast walking',
        'examples': [

        ]
    },
    {
        'name': 'run',
        'description': 'running',
        'examples': [

        ]
    },
    {
        'name': 'sit_down',
        'description': 'sit down on the ground or an object',
        'examples': [

        ]
    },
    {
        'name': 'lay_down',
        'description': 'lay down on the ground or an object',
        'examples': [

        ]
    },
    {
        'name': 'stand_up',
        'description': 'stand up from sitting or lying position',
        'examples': [

        ]
    },
    {
        'name': 'jump_fixed',
        'description': 'jump at current position',
        'examples': [

        ]
    },
    {
        'name': 'jump_over',
        'description': 'jump over an object',
        'examples': [

        ]
    },
    {
        'name': 'pick_up_left_hand',
        'description': 'pick up an object with left hand',
        'examples': [

        ]
    },
    {
        'name': 'pick_up_right_hand',
        'description': 'pick up an object with right hand',
        'examples': [

        ]
    },
    {
        'name': 'pick_up_both_hands',
        'description': 'pick up an object with both hands',
        'examples': [

        ]
    },
    {
        'name': 'drop_item',
        'description': 'drop item currently in hands to the ground',
        'examples': [

        ]
    },
    {
        'name': 'store_item',
        'description': 'store item in hand in pocket / inventory',
        'examples': [

        ]
    },
    {
        'name': 'retrieve_item',
        'description': 'retrieve item from pocket / inventory into hand',
        'examples': [

        ]
    },
    {
        'name': 'place_item',
        'description': 'place item currently in hands on the ground or an object',
        'examples': [

        ]
    },
    {
        'name': 'drop_item',
        'description': 'drop item currently in hands to the ground',
        'examples': [

        ]
    },

    # Chara interaction
    {
        'name': 'give_item',
        'description': 'give item in hand to the other chara\'s hand',
        'examples': [

        ]
    },
    {
        'name': 'take_hand',
        'description': 'take hand of the other chara, depending on position, and interlock',
        'examples': [

        ]
    },
    {
        'name': 'caress_cheek',
        'description': 'caress cheek of the other chara',
        'examples': [

        ]
    },
    {
        'name': 'caress_head',
        'description': 'caress head of the other chara',
        'examples': [

        ]
    },
    {
        'name': 'kiss_hand',
        'description': 'take hand of the other chara, and kiss it in a romantic way',
        'examples': [

        ]
    },
    {
        'name': 'kiss_cheek',
        'description': 'kiss cheek of the other chara',
        'examples': [

        ]
    },
    {
        'name': 'kiss_forehead',
        'description': 'kiss forehead of the other chara',
        'examples': [

        ]
    },
    {
        'name': 'kiss_lips',
        'description': 'kiss the other chara',
        'examples': [

        ]
    },
    {
        'name': 'push_away',
        'description': 'push away the other chara',
        'examples': [

        ]
    },
]

# CountenanceHandler - module main class
class MovementHandler(HarmonyClientModuleBase):
    def __init__(self, backend_connector, movement_config):
        # execute the base constructor
        HarmonyClientModuleBase.__init__(self, backend_connector=backend_connector)
        # Set config
        self.config = movement_config
        # Movement related data
        self.animations_map = {}

        # Debug: List all Animations existing in the game
        info = Info.Instance
        # print(json.dumps(dir(info)))

        animations = {}
        animation_groups = dict(info.dicAGroupCategory)
        for group_id, group_info in animation_groups.items():
            animations[group_id] = {
                "name": group_info.name,
                "categories": {}
            }
            categories = dict(animation_groups[group_id].dicCategory)
            for category_id, category_name in categories.items():
                animation_items = dict(info.dicAnimeLoadInfo[group_id][category_id])
                animations[group_id]["categories"][category_id] = {
                    "name": category_name,
                    "animation_items": []
                }
                for item_info in animation_items.values():
                    animations[group_id]["categories"][category_id]["animation_items"].append(item_info.name)

        print(json.dumps(animations))
        raise RuntimeError("Dont want to start if debug")

    def create_animations_map(self):

    def handle_event(
            self,
            event  # HarmonyLinkEvent
    ):
        # AI State update
        # if event.event_type == EVENT_TYPE_AI_STATUS and event.status == EVENT_STATE_DONE:
        #     self.update_ai_state(ai_state=event.payload)
        #     # Update face expression based on status context
        #     self.update_chara_from_state()
        #
        # if event.event_type == EVENT_TYPE_AI_COUNTENANCE_UPDATE and event.status == EVENT_STATE_DONE:
        #     self.update_countenance_state(countenance_state=event.payload)
        #     # Update face expression based on status context
        #     self.update_chara_from_state()

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
        # self.countenance_update('', self.countenance_state.emotional_state, self.countenance_state.facial_expression)

    # def countenance_update(self, gender, emotion_name, expression_name):
    #     emotion = emotions_default['neutral']
    #     if emotion_name in emotions_default:
    #         emotion.update(emotions_default[emotion_name])
    #
    #     expression = expressions_default['normal']
    #     if expression_name in expressions_default:
    #         expression.update(expressions_default[expression_name])
    #
    #     # Check for gender specific emotions
    #     if gender == "F" and emotion_name in emotions_female:
    #         emotion = emotions_female['neutral']
    #         if emotion_name in emotions_female:
    #             emotion.update(emotions_female[emotion_name])
    #
    #         expression = expressions_female['normal']
    #         if expression_name in expressions_female:
    #             expression.update(expressions_female[expression_name])
    #     elif gender == "M" and emotion_name in emotions_male:
    #         emotion = emotions_male['neutral']
    #         if emotion_name in emotions_male:
    #             emotion.update(emotions_male[emotion_name])
    #
    #         expression = expressions_male['normal']
    #         if expression_name in expressions_male:
    #             expression.update(expressions_male[expression_name])
    #
    #     # Expression on top of emotion
    #     target_state = emotion
    #     target_state.update(expression)
    #
    #     for function in target_state:
    #         if function in char_act_funcs:
    #             char_act_funcs[function][0](self.chara.actor, target_state[function])
