# Koikaji Kajiwoto Module
# (c) 2023 RuntimeRacer (runtimeracer@gmail.com)

# Import Backend base Module
from backend import *

# Actions
RPC_ACTION_KAJIWOTO_LOGIN = 'KAJIWOTO_LOGIN'
RPC_ACTION_KAJIWOTO_SELECT_ROOM = 'KAJIWOTO_SELECT_ROOM'


# KajiwotoHandler - module main class
class KajiwotoHandler(KoikajiBackendEventHandler):
    def __init__(self, backend_handler, kajiwoto_config):
        # execute the base constructor
        KoikajiBackendEventHandler.__init__(self, backend_handler=backend_handler)
        # Set config
        self.config = kajiwoto_config

    def handle_event(
            self,
            rpc_response  # KoikajiBackendRPCResponse
    ):
        # To be implemented in subclasses
        return

    def login(self):
        action = KoikajiBackendRPCRequest(
            action=RPC_ACTION_KAJIWOTO_LOGIN,
            mode=RPC_MODE_SYNC,
            params={
                "username": self.config["username"],
                "password": self.config["password"]
            }
        )
        response, _, _ = self.backendHandler.perform_rpc_action(action)
        if response.result == RPC_RESULT_SUCCESS:
            print 'Koikaji Backend Kajiwoto login successful.'
            return True
        else:
            print 'Koikaji Backend Kajiwoto login failed. Error: {0}'.format(response.params)
            return False

    def select_room(self):
        action = KoikajiBackendRPCRequest(
            action=RPC_ACTION_KAJIWOTO_SELECT_ROOM,
            mode=RPC_MODE_SYNC,
            params={
                "kaji_room_id": self.config["kaji_room_id"]
            }
        )
        response, _, _ = self.backendHandler.perform_rpc_action(action)
        if response.result == RPC_RESULT_SUCCESS:
            print 'Koikaji Backend Kaji room selected for Kaji: {0}.'.format(response.params["kaji_name"])
            return True
        else:
            print 'Koikaji Backend Kaji room selection failed. Error: {0}'.format(response.params)
            return False



# Kaji - Internal representation for a Kaji
class Kaji:
    def __init__(self, state):
        self.state = state
