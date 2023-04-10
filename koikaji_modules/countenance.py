# Koikaji Countenance Module
# (c) 2023 RuntimeRacer (runtimeracer@gmail.com)

# VNGE
from vngameengine import vnge_game as game
import vnlibfaceexpressions

# Import Backend base Module
from backend import *
from kajiwoto import RPC_ACTION_KAJIWOTO_EVENT_KAJI_SPEECH, RPC_ACTION_KAJIWOTO_EVENT_KAJI_STATUS


# CountenanceHandler - module main class
class CountenanceHandler(KoikajiBackendEventHandler):
    def __init__(self, backend_handler, countenance_config):
        # execute the base constructor
        KoikajiBackendEventHandler.__init__(self, backend_handler=backend_handler)
        # Set config
        self.config = countenance_config

    def handle_event(
            self,
            rpc_response  # KoikajiBackendRPCResponse
    ):
        # Kaji Status update
        if rpc_response.action == RPC_ACTION_KAJIWOTO_EVENT_KAJI_STATUS and rpc_response.result == RPC_RESULT_SUCCESS:
            self.update_kaji("", kaji_data=rpc_response.params)
            # TODO: Update face expression based on status context

        if rpc_response.action == RPC_ACTION_KAJIWOTO_EVENT_KAJI_SPEECH and rpc_response.result == RPC_RESULT_SUCCESS:

            utterance_data = rpc_response.params

            #if utterance_data["type"] == "UTTERANCE_NONVERBAL" and len(utterance_data["content"]) > 0:
                # TODO: Update face expression based on nonverbal context

        return
