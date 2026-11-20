# ==============================================================================
# PROPRIETARY INTELLECTUAL PROPERTY & TRADE SECRET NOTICE
# System: VirtuFilm Studio AI (Cindy AI Director Architecture v8.0)
# Inventor & Owner: Ehab Fikry (المخرج / إيهاب فكري)
# Patent Reference: CAD-IP-2026-001
# Legal Protection:
#   1. WIPO Berne Convention (Automatic International Copyright in 181 Countries)
#   2. Egyptian Intellectual Property Law No. 82 of 2002 (ITIDA Software Deposit)
#   3. Trade Secret & Cryptographic SHA-256 Prior-Art Ledger
# Unauthorized copying, reverse engineering, or redistribution is strictly prohibited.
# ==============================================================================

# -*- coding: utf-8 -*-
"""
Cindy AI Director — Universal Parametric 3D Pre-vis Engine (cindy_previs_engine.py)
Version 8.0: True Polar/Spherical Orbit & Crane Solver, Pose-Aware Eye/Chest Tracking,
Wall-Collision Ray Guard, Walk-Cycle Stride Oscillator, and Rich Architectural Environments
(Bedroom with Window & Bed, Space-to-Window Dive, Street, Room, Alley).
"""

import bpy
import sys
import os
import json
import math
import time
import shutil
from mathutils import Vector, Euler

OUTPUT_DIR = r"C:\Users\DELL\Desktop\Cindy-AI-Director\outputs\blender_guides"
SCENES_DIR = r"D:\Blender\scenes"
SPEC_FILE = os.path.join(OUTPUT_DIR, "current_previs_spec.json")
REPO_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else r"C:\Users\DELL\Desktop\Cindy-AI-Director"
if REPO_DIR not in sys.path:
    sys.path.insert(0, REPO_DIR)

DEFAULT_SPEC = {
    "title": "مشهد المواجهة في الغرفة (Room Confrontation)",
    "environment": {
        "type": "room",
        "has_door": True,
        "has_desk": True,
        "door_crack_sec": 1.9,
        "door_open_sec": 2.7
    },
    "duration_sec": 8.0,
    "fps": 24,
    "actors": [
        {
            "id": "actor_1",
            "name": "Actor_1_Lead",
            "color": [0.95, 0.55, 0.15],
            "height_m": 1.84,
            "start_pos": [0.0, 1.2, 0.0],
            "start_look_at": [0.0, -2.0, 1.5],
            "keyframes": [
                {"time_sec": 0.0, "pos": [0.0, 1.2, 0.0], "look_at": [0.0, -2.0, 1.5], "pose": "STAND"},
                {"time_sec": 2.0, "pos": [0.0, 1.2, 0.0], "look_at": [0.0, -2.0, 1.5], "pose": "STAND"},
                {"time_sec": 2.7, "pos": [0.0, 1.2, 0.0], "look_at": [-3.0, 1.25, 1.6], "pose": "STAND"},
                {"time_sec": 5.0, "pos": [0.0, 1.2, 0.0], "look_at": [-0.85, 1.2, 1.68], "pose": "STAND"},
                {"time_sec": 8.0, "pos": [0.0, 1.2, 0.0], "look_at": [-0.85, 1.2, 1.68], "pose": "STAND"}
            ]
        },
        {
            "id": "actor_2",
            "name": "Actor_2_Entrant",
            "color": [0.15, 0.68, 0.95],
            "height_m": 1.86,
            "start_pos": [-3.6, 1.25, 0.0],
            "start_look_at": [0.0, 1.2, 1.68],
            "keyframes": [
                {"time_sec": 0.0, "pos": [-3.6, 1.25, 0.0], "look_at": [0.0, 1.2, 1.68], "pose": "WALK"},
                {"time_sec": 2.0, "pos": [-3.4, 1.25, 0.0], "look_at": [0.0, 1.2, 1.68], "pose": "WALK"},
                {"time_sec": 2.8, "pos": [-2.5, 1.22, 0.0], "look_at": [0.0, 1.2, 1.68], "pose": "WALK"},
                {"time_sec": 5.5, "pos": [-0.85, 1.2, 0.0], "look_at": [0.0, 1.2, 1.68], "pose": "STAND"},
                {"time_sec": 8.0, "pos": [-0.85, 1.2, 0.0], "look_at": [0.0, 1.2, 1.68], "pose": "STAND"}
            ]
        }
    ],
    "props": [],
    "camera_beats": [
        {
            "time_sec": 0.0,
            "name": "Beat 1A: High Angle on Actor 1",
            "framing": "HIGH_ANGLE_ON_ACTOR",
            "target": "actor_1",
            "lens_mm": 40.0,
            "transition": "SMOOTH"
        },
        {
            "time_sec": 2.0,
            "name": "Beat 1B: Crane Down to Face",
            "framing": "FACE_CLOSE_UP",
            "target": "actor_1",
            "lens_mm": 50.0,
            "transition": "SMOOTH"
        },
        {
            "time_sec": 2.7,
            "name": "Beat 2: Whip Pan to Doorway",
            "framing": "DOOR_ENTRANCE",
            "target": "actor_2",
            "lens_mm": 32.0,
            "transition": "WHIP"
        },
        {
            "time_sec": 3.5,
            "name": "Beat 3: Medium Two Following Entrance",
            "framing": "MEDIUM_TWO",
            "lens_mm": 35.0,
            "transition": "SMOOTH"
        },
        {
            "time_sec": 5.8,
            "name": "Beat 4: Tight Climax Medium Two Standoff",
            "framing": "TIGHT_MEDIUM_TWO",
            "lens_mm": 45.0,
            "transition": "SMOOTH"
        }
    ]
}


def build_rigged_human_actor(name, color_rgb, height_m=1.80):
    """
    Builds a unified rigged humanoid mannequin using an Armature and vertex groups.
    Includes a glowing smartphone prop in the right hand when seated/texting or standing.
    """
    scale_f = height_m / 1.80

    bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
    arm_obj = bpy.context.active_object
    arm_obj.name = name
    arm = arm_obj.data
    arm.name = f"{name}_ArmatureData"

    bpy.ops.armature.select_all(action='SELECT')
    bpy.ops.armature.delete()

    b_root = arm.edit_bones.new("Root")
    b_root.head = (0.0, 0.0, 0.0)
    b_root.tail = (0.0, 0.0, 0.2 * scale_f)

    b_pelvis = arm.edit_bones.new("Pelvis")
    b_pelvis.head = (0.0, 0.0, 0.88 * scale_f)
    b_pelvis.tail = (0.0, 0.0, 1.05 * scale_f)
    b_pelvis.parent = b_root

    b_spine = arm.edit_bones.new("Spine")
    b_spine.head = (0.0, 0.0, 1.05 * scale_f)
    b_spine.tail = (0.0, 0.0, 1.48 * scale_f)
    b_spine.parent = b_pelvis

    b_head = arm.edit_bones.new("Head")
    b_head.head = (0.0, 0.0, 1.48 * scale_f)
    b_head.tail = (0.0, 0.0, 1.80 * scale_f)
    b_head.parent = b_spine

    b_thigh_l = arm.edit_bones.new("Thigh_L")
    b_thigh_l.head = (-0.11 * scale_f, 0.0, 0.88 * scale_f)
    b_thigh_l.tail = (-0.11 * scale_f, 0.0, 0.44 * scale_f)
    b_thigh_l.parent = b_pelvis

    b_shin_l = arm.edit_bones.new("Shin_L")
    b_shin_l.head = (-0.11 * scale_f, 0.0, 0.44 * scale_f)
    b_shin_l.tail = (-0.11 * scale_f, 0.0, 0.0)
    b_shin_l.parent = b_thigh_l

    b_thigh_r = arm.edit_bones.new("Thigh_R")
    b_thigh_r.head = (0.11 * scale_f, 0.0, 0.88 * scale_f)
    b_thigh_r.tail = (0.11 * scale_f, 0.0, 0.44 * scale_f)
    b_thigh_r.parent = b_pelvis

    b_shin_r = arm.edit_bones.new("Shin_R")
    b_shin_r.head = (0.11 * scale_f, 0.0, 0.44 * scale_f)
    b_shin_r.tail = (0.11 * scale_f, 0.0, 0.0)
    b_shin_r.parent = b_thigh_r

    b_arm_l = arm.edit_bones.new("Arm_L")
    b_arm_l.head = (-0.24 * scale_f, 0.0, 1.42 * scale_f)
    b_arm_l.tail = (-0.24 * scale_f, 0.0, 0.88 * scale_f)
    b_arm_l.parent = b_spine

    b_arm_r = arm.edit_bones.new("Arm_R")
    b_arm_r.head = (0.24 * scale_f, 0.0, 1.42 * scale_f)
    b_arm_r.tail = (0.24 * scale_f, 0.0, 0.88 * scale_f)
    b_arm_r.parent = b_spine

    bpy.ops.object.mode_set(mode='OBJECT')

    mat_body = bpy.data.materials.new(f"Mat_{name}")
    mat_body.diffuse_color = (color_rgb[0], color_rgb[1], color_rgb[2], 1.0)

    parts = []

    bpy.ops.mesh.primitive_cylinder_add(radius=0.18 * scale_f, depth=0.18 * scale_f, location=(0.0, 0.0, 0.96 * scale_f))
    p_pelvis = bpy.context.active_object
    vg = p_pelvis.vertex_groups.new(name="Pelvis")
    vg.add(list(range(len(p_pelvis.data.vertices))), 1.0, 'REPLACE')
    parts.append(p_pelvis)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.20 * scale_f, depth=0.46 * scale_f, location=(0.0, 0.0, 1.25 * scale_f))
    p_torso = bpy.context.active_object
    vg = p_torso.vertex_groups.new(name="Spine")
    vg.add(list(range(len(p_torso.data.vertices))), 1.0, 'REPLACE')
    parts.append(p_torso)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.075 * scale_f, depth=0.48 * scale_f, location=(0.0, 0.0, 1.41 * scale_f), rotation=(0.0, math.radians(90), 0.0))
    p_sh = bpy.context.active_object
    vg = p_sh.vertex_groups.new(name="Spine")
    vg.add(list(range(len(p_sh.data.vertices))), 1.0, 'REPLACE')
    parts.append(p_sh)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.125 * scale_f, location=(0.0, 0.0, 1.66 * scale_f))
    p_head = bpy.context.active_object
    p_head.scale = (0.92, 1.0, 1.12)
    bpy.ops.object.transform_apply(scale=True)
    vg = p_head.vertex_groups.new(name="Head")
    vg.add(list(range(len(p_head.data.vertices))), 1.0, 'REPLACE')
    parts.append(p_head)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -0.105 * scale_f, 1.685 * scale_f))
    p_visor = bpy.context.active_object
    p_visor.scale = (0.16 * scale_f, 0.05 * scale_f, 0.038 * scale_f)
    bpy.ops.object.transform_apply(scale=True)
    mat_visor = bpy.data.materials.new(f"Mat_{name}_Visor")
    mat_visor.diffuse_color = (0.06, 0.06, 0.08, 1.0)
    p_visor.data.materials.append(mat_visor)
    vg = p_visor.vertex_groups.new(name="Head")
    vg.add(list(range(len(p_visor.data.vertices))), 1.0, 'REPLACE')
    parts.append(p_visor)

    for side, bone_thigh, bone_shin, lx in (('L', 'Thigh_L', 'Shin_L', -0.11 * scale_f), ('R', 'Thigh_R', 'Shin_R', 0.11 * scale_f)):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.075 * scale_f, depth=0.42 * scale_f, location=(lx, 0.0, 0.66 * scale_f))
        p_thigh = bpy.context.active_object
        vg = p_thigh.vertex_groups.new(name=bone_thigh)
        vg.add(list(range(len(p_thigh.data.vertices))), 1.0, 'REPLACE')
        parts.append(p_thigh)

        bpy.ops.mesh.primitive_cylinder_add(radius=0.065 * scale_f, depth=0.42 * scale_f, location=(lx, 0.0, 0.22 * scale_f))
        p_shin = bpy.context.active_object
        vg = p_shin.vertex_groups.new(name=bone_shin)
        vg.add(list(range(len(p_shin.data.vertices))), 1.0, 'REPLACE')
        parts.append(p_shin)

    for side, bone_arm, ax in (('L', 'Arm_L', -0.24 * scale_f), ('R', 'Arm_R', 0.24 * scale_f)):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.052 * scale_f, depth=0.54 * scale_f, location=(ax, 0.0, 1.15 * scale_f))
        p_arm = bpy.context.active_object
        vg = p_arm.vertex_groups.new(name=bone_arm)
        vg.add(list(range(len(p_arm.data.vertices))), 1.0, 'REPLACE')
        parts.append(p_arm)

    for p in parts:
        if p != p_visor:
            p.data.materials.append(mat_body)

    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = p_torso
    bpy.ops.object.join()
    body_mesh = bpy.context.active_object
    body_mesh.name = f"{name}_Body"

    mod = body_mesh.modifiers.new("ArmatureMod", 'ARMATURE')
    mod.object = arm_obj
    body_mesh.parent = arm_obj

    for pb in arm_obj.pose.bones:
        pb.rotation_mode = 'XYZ'

    arm_obj["height_m"] = height_m
    arm_obj["scale_f"] = scale_f
    arm_obj["current_pose"] = "STAND"
    return arm_obj


def apply_rigged_pose(arm_obj, pose_name, scale_f=1.0, walk_phase=0.0):
    """
    Applies anatomical keyframe poses on the skeleton bones.
    Supports WALK with dynamic stride phase, SIT, SIT_PHONE, KNEEL, CROUCH, STAND.
    """
    pose = (pose_name or "STAND").upper()
    arm_obj["current_pose"] = pose
    pb = arm_obj.pose.bones

    for b_name in ["Pelvis", "Spine", "Head", "Thigh_L", "Shin_L", "Thigh_R", "Shin_R", "Arm_L", "Arm_R"]:
        if b_name in pb:
            pb[b_name].location = (0.0, 0.0, 0.0)
            pb[b_name].rotation_euler = (0.0, 0.0, 0.0)

    if pose == "KNEEL":
        pb["Pelvis"].location = Vector((0.0, -0.10 * scale_f, -0.44 * scale_f))
        pb["Spine"].rotation_euler = Euler((math.radians(24), 0.0, 0.0), 'XYZ')
        pb["Head"].rotation_euler = Euler((math.radians(10), 0.0, 0.0), 'XYZ')
        pb["Thigh_L"].rotation_euler = Euler((math.radians(40), 0.0, 0.0), 'XYZ')
        pb["Shin_L"].rotation_euler = Euler((math.radians(-85), 0.0, 0.0), 'XYZ')
        pb["Thigh_R"].rotation_euler = Euler((math.radians(80), 0.0, 0.0), 'XYZ')
        pb["Shin_R"].rotation_euler = Euler((math.radians(-80), 0.0, 0.0), 'XYZ')
        pb["Arm_L"].rotation_euler = Euler((math.radians(35), 0.0, 0.0), 'XYZ')
        pb["Arm_R"].rotation_euler = Euler((math.radians(35), 0.0, 0.0), 'XYZ')

    elif pose == "CROUCH":
        pb["Pelvis"].location = Vector((0.0, -0.12 * scale_f, -0.52 * scale_f))
        pb["Spine"].rotation_euler = Euler((math.radians(32), 0.0, 0.0), 'XYZ')
        pb["Thigh_L"].rotation_euler = Euler((math.radians(75), 0.0, 0.0), 'XYZ')
        pb["Shin_L"].rotation_euler = Euler((math.radians(-85), 0.0, 0.0), 'XYZ')
        pb["Thigh_R"].rotation_euler = Euler((math.radians(75), 0.0, 0.0), 'XYZ')
        pb["Shin_R"].rotation_euler = Euler((math.radians(-85), 0.0, 0.0), 'XYZ')

    elif pose == "WALK":
        s = math.sin(walk_phase)
        bob = abs(math.cos(walk_phase)) * 0.03 * scale_f
        pb["Pelvis"].location = Vector((0.0, 0.0, -bob))
        pb["Spine"].rotation_euler = Euler((math.radians(5), 0.0, math.radians(s * 4)), 'XYZ')
        pb["Thigh_L"].rotation_euler = Euler((math.radians(26 * s), 0.0, 0.0), 'XYZ')
        pb["Shin_L"].rotation_euler = Euler((math.radians(-max(0.0, -s) * 32 - 6), 0.0, 0.0), 'XYZ')
        pb["Thigh_R"].rotation_euler = Euler((math.radians(-26 * s), 0.0, 0.0), 'XYZ')
        pb["Shin_R"].rotation_euler = Euler((math.radians(-max(0.0, s) * 32 - 6), 0.0, 0.0), 'XYZ')
        pb["Arm_L"].rotation_euler = Euler((math.radians(-20 * s), 0.0, 0.0), 'XYZ')
        pb["Arm_R"].rotation_euler = Euler((math.radians(20 * s), 0.0, 0.0), 'XYZ')

    elif "SIT" in pose:
        pb["Pelvis"].location = Vector((0.0, 0.0, -0.42 * scale_f))
        pb["Spine"].rotation_euler = Euler((math.radians(8), 0.0, 0.0), 'XYZ')
        pb["Head"].rotation_euler = Euler((math.radians(14), 0.0, 0.0), 'XYZ')
        pb["Thigh_L"].rotation_euler = Euler((math.radians(88), 0.0, math.radians(-5)), 'XYZ')
        pb["Shin_L"].rotation_euler = Euler((math.radians(-88), 0.0, 0.0), 'XYZ')
        pb["Thigh_R"].rotation_euler = Euler((math.radians(88), 0.0, math.radians(5)), 'XYZ')
        pb["Shin_R"].rotation_euler = Euler((math.radians(-88), 0.0, 0.0), 'XYZ')
        # Hands raised holding phone/book naturally in lap/chest level
        pb["Arm_L"].rotation_euler = Euler((math.radians(48), 0.0, math.radians(15)), 'XYZ')
        pb["Arm_R"].rotation_euler = Euler((math.radians(52), 0.0, math.radians(-18)), 'XYZ')

    else:  # STAND
        pb["Pelvis"].location = Vector((0.0, 0.0, 0.0))


def get_actor_anatomical_targets(actor_obj):
    """
    Uses Blender's evaluated world matrix on the actual Head and Spine pose bones!
    Guarantees 100% anatomical precision for eye_pos and chest_pos regardless of pose (STAND, SIT, KNEEL, CROUCH).
    """
    if not actor_obj:
        return Vector((0.0, 1.2, 1.62)), Vector((0.0, 1.2, 1.32)), 0.0

    yaw = actor_obj.rotation_euler.z
    if hasattr(actor_obj, "pose") and actor_obj.pose and "Head" in actor_obj.pose.bones and "Spine" in actor_obj.pose.bones:
        pb_head = actor_obj.pose.bones["Head"]
        pb_spine = actor_obj.pose.bones["Spine"]
        # Center of Head sphere (with Gaze Visor) is 58% along the Head bone
        head_world = actor_obj.matrix_world @ pb_head.head.lerp(pb_head.tail, 0.58)
        chest_world = actor_obj.matrix_world @ pb_spine.head.lerp(pb_spine.tail, 0.55)
        return head_world, chest_world, yaw

    p = actor_obj.location.copy()
    h = float(actor_obj.get("height_m", 1.80))
    return Vector((p.x, p.y, p.z + h * 0.91)), Vector((p.x, p.y, p.z + h * 0.72)), yaw


def build_prop(prop_spec):
    p_type = (prop_spec.get("type") or "dog").lower()
    p_name = prop_spec.get("name") or f"Prop_{p_type}"
    pos = Vector(prop_spec.get("pos") or [0.0, 0.0, 0.0])
    color = prop_spec.get("color") or [0.45, 0.28, 0.15]
    scale = float(prop_spec.get("scale") or 1.0)
    look = Vector(prop_spec.get("look_at") or [0.0, 1.0, 0.0])

    root = bpy.data.objects.new(p_name, None)
    bpy.context.scene.collection.objects.link(root)

    mat_prop = bpy.data.materials.new(f"Mat_{p_name}")
    mat_prop.diffuse_color = (color[0], color[1], color[2], 1.0)

    if "dog" in p_type or "cat" in p_type or "animal" in p_type:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.14 * scale, depth=0.48 * scale,
            location=(0.0, 0.0, 0.28 * scale),
            rotation=(math.radians(90), 0.0, 0.0)
        )
        body = bpy.context.active_object
        body.data.materials.append(mat_prop)
        body.parent = root

        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10 * scale, location=(0.0, -0.26 * scale, 0.38 * scale))
        head = bpy.context.active_object
        head.data.materials.append(mat_prop)
        head.parent = root

        bpy.ops.mesh.primitive_cone_add(
            radius1=0.05 * scale, depth=0.12 * scale,
            location=(0.0, -0.34 * scale, 0.36 * scale),
            rotation=(math.radians(90), 0.0, 0.0)
        )
        snout = bpy.context.active_object
        snout.data.materials.append(mat_prop)
        snout.parent = root

        for ex in (-0.06 * scale, 0.06 * scale):
            bpy.ops.mesh.primitive_cone_add(
                radius1=0.035 * scale, depth=0.09 * scale,
                location=(ex, -0.24 * scale, 0.48 * scale),
                rotation=(math.radians(-15), 0.0, 0.0)
            )
            ear = bpy.context.active_object
            ear.data.materials.append(mat_prop)
            ear.parent = root

        for lx in (-0.08 * scale, 0.08 * scale):
            for ly in (-0.16 * scale, 0.16 * scale):
                bpy.ops.mesh.primitive_cylinder_add(
                    radius=0.035 * scale, depth=0.22 * scale,
                    location=(lx, ly, 0.11 * scale)
                )
                leg = bpy.context.active_object
                leg.data.materials.append(mat_prop)
                leg.parent = root

        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.025 * scale, depth=0.22 * scale,
            location=(0.0, 0.22 * scale, 0.38 * scale),
            rotation=(math.radians(-35), 0.0, 0.0)
        )
        tail = bpy.context.active_object
        tail.data.materials.append(mat_prop)
        tail.parent = root

    elif "bed" in p_type:
        # Bedroom Bed with mattress, headboard, and pillow
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.28 * scale))
        mattress = bpy.context.active_object
        mattress.scale = (1.5 * scale, 2.0 * scale, 0.42 * scale)
        bpy.ops.object.transform_apply(scale=True)
        mat_bed = bpy.data.materials.new("Mat_BedSheet")
        mat_bed.diffuse_color = (0.18, 0.24, 0.38, 1.0)
        mattress.data.materials.append(mat_bed)
        mattress.parent = root

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.95 * scale, 0.68 * scale))
        hb = bpy.context.active_object
        hb.scale = (1.55 * scale, 0.12 * scale, 0.85 * scale)
        bpy.ops.object.transform_apply(scale=True)
        hb.data.materials.append(mat_prop)
        hb.parent = root

    elif "lamp" in p_type or "post" in p_type or "streetlamp" in p_type:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.06 * scale, depth=2.8 * scale, location=(0.0, 0.0, 1.4 * scale))
        pole = bpy.context.active_object
        mat_dark = bpy.data.materials.new("Mat_LampPost")
        mat_dark.diffuse_color = (0.08, 0.09, 0.10, 1.0)
        pole.data.materials.append(mat_dark)
        pole.parent = root

        bpy.ops.mesh.primitive_cone_add(radius1=0.22 * scale, depth=0.35 * scale, location=(0.0, 0.0, 2.85 * scale))
        lantern = bpy.context.active_object
        mat_glass = bpy.data.materials.new("Mat_LanternGlass")
        mat_glass.diffuse_color = (1.0, 0.88, 0.45, 1.0)
        lantern.data.materials.append(mat_glass)
        lantern.parent = root

        bpy.ops.object.light_add(type='POINT', radius=0.4, location=(pos.x, pos.y, (2.85 * scale)))
        l_lamp = bpy.context.active_object
        l_lamp.data.energy = 850
        l_lamp.data.color = (1.0, 0.85, 0.55)
        l_lamp.parent = root

    elif "car" in p_type or "vehicle" in p_type:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.65 * scale))
        car = bpy.context.active_object
        car.scale = (1.8 * scale, 4.2 * scale, 1.2 * scale)
        bpy.ops.object.transform_apply(scale=True)
        car.data.materials.append(mat_prop)
        car.parent = root

    elif "table" in p_type or "desk" in p_type:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.72 * scale))
        top = bpy.context.active_object
        top.scale = (1.3 * scale, 0.75 * scale, 0.06 * scale)
        bpy.ops.object.transform_apply(scale=True)
        top.data.materials.append(mat_prop)
        top.parent = root

    elif "chair" in p_type or "bench" in p_type:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.44 * scale))
        seat = bpy.context.active_object
        seat.scale = (0.52 * scale, 0.52 * scale, 0.08 * scale)
        bpy.ops.object.transform_apply(scale=True)
        seat.data.materials.append(mat_prop)
        seat.parent = root
    else:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.4 * scale))
        box = bpy.context.active_object
        box.scale = (0.6 * scale, 0.6 * scale, 0.6 * scale)
        bpy.ops.object.transform_apply(scale=True)
        box.data.materials.append(mat_prop)
        box.parent = root

    root.location = pos
    dx = look.x - pos.x
    dy = look.y - pos.y
    yaw = math.atan2(dx, -dy) if (abs(dx) > 1e-4 or abs(dy) > 1e-4) else 0.0
    root.rotation_euler = Euler((0.0, 0.0, yaw), 'XYZ')

    return root


def build_environment(scene, env_spec, fps, spec_title=""):
    env_type = (env_spec.get("type") or "room").lower()
    title_lower = (spec_title or "").lower()
    is_bedroom_or_window = ("bedroom" in env_type or "window" in env_type or "bedroom" in title_lower or "window" in title_lower or "earth" in title_lower)

    bpy.ops.mesh.primitive_plane_add(size=28.0, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Stage_Floor"
    mat_floor = bpy.data.materials.new("Mat_Floor")

    if "street" in env_type or "exterior" in env_type or "alley" in env_type:
        mat_floor.diffuse_color = (0.07, 0.08, 0.09, 1.0)
        floor.data.materials.append(mat_floor)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-2.2, 0.0, 0.1))
        pavement = bpy.context.active_object
        pavement.name = "Sidewalk_Kerb"
        pavement.scale = (1.8, 24.0, 0.2)
        bpy.ops.object.transform_apply(scale=True)
        mat_stone = bpy.data.materials.new("Mat_Pavement")
        mat_stone.diffuse_color = (0.16, 0.17, 0.18, 1.0)
        pavement.data.materials.append(mat_stone)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-4.2, 0.0, 2.5))
        bld = bpy.context.active_object
        bld.scale = (2.2, 24.0, 5.0)
        bpy.ops.object.transform_apply(scale=True)
        mat_bld = bpy.data.materials.new("Mat_Building")
        mat_bld.diffuse_color = (0.12, 0.13, 0.16, 1.0)
        bld.data.materials.append(mat_bld)

        bpy.ops.object.light_add(type='SPOT', radius=2.5, location=(-1.5, 0.0, 3.8))
        street_l = bpy.context.active_object
        street_l.data.energy = 1400
        street_l.data.spot_size = math.radians(80)
        street_l.data.color = (1.0, 0.88, 0.65)

        bpy.ops.object.light_add(type='AREA', radius=5.0, location=(3.0, -2.0, 4.0))
        ambient_l = bpy.context.active_object
        ambient_l.data.energy = 500
        ambient_l.data.color = (0.25, 0.40, 0.75)

    elif is_bedroom_or_window:
        # Bedroom stage with an open architectural window frame on the front (-Y) side so camera can dive straight through!
        mat_floor.diffuse_color = (0.10, 0.11, 0.14, 1.0)
        floor.data.materials.append(mat_floor)

        mat_wall = bpy.data.materials.new("Mat_BedroomWall")
        mat_wall.diffuse_color = (0.15, 0.17, 0.22, 1.0)

        # Back wall (+Y = 3.2)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 3.2, 1.6))
        wb = bpy.context.active_object
        wb.scale = (7.0, 0.18, 3.2)
        bpy.ops.object.transform_apply(scale=True)
        wb.data.materials.append(mat_wall)

        # Window frame on front wall (Y = -2.2) with large central glass opening so camera dives cleanly without wall collision!
        mat_frame = bpy.data.materials.new("Mat_WinFrame")
        mat_frame.diffuse_color = (0.22, 0.25, 0.32, 1.0)

        # Left & Right window pillars
        for wx in (-2.4, 2.4):
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(wx, -2.2, 1.6))
            wp = bpy.context.active_object
            wp.scale = (2.2, 0.18, 3.2)
            bpy.ops.object.transform_apply(scale=True)
            wp.data.materials.append(mat_wall)

        # Window sill (bottom) and header (top) leaving Y=-2.2 open from X=-1.3..+1.3, Z=0.75..2.55
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -2.2, 0.36))
        sill = bpy.context.active_object
        sill.scale = (2.6, 0.22, 0.72)
        bpy.ops.object.transform_apply(scale=True)
        sill.data.materials.append(mat_frame)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -2.2, 2.88))
        header = bpy.context.active_object
        header.scale = (2.6, 0.22, 0.64)
        bpy.ops.object.transform_apply(scale=True)
        header.data.materials.append(mat_frame)

        # Bed placed under actor if not already in props
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.65, 0.22))
        bed = bpy.context.active_object
        bed.name = "Bedroom_Bed"
        bed.scale = (1.6, 2.1, 0.44)
        bpy.ops.object.transform_apply(scale=True)
        mat_bed = bpy.data.materials.new("Mat_Bed")
        mat_bed.diffuse_color = (0.16, 0.22, 0.36, 1.0)
        bed.data.materials.append(mat_bed)

        # Cool moonlight + blue smartphone screen glow on actor's face
        bpy.ops.object.light_add(type='POINT', radius=0.25, location=(0.0, -0.25, 1.15))
        phone_l = bpy.context.active_object
        phone_l.data.energy = 450
        phone_l.data.color = (0.35, 0.68, 1.0)

        bpy.ops.object.light_add(type='SPOT', radius=1.8, location=(0.0, -3.5, 3.6))
        moon_l = bpy.context.active_object
        moon_l.data.energy = 900
        moon_l.data.color = (0.65, 0.80, 1.0)

    else:
        # Interior Studio / Room (Moved left wall to X = -3.8 so camera never clips inside it)
        mat_floor.diffuse_color = (0.12, 0.13, 0.15, 1.0)
        floor.data.materials.append(mat_floor)

        mat_wall = bpy.data.materials.new("Mat_Wall")
        mat_wall.diffuse_color = (0.19, 0.21, 0.25, 1.0)
        mat_wood = bpy.data.materials.new("Mat_Wood")
        mat_wood.diffuse_color = (0.36, 0.22, 0.12, 1.0)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 3.8, 1.6))
        wb = bpy.context.active_object
        wb.scale = (8.2, 0.2, 3.2)
        bpy.ops.object.transform_apply(scale=True)
        wb.data.materials.append(mat_wall)

        if env_spec.get("has_door", True):
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-3.8, -0.75, 1.6))
            wl_front = bpy.context.active_object
            wl_front.scale = (0.2, 3.0, 3.2)
            bpy.ops.object.transform_apply(scale=True)
            wl_front.data.materials.append(mat_wall)

            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-3.8, 2.85, 1.6))
            wl_back = bpy.context.active_object
            wl_back.scale = (0.2, 2.2, 3.2)
            bpy.ops.object.transform_apply(scale=True)
            wl_back.data.materials.append(mat_wall)

            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-3.8, 1.25, 2.64))
            lintel = bpy.context.active_object
            lintel.scale = (0.2, 1.0, 1.12)
            bpy.ops.object.transform_apply(scale=True)
            lintel.data.materials.append(mat_wall)

            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-3.8, 1.25, 1.03))
            door = bpy.context.active_object
            door.name = "Room_Door"
            door.scale = (0.06, 0.98, 2.06)
            bpy.ops.object.transform_apply(scale=True)
            door.data.materials.append(mat_wood)

            scene.cursor.location = Vector((-3.8, 1.75, 0.0))
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

            f_crack = max(1, int(env_spec.get("door_crack_sec", 1.9) * fps))
            f_open = max(f_crack + 4, int(env_spec.get("door_open_sec", 2.7) * fps))

            door.rotation_euler = Euler((0, 0, 0), 'XYZ')
            door.keyframe_insert("rotation_euler", frame=1)
            door.keyframe_insert("rotation_euler", frame=max(1, f_crack - 2))
            door.rotation_euler = Euler((0, 0, math.radians(24)), 'XYZ')
            door.keyframe_insert("rotation_euler", frame=f_crack + 4)
            door.rotation_euler = Euler((0, 0, math.radians(82)), 'XYZ')
            door.keyframe_insert("rotation_euler", frame=f_open)

        if env_spec.get("has_desk", False):
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.1, 2.0, 0.38))
            desk = bpy.context.active_object
            desk.scale = (0.9, 0.55, 0.76)
            bpy.ops.object.transform_apply(scale=True)
            desk.data.materials.append(mat_wood)

        bpy.ops.object.light_add(type='SPOT', radius=1.2, location=(0.0, 0.2, 3.4))
        key_l = bpy.context.active_object
        key_l.data.energy = 1000
        key_l.data.spot_size = math.radians(70)
        key_l.data.color = (1.0, 0.92, 0.82)

        bpy.ops.object.light_add(type='AREA', radius=1.8, location=(-4.5, 1.25, 2.2))
        door_l = bpy.context.active_object
        door_l.data.energy = 900
        door_l.data.color = (0.72, 0.86, 1.0)


def compute_framing_vectors(framing, actor_objs, scene, props_dict=None, beat_name=""):
    """
    Pose-aware mathematical framing solver.
    Uses get_actor_anatomical_targets() so sitting, kneeling, or standing actors
    are always framed accurately at their true eye/chest elevation.
    """
    a1 = actor_objs.get("actor_1")
    a2 = actor_objs.get("actor_2")

    eye1, chest1, yaw1 = get_actor_anatomical_targets(a1)
    p1 = a1.location.copy() if a1 else Vector((0.0, 1.2, 0.0))
    fwd1 = Vector((math.sin(yaw1), -math.cos(yaw1), 0.0))

    eye2, chest2, yaw2 = get_actor_anatomical_targets(a2)
    p2 = a2.location.copy() if a2 else Vector((-0.85, 1.2, 0.0))

    target_prop = None
    if props_dict:
        for p_k, p_v in props_dict.items():
            if any(w in p_k.lower() for w in ("dog", "animal", "cat")):
                target_prop = p_v
                break

    b_lower = (beat_name or "").lower()
    f_upper = (framing or "MEDIUM_TWO").upper()

    # Special semantic awareness for Space/Sky/Window Dive shots!
    if "space" in b_lower or "earth" in b_lower or "sky" in b_lower or f_upper == "EXTREME_WIDE_AERIAL":
        cam_pos = Vector((p1.x, p1.y - 11.5, eye1.z + 6.5))
        look_at = eye1
    elif "window" in b_lower or f_upper == "WINDOW_EXTERIOR":
        cam_pos = Vector((p1.x, -3.2, eye1.z + 0.45))
        look_at = eye1
    elif f_upper == "BIRDS_EYE_OVERHEAD":
        cam_pos = Vector((p1.x, p1.y - 1.4, eye1.z + 2.4))
        look_at = chest1
    elif f_upper == "HIGH_ANGLE_ON_ACTOR":
        cam_pos = Vector((p1.x, p1.y - 1.85, eye1.z + 0.75))
        look_at = Vector((p1.x, p1.y, (eye1.z + chest1.z) * 0.5))
    elif f_upper == "LOW_ANGLE_HERO":
        cam_pos = Vector((p1.x, p1.y - 1.35, max(0.25, chest1.z - 0.35)))
        look_at = eye1
    elif f_upper == "FACE_CLOSE_UP":
        cam_pos = Vector((p1.x, p1.y - 1.05, eye1.z + 0.02))
        look_at = eye1
    elif f_upper == "FACE_CLOSE_UP_ACTOR_2":
        cam_pos = Vector((p2.x, p2.y - 1.05, eye2.z + 0.02))
        look_at = eye2
    elif f_upper == "EXTREME_CLOSE_UP_ACTOR_1":
        offset_dir = (fwd1 * 0.35 + Vector((0.0, -0.65, 0.0))).normalized()
        cam_pos = eye1 + offset_dir * 1.15
        cam_pos.z = eye1.z + 0.04
        look_at = eye1 - Vector((0.0, 0.0, 0.03))
    elif f_upper == "EXTREME_CLOSE_UP_ACTOR_2":
        cam_pos = Vector((p2.x, p2.y - 0.68, eye2.z + 0.01))
        look_at = eye2
    elif f_upper == "DOOR_ENTRANCE":
        if a2:
            door_target = Vector((min(p2.x, -2.4), p2.y, eye2.z - 0.1))
            cam_pos = Vector((-0.25, 0.35, eye1.z - 0.05))
            look_at = door_target
        else:
            # Single actor scene: medium-wide approach toward actor
            cam_pos = Vector((p1.x, p1.y - 2.6, eye1.z + 0.25))
            look_at = eye1
    elif f_upper == "MEDIUM_TWO":
        if target_prop:
            prop_pos = target_prop.location.copy()
            mid = (p1 + prop_pos) * 0.5
            dist = max(1.85, (p1 - prop_pos).length * 1.8)
            look_at = Vector((mid.x, mid.y, (eye1.z + 0.35) * 0.5))
            cam_pos = Vector((look_at.x + 0.35, look_at.y - dist, look_at.z + 0.25))
        elif a2:
            mid_eye = (eye1 + eye2) * 0.5
            mid_chest = (chest1 + chest2) * 0.5
            look_at = (mid_eye + mid_chest) * 0.5
            dist = max(1.85, (p1 - p2).length * 2.1)
            cam_pos = Vector((look_at.x, look_at.y - dist, look_at.z + 0.04))
        else:
            look_at = (eye1 + chest1) * 0.5
            cam_pos = Vector((p1.x, p1.y - 2.1, look_at.z + 0.05))
    elif f_upper == "TIGHT_MEDIUM_TWO":
        if target_prop:
            prop_pos = target_prop.location.copy()
            mid = (p1 + prop_pos) * 0.5
            look_at = Vector((mid.x, mid.y, (eye1.z + 0.3) * 0.5))
            cam_pos = Vector((look_at.x + 0.25, look_at.y - 1.45, look_at.z + 0.15))
        elif a2:
            mid_eye = (eye1 + eye2) * 0.5
            look_at = Vector((mid_eye.x, mid_eye.y, mid_eye.z - 0.08))
            dist = max(1.45, (p1 - p2).length * 1.68)
            cam_pos = Vector((look_at.x, look_at.y - dist, look_at.z + 0.02))
        else:
            look_at = eye1
            cam_pos = Vector((p1.x, p1.y - 1.45, eye1.z + 0.02))
    elif f_upper == "OTS_1_TO_2":
        cam_pos = Vector((p1.x + 0.28, p1.y - 0.52, eye1.z + 0.04))
        look_at = eye2 if a2 else eye1
    elif f_upper == "OTS_2_TO_1":
        cam_pos = Vector((p2.x - 0.28, p2.y - 0.52, eye2.z + 0.04))
        look_at = eye1
    elif f_upper == "FULL_BODY_ACTOR_1":
        cam_pos = Vector((p1.x, p1.y - 3.1, chest1.z))
        look_at = chest1
    elif f_upper == "FULL_BODY_ACTOR_2":
        cam_pos = Vector((p2.x, p2.y - 3.1, chest2.z))
        look_at = chest2
    elif f_upper == "ORBIT_LEFT":
        cam_pos = Vector((p1.x - 1.65, p1.y - 1.15, eye1.z + 0.05))
        look_at = eye1
    elif f_upper == "ORBIT_RIGHT":
        cam_pos = Vector((p1.x + 1.65, p1.y - 1.15, eye1.z + 0.05))
        look_at = eye1
    elif f_upper == "WIDE_MASTER":
        if len(actor_objs) >= 3:
            eyes = [get_actor_anatomical_targets(ao)[0] for ao in actor_objs.values() if ao]
            chests = [get_actor_anatomical_targets(ao)[1] for ao in actor_objs.values() if ao]
            mid = sum(chests, Vector((0, 0, 0))) / max(1, len(chests))
        else:
            mid = (chest1 + chest2) * 0.5 if a2 else chest1
        cam_pos = Vector((mid.x, mid.y - 4.8, mid.z + 0.85))
        look_at = mid
    elif f_upper in ("GROUP_THREE", "MEDIUM_GROUP", "THREE_SHOT"):
        chests = [get_actor_anatomical_targets(ao)[1] for ao in actor_objs.values() if ao]
        eyes = [get_actor_anatomical_targets(ao)[0] for ao in actor_objs.values() if ao]
        mid_c = sum(chests, Vector((0, 0, 0))) / max(1, len(chests))
        mid_e = sum(eyes, Vector((0, 0, 0))) / max(1, len(eyes))
        look_at = (mid_c + mid_e) * 0.5
        xs = [ao.location.x for ao in actor_objs.values() if ao]
        ys = [ao.location.y for ao in actor_objs.values() if ao]
        span = max(1.5, math.hypot(max(xs) - min(xs), max(ys) - min(ys)) if xs else 1.5)
        dist = max(2.2, span * 1.95)
        cam_pos = Vector((look_at.x, look_at.y - dist, look_at.z + 0.12))
    else:
        cam_pos = Vector((p1.x, p1.y - 1.85, eye1.z))
        look_at = eye1

    # Safety clamp: keep camera inside room bounds X in [-3.4, 3.4], Y <= 3.3, Z >= 0.22
    cam_pos.x = max(-3.4, min(3.4, cam_pos.x))
    cam_pos.y = min(3.3, cam_pos.y)
    cam_pos.z = max(0.22, cam_pos.z)

    return cam_pos, look_at


def smoothstep_cinematic(t):
    """Quintic smoothstep (6t^5 - 15t^4 + 10t^3) for zero-jerk Steadicam acceleration/deceleration."""
    t = max(0.0, min(1.0, float(t)))
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


def whip_ease(t):
    """Fast exponential whip-pan curve."""
    t = max(0.0, min(1.0, float(t)))
    return t * t * (3.0 - 2.0 * t) ** 2


def interpolate_camera_spherical(pos_a, look_a, lens_a, pos_b, look_b, lens_b, raw_t, transition="SMOOTH"):
    """
    True Spherical/Cylindrical Arc Camera Trajectory Solver!
    Instead of moving in a robotic straight line (which cuts through actors or zooms erratically),
    interpolates the camera in polar coordinates (Radius, Azimuth Angle, Elevation Z) around the moving Look-At target!
    """
    if transition == "WHIP":
        u = whip_ease(raw_t)
    elif transition == "LINEAR":
        u = max(0.0, min(1.0, float(raw_t)))
    else:
        u = smoothstep_cinematic(raw_t)

    look_curr = look_a.lerp(look_b, u)
    lens_curr = lens_a + (lens_b - lens_a) * u

    rel_a = pos_a - look_a
    rel_b = pos_b - look_b

    r_a = math.hypot(rel_a.x, rel_a.y)
    r_b = math.hypot(rel_b.x, rel_b.y)

    theta_a = math.atan2(rel_a.x, -rel_a.y)
    theta_b = math.atan2(rel_b.x, -rel_b.y)

    # Shortest angular arc
    d_theta = (theta_b - theta_a + math.pi) % (2.0 * math.pi) - math.pi

    # Use logarithmic radius interpolation when zooming across huge distances (e.g. Space -> Window -> Close-up)
    if r_a > 0.2 and r_b > 0.2 and (r_a / r_b > 2.5 or r_b / r_a > 2.5):
        r_curr = math.exp(math.log(r_a) + (math.log(r_b) - math.log(r_a)) * u)
    else:
        r_curr = r_a + (r_b - r_a) * u

    theta_curr = theta_a + d_theta * u
    z_curr = rel_a.z + (rel_b.z - rel_a.z) * u

    cam_x = look_curr.x + r_curr * math.sin(theta_curr)
    cam_y = look_curr.y - r_curr * math.cos(theta_curr)
    cam_z = max(0.20, look_curr.z + z_curr)

    return Vector((cam_x, cam_y, cam_z)), look_curr, lens_curr


def normalize_spec(raw):
    if not isinstance(raw, dict):
        return DEFAULT_SPEC
    spec = dict(raw)
    spec["duration_sec"] = float(spec.get("duration_sec") or spec.get("duration") or 8.0)
    spec["fps"] = int(spec.get("fps") or 24)

    raw_actors = spec.get("actors")
    norm_actors = []
    if isinstance(raw_actors, dict):
        for idx, (k, v) in enumerate(raw_actors.items()):
            if not isinstance(v, dict):
                continue
            aid = "actor_1" if idx == 0 else ("actor_2" if idx == 1 else k)
            norm_actors.append({
                "id": aid,
                "name": v.get("name", aid),
                "color": v.get("color", [0.95, 0.55, 0.15] if idx == 0 else [0.15, 0.68, 0.95]),
                "height_m": float(v.get("height_m") or v.get("height") or 1.80),
                "start_pos": v.get("start_pos", [0.0, 1.2, 0.0]),
                "start_look_at": v.get("start_look_at", [0.0, -2.0, 1.5]),
                "keyframes": v.get("keyframes", [])
            })
    elif isinstance(raw_actors, list):
        for idx, v in enumerate(raw_actors):
            if not isinstance(v, dict):
                continue
            aid = v.get("id") or ("actor_1" if idx == 0 else f"actor_{idx+1}")
            norm_actors.append({
                "id": aid,
                "name": v.get("name", aid),
                "color": v.get("color", [0.95, 0.55, 0.15] if idx == 0 else [0.15, 0.68, 0.95]),
                "height_m": float(v.get("height_m") or v.get("height") or 1.80),
                "start_pos": v.get("start_pos", [0.0, 1.2, 0.0]),
                "start_look_at": v.get("start_look_at", [0.0, -2.0, 1.5]),
                "keyframes": v.get("keyframes", [])
            })
    if norm_actors:
        for a in norm_actors:
            for kf in a.get("keyframes", []):
                if "time_sec" not in kf and "time" in kf:
                    kf["time_sec"] = float(kf["time"])
                look_val = kf.get("look_at") or kf.get("face_target") or [0.0, -2.0, 1.5]
                if len(look_val) == 2:
                    look_val = [look_val[0], look_val[1], 1.5]
                kf["look_at"] = look_val
                pos_val = kf.get("pos", [0.0, 1.2, 0.0])
                if len(pos_val) == 2:
                    pos_val = [pos_val[0], pos_val[1], 0.0]
                kf["pos"] = pos_val
                if "pose" not in kf:
                    kf["pose"] = "STAND"
        spec["actors"] = norm_actors

    raw_props = spec.get("props") or []
    norm_props = []
    if isinstance(raw_props, list):
        for idx, p in enumerate(raw_props):
            if not isinstance(p, dict):
                continue
            norm_props.append({
                "id": p.get("id") or f"prop_{idx+1}",
                "type": p.get("type") or "dog",
                "name": p.get("name") or p.get("type", "Prop"),
                "pos": p.get("pos") or [0.0, 0.0, 0.0],
                "color": p.get("color") or [0.45, 0.28, 0.15],
                "scale": float(p.get("scale") or 1.0),
                "look_at": p.get("look_at") or [0.0, 1.0, 0.0]
            })
    spec["props"] = norm_props

    raw_beats = spec.get("camera_beats") or spec.get("beats") or []
    norm_beats = []
    for b in raw_beats:
        if not isinstance(b, dict):
            continue
        t_sec = float(b.get("time_sec") if "time_sec" in b else b.get("time", 0.0))
        norm_beats.append({
            "time_sec": t_sec,
            "name": b.get("name") or b.get("label") or b.get("framing", "Shot"),
            "framing": b.get("framing", "MEDIUM_TWO"),
            "lens_mm": float(b.get("lens_mm") or b.get("lens") or 45.0),
            "transition": b.get("transition", "SMOOTH"),
            "cam_pos": b.get("cam_pos"),
            "look_at": b.get("look_at")
        })
    if norm_beats:
        spec["camera_beats"] = norm_beats
    return spec


def import_and_bind_tripo_mesh(arm_obj, mesh_path, scale_f=1.0):
    if not mesh_path or not os.path.exists(mesh_path):
        return None
    try:
        bpy.ops.object.select_all(action='DESELECT')
        ext = os.path.splitext(mesh_path)[1].lower()
        if ext in ('.glb', '.gltf'):
            bpy.ops.import_scene.gltf(filepath=mesh_path)
        elif ext == '.obj':
            try:
                bpy.ops.wm.obj_import(filepath=mesh_path)
            except Exception:
                bpy.ops.import_scene.obj(filepath=mesh_path)
        elif ext == '.fbx':
            bpy.ops.import_scene.fbx(filepath=mesh_path)
        else:
            return None

        imported_objs = [o for o in bpy.context.selected_objects if o.type == 'MESH']
        if not imported_objs:
            return None

        custom_mesh = imported_objs[0]
        custom_mesh.name = f"{arm_obj.name}_TripoMesh"
        custom_mesh.location = arm_obj.location
        custom_mesh.scale = (scale_f, scale_f, scale_f)
        bpy.context.view_layer.objects.active = custom_mesh
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        custom_mesh.select_set(True)
        arm_obj.select_set(True)
        bpy.context.view_layer.objects.active = arm_obj
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')

        for child in arm_obj.children:
            if child != custom_mesh and child.type == 'MESH':
                child.hide_render = True
                child.hide_viewport = True

        return custom_mesh
    except Exception as e:
        print(f"[PREVIS] Warning binding custom Tripo mesh: {e}")
        return None


def generate_previs_from_spec(spec):
    spec = normalize_spec(spec)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(SCENES_DIR, exist_ok=True)

    bpy.ops.wm.read_homefile(use_empty=True)
    scene = bpy.context.scene

    fps = int(spec.get("fps", 24))
    duration_sec = float(spec.get("duration_sec", 8.0))
    total_frames = max(24, int(duration_sec * fps))

    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.render.resolution_x = 960
    scene.render.resolution_y = 540
    scene.render.resolution_percentage = 100
    scene.render.fps = fps
    scene.frame_start = 1
    scene.frame_end = total_frames

    shading = scene.display.shading
    shading.light = 'STUDIO'
    shading.color_type = 'MATERIAL'
    shading.show_shadows = True
    shading.show_cavity = True

    # 1. Build Environment
    build_environment(scene, spec.get("environment", {}), fps, spec_title=spec.get("title", ""))

    # 2. Build Props
    props_objs = {}
    for p_spec in spec.get("props", []):
        pid = p_spec.get("id", "prop_1")
        p_obj = build_prop(p_spec)
        props_objs[pid] = p_obj

    # 3. Build & Animate Actors with Realistic Walk Stride Cycles
    actor_objs = {}
    actor_kf_map = {}
    for a_spec in spec.get("actors", []):
        aid = a_spec.get("id", "actor_1")
        aname = a_spec.get("name", aid)
        color = a_spec.get("color", [0.9, 0.5, 0.2])
        height_m = float(a_spec.get("height_m", 1.80))
        scale_f = height_m / 1.80

        arm_obj = build_rigged_human_actor(aname, color, height_m=height_m)
        actor_objs[aid] = arm_obj

        tripo_path = a_spec.get("custom_mesh_path") or spec.get("tripo_mesh_path")
        if not tripo_path:
            candidate_glb = os.path.join(OUTPUT_DIR, "latest_tripo_actor.glb")
            if os.path.exists(candidate_glb):
                tripo_path = candidate_glb
        if tripo_path and os.path.exists(tripo_path):
            import_and_bind_tripo_mesh(arm_obj, tripo_path, scale_f=scale_f)

        kfs = a_spec.get("keyframes", [])
        if not kfs:
            s_pos = a_spec.get("start_pos", [0.0, 1.2, 0.0])
            s_look = a_spec.get("start_look_at", [0.0, -2.0, 1.5])
            kfs = [{"time_sec": 0.0, "pos": s_pos, "look_at": s_look, "pose": "STAND"}]

        actor_kf_map[aid] = kfs

        for kf in kfs:
            f_num = max(1, min(total_frames, int(float(kf.get("time_sec", 0.0)) * fps) + 1))
            pos = Vector(kf.get("pos", [0.0, 1.2, 0.0]))
            look = Vector(kf.get("look_at", [0.0, -2.0, 1.5]))
            pose = kf.get("pose", "STAND")

            dx = look.x - pos.x
            dy = look.y - pos.y
            yaw = math.atan2(dx, -dy) if (abs(dx) > 1e-4 or abs(dy) > 1e-4) else 0.0

            arm_obj.location = pos
            arm_obj.rotation_euler = Euler((0.0, 0.0, yaw), 'XYZ')
            arm_obj.keyframe_insert("location", frame=f_num)
            arm_obj.keyframe_insert("rotation_euler", frame=f_num)

            apply_rigged_pose(arm_obj, pose, scale_f=scale_f, walk_phase=0.0)
            for b_name in ["Pelvis", "Spine", "Head", "Thigh_L", "Shin_L", "Thigh_R", "Shin_R", "Arm_L", "Arm_R"]:
                if b_name in arm_obj.pose.bones:
                    arm_obj.pose.bones[b_name].keyframe_insert("location", frame=f_num)
                    arm_obj.pose.bones[b_name].keyframe_insert("rotation_euler", frame=f_num)

        # Add natural walking leg stride oscillation between WALK keyframes so actors don't ice-skate!
        for i in range(len(kfs) - 1):
            kf1, kf2 = kfs[i], kfs[i + 1]
            f1 = max(1, min(total_frames, int(float(kf1.get("time_sec", 0.0)) * fps) + 1))
            f2 = max(1, min(total_frames, int(float(kf2.get("time_sec", 0.0)) * fps) + 1))
            dist = (Vector(kf2.get("pos", [0, 0, 0])) - Vector(kf1.get("pos", [0, 0, 0]))).length
            if (str(kf1.get("pose", "")).upper() == "WALK" or dist > 0.35) and (f2 - f1 >= 8):
                for f_step in range(f1 + 4, f2 - 2, 4):
                    phase = (f_step - f1) * 0.45
                    apply_rigged_pose(arm_obj, "WALK", scale_f=scale_f, walk_phase=phase)
                    for b_name in ["Pelvis", "Spine", "Thigh_L", "Shin_L", "Thigh_R", "Shin_R", "Arm_L", "Arm_R"]:
                        if b_name in arm_obj.pose.bones:
                            arm_obj.pose.bones[b_name].keyframe_insert("location", frame=f_step)
                            arm_obj.pose.bones[b_name].keyframe_insert("rotation_euler", frame=f_step)

        if arm_obj.animation_data and arm_obj.animation_data.action:
            act = arm_obj.animation_data.action
            fcurves_list = getattr(act, "fcurves", None)
            if fcurves_list is not None:
                for fc in fcurves_list:
                    for kp in fc.keyframe_points:
                        kp.interpolation = 'BEZIER'
                        kp.easing = 'EASE_IN_OUT'

        # Optional high-level kinematic planner action from spec ("approach_table", "sit_on_chair", "door_entry")
        kinematic_action = str(a_spec.get("action") or a_spec.get("kinematic_action") or "").strip().lower()
        if kinematic_action:
            try:
                import cindy_blender_bridge as cbb
                if kinematic_action in ("approach_table", "approach", "walk_to_table"):
                    s_pos = a_spec.get("start_pos") or kfs[0].get("pos", [0.0, -2.5, 0.0])
                    side = str(a_spec.get("side") or a_spec.get("blocking_side") or "front").lower()
                    target_id = a_spec.get("target_id") or a_spec.get("target_prop")
                    target_obj = props_objs.get(target_id) if target_id else None
                    cbb.plan_actor_approach(
                        bpy.context, arm_obj,
                        (float(s_pos[0]), float(s_pos[1])),
                        side=side, target_obj=target_obj
                    )
                elif kinematic_action in ("sit_on_chair", "sit", "seated"):
                    chair_id = a_spec.get("chair_id")
                    chair_target = props_objs.get(chair_id) if chair_id else None
                    cbb.plan_actor_sit_on_chair(bpy.context, arm_obj, chair_obj=chair_target)
                elif kinematic_action in ("door_entry", "door_interaction", "open_door"):
                    s_pos = a_spec.get("start_pos") or kfs[0].get("pos", [0.0, 3.8, 0.0])
                    e_pos = a_spec.get("end_pos") or kfs[-1].get("pos", [0.0, 1.2, 0.0])
                    door_id = a_spec.get("door_id")
                    door_target = props_objs.get(door_id) if door_id else None
                    cbb.plan_door_interaction(
                        bpy.context, arm_obj, door_obj=door_target,
                        start_xy=(float(s_pos[0]), float(s_pos[1])),
                        end_xy=(float(e_pos[0]), float(e_pos[1]))
                    )
            except Exception as e_kin:
                print(f"[PREVIS] Kinematic action '{kinematic_action}' warning: {e_kin}")

    # 4. Create Cinema Camera & True Spherical/Polar Trajectory Solver
    bpy.ops.object.camera_add(location=(0, -2.5, 1.6))
    cam = bpy.context.active_object
    cam.name = "Cinema_Camera"
    scene.camera = cam
    cam.data.sensor_width = 36.0
    cam.data.passepartout_alpha = 0.95
    cam.data.show_composition_thirds = True

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 1.2, 1.5))
    look_empty = bpy.context.active_object
    look_empty.name = "Cam_LookAt_Target"

    beats = spec.get("camera_beats", [])
    if not beats:
        beats = DEFAULT_SPEC["camera_beats"]

    # Evaluate exact camera waypoints at each beat
    resolved_beats = []
    keyframe_records = []

    for idx, b in enumerate(beats):
        f_num = max(1, min(total_frames, int(float(b.get("time_sec", 0.0)) * fps) + 1))
        if idx == 0:
            f_num = 1
        elif idx == len(beats) - 1 and f_num < total_frames and str(b.get("transition", "SMOOTH")).upper() != "CUT":
            f_num = total_frames

        scene.frame_set(f_num)
        bpy.context.view_layer.update()

        framing = b.get("framing", "MEDIUM_TWO")
        b_name = b.get("name", f"Beat {idx+1}")
        if framing == "CUSTOM" and b.get("cam_pos") and b.get("look_at"):
            cam_pos = Vector(b["cam_pos"])
            look_at = Vector(b["look_at"])
        else:
            cam_pos, look_at = compute_framing_vectors(framing, actor_objs, scene, props_dict=props_objs, beat_name=b_name)

        lens_mm = float(b.get("lens_mm", 45.0))
        transition = str(b.get("transition", "SMOOTH")).upper()

        resolved_beats.append({
            "frame": f_num,
            "cam_pos": cam_pos,
            "look_at": look_at,
            "lens_mm": lens_mm,
            "transition": transition,
            "framing": framing,
            "name": b_name
        })
        keyframe_records.append((f_num, f"cindy_beat{idx+1}_{framing.lower()}", b_name))

    # Ensure final frame is covered
    if resolved_beats[-1]["frame"] < total_frames:
        last_b = dict(resolved_beats[-1])
        last_b["frame"] = total_frames
        resolved_beats.append(last_b)

    # Bake per-frame Spherical Arc Trajectory + Locked Horizon Rotation
    current_rot_quat = None
    for f in range(1, total_frames + 1):
        scene.frame_set(f)

        # Find active segment [seg_start, seg_end]
        seg_a = resolved_beats[0]
        seg_b = resolved_beats[-1]
        for idx in range(len(resolved_beats) - 1):
            if resolved_beats[idx]["frame"] <= f <= resolved_beats[idx + 1]["frame"]:
                seg_a = resolved_beats[idx]
                seg_b = resolved_beats[idx + 1]
                break

        span = max(1, seg_b["frame"] - seg_a["frame"])
        raw_t = (f - seg_a["frame"]) / float(span)

        if seg_b["transition"] == "CUT" and f < seg_b["frame"]:
            c_pos = seg_a["cam_pos"].copy()
            l_pos = seg_a["look_at"].copy()
            lens_val = seg_a["lens_mm"]
        else:
            c_pos, l_pos, lens_val = interpolate_camera_spherical(
                seg_a["cam_pos"], seg_a["look_at"], seg_a["lens_mm"],
                seg_b["cam_pos"], seg_b["look_at"], seg_b["lens_mm"],
                raw_t, transition=seg_b["transition"]
            )

        cam.location = c_pos
        look_empty.location = l_pos
        cam.data.lens = lens_val

        raw_direction = (l_pos - c_pos)
        if raw_direction.length > 0.001:
            target_quat = raw_direction.to_track_quat('-Z', 'Y')
        else:
            target_quat = cam.rotation_euler.to_quaternion()

        if current_rot_quat is None or (seg_b["transition"] == "CUT" and f == seg_b["frame"]):
            current_rot_quat = target_quat
        else:
            slerp_factor = 0.55 if seg_b["transition"] == "WHIP" else 0.35
            current_rot_quat = current_rot_quat.slerp(target_quat, slerp_factor)

        # Subtle fluid-head breathing on X (pitch) and Z (yaw) ONLY — Y (roll) stays 0.0 so horizon is 100% level!
        final_euler = current_rot_quat.to_euler('XYZ')
        final_euler.x += math.sin(f * 0.06) * 0.0018
        final_euler.z += math.cos(f * 0.05) * 0.0018

        cam.rotation_euler = final_euler
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)
        cam.data.keyframe_insert("lens", frame=f)
        look_empty.keyframe_insert("location", frame=f)

    # 5. Run Director Quality Gate & Scene Audit (Auto-Fix physical grounding, clearance & eye-lines)
    try:
        import cindy_blender_bridge as cbb
        from cindy_director_gate import CindyDirectorGate
        import cindy_prompt_profiles as cpp
        from cindy_prompt_grammar import CindyPromptGrammar
    except Exception as e_imp:
        print(f"[PREVIS] Module import warning: {e_imp}")
        cbb = None
        CindyDirectorGate = None
        cpp = None
        CindyPromptGrammar = None

    audited_actors = []
    audit_report = {"passed": True, "actor_count": len(actor_objs), "auto_fixes_applied": [], "checks": []}
    if cbb is not None:
        try:
            audited_actors, audit_report = cbb._run_scene_audit_and_extract(bpy.context, auto_fix=True)
        except Exception as e_aud:
            print(f"[PREVIS] Scene audit warning: {e_aud}")

    # Save Blend File
    blend_path = os.path.join(SCENES_DIR, "cindy_dynamic_previs.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    # Render Keyframe Stills
    scene.render.image_settings.file_format = 'JPEG'
    scene.render.image_settings.quality = 94
    rendered_stills = []

    for f_num, fname, b_label in keyframe_records:
        scene.frame_set(f_num)
        out_jpg = os.path.join(OUTPUT_DIR, f"{fname}.jpg")
        scene.render.filepath = out_jpg
        bpy.ops.render.render(write_still=True)
        rendered_stills.append({
            "frame": f_num,
            "time_sec": round((f_num - 1) / fps, 1),
            "label": b_label,
            "url": f"/outputs/blender_guides/{fname}.jpg"
        })

    # Render Primary Beauty Guide Still + Calibrated 8-bit Depth Guide Pass (frame 1 / primary beat)
    ts = int(time.time())
    hero_frame = keyframe_records[0][0] if keyframe_records else 1
    scene.frame_set(hero_frame)
    beauty_filename = f"blender_guide_{ts}_rgb.png"
    depth_filename = f"blender_guide_{ts}_depth.png"
    beauty_path = os.path.join(OUTPUT_DIR, beauty_filename)
    depth_path = os.path.join(OUTPUT_DIR, depth_filename)
    latest_depth_path = os.path.join(OUTPUT_DIR, "cindy_previs_depth.png")

    try:
        if rendered_stills:
            first_still_file = os.path.join(OUTPUT_DIR, f"{keyframe_records[0][1]}.jpg")
            if os.path.exists(first_still_file):
                shutil.copyfile(first_still_file, beauty_path)
        if not os.path.exists(beauty_path):
            scene.render.image_settings.file_format = 'PNG'
            scene.render.image_settings.color_mode = 'RGBA'
            scene.render.filepath = beauty_path
            bpy.ops.render.render(write_still=True)
    except Exception as e_b:
        print(f"[PREVIS] Beauty guide write warning: {e_b}")

    if cbb is not None:
        try:
            cbb._render_calibrated_depth_pass_53(scene, depth_path, near_clip=0.45, far_clip=8.0)
            if os.path.exists(depth_path):
                shutil.copyfile(depth_path, latest_depth_path)
        except Exception as e_d:
            print(f"[PREVIS] Depth pass render warning: {e_d}")

    if CindyDirectorGate is not None:
        try:
            if os.path.exists(beauty_path):
                b_check = CindyDirectorGate.audit_rendered_guide_image(beauty_path, pass_type="beauty")
                audit_report.setdefault("checks", []).append(b_check)
                if not b_check.get("passed", True):
                    audit_report["passed"] = False
            if os.path.exists(depth_path):
                d_check = CindyDirectorGate.audit_rendered_guide_image(depth_path, pass_type="depth")
                audit_report.setdefault("checks", []).append(d_check)
                if not d_check.get("passed", True):
                    audit_report["passed"] = False
        except Exception as e_img_aud:
            print(f"[PREVIS] Guide image audit warning: {e_img_aud}")

    # 6. Synthesize Standardized 7-Engine Prompt Profiles (cindy_prompt_profiles.py)
    prompt_package = {}
    if cpp is not None:
        try:
            cam_samples = cbb._collect_camera_samples(bpy.context) if cbb else []
            cam_stages = (
                cpp.classify_camera_path(cam_samples)
                if len(cam_samples) >= 2
                else [cpp.CameraStage(0.0, duration_sec, "static")]
            )
            cast_list = []
            for a_spec in spec.get("actors", []):
                aname = a_spec.get("name") or a_spec.get("id", "Actor")
                app = a_spec.get("appearance") or f"Character {aname} in dramatic lighting, realistic skin and wardrobe"
                prop_lbl = a_spec.get("locked_prop") or ""
                cast_list.append({"name": aname, "appearance": app, "locked_prop": prop_lbl})
            if not cast_list and audited_actors:
                cast_list = audited_actors
            if not cast_list:
                cast_list = [{"name": "Protagonist", "appearance": "Lead character in realistic cinema wardrobe", "locked_prop": ""}]

            spec_beats = []
            for a_spec in spec.get("actors", []):
                aname = a_spec.get("name") or a_spec.get("id", "Actor")
                kfs = a_spec.get("keyframes", [])
                if len(kfs) >= 2:
                    for idx_k in range(len(kfs) - 1):
                        t0_k = float(kfs[idx_k].get("time_sec", 0.0))
                        t1_k = float(kfs[idx_k + 1].get("time_sec", duration_sec))
                        if t1_k <= t0_k:
                            t1_k = min(duration_sec, t0_k + 1.5)
                        pose_k = str(kfs[idx_k].get("pose", "STAND")).upper()
                        act_desc = kfs[idx_k].get("action_desc") or (
                            "strides purposefully across the room toward mark" if pose_k == "WALK"
                            else "remains seated in focused dialogue" if pose_k == "SIT"
                            else "gestures expressively during tense exchange" if pose_k in ("POINT", "GESTURE")
                            else "holds ground with subtle micro-expressions and intense eye contact"
                        )
                        spec_beats.append(cpp.Beat(t0=round(t0_k, 2), t1=round(t1_k, 2), actor=aname, action=act_desc))
                elif len(kfs) == 1:
                    pose_k = str(kfs[0].get("pose", "STAND")).upper()
                    act_desc = kfs[0].get("action_desc") or (
                        "remains seated at the table with focused gaze" if pose_k == "SIT"
                        else "stands poised and reacts with subtle breathing and eye contact"
                    )
                    spec_beats.append(cpp.Beat(t0=0.0, t1=round(duration_sec, 2), actor=aname, action=act_desc))

            if not spec_beats and cbb is not None:
                raw_beats = cbb._derive_actor_beats(bpy.context, cast_list, duration_sec)
                spec_beats = [cpp.Beat(t0=b[0], t1=b[1], actor=b[2], action=b[3]) for b in raw_beats]

            dialogue_list = []
            for d_item in spec.get("dialogue", []):
                if isinstance(d_item, dict) and d_item.get("line"):
                    dialogue_list.append(cpp.Dialogue(
                        speaker=d_item.get("speaker", cast_list[0]["name"]),
                        line=d_item.get("line", ""),
                        tone=d_item.get("tone", "low, measured intensity")
                    ))

            env_cfg = spec.get("environment", {})
            env_style = str(env_cfg.get("style", "INTERIOR_DRAMATIC"))
            env_desc = env_cfg.get("description") or f"{spec.get('title', 'Cinematic 3D Previz set')} ({env_style.replace('_', ' ').lower()}), physically grounded architecture and depth"
            lighting_desc = env_cfg.get("lighting") or "dramatic motivating key light, soft warm fill, and crisp rim separation"
            first_framing = beats[0].get("framing", "MEDIUM_TWO") if beats else "MEDIUM_TWO"
            shot_type_map = {
                "WIDE_ESTABLISHING": "Wide Establishing Shot",
                "WIDE_MASTER": "Wide Master Shot",
                "EXTREME_WIDE_AERIAL": "Extreme Wide Aerial Shot",
                "WINDOW_EXTERIOR": "Exterior Through-Window Framing",
                "BIRDS_EYE_OVERHEAD": "Overhead Bird's-Eye Shot",
                "TOP_DOWN_GOD": "Overhead Top-Down Shot",
                "HIGH_ANGLE_ON_ACTOR": "High-Angle Dramatic Shot",
                "HIGH_VULNERABLE": "High-Angle Dramatic Shot",
                "LOW_ANGLE_HERO": "Low-Angle Hero Shot",
                "LOW_HERO": "Low-Angle Hero Shot",
                "MEDIUM_TWO": "Medium Two-Shot",
                "TIGHT_MEDIUM_TWO": "Tight Medium Two-Shot",
                "GROUP_THREE": "Medium Wide Three-Shot",
                "THREE_SHOT": "Medium Wide Three-Shot",
                "MEDIUM_GROUP": "Medium Group Shot",
                "OTS_A_TO_B": "Over-the-Shoulder Shot",
                "OTS_1_TO_2": "Over-the-Shoulder Shot",
                "OTS_B_TO_A": "Reverse Over-the-Shoulder Shot",
                "OTS_2_TO_1": "Reverse Over-the-Shoulder Shot",
                "CLOSEUP_A": "Close-Up Shot",
                "CLOSEUP_B": "Close-Up Shot",
                "FACE_CLOSE_UP": "Close-Up Shot",
                "FACE_CLOSE_UP_ACTOR_2": "Close-Up Shot",
                "EXTREME_CLOSE_UP_ACTOR_1": "Extreme Close-Up Shot",
                "EXTREME_CLOSE_UP_ACTOR_2": "Extreme Close-Up Shot",
                "FULL_BODY_ACTOR_1": "Full-Body Cowboy Shot",
                "FULL_BODY_ACTOR_2": "Full-Body Cowboy Shot",
                "DOOR_ENTRANCE": "Doorway Threshold Medium-Wide Shot",
                "ORBIT_LEFT": "Arcing Medium Shot",
                "ORBIT_RIGHT": "Arcing Medium Shot",
            }
            shot_type_label = shot_type_map.get(first_framing, "Medium Two-Shot" if len(cast_list) == 2 else "Medium Wide Group Shot" if len(cast_list) >= 3 else "Medium Shot")
            lens_mm_val = float(beats[-1].get("lens_mm", 45.0))

            shot_spec = cpp.ShotSpec(
                shot_type=shot_type_label,
                lens_mm=lens_mm_val,
                environment=env_desc,
                lighting=lighting_desc,
                style=spec.get("visual_style") or "cinematic 35mm film look, photorealistic skin and fabric, subtle film grain",
                cast=cast_list,
                beats=spec_beats,
                camera=cam_stages,
                duration_s=duration_sec,
                aspect="16:9",
                dialogue=dialogue_list,
                ambience=spec.get("ambience") or "natural room tone, subtle footsteps and cloth rustle",
                has_start_frame=False,
                references=[c["name"] for c in cast_list],
            )

            target_engine = str(spec.get("target_engine", "WAN_2_2")).upper()
            if target_engine not in cpp.PROFILES:
                target_engine = "WAN_2_2"
            selected_profile = cpp.render(shot_spec, target_engine)
            all_profiles = cpp.render_all(shot_spec)

            if CindyPromptGrammar is not None:
                lens_str = f"{int(round(lens_mm_val))}mm prime lens"
                prompt_package = CindyPromptGrammar.build_seven_part_prompt(
                    visual_style=shot_spec.style,
                    shot_type=shot_type_label,
                    camera_lens=lens_str,
                    camera_motion=", ".join(f"{s.t0:.1f}-{s.t1:.1f}s {s.move}" for s in cam_stages),
                    scene_environment=f"{env_desc}, {lighting_desc}",
                    cast_and_props=cast_list,
                    chronological_beats=[
                        {"time": f"{b.t0:.1f}-{b.t1:.1f}s", "actor": b.actor, "action": b.action}
                        for b in spec_beats
                    ],
                    audio_design=shot_spec.ambience,
                    target_model=target_engine,
                )
            prompt_package["master_prompt"] = selected_profile["prompt"]
            prompt_package["positive_prompt"] = selected_profile["prompt"]
            prompt_package["negative_prompt"] = selected_profile["negative_prompt"]
            prompt_package["profile_notes"] = selected_profile["notes"]
            prompt_package["recommended_duration_s"] = selected_profile.get("recommended_duration_s") or selected_profile.get("duration_s", duration_sec)
            prompt_package["all_tool_prompts"] = all_profiles
        except Exception as e_pp:
            print(f"[PREVIS] Prompt profile synthesis warning: {e_pp}")

    # Render Full MP4 Video (Compatible with Blender 4.x and Blender 5.3+)
    mp4_name = f"cindy_previs_{ts}.mp4"
    mp4_path = os.path.join(OUTPUT_DIR, mp4_name)
    latest_mp4_path = os.path.join(OUTPUT_DIR, "director_confrontation_previz_v3.mp4")

    try:
        scene.render.image_settings.file_format = 'FFMPEG'
        scene.render.ffmpeg.format = 'MPEG4'
        scene.render.ffmpeg.codec = 'H264'
        scene.render.ffmpeg.constant_rate_factor = 'HIGH'
        scene.render.filepath = mp4_path
        bpy.ops.render.render(animation=True)
    except TypeError:
        import subprocess
        seq_dir = os.path.join(OUTPUT_DIR, f"seq_{ts}")
        os.makedirs(seq_dir, exist_ok=True)
        scene.render.image_settings.file_format = 'JPEG'
        scene.render.image_settings.quality = 92
        scene.render.filepath = os.path.join(seq_dir, "frame_")
        bpy.ops.render.render(animation=True)
        sp_kwargs = {"creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)} if os.name == "nt" else {}
        subprocess.run([
            "ffmpeg", "-y", "-framerate", str(fps),
            "-i", os.path.join(seq_dir, "frame_%04d.jpg"),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", mp4_path
        ], check=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **sp_kwargs)
        shutil.rmtree(seq_dir, ignore_errors=True)

    try:
        shutil.copyfile(mp4_path, latest_mp4_path)
    except Exception:
        pass

    meta_out = {
        "timestamp": ts,
        "title": spec.get("title", "3D Pre-vis Scene"),
        "frame": total_frames,
        "duration_sec": duration_sec,
        "lens_focal_length_mm": beats[-1].get("lens_mm", 45.0),
        "resolution": [960, 540],
        "video_url": f"/outputs/blender_guides/{mp4_name}",
        "rgb_url": f"/outputs/blender_guides/{beauty_filename}" if os.path.exists(beauty_path) else (rendered_stills[0]["url"] if rendered_stills else ""),
        "depth_url": f"/outputs/blender_guides/{depth_filename}" if os.path.exists(depth_path) else "",
        "stills": rendered_stills,
        "prompt_package": prompt_package,
        "audit": audit_report,
        "meta": {
            "timestamp": ts,
            "frame": total_frames,
            "duration_sec": duration_sec,
            "lens_focal_length_mm": beats[-1].get("lens_mm", 45.0),
            "resolution": [960, 540],
            "camera_motion_preset": "SPHERICAL_ARC_PREVIS"
        },
        "spec": spec
    }
    with open(os.path.join(OUTPUT_DIR, f"blender_guide_{ts}_meta.json"), "w", encoding="utf-8") as mf:
        json.dump(meta_out, mf, indent=2, ensure_ascii=False)
    with open(os.path.join(OUTPUT_DIR, "latest_previs_result.json"), "w", encoding="utf-8") as lf:
        json.dump(meta_out, lf, indent=2, ensure_ascii=False)

    print("[CINDY_PREVIS_SUCCESS]", json.dumps(meta_out, ensure_ascii=False))


if __name__ == "__main__":
    spec_to_run = DEFAULT_SPEC
    custom_spec_path = None
    if "--" in sys.argv:
        extra_args = sys.argv[sys.argv.index("--") + 1:]
        if extra_args and os.path.exists(extra_args[0]):
            custom_spec_path = extra_args[0]
    target_spec_file = custom_spec_path or (SPEC_FILE if os.path.exists(SPEC_FILE) else None)
    if target_spec_file:
        try:
            with open(target_spec_file, "r", encoding="utf-8") as f:
                spec_to_run = json.load(f)
        except Exception as e:
            print("Warning: failed to load spec file, using default:", e)
    generate_previs_from_spec(spec_to_run)
