
import bpy
import math

bpy.ops.wm.read_homefile(use_empty=True)

# Test creating an articulated actor
root = bpy.data.objects.new('Actor_Root', None)
bpy.context.scene.collection.objects.link(root)

# Legs
bpy.ops.mesh.primitive_cylinder_add(radius=0.075, depth=0.88, location=(0, 0, 0.44))
legs = bpy.context.active_object
legs.parent = root

# Torso pivot at hip (0, 0, 0.88)
bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.62, location=(0, 0, 1.19))
torso = bpy.context.active_object
torso.parent = root

# Change origin of torso to hip
bpy.context.scene.cursor.location = (0, 0, 0.88)
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

# Head attached to torso
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(0, 0, 1.68))
head = bpy.context.active_object
head.parent = torso

# Test bending torso forward
torso.rotation_euler = (math.radians(45), 0, 0)
print('Articulated setup test successful!')
