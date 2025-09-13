"""
WindowsInput Mock Module for VNGE Harmony Link Plugin Testing

This module provides mock implementations of the WindowsInput library
that is used by the VNGE plugin for Windows input simulation.
"""

import sys


class MockVirtualKeyCode:
    """Mock implementation of WindowsInput VirtualKeyCode enum"""
    
    # Common key codes
    SPACE = 0x20
    RETURN = 0x0D
    ESCAPE = 0x1B
    TAB = 0x09
    SHIFT = 0x10
    CONTROL = 0x11
    MENU = 0x12  # Alt key
    
    # Letter keys
    VK_A = 0x41
    VK_B = 0x42
    VK_C = 0x43
    VK_D = 0x44
    VK_E = 0x45
    VK_F = 0x46
    VK_G = 0x47
    VK_H = 0x48
    VK_I = 0x49
    VK_J = 0x4A
    VK_K = 0x4B
    VK_L = 0x4C
    VK_M = 0x4D
    VK_N = 0x4E
    VK_O = 0x4F
    VK_P = 0x50
    VK_Q = 0x51
    VK_R = 0x52
    VK_S = 0x53
    VK_T = 0x54
    VK_U = 0x55
    VK_V = 0x56
    VK_W = 0x57
    VK_X = 0x58
    VK_Y = 0x59
    VK_Z = 0x5A
    
    # Number keys
    VK_0 = 0x30
    VK_1 = 0x31
    VK_2 = 0x32
    VK_3 = 0x33
    VK_4 = 0x34
    VK_5 = 0x35
    VK_6 = 0x36
    VK_7 = 0x37
    VK_8 = 0x38
    VK_9 = 0x39


class MockKeyCode:
    """Mock implementation of WindowsInput key codes"""
    
    # Common key codes
    VK_SPACE = 0x20
    VK_RETURN = 0x0D
    VK_ESCAPE = 0x1B
    VK_TAB = 0x09
    VK_SHIFT = 0x10
    VK_CONTROL = 0x11
    VK_MENU = 0x12  # Alt key
    
    # Letter keys
    VK_A = 0x41
    VK_B = 0x42
    VK_C = 0x43
    VK_D = 0x44
    VK_E = 0x45
    VK_F = 0x46
    VK_G = 0x47
    VK_H = 0x48
    VK_I = 0x49
    VK_J = 0x4A
    VK_K = 0x4B
    VK_L = 0x4C
    VK_M = 0x4D
    VK_N = 0x4E
    VK_O = 0x4F
    VK_P = 0x50
    VK_Q = 0x51
    VK_R = 0x52
    VK_S = 0x53
    VK_T = 0x54
    VK_U = 0x55
    VK_V = 0x56
    VK_W = 0x57
    VK_X = 0x58
    VK_Y = 0x59
    VK_Z = 0x5A
    
    # Number keys
    VK_0 = 0x30
    VK_1 = 0x31
    VK_2 = 0x32
    VK_3 = 0x33
    VK_4 = 0x34
    VK_5 = 0x35
    VK_6 = 0x36
    VK_7 = 0x37
    VK_8 = 0x38
    VK_9 = 0x39


class MockKeyboardInput:
    """Mock implementation of WindowsInput KeyboardInput"""
    
    def __init__(self):
        self.pressed_keys = []
        self.released_keys = []
    
    def key_down(self, key_code):
        """Simulate key down event"""
        self.pressed_keys.append(key_code)
    
    def key_up(self, key_code):
        """Simulate key up event"""
        self.released_keys.append(key_code)
    
    def key_press(self, key_code):
        """Simulate key press (down + up)"""
        self.key_down(key_code)
        self.key_up(key_code)
    
    def text_entry(self, text):
        """Simulate text entry"""
        for char in text:
            # Simplified - just record the text
            self.pressed_keys.append(ord(char.upper()))
            self.released_keys.append(ord(char.upper()))
    
    # Test helper methods
    def get_pressed_keys(self):
        """Get list of pressed keys (for testing)"""
        return self.pressed_keys.copy()
    
    def get_released_keys(self):
        """Get list of released keys (for testing)"""
        return self.released_keys.copy()
    
    def clear_history(self):
        """Clear key press history (for testing)"""
        self.pressed_keys.clear()
        self.released_keys.clear()


class MockMouseInput:
    """Mock implementation of WindowsInput MouseInput"""
    
    def __init__(self):
        self.position = (0, 0)
        self.clicks = []
        self.moves = []
    
    def move_to(self, x, y):
        """Move mouse to position"""
        self.position = (x, y)
        self.moves.append((x, y))
    
    def move_by(self, dx, dy):
        """Move mouse by relative amount"""
        new_x = self.position[0] + dx
        new_y = self.position[1] + dy
        self.move_to(new_x, new_y)
    
    def left_button_down(self):
        """Simulate left mouse button down"""
        self.clicks.append(('left', 'down', self.position))
    
    def left_button_up(self):
        """Simulate left mouse button up"""
        self.clicks.append(('left', 'up', self.position))
    
    def left_button_click(self):
        """Simulate left mouse button click"""
        self.left_button_down()
        self.left_button_up()
    
    def right_button_down(self):
        """Simulate right mouse button down"""
        self.clicks.append(('right', 'down', self.position))
    
    def right_button_up(self):
        """Simulate right mouse button up"""
        self.clicks.append(('right', 'up', self.position))
    
    def right_button_click(self):
        """Simulate right mouse button click"""
        self.right_button_down()
        self.right_button_up()
    
    def scroll_vertically(self, clicks):
        """Simulate vertical scrolling"""
        self.clicks.append(('scroll', 'vertical', clicks))
    
    def scroll_horizontally(self, clicks):
        """Simulate horizontal scrolling"""
        self.clicks.append(('scroll', 'horizontal', clicks))
    
    # Test helper methods
    def get_position(self):
        """Get current mouse position (for testing)"""
        return self.position
    
    def get_clicks(self):
        """Get list of mouse clicks (for testing)"""
        return self.clicks.copy()
    
    def get_moves(self):
        """Get list of mouse moves (for testing)"""
        return self.moves.copy()
    
    def clear_history(self):
        """Clear mouse action history (for testing)"""
        self.clicks.clear()
        self.moves.clear()


class MockInputSimulator:
    """Mock implementation of WindowsInput InputSimulator"""
    
    def __init__(self):
        self.keyboard = MockKeyboardInput()
        self.mouse = MockMouseInput()
    
    @property
    def Keyboard(self):
        """Get keyboard input simulator"""
        return self.keyboard
    
    @property
    def Mouse(self):
        """Get mouse input simulator"""
        return self.mouse
    
    # Test helper methods
    def reset_all(self):
        """Reset all input simulators (for testing)"""
        self.keyboard.clear_history()
        self.mouse.clear_history()


def setup_windows_input_mocks():
    """
    Set up WindowsInput mocks in the global namespace.
    This function should be called before importing any plugin modules.
    """
    # Create mock WindowsInput module
    windows_input = type(sys)('WindowsInput')
    
    # Add mock classes to the module
    windows_input.VirtualKeyCode = MockVirtualKeyCode
    windows_input.KeyCode = MockKeyCode
    windows_input.KeyboardInput = MockKeyboardInput
    windows_input.MouseInput = MockMouseInput
    windows_input.InputSimulator = MockInputSimulator
    
    # Add the mock module to sys.modules so imports work
    sys.modules['WindowsInput'] = windows_input
    
    # Use test logging system if available
    try:
        from framework.base import get_logger
        logger = get_logger("WindowsInputMocks")
        logger.debug("WindowsInput mocks initialized")
    except ImportError:
        # Fallback to print if logging system not available
        print("WindowsInput mocks initialized")


# Global instance for testing
_mock_input_simulator = MockInputSimulator()


def get_mock_input_simulator():
    """Get the global mock InputSimulator instance for testing"""
    return _mock_input_simulator


def reset_windows_input_mocks():
    """Reset all WindowsInput mock states (useful between tests)"""
    _mock_input_simulator.reset_all()
