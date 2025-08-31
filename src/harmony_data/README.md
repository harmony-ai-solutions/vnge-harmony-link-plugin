# VNGE Plugin Data Definitions

This folder contains data definitions used by some of the modules of the VNGE Plugin.

! Attention: When modifying these files, make sure to validate the JSON schema. If the schema isn't valid the VNGE Plugin
will encounter issues when loading the files

## Action Definitions
File: `actions.json`

This file contains action definitions and roleplay examples for the specified action.
The VNGE Plugin will only execute actions defined in this list.

An action definition looks like this:

```python
example_action = {
    "name": "got_pushed_away", # unique name identifier of the action
    "description": "got pushed away by the other chara", # description of the action; so the intention to be captured is clear
    "category": "character_interaction", # category of the action; defines how the action will be evaluated on plugin side
    "duration": 1.0, # default duration for this action
    # examples define roleplay actions which may trigger this action. Used for RAG matching
    "examples": [
        "{{character}} falls backwards",
        "{{character}} loses balance and topples over",
        "{{character}} steps back surprisedly",
        "{{character}} recoils from the sudden movement",
        "{{character}} takes a step back from {{other_character}}"
    ],
    # trigger_conditions reference other action names which are required to trigger this. may be empty
    # a trigger condition can either be a character's own action, or an action executed by another character 
    "trigger_conditions": [
        "push_away"
    ],
    # animations reference valid ingame animations which may play while this action is being executed
    # if empty, idle animations may play
    "animations": [
        {}
    ]
}
```


## List of available ingame Animations
File: `animation_list.json`
Sample: `animation_list.sample.json`

This file contains animations detected from ingame assets.
These Actions have no proper description, so they need to be manually or dynamically mapped to action definitions.

These animations have been loaded from Koikatsu Sunshine and may contain different names for actions than other Illusion
games, as well as animations from mod files. We'll look into providing individual lists for all supported games in the future.

A new animation list for your game can be generated when starting the plugin with `debug_mode = 2` set in `harmony.ini`.

