# Koikaji Countenance Module
# (c) 2023 RuntimeRacer (runtimeracer@gmail.com)

# Import Backend base Module
from backend import *

# Actions
RPC_ACTION_KAJISPEECH_START_LISTEN = 'KAJISPEECH_START_LISTEN'
RPC_ACTION_KAJISPEECH_STOP_LISTEN = 'KAJISPEECH_STOP_LISTEN'


# CountenanceHandler - module main class
class SpeechToTextHandler(KoikajiBackendEventHandler):
    def __init__(self, backend_handler, stt_config):
        # execute the base constructor
        KoikajiBackendEventHandler.__init__(self, backend_handler=backend_handler)
        # Set config
        self.config = stt_config
        # Recording Handling
        self.is_recording_microphone = False

    def start_listen(self, kaji_id):
        if self.is_recording_microphone:
            return False

        action = KoikajiBackendRPCRequest(
            action=RPC_ACTION_KAJISPEECH_START_LISTEN,
            mode=RPC_MODE_SYNC,
            params={}
        )
        response, _, _ = self.backendHandler.perform_rpc_action(action)
        if response.result == RPC_RESULT_SUCCESS:
            print 'Koikaji Backend: listening...'
            self.is_recording_microphone = True
            return True
        else:
            print 'Koikaji Backend: listen failed. Error: {0}'.format(response.params)
            return False

    def stop_listen(self, kaji_id):
        if not self.is_recording_microphone:
            return False

        action = KoikajiBackendRPCRequest(
            action=RPC_ACTION_KAJISPEECH_STOP_LISTEN,
            mode=RPC_MODE_SYNC,
            params={}
        )
        response, _, _ = self.backendHandler.perform_rpc_action(action)
        if response.result == RPC_RESULT_SUCCESS:
            print 'Koikaji Backend: listening stopped. Processing speech...'
            self.is_recording_microphone = False
            return True
        else:
            print 'Koikaji Backend: stop listen failed. Error: {0}'.format(response.params)
            return False

