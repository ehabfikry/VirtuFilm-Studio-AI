
import bpy
import math

bpy.ops.wm.read_homefile(use_empty=True)

root = bpy.data.objects.new('Dog_Root', None)
bpy.context.scene.collection.objects.link(root)

# Dog body
bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=0.48, location=(0, 0, 0.28), rotation=(math.radians(90), 0, 0))
body = bpy.context.active_object
body.parent = root

# Dog head
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(0, -0.26, 0.38))
head = bpy.context.active_object
head.parent = root

# Dog snout / muzzle
bpy.ops.mesh.primitive_cone_add(radius1=0.05, depth=0.12, location=(0, -0.34, 0.36), rotation=(math.radians(90), 0, 0))
muzzle = bpy.context.active_object
muzzle.parent = root

# 4 Legs
for lx in (-0.08, 0.08):
    for ly in (-0.16, 0.16):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.22, location=(lx, ly, 0.11))
        leg = bpy.context.active_object
        leg.parent = root

# Tail
bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.22, location=(0, 0.22, 0.38), rotation=(math.radians(-35), 0, 0))
tail = bpy.context.active_object
tail.parent = root

print('Dog proxy created successfully with', len(root.children), 'parts!')
