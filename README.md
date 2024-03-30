# Trial Blender Addons
This is a repository that contains addons for Blender specifically for creating models and levels for use with the [Trial engine](https://shirakumo.org/projects/trial).

## Installation
First you will need the [glTF Physics Exporter](https://github.com/eoineoineoin/glTF_Physics_Blender_Exporter) plugin, as Trial depends on its capabilities for physics.

Then you can [download the latest release](https://github.com/Shirakumo/trial-blender-addons/releases/latest/download/SHIRAKUMO_trial_extensions.zip) of our plugin directly here from GitHub. The zip files can be imported into Blender just like any other addon.

Activating the plugin should give you a new menu entry under ``Add`` to create trigger volumes, as well as new action properties specific to Trial. Finally, it hooks into the glTF2 plugin to properly export and import the extra data.

## JSON Schema
The export/import defines the ``SHIRAKUMO_trial`` extension block, which can contain different fields depending on the type of node it is attached to.

On rig nodes the fields are:

- ``cancelable``
- ``invincible``
- ``targetDamage``
- ``stunTarget``
- ``knockTarget``
- ``lockTarget``
- ``lockCamera``

On object nodes set as triggers the fields are:

- ``form``
- ``spawn``
- ``spawnCount``
- ``autoDeactivate``
- ``respawnCooldown``
- ``kill``

On animations the fields are:

- ``rootMotion``
- ``velocityScale``
- ``loop``
- ``next``

On scenes the fields are:

- ``envmap``
- ``envmapOrientation``
- ``envmapColor``

