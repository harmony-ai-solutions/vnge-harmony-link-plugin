import sys
import os
import time

# Add the Lib directory to the Python path
lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'Lib'))
if lib_path not in sys.path:
    sys.path.append(lib_path)

# Import actual VNGE classes
from vngameengine import VNController, VNNeoController, GData
from vngameenginestudio import StudioController
from ..mocks.unity_mocks import MockGameObject, MockVector3
from ..mocks.system_mocks import MockStudio


def create_gdata_fixture():
    """
    Create a GData fixture with realistic test data.
    """
    gdata = GData()
    gdata.game = None
    gdata.count = 0
    gdata._check_list = {}
    
    return gdata


def create_scene_data_fixture(entities=None, scene_file="test_scene.png"):
    """
    Create scene data fixture with realistic test data.
    Note: Using GData as scene data container since VNGE uses it this way.
    """
    if entities is None:
        entities = ['kaji', 'user']
    
    # Initialize scene data attributes
    scenedata = create_gdata_fixture()
    scenedata.actors = {}
    scenedata.props = {}
    scenedata.current_action = None  # Fix the issue mentioned in memory bank
    scenedata.scene_loaded = True
    scenedata.scene_file = scene_file
    
    # Add test entity data
    for i, entity_id in enumerate(entities):
        scenedata.actors[entity_id] = {
            'entity_id': entity_id,
            'position': MockVector3(i * 2.0, 0.0, 0.0),
            'rotation': MockVector3(0.0, 0.0, 0.0),
            'animation_state': 'idle',
            'is_active': True,
            'last_update': time.time()
        }
    
    return scenedata


def create_vncontroller_fixture(engine_name="charastudio", entities=None):
    """
    Create a VNController fixture using the actual VNGE VNController class.
    This provides realistic behavior while still being controllable for testing.
    """
    if entities is None:
        entities = ['kaji', 'user']
    
    # Create a mock game object to attach the controller to
    game_object = MockGameObject("VNGE_Game_Test")
    
    # Select the appropriate controller class based on engine type
    if engine_name == "studio":
        game_controller = StudioController()
    elif engine_name in ["neo", "charastudio", "neov2", "phstudio"]:
        # For NEO-based engines, we need to use VNNeoController or its subclasses
        # Since VNNeoController is also abstract, we'll create a simple test controller
        class TestNeoController(VNNeoController):
            def __init__(self):
                self.engine_name = engine_name
                self.pygamepath = lib_path
                # Initialize required attributes before calling parent constructor
                self._vnButtons = ["Test Action"]
                self._vnButtonsActions = [lambda g: None]
                VNNeoController.__init__(self)
        
        game_controller = TestNeoController()
    else:
        # Default fallback - create a basic test controller
        class TestController(VNController):
            def __init__(self):
                self.engine_name = engine_name
                self.pygamepath = lib_path
                VNController.__init__(self)
        
        game_controller = TestController()
    
    # Set up the controller for testing
    game_controller.gameObject = game_object
    game_controller.component = game_controller
    
    # Override studio with our mock for testing
    game_controller.studio = MockStudio()
    
    # Initialize scene data with actual GData
    game_controller.scenedata = create_scene_data_fixture(entities)
    game_controller.gdata = create_gdata_fixture()
    
    # Initialize essential attributes for testing
    game_controller._scenef_actors = {}
    game_controller._scenef_props = {}
    
    # Set up test-friendly initial state
    game_controller.visible = True
    game_controller.isTitleScreen = False
    game_controller.isFuncLocked = False
    game_controller.current_game = "test_game"
    
    # Initialize character registration
    game_controller.registeredChars = {}
    game_controller.register_char("s", "ffffff", "System")
    game_controller.register_char("kaji", "ff5555", "Kaji")
    game_controller.register_char("user", "5555ff", "User")
    
    # Set up basic text and buttons
    game_controller._vnText = "VNGE Test Controller Ready"
    game_controller._vnButtons = ["Test Action"]
    game_controller._vnButtonsActions = [lambda g: None]
    
    # Initialize the controller
    try:
        game_controller.Start()
    except Exception as e:
        print("Warning: VNController.Start() failed: {}".format(e))
        # Continue anyway for testing
    
    return game_controller


def create_game_fixture(engine_name="charastudio", entities=None):
    """
    Creates and initializes a VNController instance for testing using actual VNGE classes.
    """
    return create_vncontroller_fixture(engine_name, entities)


def create_game_fixture_with_scene_data(scene_file="test_scene.png", entities=None):
    """
    Create game fixture with pre-loaded scene data for testing.
    """
    game = create_game_fixture(entities=entities)
    
    # Update scene data with file information
    game.scenedata.scene_file = scene_file
    game.scenedata.scene_loaded = True
    
    # Populate actors in scene data
    if entities:
        for i, entity_id in enumerate(entities):
            game.scenedata.actors[entity_id] = {
                'entity_id': entity_id,
                'position': MockVector3(i * 2.0, 0.0, 0.0),
                'rotation': MockVector3(0.0, 0.0, 0.0),
                'animation_state': 'idle',
                'is_active': True,
                'last_update': time.time()
            }
    
    return game


def create_game_fixture_with_timers(timer_configs=None):
    """
    Create game fixture with pre-configured timers for testing timing systems.
    """
    game = create_game_fixture()
    
    if timer_configs is None:
        def timer1_complete(g):
            print("Timer 1 complete")
        
        def timer2_complete(g):
            print("Timer 2 complete")
        
        timer_configs = [
            {'duration': 1.0, 'end_func': timer1_complete},
            {'duration': 2.0, 'end_func': timer2_complete},
        ]
    
    # Set up timers
    for config in timer_configs:
        timer_id = game.set_timer(
            config['duration'],
            config['end_func'],
            config.get('upd_func')
        )
        print("Set timer {} for {} seconds".format(timer_id, config['duration']))
    
    return game


def create_performance_test_game_fixture(entity_count=10):
    """
    Create game fixture optimized for performance testing with many entities.
    """
    entities = ['entity_{}'.format(i) for i in range(entity_count)]
    game = create_game_fixture(entities=entities)
    
    # Pre-populate with performance test data
    for entity_id in entities:
        game.scenedata.actors[entity_id] = {
            'entity_id': entity_id,
            'position': MockVector3(0.0, 0.0, 0.0),
            'last_action_time': time.time(),
            'action_count': 0,
            'is_active': True
        }
    
    return game


def create_game_fixture_with_registered_actors(actor_fixtures=None):
    """
    Create game fixture with pre-registered actor fixtures for comprehensive testing.
    """
    game = create_game_fixture()
    
    if actor_fixtures:
        for entity_id, actor in actor_fixtures.items():
            game.scenef_reg_actor(entity_id, actor)
            
            # Also add to scene data
            if hasattr(actor, 'objctrl') and hasattr(actor.objctrl, 'oiCharInfo'):
                pos = actor.objctrl.oiCharInfo.changeAmount.pos
                rot = actor.objctrl.oiCharInfo.changeAmount.rot
            else:
                pos = MockVector3(0.0, 0.0, 0.0)
                rot = MockVector3(0.0, 0.0, 0.0)
            
            game.scenedata.actors[entity_id] = {
                'entity_id': entity_id,
                'position': pos,
                'rotation': rot,
                'actor_instance': actor,
                'is_active': True,
                'last_update': time.time()
            }
    
    return game
