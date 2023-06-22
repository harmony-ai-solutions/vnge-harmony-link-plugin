# Harmony Link Plugin for VNGE
# (c) 2023 RuntimeRacer (runtimeracer@gmail.com)
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

    def run(self):
        self.running = True
        while self.running:
            if not self.wait_voice_played():
                time.sleep(self.lipsync_interval)
                continue
            self.running = False

    def wait_voice_played(self):
        if self.tts_handler.playing_utterance.isPlaying:
            # Add LipSync to chara
            self.tts_handler.fake_lipsync_update()
            # return false means job not done, it will run again in next update
            return False
        else:
            # here the sound file is played, you can mark some flag or delete the file
            print '[{0}]: done playing file: {1}!'.format(self.tts_handler.__class__.__name__, self.tts_handler.playing_utterance.filename)
            self.tts_handler.playing_utterance.Cleanup()
            # TODO: Send Message to Harmony Link to delete the source file from disk
            self.tts_handler.fake_lipsync_stop()
            # Recursive call to PlayVoice in case we have pending audios for this AI Entity
            self.tts_handler.playing_utterance = None
            self.tts_handler.play_voice()
            return True


# TextToSpeechHandler - main module class
class TextToSpeechHandler(HarmonyClientModuleBase):
    def __init__(self, backend_handler, tts_config):
        # execute the base constructor
        HarmonyClientModuleBase.__init__(self, backend_handler=backend_handler)
        # Set config
        self.config = tts_config
        # TTS Handling
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
        if event.event_type == EVENT_TYPE_AI_SPEECH and event.state == EVENT_STATE_DONE:

            utterance_data = event.payload

            if utterance_data["type"] == "UTTERANCE_VERBAL" and len(utterance_data["audio_file"]) > 0:
                audio_file = utterance_data["audio_file"]
                # Build Sound source and queue it for playing
                # soundType can be "BGM", "ENV", "SystemSE" or "GameSE"
                # they are almost the same but with separated volume control in studio setting
                utterance_sound_type = "BGM"
                utterance_player = SoundSource()
                err = utterance_player.CreateAudioSource(utterance_sound_type)
                if err:
                    utterance_player.Cleanup()
                    print '[{0}]: Unable to create sound source: {1}'.format(self.__class__.__name__, err)
                    return

                # load file
                err = utterance_player.LoadAudioFile(audio_file)
                if err:
                    utterance_player.Cleanup()
                    print '[{0}]: Unable to load audio file: {1}'.format(self.__class__.__name__, err)
                    return

                utterance_player.filename = audio_file
                print '[{0}]: Successfully loaded audio file: {1}'.format(self.__class__.__name__, audio_file)

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
            print '[{0}]: Playing audio file: {1}'.format(self.__class__.__name__, self.playing_utterance.filename)
            # add monitor job to check play status and perform lipsync updates
            TTSProcessorThread(tts_handler=self).start()

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
