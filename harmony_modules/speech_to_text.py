# Harmony Link Plugin for VNGE
# (c) 2023 RuntimeRacer (runtimeracer@gmail.com)
#
# This file contains all handling to be done with the Harmony Link STT Module
#
# Import Client base Module
from harmony_modules.common import *

# Constants
RESULT_MODE_PROCESS = "process"
RESULT_MODE_RETURN  = "return"

# CountenanceHandler - module main class
class SpeechToTextHandler(HarmonyClientModuleBase):
    def __init__(self, entity_controller, stt_config):
        # execute the base constructor
        HarmonyClientModuleBase.__init__(self, entity_controller=entity_controller)
        # Set config
        self.config = stt_config
        # Recording Handling
        self.is_recording_microphone = False

    def handle_event(
            self,
            event  # HarmonyLinkEvent
    ):
        # Audio processed and utterance received
        if event.event_type == EVENT_TYPE_STT_OUTPUT_TEXT and event.status == EVENT_STATE_DONE:

            utterance_data = event.payload

            if utterance_data["type"] == UTTERANCE_VERBAL and len(utterance_data["content"]) > 0:
                # Since this was an output created by the current entity, it needs to be distributed
                # to the other entities, which then "decide" if it's relevant to them in some way or not
                event = HarmonyLinkEvent(
                    event_id='actor_{0}_utterance'.format(self.entity_controller.entity_id),  # This is an arbitrary dummy ID to conform the Harmony Link API
                    event_type=EVENT_TYPE_PERCEPTION_ACTOR_UTTERANCE,
                    status=EVENT_STATE_DONE,
                    payload={
                        "entity_id": self.entity_controller.entity_id,
                        "utterance_content": utterance_data["content"]
                    }
                )

                for entity_id, controller in self.entity_controller.game.scenedata.active_entities:
                    if entity_id == self.entity_controller.entity_id or controller.perceptionModule is None:
                        continue
                    # FIXME: This is not very performant, will cause issues with many characters
                    controller.perceptionModule.handle_event(event)

    def start_listen(self):
        if self.is_recording_microphone:
            return False

        event = HarmonyLinkEvent(
            event_id='start_listen',  # This is an arbitrary dummy ID to conform the Harmony Link API
            event_type=EVENT_TYPE_STT_START_LISTEN,
            status=EVENT_STATE_NEW,
            payload={
                "auto_vad": self.config['auto_vad'],
                "vad_mode": self.config['vad_mode'],
                "result_mode": RESULT_MODE_RETURN if self.config['auto_vad'] == 1 else RESULT_MODE_PROCESS
            }
        )
        success = self.backend_connector.send_event(event)
        if success:
            print 'Harmony Link: listening...'
            self.is_recording_microphone = True
            return True
        else:
            print 'Harmony Link: listen failed'
            return False

    def stop_listen(self):
        if not self.is_recording_microphone:
            return False

        event = HarmonyLinkEvent(
            event_id='stop_listen',  # This is an arbitrary dummy ID to conform the Harmony Link API
            event_type=EVENT_TYPE_STT_STOP_LISTEN,
            status=EVENT_STATE_NEW,
            payload={}
        )
        success = self.backend_connector.send_event(event)
        if success:
            print 'Harmony Link: listening stopped. Processing speech...'
            self.is_recording_microphone = False
            return True
        else:
            print 'Harmony Link: stop listen failed.'
            return False

