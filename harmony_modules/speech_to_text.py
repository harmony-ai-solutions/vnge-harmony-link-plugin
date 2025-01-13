# Harmony Link Plugin for VNGE
# (c) 2023-2025 Project Harmony.AI (contact@project-harmony.ai)
#
# This file contains all handling to be done with the Harmony Link STT Module
#
# Import Client base Module
from harmony_modules.common import *

# VNGE
from System import Array, Single
from UnityEngine import AudioClip, Microphone

from threading import Thread, Lock
import base64
import time
import struct

# Constants
RESULT_MODE_PROCESS = "process"
RESULT_MODE_RETURN = "return"


class MicrophoneRecordingThread(Thread):
    def __init__(self, stt_handler, record_stepping=100):
        # Execute the base constructor
        Thread.__init__(self)
        # Control flow
        self.running = False
        # Params
        self.tts_handler = stt_handler
        self.record_stepping = record_stepping  # in milliseconds
        self.sleep_time = record_stepping / 1000.0  # Convert to seconds
        self.last_sample_position = 0
        self.clip_samples = self.tts_handler.recording_clip.samples
        self.channels = self.tts_handler.channels
        self.lock = Lock()
        self.bytes_per_sample = self.tts_handler.bytes_per_sample
        self.bytes_per_second = self.tts_handler.bytes_per_second
        self.max_buffer_bytes = self.tts_handler.max_buffer_bytes

    def run(self):
        self.running = True
        while self.running:
            current_position = Microphone.GetPosition(self.tts_handler.microphone_name)
            sample_count = 0
            if current_position < self.last_sample_position:
                # Wrap-around occurred
                sample_count = self.clip_samples - self.last_sample_position + current_position
            else:
                sample_count = current_position - self.last_sample_position

            if sample_count > 0:
                samples = Array.CreateInstance(Single, sample_count)
                # Read samples from last_sample_position to current_position
                if current_position >= self.last_sample_position:
                    # No wrap-around
                    self.tts_handler.recording_clip.GetData(samples, self.last_sample_position)
                else:
                    # Wrap-around
                    first_part_length = self.clip_samples - self.last_sample_position
                    first_part_samples = Array.CreateInstance(Single, first_part_length)
                    self.tts_handler.recording_clip.GetData(first_part_samples, self.last_sample_position)
                    second_part_length = current_position
                    second_part_samples = Array.CreateInstance(Single, second_part_length)
                    self.tts_handler.recording_clip.GetData(second_part_samples, 0)
                    # Combine samples
                    first_part_samples.CopyTo(samples, 0)
                    second_part_samples.CopyTo(samples, first_part_length)

                # Convert samples to 16-bit PCM byte data
                audio_bytes = b''.join([struct.pack('<h', int(max(min(s, 1.0), -1.0) * 32767)) for s in samples])

                # Lock the buffer while appending
                with self.lock:
                    # Append new audio bytes
                    self.tts_handler.recording_buffer.extend(audio_bytes)
                    # Remove oldest data if buffer exceeds max size
                    buffer_length = len(self.tts_handler.recording_buffer)
                    if buffer_length > self.max_buffer_bytes:
                        excess_bytes = buffer_length - self.max_buffer_bytes
                        del self.tts_handler.recording_buffer[:excess_bytes]
                        self.tts_handler.dropped_buffer_bytes += excess_bytes

                # Update last_sample_position
                self.last_sample_position = current_position

            # Sleep for the record stepping interval
            time.sleep(self.sleep_time)

    def stop(self):
        self.running = False


# CountenanceHandler - module main class
class SpeechToTextHandler(HarmonyClientModuleBase):
    def __init__(self, entity_controller, stt_config):
        # execute the base constructor
        HarmonyClientModuleBase.__init__(self, entity_controller=entity_controller)
        # Set config
        self.config = stt_config
        # Get Base vars from config
        self.channels = int(self.config['channels'])
        self.bit_depth = int(self.config['bit_depth'])
        self.sample_rate = int(self.config['sample_rate'])
        self.buffer_clip_duration = int(self.config['buffer_clip_duration'])
        self.record_stepping = int(self.config['record_stepping'])
        self.microphone_name = self.get_microphone()
        # Recording Handling
        self.is_recording_microphone = False
        self.active_recording_events = {}
        self.recording_buffer = None # bytearray
        self.recording_clip = None # AudioClip
        self.recording_start_time = None # time.time
        self.recording_thread = None
        self.dropped_buffer_bytes = 0
        # Calculate bytes per second
        self.bytes_per_sample = self.bit_depth // 8
        self.bytes_per_second = int(
            self.sample_rate * self.channels * self.bytes_per_sample
        )
        # Calculate maximum buffer size in bytes
        self.max_buffer_bytes = int(
            self.bytes_per_second * float(self.buffer_clip_duration)
        )

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
        if event.event_type == EVENT_TYPE_STT_FETCH_MICROPHONE and event.status == EVENT_STATE_DONE:
            # This event triggers the recording of an audio clip using the default microphone.
            # Upon finishing the recording, it will send the recorded audio to Harmony Link for VAD & STT transcription
            recording_task = event.payload
            # Extract parameters from recording task
            duration_millis = recording_task.get('duration', 5000)  # Default to 5 seconds, in miliseconds
            duration = duration_millis / 1000.0
            start_time_millis = recording_task.get('start_time', int(time.time() * 1000))  # Start time in milliseconds
            start_time = start_time_millis / 1000.0  # Convert start time to seconds

            # Start a new thread to handle recording
            # event_time = time.time()
            fetch_microphone_thread = Thread(
                target=self.process_recording_request,
                args=(event.event_id, start_time, duration)
            )
            fetch_microphone_thread.start()

            # Store event to mark it as processing
            self.active_recording_events[event.event_id] = event

    def start_listen(self):
        if self.is_recording_microphone:
            return False

        # Start recording from microphone via Unity's APIs:
        if not self.start_continuous_recording():
            return False

        # Start the recording thread
        self.recording_thread = MicrophoneRecordingThread(
            stt_handler=self,
            record_stepping=self.record_stepping
        )
        self.recording_thread.start()

        # Send Event to Harmony Link to listen to the recorded Audio
        event = HarmonyLinkEvent(
            event_id='start_listen',  # This is an arbitrary dummy ID to conform the Harmony Link API
            event_type=EVENT_TYPE_STT_START_LISTEN,
            status=EVENT_STATE_NEW,
            payload={
                "auto_vad": bool(self.config['auto_vad']),
                "vad_mode": int(self.config['vad_mode']),
                "result_mode": RESULT_MODE_RETURN if bool(self.config['auto_vad']) else RESULT_MODE_PROCESS,
                "start_time": int(self.recording_start_time * 1000),  # Convert to milliseconds
                "channels": self.channels,
                "bit_depth": self.bit_depth,
                "sample_rate": self.sample_rate
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

            # Stop recording to ongoing audio clip
            if not self.stop_continuous_recording():
                print 'failed to stop continous recording'
                return False

            self.is_recording_microphone = False
            return True
        else:
            print 'Harmony Link: stop listen failed.'
            return False

    def get_microphone(self):
        # Determine the microphone to use
        devices = Microphone.devices
        device_capabilities = {}
        microphone_name = self.config['microphone']
        if len(devices) <= 0 or len(microphone_name) == 0:
            print 'No microphone available.'
            return None
        else:
            print 'Available microphones:'
            for mic_id, device in enumerate(devices):
                # Get recording capabilities
                minFreq, maxFreq = Microphone.GetDeviceCaps(device)
                print "{0} : {1} (MinFreq: {2}, MaxFreq: {3})".format(mic_id, device, minFreq, maxFreq)
                device_capabilities[device] = (minFreq, maxFreq)

        if microphone_name == 'default':
            microphone_name = devices[0]

        # Check for correct sample rate being used
        minFreq, maxFreq = device_capabilities[microphone_name]
        if not minFreq == 0 and not maxFreq == 0:
            if self.sample_rate > maxFreq:
                self.sample_rate = maxFreq
                print "correcting sample rate from config to {0}".format(self.sample_rate)
            elif self.sample_rate < minFreq:
                self.sample_rate = minFreq
                print "correcting sample rate from config to {0}".format(self.sample_rate)

        return microphone_name

    def start_continuous_recording(self):
        # This starts a continous microphone recording clip which will be used to fetch
        # audio samples for Harmony's STT transcription module from
        if self.microphone_name is None or isinstance(self.microphone_name, str) and len(self.microphone_name) == 0:
            print 'No microphone available.'
            return False

        # Reset Buffer before starting recording
        self.recording_buffer = bytearray()
        self.dropped_buffer_bytes = 0

        print 'Recording with microphone: {0}'.format(self.microphone_name)
        self.recording_clip = Microphone.Start(self.microphone_name, True, self.record_stepping, self.sample_rate)
        # Wait until recording has started
        start_time = time.time()
        while not Microphone.IsRecording(self.microphone_name):
            if time.time() - start_time > 1.0:
                print 'Failed to start continuous recording.'
                return False
            time.sleep(0.1)
        print 'Continuous recording started.'
        self.recording_start_time = time.time()
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

        # Stop the recording thread
        if self.recording_thread is not None:
            self.recording_thread.stop()
            self.recording_thread.join()
            self.recording_thread = None

        print 'Continuous recording stopped.'
        return True

    def process_recording_request(self, event_id, start_time, duration):
        # Calculate start and end times relative to recording start
        current_time = time.time()
        start_time = start_time - self.recording_start_time
        if start_time < 0:
            start_time = 0.0
        print "Start time: {0}".format(start_time)
        end_time = start_time + duration
        print "End time: {0}".format(end_time)

        # Determine if we need to wait
        wait_time = end_time - (current_time - self.recording_start_time)
        if wait_time > 0:
            time.sleep(wait_time)

        # Calculate byte indices
        start_byte = int(start_time * self.bytes_per_second) - self.dropped_buffer_bytes
        end_byte = int(end_time * self.bytes_per_second) - self.dropped_buffer_bytes
        total_bytes = end_byte - start_byte

        # ensure we have the correct byte length in case of rounding errors
        end_byte += total_bytes % self.bytes_per_sample

        # Get bytes from buffer
        audio_bytes = self.recording_buffer[start_byte:end_byte]

        # # Encode to base64
        # encoded_data = base64.b64encode(audio_bytes)

        print "Length of audio_bytes:", len(audio_bytes)
        print "First 20 bytes of audio_bytes:", audio_bytes[:20]

        # Encode to base64
        encoded_data = base64.b64encode(audio_bytes)

        print "Length of encoded_data:", len(encoded_data)
        print "First 50 characters of encoded_data:", encoded_data[:50]

        # Send result event
        result_event = HarmonyLinkEvent(
            event_id=event_id,
            event_type=EVENT_TYPE_STT_FETCH_MICROPHONE_RESULT,
            status=EVENT_STATE_NEW,
            payload={
                'start_time': int(start_time * 1000),
                'duration': int(duration * 1000),
                'audio_bytes': encoded_data,
                'channels': self.channels,
                'bit_depth': self.bit_depth,
                'sample_rate': self.sample_rate,
            }
        )
        self.backend_connector.send_event(result_event)
        # Remove the event from the tracking
        del self.active_recording_events[event_id]

