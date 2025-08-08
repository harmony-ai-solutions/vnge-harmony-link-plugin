# Harmony Link Connector Module for VNGE
# (c) 2023-2025 Project Harmony.AI (contact@project-harmony.ai)
#
# This module uses the .NET hooks to interface with Harmony Link's Event Backend
# Preferred Connection mode is WebSockets, which requires .NET Framework 4.5 or higher in the Game Libraries to work.
# However, if the Game does NOT support WebSockets yet, it does fallback to an async HTTP protocol using 2 web servers.
from System import Uri, Array, ArraySegment, Byte
from System.Text.Encoding import UTF8

# Import logging module
from harmony_modules.logging import get_logger

# Initialize logger for this module
logger = get_logger(__name__)

_use_websockets = False
_http_port_allocation_step = 0

try:
    from System.Net import WebSockets
    from System.Net.WebSockets import WebSocketMessageType, WebSocketState
    from System import AggregateException, InvalidOperationException
    from System.Threading import CancellationTokenSource, CancellationToken
    logger.info('WebSocket protocol supported. Communication will use WebSockets if enabled.')
    _use_websockets = True
except Exception as e:
    from System.Net import HttpWebRequest
    from System.IO import StreamReader
    import urllib
    import BaseHTTPServer
    logger.warning('WebSocket protocol not supported. Fallback to Async HTTP.')

from harmony_modules.common import HarmonyLinkEvent
from threading import Thread, current_thread
import json
import time


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
            logger.debug('ConnectorEventThread Received POST message: %s', post_data)
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
        self.shutting_down = False
        self.handler = handler
        if _use_websockets:
            # Set params
            self.ws_endpoint = ws_endpoint
            self.ws_buffer_size = ws_buffer_size
            # Initialize WebSocket Handling with unified cancellation token
            self.cts = CancellationTokenSource()
            self.web_socket_task = None
            self.web_socket_receive_task = None
        else:
            # Set params
            self.http_listen_port = http_listen_port
            # Initialize HTTP Server
            try:
                server_address = ('localhost', self.http_listen_port)
                self.http_server = BaseHTTPServer.HTTPServer(
                    server_address,
                    harmony_http_handler_factory(self),
                    bind_and_activate=False
                )
                try:
                    self.http_server.server_bind()
                    self.http_server.server_activate()
                except:
                    self.http_server.server_close()
                    raise
            except SystemError:
                logger.warning('localhost not working, trying with IP 127.0.0.1 ...')
                server_address = ('127.0.0.1', self.http_listen_port)
                self.http_server = BaseHTTPServer.HTTPServer(
                    server_address,
                    harmony_http_handler_factory(self),
                    bind_and_activate=False
                )
                try:
                    self.http_server.server_bind()
                    self.http_server.server_activate()
                except:
                    self.http_server.server_close()
                    raise
                pass

    def run(self):
        if _use_websockets:
            # Connect to Web Socket Backend with improved error handling
            if not self._establish_websocket_connection():
                logger.error('Failed to establish WebSocket connection. Shutting down...')
                self.handler.shutdown_func(self.handler.game)
                return

            # Init buffer
            connection_buffer = Array.CreateInstance(Byte, self.ws_buffer_size)
            connection_buffer_segment = ArraySegment[Byte](connection_buffer)
            
            # Set running
            logger.info('Starting ConnectorEventThread')
            self.running = True
            
            while self.running:
                # Check connection state before attempting to receive
                if not self._is_websocket_connected():
                    logger.warning('WebSocket connection lost. Attempting to reconnect...')
                    if not self._establish_websocket_connection():
                        logger.error('Failed to reconnect WebSocket. Shutting down...')
                        self.handler.shutdown_func(self.handler.game)
                        break
                    # Reinitialize buffer after reconnection
                    connection_buffer = Array.CreateInstance(Byte, self.ws_buffer_size)
                    connection_buffer_segment = ArraySegment[Byte](connection_buffer)

                # Creates an async receive task and monitors until we get data from the backend
                try:
                    self.web_socket_receive_task = self.handler.web_socket_client.ReceiveAsync(connection_buffer_segment, self.cts.Token)
                    self.web_socket_receive_task.Wait()

                    logger.debug("message received")

                    # Process data if task returns text data
                    if self.web_socket_receive_task.Result.MessageType == WebSocketMessageType.Text:
                        received_data = connection_buffer[:self.web_socket_receive_task.Result.Count]
                        message_string = UTF8.GetString(received_data)
                        self.process_event_message(message_string=message_string, session_id="")
                    else:
                        # Not a text message
                        continue
                except AggregateException as e:
                    # Check if this is a cancellation (normal shutdown) or an error
                    if self.shutting_down or self.cts.Token.IsCancellationRequested:
                        # This is expected during normal shutdown - don't log as error
                        logger.info('WebSocket connection cancelled (normal shutdown)')
                        break
                    else:
                        # This is an unexpected error - log it and attempt to reconnect
                        logger.error('websocket communication with Harmony Link failed: %s', e.ToString())
                        logger.warning('Unexpected WebSocket error. Attempting to reconnect...')
                        # Brief delay before reconnection attempt
                        time.sleep(2)
                        continue
                except Exception as e:
                    logger.error('Unexpected error in WebSocket receive loop: %s', str(e))
                    logger.info('Shutting down...')
                    self.handler.shutdown_func(self.handler.game)
                    break

            logger.info('ConnectorEventThread finished.')
        else:
            # Open HTTP Listenener and wait for messages
            # Set running
            logger.info('Starting ConnectorEventThread')
            self.running = True
            self.http_server.serve_forever()
            logger.info('ConnectorEventThread finished.')

    def _establish_websocket_connection(self):
        """Establish WebSocket connection with proper error handling and state verification"""
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                logger.info('Attempting WebSocket connection (attempt %s/%s)...', attempt + 1, max_retries)

                # Create connection task with timeout
                connection_timeout = CancellationTokenSource()
                connection_timeout.CancelAfter(10000)  # 10 second timeout
                
                self.web_socket_task = self.handler.web_socket_client.ConnectAsync(
                    Uri(self.ws_endpoint), 
                    connection_timeout.Token
                )
                self.web_socket_task.Wait()
                
                # Verify connection state
                if self._is_websocket_connected():
                    logger.info('WebSocket connection established successfully')
                    return True
                else:
                    logger.warning('WebSocket connection failed - invalid state: %s', self.handler.web_socket_client.State)

            except AggregateException as e:
                logger.warning('WebSocket connection attempt %s failed: %s', attempt + 1, e.ToString())

            except Exception as e:
                logger.warning('Unexpected error during WebSocket connection attempt %s: %s', attempt + 1, str(e))

            # Wait before retry (except on last attempt)
            if attempt < max_retries - 1:
                logger.info('Waiting %s seconds before retry...', retry_delay)
                time.sleep(retry_delay)
                # Try to close and recreate the WebSocket client for clean retry
                try:
                    if self.handler.web_socket_client.State != WebSocketState.Closed:
                        self.handler.web_socket_client.CloseAsync(WebSockets.WebSocketCloseStatus.NormalClosure, "Retry", getattr(CancellationToken, 'None')).Wait()
                except:
                    pass  # Ignore errors during cleanup
                
                # Recreate WebSocket client for next attempt
                self.handler.web_socket_client = _init_web_socket_client()

        logger.error('Failed to establish WebSocket connection after %s attempts', max_retries)
        return False

    def _is_websocket_connected(self):
        """Check if WebSocket is in a connected state"""
        try:
            return (self.handler.web_socket_client is not None and 
                    self.handler.web_socket_client.State == WebSocketState.Open)
        except:
            return False

    def process_event_message(self, message_string, session_id):
        if len(message_string) == 0:
            logger.warning('Message event was empty!')

        try:
            message_json = json.loads(message_string)
            logger.debug('Event message received: %s', message_string)
            message = HarmonyLinkEvent(**message_json)
            self.handler.handle_event(event=message, session_id=session_id)
        except ValueError as e:
            logger.error('failed to read event message: %s', str(e))
            logger.error('original message: %s', message_string)

    def is_running(self):
        return self.running

    def stop_execution(self):
        logger.info('Stopping ConnectorEventThread...')
        if _use_websockets:
            # Set shutdown flag before cancelling to suppress error messages
            self.shutting_down = True
            self.cts.Cancel()
        else:
            self.http_server.shutdown()
        self.running = False


# ConnectorEventHandler
class ConnectorEventHandler:
    global _use_websockets

    def __init__(self, ws_endpoint, ws_buffer_size, http_endpoint, http_listen_port, shutdown_func, game):
        global _http_port_allocation_step
        # Setup Config Params
        self.ws_endpoint = ws_endpoint
        self.ws_buffer_size = ws_buffer_size
        self.http_endpoint = http_endpoint
        self.http_listen_port = int(http_listen_port) + _http_port_allocation_step
        _http_port_allocation_step += 1
        self.harmony_session_id = ""

        # Setup Connector
        self.eventHandlers = []
        # Init clients required for comms
        if _use_websockets:
            self.web_socket_client = _init_web_socket_client()
        else:
            self.web_socket_client = None

        # Init job thread for checking on async requests
        self.eventJob = ConnectorEventThread(
            handler=self,
            ws_endpoint=self.ws_endpoint,
            ws_buffer_size=self.ws_buffer_size,
            http_listen_port=self.http_listen_port
        )
        # Plugin Shutdown Func in case Connector fails
        self.shutdown_func = shutdown_func
        self.game = game

    # start starts all subprocesses required for backend handling
    def start(self):
        logger.info('Starting ConnectorEventHandler')
        if not self.eventJob.is_running():
            self.eventJob.start()

    def stop(self):
        # Deactivate all connected Event Handlers
        if len(self.eventHandlers) > 0:
            for event_handler in self.eventHandlers:
                event_handler.deactivate()

        # Stop thread in case it's still running
        logger.info('Stopping ConnectorEventHandler')
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
            # Use a while loop here because on some systems the init event gets sent already, despite the
            # connection hasn't been fully established yet
            retries = 0
            while not self.eventJob.is_running() and retries < 5:
                logger.info('ConnectorEventHandler: Waiting for connection init...')
                time.sleep(1)
                retries += 1
            if not self.eventJob.is_running():
                logger.error('Failed to send message to Harmony Link: WebSocket Connection Handshake failed')
                return False
            
            # Additional check for WebSocket connection state
            if not self.eventJob._is_websocket_connected():
                logger.error('Failed to send message to Harmony Link: WebSocket not in connected state')
                return False
                
            return _send_web_socket_event(client=self.web_socket_client, event=event)
        else:
            success, response_body, response_headers = _send_http_event(
                endpoint=self.http_endpoint,
                session_id=self.harmony_session_id,
                result_port=str(self.http_listen_port),
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
            logger.warning('Invalid event received. Data: %s', event)
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
    # Check valid input and convert to HarmonyLinkEvent if needed
    if not isinstance(event, HarmonyLinkEvent):
        # If it's a dictionary, try to convert it to HarmonyLinkEvent
        if isinstance(event, dict):
            try:
                event = HarmonyLinkEvent(**event)
                logger.debug('Converted dictionary to HarmonyLinkEvent: %s', event.event_type)
            except Exception as e:
                logger.warning('Failed to convert dictionary to HarmonyLinkEvent: %s', str(e))
                logger.warning('Event data: %s', event)
                return False
        else:
            # If it's not a dict or HarmonyLinkEvent, it's invalid
            if not isinstance(event, str):
                event_str = json.dumps(event, cls=HarmonyEventJSONEncoder)
            else:
                event_str = event
            logger.warning('Tried to send invalid event. Data: %s', event_str)
            return False

    # Check WebSocket state before sending
    try:
        if client.State != WebSocketState.Open:
            logger.error('Failed to send message to Harmony Link: WebSocket not in Open state (current state: %s)', client.State)
            return False
    except Exception as e:
        logger.error('Failed to check WebSocket state: %s', str(e))
        return False

    # Serialize the event
    message_string = json.dumps(event, cls=HarmonyEventJSONEncoder)
    encoded_message = UTF8.GetBytes(message_string)
    send_buffer = Array[Byte](encoded_message)
    send_buffer_segment = ArraySegment[Byte](send_buffer)
    
    # Send it
    try:
        logger.debug('Sending WebSocket message: %s', message_string)
        send_task = client.SendAsync(send_buffer_segment, WebSocketMessageType.Text, True, getattr(CancellationToken, 'None'))
        send_task.Wait()
        logger.debug('WebSocket message sent successfully')
        return True
    except InvalidOperationException as e:
        logger.error('Failed to send message to Harmony Link: %s', e.ToString())
        return False
    except AggregateException as e:
        logger.error('Failed to send message to Harmony Link: %s', e.ToString())
        return False


# _do_rpc_call performs an RPC call to the Support Backend Module using provided client and endpoint
def _send_http_event(
        endpoint,  # str
        session_id,  # str
        result_port,  # str
        event,  # HarmonyLinkEvent
):
    # Check valid input and convert to HarmonyLinkEvent if needed
    if not isinstance(event, HarmonyLinkEvent):
        # If it's a dictionary, try to convert it to HarmonyLinkEvent
        if isinstance(event, dict):
            try:
                event = HarmonyLinkEvent(**event)
                logger.debug('Converted dictionary to HarmonyLinkEvent: %s', event.event_type)
            except Exception as e:
                logger.warning('Failed to convert dictionary to HarmonyLinkEvent: %s', str(e))
                logger.warning('Event data: %s', event)
                return False, None, None
        else:
            # If it's not a dict or HarmonyLinkEvent, it's invalid
            if not isinstance(event, str):
                event_str = json.dumps(event, cls=HarmonyEventJSONEncoder)
            else:
                event_str = event
            logger.warning('Tried to send invalid event. Data: %s', event_str)
            return False, None, None

    # Build and Execute the request
    message_string = json.dumps(event, cls=HarmonyEventJSONEncoder)

    # Create request
    request = HttpWebRequest.Create(endpoint)
    request.Method = "POST"
    request.Accept = "application/json"
    request.ContentType = "application/json"
    request.Headers.Add("Harmony-Session-Id", session_id)
    request.Headers.Add("Harmony-Result-Port", result_port)

    byte_array = UTF8.GetBytes(message_string)
    request.ContentLength = byte_array.Length
    data_stream = request.GetRequestStream()
    data_stream.Write(byte_array, 0, byte_array.Length)
    data_stream.Close()

    # Get response
    response = request.GetResponse()
    response_status_code = int(response.StatusCode)
    response_data = StreamReader(response.GetResponseStream()).ReadToEnd()
    response_headers = {}
    for i in range(response.Headers.Count):
        response_headers[response.Headers.Keys[i]] = response.Headers[i]
    response.Close()

    logger.info("Response code: %s - Message %s", response_status_code, response_data)
    logger.debug("Response headers: %s", json.dumps(response_headers))

    # Evaluate response
    if response_status_code != 200:
        logger.error('Failed to send message to Harmony Link: %s', response.reason)
        return False, None, None

    # Return response data
    return True, response_data, response_headers
