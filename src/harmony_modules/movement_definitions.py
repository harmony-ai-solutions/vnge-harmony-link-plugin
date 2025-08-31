
# Action Categories - centralized constants for action classification
class ActionCategories:
    MOVEMENT = 'movement'
    POSTURE_SITTING = 'posture_sitting'
    POSTURE_STANDING = 'posture_standing'
    POSTURE_LAYING = 'posture_laying'
    SIMPLE_ACTION = 'simple_action'
    OBJECT_INTERACTION = 'object_interaction'
    CHARACTER_INTERACTION = 'character_interaction'


class CompletionTypes:
    DISTANCE = "distance"  # Movement actions - complete when distance threshold reached
    STATE = "state"        # Posture actions - complete when state achieved
    DURATION = "duration"  # Simple actions - complete after fixed duration


# Helper function to get actions as a dictionary for easy retrieval
def get_actions_dict():
    """
    Returns registered_actions as a dictionary with action name as key
    
    Returns:
        dict: Dictionary mapping action names to action definitions
    """
    return {action['name']: action for action in registered_actions}


def get_action_by_name(action_name):
    """
    Get a specific action definition by name
    
    Args:
        action_name (str): Name of the action to retrieve
        
    Returns:
        dict: Action definition or None if not found
    """
    actions_dict = get_actions_dict()
    return actions_dict.get(action_name)

# Dummy placeholder until refactor done
registered_actions = []