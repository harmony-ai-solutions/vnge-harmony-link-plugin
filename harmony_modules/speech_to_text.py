# Harmony Link Plugin for VNGE
# (c) 2023 RuntimeRacer (runtimeracer@gmail.com)
#
# This file contains all handling to be done with the Harmony Link STT Module
#
# Import Client base Module
from harmony_modules.common import *

# VNGE
from UnityEngine import AudioClip, Microphone

import threading
import base64
import time
import struct

# Constants
RESULT_MODE_PROCESS = "process"
RESULT_MODE_RETURN = "return"


# CountenanceHandler - module main class
class SpeechToTextHandler(HarmonyClientModuleBase):
    def __init__(self, entity_controller, stt_config):
        # execute the base constructor
        HarmonyClientModuleBase.__init__(self, entity_controller=entity_controller)
        # Set config
        self.config = stt_config
        # Get Base vars from config
        self.microphone_name = self.get_microphone()
        self.sample_rate = int(self.config['sample_rate'])
        self.clip_duration = int(self.config['clip_duration'])
        # Recording Handling
        self.is_recording_microphone = False
        self.active_recording_events = {}
        self.recording_clip = None
        self.recording_start_time = None

    def handle_event(
            self,
            event  # HarmonyLinkEvent
    ):
        # Audio processed and utterance received
        if event.event_type == EVENT_TYPE_STT_OUTPUT_TEXT and event.status == EVENT_STATE_DONE:

            utterance_data = event.payload

            if len(utterance_data["content"]) > 0:
                # Since this was an output created by the current entity, it needs to be distributed
                # to the other entities, which then "decide" if it's relevant to them in some way or not
                utterance_data["entity_id"] = self.entity_controller.entity_id
                event = HarmonyLinkEvent(
                    event_id='actor_{0}_VAD_utterance'.format(self.entity_controller.entity_id),
                    event_type=EVENT_TYPE_PERCEPTION_ACTOR_UTTERANCE,
                    status=EVENT_STATE_DONE,
                    payload=utterance_data
                )

                # FIXME: This is not very performant, will cause issues with many characters
                for entity_id, controller in self.entity_controller.game.scenedata.active_entities.items():
                    if entity_id == self.entity_controller.entity_id or controller.perceptionModule is None:
                        continue
                    controller.perceptionModule.handle_event(event)

        # User / Source entity starts talking
        if event.event_type == EVENT_TYPE_STT_SPEECH_STARTED and event.status == EVENT_STATE_DONE:
            # This event is intended to perform as an "interruption event" for LLM and TTS
            # on the listening entities.
            # FIXME: This is not very performant, will cause issues with many characters
            for entity_id, controller in self.entity_controller.game.scenedata.active_entities.items():
                if entity_id == self.entity_controller.entity_id or controller.perceptionModule is None:
                    continue
                #
                event.payload = {
                    "entity_id": self.entity_controller.entity_id
                }
                controller.perceptionModule.handle_event(event)

        # User / Source entity stops talking
        if event.event_type == EVENT_TYPE_STT_SPEECH_STOPPED and event.status == EVENT_STATE_DONE:
            # This event is intended to perform as an "interruption event" for LLM and TTS
            # on the listening entities.
            # FIXME: This is not very performant, will cause issues with many characters
            for entity_id, controller in self.entity_controller.game.scenedata.active_entities.items():
                if entity_id == self.entity_controller.entity_id or controller.perceptionModule is None:
                    continue
                #
                event.payload = {
                    "entity_id": self.entity_controller.entity_id
                }
                controller.perceptionModule.handle_event(event)

        # Received event to start recording Audio through the Game's utilities
        if event.event_type == EVENT_TYPE_STT_RECORD_MICROPHONE and event.status == EVENT_STATE_NEW:
            # This event triggers the recording of an audio clip using the default microphone.
            # Upon finishing the recording, it will send the recorded audio to Harmony Link for VAD & STT transcription
            recording_task = event.payload
            # Extract parameters from recording task
            duration = recording_task.get('duration', 5)  # Default to 5 seconds

            # Start a new thread to handle recording
            event_time = time.time()
            recording_thread = threading.Thread(
                target=self.process_recording_request,
                args=(event.event_id, event_time, duration)
            )
            recording_thread.start()

            # Mark event as processing and store it
            event.status = EVENT_STATE_PROCESSING
            self.active_recording_events[event.event_id] = event

    def start_listen(self):
        if self.is_recording_microphone:
            return False

        # Start recording from microphone via Unity's APIs:
        if not self.start_continuous_recording():
            return False

        # Send Event to Harmony Link to listen to the recorded Audio
        event = HarmonyLinkEvent(
            event_id='start_listen',  # This is an arbitrary dummy ID to conform the Harmony Link API
            event_type=EVENT_TYPE_STT_START_LISTEN,
            status=EVENT_STATE_NEW,
            payload={
                "auto_vad": bool(self.config['auto_vad']),
                "vad_mode": int(self.config['vad_mode']),
                "result_mode": RESULT_MODE_RETURN if bool(self.config['auto_vad']) else RESULT_MODE_PROCESS
            }
        )
        success = self.backend_connector.send_event(event)
        if success:
            print 'Harmony Link: listening...'
            self.is_recording_microphone = True
            return True
        else:
            print 'Harmony Link: listen failed'
            # Stop recording
            return False

    def stop_listen(self):
        if not self.is_recording_microphone:
            return False

        # Send Event to Harmony Link to stop listening
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

            # Stop recording to ongoing audio clip
            if not self.stop_continuous_recording():
                print 'failed to stop continous recording'
                return False

            return True
        else:
            print 'Harmony Link: stop listen failed.'
            return False

    def get_microphone(self):
        # Determine the microphone to use
        devices = Microphone.devices
        microphone_name = self.config['microphone']
        if len(devices) <= 0 or len(microphone_name) == 0:
            print 'No microphone available.'
            return None
        else:
            print 'Available microphones:'
            for mic_id, device in enumerate(devices):
                print"{0} : {1}".format(mic_id, device)

        if microphone_name == 'default':
            microphone_name = devices[0]

        return microphone_name

    def start_continuous_recording(self):
        # This starts a continous microphone recording clip which will be used to fetch
        # audio samples for Harmony's STT transcription module from
        if self.microphone_name is None or isinstance(self.microphone_name, str) and len(self.microphone_name) == 0:
            print 'No microphone available.'
            return False

        print 'Recording with microphone: {0}'.format(self.microphone_name)
        loop = True
        self.recording_clip = Microphone.Start(self.microphone_name, loop, self.clip_duration, self.sample_rate)
        self.recording_start_time = time.time()
        # Wait until recording has started
        start_time = time.time()
        while not Microphone.IsRecording(self.microphone_name):
            if time.time() - start_time > 1.0:
                print 'Failed to start continuous recording.'
                return False
            time.sleep(0.1)
        print 'Continuous recording started.'
        return True

    def stop_continuous_recording(self):
        if not self.is_recording_microphone or self.recording_clip is None or not Microphone.IsRecording(self.microphone_name):
            return False

        # Wait until all recording events have completed
        timeout_counter = 0
        while len(self.active_recording_events) > 0:
            if timeout_counter % 10 == 0:
                print 'waiting for recording clips to finish...'
            if timeout_counter < 100:
                timeout_counter += 1
                time.sleep(0.1)
            else:
                print 'recording events did not finish within timeout of 10 seconds'
                return False

        # Stop the microphone recording
        Microphone.End(self.microphone_name)
        self.is_recording_microphone = False
        print 'Continuous recording stopped.'
        return True

    def process_recording_request(self, event_id, request_time, duration):
        # Wait for the requested duration
        time.sleep(duration)

        # Calculate start and end times relative to recording start
        start_time = request_time - self.recording_start_time
        end_time = start_time + duration

        # Calculate sample indices
        start_sample = int(start_time * self.sample_rate)
        end_sample = int(end_time * self.sample_rate)
        total_samples = self.recording_clip.samples

        # Handle looping - Recorded audio clip will be looped over as soon as max duration is reached
        samples = []
        if start_sample < end_sample <= total_samples:
            # Simple case: no looping
            length = end_sample - start_sample
            samples = [0.0] * length
            self.recording_clip.GetData(samples, start_sample)
        elif end_sample > total_samples:
            # Recording wrapped around the clip length
            first_part_length = total_samples - start_sample
            second_part_length = end_sample - total_samples
            samples = [0.0] * (first_part_length + second_part_length)
            # Get first part
            self.recording_clip.GetData(samples[:first_part_length], start_sample)
            # Get second part from the beginning of the clip
            self.recording_clip.GetData(samples[first_part_length:], 0)
        else:
            print 'Invalid sample indices.'
            return

        # Convert samples to 16-bit PCM byte data
        byte_data = b''.join([struct.pack('<h', int(max(min(s, 1.0), -1.0) * 32767)) for s in samples])
        # Encode to base64
        encoded_data = base64.b64encode(byte_data)
        # Send result event
        result_event = HarmonyLinkEvent(
            event_id=event_id,
            event_type=EVENT_TYPE_STT_RECORD_MICROPHONE_RESULT,
            status=EVENT_STATE_DONE,
            payload={
                'audio_data': encoded_data
            }
        )
        self.backend_connector.send_event(result_event)
        # Remove the event from the tracking
        del self.active_recording_events[event_id]

