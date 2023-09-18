# Harmony Link Connector Module for VNGE
# (c) 2023 RuntimeRacer (runtimeracer@gmail.com)
#
# This module uses the .NET hooks to interface with Harmony Link's Event Backend
# Preferred Connection mode is WebSockets, which requires .NET Framework 4.5 or higher in the Game Libraries to work.
# However, if the Game does NOT support WebSockets yet, it does fallback to an async HTTP protocol using 2 web servers.
from System import Uri, Array, ArraySegment, Byte
from System.Text.Encoding import UTF8

_use_websockets = False

try:
    from System.Net import WebSockets
    from System.Net.WebSockets import WebSocketMessageType
    from System import AggregateException, InvalidOperationException
    from System.Threading import CancellationTokenSource, CancellationToken
    print 'WebSocket protocol supported. Communication will use WebSockets if enabled.'
    _use_websockets = True
except Exception as e:
    from System.Net import WebClient, WebException
    from System.IO import StreamReader

    import urllib
    import BaseHTTPServer
    print 'WebSocket protocol not supported. Fallback to Async HTTP.'

from harmony_modules.common import HarmonyLinkEvent
from threading import Thread, current_thread
import json


# Define Classes
class HarmonyEventJSONEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__

def harmony_http_handler_factory(connector_thread):
    class HarmonyEventHTTPHandler(BaseHTTPServer.BaseHTTPRequestHandler):
        def do_POST(self):
            # Read data
            session_id = self.headers['Harmony-Session-Id']
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            print 'DEBUG: ConnectorEventThread Received POST message: {0}'.format(post_data)
            # Forward received data to connector
            connector_thread.process_event_message(message_string=post_data, session_id=session_id)
            # Send OK back to sender
            self.send_response(200)
            self.end_headers()

    return HarmonyEventHTTPHandler

# ConnectorEventThread - Thread for checking on async requests being processed
class ConnectorEventThread(Thread):
    global _use_websockets

    def __init__(self, handler, ws_endpoint, ws_buffer_size, http_listen_port):
        # execute the base constructor
        Thread.__init__(self)
        # Control flow
        self.running = False
        self.handler = handler
        if _use_websockets:
            # Set params
            self.ws_endpoint = ws_endpoint
            self.ws_buffer_size = ws_buffer_size
            # Initialize WebSocket Handling
            self.cts = CancellationTokenSource()
            self.web_socket_task = None
            self.web_socket_receive_task = None
        else:
            # Set params
            self.http_listen_port = int(http_listen_port)
            # Initialize HTTP Server
            server_address = ('', self.http_listen_port)
            self.http_server = BaseHTTPServer.HTTPServer(server_address, harmony_http_handler_factory(self))

    def run(self):
        if _use_websockets:
            # Connect to Web Socket Backend
            try:
                self.web_socket_task = self.handler.web_socket_client.ConnectAsync(Uri(self.ws_endpoint), CancellationToken.None)
                self.web_socket_task.Wait()  # This Directive ensures the task runs in background & handles WS heartbeat
            except AggregateException as e:
                print 'Unable to start websocket communication with Harmony Link: {0}'.format(e.ToString())
                print 'Shutting down...'
                self.handler.shutdown_func(self.handler.game)
                return
            # Init buffer
            connection_buffer = Array.CreateInstance(Byte, self.ws_buffer_size)
            connection_buffer_segment = ArraySegment[Byte](connection_buffer)
            # Set running
            print 'Starting ConnectorEventThread'
            self.running = True
            while self.running:
                # Creates an async receive task and monitors until we get data from the backend
                try:
                    self.web_socket_receive_task = self.handler.web_socket_client.ReceiveAsync(connection_buffer_segment, self.cts.Token)
                    self.web_socket_receive_task.Wait()

                    print "message received"

                    # Process data if task returns text data
                    if self.web_socket_receive_task.Result.MessageType == WebSocketMessageType.Text:
                        received_data = connection_buffer[:self.web_socket_receive_task.Result.Count]
                        message_string = UTF8.GetString(received_data)
                        self.process_event_message(message_string=message_string, session_id="")
                    else:
                        # Not a text message
                        continue
                except AggregateException as e:
                    print 'websocket communication with Harmony Link failed: {0}'.format(e.ToString())
                    print 'Shutting down...'
                    self.handler.shutdown_func(self.handler.game)

            print 'ConnectorEventThread finished.'
        else:
            # Open HTTP Listenener and wait for messages
            # Set running
            print 'Starting ConnectorEventThread'
            self.running = True
            self.http_server.serve_forever()
            print 'ConnectorEventThread finished.'

    def process_event_message(self, message_string, session_id):
        if len(message_string) == 0:
            print 'Warning: Message event was empty!'

        try:
            message_json = json.loads(message_string)
            print 'DEBUG: Event message received: {0}'.format(message_string)
            message = HarmonyLinkEvent(**message_json)
            self.handler.handle_event(event=message, session_id=session_id)
        except ValueError as e:
            print 'failed to read event message: {0}'.format(str(e))
            print 'original message: {0}'.format(message_string)

    def is_running(self):
        return self.running

    def stop_execution(self):
        print 'Stopping ConnectorEventThread...'
        if _use_websockets:
            self.cts.Cancel()
        else:
            self.http_server.shutdown()
        self.running = False


# ConnectorEventHandler
class ConnectorEventHandler:
    global _use_websockets

    def __init__(self, ws_endpoint, ws_buffer_size, http_endpoint, http_listen_port, shutdown_func, game):
        # Setup Connector
        self.eventHandlers = []
        # Init job thread for checking on async requests
        self.eventJob = ConnectorEventThread(
            handler=self,
            ws_endpoint=ws_endpoint,
            ws_buffer_size=ws_buffer_size,
            http_listen_port=http_listen_port
        )
        # Init clients required for comms
        if _use_websockets:
            self.web_socket_client = _init_web_socket_client()
        else:
            self.http_endpoint = http_endpoint
            self.http_listen_port = http_listen_port
            self.harmony_session_id = ""
        # Plugin Shutdown Func in case Connector fails
        self.shutdown_func = shutdown_func
        self.game = game

    # start starts all subprocesses required for backend handling
    def start(self):
        print 'Starting ConnectorEventHandler'
        if not self.eventJob.is_running():
            self.eventJob.start()

    def stop(self):
        # Deactivate all connected Event Handlers
        if len(self.eventHandlers) > 0:
            for event_handler in self.eventHandlers:
                event_handler.deactivate()

        # Stop thread in case it's still running
        print 'Stopping ConnectorEventHandler'
        if self.eventJob.is_running():
            self.eventJob.stop_execution()
            if self.eventJob is not current_thread():
                self.eventJob.join()

    def register_event_handler(self, event_handler):
        if event_handler not in self.eventHandlers:
            self.eventHandlers.append(event_handler)

    def unregister_event_handler(self, event_handler):
        if event_handler in self.eventHandlers:
            self.eventHandlers.remove(event_handler)

    # perform_rpc_action executes a backend action on the Support Backend Module
    # Upon receiving the result, perform the handling task
    def send_event(self, event):
        if _use_websockets:
            return _send_web_socket_event(client=self.web_socket_client, event=event)
        else:
            success, response_body, response_headers = _send_http_event(
                endpoint=self.http_endpoint,
                session_id=self.harmony_session_id,
                result_port=self.http_listen_port,
                event=event
            )

            # Check if failed
            if success is False:
                return False
            # If successful, update harmony session ID
            session_id = response_headers["Harmony-Session-Id"]
            if len(session_id) > 0:
                self.harmony_session_id = session_id
            # Return success
            return True

    # handle_event is used to forward events received via received websocket messages
    def handle_event(
            self,
            session_id,
            event  # HarmonyLinkEvent
    ):
        # Check is valid response
        if not isinstance(event, HarmonyLinkEvent):
            if not isinstance(event, str):
                event = json.dumps(event, cls=HarmonyEventJSONEncoder)
            print 'Warning: Invalid event received. Data: {0}'.format(event)
        else:
            if _use_websockets or len(session_id) > 0 and session_id == self.harmony_session_id:
                # Broadcast to event handlers
                for event_handler in self.eventHandlers:
                    event_handler.handle_event(event)


# _init_web_socket_client - Initializes a .NET WebSocket Client
def _init_web_socket_client():
    # Create a WebSocket client
    web_socket = WebSockets.ClientWebSocket()
    return web_socket


# _send_web_socket_event sends a WebSocket Event to Harmony Link using the provided client
def _send_web_socket_event(
        client,  # System.Net.WebSockets.ClientWebSocket
        event,  # HarmonyLinkEvent
):
    # Check valid input
    if not isinstance(event, HarmonyLinkEvent):
        if not isinstance(event, str):
            event = json.dumps(event, cls=HarmonyEventJSONEncoder)
        print 'Warning: Tried to send invalid event. Data: {0}'.format(event)
        return

    # Serialize the event
    message_string = json.dumps(event, cls=HarmonyEventJSONEncoder)
    encoded_message = UTF8.GetBytes(message_string)
    send_buffer = Array[Byte](encoded_message)
    send_buffer_segment = ArraySegment[Byte](send_buffer)
    # Send it
    try:
        send_task = client.SendAsync(send_buffer_segment, WebSocketMessageType.Text, True, CancellationToken.None)
        send_task.Wait()
        return True
    except InvalidOperationException as e:
        print 'Failed to send message to Harmony Link: {0}'.format(e.ToString())
        return False


# _do_rpc_call performs an RPC call to the Support Backend Module using provided client and endpoint
def _send_http_event(
        endpoint,  # str
        session_id,  # str
        result_port,  # str
        event,  # HarmonyLinkEvent
):
    # Check valid input
    if not isinstance(event, HarmonyLinkEvent):
        if not isinstance(event, str):
            event = json.dumps(event, cls=HarmonyEventJSONEncoder)
        print 'Warning: Tried to send invalid event. Data: {0}'.format(event)
        return

    # Build and Execute the request
    message_string = json.dumps(event, cls=HarmonyEventJSONEncoder)

    # Create WebClient instance
    client = WebClient()
    # Set headers
    client.Headers["Accept"] = "application/json"
    client.Headers["Content-Type"] = "application/json"
    client.Headers["Harmony-Session-Id"] = session_id
    client.Headers["Harmony-Result-Port"] = result_port

    try:
        # Send request and get response data
        response_data = client.UploadString(endpoint, "POST", message_string)
        # Assuming a successful response, status code would be 200 OK
        response_status_code = 200

    except WebException as e:
        # This block will handle HTTP error status codes
        if e.Response:
            response_status_code = int(e.Response.StatusCode)

            # To read the error response body (if any)
            response = e.Response
            response_stream = response.GetResponseStream()
            reader = StreamReader(response_stream)
            response_data = reader.ReadToEnd()
            response_headers = {}
            for i in range(response.Headers.Count):
                response_headers[response.Headers.Keys[i]] = response.Headers[i]
            reader.Close()

            print "Response code: {0} - Message {1}".format(response_status_code, response_data)
            print "Response headers: {0}".format(json.dumps(response_headers))

            print 'Failed to send message to Harmony Link: {0}'.format(response.reason)
            return False, None, None
        else:
            # Handle other web exceptions, which might not be tied to an HTTP status code
            print 'Failed to send message to Harmony Link: {0}'.format(e)
            return False, None, None

    finally:
        # Handling response headers and closing the client
        response_headers = {}
        for key in client.ResponseHeaders.AllKeys:
            response_headers[key] = client.ResponseHeaders[key]

        client.Dispose()

    print "Response code: {0} - Message {1}".format(response_status_code, response_data)
    print "Response headers: {0}".format(json.dumps(response_headers))

    # Return response data
    return True, response_data, response_headers
