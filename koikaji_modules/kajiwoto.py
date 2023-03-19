# Koikaji Kajiwoto Module
# (c) 2023 RuntimeRacer (runtimeracer@gmail.com)

# Import Backend base Module
from backend import *

# Actions
RPC_ACTION_KAJIWOTO_LOGIN = 'KAJIWOTO_LOGIN'
RPC_ACTION_KAJIWOTO_SELECT_ROOM = 'KAJIWOTO_SELECT_ROOM'
RPC_ACTION_KAJIWOTO_JOIN_ROOM = 'KAJIWOTO_JOIN_ROOM'

# Events
RPC_ACTION_KAJIWOTO_EVENT_KAJI_STATUS = 'KAJIWOTO_EVENT_KAJI_STATUS'
RPC_ACTION_KAJIWOTO_EVENT_KAJI_SPEECH = 'KAJIWOTO_EVENT_KAJI_SPEECH'
RPC_ACTION_KAJIWOTO_EVENT_KAJI_ACTION = 'KAJIWOTO_EVENT_KAJI_ACTION'


# KajiwotoHandler - module main class
class KajiwotoHandler(KoikajiBackendEventHandler):
    def __init__(self, backend_handler, kajiwoto_config):
        # execute the base constructor
        KoikajiBackendEventHandler.__init__(self, backend_handler=backend_handler)
        # Set config
        self.config = kajiwoto_config
        # Kaji Details - Put in map later to allow more than 1 Kaji
        self.kaji = None

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
            print 'Koikaji Backend: Kajiwoto login successful.'
            return True
        else:
            print 'Koikaji Backend: Kajiwoto login failed. Error: {0}'.format(response.params)
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
            self.kaji = Kaji(name=response.params["kaji_name"])
            print 'Koikaji Backend: Kaji room selected for Kaji: {0}.'.format(self.kaji.name)
            return True
        else:
            print 'Koikaji Backend: Kaji room selection failed. Error: {0}'.format(response.params)
            return False

    def join_room(self):
        action = KoikajiBackendRPCRequest(
            action=RPC_ACTION_KAJIWOTO_JOIN_ROOM,
            mode=RPC_MODE_SYNC,
            params={
                "kaji_room_id": self.config["kaji_room_id"],
                "kaji_name": self.kaji.name
            }
        )
        response, _, _ = self.backendHandler.perform_rpc_action(action)
        if response.result == RPC_RESULT_SUCCESS:
            self.kaji.room_id = response.params["kaji_id"]
            self.kaji.name = response.params["kaji_name"]
            self.kaji.mood = response.params["kaji_mood"]
            self.kaji.behaviour = response.params["kaji_behaviour"]
            self.kaji.persona = response.params["kaji_persona"]
            self.kaji.status_message = response.params["kaji_status_message"]
            print 'Koikaji Backend: joined room for Kaji: {0}.'.format(self.kaji.name)

            # Send Kaji Status Event
            status_update = KoikajiBackendRPCResponse(
                action=RPC_ACTION_KAJIWOTO_EVENT_KAJI_STATUS,
                result=RPC_RESULT_SUCCESS,
                params=self.kaji,
            )
            self.backendHandler.handle_rpc_response(status_update)

            return True
        else:
            print 'Koikaji Backend: joining Kaji room failed. Error: {0}'.format(response.params)
            return False


# Kaji - Internal representation for a Kaji
class Kaji:
    def __init__(self, room_id="", name="", mood="", behaviour="", persona="", status_message=""):
        self.room_id = room_id
        self.name = name
        self.mood = mood
        self.behaviour = behaviour
        self.persona = persona
        self.status_message = status_message
