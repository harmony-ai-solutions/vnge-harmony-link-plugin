# Koikaji Backend Module
# (c) 2023 RuntimeRacer (runtimeracer@gmail.com)
#
# This module uses the .NET WebClient module to interface with Koikaji's Support Backend Module via RPC
# RPC Requests are simple JSON

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

# KoikajiBackendRPCRequest - Base class for request actions
class KoikajiBackendRPCRequest:
    def __init__(self, action, mode, params):
        self.action = action
        self.mode = mode
        self.params = params


# KoikajiCommsRPCResponse - Base class for response handling
class KoikajiBackendRPCResponse:
    def __init__(self, result, ticket_id, action, params):
        self.result = result
        self.ticket_id = ticket_id  # Ticket ID identifies the pending action for event handling
        self.action = action
        self.params = params


# KoikajiCheckResultsThread - Thread for checking on async requests being processed
class KoikajiCheckResultsThread(Thread):
    def __init__(self, endpoint, handler, interval_seconds=1):
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
        # Create action to check backend
        check = KoikajiBackendRPCRequest(RPC_ACTION_CHECK_PENDING_REQUESTS, RPC_MODE_SYNC, '')
        check_response = _do_rpc_call(client=self.webClient, endpoint=self.endpoint, request=check)
        _, processed, pending = self.handler.handle_rpc_response(response=check_response)

    def is_running(self):
        return self.running

    def stop_execution(self):
        print 'Stopping KoikajiCheckResultsThread'
        self.running = False


# KoiajiBackendHandler
class KoikajiBackendHandler:
    def __init__(self, endpoint):
        # Setup Backend Handler - Uses a simple HTTP client internally
        self.endpoint = endpoint
        self.webClient = _init_web_client()
        # Init job thread for checking on async requests
        self.checkAsyncResultsJob = KoikajiCheckResultsThread(endpoint=endpoint, handler=self)

    # start starts all subprocesses required for backend handling
    def start(self):
        print 'Starting KoikajiBackendHandler'
        if not self.checkAsyncResultsJob.is_running():
            self.checkAsyncResultsJob.start()

    def stop(self):
        # Stop thread in case it's still running
        print 'Stopping KoikajiBackendHandler'
        if self.checkAsyncResultsJob.is_running():
            print 'Starting KoikajiBackendHandler'
            self.checkAsyncResultsJob.stop_execution()
            self.checkAsyncResultsJob.join()

    # perform_rpc_action executes a backend action on the Support Backend Module
    # Upon
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
                response = json.dumps(response)
            return KoikajiBackendRPCResponse(RPC_RESULT_INVALID, '', response), processed, pending

        # check is failed request
        if response.result == RPC_RESULT_INVALID or response.result == RPC_RESULT_ERROR:
            # In case we ever need to handle sth. like that, add it here
            return response, processed, pending

        # Event handling if required
        if response.action == RPC_ACTION_CHECK_PENDING_REQUESTS:
            # Iterate over returned list of pending requests
            for action_json in response.result:
                if getattr(action_json, 'result') == RPC_RESULT_PENDING:
                    pending += 1
                else:
                    action_response = KoikajiBackendRPCResponse(**action_json)
                    self.handle_rpc_response(action_response)
                    processed += 1

        # Return response to initial caller
        return response, processed, pending


# _init_web_client - Always JSON, so we can set headers here once directly
def _init_web_client():
    web_client = WebClient()
    web_client.Headers.Add("Accept", "application/json")
    web_client.Headers.Add("Content-Type", "application/json")
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
        return KoikajiBackendRPCResponse(RPC_RESULT_INVALID, action, params)

    # Build and Execute the request
    request_string = json.dumps(request)
    response_string = client.UploadString(endpoint, request_string)
    # Check response & return
    if len(response_string) == 0:
        return KoikajiBackendRPCResponse(RPC_RESULT_INVALID, request.action, 'Response was empty!')
    response_json = json.loads(response_string)
    response = KoikajiBackendRPCResponse(**response_json)
    return response
