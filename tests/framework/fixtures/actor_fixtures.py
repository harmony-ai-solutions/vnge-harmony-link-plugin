import sys
import os
import time

# Add the Lib directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'Lib')))

from vngameengine import HSNeoOCIChar
from ..mocks.unity_mocks import MockGameObject, MockVector3, MockColor
from ..mocks.system_mocks import MockOCIChar


def create_realistic_oci_char_fixture(entity_id="kaji", sex=1, position=None, rotation=None):
    """
    Creates a realistic fixture for the OCIChar class with comprehensive state data.
    """
    # Create mock OCIChar with realistic data
    mock_oci_char = MockOCIChar()
    
    # Set basic properties
    mock_oci_char.sex = sex
    mock_oci_char.treeNodeObject.textName = entity_id
    
    # Set realistic position and rotation
    if position:
        mock_oci_char.charInfo.transform.position = MockVector3(position[0], position[1], position[2])
        mock_oci_char.oiCharInfo.changeAmount.pos = MockVector3(position[0], position[1], position[2])
    else:
        # Default positions for common test entities
        default_positions = {
            'kaji': MockVector3(0.0, 0.0, 0.0),
            'user': MockVector3(2.0, 0.0, 0.0),
            'test_character': MockVector3(-1.0, 0.0, 1.0)
        }
        pos = default_positions.get(entity_id, MockVector3(0.0, 0.0, 0.0))
        mock_oci_char.charInfo.transform.position = pos
        mock_oci_char.oiCharInfo.changeAmount.pos = pos
    
    if rotation:
        mock_oci_char.charInfo.transform.rotation = MockVector3(rotation[0], rotation[1], rotation[2])
        mock_oci_char.oiCharInfo.changeAmount.rot = MockVector3(rotation[0], rotation[1], rotation[2])
    else:
        # Default facing forward
        mock_oci_char.oiCharInfo.changeAmount.rot = MockVector3(0.0, 0.0, 0.0)
    
    # Set realistic character state
    mock_oci_char.oiCharInfo.animeSpeed = 1.0
    mock_oci_char.oiCharInfo.animePattern = 0
    mock_oci_char.charAnimeCtrl.normalizedTime = 0.0
    mock_oci_char.charAnimeCtrl.isForceLoop = False
    
    # Set realistic clothing and accessory states
    if sex == 1:  # Female
        mock_oci_char.charFileStatus.clothesState = [0, 0, 0, 0, 0, 0, 0, 0]  # All clothes on
        mock_oci_char.charFileStatus.showAccessory = [True] * 20  # All accessories visible
        mock_oci_char.oiCharInfo.skinRate = 0.3  # Moderate skin shine
        mock_oci_char.oiCharInfo.nipple = 0.0  # Default nipple state
    else:  # Male
        mock_oci_char.charFileStatus.clothesState = [0, 0, 0, 0, 0, 0, 0, 0]  # All clothes on
        mock_oci_char.charFileStatus.showAccessory = [True] * 10  # Male accessories
        mock_oci_char.oiCharInfo.visibleSon = False  # Default son visibility
        mock_oci_char.oiCharInfo.simpleColor = MockColor(0.8, 0.7, 0.6, 1.0)  # Skin tone
    
    # Set realistic facial expressions
    mock_oci_char.charFileStatus.eyesLookPtn = 0  # Looking forward
    mock_oci_char.charFileStatus.neckLookPtn = 0  # Neck forward
    mock_oci_char.charFileStatus.eyesBlink = True  # Blinking enabled
    mock_oci_char.charFileStatus.eyesOpenMax = 1.0  # Eyes fully open
    mock_oci_char.oiCharInfo.mouthOpen = 0.0  # Mouth closed
    mock_oci_char.oiCharInfo.lipSync = False  # Lip sync disabled
    
    # Set realistic body shape values
    if sex == 1:  # Female
        mock_oci_char.charInfo.chaFile.custom.body.shapeValueBody = [
            0.5,   # Height
            0.6,   # Breast size
            0.4,   # Waist
            0.5,   # Hip
            0.5,   # Arm thickness
            0.5,   # Leg thickness
            0.5,   # Shoulder width
            0.5,   # Neck thickness
            0.5,   # Torso length
            0.5    # Leg length
        ]
        mock_oci_char.charInfo.chaFile.custom.face.shapeValueFace = [0.5] * 20  # Default face shape
    else:  # Male
        mock_oci_char.charInfo.chaFile.custom.body.shapeValueBody = [
            0.7,   # Height (taller)
            0.0,   # No breast
            0.6,   # Waist (broader)
            0.4,   # Hip (narrower)
            0.7,   # Arm thickness (more muscular)
            0.6,   # Leg thickness
            0.8,   # Shoulder width (broader)
            0.6,   # Neck thickness
            0.6,   # Torso length
            0.6    # Leg length
        ]
        mock_oci_char.charInfo.chaFile.custom.face.shapeValueFace = [0.5] * 20  # Default face shape
    
    # Initialize IK/FK systems
    mock_oci_char.oiCharInfo.enableIK = False
    mock_oci_char.oiCharInfo.enableFK = False
    mock_oci_char.oiCharInfo.activeIK = [False] * 5  # Body, RightLeg, LeftLeg, RightArm, LeftArm
    mock_oci_char.oiCharInfo.activeFK = [False] * 7  # Hair, Neck, Breast, Body, RightHand, LeftHand, Skirt
    
    # Initialize voice system
    mock_oci_char.voiceCtrl.isPlay = False
    mock_oci_char.voiceCtrl.list = []
    mock_oci_char.voiceCtrl.repeat = 0  # No repeat
    
    # Mark as initialized for testing
    mock_oci_char.is_initialized = True
    
    return mock_oci_char


def create_oci_char_fixture(sex=1):
    """
    Creates a fixture for the OCIChar class.
    """
    return create_realistic_oci_char_fixture("test_character", sex)


def create_actor_fixture(entity_id="kaji", sex=1, position=None, rotation=None):
    """
    Creates and initializes a proper vnactor.ActorHSNeo instance for testing,
    using a realistic fixture for OCIChar with enhanced data.
    """
    # Create realistic OCIChar fixture
    oci_char_fixture = create_realistic_oci_char_fixture(entity_id, sex, position, rotation)
    
    # Create HSNeoOCIChar wrapper
    hsneo_char = HSNeoOCIChar(oci_char_fixture)
    
    # Get the actor instance
    actor = hsneo_char.as_actor
    
    # Add additional testing capabilities to the actor
    if hasattr(actor, 'objctrl'):
        # Ensure the actor has access to the mock OCIChar
        actor.objctrl = oci_char_fixture
        
        # Add testing helper methods
        def get_animation_count():
            return len(oci_char_fixture.animation_history)
        
        def get_last_animation():
            if oci_char_fixture.animation_history:
                return oci_char_fixture.animation_history[-1]
            return None
        
        def reset_for_test():
            oci_char_fixture.reset_for_test()
        
        # Bind helper methods to actor
        actor.get_animation_count = get_animation_count
        actor.get_last_animation = get_last_animation
        actor.reset_for_test = reset_for_test
    
    return actor


def create_multiple_actor_fixtures(entity_ids=None, include_male=True):
    """
    Create multiple actor fixtures for testing multi-character scenarios.
    """
    if entity_ids is None:
        entity_ids = ['kaji', 'user', 'character_3']
    
    actors = {}
    
    for i, entity_id in enumerate(entity_ids):
        # Alternate between male and female, or use specific patterns
        if entity_id == 'user' and include_male:
            sex = 0  # Male user
        else:
            sex = 1  # Female characters
        
        # Position characters in a line for testing
        position = (i * 2.0, 0.0, 0.0)
        
        actors[entity_id] = create_actor_fixture(entity_id, sex, position)
    
    return actors


def create_actor_with_animation_history(entity_id="test_actor", animation_sequence=None):
    """
    Create an actor fixture with pre-populated animation history for testing.
    """
    actor = create_actor_fixture(entity_id)
    
    if animation_sequence is None:
        animation_sequence = [
            {'action': 'idle', 'group': 0, 'category': 0, 'no': 0},
            {'action': 'walk', 'group': 0, 'category': 1, 'no': 0},
            {'action': 'wave', 'group': 1, 'category': 0, 'no': 0}
        ]
    
    # Simulate animation execution history
    for i, anim in enumerate(animation_sequence):
        if hasattr(actor, 'objctrl'):
            actor.objctrl.LoadAnime(
                anim['group'], 
                anim['category'], 
                anim['no'], 
                0.0  # normalized_time
            )
        
        # Add delay between animations for realistic timing
        time.sleep(0.01)
    
    return actor


def create_actor_with_custom_state(entity_id="custom_actor", **state_overrides):
    """
    Create an actor fixture with custom state values for specific testing scenarios.
    
    Args:
        entity_id: Actor identifier
        **state_overrides: Dictionary of state values to override
            Examples:
            - position=(1.0, 0.0, 2.0)
            - rotation=(0.0, 90.0, 0.0)
            - clothing_state=[1, 1, 0, 0, 0, 0, 0, 0]  # Partially clothed
            - animation_speed=2.0
            - eyes_open=0.5
            - mouth_open=0.3
    """
    actor = create_actor_fixture(entity_id)
    
    if hasattr(actor, 'objctrl'):
        oci_char = actor.objctrl
        
        # Apply position override
        if 'position' in state_overrides:
            pos = state_overrides['position']
            oci_char.charInfo.transform.position = MockVector3(pos[0], pos[1], pos[2])
            oci_char.oiCharInfo.changeAmount.pos = MockVector3(pos[0], pos[1], pos[2])
        
        # Apply rotation override
        if 'rotation' in state_overrides:
            rot = state_overrides['rotation']
            oci_char.oiCharInfo.changeAmount.rot = MockVector3(rot[0], rot[1], rot[2])
        
        # Apply clothing state override
        if 'clothing_state' in state_overrides:
            oci_char.charFileStatus.clothesState = state_overrides['clothing_state']
        
        # Apply animation speed override
        if 'animation_speed' in state_overrides:
            oci_char.oiCharInfo.animeSpeed = state_overrides['animation_speed']
        
        # Apply facial expression overrides
        if 'eyes_open' in state_overrides:
            oci_char.charFileStatus.eyesOpenMax = state_overrides['eyes_open']
        
        if 'mouth_open' in state_overrides:
            oci_char.oiCharInfo.mouthOpen = state_overrides['mouth_open']
        
        # Apply IK/FK overrides
        if 'enable_ik' in state_overrides:
            oci_char.oiCharInfo.enableIK = state_overrides['enable_ik']
        
        if 'enable_fk' in state_overrides:
            oci_char.oiCharInfo.enableFK = state_overrides['enable_fk']
        
        # Apply body shape overrides
        if 'body_shapes' in state_overrides:
            oci_char.charInfo.chaFile.custom.body.shapeValueBody = state_overrides['body_shapes']
        
        if 'face_shapes' in state_overrides:
            oci_char.charInfo.chaFile.custom.face.shapeValueFace = state_overrides['face_shapes']
    
    return actor
