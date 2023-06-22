# Harmony Link Connector Module for VNGE
# (c) 2023 RuntimeRacer (runtimeracer@gmail.com)
#
# This module uses the .NET hooks to interface with Harmony Link's Event Backend
# Requires .NET Framework 4.5 or higher to work.
from System.Net import WebSockets
from System.Net.WebSockets import WebSocketMessageType
from System import AggregateException, InvalidOperationException
from System import Uri, Array, ArraySegment, Byte
from System.Text.Encoding import UTF8
from System.Threading import CancellationTokenSource, CancellationToken

from common import HarmonyLinkEvent
from threading import Thread, current_thread
import json

# Define Constants


# Define Classes
class HarmonyEventJSONEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


# ConnectorEventThread - Thread for checking on async requests being processed
class ConnectorEventThread(Thread):
    def __init__(self, handler, endpoint, buffer_size):
        # execute the base constructor
        Thread.__init__(self)
        # Control flow
        self.running = False
        # Set params
        self.endpoint = endpoint
        self.buffer_size = buffer_size
        self.handler = handler
        # Initialize WebSocket Handling
        self.cts = CancellationTokenSource()
        self.web_socket_task = None
        self.web_socket_receive_task = None

    def run(self):
        # Connect to Web Socket Backend
        try:
            self.web_socket_task = self.handler.web_socket_client.ConnectAsync(Uri(self.endpoint), CancellationToken.None)
            self.web_socket_task.Wait()  # This Directive ensures the task runs in background & handles WS heartbeat
        except AggregateException as e:
            print 'Unable to start websocket communication with Harmony Link: {0}'.format(e.ToString())
            return
        # Init buffer
        connection_buffer = Array.CreateInstance(Byte, self.buffer_size)
        connection_buffer_segment = ArraySegment[Byte](connection_buffer)
        # Set running
        print 'Starting ConnectorEventThread'
        self.running = True
        while self.running:
            # Creates an async receive task and monitors until we get data from the backend
            self.web_socket_receive_task = self.handler.web_socket_client.ReceiveAsync(connection_buffer_segment, self.cts.Token)
            self.web_socket_receive_task.Wait()

            # Process data if task returns text data
            if self.web_socket_receive_task.Result.MessageType == WebSocketMessageType.Text:
                received_data = connection_buffer[:self.web_socket_receive_task.Result.Count]
                message_string = UTF8.GetString(received_data)
                self.process_websocket_message(message_string)
            else:
                # Not a text message
                continue
        print 'ConnectorEventThread finished.'

    def process_websocket_message(self, message_string):
        if len(message_string) == 0:
            print 'Warning: WebSocket event was empty!'
        message_json = json.loads(message_string)
        message = HarmonyLinkEvent(**message_json)
        self.handler.handle_event(event=message)

    def is_running(self):
        return self.running

    def stop_execution(self):
        print 'Stopping ConnectorEventThread...'
        self.cts.Cancel()
        self.running = False


# ConnectorEventHandler
class ConnectorEventHandler:
    def __init__(self, endpoint, buffer_size):
        # Setup Connector
        self.endpoint = endpoint
        self.buffer_size = buffer_size
        self.eventHandlers = []
        self.web_socket_client = _init_web_socket_client()
        # Init job thread for checking on async requests
        self.eventJob = ConnectorEventThread(handler=self, endpoint=self.endpoint, buffer_size=self.buffer_size)

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
        return _send_web_socket_event(client=self.web_socket_client, event=event)

    # handle_event is used to forward events received via received websocket messages
    def handle_event(
            self,
            event  # HarmonyLinkEvent
    ):
        # Check is valid response
        if not isinstance(event, HarmonyLinkEvent):
            if not isinstance(event, str):
                event = json.dumps(event, cls=HarmonyEventJSONEncoder)
            print 'Warning: Invalid event received. Data: {0}'.format(event)
        else:
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
