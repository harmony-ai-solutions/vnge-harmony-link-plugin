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
import os
import re

from harmony_modules.logging import get_logger

# Initialize logger for this module
logger = get_logger(__name__)

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
        self.stt_handler = stt_handler
        self.record_stepping = record_stepping  # in milliseconds
        self.sleep_time = record_stepping / 1000.0  # Convert to seconds
        self.last_sample_position = 0
        self.clip_samples = self.stt_handler.recording_clip.samples  # samples per channel
        self.channels = self.stt_handler.channels
        self.bytes_per_sample = self.stt_handler.bytes_per_sample
        self.bytes_per_second = self.stt_handler.bytes_per_second
        self.max_buffer_bytes = self.stt_handler.max_buffer_bytes

    def run(self):
        self.running = True
        while self.running:
            current_position = Microphone.GetPosition(self.stt_handler.microphone_name)
            sample_count = 0
            if current_position < self.last_sample_position:
                # Wrap-around occurred (positions are in samples per channel)
                sample_count = self.clip_samples - self.last_sample_position + current_position
            else:
                sample_count = current_position - self.last_sample_position

            if sample_count > 0:
                # Unity's GetData expects the data buffer length in total samples (interleaved across channels)
                total_samples_to_read = sample_count * self.channels
                samples = Array.CreateInstance(Single, total_samples_to_read)

                # Read samples from last_sample_position to current_position
                if current_position >= self.last_sample_position:
                    # No wrap-around
                    self.stt_handler.recording_clip.GetData(samples, self.last_sample_position)
                else:
                    # Wrap-around
                    first_part_length = (self.clip_samples - self.last_sample_position) * self.channels
                    first_part_samples = Array.CreateInstance(Single, first_part_length)
                    self.stt_handler.recording_clip.GetData(first_part_samples, self.last_sample_position)

                    second_part_length = current_position * self.channels
                    second_part_samples = Array.CreateInstance(Single, second_part_length)
                    self.stt_handler.recording_clip.GetData(second_part_samples, 0)

                    # Combine samples
                    first_part_samples.CopyTo(samples, 0)
                    second_part_samples.CopyTo(samples, first_part_length)

                # Convert samples to 16-bit PCM byte data (little-endian)
                # Clamp to [-1.0, 1.0], scale, then convert
                audio_bytes = b''.join([struct.pack('<h', int(max(min(s, 1.0), -1.0) * 32767)) for s in samples])

                # Lock the buffer while appending
                with self.stt_handler.buffer_lock:
                    # Append new audio bytes
                    self.stt_handler.recording_buffer.extend(audio_bytes)
                    # Remove oldest data if buffer exceeds max size
                    buffer_length = len(self.stt_handler.recording_buffer)
                    if buffer_length > self.max_buffer_bytes:
                        # Important: drop in multiples of block align (channels * bytes per sample) to avoid misalignment
                        excess_bytes = buffer_length - self.max_buffer_bytes
                        block_align = self.channels * self.bytes_per_sample
                        if excess_bytes % block_align != 0:
                            excess_bytes -= (excess_bytes % block_align)
                        if excess_bytes > 0:
                            del self.stt_handler.recording_buffer[:excess_bytes]
                            self.stt_handler.dropped_buffer_bytes += excess_bytes

                # Update last_sample_position (still in samples per channel)
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
        self.buffer_clip_duration = int(self.config['buffer_clip_duration'])  # seconds
        self.record_stepping = int(self.config['record_stepping'])  # milliseconds
        self.microphone_name = self.get_microphone()

        # Recording Handling
        self.is_recording_microphone = False
        self.active_recording_events = {}
        self.recording_buffer = None  # bytearray
        self.recording_clip = None  # AudioClip
        self.recording_start_time = None  # time.time
        self.recording_thread = None
        self.dropped_buffer_bytes = 0
        self.buffer_lock = Lock()
        
        # Control Operation synchronization
        self.operation_lock = Lock()           # Prevents overlapping start/stop operations
        self.processing_lock = Lock()          # Protects maps from concurrent access during audio chunk processing
        self.operation_in_progress = False     # Keeps track of ongoing start / stop recording operation
        
        # Calculate bytes per second
        self.bytes_per_sample = self.bit_depth // 8
        self.bytes_per_second = self.sample_rate * self.channels * self.bytes_per_sample
        # Calculate maximum buffer size in bytes
        self.max_buffer_bytes = self.bytes_per_second * self.buffer_clip_duration
        # Debug options (safe parse from config; default False)
        self.debug_save_python_wavs = self._to_bool(self.config.get('debug_save_python_wavs', False))
        self.debug_dir = os.path.join('harmony_debug_audio')
        self._ensure_debug_dir()

    def _to_bool(self, val):
        if isinstance(val, bool):
            return val
        try:
            s = str(val).strip().lower()
            return s in ('1', 'true', 'yes', 'y', 'on')
        except Exception:
            return False

    def _ensure_debug_dir(self):
        if self.debug_save_python_wavs:
            try:
                if not os.path.isdir(self.debug_dir):
                    os.makedirs(self.debug_dir)
            except Exception as e:
                logger.warn("Unable to create debug directory '%s': %s", self.debug_dir, str(e))

    def _sanitize(self, text):
        try:
            return re.sub(r'[^A-Za-z0-9_\-]+', '_', text or '')
        except Exception:
            return 'chunk'

    def _write_wav_file(self, pcm_bytes, filename_prefix, suffix=''):
        """
        Write a WAV file with PCM 16-bit little-endian data using current audio params.
        Ensures data chunk is aligned to block boundaries (channels * bytes_per_sample).
        """
        try:
            block_align = self.channels * self.bytes_per_sample
            data_size = len(pcm_bytes)
            # Align to block boundary (trim tail if not aligned)
            if data_size % block_align != 0:
                aligned_size = data_size - (data_size % block_align)
                logger.debug("Trimming WAV data from %s to %s bytes to maintain block alignment", data_size, aligned_size)
                pcm_bytes = pcm_bytes[:aligned_size]
                data_size = len(pcm_bytes)

            # WAV header fields
            chunk_size = 36 + data_size
            audio_format = 1  # PCM
            byte_rate = self.sample_rate * block_align
            bits_per_sample = self.bit_depth

            # File path
            timestamp = int(time.time() * 1000)
            safe_suffix = self._sanitize(suffix)
            file_name = "{0}_{1}_{2}.wav".format(filename_prefix, timestamp, safe_suffix) if safe_suffix else "{0}_{1}.wav".format(filename_prefix, timestamp)
            file_path = os.path.join(self.debug_dir, file_name)

            with open(file_path, 'wb') as f:
                # RIFF header
                f.write(b'RIFF')
                f.write(struct.pack('<I', chunk_size))
                f.write(b'WAVE')
                # fmt subchunk
                f.write(b'fmt ')
                f.write(struct.pack('<I', 16))  # Subchunk1Size for PCM
                f.write(struct.pack('<H', audio_format))  # AudioFormat
                f.write(struct.pack('<H', self.channels))  # NumChannels
                f.write(struct.pack('<I', self.sample_rate))  # SampleRate
                f.write(struct.pack('<I', byte_rate))  # ByteRate
                f.write(struct.pack('<H', block_align))  # BlockAlign
                f.write(struct.pack('<H', bits_per_sample))  # BitsPerSample
                # data subchunk
                f.write(b'data')
                f.write(struct.pack('<I', data_size))
                # PCM data
                f.write(pcm_bytes)

            logger.info("Saved debug WAV: %s (channels=%s, sample_rate=%s, bit_depth=%s, bytes=%s)",
                        file_path, self.channels, self.sample_rate, self.bit_depth, data_size)
        except Exception as e:
            logger.error("Failed to write debug WAV: %s", str(e))

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
            # This event fetches a slice of an audio clip recorded using the default microphone.
            # it will send the fetched audio to Harmony Link for VAD & STT transcription

            # Check if we're currently recording / Monkey check
            with self.operation_lock:
                if not self.is_recording_microphone:
                    logger.warning('tried to fetch from microphone while no recording in progress')
                    event.status = EVENT_STATE_ERROR
                    return

            # Get task details
            recording_task = event.payload
            # Extract parameters from recording task
            start_byte = recording_task.get('start_byte', 0)
            bytes_count = recording_task.get('bytes_count', self.bytes_per_second * 5)  # Default to 5 seconds

            try:
                with self.processing_lock:
                    # Store event to mark it as processing
                    self.active_recording_events[event.event_id] = event

                # Start a new thread to handle recording
                fetch_microphone_thread = Thread(
                    target=self.process_recording_request,
                    args=(event.event_id, start_byte, bytes_count)
                )
                fetch_microphone_thread.start()
            except Exception as e:
                logger.error("Failed to start processing thread for event %s: %s", event.event_id, str(e))
                with self.processing_lock:
                    # Store event to mark it as processing
                    del self.active_recording_events[event.event_id]

    def start_listen(self):
        """Start listening with enhanced synchronization protection"""
        with self.operation_lock:
            # Prevent overlapping operations or button spam
            if self.operation_in_progress or self.is_recording_microphone:
                logger.debug("Start listen blocked: operation_in_progress=%s, is_recording=%s", self.operation_in_progress, self.is_recording_microphone)
                return False

            self.operation_in_progress = True
            
            try:
                # Execute the actual start recording logic
                success = self._execute_start_recording()
                if success:
                    self.is_recording_microphone = True
                    logger.info('Recording started successfully')
                else:
                    logger.error('Failed to start recording')
                return success
            finally:
                self.operation_in_progress = False

    def _execute_start_recording(self):
        """Execute the actual start recording logic"""
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
                "result_mode": RESULT_MODE_RETURN if bool(self.config['auto_vad']) else RESULT_MODE_PROCESS,
                "channels": self.channels,
                "bit_depth": self.bit_depth,
                "sample_rate": self.sample_rate
            }
        )
        success = self.backend_connector.send_event(event)
        if not success:
            logger.error('Failed to send start_listen event to Harmony Link')
            # Clean up on failure
            self.stop_continuous_recording()
            return False
        
        return True

    def stop_listen(self):
        """Stop listening with graceful frame completion"""
        with self.operation_lock:
            # Prevent overlapping operations
            if self.operation_in_progress and not self.is_recording_microphone:
                logger.debug("Stop listen blocked: not currently recording")
                return False

            self.operation_in_progress = True
            
            try:
                # Wait for current audio fetch events to complete naturally
                self._wait_for_request_completion()
                
                # Execute the actual stop recording logic
                success = self._execute_stop_recording()
                if success:
                    self.is_recording_microphone = False
                    logger.info('Recording stopped successfully')
                else:
                    logger.error('Failed to stop recording cleanly')
                return success
            finally:
                self.operation_in_progress = False

    def _wait_for_request_completion(self, timeout=3.0):
        """Wait for currently processing audio fetch events to complete naturally"""
        with self.processing_lock:
            if not self.active_recording_events:
                return
            
        start_time = time.time()
        initial_count = 0
        remaining_count = 0
        with self.processing_lock:
            initial_count = remaining_count = len(self.active_recording_events)

        logger.debug("Waiting for %d audio fetch events to complete...", initial_count)
        while remaining_count > 0 and (time.time() - start_time) < timeout:
            time.sleep(0.1)
            with self.processing_lock:
                remaining_count = len(self.active_recording_events)

        # evaluate result of wait routine
        with self.processing_lock:
            remaining_count = len(self.active_recording_events)
            if remaining_count > 0:
                logger.warning("Timeout waiting for fetch completion, %d frames completed, %d may be lost", initial_count - remaining_count, remaining_count)
            else:
                logger.debug("All %d remaining audio fetches completed successfully", initial_count)

    def _execute_stop_recording(self):
        """Execute the actual stop recording logic"""
        # Send Event to Harmony Link to stop listening
        event = HarmonyLinkEvent(
            event_id='stop_listen',  # This is an arbitrary dummy ID to conform the Harmony Link API
            event_type=EVENT_TYPE_STT_STOP_LISTEN,
            status=EVENT_STATE_NEW,
            payload={}
        )
        success = self.backend_connector.send_event(event)
        if not success:
            logger.error('Failed to send stop_listen event to Harmony Link')
            return False

        # Stop recording to ongoing audio clip
        if not self.stop_continuous_recording():
            logger.error('Failed to stop continuous recording')
            return False

        return True

    def get_microphone(self):
        # Determine the microphone to use
        devices = Microphone.devices
        device_capabilities = {}
        microphone_name = self.config['microphone']
        # REMARK: Some Microphone names cannot be displayed on some Unity Versions
        # https://stackoverflow.com/questions/44250989/unity-design-flaw-how-to-distinguish-microphones-with-empty-names-or-same-name
        #
        # Therefore we explicitly allow microphone name to be an empty string
        if len(devices) <= 0:
            logger.warning('No microphone available.')
            return None
        else:
            logger.info('Available microphones:')
            for mic_id, device in enumerate(devices):
                # Get recording capabilities
                minFreq, maxFreq = Microphone.GetDeviceCaps(device)
                logger.info("%s : %s (MinFreq: %s, MaxFreq: %s)", mic_id, device, minFreq, maxFreq)
                device_capabilities[device] = (minFreq, maxFreq)

        if microphone_name == 'default':
            microphone_name = devices[0]
        elif microphone_name not in device_capabilities:
            logger.error('No microphone with provided name "%s" available.', microphone_name)
            return None

        # Check for correct sample rate being used
        minFreq, maxFreq = device_capabilities[microphone_name]
        if not minFreq == 0 and not maxFreq == 0:
            if self.sample_rate > maxFreq:
                self.sample_rate = maxFreq
                logger.warning("correcting sample rate from config to %s", self.sample_rate)
            elif self.sample_rate < minFreq:
                self.sample_rate = minFreq
                logger.warning("correcting sample rate from config to %s", self.sample_rate)

        return microphone_name

    def start_continuous_recording(self):
        # This starts a continous microphone recording clip which will be used to fetch
        # audio samples for Harmony's STT transcription module from

        # REMARK: Some Microphone names cannot be displayed on some Unity Versions
        # https://stackoverflow.com/questions/44250989/unity-design-flaw-how-to-distinguish-microphones-with-empty-names-or-same-name
        #
        # Therefore we explicitly allow microphone name to be an empty string
        if self.microphone_name is None or not isinstance(self.microphone_name, str):
            logger.error('No microphone available.')
            return False

        # Reset Buffer before starting recording
        self.recording_buffer = bytearray()
        self.dropped_buffer_bytes = 0

        logger.info('Recording with microphone: "%s"', self.microphone_name)
        # Use buffer_clip_duration for the clip length (in seconds); frequency is sample_rate
        self.recording_clip = Microphone.Start(self.microphone_name, True, self.buffer_clip_duration, self.sample_rate)
        # Wait until recording has started
        start_time = time.time()
        while not Microphone.IsRecording(self.microphone_name):
            if time.time() - start_time > 1.0:
                logger.error('Failed to start continuous recording.')
                return False
            time.sleep(0.1)
        logger.info('Continuous recording started.')
        self.recording_start_time = time.time()
        return True

    def stop_continuous_recording(self):
        if not self.is_recording_microphone or self.recording_clip is None or not Microphone.IsRecording(self.microphone_name):
            return False

        # Wait until all recording events have completed
        timeout_counter = 0
        while len(self.active_recording_events) > 0:
            if timeout_counter % 10 == 0:
                logger.debug('waiting for recording clips to finish...')
            if timeout_counter < 100:
                timeout_counter += 1
                time.sleep(0.1)
            else:
                logger.error('recording events did not finish within timeout of 10 seconds')
                return False

        # Stop the microphone recording
        Microphone.End(self.microphone_name)

        # Stop the recording thread
        if self.recording_thread is not None:
            self.recording_thread.stop()
            self.recording_thread.join()
            self.recording_thread = None

        logger.info('Continuous recording stopped.')
        return True

    def get_buffer_fetch_indices(self, start_byte, end_byte):
        actual_start_byte = start_byte - self.dropped_buffer_bytes
        actual_end_byte = end_byte - self.dropped_buffer_bytes
        buffer_size = len(self.recording_buffer)
        return actual_start_byte, actual_end_byte, buffer_size

    def process_recording_request(self, event_id, start_byte, bytes_count):
        """Process recording request"""
        # Get end byte
        end_byte = start_byte + bytes_count
        # Determine if we need to wait
        with self.buffer_lock:
            actual_start_byte, actual_end_byte, buffer_size = self.get_buffer_fetch_indices(start_byte, end_byte)

        # If start index is after current buffer boundary
        while actual_start_byte > buffer_size:
            time_till_buffer_reached = (actual_start_byte - buffer_size) / float(self.bytes_per_second)
            logger.debug('start index (%s) still exceeding buffer range (%s). Waiting for %d seconds.', actual_start_byte, buffer_size, time_till_buffer_reached)
            time.sleep(max(time_till_buffer_reached, 0.0))
            # Determine again if we need to wait more
            with self.buffer_lock:
                actual_start_byte, actual_end_byte, buffer_size = self.get_buffer_fetch_indices(start_byte, end_byte)

        # If end index is after current buffer boundary
        while actual_end_byte > buffer_size:
            time_till_buffer_reached = (actual_end_byte - buffer_size) / float(self.bytes_per_second)
            logger.debug('end index (%s) still exceeding buffer range (%s). Waiting for %d seconds.', actual_end_byte, buffer_size, time_till_buffer_reached)
            time.sleep(max(time_till_buffer_reached, 0.0))
            # Determine again if we need to wait more
            with self.buffer_lock:
                actual_start_byte, actual_end_byte, buffer_size = self.get_buffer_fetch_indices(start_byte, end_byte)

        # Get bytes from buffer
        with self.buffer_lock:
            actual_start_byte, actual_end_byte, buffer_size = self.get_buffer_fetch_indices(start_byte, end_byte)

            logger.debug("Bytes count: %s", bytes_count)
            logger.debug("Start byte (total / buffer): %s / %s", start_byte, start_byte - self.dropped_buffer_bytes)
            logger.debug("End byte (total / buffer): %s / %s", end_byte, end_byte - self.dropped_buffer_bytes)

            audio_bytes = self.recording_buffer[actual_start_byte:actual_end_byte]

        # DEBUG CODE: save chunk as WAV on Python side if enabled
        if self.debug_save_python_wavs:
            self._write_wav_file(audio_bytes, filename_prefix="mic_chunk", suffix=event_id)

        # DEBUG TRACE
        logger.trace("Length of audio_bytes: %s", len(audio_bytes))
        logger.trace("First 20 bytes of audio_bytes: %s", audio_bytes[:20])

        # Encode to base64
        encoded_data = self.encode_audio_data(audio_bytes)
        if encoded_data is None:
            logger.error("Failed to encode audio data for event %s", event_id)
            with self.processing_lock:
                del self.active_recording_events[event_id]
            return

        # Validate all parameters before sending
        if self.channels <= 0 or self.bit_depth <= 0 or self.sample_rate <= 0:
            logger.error("Invalid audio parameters: channels=%d, bit_depth=%d, sample_rate=%d", self.channels, self.bit_depth, self.sample_rate)
            with self.processing_lock:
                del self.active_recording_events[event_id]
            return

        # Send result event with actual audio data
        result_event = HarmonyLinkEvent(
            event_id=event_id,
            event_type=EVENT_TYPE_STT_FETCH_MICROPHONE_RESULT,
            status=EVENT_STATE_NEW,
            payload={
                'audio_bytes': encoded_data,
                'channels': self.channels,
                'bit_depth': self.bit_depth,
                'sample_rate': self.sample_rate,
            }
        )
        self.backend_connector.send_event(result_event)

        with self.processing_lock:
            # Remove the event from the tracking
            del self.active_recording_events[event_id]

    def encode_audio_data(self, audio_bytes):
        """safely encode audio data for transmission"""
        try:
            # Validate input
            if not audio_bytes or len(audio_bytes) == 0:
                logger.error("Empty audio data provided for encoding")
                return None

            # Log audio data stats for debugging
            logger.debug("Encoding audio data: %d bytes", len(audio_bytes))

            # Encode to base64 and explicitly decode to UTF-8 string
            encoded_bytes = base64.b64encode(audio_bytes)
            encoded_string = encoded_bytes.decode('utf-8', errors='strict')

            logger.debug("Successfully encoded %d bytes to %d character string", len(audio_bytes), len(encoded_string))
            return encoded_string

        except Exception as e:
            logger.error("Failed to encode audio data: %s", str(e))
            return None
