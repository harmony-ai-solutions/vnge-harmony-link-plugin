
# FIXME: Turn this into proper Dependency Injection

# Object, character & user controllers
user_controlled_entity_id = None
active_entities = {}
registered_props = {}

# List of ready characters - this is used to synchronize characters finished initialization
ready_entities = []
failed_entities = []

# static actors in the scene, which may be relevant for movement or interactions
static_actors = {}

def flush():
    # Flushes all global variables on Plugin init, to clean up any stale state from previous runs
    global user_controlled_entity_id, active_entities, registered_props
    global ready_entities, failed_entities
    global static_actors

    # Object, character & user controllers
    user_controlled_entity_id = None
    active_entities = {}
    registered_props = {}

    # List of ready characters - this is used to synchronize characters finished initialization
    ready_entities = []
    failed_entities = []

    # static actors in the scene, which may be relevant for movement or interactions
    static_actors = {}
