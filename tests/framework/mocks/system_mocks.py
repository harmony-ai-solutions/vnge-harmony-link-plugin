"""
System.Net Mock Classes for VNGE Harmony Link Plugin Testing

This module provides comprehensive mock implementations of System.Net classes
that are used by the VNGE plugin, enabling testing without .NET dependencies.
"""
import os
import sys
import time
import threading
import json
from collections import deque

# Import Unity mocks that we'll reference
from .unity_mocks import MockVector3, MockColor, MockQuaternion, MockTransform, MockAnimator


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


class MockBindingFlags:
    """Mock implementation of System.Reflection.BindingFlags enum"""
    
    # Common binding flags used in .NET reflection
    Default = 0
    IgnoreCase = 1
    DeclaredOnly = 2
    Instance = 4
    Static = 8
    Public = 16
    NonPublic = 32
    FlattenHierarchy = 64
    InvokeMethod = 256
    CreateInstance = 512
    GetField = 1024
    SetField = 2048
    GetProperty = 4096
    SetProperty = 8192
    PutDispProperty = 16384
    PutRefDispProperty = 32768
    ExactBinding = 65536
    SuppressChangeType = 131072
    OptionalParamBinding = 262144
    IgnoreReturn = 16777216


class MockType:
    """Mock implementation of System.Type"""
    
    def __init__(self, name="MockType"):
        self.name = name
    
    def GetMethod(self, name, binding_flags=None):
        """Get method by name"""
        return MockMethodInfo(name)
    
    def GetProperty(self, name, binding_flags=None):
        """Get property by name"""
        return MockPropertyInfo(name)
    
    def GetField(self, name, binding_flags=None):
        """Get field by name"""
        return MockFieldInfo(name)


class MockMethodInfo:
    """Mock implementation of System.Reflection.MethodInfo"""
    
    def __init__(self, name):
        self.Name = name
    
    def Invoke(self, obj, parameters):
        """Invoke method"""
        return None


class MockPropertyInfo:
    """Mock implementation of System.Reflection.PropertyInfo"""
    
    def __init__(self, name):
        self.Name = name
    
    def GetValue(self, obj, index=None):
        """Get property value"""
        return None
    
    def SetValue(self, obj, value, index=None):
        """Set property value"""
        pass


class MockFieldInfo:
    """Mock implementation of System.Reflection.FieldInfo"""
    
    def __init__(self, name):
        self.Name = name
    
    def GetValue(self, obj):
        """Get field value"""
        return None
    
    def SetValue(self, obj, value):
        """Set field value"""
        pass


class MockEnum:
    """Mock implementation of System.Enum"""
    
    @staticmethod
    def Parse(enum_type, value, ignore_case=False):
        """Parse string value to enum"""
        # For VNGE KeyCode parsing, use the existing MockKeyCode from unity_mocks
        if isinstance(value, str):
            try:
                # Import MockKeyCode from unity_mocks
                from .unity_mocks import MockKeyCode
                
                # Try to get the key code value from MockKeyCode
                if hasattr(MockKeyCode, value):
                    return getattr(MockKeyCode, value)
                
                # If ignore_case is True, try case-insensitive lookup
                if ignore_case:
                    for attr_name in dir(MockKeyCode):
                        if (attr_name.lower() == value.lower() and 
                            not attr_name.startswith('_') and 
                            not callable(getattr(MockKeyCode, attr_name))):
                            return getattr(MockKeyCode, attr_name)
                
                # Special handling for 'None' - return the None value from MockKeyCode
                if value.lower() == 'none':
                    # Return a special None value that won't cause attribute errors
                    return 0  # KeyCode.None is typically 0
                
                # Fallback to 0 if key not found
                return 0
            except Exception as e:
                print("MockEnum.Parse error: " + str(e))
                return 0
        return value
    
    @staticmethod
    def TryParse(enum_type, value, ignore_case=False):
        """Try to parse string value to enum, returns (success, result)"""
        try:
            result = MockEnum.Parse(enum_type, value, ignore_case)
            return (True, result)
        except:
            return (False, None)


class MockString:
    """Mock implementation of System.String"""
    
    def __init__(self, value=""):
        self.value = str(value)
    
    def __str__(self):
        return self.value
    
    def __repr__(self):
        return "MockString('{}')".format(self.value)
    
    def __eq__(self, other):
        if isinstance(other, MockString):
            return self.value == other.value
        return self.value == str(other)
    
    def __len__(self):
        return len(self.value)
    
    def __getitem__(self, index):
        return self.value[index]
    
    def __add__(self, other):
        return MockString(self.value + str(other))
    
    def __contains__(self, item):
        return str(item) in self.value
    
    @property
    def Length(self):
        """Get string length"""
        return len(self.value)
    
    def ToLower(self):
        """Convert to lowercase"""
        return MockString(self.value.lower())
    
    def ToUpper(self):
        """Convert to uppercase"""
        return MockString(self.value.upper())
    
    def Trim(self):
        """Trim whitespace"""
        return MockString(self.value.strip())
    
    def TrimStart(self):
        """Trim leading whitespace"""
        return MockString(self.value.lstrip())
    
    def TrimEnd(self):
        """Trim trailing whitespace"""
        return MockString(self.value.rstrip())
    
    def StartsWith(self, prefix):
        """Check if string starts with prefix"""
        return self.value.startswith(str(prefix))
    
    def EndsWith(self, suffix):
        """Check if string ends with suffix"""
        return self.value.endswith(str(suffix))
    
    def Contains(self, substring):
        """Check if string contains substring"""
        return str(substring) in self.value
    
    def IndexOf(self, substring, start_index=0):
        """Find index of substring"""
        try:
            return self.value.index(str(substring), start_index)
        except ValueError:
            return -1
    
    def LastIndexOf(self, substring):
        """Find last index of substring"""
        try:
            return self.value.rindex(str(substring))
        except ValueError:
            return -1
    
    def Replace(self, old, new):
        """Replace occurrences of old with new"""
        return MockString(self.value.replace(str(old), str(new)))
    
    def Split(self, separator=None):
        """Split string by separator"""
        if separator is None:
            return [MockString(s) for s in self.value.split()]
        return [MockString(s) for s in self.value.split(str(separator))]
    
    def Substring(self, start_index, length=None):
        """Get substring"""
        if length is None:
            return MockString(self.value[start_index:])
        return MockString(self.value[start_index:start_index + length])
    
    def PadLeft(self, total_width, pad_char=' '):
        """Pad string on the left"""
        return MockString(self.value.rjust(total_width, str(pad_char)))
    
    def PadRight(self, total_width, pad_char=' '):
        """Pad string on the right"""
        return MockString(self.value.ljust(total_width, str(pad_char)))
    
    @staticmethod
    def Empty():
        """Get empty string"""
        return MockString("")
    
    @staticmethod
    def IsNullOrEmpty(value):
        """Check if string is null or empty"""
        return value is None or str(value) == ""
    
    @staticmethod
    def IsNullOrWhiteSpace(value):
        """Check if string is null, empty, or whitespace"""
        return value is None or str(value).strip() == ""
    
    @staticmethod
    def Join(separator, values):
        """Join values with separator"""
        return MockString(str(separator).join(str(v) for v in values))
    
    @staticmethod
    def Format(format_string, *args):
        """Format string with arguments"""
        try:
            return MockString(str(format_string).format(*args))
        except:
            return MockString(str(format_string))
    
    @staticmethod
    def Concat(*values):
        """Concatenate values"""
        return MockString(''.join(str(v) for v in values))
    
    @staticmethod
    def Compare(str_a, str_b, ignore_case=False):
        """Compare two strings"""
        a = str(str_a)
        b = str(str_b)
        if ignore_case:
            a = a.lower()
            b = b.lower()
        if a < b:
            return -1
        elif a > b:
            return 1
        return 0


class MockSingle:
    """Mock implementation of System.Single (float)"""
    
    def __init__(self, value=0.0):
        self.value = float(value)
    
    def __str__(self):
        return str(self.value)
    
    def __repr__(self):
        return "MockSingle({})".format(self.value)
    
    def __float__(self):
        return self.value
    
    def __int__(self):
        return int(self.value)
    
    def __eq__(self, other):
        if isinstance(other, MockSingle):
            return abs(self.value - other.value) < 1e-6
        return abs(self.value - float(other)) < 1e-6
    
    def __lt__(self, other):
        if isinstance(other, MockSingle):
            return self.value < other.value
        return self.value < float(other)
    
    def __le__(self, other):
        if isinstance(other, MockSingle):
            return self.value <= other.value
        return self.value <= float(other)
    
    def __gt__(self, other):
        if isinstance(other, MockSingle):
            return self.value > other.value
        return self.value > float(other)
    
    def __ge__(self, other):
        if isinstance(other, MockSingle):
            return self.value >= other.value
        return self.value >= float(other)
    
    def __add__(self, other):
        if isinstance(other, MockSingle):
            return MockSingle(self.value + other.value)
        return MockSingle(self.value + float(other))
    
    def __sub__(self, other):
        if isinstance(other, MockSingle):
            return MockSingle(self.value - other.value)
        return MockSingle(self.value - float(other))
    
    def __mul__(self, other):
        if isinstance(other, MockSingle):
            return MockSingle(self.value * other.value)
        return MockSingle(self.value * float(other))
    
    def __truediv__(self, other):
        if isinstance(other, MockSingle):
            return MockSingle(self.value / other.value)
        return MockSingle(self.value / float(other))
    
    def __div__(self, other):  # Python 2 compatibility
        return self.__truediv__(other)
    
    def __neg__(self):
        return MockSingle(-self.value)
    
    def __abs__(self):
        return MockSingle(abs(self.value))
    
    @staticmethod
    def Parse(value):
        """Parse string to Single"""
        return MockSingle(float(value))
    
    @staticmethod
    def TryParse(value):
        """Try to parse string to Single, returns (success, result)"""
        try:
            result = MockSingle(float(value))
            return (True, result)
        except:
            return (False, MockSingle(0.0))
    
    @staticmethod
    def IsNaN(value):
        """Check if value is NaN"""
        import math
        if isinstance(value, MockSingle):
            return math.isnan(value.value)
        return math.isnan(float(value))
    
    @staticmethod
    def IsInfinity(value):
        """Check if value is infinity"""
        import math
        if isinstance(value, MockSingle):
            return math.isinf(value.value)
        return math.isinf(float(value))
    
    @staticmethod
    def IsPositiveInfinity(value):
        """Check if value is positive infinity"""
        import math
        if isinstance(value, MockSingle):
            return math.isinf(value.value) and value.value > 0
        val = float(value)
        return math.isinf(val) and val > 0
    
    @staticmethod
    def IsNegativeInfinity(value):
        """Check if value is negative infinity"""
        import math
        if isinstance(value, MockSingle):
            return math.isinf(value.value) and value.value < 0
        val = float(value)
        return math.isinf(val) and val < 0
    
    # Constants
    MaxValue = 3.4028235e+38
    MinValue = -3.4028235e+38
    Epsilon = 1.401298e-45
    NaN = float('nan')
    PositiveInfinity = float('inf')
    NegativeInfinity = float('-inf')


class MockConvert:
    """Mock implementation of System.Convert"""
    
    @staticmethod
    def ToInt32(value):
        """Convert value to int32"""
        return int(value)
    
    @staticmethod
    def ToSingle(value):
        """Convert value to float"""
        return float(value)
    
    @staticmethod
    def ToDouble(value):
        """Convert value to double"""
        return float(value)
    
    @staticmethod
    def ToString(value):
        """Convert value to string"""
        return str(value)
    
    @staticmethod
    def ToBoolean(value):
        """Convert value to boolean"""
        return bool(value)
    
    @staticmethod
    def ToByte(value):
        """Convert value to byte"""
        return int(value) & 0xFF
    
    @staticmethod
    def ToChar(value):
        """Convert value to char"""
        if isinstance(value, int):
            return chr(value)
        return str(value)[0] if str(value) else '\0'
    
    @staticmethod
    def ToDateTime(value):
        """Convert value to DateTime (mock)"""
        import time
        return time.time()
    
    @staticmethod
    def ToDecimal(value):
        """Convert value to decimal"""
        return float(value)
    
    @staticmethod
    def ToInt16(value):
        """Convert value to int16"""
        return int(value) & 0xFFFF
    
    @staticmethod
    def ToInt64(value):
        """Convert value to int64"""
        return int(value)
    
    @staticmethod
    def ToSByte(value):
        """Convert value to signed byte"""
        val = int(value) & 0xFF
        return val if val < 128 else val - 256
    
    @staticmethod
    def ToUInt16(value):
        """Convert value to uint16"""
        return int(value) & 0xFFFF
    
    @staticmethod
    def ToUInt32(value):
        """Convert value to uint32"""
        return int(value) & 0xFFFFFFFF
    
    @staticmethod
    def ToUInt64(value):
        """Convert value to uint64"""
        return int(value)


class MockAnimationInfo:
    """Mock implementation of animation info from Studio.Info"""

    def __init__(self, name, bundle_path="", clip="", file_name="", manifest=""):
        self.name = name
        self.bundlePath = bundle_path
        self.clip = clip
        self.fileName = file_name
        self.manifest = manifest


class MockGroupCategory:
    """Mock implementation of animation group category"""

    def __init__(self, name, categories=None):
        self.name = name
        self.dicCategory = categories or {}


class MockCharInfo:
    """Mock implementation of character info for VNGE actors"""
    
    def __init__(self):
        self.sex = 1  # 0=male, 1=female
        self.transform = MockTransform(None)  # Pass None as game_object
        self.chaFile = MockCharFile()
        self.fileStatus = MockCharFileStatus()
        
    def GetLookEyesPtn(self):
        return 0
    
    def ChangeLookEyesPtn(self, ptn):
        pass
    
    def GetLookNeckPtn(self):
        return 0
    
    def ChangeLookNeckPtn(self, ptn):
        pass
    
    def GetMouthPtn(self):
        return 0
    
    def ChangeMouthPtn(self, ptn):
        pass
    
    def GetEyesPtn(self):
        return 0
    
    def ChangeEyesPtn(self, ptn):
        pass
    
    def GetEyebrowPtn(self):
        return 0
    
    def ChangeEyebrowPtn(self, ptn):
        pass


class MockCharFile:
    """Mock implementation of character file data"""
    
    def __init__(self):
        self.custom = MockCustom()
        self.parameter = MockParameter()


class MockCustom:
    """Mock implementation of character custom data"""
    
    def __init__(self):
        self.body = MockBody()
        self.face = MockFace()


class MockBody:
    """Mock implementation of character body data"""
    
    def __init__(self):
        self.shapeValueBody = [0.5] * 10  # Default body shape values


class MockFace:
    """Mock implementation of character face data"""
    
    def __init__(self):
        self.shapeValueFace = [0.5] * 20  # Default face shape values


class MockParameter:
    """Mock implementation of character parameters"""
    
    def __init__(self):
        self.personality = 0


class MockCharFileStatus:
    """Mock implementation of character file status"""
    
    def __init__(self):
        self.coordinateType = 0
        self.clothesState = [0] * 8
        self.showAccessory = [True] * 20
        self.eyesLookPtn = 0
        self.neckLookPtn = 0
        self.eyesBlink = True
        self.eyesOpenMax = 1.0
        self.shoesType = 0


class MockOICharInfo:
    """Mock implementation of OICharInfo for character object info"""
    
    def __init__(self):
        self.changeAmount = MockChangeAmount()
        self.animeInfo = MockAnimeInfo()
        self.animeSpeed = 1.0
        self.animePattern = 0
        self.enableIK = False
        self.enableFK = False
        self.activeIK = [False] * 5
        self.activeFK = [False] * 7
        self.charFile = MockCharFile()
        self.visibleSon = False
        self.sonLength = 0
        self.simpleColor = MockColor()
        self.skinRate = 0.0
        self.nipple = 0.0
        self.mouthOpen = 0.0
        self.lipSync = False


class MockChangeAmount:
    """Mock implementation of change amount for position/rotation/scale"""
    
    def __init__(self):
        self.pos = MockVector3(0, 0, 0)
        self.rot = MockVector3(0, 0, 0)
        self.scale = MockVector3(1, 1, 1)


class MockAnimeInfo:
    """Mock implementation of animation info"""
    
    def __init__(self):
        self.group = 0
        self.category = 0
        self.no = 0


class MockCharAnimeCtrl:
    """Mock implementation of character animation controller"""
    
    def __init__(self):
        self.normalizedTime = 0.0
        self.isForceLoop = False
        self.animator = MockAnimator()
        self.name = "default_animation"


class MockVoiceCtrl:
    """Mock implementation of voice controller"""
    
    def __init__(self):
        self.isPlay = False
        self.list = []
        self.repeat = 0  # MockVoiceCtrlRepeat.None


class MockLookAtInfo:
    """Mock implementation of look at info"""
    
    def __init__(self):
        self.target = MockTransform(None)  # Pass None as game_object


class MockNeckLookCtrl:
    """Mock implementation of neck look controller"""
    
    def SaveNeckLookCtrl(self, writer):
        pass
    
    def LoadNeckLookCtrl(self, reader):
        pass


class MockTreeNodeObject:
    """Mock implementation of tree node object"""
    
    def __init__(self, name=""):
        self.textName = name
        self.visible = True
        self.parent = None
        self.child = []
        self.childCount = 0
    
    def SetVisible(self, visible):
        self.visible = visible


class MockOCIChar:
    """Mock implementation of Studio.OCIChar"""
    
    def __init__(self):
        self.charInfo = MockCharInfo()
        self.oiCharInfo = MockOICharInfo()
        self.charAnimeCtrl = MockCharAnimeCtrl()
        self.voiceCtrl = MockVoiceCtrl()
        self.lookAtInfo = MockLookAtInfo()
        self.neckLookCtrl = MockNeckLookCtrl()
        self.treeNodeObject = MockTreeNodeObject("Character")
        self.sex = 1  # 0=male, 1=female
        self.listBones = []
        self.listIKTarget = []
        self.finalIK = MockFinalIK()
        self.fkCtrl = MockFKCtrl()
        
        # Add charFileStatus as alias to charInfo.fileStatus for compatibility
        self.charFileStatus = self.charInfo.fileStatus
        
        # Animation tracking for testing
        self.animation_history = []
        self.is_initialized = False
    
    def LoadAnime(self, group, category, no, normalized_time=0):
        """Load animation with specified parameters"""
        self.oiCharInfo.animeInfo.group = group
        self.oiCharInfo.animeInfo.category = category
        self.oiCharInfo.animeInfo.no = no
        self.charAnimeCtrl.normalizedTime = normalized_time
        
        # Track animation for testing
        animation_key = "{}_{}_{}_{}".format(group, category, no, normalized_time)
        self.animation_history.append({
            'animation': animation_key,
            'group': group,
            'category': category,
            'no': no,
            'normalized_time': normalized_time,
            'timestamp': time.time()
        })
    
    def RestartAnime(self):
        """Restart current animation"""
        pass
    
    def SetClothesState(self, index, state):
        """Set clothing state"""
        if 0 <= index < len(self.oiCharInfo.charFile.custom.body.shapeValueBody):
            # Simplified - just track the call
            pass
    
    def ShowAccessory(self, index, show):
        """Show/hide accessory"""
        if 0 <= index < len(self.charFileStatus.showAccessory):
            self.charFileStatus.showAccessory[index] = bool(show)
    
    def SetTearsLv(self, level):
        """Set tears level"""
        pass
    
    def GetTearsLv(self):
        """Get tears level"""
        return 0.0
    
    def SetHohoAkaRate(self, rate):
        """Set face red rate"""
        pass
    
    def GetHohoAkaRate(self):
        """Get face red rate"""
        return 0.0
    
    def SetNipStand(self, level):
        """Set nipple stand level"""
        self.oiCharInfo.nipple = level
    
    def SetVisibleSon(self, visible):
        """Set son visibility"""
        self.oiCharInfo.visibleSon = visible
    
    def SetVisibleSimple(self, visible):
        """Set simple visibility"""
        pass
    
    def SetSimpleColor(self, color):
        """Set simple color"""
        self.oiCharInfo.simpleColor = color
    
    def ChangeLookEyesPtn(self, ptn):
        """Change eye look pattern"""
        self.charFileStatus.eyesLookPtn = ptn
    
    def ChangeLookNeckPtn(self, ptn):
        """Change neck look pattern"""
        self.charFileStatus.neckLookPtn = ptn
    
    def ChangeEyesOpen(self, open_amount):
        """Change eyes open amount"""
        self.charFileStatus.eyesOpenMax = open_amount
    
    def ChangeBlink(self, blink):
        """Change blink state"""
        self.charFileStatus.eyesBlink = blink
    
    def ChangeMouthOpen(self, open_amount):
        """Change mouth open amount"""
        self.oiCharInfo.mouthOpen = open_amount
    
    def ChangeLipSync(self, sync):
        """Change lip sync state"""
        self.oiCharInfo.lipSync = sync
    
    def ChangeHandAnime(self, hand, pattern):
        """Change hand animation pattern"""
        pass
    
    def AddVoice(self, group, category, no):
        """Add voice to queue"""
        pass
    
    def DeleteVoice(self, index):
        """Delete voice from queue"""
        pass
    
    def DeleteAllVoice(self):
        """Delete all voices"""
        self.voiceCtrl.list = []
    
    def PlayVoice(self, index=0):
        """Play voice"""
        self.voiceCtrl.isPlay = True
    
    def StopVoice(self):
        """Stop voice"""
        self.voiceCtrl.isPlay = False
    
    def ActiveFK(self, bone_group, active, force=0):
        """Activate FK for bone group"""
        pass
    
    def ActiveIK(self, bone_group, active, force=0):
        """Activate IK for bone group"""
        pass
    
    def ActiveKinematicMode(self, mode, active, force=0):
        """Activate kinematic mode"""
        pass
    
    def get_animation_count(self):
        """Get number of animations executed (for testing)"""
        return len(self.animation_history)
    
    def get_last_animation(self):
        """Get last executed animation (for testing)"""
        if self.animation_history:
            return self.animation_history[-1]
        return None
    
    def reset_for_test(self):
        """Reset character state for testing"""
        self.animation_history = []
        self.is_initialized = False
        self.voiceCtrl.isPlay = False
        self.voiceCtrl.list = []
        self.charAnimeCtrl.normalizedTime = 0.0
        self.oiCharInfo.animeInfo.group = 0
        self.oiCharInfo.animeInfo.category = 0
        self.oiCharInfo.animeInfo.no = 0


class MockFinalIK:
    """Mock implementation of FinalIK component"""
    
    def __init__(self):
        self.enabled = False


class MockFKCtrl:
    """Mock implementation of FK controller"""
    
    def __init__(self):
        self.enabled = False
        self.parts = []


class MockOCIItem:
    """Mock implementation of Studio.OCIItem"""
    
    def __init__(self):
        self.objectInfo = MockObjectInfo()
        self.itemInfo = MockItemInfo()
        self.treeNodeObject = MockTreeNodeObject("Item")
        self.isChangeColor = True
        self.isAnime = False
        self.isFK = False
        self.animator = MockAnimator()
        self.animeSpeed = 1.0


class MockOCIFolder:
    """Mock implementation of Studio.OCIFolder"""
    
    def __init__(self):
        self.objectInfo = MockObjectInfo()
        self.treeNodeObject = MockTreeNodeObject("Folder")
        self.name = "MockFolder"


class MockOCILight:
    """Mock implementation of Studio.OCILight"""
    
    def __init__(self):
        self.objectInfo = MockObjectInfo()
        self.lightInfo = MockLightInfo()
        self.treeNodeObject = MockTreeNodeObject("Light")
        self.lightType = "Directional"


class MockObjectInfo:
    """Mock implementation of object info"""
    
    def __init__(self):
        self.changeAmount = MockChangeAmount()


class MockItemInfo:
    """Mock implementation of item info"""
    
    def __init__(self):
        self.changeAmount = MockChangeAmount()
        self.no = 0
        self.color = [MockColor()] * 8
        self.alpha = 1.0
        self.emissionColor = MockColor()
        self.emissionPower = 0.0
        self.lineColor = MockColor()
        self.lineWidth = 1.0
        self.lightCancel = 0.0
        self.enableDynamicBone = False
        self.enableFK = False
        self.animePattern = 0


class MockLightInfo:
    """Mock implementation of light info"""
    
    def __init__(self):
        self.no = 0
        self.enable = True
        self.color = MockColor()
        self.intensity = 1.0
        self.shadow = True
        self.range = 10.0
        self.spotAngle = 30.0


class MockStudio:
    """Mock implementation of Studio.Studio.Instance"""
    
    def __init__(self):
        self.dicObjectCtrl = {}
        self.dicInfo = {}
        self.sceneInfo = MockSceneInfo()
        self.cameraCtrl = MockCameraCtrl()
        self.treeNodeCtrl = MockTreeNodeCtrl()
        self.bgmCtrl = MockBGMCtrl()
        self.envCtrl = MockEnvCtrl()
        self.outsideSoundCtrl = MockOutsideSoundCtrl()
        self.cameraLightCtrl = MockCameraLightCtrl()
        self.workInfo = MockWorkInfo()
        self.ociCamera = None
    
    def InitScene(self, clear_objects=True):
        """Initialize scene"""
        if clear_objects:
            self.dicObjectCtrl.clear()
            self.dicInfo.clear()
    
    def LoadScene(self, file_path):
        """Load scene from file"""
        pass
    
    def AddMap(self, map_id, *args):
        """Add map to scene"""
        pass
    
    def ChangeCamera(self, oci_camera):
        """Change active camera"""
        self.ociCamera = oci_camera


class MockSceneInfo:
    """Mock implementation of scene info"""
    
    def __init__(self):
        self.cameraData = [MockCameraData() for _ in range(10)]
        self.background = ""
        self.frame = ""
        self.map = -1
        self.mapOption = True
        self.charaLight = MockCharaLight()


class MockCameraData:
    """Mock implementation of camera data"""
    
    def __init__(self):
        self.pos = MockVector3(0, 1, -5)
        self.distance = MockVector3(0, 0, 5)
        self.rotate = MockVector3(0, 0, 0)
        self.parse = 23.0  # Field of view
    
    def Copy(self, other):
        """Copy camera data from another instance"""
        self.pos = other.pos
        self.distance = other.distance
        self.rotate = other.rotate
        self.parse = other.parse


class MockCameraCtrl:
    """Mock implementation of camera controller"""
    
    def __init__(self):
        self.cameraData = MockCameraData()
        self.fieldOfView = 23.0
        self.noCtrlCondition = None


class MockTreeNodeCtrl:
    """Mock implementation of tree node controller"""
    
    def __init__(self):
        self.selectNode = None
    
    def SetParent(self, child_node, parent_node):
        """Set parent-child relationship"""
        if parent_node:
            parent_node.child.append(child_node)
            parent_node.childCount = len(parent_node.child)
        child_node.parent = parent_node
    
    def DeleteNode(self, node):
        """Delete node from tree"""
        if node.parent:
            if node in node.parent.child:
                node.parent.child.remove(node)
                node.parent.childCount = len(node.parent.child)


class MockBGMCtrl:
    """Mock implementation of BGM controller"""
    
    def __init__(self):
        self.no = 0
        self.play = False
    
    def Play(self, bgm_no=None):
        """Play BGM"""
        if bgm_no is not None:
            self.no = bgm_no
        self.play = True
    
    def Stop(self):
        """Stop BGM"""
        self.play = False


class MockEnvCtrl:
    """Mock implementation of environment sound controller"""
    
    def __init__(self):
        self.no = 0
        self.play = False
    
    def Play(self, env_no=None):
        """Play environment sound"""
        if env_no is not None:
            self.no = env_no
        self.play = True
    
    def Stop(self):
        """Stop environment sound"""
        self.play = False


class MockOutsideSoundCtrl:
    """Mock implementation of outside sound controller"""
    
    def __init__(self):
        self.fileName = ""
        self.play = False
        self.repeat = 0  # MockBGMCtrlRepeat.None
    
    def Play(self, file_name=None):
        """Play outside sound"""
        if file_name is not None:
            self.fileName = file_name
        self.play = True
    
    def Stop(self):
        """Stop outside sound"""
        self.play = False


class MockCameraLightCtrl:
    """Mock implementation of camera light controller"""
    
    def Reflect(self):
        """Reflect camera light changes"""
        pass


class MockCharaLight:
    """Mock implementation of character light"""
    
    def __init__(self):
        self.color = MockColor()
        self.intensity = 1.0
        self.rot = [0.0, 0.0]
        self.shadow = True


class MockWorkInfo:
    """Mock implementation of work info"""
    
    def __init__(self):
        self.useAlt = True


class MockStudioInfo:
    """Mock implementation of Studio.Info.Instance"""

    def __init__(self):
        self.dicAnimeLoadInfo = self._create_animation_database()
        self.dicAGroupCategory = self._create_group_categories()
        self.dicFemaleAnimeLoadInfo = self.dicAnimeLoadInfo  # Alias for compatibility

    def _create_animation_database(self):
        """Create mock animation database structure"""
        # Try to load from actual animation_list.json if available
        animation_file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src', 'harmony_data', 'animation_list.json')

        if os.path.exists(animation_file):
            try:
                with open(animation_file, 'r') as f:
                    animation_data = json.load(f)
                    return self._convert_animation_data(animation_data)
            except Exception as e:
                print("Warning: Could not load animation_list.json: {}".format(e))

        # Fallback to basic mock data
        return self._create_basic_animation_database()

    def _convert_animation_data(self, animation_data):
        """Convert JSON animation data to mock structure"""
        converted = {}

        for group_id_str, group_data in animation_data.items():
            try:
                group_id = int(group_id_str)
                converted[group_id] = {}

                if 'categories' in group_data:
                    for category_id_str, category_data in group_data['categories'].items():
                        try:
                            category_id = int(category_id_str)
                            converted[group_id][category_id] = {}

                            if 'animation_items' in category_data:
                                for i, item in enumerate(category_data['animation_items']):
                                    converted[group_id][category_id][i] = MockAnimationInfo(
                                        name=item.get('name', 'animation_{}'.format(i)),
                                        bundle_path=item.get('metadata', {}).get('bundlePath', ''),
                                        clip=item.get('metadata', {}).get('clip', ''),
                                        file_name=item.get('metadata', {}).get('fileName', ''),
                                        manifest=item.get('metadata', {}).get('manifest', '')
                                    )
                        except (ValueError, KeyError):
                            continue
            except (ValueError, KeyError):
                continue

        return converted

    def _create_basic_animation_database(self):
        """Create basic mock animation database for testing"""
        return {
            0: {  # Base animations
                0: {  # Idle animations
                    0: MockAnimationInfo("idle_01", "base/idle", "idle_01.anim"),
                    1: MockAnimationInfo("idle_02", "base/idle", "idle_02.anim"),
                    2: MockAnimationInfo("idle_03", "base/idle", "idle_03.anim"),
                },
                1: {  # Basic movements
                    0: MockAnimationInfo("walk_forward", "base/movement", "walk_forward.anim"),
                    1: MockAnimationInfo("walk_backward", "base/movement", "walk_backward.anim"),
                    2: MockAnimationInfo("run_forward", "base/movement", "run_forward.anim"),
                    3: MockAnimationInfo("turn_left", "base/movement", "turn_left.anim"),
                    4: MockAnimationInfo("turn_right", "base/movement", "turn_right.anim"),
                }
            },
            1: {  # Gestures
                0: {  # Hand gestures
                    0: MockAnimationInfo("wave_hand", "gestures/hand", "wave_hand.anim"),
                    1: MockAnimationInfo("point_forward", "gestures/hand", "point_forward.anim"),
                    2: MockAnimationInfo("thumbs_up", "gestures/hand", "thumbs_up.anim"),
                },
                1: {  # Head gestures
                    0: MockAnimationInfo("nod_yes", "gestures/head", "nod_yes.anim"),
                    1: MockAnimationInfo("shake_no", "gestures/head", "shake_no.anim"),
                    2: MockAnimationInfo("tilt_head", "gestures/head", "tilt_head.anim"),
                }
            },
            2: {  # Postures
                0: {  # Sitting
                    0: MockAnimationInfo("sit_down", "postures/sitting", "sit_down.anim"),
                    1: MockAnimationInfo("sit_idle", "postures/sitting", "sit_idle.anim"),
                    2: MockAnimationInfo("stand_up", "postures/sitting", "stand_up.anim"),
                },
                1: {  # Laying
                    0: MockAnimationInfo("lay_down", "postures/laying", "lay_down.anim"),
                    1: MockAnimationInfo("lay_idle", "postures/laying", "lay_idle.anim"),
                    2: MockAnimationInfo("get_up", "postures/laying", "get_up.anim"),
                }
            }
        }

    def _create_group_categories(self):
        """Create mock group categories"""
        return {
            0: MockGroupCategory("Base", {
                0: "Idle",
                1: "Movement"
            }),
            1: MockGroupCategory("Gestures", {
                0: "Hand",
                1: "Head"
            }),
            2: MockGroupCategory("Postures", {
                0: "Sitting",
                1: "Laying"
            })
        }


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

    # Create System.Text.Encoding submodule
    encoding_module = type(sys)('System.Text.Encoding')
    encoding_module.UTF8 = MockUTF8Encoding()

    # Create System.Text submodule
    text_module = type(sys)('System.Text')
    text_module.Encoding = encoding_module

    # Create System.Reflection submodule
    reflection_module = type(sys)('System.Reflection')
    reflection_module.BindingFlags = MockBindingFlags
    reflection_module.Type = MockType
    reflection_module.MethodInfo = MockMethodInfo
    reflection_module.PropertyInfo = MockPropertyInfo
    reflection_module.FieldInfo = MockFieldInfo

    # Create mock Studio module
    studio_module = type(sys)('Studio')
    studio_module.Info = type('Info', (), {'Instance': MockStudioInfo()})()
    studio_module.Studio = MockStudio()
    studio_module.OCIChar = MockOCIChar
    studio_module.OCIItem = MockOCIItem
    studio_module.OCIFolder = MockOCIFolder
    studio_module.OCILight = MockOCILight
    studio_module.OICharInfo = MockOICharInfo
    
    # Add submodules to System
    system_module.Net = system_net
    system_module.Threading = threading_module
    system_module.IO = io_module
    system_module.Text = text_module
    system_module.Reflection = reflection_module
    system_module.Uri = MockUri
    system_module.Convert = MockConvert
    system_module.Array = MockArray
    system_module.ArraySegment = MockArraySegment
    system_module.Byte = MockByte
    system_module.Enum = MockEnum
    system_module.String = MockString
    system_module.Single = MockSingle
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
    sys.modules['System.Text.Encoding'] = encoding_module
    sys.modules['System.Reflection'] = reflection_module
    sys.modules['Studio'] = studio_module
    
    # Use test logging system if available
    try:
        from framework.base import get_logger
        logger = get_logger("SystemMocks")
        logger.debug("System mocks initialized")
    except ImportError:
        # Fallback to print if logging system not available
        print("System mocks initialized")
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
