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
        self.kaji = None

    def handle_event(
            self,
            rpc_response  # KoikajiBackendRPCResponse
    ):
        # Kaji Status update
        if rpc_response.action == RPC_ACTION_KAJIWOTO_EVENT_KAJI_STATUS and rpc_response.result == RPC_RESULT_SUCCESS:
            if self.kaji is None:
                self.kaji = rpc_response.params

            print 'Koikaji Backend: Updated status for Kaji "{0}":'.format(self.kaji.name)
            print 'Mood: {0}.'.format(self.kaji.mood)
            print 'Behaviour: {0}.'.format(self.kaji.behaviour)
            print 'Persona: {0}.'.format(self.kaji.persona)
            print 'Status Message: {0}.'.format(self.kaji.status_message)

            # TODO: Update chara

        return