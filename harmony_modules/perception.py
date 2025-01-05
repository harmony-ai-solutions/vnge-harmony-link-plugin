# Harmony Link Plugin for VNGE
# (c) 2023-2025 Project Harmony.AI (contact@project-harmony.ai)
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

# Perception related - this might be individual for different characters later, but for now assume a base value
_visual_perception_range = 1000  # Distance for entities to recognize others
_visual_perception_field_angle = 170  # Degrees for which the perception range can detect objects around the range beam
_talking_perception_range = 400  # Distance for Entities to recognize others talking
_comprehension_perception_range = 100  # Distance for entities to understand what another entity or user says


# PerceptionHandler - module main class
class PerceptionHandler(HarmonyClientModuleBase):
    def __init__(self, entity_controller, perception_config):
        # execute the base constructor
        HarmonyClientModuleBase.__init__(self, entity_controller=entity_controller)
        # Set config
        self.config = perception_config

    def handle_event(
            self,
            event  # HarmonyLinkEvent
    ):

        if event.event_type == EVENT_TYPE_PERCEPTION_ACTOR_UTTERANCE and event.status == EVENT_STATE_DONE:
            # Get the chara actor for this entity
            utterance_data = event.payload
            event_entity_id = utterance_data["entity_id"]
            event_actor = self.entity_controller.game.scenef_get_actor(event_entity_id)
            if event_actor is None:
                print 'Entity "{0}" - Perception module: No actor chara found for entity ID "{0}"'.format(
                    self.entity_controller.entity_id,
                    event_entity_id
                )

                # Forward it as explicit user utterance event to harmony link for this entity
                event = HarmonyLinkEvent(
                    event_id='actor_{0}_VAD_utterance_processed'.format(self.entity_controller.entity_id),
                    event_type=EVENT_TYPE_USER_UTTERANCE,
                    status=EVENT_STATE_NEW,
                    payload=utterance_data
                )
                self.backend_connector.send_event(event)
                return

            # Check if this event could be recognized by the actor
            self.check_for_event_recognition(event, event_actor)

        # Suppress Speech output for the current entity
        if event.event_type == EVENT_TYPE_STT_SPEECH_STARTED and event.status == EVENT_STATE_DONE:
            # event_entity_id = event.payload
            self.entity_controller.ttsModule.suppress_speech(suppress=True)

        # Unsuppress Speech output for the current entity
        if event.event_type == EVENT_TYPE_STT_SPEECH_STOPPED and event.status == EVENT_STATE_DONE:
            # event_entity_id = event.payload
            self.entity_controller.ttsModule.suppress_speech(suppress=False)

        return

    def check_for_event_recognition(self, event, event_actor):
        # TODO
        return



