# Harmony Link Plugin for VNGE
# (c) 2023 RuntimeRacer (runtimeracer@gmail.com)
#
# This file contains all handling to be done with the Harmony Link STT Module
#
# Import Client base Module
from harmony_modules.common import *


# CountenanceHandler - module main class
class SpeechToTextHandler(HarmonyClientModuleBase):
    def __init__(self, backend_connector, stt_config):
        # execute the base constructor
        HarmonyClientModuleBase.__init__(self, backend_connector=backend_connector)
        # Set config
        self.config = stt_config
        # Recording Handling
        self.is_recording_microphone = False

    def start_listen(self):
        if self.is_recording_microphone:
            return False

        event = HarmonyLinkEvent(
            event_id='start_listen',  # This is an arbitrary dummy ID to conform the Harmony Link API
            event_type=EVENT_TYPE_STT_START_LISTEN,
            status=EVENT_STATE_NEW,
            payload={}
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

