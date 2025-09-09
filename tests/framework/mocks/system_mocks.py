"""
System.Net Mock Classes for VNGE Harmony Link Plugin Testing

This module provides comprehensive mock implementations of System.Net classes
that are used by the VNGE plugin, enabling testing without .NET dependencies.
"""

import sys
import time
import threading
import json
from collections import deque


class MockWebSocketState:
    """Mock implementation of System.Net.WebSockets.WebSocketState enum"""
    
    None_ = 0
    Connecting = 1
    Open = 2
    CloseSent = 3
    CloseReceived = 4
    Closed = 5
    Aborted = 6


class MockWebSocketMessageType:
    """Mock implementation of System.Net.WebSockets.WebSocketMessageType enum"""
    
    Text = 0
    Binary = 1
    Close = 2


class MockWebSocketCloseStatus:
    """Mock implementation of System.Net.WebSockets.WebSocketCloseStatus enum"""
    
    NormalClosure = 1000
    EndpointUnavailable = 1001
    ProtocolError = 1002
    UnsupportedData = 1003
    NoStatusReceived = 1005
    AbnormalClosure = 1006
    InvalidPayloadData = 1007
    PolicyViolation = 1008
    MessageTooBig = 1009
    MandatoryExtension = 1010
    InternalServerError = 1011


class MockCancellationToken:
    """Mock implementation of System.Threading.CancellationToken"""
    
    def __init__(self, is_cancelled=False):
        self.is_cancelled = is_cancelled
    
    @property
    def IsCancellationRequested(self):
        return self.is_cancelled
    


class MockCancellationTokenSource:
    """Mock implementation of System.Threading.CancellationTokenSource"""
    
    def __init__(self):
        self._is_cancelled = False
        self._token = MockCancellationToken(False)
    
    @property
    def Token(self):
        return self._token
    
    def Cancel(self):
        """Cancel the token"""
        self._is_cancelled = True
        self._token.is_cancelled = True
    
    def CancelAfter(self, milliseconds):
        """Cancel after specified milliseconds"""
        def cancel_delayed():
            time.sleep(milliseconds / 1000.0)
            self.Cancel()
        
        t = threading.Thread(target=cancel_delayed)
        t.daemon = True   # must set attribute before start()
        t.start()


class MockTask:
    """Mock implementation of System.Threading.Tasks.Task"""
    
    def __init__(self, result=None, exception=None, is_completed=True):
        self.result = result
        self.exception = exception
        self.is_completed = is_completed
        self._wait_event = threading.Event()
        if is_completed:
            self._wait_event.set()
    
    @property
    def Result(self):
        """Get the task result"""
        if self.exception:
            raise self.exception
        return self.result
    
    @property
    def IsCompleted(self):
        return self.is_completed
    
    @property
    def IsFaulted(self):
        return self.exception is not None
    
    def Wait(self, timeout=None):
        """Wait for task completion"""
        if timeout:
            return self._wait_event.wait(timeout / 1000.0)  # Convert ms to seconds
        else:
            self._wait_event.wait()
            return True
    
    def complete(self, result=None, exception=None):
        """Complete the task (for testing)"""
        self.result = result
        self.exception = exception
        self.is_completed = True
        self._wait_event.set()


class MockWebSocketReceiveResult:
    """Mock implementation of System.Net.WebSockets.WebSocketReceiveResult"""
    
    def __init__(self, count=0, message_type=MockWebSocketMessageType.Text, end_of_message=True):
        self.Count = count
        self.MessageType = message_type
        self.EndOfMessage = end_of_message

# Generic metaclass that lets us do: Class[T](...) in tests
class _GenericMeta(type):
    def __getitem__(cls, _type_arg):
        # We ignore the type arg; return a callable that constructs `cls`
        def _ctor(*args, **kwargs):
            return cls(*args, **kwargs)
        return _ctor

class MockArraySegment(object):
    __metaclass__ = _GenericMeta

    """Mock implementation of System.ArraySegment[T]"""

    def __init__(self, array, offset=0, count=None):
        self.Array = array
        self.Offset = int(offset)
        if count is None:
            self.Count = len(array) - self.Offset
        else:
            self.Count = int(count)

    def __getitem__(self, index):
        if index < 0 or index >= self.Count:
            raise IndexError("ArraySegment index out of range")
        return self.Array[self.Offset + index]

    def __setitem__(self, index, value):
        if index < 0 or index >= self.Count:
            raise IndexError("ArraySegment index out of range")
        self.Array[self.Offset + index] = value

    def __len__(self):
        return self.Count


class MockArray(object):
    __metaclass__ = _GenericMeta

    """Mock implementation of System.Array[T]"""

    @staticmethod
    def CreateInstance(element_type, length):
        """Create an array instance filled with zeros (like new T[length])."""
        return [0] * int(length)

    def __new__(cls, source):
        """
        Support Array[T](iterable) -> python list of items.
        Returning a non-instance is fine in Python: __new__ may return any object.
        """
        return list(source)


class MockByte(object):
    """Mock implementation of System.Byte (marker only)."""
    pass


class MockClientWebSocket:
    """Mock implementation of System.Net.WebSockets.ClientWebSocket"""
    
    def __init__(self):
        self.state = MockWebSocketState.Closed
        self.connected_uri = None
        self.message_queue = deque()
        self.sent_messages = []
        self.received_messages = []  # Track received messages for testing
        self._lock = threading.Lock()
        self._connection_delay = 0.1  # Simulate connection delay
        self._should_fail_connection = False
        self._should_fail_send = False
        self._should_fail_receive = False
    
    @property
    def State(self):
        return self.state
    
    @property
    def WebSocketState(self):
        return self.state
    
    def ConnectAsync(self, uri, cancellation_token):
        """Mock WebSocket connection"""
        def connect():
            time.sleep(self._connection_delay)
            
            if self._should_fail_connection or cancellation_token.IsCancellationRequested:
                self.state = MockWebSocketState.Aborted
                task.complete(exception=Exception("Connection failed"))
            else:
                self.connected_uri = uri
                self.state = MockWebSocketState.Open
                task.complete(True)
        
        task = MockTask(is_completed=False)
        t = threading.Thread(target=connect)
        t.daemon = True   # must set attribute before start()
        t.start()
        return task
    
    def SendAsync(self, buffer_segment, message_type, end_of_message, cancellation_token):
        """Mock WebSocket send"""
        def send():
            if self._should_fail_send or cancellation_token.IsCancellationRequested:
                task.complete(exception=Exception("Send failed"))
            elif self.state != MockWebSocketState.Open:
                task.complete(exception=Exception("WebSocket not open"))
            else:
                # Extract message from buffer
                message_bytes = []
                for i in range(buffer_segment.Count):
                    message_bytes.append(buffer_segment[i])
                
                message_text = ''.join(chr(b) for b in message_bytes)
                
                with self._lock:
                    self.sent_messages.append({
                        'message': message_text,
                        'type': message_type,
                        'end_of_message': end_of_message,
                        'timestamp': time.time()
                    })
                
                task.complete(True)
        
        task = MockTask(is_completed=False)
        t = threading.Thread(target=send)
        t.daemon = True   # must set attribute before start()
        t.start()
        return task
    
    def ReceiveAsync(self, buffer_segment, cancellation_token):
        """Mock WebSocket receive"""
        def receive():
            if self._should_fail_receive or cancellation_token.IsCancellationRequested:
                task.complete(exception=Exception("Receive failed"))
            elif self.state != MockWebSocketState.Open:
                task.complete(exception=Exception("WebSocket not open"))
            else:
                # Wait for a message or timeout
                timeout = 5.0  # 5 second timeout
                start_time = time.time()
                
                while time.time() - start_time < timeout:
                    with self._lock:
                        if self.message_queue:
                            message_data = self.message_queue.popleft()
                            message_text = message_data['message']
                            message_bytes = [ord(c) for c in message_text]
                            
                            # Copy message to buffer
                            bytes_to_copy = min(len(message_bytes), buffer_segment.Count)
                            for i in range(bytes_to_copy):
                                buffer_segment[i] = message_bytes[i]
                            
                            result = MockWebSocketReceiveResult(
                                count=bytes_to_copy,
                                message_type=message_data.get('type', MockWebSocketMessageType.Text),
                                end_of_message=True
                            )
                            task.complete(result)
                            return
                    
                    time.sleep(0.01)  # Small delay to prevent busy waiting
                
                # Timeout - return empty result
                result = MockWebSocketReceiveResult(count=0)
                task.complete(result)
        
        task = MockTask(is_completed=False)
        t = threading.Thread(target=receive)
        t.daemon = True   # must set attribute before start()
        t.start()
        return task
    
    def CloseAsync(self, close_status, status_description, cancellation_token):
        """Mock WebSocket close"""
        def close():
            self.state = MockWebSocketState.Closed
            task.complete(True)
        
        task = MockTask(is_completed=False)
        t = threading.Thread(target=close)
        t.daemon = True   # must set attribute before start()
        t.start()
        return task
    
    # Test helper methods
    def simulate_received_message(self, message, message_type=MockWebSocketMessageType.Text):
        """Simulate receiving a message (for testing)"""
        with self._lock:
            self.message_queue.append({
                'message': message,
                'type': message_type,
                'timestamp': time.time()
            })
    
    def get_sent_messages(self):
        """Get all sent messages (for testing)"""
        with self._lock:
            return self.sent_messages.copy()
    
    def clear_sent_messages(self):
        """Clear sent messages history (for testing)"""
        with self._lock:
            self.sent_messages.clear()
    
    def set_connection_delay(self, delay_seconds):
        """Set connection delay for testing"""
        self._connection_delay = delay_seconds
    
    def set_should_fail_connection(self, should_fail):
        """Set whether connection should fail (for testing)"""
        self._should_fail_connection = should_fail
    
    def set_should_fail_send(self, should_fail):
        """Set whether send should fail (for testing)"""
        self._should_fail_send = should_fail
    
    def set_should_fail_receive(self, should_fail):
        """Set whether receive should fail (for testing)"""
        self._should_fail_receive = should_fail
    
    def reset_test_state(self):
        """Reset all test state"""
        self.state = MockWebSocketState.Closed
        self.connected_uri = None
        self.message_queue.clear()
        self.sent_messages.clear()
        self.received_messages.clear()
        self._connection_delay = 0.1
        self._should_fail_connection = False
        self._should_fail_send = False
        self._should_fail_receive = False
    
    def reset_for_test(self):
        """Reset for test (alias for reset_test_state)"""
        self.reset_test_state()
    
    def reset_state(self):
        """Reset state (alias for reset_test_state)"""
        self.reset_test_state()


class MockHttpWebRequest:
    """Mock implementation of System.Net.HttpWebRequest"""
    
    def __init__(self, uri):
        self.uri = uri
        self.method = "GET"
        self.content_type = None
        self.accept = None
        self.content_length = 0
        self.headers = {}
        self._request_stream = MockMemoryStream()
        self._response = None
    
    @property
    def Method(self):
        return self.method
    
    @Method.setter
    def Method(self, value):
        self.method = value
    
    @property
    def ContentType(self):
        return self.content_type
    
    @ContentType.setter
    def ContentType(self, value):
        self.content_type = value
    
    @property
    def Accept(self):
        return self.accept
    
    @Accept.setter
    def Accept(self, value):
        self.accept = value
    
    @property
    def ContentLength(self):
        return self.content_length
    
    @ContentLength.setter
    def ContentLength(self, value):
        self.content_length = value
    
    @property
    def Headers(self):
        return MockWebHeaderCollection(self.headers)
    
    def GetRequestStream(self):
        """Get request stream for writing data"""
        return self._request_stream
    
    def GetResponse(self):
        """Get HTTP response"""
        # Simulate HTTP response
        if not self._response:
            self._response = MockHttpWebResponse(200, "OK", {"Content-Type": "application/json"})
        return self._response
    
    def set_mock_response(self, status_code, status_description, headers=None, body=""):
        """Set mock response for testing"""
        self._response = MockHttpWebResponse(status_code, status_description, headers or {}, body)


class MockHttpWebResponse:
    """Mock implementation of System.Net.HttpWebResponse"""
    
    def __init__(self, status_code, status_description, headers=None, body=""):
        self.status_code = status_code
        self.status_description = status_description
        self.headers = headers or {}
        self.body = body
        self._response_stream = MockMemoryStream(body)
    
    @property
    def StatusCode(self):
        return self.status_code
    
    @property
    def StatusDescription(self):
        return self.status_description
    
    @property
    def Headers(self):
        return MockWebHeaderCollection(self.headers)
    
    def GetResponseStream(self):
        """Get response stream for reading data"""
        return self._response_stream
    
    def Close(self):
        """Close the response"""
        pass


class MockWebHeaderCollection:
    """Mock implementation of System.Net.WebHeaderCollection"""
    
    def __init__(self, headers=None):
        self._headers = headers or {}
    
    def Add(self, name, value):
        """Add a header"""
        self._headers[name] = value
    
    def __getitem__(self, name):
        return self._headers.get(name)
    
    def __setitem__(self, name, value):
        self._headers[name] = value
    
    @property
    def Count(self):
        return len(self._headers)
    
    @property
    def Keys(self):
        return list(self._headers.keys())


class MockMemoryStream:
    """Mock implementation of System.IO.MemoryStream"""
    
    def __init__(self, initial_data=""):
        self.data = initial_data
        self.position = 0
    
    def Write(self, buffer, offset, count):
        """Write data to stream"""
        data_to_write = buffer[offset:offset + count]
        self.data += ''.join(chr(b) for b in data_to_write)
    
    def Read(self, buffer, offset, count):
        """Read data from stream"""
        bytes_to_read = min(count, len(self.data) - self.position)
        for i in range(bytes_to_read):
            buffer[offset + i] = ord(self.data[self.position + i])
        self.position += bytes_to_read
        return bytes_to_read
    
    def Close(self):
        """Close the stream"""
        pass


class MockStreamReader:
    """Mock implementation of System.IO.StreamReader"""
    
    def __init__(self, stream):
        self.stream = stream
    
    def ReadToEnd(self):
        """Read all text from stream"""
        return self.stream.data


class MockUri:
    """Mock implementation of System.Uri"""
    
    def __init__(self, uri_string):
        self.uri_string = uri_string
    
    def __str__(self):
        return self.uri_string


class MockUTF8Encoding:
    """Mock implementation of System.Text.UTF8Encoding"""
    
    @staticmethod
    def GetBytes(text):
        """Convert string to bytes"""
        return [ord(c) for c in text]
    
    @staticmethod
    def GetString(byte_array):
        """Convert bytes to string"""
        return ''.join(chr(b) for b in byte_array)


class MockTextEncoding:
    """Mock implementation of System.Text.Encoding"""
    
    UTF8 = MockUTF8Encoding()


class MockAggregateException(Exception):
    """Mock implementation of System.AggregateException"""
    
    def __init__(self, message, inner_exceptions=None):
        super(MockAggregateException, self).__init__(message)
        self.inner_exceptions = inner_exceptions or []
    
    def ToString(self):
        return str(self)


class MockInvalidOperationException(Exception):
    """Mock implementation of System.InvalidOperationException"""
    
    def __init__(self, message):
        super(MockInvalidOperationException, self).__init__(message)
    
    def ToString(self):
        return str(self)


def setup_system_mocks():
    """
    Set up System.Net mocks in the global namespace.
    This function should be called before importing any plugin modules.
    """
    # Create mock System module
    system_module = type(sys)('System')
    
    # Create System.Net submodule
    system_net = type(sys)('System.Net')
    system_net.HttpWebRequest = MockHttpWebRequest
    system_net.HttpWebResponse = MockHttpWebResponse
    system_net.WebHeaderCollection = MockWebHeaderCollection
    
    # Create System.Net.WebSockets submodule
    websockets_module = type(sys)('System.Net.WebSockets')
    websockets_module.ClientWebSocket = MockClientWebSocket
    websockets_module.WebSocketState = MockWebSocketState
    websockets_module.WebSocketMessageType = MockWebSocketMessageType
    websockets_module.WebSocketCloseStatus = MockWebSocketCloseStatus
    
    system_net.WebSockets = websockets_module
    
    # Create System.Threading submodule
    threading_module = type(sys)('System.Threading')
    threading_module.CancellationToken = MockCancellationToken
    threading_module.CancellationTokenSource = MockCancellationTokenSource
    
    # Create System.Threading.Tasks submodule
    tasks_module = type(sys)('System.Threading.Tasks')
    tasks_module.Task = MockTask
    threading_module.Tasks = tasks_module
    
    # Create System.IO submodule
    io_module = type(sys)('System.IO')
    io_module.MemoryStream = MockMemoryStream
    io_module.StreamReader = MockStreamReader
    
    # Create System.Text submodule
    text_module = type(sys)('System.Text')
    text_module.Encoding = MockTextEncoding
    
    # Add submodules to System
    system_module.Net = system_net
    system_module.Threading = threading_module
    system_module.IO = io_module
    system_module.Text = text_module
    system_module.Uri = MockUri
    system_module.Array = MockArray
    system_module.ArraySegment = MockArraySegment
    system_module.Byte = MockByte
    system_module.AggregateException = MockAggregateException
    system_module.InvalidOperationException = MockInvalidOperationException
    
    # Add to sys.modules
    sys.modules['System'] = system_module
    sys.modules['System.Net'] = system_net
    sys.modules['System.Net.WebSockets'] = websockets_module
    sys.modules['System.Threading'] = threading_module
    sys.modules['System.Threading.Tasks'] = tasks_module
    sys.modules['System.IO'] = io_module
    sys.modules['System.Text'] = text_module
    sys.modules['System.Text.Encoding'] = MockTextEncoding
    
    # Use test logging system if available
    try:
        from framework.base import get_logger
        logger = get_logger("SystemMocks")
        logger.debug("System.Net mocks initialized")
    except ImportError:
        # Fallback to print if logging system not available
        print("System.Net mocks initialized")
        pass


def create_mock_websocket_client():
    """Create a new mock WebSocket client for testing"""
    return MockClientWebSocket()


def create_mock_http_request(uri):
    """Create a new mock HTTP request for testing"""
    return MockHttpWebRequest(uri)


# Set the 'None' attribute dynamically to avoid Python keyword conflict
# This allows getattr(CancellationToken, 'None') to work as expected
setattr(MockCancellationToken, 'None', MockCancellationToken(False))
