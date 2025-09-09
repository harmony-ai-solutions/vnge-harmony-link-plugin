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
    
    # Special keys
    Space = 32
    Return = 13
    Escape = 27
    LeftShift = 304
    RightShift = 303
    LeftControl = 306
    RightControl = 305
    LeftAlt = 308
    RightAlt = 307


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


class MockGUI:
    """Mock implementation of UnityEngine.GUI"""
    
    def __init__(self):
        self.color = MockColor.white()
        self.button_clicks = []
        self.text_fields = {}
        self.interaction_history = []  # Track GUI interactions for testing
    
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


# Global instances that will be used by the plugin
_mock_input = MockInput()
_mock_gui = MockGUI()
_mock_gui_layout = MockGUILayout()


def setup_unity_mocks():
    """
    Set up Unity Engine mocks in the global namespace.
    This function should be called before importing any plugin modules.
    """
    # Create mock UnityEngine module
    unity_engine = type(sys)('UnityEngine')
    
    # Add all mock classes to the module
    unity_engine.Vector2 = MockVector2
    unity_engine.Vector3 = MockVector3
    unity_engine.Rect = MockRect
    unity_engine.Color = MockColor
    unity_engine.KeyCode = MockKeyCode
    unity_engine.Input = _mock_input
    unity_engine.GUI = _mock_gui
    unity_engine.GUILayout = _mock_gui_layout
    unity_engine.Screen = MockScreen
    
    # Add the mock module to sys.modules so imports work
    sys.modules['UnityEngine'] = unity_engine
    
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


def reset_unity_mocks():
    """Reset all Unity mock states (useful between tests)"""
    _mock_input.reset_all_states()
    _mock_gui.clear_state()
    _mock_gui_layout.clear_state()
    MockScreen.width = 1920
    MockScreen.height = 1080
