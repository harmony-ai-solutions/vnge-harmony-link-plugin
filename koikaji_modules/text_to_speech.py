# Koikaji TTS Module
# (c) 2023 RuntimeRacer (runtimeracer@gmail.com)

import random
rng = random.WichmannHill()
# we will not use simple random because of bug
# see https://github.com/IronLanguages/ironpython2/issues/231 for details

# VNGE
from vnsound import SoundSource
from vngameengine import vnge_game as game

# Import Backend base Module
from backend import *
from kajiwoto import RPC_ACTION_KAJIWOTO_EVENT_KAJI_SPEECH, RPC_ACTION_KAJIWOTO_EVENT_KAJI_STATUS


# TextToSpeechHandler - main module class
class TextToSpeechHandler(KoikajiBackendEventHandler):
    def __init__(self, backend_handler, tts_config):
        # execute the base constructor
        KoikajiBackendEventHandler.__init__(self, backend_handler=backend_handler)
        # Set config
        self.config = tts_config
        # TTS Handling
        self.playing_utterance = None
        self.pending_utterances = []

    def handle_event(
            self,
            rpc_response  # KoikajiBackendRPCResponse
    ):
        # Kaji Status update
        if rpc_response.action == RPC_ACTION_KAJIWOTO_EVENT_KAJI_STATUS and rpc_response.result == RPC_RESULT_SUCCESS:
            self.update_kaji("", kaji_data=rpc_response.params)

        # Kaji Speech Utterance
        if rpc_response.action == RPC_ACTION_KAJIWOTO_EVENT_KAJI_SPEECH and rpc_response.result == RPC_RESULT_SUCCESS:

            utterance_data = rpc_response.params

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

                utterance_player.kaji_id = ""  # TODO Audio per Kaji later
                utterance_player.filename = audio_file
                print '[{0}]: Successfully loaded audio file: {1}'.format(self.__class__.__name__, audio_file)

                # Append to queue
                self.pending_utterances.append(utterance_player)
                # Play
                self.play_voice(kaji_id="")

            # TODO: Update chara to perform lipsync on play

        return

    def play_voice(self, kaji_id):
        if self.playing_utterance is not None:
            return

        if len(self.pending_utterances) > 0:
            self.playing_utterance = self.pending_utterances.pop(0)
            self.playing_utterance.Play()
            print '[{0}]: Playing audio file: {1}'.format(self.__class__.__name__, self.playing_utterance.filename)
            # add monitor job to check play status
            game.append_update_job(self.wait_voice_played)

    def wait_voice_played(self):
        if self.playing_utterance.isPlaying:
            # Add LipSync to chara
            self.fake_lipsync_update()
            # return false means job not done, it will run again in next update
            return False
        else:
            # here the sound file is played, you can mark some flag or delete the file
            print '[{0}]: done playing file: {1}!'.format(self.__class__.__name__, self.playing_utterance.filename)
            self.playing_utterance.Cleanup()
            # TODO: Send Message to Koikaji Backend to delete the source file from disk
            self.fake_lipsync_stop()
            # Recursive call to PlayVoice in case we have pending audios
            self.playing_utterance = None
            self.play_voice(kaji_id=self.playing_utterance.kaji_id)
            return True

    def fake_lipsync_stop(self):
        if self.chara is not None:
            self.chara.actor.set_mouth_open(0)

    def fake_lipsync_update(self):
        if self.chara is not None:
            mo = rng.random()
            if mo > 0.7:
                self.readingChar.set_mouth_open(1.0)
            else:
                self.readingChar.set_mouth_open(mo)
