"""
Unity Util Mock Module for VNGE Harmony Link Plugin Testing

This module provides mock implementations of the unity_util module
that is used by the VNGE plugin for Unity utility functions.
"""

import sys


class MockGUIBehavior:
    """Mock GUI behavior for testing"""

    def __init__(self, controller_class):
        self.controller_class = controller_class
        self.controller_instance = None
        self.is_active = True

    def start(self):
        """Start the behavior"""
        if self.controller_class:
            self.controller_instance = self.controller_class()

    def stop(self):
        """Stop the behavior"""
        self.is_active = False

    def update(self):
        """Update the behavior"""
        if self.is_active and self.controller_instance:
            if hasattr(self.controller_instance, 'Update'):
                self.controller_instance.Update()


class MockUnityUtil:
    """Mock implementation of unity_util utility functions"""
    
    # Class variables to track state
    _behaviors = []
    _metakey_state = (False, False, False)  # ctrl, alt, shift
    
    @staticmethod
    def metakey_state():
        """
        Get the current state of meta keys (ctrl, alt, shift).
        This is the most frequently used function in unity_util.
        Returns: (ctrl, alt, shift) tuple of booleans
        """
        return MockUnityUtil._metakey_state
    
    @staticmethod
    def clean_behaviors():
        """
        Clean up all GUI behaviors.
        This is called before creating new behaviors.
        """
        for behavior in MockUnityUtil._behaviors:
            if hasattr(behavior, 'stop'):
                behavior.stop()
        MockUnityUtil._behaviors.clear()
    
    @staticmethod
    def create_gui_behavior(controller_class):
        """
        Create a GUI behavior from a controller class.
        This is used to create game controllers and UI systems.
        Returns: Mock behavior instance
        """
        behavior = MockGUIBehavior(controller_class)
        MockUnityUtil._behaviors.append(behavior)
        behavior.start()
        return behavior
    
    # Test helper methods
    @staticmethod
    def set_metakey_state(ctrl=False, alt=False, shift=False):
        """Set meta key state for testing"""
        MockUnityUtil._metakey_state = (ctrl, alt, shift)
    
    @staticmethod
    def get_active_behaviors():
        """Get list of active behaviors for testing"""
        return [b for b in MockUnityUtil._behaviors if b.is_active]
    
    @staticmethod
    def reset_for_test():
        """Reset all state for testing"""
        MockUnityUtil.clean_behaviors()
        MockUnityUtil._metakey_state = (False, False, False)
    
    # Additional utility functions that might be used
    @staticmethod
    def get_screen_width():
        """Get screen width"""
        return 1920
    
    @staticmethod
    def get_screen_height():
        """Get screen height"""
        return 1080
    
    @staticmethod
    def get_mouse_position():
        """Get current mouse position"""
        return (0, 0)
    
    @staticmethod
    def is_key_pressed(key_code):
        """Check if a key is pressed"""
        return False
    
    @staticmethod
    def is_mouse_button_pressed(button):
        """Check if a mouse button is pressed"""
        return False
    
    @staticmethod
    def get_time():
        """Get current time"""
        import time
        return time.time()
    
    @staticmethod
    def get_delta_time():
        """Get delta time"""
        return 0.016667  # ~60 FPS
    
    @staticmethod
    def log_message(message, level="INFO"):
        """Log a message"""
        print("[{}] {}".format(level, message))
    
    @staticmethod
    def create_vector2(x, y):
        """Create a Vector2"""
        from framework.mocks.unity_mocks import MockVector2
        return MockVector2(x, y)
    
    @staticmethod
    def create_vector3(x, y, z):
        """Create a Vector3"""
        from framework.mocks.unity_mocks import MockVector3
        return MockVector3(x, y, z)
    
    @staticmethod
    def create_rect(x, y, width, height):
        """Create a Rect"""
        from framework.mocks.unity_mocks import MockRect
        return MockRect(x, y, width, height)
    
    @staticmethod
    def create_color(r, g, b, a=1.0):
        """Create a Color"""
        from framework.mocks.unity_mocks import MockColor
        return MockColor(r, g, b, a)
    
    @staticmethod
    def distance_2d(pos1, pos2):
        """Calculate 2D distance between two positions"""
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        return (dx * dx + dy * dy) ** 0.5
    
    @staticmethod
    def distance_3d(pos1, pos2):
        """Calculate 3D distance between two positions"""
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        dz = pos1[2] - pos2[2]
        return (dx * dx + dy * dy + dz * dz) ** 0.5
    
    @staticmethod
    def lerp(a, b, t):
        """Linear interpolation"""
        return a + (b - a) * max(0.0, min(1.0, t))
    
    @staticmethod
    def clamp(value, min_val, max_val):
        """Clamp value between min and max"""
        return max(min_val, min(value, max_val))
    
    @staticmethod
    def normalize_angle(angle):
        """Normalize angle to 0-360 range"""
        while angle < 0:
            angle += 360
        while angle >= 360:
            angle -= 360
        return angle
    
    @staticmethod
    def degrees_to_radians(degrees):
        """Convert degrees to radians"""
        import math
        return degrees * math.pi / 180.0
    
    @staticmethod
    def radians_to_degrees(radians):
        """Convert radians to degrees"""
        import math
        return radians * 180.0 / math.pi
    
    @staticmethod
    def format_time(seconds):
        """Format time in seconds to readable string"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return "{}:{:02d}".format(minutes, secs)
    
    @staticmethod
    def safe_divide(a, b, default=0.0):
        """Safe division with default value"""
        if b == 0:
            return default
        return a / b
    
    @staticmethod
    def is_approximately_equal(a, b, tolerance=0.001):
        """Check if two values are approximately equal"""
        return abs(a - b) < tolerance


def setup_unity_util_mocks():
    """
    Set up unity_util mocks in the global namespace.
    This function should be called before importing any plugin modules.
    """
    # Create mock unity_util module
    unity_util = type(sys)('unity_util')
    
    # Add all utility functions to the module
    for attr_name in dir(MockUnityUtil):
        if not attr_name.startswith('_'):
            setattr(unity_util, attr_name, getattr(MockUnityUtil, attr_name))
    
    # Add the mock module to sys.modules so imports work
    sys.modules['unity_util'] = unity_util
    
    # Use test logging system if available
    try:
        from framework.base import get_logger
        logger = get_logger("UnityUtilMocks")
        logger.debug("unity_util mocks initialized")
    except ImportError:
        # Fallback to print if logging system not available
        print("unity_util mocks initialized")


def reset_unity_util_mocks():
    """Reset all unity_util mock states (useful between tests)"""
    MockUnityUtil.reset_for_test()


def get_mock_unity_util():
    """Get the MockUnityUtil class for testing"""
    return MockUnityUtil
