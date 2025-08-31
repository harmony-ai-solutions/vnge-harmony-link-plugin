# VNGE Plugin Data Definitions

This folder contains data definitions used by some of the modules of the VNGE Plugin.

! Attention: When modifying these files, make sure to validate the JSON schema. If the schema isn't valid the VNGE Plugin
will encounter issues when loading the files

## Action Definitions
File: `actions.json`

This file contains action definitions and roleplay examples for the specified action.
The VNGE Plugin will only execute actions defined in this list.


## List of available ingame Animations
File: `animation_list.json`
Sample: `animation_list.sample.json`

This file contains animations detected from ingame assets.
These Actions have no proper description, so they need to be manually or dynamically mapped to action definitions.

These animations have been loaded from Koikatsu Sunshine and may contain different names for actions than other Illusion
games, as well as animations from mod files. We'll look into providing individual lists for all supported games in the future.

A new animation list for your game can be generated when starting the plugin with `debug_mode = 2` set in `harmony.ini`.

