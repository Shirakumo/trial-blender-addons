# Trial Blender Addons
This is a repository that contains addons for Blender specifically for creating models and levels for use with the [Trial engine](https://shirakumo.org/projects/trial).

## Installation
Then you can [download the latest release](https://github.com/Shirakumo/trial-blender-addons/releases/latest/) of our plugin and the dependent ``KHR_physics_rigid_bodies`` directly here from GitHub. The zip files can be imported into Blender just like any other addon.

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

On object nodes set as physics objects the fields are:

- ``virtual`` If true the object should not be rendered but still participate in collisions
- ``trigger``
  - ``form`` The Lisp expression to evaluate
- ``spawner``
  - ``spawn`` The object to spawn. Can either be:
    - The name of another object in the scene
    - A Lisp expression designating a list of the object class and the initialisation arguments
  - ``spawnCount`` The number of objects to spawn
  - ``autoDeactivate`` Whether the trigger should deactivate after all spawned objects were removed
  - ``respawnCooldown`` How much time to wait to respawn a removed object
- ``killvolume``
  - ``kill`` A Lisp type expression to match which objects to remove when entering the trigger volume
- ``checkpoint``
  - ``spawnPoint`` The location at which to respawn after triggering the checkpoint
- ``progressionTrigger``
  - ``state`` The state to update. If unset defaults to ``progression``
  - ``value`` The value to update it with. If unset defaults to ``1``
  - ``mode`` The mode to determine how to update the state. If unset defaults to ``INC``. Can be one of:
    - ``INC`` The new value is the ``value`` added to the current state value
    - ``DEC`` The new value is the ``value`` subtracted from the current state value
    - ``SET`` The new value is the ``value``
  - ``condition`` The condition that must be true for the state update to happen. If unset defaults to ``T``. Should be a Lisp expression that evaluates to a boolean.
- ``cameraTrigger``
  - ``state`` What state the camera should be in once hitting this trigger. Can be one of:
    - ``FREE`` The camera can be freely moved by the player
    - ``FIXED`` The camera is in a fixed offset to its target
    - ``ANIMATED`` The camera follows the path and orientation encoded in the animation named by ``target``
  - ``target`` The name of the object to target. If unset, don't change the target.
  - ``offset`` The offset of the camera to the target as a triplet of coordinates:
    1. ``DISTANCE`` The distance between the camera and the target
    2. ``ANGLE`` The angle on the world XZ plane that the camera is at
    3. ``HEIGHT`` The angle of the camera on the Y quadrant above the XZ plane

On animations the fields are:

- ``type`` 
  - ``DEFAULT`` Default animation that is just played back with no engine assistance.
  - ``BLOCKING`` A blocking animation that has a ``cancelable`` property.
  - ``PHYSICAL`` A physical root-motion animation.
- ``velocityScale`` How much to scale the physical root motion by
- ``loop`` Whether the animation should loop or not
- ``next`` The name of the animation to queue after this one
- ``blendDuration`` The default duration (in seconds) to use when blending to this animation

On scenes the fields are:

- ``envmap`` The path to the hdr environment map file
- ``envmapOrientation`` A 3-component vector designating the orientation of the environment map
- ``envmapColor`` A 3-component color multiplier of the environment map

