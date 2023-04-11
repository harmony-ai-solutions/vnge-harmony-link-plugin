# Koikaji Backend Module
# (c) 2023 RuntimeRacer (runtimeracer@gmail.com)
#
# This module uses the .NET WebClient module to interface with Koikaji's Support Backend Module via RPC
# RPC Requests are simple JSON

# Next steps:
# 1. Instead of only Polling, use HttpListener
#    (https://learn.microsoft.com/de-de/dotnet/api/system.net.httplistener?view=netcore-2.1)
#    to handle events from external modules
# 2. Also consider using WebSocket directly, for faster and more streamlined handling of comms
#    (https://learn.microsoft.com/de-de/dotnet/api/system.net.websockets.clientwebsocket?view=netcore-2.1)
#

from System.Net import WebClient
from threading import Thread
import time
import json

# Define Constants

# Backend processing modes
RPC_MODE_SYNC = 'SYNC'  # This RPC Call is blocking; means we'll have to wait until support module finishes execution
RPC_MODE_ASYNC = 'ASYNC'  # This RPC Call is non-blocking; means we're waiting until

# Result types
RPC_RESULT_INVALID = 'INVALID_REQUEST'  # Default result if the request is malformed or calling an invalid action
RPC_RESULT_SUCCESS = 'SUCCESS'  # Request was handled and returned successfully
RPC_RESULT_ERROR = 'ERROR'  # Request returned a backend issue
RPC_RESULT_PENDING = 'PENDING'  # Request is in pending state (default response for async requests)

# Actions
RPC_ACTION_CHECK_PENDING_REQUESTS = 'CHECK_PENDING_REQUESTS'


# Define Classes
class KoikajiBackendJSONEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


# Kaji - Internal representation for a Kaji
class Kaji:
    def __init__(self, room_id="", name="", mood="", behaviour="", persona="", status_message=""):
        self.room_id = room_id
        self.name = name
        self.mood = mood
        self.behaviour = behaviour
        self.persona = persona
        self.status_message = status_message


# KoikajiBackendRPCRequest - Base class for request actions
class KoikajiBackendRPCRequest:
    def __init__(self, action, mode, params):
        self.action = action
        self.mode = mode
        self.params = params


# KoikajiCommsRPCResponse - Base class for response handling
class KoikajiBackendRPCResponse:
    def __init__(self, result, action, params, ticket_id=''):
        self.result = result
        self.action = action
        self.params = params
        self.ticket_id = ticket_id  # Ticket ID identifies the pending action for event handling


# KoikajiCheckResultsThread - Thread for checking on async requests being processed
class KoikajiCheckResultsThread(Thread):
    def __init__(self, endpoint, handler, interval_seconds=3):
        # execute the base constructor
        Thread.__init__(self)
        # Control flow
        self.running = False
        # Set params
        self.endpoint = endpoint
        self.handler = handler
        self.webClient = _init_web_client()
        self.interval_millis = interval_seconds if interval_seconds >= 0.1 else 0.1

    def run(self):
        # Set running
        print 'Starting KoikajiCheckResultsThread'
        self.running = True
        while self.running:
            self.check_async_requests()
            time.sleep(self.interval_millis)
        print 'KoikajiCheckResultsThread finished.'

    def check_async_requests(self):
        print 'Checking for pending requests in Koikaji Backend module...'
        check = KoikajiBackendRPCRequest(RPC_ACTION_CHECK_PENDING_REQUESTS, RPC_MODE_SYNC, '')
        check_response = _do_rpc_call(client=self.webClient, endpoint=self.endpoint, request=check)
        check_response, processed, pending = self.handler.handle_rpc_response(response=check_response)

        if check_response.result == RPC_RESULT_ERROR or check_response.result == RPC_RESULT_INVALID:
            print '... Pending request check failed. Result: {0}, Message: {1}'.format(check_response.result, check_response.params)
        else:
            print '... Pending request check done. Processed: {0}, Still pending: {1}'.format(processed, pending)

    def is_running(self):
        return self.running

    def stop_execution(self):
        print 'Stopping KoikajiCheckResultsThread...'
        self.running = False


# KoikajiBackendHandler
class KoikajiBackendHandler:
    def __init__(self, endpoint):
        # Setup Backend Handler - Uses a simple HTTP client internally
        self.endpoint = endpoint
        self.webClient = _init_web_client()
        self.eventHandlers = []
        # Init job thread for checking on async requests
        self.checkAsyncResultsJob = KoikajiCheckResultsThread(endpoint=endpoint, handler=self)

    # start starts all subprocesses required for backend handling
    def start(self):
        print 'Starting KoikajiBackendHandler'
        if not self.checkAsyncResultsJob.is_running():
            self.checkAsyncResultsJob.start()

    def stop(self):
        # Deactivate all connected Event Handlers
        if len(self.eventHandlers) > 0:
            for event_handler in self.eventHandlers:
                event_handler.deactivate()

        # Stop thread in case it's still running
        print 'Stopping KoikajiBackendHandler'
        if self.checkAsyncResultsJob.is_running():
            self.checkAsyncResultsJob.stop_execution()
            self.checkAsyncResultsJob.join()

    def register_event_handler(self, event_handler):
        if event_handler not in self.eventHandlers:
            self.eventHandlers.append(event_handler)

    def unregister_event_handler(self, event_handler):
        if event_handler in self.eventHandlers:
            self.eventHandlers.remove(event_handler)

    # perform_rpc_action executes a backend action on the Support Backend Module
    # Upon receiving the result, perform the handling task
    def perform_rpc_action(self, action):
        response = _do_rpc_call(client=self.webClient, endpoint=self.endpoint, request=action)
        return self.handle_rpc_response(response=response)

    # handle_rpc_response is used to trigger events based on an RPC action
    def handle_rpc_response(
            self,
            response  # KoikajiBackendRPCResponse
    ):
        # return params
        processed = 0
        pending = 0

        # Check is valid response
        if not isinstance(response, KoikajiBackendRPCResponse):
            if not isinstance(response, str):
                response = json.dumps(response, cls=KoikajiBackendJSONEncoder)
            return KoikajiBackendRPCResponse(result=RPC_RESULT_INVALID, action='', params=response), processed, pending

        # check is failed request
        if response.result == RPC_RESULT_INVALID or response.result == RPC_RESULT_ERROR:
            # In case we ever need to handle sth. like that, add it here
            return response, processed, pending

        # Event handling if required
        if response.action == RPC_ACTION_CHECK_PENDING_REQUESTS:
            # Iterate over returned list of pending requests
            for pending_response in response.params:
                if pending_response["result"] == RPC_RESULT_PENDING:
                    pending += 1
                else:
                    action_response = KoikajiBackendRPCResponse(**pending_response)
                    self.handle_rpc_response(action_response)
                    processed += 1
        else:
            # Broadcast to event handlers
            for event_handler in self.eventHandlers:
                event_handler.handle_event(response)

        # Return response to initial caller
        return response, processed, pending


# KoikajiBackendEventHandler - used for registering further modules for handling events
class KoikajiBackendEventHandler:
    def __init__(self, backend_handler):
        self.backendHandler = backend_handler
        self.active = False
        # Kaji Details - Put in dict later to allow more than 1 Kaji
        self.kaji = None
        # Chara Details - Put in dict later to allow more than 1 Chara
        self.chara = None

    def activate(self):
        self.backendHandler.register_event_handler(self)
        self.active = True

    def deactivate(self):
        self.backendHandler.unregister_event_handler(self)
        self.active = False

    def update_kaji(self, kaji_id, kaji_data):
        # TODO Add Handling by ID with kaji dict
        print '[{0}]: Updated Kaji:'.format(self.__class__.__name__)

        if kaji_data is None or len(kaji_data) == 0:
            self.kaji = None
            print '[{0}]: Kaji set to none'.format(self.__class__.__name__)

        if self.kaji is None:
            self.kaji = Kaji()

        self.kaji.id = kaji_data["kaji_id"]
        self.kaji.room_id = kaji_data["kaji_room_id"]
        self.kaji.name = kaji_data["kaji_name"]
        self.kaji.mood = kaji_data["kaji_mood"]
        self.kaji.behaviour = kaji_data["kaji_behaviour"]
        self.kaji.persona = kaji_data["kaji_persona"]
        self.kaji.status_message = kaji_data["kaji_status_message"]

        if isinstance(self.kaji, Kaji):
            print '[{0}]: Room ID: {1}'.format(self.__class__.__name__, self.kaji.room_id)
            print '[{0}]: Name: {1}.'.format(self.__class__.__name__, self.kaji.name)
            print '[{0}]: Mood: {1}.'.format(self.__class__.__name__, self.kaji.mood)
            print '[{0}]: Behaviour: {1}.'.format(self.__class__.__name__, self.kaji.behaviour)
            print '[{0}]: Persona: {1}.'.format(self.__class__.__name__, self.kaji.persona)
            print '[{0}]: Status Message: {1}.'.format(self.__class__.__name__, self.kaji.status_message)

    def update_chara(self, chara_id, chara):
        print '[{0}]: Updated Chara:'.format(self.__class__.__name__)
        self.chara = chara

    def handle_event(
            self,
            rpc_response  # KoikajiBackendRPCResponse
    ):
        # To be implemented in subclasses
        return


# _init_web_client - Always JSON, so we can set headers here once directly
def _init_web_client():
    web_client = WebClient()
    return web_client


# _do_rpc_call performs an RPC call to the Support Backend Module using provided client and endpoint
def _do_rpc_call(
        client,  # System.Net.WebClient
        endpoint,  # str
        request,  # KoikajiBackendRPCRequest
):
    # Check valid input
    if not isinstance(request, KoikajiBackendRPCRequest):
        action = request.action if hasattr(request, 'action') else ''
        params = request.params if hasattr(request, 'params') else request
        if not isinstance(params, str):
            params = json.dumps(params)
        return KoikajiBackendRPCResponse(result=RPC_RESULT_INVALID, action=action, params=params)

    # Build and Execute the request
    request_string = json.dumps(request, cls=KoikajiBackendJSONEncoder)
    try:
        client.Headers.Add("Accept", "application/json")
        client.Headers.Add("Content-Type", "application/json")
        response_string = client.UploadString(endpoint, request_string)
    except SystemError as e:
        return KoikajiBackendRPCResponse(result=RPC_RESULT_INVALID, action=request.action, params=e.message)
    # Check response & return
    if len(response_string) == 0:
        return KoikajiBackendRPCResponse(result=RPC_RESULT_INVALID, action=request.action, params='Response was empty!')
    response_json = json.loads(response_string)
    response = KoikajiBackendRPCResponse(**response_json)
    return response
