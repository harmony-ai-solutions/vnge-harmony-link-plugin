# Harmony Link Plugin for VNGE
# (c) 2023-2025 Project Harmony.AI (contact@project-harmony.ai)
#
# This file contains all handling to be done with the Harmony Link TTS Module

# Import Client base Module
from harmony_modules.common import *

# VNGE
from vnsound import SoundSource
from vngameengine import vnge_game as game

import random
import time
from threading import Thread

from harmony_modules.logging import get_logger

# Initialize logger for this module
logger = get_logger(__name__)

rng = random.WichmannHill()
# we will not use simple random because of bug
# see https://github.com/IronLanguages/ironpython2/issues/231 for details


class TTSProcessorThread(Thread):
    def __init__(self, tts_handler, lipsync_interval=0.1):
        # execute the base constructor
        Thread.__init__(self)
        # Control flow
        self.running = False
        # Params
        self.tts_handler = tts_handler
        self.lipsync_interval = lipsync_interval if lipsync_interval >= 0.1 else 0.1
        # Audio playback state tracking
        self.playback_started = False
        self.start_time = time.time()
        self.min_playback_duration = 0.5  # Minimum time to wait before considering playback done

    def run(self):
        self.running = True
        while self.running:
            if not self.wait_voice_played():
                time.sleep(self.lipsync_interval)
                continue
            self.running = False

    def wait_voice_played(self):
        if not self.tts_handler.playing_utterance:
            logger.error('Tried to monitor an undefined utterance player!')
            return True

        current_time = time.time()
        elapsed_time = current_time - self.start_time

        # Check if audio is currently playing
        is_playing = self.tts_handler.playing_utterance.isPlaying
        
        if is_playing:
            # Track that we've seen playback start
            if not self.playback_started:
                self.playback_started = True
                logger.debug('Audio playback started for file: %s', self.tts_handler.playing_utterance.filename)
            
            # Add LipSync to chara
            self.tts_handler.fake_lipsync_update()
            # return false means job not done, it will run again in next update
            return False
        else:
            # Audio is not playing - but we need to be careful about timing
            
            # If we haven't seen playback start yet and it's been less than minimum duration,
            # keep waiting (audio system might still be initializing)
            if not self.playback_started and elapsed_time < self.min_playback_duration:
                logger.debug('Waiting for audio initialization (%.2fs elapsed)', elapsed_time)
                return False
            
            # If we've seen playback start, or enough time has passed, consider it done
            if self.playback_started:
                logger.debug('Audio playback completed for file: %s (played for %.2fs)', 
                           self.tts_handler.playing_utterance.filename, elapsed_time)
            else:
                logger.warning('Audio playback may have failed to start for file: %s (%.2fs elapsed)', 
                              self.tts_handler.playing_utterance.filename, elapsed_time)
            
            # Send Message to Harmony Link to delete the source file from disk
            playback_done_event = HarmonyLinkEvent(
                event_id='playback_done',  # This is an arbitrary dummy ID to conform the Harmony Link API
                event_type=EVENT_TYPE_TTS_PLAYBACK_DONE,
                status=EVENT_STATE_NEW,
                payload=self.tts_handler.playing_utterance.filename
            )
            self.tts_handler.backend_connector.send_event(playback_done_event)
            self.tts_handler.playing_utterance.Cleanup()
            self.tts_handler.fake_lipsync_stop()
            # Recursive call to PlayVoice in case we have pending audios for this AI Entity
            self.tts_handler.playing_utterance = None
            self.tts_handler.play_voice()
            return True


# TextToSpeechHandler - main module class
class TextToSpeechHandler(HarmonyClientModuleBase):
    def __init__(self, entity_controller, tts_config):
        # execute the base constructor
        HarmonyClientModuleBase.__init__(self, entity_controller=entity_controller)
        # Set config
        self.config = tts_config
        # TTS Handling
        self.speech_suppressed = False
        self.playing_utterance = None
        self.pending_utterances = []

    def handle_event(
            self,
            event  # HarmonyLinkEvent
    ):
        # AI Status update
        if event.event_type == EVENT_TYPE_AI_STATUS and event.status == EVENT_STATE_DONE:
            self.update_ai_state(ai_state=event.payload)

        # AI Speech Utterance
        if (
                event.event_type == EVENT_TYPE_AI_SPEECH or
                event.event_type == EVENT_TYPE_AI_ACTION
        ) and event.status == EVENT_STATE_DONE:

            utterance_data = event.payload
            audio_file = utterance_data["audio_file"]

            if len(audio_file) > 0:
                # Just abort here if speech is suppressed for this actor
                if self.speech_suppressed:
                    logger.info('Speech currently suppressed. Ignoring utterance')
                    # Send Message to Harmony Link to delete the source file from disk
                    playback_done_event = HarmonyLinkEvent(
                        event_id='playback_done',  # This is an arbitrary dummy ID to conform the Harmony Link API
                        event_type=EVENT_TYPE_TTS_PLAYBACK_DONE,
                        status=EVENT_STATE_NEW,
                        payload=audio_file
                    )
                    self.backend_connector.send_event(playback_done_event)
                    return

                # Build Sound source and queue it for playing
                # soundType can be "BGM", "ENV", "SystemSE" or "GameSE"
                # they are almost the same but with separated volume control in studio setting
                utterance_sound_type = "BGM"
                utterance_player = SoundSource()
                err = utterance_player.CreateAudioSource(utterance_sound_type)
                if err:
                    utterance_player.Cleanup()
                    logger.error('Unable to create sound source: %s', err)
                    return

                # load file
                err = utterance_player.LoadAudioFile(audio_file)
                if err:
                    utterance_player.Cleanup()
                    logger.error('Unable to load audio file: %s', err)
                    return

                utterance_player.filename = audio_file
                logger.info('Successfully loaded audio file: %s', audio_file)

                # Append to queue
                self.pending_utterances.append(utterance_player)
                # Play
                self.play_voice()

            # TODO: Update chara to perform lipsync on play

        return

    def play_voice(self):
        if self.playing_utterance is not None:
            return

        if len(self.pending_utterances) > 0:
            self.playing_utterance = self.pending_utterances.pop(0)
            self.playing_utterance.Play()
            logger.info('Playing audio file: %s', self.playing_utterance.filename)
            # add monitor job to check play status and perform lipsync updates
            TTSProcessorThread(tts_handler=self).start()

    def suppress_speech(self, suppress=False):
        # Update suppression mode
        # if not suppressed, just return
        self.speech_suppressed = suppress
        if not self.speech_suppressed:
            return

        if self.playing_utterance is None:
            return

        self.playing_utterance.Stop()
        self.playing_utterance.Cleanup()
        self.playing_utterance = None
        self.pending_utterances = []
        self.fake_lipsync_stop()

    def fake_lipsync_stop(self):
        if self.chara is not None:
            self.chara.actor.set_mouth_open(0)

    def fake_lipsync_update(self):
        if self.chara is not None:
            mo = rng.random()
            if mo > 0.7:
                self.chara.actor.set_mouth_open(1.0)
            else:
                self.chara.actor.set_mouth_open(mo)
