# Trial Blender Addons
This is a repository that contains addons for Blender specifically for creating models and levels for use with the [Trial engine](https://shirakumo.org/projects/trial).

## Installation
First you will need the [glTF Physics Exporter](https://github.com/eoineoineoin/glTF_Physics_Blender_Exporter) plugin, as Trial depends on its capabilities for physics.

Then you can [download the latest release](https://github.com/Shirakumo/trial-blender-addons/releases/latest/download/SHIRAKUMO_trial_extensions.zip) of our plugin directly here from GitHub. The zip files can be imported into Blender just like any other addon.

Activating the plugin should give you a new menu entry under ``Add`` to create trigger volumes, as well as new action properties specific to Trial. Finally, it hooks into the glTF2 plugin to properly export and import the extra data.

## JSON Schema
The export/import defines the ``SHIRAKUMO_trial`` extension block, which can contain different fields depending on the type of node it is attached to.

On rig nodes the fields are:

- ``cancelable`` (animated) Whether the animation can be cancelled
- ``invincible`` (animated) Whether the character is invincible
- ``targetDamage`` (animated) How much damage to deal to the target
- ``stunTarget`` (animated) How much stun time to add to the target
- ``knockTarget`` (animated) Whether the target should receive knockback
- ``lockTarget`` (animated) Whether the attack target should be locked into the place and orientation of the object named ``target``
- ``lockCamera`` (animated) Whether the camera should be locked into the place and orientation of the object named ``camera``

On object nodes set as triggers the fields are:

- ``form`` The Lisp expression to evaluate
- ``spawn`` The object to spawn. Can either be:
  - The name of another object in the scene
  - A Lisp expression designating a list of the object class and the initialisation arguments
- ``spawnCount`` The number of objects to spawn
- ``autoDeactivate`` Whether the trigger should deactivate after all spawned objects were removed
- ``respawnCooldown`` How much time to wait to respawn a removed object
- ``kill`` A Lisp type expression to match which objects to remove when entering the trigger volume

On animations the fields are:

- ``rootMotion`` Whether the animation should use inferred physical root motion
- ``velocityScale`` How much to scale the physical root motion by
- ``loop`` Whether the animation should loop or not
- ``next`` The name of the animation to queue after this one

On scenes the fields are:

- ``envmap`` The path to the hdr environment map file
- ``envmapOrientation`` A 3-component vector designating the orientation of the environment map
- ``envmapColor`` A 3-component color multiplier of the environment map

