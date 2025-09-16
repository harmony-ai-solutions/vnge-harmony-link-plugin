"""
Unity Engine Mock Classes for VNGE Harmony Link Plugin Testing

This module provides comprehensive mock implementations of Unity Engine classes
that are used by the VNGE plugin, enabling testing without Unity dependencies.
"""

import sys
import time
import threading
from collections import defaultdict


class MockVector2:
    """Mock implementation of UnityEngine.Vector2"""
    
    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)
    
    def __str__(self):
        return "({}, {})".format(self.x, self.y)
    
    def __repr__(self):
        return "MockVector2({}, {})".format(self.x, self.y)
    
    def __eq__(self, other):
        if not isinstance(other, MockVector2):
            return False
        return abs(self.x - other.x) < 0.001 and abs(self.y - other.y) < 0.001
    
    @property
    def magnitude(self):
        return (self.x * self.x + self.y * self.y) ** 0.5
    
    @classmethod
    def zero(cls):
        return cls(0.0, 0.0)


class MockVector3:
    """Mock implementation of UnityEngine.Vector3"""
    
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
    
    def __str__(self):
        return "({}, {}, {})".format(self.x, self.y, self.z)
    
    def __repr__(self):
        return "MockVector3({}, {}, {})".format(self.x, self.y, self.z)
    
    def __eq__(self, other):
        if not isinstance(other, MockVector3):
            return False
        return (abs(self.x - other.x) < 0.001 and 
                abs(self.y - other.y) < 0.001 and 
                abs(self.z - other.z) < 0.001)
    
    def __add__(self, other):
        return MockVector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return MockVector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return MockVector3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    @property
    def magnitude(self):
        return (self.x * self.x + self.y * self.y + self.z * self.z) ** 0.5
    
    def distance(self, other):
        """Calculate distance to another Vector3"""
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return (dx*dx + dy*dy + dz*dz) ** 0.5
    
    @classmethod
    def zero(cls):
        return cls(0.0, 0.0, 0.0)
    
    @classmethod
    def one(cls):
        return cls(1.0, 1.0, 1.0)


class MockVector4:
    """Mock implementation of UnityEngine.Vector4"""
    
    def __init__(self, x=0.0, y=0.0, z=0.0, w=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.w = float(w)
    
    def __str__(self):
        return "({}, {}, {}, {})".format(self.x, self.y, self.z, self.w)
    
    def __repr__(self):
        return "MockVector4({}, {}, {}, {})".format(self.x, self.y, self.z, self.w)
    
    def __eq__(self, other):
        if not isinstance(other, MockVector4):
            return False
        return (abs(self.x - other.x) < 0.001 and 
                abs(self.y - other.y) < 0.001 and 
                abs(self.z - other.z) < 0.001 and
                abs(self.w - other.w) < 0.001)
    
    def __add__(self, other):
        return MockVector4(self.x + other.x, self.y + other.y, self.z + other.z, self.w + other.w)
    
    def __sub__(self, other):
        return MockVector4(self.x - other.x, self.y - other.y, self.z - other.z, self.w - other.w)
    
    def __mul__(self, scalar):
        return MockVector4(self.x * scalar, self.y * scalar, self.z * scalar, self.w * scalar)
    
    @property
    def magnitude(self):
        return (self.x * self.x + self.y * self.y + self.z * self.z + self.w * self.w) ** 0.5
    
    @classmethod
    def zero(cls):
        return cls(0.0, 0.0, 0.0, 0.0)
    
    @classmethod
    def one(cls):
        return cls(1.0, 1.0, 1.0, 1.0)


class MockRect:
    """Mock implementation of UnityEngine.Rect"""
    
    def __init__(self, x=0.0, y=0.0, width=0.0, height=0.0):
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)
    
    def __str__(self):
        return "Rect({}, {}, {}, {})".format(self.x, self.y, self.width, self.height)
    
    def __repr__(self):
        return "MockRect({}, {}, {}, {})".format(self.x, self.y, self.width, self.height)
    
    def contains(self, point):
        """Check if a point (Vector2) is inside this rect"""
        return (self.x <= point.x <= self.x + self.width and
                self.y <= point.y <= self.y + self.height)


class MockColor:
    """Mock implementation of UnityEngine.Color"""
    
    def __init__(self, r=1.0, g=1.0, b=1.0, a=1.0):
        self.r = float(r)
        self.g = float(g)
        self.b = float(b)
        self.a = float(a)
    
    def __str__(self):
        return "Color({}, {}, {}, {})".format(self.r, self.g, self.b, self.a)
    
    def __repr__(self):
        return "MockColor({}, {}, {}, {})".format(self.r, self.g, self.b, self.a)
    
    @classmethod
    def white(cls):
        return cls(1.0, 1.0, 1.0, 1.0)
    
    @classmethod
    def black(cls):
        return cls(0.0, 0.0, 0.0, 1.0)
    
    @classmethod
    def red(cls):
        return cls(1.0, 0.0, 0.0, 1.0)
    
    @classmethod
    def green(cls):
        return cls(0.0, 1.0, 0.0, 1.0)
    
    @classmethod
    def blue(cls):
        return cls(0.0, 0.0, 1.0, 1.0)


class MockMatrix4x4:
    """Mock implementation of UnityEngine.Matrix4x4"""
    
    def __init__(self, m00=1.0, m01=0.0, m02=0.0, m03=0.0,
                       m10=0.0, m11=1.0, m12=0.0, m13=0.0,
                       m20=0.0, m21=0.0, m22=1.0, m23=0.0,
                       m30=0.0, m31=0.0, m32=0.0, m33=1.0):
        """Initialize 4x4 matrix with given values (defaults to identity)"""
        self.m00, self.m01, self.m02, self.m03 = float(m00), float(m01), float(m02), float(m03)
        self.m10, self.m11, self.m12, self.m13 = float(m10), float(m11), float(m12), float(m13)
        self.m20, self.m21, self.m22, self.m23 = float(m20), float(m21), float(m22), float(m23)
        self.m30, self.m31, self.m32, self.m33 = float(m30), float(m31), float(m32), float(m33)
    
    def __str__(self):
        return "Matrix4x4([{}, {}, {}, {}], [{}, {}, {}, {}], [{}, {}, {}, {}], [{}, {}, {}, {}])".format(
            self.m00, self.m01, self.m02, self.m03,
            self.m10, self.m11, self.m12, self.m13,
            self.m20, self.m21, self.m22, self.m23,
            self.m30, self.m31, self.m32, self.m33
        )
    
    def __repr__(self):
        return "MockMatrix4x4({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})".format(
            self.m00, self.m01, self.m02, self.m03,
            self.m10, self.m11, self.m12, self.m13,
            self.m20, self.m21, self.m22, self.m23,
            self.m30, self.m31, self.m32, self.m33
        )
    
    def __eq__(self, other):
        if not isinstance(other, MockMatrix4x4):
            return False
        return (abs(self.m00 - other.m00) < 0.001 and abs(self.m01 - other.m01) < 0.001 and
                abs(self.m02 - other.m02) < 0.001 and abs(self.m03 - other.m03) < 0.001 and
                abs(self.m10 - other.m10) < 0.001 and abs(self.m11 - other.m11) < 0.001 and
                abs(self.m12 - other.m12) < 0.001 and abs(self.m13 - other.m13) < 0.001 and
                abs(self.m20 - other.m20) < 0.001 and abs(self.m21 - other.m21) < 0.001 and
                abs(self.m22 - other.m22) < 0.001 and abs(self.m23 - other.m23) < 0.001 and
                abs(self.m30 - other.m30) < 0.001 and abs(self.m31 - other.m31) < 0.001 and
                abs(self.m32 - other.m32) < 0.001 and abs(self.m33 - other.m33) < 0.001)
    
    def __mul__(self, other):
        """Matrix multiplication"""
        if isinstance(other, MockMatrix4x4):
            # Matrix * Matrix multiplication
            result = MockMatrix4x4()
            for i in range(4):
                for j in range(4):
                    value = 0.0
                    for k in range(4):
                        value += getattr(self, 'm{}{}'.format(i, k)) * getattr(other, 'm{}{}'.format(k, j))
                    setattr(result, 'm{}{}'.format(i, j), value)
            return result
        elif isinstance(other, MockVector3):
            # Matrix * Vector3 transformation (treating Vector3 as homogeneous coordinate with w=1)
            x = self.m00 * other.x + self.m01 * other.y + self.m02 * other.z + self.m03
            y = self.m10 * other.x + self.m11 * other.y + self.m12 * other.z + self.m13
            z = self.m20 * other.x + self.m21 * other.y + self.m22 * other.z + self.m23
            return MockVector3(x, y, z)
        return self
    
    @property
    def inverse(self):
        """Get inverse matrix (simplified for testing - returns identity)"""
        return MockMatrix4x4.identity()
    
    @property
    def transpose(self):
        """Get transpose matrix"""
        return MockMatrix4x4(
            self.m00, self.m10, self.m20, self.m30,
            self.m01, self.m11, self.m21, self.m31,
            self.m02, self.m12, self.m22, self.m32,
            self.m03, self.m13, self.m23, self.m33
        )
    
    def MultiplyPoint(self, point):
        """Transform a point (Vector3) by this matrix"""
        return self * point
    
    def MultiplyVector(self, vector):
        """Transform a vector (Vector3) by this matrix (ignoring translation)"""
        x = self.m00 * vector.x + self.m01 * vector.y + self.m02 * vector.z
        y = self.m10 * vector.x + self.m11 * vector.y + self.m12 * vector.z
        z = self.m20 * vector.x + self.m21 * vector.y + self.m22 * vector.z
        return MockVector3(x, y, z)
    
    @classmethod
    def identity(cls):
        """Identity matrix"""
        return cls()
    
    @classmethod
    def zero(cls):
        """Zero matrix"""
        return cls(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    
    @classmethod
    def TRS(cls, translation, rotation, scale):
        """Create transformation matrix from translation, rotation, and scale"""
        # Simplified for testing - just return identity
        return cls.identity()
    
    @classmethod
    def Translate(cls, vector):
        """Create translation matrix"""
        return cls(1, 0, 0, vector.x,
                   0, 1, 0, vector.y,
                   0, 0, 1, vector.z,
                   0, 0, 0, 1)
    
    @classmethod
    def Scale(cls, vector):
        """Create scale matrix"""
        return cls(vector.x, 0, 0, 0,
                   0, vector.y, 0, 0,
                   0, 0, vector.z, 0,
                   0, 0, 0, 1)


class MockQuaternion:
    """Mock implementation of UnityEngine.Quaternion"""
    
    def __init__(self, x=0.0, y=0.0, z=0.0, w=1.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.w = float(w)
    
    def __str__(self):
        return "({}, {}, {}, {})".format(self.x, self.y, self.z, self.w)
    
    def __repr__(self):
        return "MockQuaternion({}, {}, {}, {})".format(self.x, self.y, self.z, self.w)
    
    def __eq__(self, other):
        if not isinstance(other, MockQuaternion):
            return False
        return (abs(self.x - other.x) < 0.001 and 
                abs(self.y - other.y) < 0.001 and 
                abs(self.z - other.z) < 0.001 and
                abs(self.w - other.w) < 0.001)
    
    def __mul__(self, other):
        """Quaternion multiplication"""
        if isinstance(other, MockQuaternion):
            return MockQuaternion(
                self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y,
                self.w * other.y + self.y * other.w + self.z * other.x - self.x * other.z,
                self.w * other.z + self.z * other.w + self.x * other.y - self.y * other.x,
                self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z
            )
        return self
    
    @property
    def eulerAngles(self):
        """Convert to Euler angles (returns MockVector3)"""
        # Simplified conversion for testing
        return MockVector3(0.0, 0.0, 0.0)
    
    @classmethod
    def identity(cls):
        """Identity quaternion"""
        return cls(0.0, 0.0, 0.0, 1.0)
    
    @classmethod
    def Euler(cls, x, y, z):
        """Create quaternion from Euler angles"""
        # Simplified for testing - just return identity
        return cls.identity()
    
    @classmethod
    def AngleAxis(cls, angle, axis):
        """Create quaternion from angle and axis"""
        # Simplified for testing - just return identity
        return cls.identity()
    
    @classmethod
    def LookRotation(cls, forward, up=None):
        """Create quaternion that looks in forward direction"""
        # Simplified for testing - just return identity
        return cls.identity()
    
    @classmethod
    def Slerp(cls, a, b, t):
        """Spherical linear interpolation between two quaternions"""
        # Simplified for testing - just return a
        return a


class MockKeyCode:
    """Mock implementation of UnityEngine.KeyCode enum"""
    
    # Common key codes used by the plugin
    A = 97
    B = 98
    C = 99
    D = 100
    E = 101
    F = 102
    G = 103
    H = 104
    I = 105
    J = 106
    K = 107
    L = 108
    M = 109
    N = 110
    O = 111
    P = 112
    Q = 113
    R = 114
    S = 115
    T = 116
    U = 117
    V = 118
    W = 119
    X = 120
    Y = 121
    Z = 122
    
    # Number keys
    Alpha0 = 48
    Alpha1 = 49
    Alpha2 = 50
    Alpha3 = 51
    Alpha4 = 52
    Alpha5 = 53
    Alpha6 = 54
    Alpha7 = 55
    Alpha8 = 56
    Alpha9 = 57
    
    # Function keys
    F1 = 282
    F2 = 283
    F3 = 284
    F4 = 285
    F5 = 286
    F6 = 287
    F7 = 288
    F8 = 289
    F9 = 290
    F10 = 291
    F11 = 292
    F12 = 293
    
    # Special keys
    Space = 32
    Return = 13
    Escape = 27
    Tab = 9
    Backspace = 8
    Delete = 127
    Insert = 277
    Home = 278
    End = 279
    PageUp = 280
    PageDown = 281
    
    # Arrow keys
    UpArrow = 273
    DownArrow = 274
    LeftArrow = 276
    RightArrow = 275
    
    # Modifier keys
    LeftShift = 304
    RightShift = 303
    LeftControl = 306
    RightControl = 305
    LeftAlt = 308
    RightAlt = 307
    LeftCommand = 310
    RightCommand = 309
    
    # Keypad
    Keypad0 = 256
    Keypad1 = 257
    Keypad2 = 258
    Keypad3 = 259
    Keypad4 = 260
    Keypad5 = 261
    Keypad6 = 262
    Keypad7 = 263
    Keypad8 = 264
    Keypad9 = 265
    KeypadPeriod = 266
    KeypadDivide = 267
    KeypadMultiply = 268
    KeypadMinus = 269
    KeypadPlus = 270
    KeypadEnter = 271
    KeypadEquals = 272


class MockTextAnchor:
    """Mock implementation of UnityEngine.TextAnchor enum"""
    
    # Text anchor positions for GUI text alignment
    UpperLeft = 0
    UpperCenter = 1
    UpperRight = 2
    MiddleLeft = 3
    MiddleCenter = 4
    MiddleRight = 5
    LowerLeft = 6
    LowerCenter = 7
    LowerRight = 8


class MockInput:
    """Mock implementation of UnityEngine.Input"""
    
    def __init__(self):
        self.key_states = defaultdict(bool)
        self.key_down_states = defaultdict(bool)
        self.key_up_states = defaultdict(bool)
        self.mouse_position = MockVector3(0, 0, 0)
        self.mouse_buttons = defaultdict(bool)
        self._lock = threading.Lock()
    
    def GetKey(self, keycode):
        """Check if a key is currently being held down"""
        with self._lock:
            return self.key_states.get(keycode, False)
    
    def GetKeyDown(self, keycode):
        """Check if a key was pressed this frame"""
        with self._lock:
            return self.key_down_states.get(keycode, False)
    
    def GetKeyUp(self, keycode):
        """Check if a key was released this frame"""
        with self._lock:
            return self.key_up_states.get(keycode, False)
    
    def GetMouseButton(self, button):
        """Check if a mouse button is being held down"""
        with self._lock:
            return self.mouse_buttons.get(button, False)
    
    @property
    def mousePosition(self):
        """Get current mouse position"""
        return self.mouse_position
    
    # Test helper methods
    def simulate_key_press(self, keycode):
        """Simulate pressing a key (for testing)"""
        with self._lock:
            self.key_states[keycode] = True
            self.key_down_states[keycode] = True
    
    def simulate_key_release(self, keycode):
        """Simulate releasing a key (for testing)"""
        with self._lock:
            self.key_states[keycode] = False
            self.key_up_states[keycode] = True
    
    def simulate_key_tap(self, keycode, duration=0.1):
        """Simulate a quick key tap (for testing)"""
        self.simulate_key_press(keycode)
        # In a real test, you might want to use threading.Timer
        # For now, we'll just set both states
        with self._lock:
            self.key_down_states[keycode] = True
    
    def clear_frame_states(self):
        """Clear per-frame states (GetKeyDown/GetKeyUp)"""
        with self._lock:
            self.key_down_states.clear()
            self.key_up_states.clear()
    
    def reset_all_states(self):
        """Reset all input states (for testing)"""
        with self._lock:
            self.key_states.clear()
            self.key_down_states.clear()
            self.key_up_states.clear()
            self.mouse_buttons.clear()
            self.mouse_position = MockVector3(0, 0, 0)
    
    def reset_for_test(self):
        """Reset for test (alias for reset_all_states)"""
        self.reset_all_states()
    
    def reset_state(self):
        """Reset state (alias for reset_all_states)"""
        self.reset_all_states()


class MockGUILayout:
    """Mock implementation of UnityEngine.GUILayout"""
    
    def __init__(self):
        self.button_clicks = []
        self.text_fields = {}
        self.labels = []
        self.scroll_positions = {}
    
    def Button(self, text, *options):
        """Mock GUI button - returns True if clicked"""
        # For testing, we can simulate button clicks
        clicked = text in self.button_clicks
        if clicked:
            self.button_clicks.remove(text)  # Remove after one click
        return clicked
    
    def Label(self, text, *options):
        """Mock GUI label"""
        self.labels.append(text)
    
    def TextField(self, text, *options):
        """Mock GUI text field"""
        # Return the current text or stored text for this field
        field_id = id(text)  # Use object id as field identifier
        return self.text_fields.get(field_id, text)
    
    def BeginHorizontal(self, *options):
        """Mock horizontal layout group"""
        pass
    
    def EndHorizontal(self):
        """End horizontal layout group"""
        pass
    
    def BeginVertical(self, *options):
        """Mock vertical layout group"""
        pass
    
    def EndVertical(self):
        """End vertical layout group"""
        pass
    
    def BeginScrollView(self, scroll_position, *options):
        """Mock scroll view"""
        return scroll_position
    
    def EndScrollView(self):
        """End scroll view"""
        pass
    
    def Space(self, pixels):
        """Mock GUI space"""
        pass
    
    def FlexibleSpace(self):
        """Mock flexible space"""
        pass
    
    def Width(self, width):
        """Mock width option"""
        return {'width': width}
    
    def Height(self, height):
        """Mock height option"""
        return {'height': height}
    
    def ExpandWidth(self, expand):
        """Mock expand width option"""
        return {'expand_width': expand}
    
    def ExpandHeight(self, expand):
        """Mock expand height option"""
        return {'expand_height': expand}
    
    # Test helper methods
    def simulate_button_click(self, text):
        """Simulate clicking a button (for testing)"""
        self.button_clicks.append(text)
    
    def set_text_field_value(self, field_text, new_value):
        """Set text field value (for testing)"""
        field_id = id(field_text)
        self.text_fields[field_id] = new_value
    
    def get_labels(self):
        """Get all labels that were drawn"""
        return self.labels.copy()
    
    def clear_state(self):
        """Clear all GUI state (for testing)"""
        self.button_clicks.clear()
        self.text_fields.clear()
        self.labels.clear()
        self.scroll_positions.clear()
    
    def reset_state(self):
        """Reset state (alias for clear_state)"""
        self.clear_state()
    
    def reset_for_test(self):
        """Reset for test (alias for clear_state)"""
        self.clear_state()


class MockTime:
    """Mock implementation of UnityEngine.Time"""
    
    _time = 0.0
    _delta_time = 0.016667  # ~60 FPS
    _fixed_time = 0.0
    _fixed_delta_time = 0.02  # 50 Hz
    _time_scale = 1.0
    _frame_count = 0
    _real_time_since_startup = 0.0
    _unscaled_time = 0.0
    _unscaled_delta_time = 0.016667
    
    @classmethod
    def time(cls):
        """Time since the start of the game"""
        return cls._time
    
    @classmethod
    def deltaTime(cls):
        """Time in seconds it took to complete the last frame"""
        return cls._delta_time
    
    @classmethod
    def fixedTime(cls):
        """Time the latest FixedUpdate had started"""
        return cls._fixed_time
    
    @classmethod
    def fixedDeltaTime(cls):
        """Interval in seconds at which physics and other fixed frame rate updates are performed"""
        return cls._fixed_delta_time
    
    @classmethod
    def timeScale(cls):
        """Scale at which time passes"""
        return cls._time_scale
    
    @classmethod
    def frameCount(cls):
        """Total number of frames that have passed"""
        return cls._frame_count
    
    @classmethod
    def realtimeSinceStartup(cls):
        """Real time in seconds since the game started"""
        return cls._real_time_since_startup
    
    @classmethod
    def unscaledTime(cls):
        """Timeframe-rate independent time in seconds since the start of the game"""
        return cls._unscaled_time
    
    @classmethod
    def unscaledDeltaTime(cls):
        """Timeframe-rate independent deltaTime"""
        return cls._unscaled_delta_time
    
    # Test helper methods
    @classmethod
    def advance_time(cls, delta):
        """Advance time by delta seconds (for testing)"""
        cls._time += delta * cls._time_scale
        cls._unscaled_time += delta
        cls._real_time_since_startup += delta
        cls._delta_time = delta * cls._time_scale
        cls._unscaled_delta_time = delta
        cls._frame_count += 1
    
    @classmethod
    def advance_fixed_time(cls, delta):
        """Advance fixed time by delta seconds (for testing)"""
        cls._fixed_time += delta
    
    @classmethod
    def set_time_scale(cls, scale):
        """Set time scale (for testing)"""
        cls._time_scale = scale
    
    @classmethod
    def reset_time(cls):
        """Reset all time values (for testing)"""
        cls._time = 0.0
        cls._delta_time = 0.016667
        cls._fixed_time = 0.0
        cls._fixed_delta_time = 0.02
        cls._time_scale = 1.0
        cls._frame_count = 0
        cls._real_time_since_startup = 0.0
        cls._unscaled_time = 0.0
        cls._unscaled_delta_time = 0.016667


class MockMathf:
    """Mock implementation of UnityEngine.Mathf"""
    
    # Mathematical constants
    PI = 3.14159265359
    Infinity = float('inf')
    NegativeInfinity = float('-inf')
    Deg2Rad = PI / 180.0
    Rad2Deg = 180.0 / PI
    Epsilon = 1.401298E-45
    
    @staticmethod
    def Abs(value):
        """Absolute value"""
        return abs(value)
    
    @staticmethod
    def Acos(value):
        """Arc cosine"""
        import math
        return math.acos(value)
    
    @staticmethod
    def Asin(value):
        """Arc sine"""
        import math
        return math.asin(value)
    
    @staticmethod
    def Atan(value):
        """Arc tangent"""
        import math
        return math.atan(value)
    
    @staticmethod
    def Atan2(y, x):
        """Arc tangent of y/x"""
        import math
        return math.atan2(y, x)
    
    @staticmethod
    def Ceil(value):
        """Ceiling"""
        import math
        return math.ceil(value)
    
    @staticmethod
    def CeilToInt(value):
        """Ceiling to integer"""
        import math
        return int(math.ceil(value))
    
    @staticmethod
    def Clamp(value, min_val, max_val):
        """Clamp value between min and max"""
        return max(min_val, min(value, max_val))
    
    @staticmethod
    def Clamp01(value):
        """Clamp value between 0 and 1"""
        return max(0.0, min(value, 1.0))
    
    @staticmethod
    def ClampAngle(angle, min_val, max_val):
        """Clamp angle between min and max"""
        if angle < -360:
            angle += 360
        if angle > 360:
            angle -= 360
        return MockMathf.Clamp(angle, min_val, max_val)
    
    @staticmethod
    def Cos(value):
        """Cosine"""
        import math
        return math.cos(value)
    
    @staticmethod
    def DeltaAngle(current, target):
        """Delta angle between current and target"""
        delta = target - current
        if delta > 180:
            delta -= 360
        elif delta < -180:
            delta += 360
        return delta
    
    @staticmethod
    def Exp(value):
        """Exponential"""
        import math
        return math.exp(value)
    
    @staticmethod
    def Floor(value):
        """Floor"""
        import math
        return math.floor(value)
    
    @staticmethod
    def FloorToInt(value):
        """Floor to integer"""
        import math
        return int(math.floor(value))
    
    @staticmethod
    def Lerp(a, b, t):
        """Linear interpolation"""
        return a + (b - a) * MockMathf.Clamp01(t)
    
    @staticmethod
    def LerpAngle(a, b, t):
        """Linear interpolation for angles"""
        delta = MockMathf.DeltaAngle(a, b)
        return a + delta * MockMathf.Clamp01(t)
    
    @staticmethod
    def LerpUnclamped(a, b, t):
        """Linear interpolation unclamped"""
        return a + (b - a) * t
    
    @staticmethod
    def Log(value, base=None):
        """Logarithm"""
        import math
        if base is None:
            return math.log(value)
        return math.log(value, base)
    
    @staticmethod
    def Log10(value):
        """Base 10 logarithm"""
        import math
        return math.log10(value)
    
    @staticmethod
    def Max(*args):
        """Maximum value"""
        return max(args)
    
    @staticmethod
    def Min(*args):
        """Minimum value"""
        return min(args)
    
    @staticmethod
    def MoveTowards(current, target, max_delta):
        """Move towards target by max delta"""
        if abs(target - current) <= max_delta:
            return target
        return current + MockMathf.Sign(target - current) * max_delta
    
    @staticmethod
    def MoveTowardsAngle(current, target, max_delta):
        """Move towards angle by max delta"""
        delta = MockMathf.DeltaAngle(current, target)
        if -max_delta < delta < max_delta:
            return target
        target = current + delta
        return MockMathf.MoveTowards(current, target, max_delta)
    
    @staticmethod
    def Pow(value, power):
        """Power"""
        return value ** power
    
    @staticmethod
    def Repeat(t, length):
        """Repeat value within length"""
        return t - MockMathf.Floor(t / length) * length
    
    @staticmethod
    def Round(value):
        """Round to nearest integer"""
        return round(value)
    
    @staticmethod
    def RoundToInt(value):
        """Round to integer"""
        return int(round(value))
    
    @staticmethod
    def Sign(value):
        """Sign of value"""
        if value > 0:
            return 1
        elif value < 0:
            return -1
        return 0
    
    @staticmethod
    def Sin(value):
        """Sine"""
        import math
        return math.sin(value)
    
    @staticmethod
    def SmoothStep(from_val, to_val, t):
        """Smooth step interpolation"""
        t = MockMathf.Clamp01(t)
        t = -2.0 * t * t * t + 3.0 * t * t
        return to_val * t + from_val * (1.0 - t)
    
    @staticmethod
    def Sqrt(value):
        """Square root"""
        import math
        return math.sqrt(value)
    
    @staticmethod
    def Tan(value):
        """Tangent"""
        import math
        return math.tan(value)


class MockWaitForSeconds:
    """Mock implementation of UnityEngine.WaitForSeconds"""
    
    def __init__(self, seconds):
        self.seconds = float(seconds)
    
    def __str__(self):
        return "WaitForSeconds({})".format(self.seconds)
    
    def __repr__(self):
        return "MockWaitForSeconds({})".format(self.seconds)


class MockEventType:
    """Mock implementation of UnityEngine.EventType enum"""
    
    # Event types used by Unity GUI system
    Ignore = 0
    Used = 1
    MouseDown = 2
    MouseUp = 3
    MouseMove = 4
    MouseDrag = 5
    KeyDown = 6
    KeyUp = 7
    ScrollWheel = 8
    Repaint = 9
    Layout = 10
    DragUpdated = 11
    DragPerform = 12
    DragExited = 15
    ValidateCommand = 16
    ExecuteCommand = 17
    ContextClick = 18


class MockEvent:
    """Mock implementation of UnityEngine.Event"""
    
    def __init__(self):
        self.type = MockEventType.Ignore
        self.mousePosition = MockVector2(0, 0)
        self.delta = MockVector2(0, 0)
        self.button = 0
        self.modifiers = 0
        self.keyCode = 0
        self.character = '\0'
        self.commandName = ""
        self.clickCount = 0
        self.isMouse = False
        self.isKey = False
        self.shift = False
        self.control = False
        self.alt = False
        self.command = False
    
    @property
    def current(self):
        """Get current event"""
        return self
    
    def Use(self):
        """Mark event as used"""
        pass


class MockGUIUtility:
    """Mock implementation of UnityEngine.GUIUtility"""
    
    @staticmethod
    def GetControlID(hint, focus_type):
        """Get a unique control ID"""
        # Simple implementation for testing
        return hash((hint, focus_type)) % 1000000
    
    @staticmethod
    def ScreenToGUIPoint(screen_point):
        """Convert screen point to GUI point"""
        return screen_point  # Simplified for testing
    
    @staticmethod
    def GUIToScreenPoint(gui_point):
        """Convert GUI point to screen point"""
        return gui_point  # Simplified for testing
    
    @staticmethod
    def RotateAroundPivot(angle, pivot_point):
        """Rotate around pivot point"""
        pass  # Simplified for testing
    
    @staticmethod
    def ScaleAroundPivot(scale, pivot_point):
        """Scale around pivot point"""
        pass  # Simplified for testing


class MockGUIContent:
    """Mock implementation of UnityEngine.GUIContent"""
    
    def __init__(self, text="", image=None, tooltip=""):
        self.text = str(text) if text is not None else ""
        self.image = image  # Could be a texture/image reference
        self.tooltip = str(tooltip) if tooltip is not None else ""
    
    def __str__(self):
        return self.text
    
    def __repr__(self):
        return "MockGUIContent('{}', image={}, tooltip='{}')".format(
            self.text, self.image, self.tooltip
        )
    
    @classmethod
    def none(cls):
        """Empty GUIContent"""
        return cls("", None, "")


class MockGUIStyle:
    """Mock implementation of UnityEngine.GUIStyle"""
    
    def __init__(self, style_name=None):
        """Initialize GUIStyle with optional style name (e.g., 'window', 'button', etc.)"""
        self.name = style_name or "default"
        
        self.normal = type('MockGUIStyleState', (), {
            'background': None,
            'textColor': MockColor.white()
        })()
        self.hover = type('MockGUIStyleState', (), {
            'background': None,
            'textColor': MockColor.white()
        })()
        self.active = type('MockGUIStyleState', (), {
            'background': None,
            'textColor': MockColor.white()
        })()
        self.focused = type('MockGUIStyleState', (), {
            'background': None,
            'textColor': MockColor.white()
        })()
        self.onNormal = type('MockGUIStyleState', (), {
            'background': None,
            'textColor': MockColor.white()
        })()
        self.onHover = type('MockGUIStyleState', (), {
            'background': None,
            'textColor': MockColor.white()
        })()
        self.onActive = type('MockGUIStyleState', (), {
            'background': None,
            'textColor': MockColor.white()
        })()
        self.onFocused = type('MockGUIStyleState', (), {
            'background': None,
            'textColor': MockColor.white()
        })()
        
        # Style properties
        self.fontSize = 12
        self.fontStyle = 0  # Normal
        self.alignment = 0  # UpperLeft
        self.wordWrap = False
        self.clipping = 0  # Overflow
        
        # Padding and margins
        self.padding = type('MockRectOffset', (), {
            'left': 0, 'right': 0, 'top': 0, 'bottom': 0
        })()
        self.margin = type('MockRectOffset', (), {
            'left': 0, 'right': 0, 'top': 0, 'bottom': 0
        })()
        self.border = type('MockRectOffset', (), {
            'left': 0, 'right': 0, 'top': 0, 'bottom': 0
        })()
        self.overflow = type('MockRectOffset', (), {
            'left': 0, 'right': 0, 'top': 0, 'bottom': 0
        })()
    
    def CalcSize(self, content):
        """Calculate size needed for content"""
        # Simplified calculation for testing
        if hasattr(content, 'text'):
            text_length = len(content.text)
        else:
            text_length = len(str(content))
        
        # Rough estimation: 8 pixels per character width, 16 pixels height
        return MockVector2(text_length * 8, 16)


class MockGUI:
    """Mock implementation of UnityEngine.GUI"""
    
    def __init__(self):
        self.color = MockColor.white()
        self.button_clicks = []
        self.text_fields = {}
        self.interaction_history = []  # Track GUI interactions for testing
        
        # Default GUI styles
        self.skin = type('MockGUISkin', (), {
            'button': MockGUIStyle(),
            'label': MockGUIStyle(),
            'textField': MockGUIStyle(),
            'box': MockGUIStyle()
        })()
    
    def Button(self, rect, text, *options):
        """Mock GUI button with rect positioning"""
        clicked = text in self.button_clicks
        if clicked:
            self.button_clicks.remove(text)
        return clicked
    
    def Label(self, rect, text, *options):
        """Mock GUI label with rect positioning"""
        pass
    
    def TextField(self, rect, text, *options):
        """Mock GUI text field with rect positioning"""
        field_id = "{}_{}_{}_{}".format(rect.x, rect.y, rect.width, rect.height)
        return self.text_fields.get(field_id, text)
    
    def WindowFunction(self, callback):
        """Mock GUI WindowFunction - returns the callback function"""
        return callback
    
    # Test helper methods
    def simulate_button_click(self, text):
        """Simulate clicking a button (for testing)"""
        self.button_clicks.append(text)
    
    def set_text_field_value(self, rect, new_value):
        """Set text field value (for testing)"""
        field_id = "{}_{}_{}_{}".format(rect.x, rect.y, rect.width, rect.height)
        self.text_fields[field_id] = new_value
    
    def clear_state(self):
        """Clear all GUI state (for testing)"""
        self.button_clicks.clear()
        self.text_fields.clear()
        self.interaction_history.clear()
    
    def reset_state(self):
        """Reset state (alias for clear_state)"""
        self.clear_state()
    
    def reset_for_test(self):
        """Reset for test (alias for clear_state)"""
        self.clear_state()


class MockScreen:
    """Mock implementation of UnityEngine.Screen"""
    
    width = 1920
    height = 1080
    dpi = 96.0
    
    @classmethod
    def set_resolution(cls, width, height):
        """Set screen resolution (for testing)"""
        cls.width = width
        cls.height = height


class MockApplication:
    """Mock implementation of UnityEngine.Application"""
    
    # Application properties
    dataPath = "/mock/StudioNEO_64_Data"  # This will make get_engine_id() return "neo"
    persistentDataPath = "/mock/persistent/data/path"
    streamingAssetsPath = "/mock/streaming/assets/path"
    temporaryCachePath = "/mock/temp/cache/path"
    consoleLogPath = "/mock/console/log/path"
    
    # Application state
    isPlaying = True
    isEditor = False
    isFocused = True
    runInBackground = True
    targetFrameRate = 60
    
    # Platform info
    platform = "WindowsPlayer"
    unityVersion = "2021.3.0f1"
    version = "1.0.0"
    companyName = "MockCompany"
    productName = "MockProduct"
    
    # System info
    systemLanguage = "English"
    internetReachability = 2  # ReachableViaLocalAreaNetwork
    
    @classmethod
    def Quit(cls, exit_code=0):
        """Quit the application"""
        cls.isPlaying = False
    
    @classmethod
    def OpenURL(cls, url):
        """Open URL in browser"""
        pass
    
    @classmethod
    def RequestUserAuthorization(cls, mode):
        """Request user authorization"""
        return True
    
    @classmethod
    def HasUserAuthorization(cls, mode):
        """Check if user has authorization"""
        return True
    
    @classmethod
    def CanStreamedLevelBeLoaded(cls, level_index):
        """Check if streamed level can be loaded"""
        return True
    
    @classmethod
    def GetStreamProgressForLevel(cls, level_index):
        """Get stream progress for level"""
        return 1.0
    
    @classmethod
    def CaptureScreenshot(cls, filename):
        """Capture screenshot"""
        pass
    
    @classmethod
    def SetStackTraceLogType(cls, log_type, stack_trace_type):
        """Set stack trace log type"""
        pass
    
    @classmethod
    def GetStackTraceLogType(cls, log_type):
        """Get stack trace log type"""
        return 0
    
    # Test helper methods
    @classmethod
    def set_platform(cls, platform):
        """Set platform for testing"""
        cls.platform = platform
    
    @classmethod
    def set_editor_mode(cls, is_editor):
        """Set editor mode for testing"""
        cls.isEditor = is_editor
        cls.isPlaying = not is_editor
    
    @classmethod
    def set_focus(cls, is_focused):
        """Set focus state for testing"""
        cls.isFocused = is_focused
    
    @classmethod
    def reset_for_test(cls):
        """Reset application state for testing"""
        cls.isPlaying = True
        cls.isEditor = False
        cls.isFocused = True
        cls.runInBackground = True
        cls.targetFrameRate = 60
        cls.platform = "WindowsPlayer"


# Global instances that will be used by the plugin
_mock_input = MockInput()
_mock_gui = MockGUI()
_mock_gui_layout = MockGUILayout()


class MockObject:
    """Mock implementation of UnityEngine.Object (base class for Unity objects)"""
    
    def __init__(self, name=""):
        self.name = name
        self.hideFlags = 0
    
    def __str__(self):
        return self.name if self.name else "MockObject"
    
    def __repr__(self):
        return "MockObject('{}')".format(self.name)
    
    def __bool__(self):
        """Unity objects can be checked for null/existence"""
        return True
    
    def __nonzero__(self):
        """Python 2 compatibility for bool check"""
        return True
    
    @staticmethod
    def Destroy(obj, delay=0.0):
        """Destroy Unity object"""
        pass
    
    @staticmethod
    def DestroyImmediate(obj, allow_destroying_assets=False):
        """Destroy Unity object immediately"""
        pass
    
    @staticmethod
    def DontDestroyOnLoad(obj):
        """Don't destroy object on scene load"""
        pass
    
    @staticmethod
    def FindObjectOfType(object_type):
        """Find object of specified type"""
        return None
    
    @staticmethod
    def FindObjectsOfType(object_type):
        """Find all objects of specified type"""
        return []
    
    @staticmethod
    def Instantiate(original, position=None, rotation=None, parent=None):
        """Instantiate Unity object"""
        if hasattr(original, '__class__'):
            return original.__class__()
        return MockObject()
    
    def GetInstanceID(self):
        """Get instance ID"""
        return id(self)


def setup_unity_mocks():
    """
    Set up Unity Engine mocks in the global namespace.
    This function should be called before importing any plugin modules.
    """
    # Create mock UnityEngine module
    unity_engine = type(sys)('UnityEngine')
    
    # Add all mock classes to the module
    unity_engine.Application = MockApplication
    unity_engine.Vector2 = MockVector2
    unity_engine.Vector3 = MockVector3
    unity_engine.Vector4 = MockVector4
    unity_engine.Matrix4x4 = MockMatrix4x4
    unity_engine.Rect = MockRect
    unity_engine.Color = MockColor
    unity_engine.Quaternion = MockQuaternion
    unity_engine.KeyCode = MockKeyCode
    unity_engine.TextAnchor = MockTextAnchor
    unity_engine.Input = _mock_input
    unity_engine.Event = MockEvent
    unity_engine.EventType = MockEventType
    unity_engine.WaitForSeconds = MockWaitForSeconds
    unity_engine.Mathf = MockMathf
    unity_engine.Time = MockTime
    unity_engine.GUI = _mock_gui
    unity_engine.GUILayout = _mock_gui_layout
    unity_engine.GUIStyle = MockGUIStyle
    unity_engine.GUIContent = MockGUIContent
    unity_engine.GUIUtility = MockGUIUtility
    unity_engine.Screen = MockScreen
    unity_engine.Transform = MockTransform
    unity_engine.Component = MockComponent
    unity_engine.GameObject = MockGameObject
    unity_engine.Animator = MockAnimator
    unity_engine.AnimationClip = MockAnimationClip
    unity_engine.AnimatorClipInfo = MockAnimatorClipInfo
    unity_engine.AnimatorStateInfo = MockAnimatorStateInfo
    unity_engine.RuntimeAnimatorController = MockRuntimeAnimatorController
    unity_engine.Object = MockObject
    
    # Add the mock module to sys.modules so imports work
    sys.modules['UnityEngine'] = unity_engine
    
    # Set up Unity game-specific modules (GameCursor, CameraControl)
    game_cursor_module = type(sys)('GameCursor')
    camera_control_module = type(sys)('CameraControl')
    
    # Add mock classes to modules
    game_cursor_module.GameCursor = MockGameCursor
    camera_control_module.CameraControl = MockCameraControl
    
    # Add the mock modules to sys.modules so imports work
    sys.modules['GameCursor'] = game_cursor_module
    sys.modules['CameraControl'] = camera_control_module
    
    # Use test logging system if available
    try:
        from framework.base import get_logger
        logger = get_logger("UnityMocks")
        logger.debug("Unity Engine mocks initialized")
    except ImportError:
        # Fallback to print if logging system not available
        print("Unity Engine mocks initialized")


def get_mock_input():
    """Get the global mock Input instance for testing"""
    return _mock_input


def get_mock_gui():
    """Get the global mock GUI instance for testing"""
    return _mock_gui


def get_mock_gui_layout():
    """Get the global mock GUILayout instance for testing"""
    return _mock_gui_layout


class MockTransform:
    """Mock implementation of UnityEngine.Transform"""
    def __init__(self, game_object):
        self.game_object = game_object
        self.position = MockVector3.zero()
        self.rotation = MockVector3.zero()
        self.scale = MockVector3.one()

class MockComponent(object):
    """Mock implementation of UnityEngine.Component"""
    def __init__(self):
        self.game_object = None

class MockAnimationClip:
    """Mock implementation of UnityEngine.AnimationClip"""
    
    def __init__(self, name="default_clip", length=3.0, frame_rate=30.0):
        self.name = name
        self.length = length
        self.frameRate = frame_rate
    
    @property
    def clip(self):
        return self


class MockAnimatorClipInfo:
    """Mock implementation of UnityEngine.AnimatorClipInfo"""
    
    def __init__(self, clip=None):
        self.clip = clip or MockAnimationClip()


class MockAnimatorStateInfo:
    """Mock implementation of UnityEngine.AnimatorStateInfo"""
    
    def __init__(self):
        self.normalizedTime = 0.0
        self.length = 1.0
        self.speed = 1.0


class MockRuntimeAnimatorController:
    """Mock implementation of UnityEngine.RuntimeAnimatorController"""
    
    def __init__(self):
        self.animationClips = [
            MockAnimationClip("idle", 2.0, 30.0),
            MockAnimationClip("walk", 1.5, 30.0),
            MockAnimationClip("run", 1.0, 30.0),
            MockAnimationClip("sit_down", 2.5, 30.0),
            MockAnimationClip("wave", 1.8, 30.0)
        ]
    
    def get_clip_by_name(self, name):
        """Get animation clip by name"""
        for clip in self.animationClips:
            if name.lower() in clip.name.lower():
                return clip
        return MockAnimationClip(name, 2.0, 30.0)  # Default fallback


class MockAnimator(MockComponent):
    """Mock implementation of UnityEngine.Animator"""
    def __init__(self):
        super(MockAnimator, self).__init__()
        self.speed = 1.0
        self.cullingMode = 0
        self.runtimeAnimatorController = MockRuntimeAnimatorController()
        self._current_clip = MockAnimationClip()

    def Play(self, state_name, layer=-1, normalized_time=float('-inf')):
        """Play animation state"""
        if isinstance(state_name, str):
            self._current_clip = self.runtimeAnimatorController.get_clip_by_name(state_name)
        elif isinstance(state_name, int):
            # Handle integer state names
            if state_name < len(self.runtimeAnimatorController.animationClips):
                self._current_clip = self.runtimeAnimatorController.animationClips[state_name]

    def GetCurrentAnimatorClipInfo(self, layer):
        """Get current animator clip info"""
        return [MockAnimatorClipInfo(self._current_clip)]
    
    def GetCurrentAnimatorStateInfo(self, layer):
        """Get current animator state info"""
        return MockAnimatorStateInfo()

class MockGameObject:
    """Mock implementation of UnityEngine.GameObject"""
    def __init__(self, name=""):
        self.name = name
        self.transform = MockTransform(self)
        self._components = {}

    def GetComponent(self, component_type):
        return self._components.get(component_type)

    def AddComponent(self, component_type):
        component = component_type()
        component.game_object = self
        self._components[component_type] = component
        return component

class MockGameCursor:
    """Mock implementation of GameCursor"""
    
    def __init__(self):
        self.enabled = True
        self.visible = True
        self.lockState = 0  # CursorLockMode.None
    
    def SetCursor(self, texture, hotspot, mode):
        """Set cursor texture and mode"""
        pass
    
    def Show(self):
        """Show cursor"""
        self.visible = True
    
    def Hide(self):
        """Hide cursor"""
        self.visible = False


class MockCameraControl:
    """Mock implementation of CameraControl"""
    
    def __init__(self):
        self.enabled = True
        self.fieldOfView = 23.0
        self.transform = None
        self.camera = None
        self.target = None
        self.distance = 5.0
        self.rotationSpeed = 1.0
        self.zoomSpeed = 1.0
        self.minDistance = 1.0
        self.maxDistance = 20.0
    
    def SetTarget(self, target):
        """Set camera target"""
        self.target = target
    
    def SetDistance(self, distance):
        """Set camera distance"""
        self.distance = distance
    
    def SetRotation(self, rotation):
        """Set camera rotation"""
        pass
    
    def LookAt(self, target):
        """Make camera look at target"""
        pass


def reset_unity_mocks():
    """Reset all Unity mock states (useful between tests)"""
    _mock_input.reset_all_states()
    _mock_gui.clear_state()
    _mock_gui_layout.clear_state()
    MockScreen.width = 1920
    MockScreen.height = 1080

# Set the 'None' attribute dynamically to avoid Python keyword conflict
# This allows getattr(KeyCode, 'None') to work as expected
setattr(MockKeyCode, 'None', 0)
