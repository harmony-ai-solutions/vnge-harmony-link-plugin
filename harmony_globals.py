
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
