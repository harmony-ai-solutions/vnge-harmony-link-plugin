"""
VNGE Engine Mock Classes for VNGE Harmony Link Plugin Testing

This module provides comprehensive mock implementations of VNGE-specific classes
that are used by the plugin, enabling testing without VNGE dependencies.
"""

import sys
import json
import os
import time
from collections import defaultdict


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


class MockStudioInfo:
    """Mock implementation of Studio.Info.Instance"""
    
    def __init__(self):
        self.dicAnimeLoadInfo = self._create_animation_database()
        self.dicAGroupCategory = self._create_group_categories()
    
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


class MockCharacterActor:
    """Mock implementation of VNGE character actor"""
    
    def __init__(self, entity_id, position=None, rotation=None):
        self.entity_id = entity_id
        self.text_name = entity_id
        
        # Import Vector3 from unity mocks
        from framework.mocks.unity_mocks import MockVector3
        self._pos = position or MockVector3(0, 0, 0)
        self._rot = rotation or MockVector3(0, 0, 0)
        
        # Animation state
        self.current_animation = None
        self.animation_history = []
        self.mouth_open_value = 0.0
        
        # Animation timing
        self.animation_start_time = None
        self.animation_duration = 2.0
        
        # Test helpers
        self._animation_callbacks = []
    
    @property
    def pos(self):
        """Get position"""
        return self._pos
    
    @property
    def rot(self):
        """Get rotation"""
        return self._rot
    
    def animate2(self, group, category, no, speed=1.0):
        """Mock animate2 method that records animation calls"""
        animation_key = "{}_{}_{}" .format(group, category, no)
        
        # Record animation
        animation_record = {
            'animation': animation_key,
            'group': group,
            'category': category,
            'no': no,
            'speed': speed,
            'timestamp': time.time(),
            'start_time': time.time()
        }
        
        self.current_animation = animation_record
        self.animation_history.append(animation_record)
        self.animation_start_time = time.time()
        
        # Calculate duration based on speed
        base_duration = self._get_animation_duration(group, category, no)
        self.animation_duration = base_duration / speed
        
        # Call any registered callbacks
        for callback in self._animation_callbacks:
            callback(self, animation_record)
        
        print("Character {} started animation: {} (duration: {:.2f}s)".format(self.entity_id, animation_key, self.animation_duration))
    
    def _get_animation_duration(self, group, category, no):
        """Get base animation duration (can be overridden for testing)"""
        # Default durations based on animation type
        duration_map = {
            (0, 0): 1.0,  # Idle animations - short
            (0, 1): 2.0,  # Movement animations - medium
            (1, 0): 1.5,  # Hand gestures - short-medium
            (1, 1): 1.0,  # Head gestures - short
            (2, 0): 3.0,  # Sitting animations - longer
            (2, 1): 3.0,  # Laying animations - longer
        }
        
        return duration_map.get((group, category), 2.0)  # Default 2 seconds
    
    def set_mouth_open(self, value):
        """Mock set_mouth_open method"""
        self.mouth_open_value = float(value)
    
    def is_animation_playing(self):
        """Check if an animation is currently playing"""
        if not self.animation_start_time:
            return False
        
        elapsed = time.time() - self.animation_start_time
        return elapsed < self.animation_duration
    
    def get_animation_progress(self):
        """Get current animation progress (0.0 to 1.0)"""
        if not self.animation_start_time:
            return 1.0
        
        elapsed = time.time() - self.animation_start_time
        progress = elapsed / self.animation_duration
        return min(progress, 1.0)
    
    def wait_for_animation_complete(self, timeout=10.0):
        """Wait for current animation to complete (for testing)"""
        start_wait = time.time()
        while self.is_animation_playing() and (time.time() - start_wait) < timeout:
            time.sleep(0.1)
        return not self.is_animation_playing()
    
    # Test helper methods
    def add_animation_callback(self, callback):
        """Add callback to be called when animation starts"""
        self._animation_callbacks.append(callback)
    
    def clear_animation_callbacks(self):
        """Clear all animation callbacks"""
        self._animation_callbacks.clear()
    
    def get_last_animation(self):
        """Get the last animation that was played"""
        return self.animation_history[-1] if self.animation_history else None
    
    def get_animation_count(self):
        """Get total number of animations played"""
        return len(self.animation_history)
    
    def clear_animation_history(self):
        """Clear animation history (for testing)"""
        self.animation_history.clear()
        self.current_animation = None
        self.animation_start_time = None
    
    def set_position(self, x, y, z):
        """Set actor position (for testing)"""
        from framework.mocks.unity_mocks import MockVector3
        self._pos = MockVector3(x, y, z)
    
    def set_rotation(self, x, y, z):
        """Set actor rotation (for testing)"""
        from framework.mocks.unity_mocks import MockVector3
        self._rot = MockVector3(x, y, z)
    
    def reset_for_test(self):
        """Reset for test"""
        self.clear_animation_history()
        self.clear_animation_callbacks()
        self.mouth_open_value = 0.0
        from framework.mocks.unity_mocks import MockVector3
        self._pos = MockVector3(0, 0, 0)
        self._rot = MockVector3(0, 0, 0)
    
    def reset_state(self):
        """Reset state (alias for reset_for_test)"""
        self.reset_for_test()


class MockGameObject:
    """Mock implementation of game object/prop"""
    
    def __init__(self, prop_id, position=None, rotation=None):
        self.prop_id = prop_id
        
        # Import Vector3 from unity mocks
        from framework.mocks.unity_mocks import MockVector3
        self.pos = position or MockVector3(0, 0, 0)
        self.rot = rotation or MockVector3(0, 0, 0)
    
    def set_position(self, x, y, z):
        """Set object position (for testing)"""
        from framework.mocks.unity_mocks import MockVector3
        self.pos = MockVector3(x, y, z)
    
    def set_rotation(self, x, y, z):
        """Set object rotation (for testing)"""
        from framework.mocks.unity_mocks import MockVector3
        self.rot = MockVector3(x, y, z)


class MockGData:
    """Mock implementation of vngameengine.GData"""
    
    def __init__(self):
        # Initialize with empty attributes that can be set dynamically
        pass


def mock_get_engine_id2():
    """Mock implementation of vngameengine.get_engine_id2()"""
    return "test_engine"


def mock_parse_key_code(key_string):
    """Mock implementation of vngameengine.parseKeyCode()"""
    # Return a tuple similar to what the real function returns
    # (unknown, keycode, ctrl, alt, shift)
    from framework.mocks.unity_mocks import MockKeyCode
    
    # Simple key mapping for testing
    key_map = {
        'V': MockKeyCode.V,
        'N': MockKeyCode.N,
        'C': MockKeyCode.C,
        'Space': MockKeyCode.Space,
        'Return': MockKeyCode.Return,
        'Escape': MockKeyCode.Escape,
    }
    
    keycode = key_map.get(key_string, MockKeyCode.A)  # Default to A
    return (False, keycode, False, False, False)  # No modifiers for simplicity


def setup_vnge_mocks():
    """
    Set up VNGE engine mocks in the global namespace.
    This function should be called before importing any plugin modules.
    """
    # Create mock vngameengine module
    vnge_module = type(sys)('vngameengine')
    vnge_module.get_engine_id2 = mock_get_engine_id2
    vnge_module.parseKeyCode = mock_parse_key_code
    vnge_module.GData = MockGData
    
    # Create mock Studio module
    studio_module = type(sys)('Studio')
    studio_module.Info = type('Info', (), {})()
    studio_module.Info.Instance = MockStudioInfo()
    
    # Create mock unity_util module (used by controls.py)
    unity_util_module = type(sys)('unity_util')
    unity_util_module.metakey_state = lambda: (False, False, False)  # ctrl, alt, shift
    
    # Create mock skin_customwindow module
    skin_customwindow_module = type(sys)('skin_customwindow')
    
    class MockSkinCustomWindow:
        def __init__(self):
            self.funcSetup = None
            self.funcWindowGUI = None
            self.metadata = None
            self.gui_data = None
    
    skin_customwindow_module.SkinCustomWindow = MockSkinCustomWindow
    
    # Create mock libkfguictrl module
    libkfguictrl_module = type(sys)('libkfguictrl')
    
    class MockComboListBox:
        def __init__(self, rect, height, options, selected_index=0):
            from framework.mocks.unity_mocks import MockRect
            self.rect = rect if hasattr(rect, 'x') else MockRect(0, 0, 100, 25)
            self.height = height
            self.options = options or []
            self.selected_index = selected_index
            self.onSelectChangeCallback = None
        
        def paint(self):
            """Mock paint method"""
            pass
        
        def importListItem(self, item):
            """Mock import list item"""
            self.options.append(item)
        
        # Test helper methods
        def simulate_selection_change(self, new_index):
            """Simulate user selecting a different option"""
            if 0 <= new_index < len(self.options):
                old_index = self.selected_index
                self.selected_index = new_index
                if self.onSelectChangeCallback:
                    self.onSelectChangeCallback(self, new_index, self.options[new_index])
    
    libkfguictrl_module.ComboListBox = MockComboListBox
    
    # Add all modules to sys.modules
    sys.modules['vngameengine'] = vnge_module
    sys.modules['Studio'] = studio_module
    sys.modules['unity_util'] = unity_util_module
    sys.modules['skin_customwindow'] = skin_customwindow_module
    sys.modules['libkfguictrl'] = libkfguictrl_module
    
    try:
        from framework.base import get_logger
        logger = get_logger("VNGEMocks")
        logger.debug("VNGE engine mocks initialized")
    except ImportError:
        print("VNGE engine mocks initialized")


def create_mock_character_actor(entity_id, position=None, rotation=None):
    """Create a mock character actor for testing"""
    return MockCharacterActor(entity_id, position, rotation)


def create_mock_game_object(prop_id, position=None, rotation=None):
    """Create a mock game object/prop for testing"""
    return MockGameObject(prop_id, position, rotation)


def get_mock_studio_info():
    """Get the mock Studio.Info instance"""
    return MockStudioInfo()


def create_test_animation_database():
    """Create a test animation database with known animations"""
    return {
        'walk': {'group': 0, 'category': 1, 'no': 0, 'duration': 2.0},
        'run': {'group': 0, 'category': 1, 'no': 2, 'duration': 1.5},
        'wave': {'group': 1, 'category': 0, 'no': 0, 'duration': 1.5},
        'nod': {'group': 1, 'category': 1, 'no': 0, 'duration': 1.0},
        'sit_down': {'group': 2, 'category': 0, 'no': 0, 'duration': 3.0},
        'stand_up': {'group': 2, 'category': 0, 'no': 2, 'duration': 3.0},
        'idle': {'group': 0, 'category': 0, 'no': 0, 'duration': 1.0},
    }
