# Koikaji Kajiwoto Module
# (c) 2023 RuntimeRacer (runtimeracer@gmail.com)

# Import Backend base Module
from backend import *
from kajiwoto import RPC_ACTION_KAJIWOTO_EVENT_KAJI_STATUS

# CountenanceHandler - module main class
class CountenanceHandler(KoikajiBackendEventHandler):
    def __init__(self, backend_handler, countenance_config):
        # execute the base constructor
        KoikajiBackendEventHandler.__init__(self, backend_handler=backend_handler)
        # Set config
        self.config = countenance_config
        # Kaji Details - Put in map later to allow more than 1 Kaji
        self.kaji_name = ""
        self.kaji_id = ""
        self.kaji_mood = ""
        self.kaji_behaviour = ""
        self.kaji_persona = ""
        self.kaji_status_message = ""

    def handle_event(
            self,
            rpc_response  # KoikajiBackendRPCResponse
    ):
        # Kaji Status update
        if rpc_response.action == RPC_ACTION_KAJIWOTO_EVENT_KAJI_STATUS and rpc_response.result == RPC_RESULT_SUCCESS:
            print 'Koikaji Backend: Updated status for Kaji "{0}":'.format(rpc_response.params["kaji_name"])
            print 'Mood: {0}.'.format(rpc_response.params["kaji_mood"])
            print 'Behaviour: {0}.'.format(rpc_response.params["kaji_behaviour"])
            print 'Persona: {0}.'.format(rpc_response.params["kaji_persona"])
            print 'Status Message: {0}.'.format(rpc_response.params["kaji_status_message"])

            # TODO: Update chara

        return