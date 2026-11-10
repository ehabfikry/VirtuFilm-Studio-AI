"""
Cindy AI Director — Universal Parametric 3D Pre-vis Engine (cindy_previs_engine.py)
Builds realistic 1.85m articulated human mannequins, hinged doors, room/alley/studio sets,
and uses Per-Frame Mathematical Look-At Tracking so the subject is 100% framed on every frame.
"""

import bpy
import sys
import os
import json
import math
import time
from mathutils import Vector, Euler

OUTPUT_DIR = r"C:\Users\DELL\Desktop\Cindy-AI-Director\outputs\blender_guides"
SCENES_DIR = r"D:\Blender\scenes"
SPEC_FILE = os.path.join(OUTPUT_DIR, "current_previs_spec.json")

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
                {"time_sec": 0.0, "pos": [0.0, 1.2, 0.0], "look_at": [0.0, -2.0, 1.5]},
                {"time_sec": 2.0, "pos": [0.0, 1.2, 0.0], "look_at": [0.0, -2.0, 1.5]},
                {"time_sec": 2.7, "pos": [0.0, 1.2, 0.0], "look_at": [-3.0, 1.25, 1.6]},
                {"time_sec": 5.0, "pos": [0.0, 1.2, 0.0], "look_at": [-0.85, 1.2, 1.68]},
                {"time_sec": 8.0, "pos": [0.0, 1.2, 0.0], "look_at": [-0.85, 1.2, 1.68]}
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
                {"time_sec": 0.0, "pos": [-3.6, 1.25, 0.0], "look_at": [0.0, 1.2, 1.68]},
                {"time_sec": 2.0, "pos": [-3.4, 1.25, 0.0], "look_at": [0.0, 1.2, 1.68]},
                {"time_sec": 2.8, "pos": [-2.5, 1.22, 0.0], "look_at": [0.0, 1.2, 1.68]},
                {"time_sec": 5.5, "pos": [-0.85, 1.2, 0.0], "look_at": [0.0, 1.2, 1.68]},
                {"time_sec": 8.0, "pos": [-0.85, 1.2, 0.0], "look_at": [0.0, 1.2, 1.68]}
            ]
        }
    ],
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
            "name": "Beat 1B: Crane Down to Actor 1 Face",
            "framing": "FACE_CLOSE_UP",
            "target": "actor_1",
            "lens_mm": 50.0,
            "transition": "SMOOTH"
        },
        {
            "time_sec": 2.8,
            "name": "Beat 2: Fast Whip Pan to Door Entrance",
            "framing": "DOOR_ENTRANCE",
            "target": "actor_2",
            "lens_mm": 38.0,
            "transition": "WHIP"
        },
        {
            "time_sec": 5.8,
            "name": "Beat 3: Pull Back to Medium Two Standoff",
            "framing": "MEDIUM_TWO",
            "target": "both",
            "lens_mm": 42.0,
            "transition": "SMOOTH"
        },
        {
            "time_sec": 8.0,
            "name": "Beat 4: Tight Medium Two Confrontation",
            "framing": "TIGHT_MEDIUM_TWO",
            "target": "both",
            "lens_mm": 50.0,
            "transition": "SMOOTH"
        }
    ]
}


def build_human_actor(name, color_rgb, height_m=1.84):
    """
    Creates an articulated, realistic-proportion human mannequin (1.84m default)
    with origin at the bottom of the feet (0, 0, 0) and front face pointing along -Y.
    """
    scale_f = height_m / 1.80
    parts = []

    # 1. Legs
    for lx in (-0.11 * scale_f, 0.11 * scale_f):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.075 * scale_f,
            depth=0.88 * scale_f,
            location=(lx, 0.0, 0.44 * scale_f)
        )
        parts.append(bpy.context.active_object)

    # 2. Torso / Chest
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.20 * scale_f,
        depth=0.62 * scale_f,
        location=(0.0, 0.0, 1.15 * scale_f)
    )
    torso = bpy.context.active_object
    torso.scale = (1.15, 0.72, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    parts.append(torso)

    # 3. Shoulders
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.075 * scale_f,
        depth=0.48 * scale_f,
        location=(0.0, 0.0, 1.41 * scale_f),
        rotation=(0.0, math.radians(90), 0.0)
    )
    parts.append(bpy.context.active_object)

    # 4. Arms
    for ax in (-0.25 * scale_f, 0.25 * scale_f):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.052 * scale_f,
            depth=0.64 * scale_f,
            location=(ax, 0.0, 1.11 * scale_f)
        )
        parts.append(bpy.context.active_object)

    # 5. Neck
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.062 * scale_f,
        depth=0.12 * scale_f,
        location=(0.0, 0.0, 1.51 * scale_f)
    )
    parts.append(bpy.context.active_object)

    # 6. Head (Eye level at ~1.68 * scale_f, Crown at ~1.80 * scale_f)
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.122 * scale_f,
        location=(0.0, 0.0, 1.675 * scale_f)
    )
    head = bpy.context.active_object
    head.scale = (0.92, 1.0, 1.12)
    bpy.ops.object.transform_apply(scale=True)
    parts.append(head)

    mat_body = bpy.data.materials.new(f"Mat_{name}")
    mat_body.diffuse_color = (color_rgb[0], color_rgb[1], color_rgb[2], 1.0)
    for p in parts:
        p.data.materials.append(mat_body)

    # 7. Dark Gaze Visor / Eye-line Band on Front Face (-Y)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0.0, -0.105 * scale_f, 1.685 * scale_f)
    )
    visor = bpy.context.active_object
    visor.scale = (0.16 * scale_f, 0.05 * scale_f, 0.038 * scale_f)
    bpy.ops.object.transform_apply(scale=True)
    mat_visor = bpy.data.materials.new(f"Mat_{name}_Visor")
    mat_visor.diffuse_color = (0.06, 0.06, 0.08, 1.0)
    visor.data.materials.append(mat_visor)
    parts.append(visor)

    # Join all parts into one rock-solid mesh
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = torso
    bpy.ops.object.join()
    actor = bpy.context.active_object
    actor.name = name

    # Set origin strictly at feet (0, 0, 0)
    bpy.context.scene.cursor.location = Vector((0.0, 0.0, 0.0))
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    return actor


def build_environment(scene, env_spec, fps):
    env_type = env_spec.get("type", "room")

    # Floor
    bpy.ops.mesh.primitive_plane_add(size=12.0, location=(0, 1.5, 0))
    floor = bpy.context.active_object
    floor.name = "Stage_Floor"
    mat_floor = bpy.data.materials.new("Mat_Floor")
    mat_floor.diffuse_color = (0.12, 0.13, 0.15, 1.0)
    floor.data.materials.append(mat_floor)

    mat_wall = bpy.data.materials.new("Mat_Wall")
    mat_wall.diffuse_color = (0.19, 0.21, 0.25, 1.0)

    mat_wood = bpy.data.materials.new("Mat_Wood")
    mat_wood.diffuse_color = (0.36, 0.22, 0.12, 1.0)

    if env_type in ("room", "corridor"):
        # Back Wall
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 3.8, 1.6))
        wb = bpy.context.active_object
        wb.scale = (7.5, 0.2, 3.2)
        bpy.ops.object.transform_apply(scale=True)
        wb.data.materials.append(mat_wall)

        if env_spec.get("has_door", True):
            # Doorway on Left Wall at X = -3.2, opening Y = 0.75 to 1.75 (width 1.0m, height 2.08m)
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-3.2, -0.75, 1.6))
            wl_front = bpy.context.active_object
            wl_front.scale = (0.2, 3.0, 3.2)
            bpy.ops.object.transform_apply(scale=True)
            wl_front.data.materials.append(mat_wall)

            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-3.2, 2.85, 1.6))
            wl_back = bpy.context.active_object
            wl_back.scale = (0.2, 2.2, 3.2)
            bpy.ops.object.transform_apply(scale=True)
            wl_back.data.materials.append(mat_wall)

            # Door Lintel above Y=0.75..1.75 from Z=2.08 to 3.20
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-3.2, 1.25, 2.64))
            lintel = bpy.context.active_object
            lintel.scale = (0.2, 1.0, 1.12)
            bpy.ops.object.transform_apply(scale=True)
            lintel.data.materials.append(mat_wall)

            # Hinged Door Leaf: spans Y=0.75..1.75, height=2.06m, hinge at (-3.2, 1.75, 0.0)
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-3.2, 1.25, 1.03))
            door = bpy.context.active_object
            door.name = "Room_Door"
            door.scale = (0.06, 0.98, 2.06)
            bpy.ops.object.transform_apply(scale=True)
            door.data.materials.append(mat_wood)

            # Set pivot at Hinge (-3.2, 1.75, 0.0) so it swings cleanly into the room!
            scene.cursor.location = Vector((-3.2, 1.75, 0.0))
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
        # Side desk behind Actor 1
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.75, 1.9, 0.38))
        desk = bpy.context.active_object
        desk.scale = (0.9, 0.55, 0.76)
        bpy.ops.object.transform_apply(scale=True)
        desk.data.materials.append(mat_wood)

    # Studio Lighting
    bpy.ops.object.light_add(type='SPOT', radius=1.2, location=(0.0, 0.2, 3.4))
    key_l = bpy.context.active_object
    key_l.data.energy = 1000
    key_l.data.spot_size = math.radians(70)
    key_l.data.color = (1.0, 0.92, 0.82)

    bpy.ops.object.light_add(type='AREA', radius=1.8, location=(-4.2, 1.25, 2.2))
    door_l = bpy.context.active_object
    door_l.data.energy = 900
    door_l.data.color = (0.72, 0.86, 1.0)

    bpy.ops.object.light_add(type='AREA', radius=2.5, location=(-0.4, 3.2, 2.3))
    rim_l = bpy.context.active_object
    rim_l.data.energy = 750
    rim_l.data.color = (0.9, 0.95, 1.0)


def compute_framing_vectors(framing, actor_objs, scene):
    """
    Given a semantic framing type and current evaluated actor positions at the current frame,
    returns (cam_location, look_at_point) mathematically calibrated so the subject is centered.
    """
    a1 = actor_objs.get("actor_1")
    a2 = actor_objs.get("actor_2")

    p1 = a1.location.copy() if a1 else Vector((0.0, 1.2, 0.0))
    h1 = a1.get("height_m", 1.84) if a1 else 1.84
    yaw1 = a1.rotation_euler.z if a1 else 0.0
    fwd1 = Vector((math.sin(yaw1), -math.cos(yaw1), 0.0))
    eye1 = Vector((p1.x, p1.y, p1.z + h1 * 0.91))
    chest1 = Vector((p1.x, p1.y, p1.z + h1 * 0.76))

    p2 = a2.location.copy() if a2 else Vector((-0.85, 1.2, 0.0))
    h2 = a2.get("height_m", 1.86) if a2 else 1.86
    yaw2 = a2.rotation_euler.z if a2 else 0.0
    fwd2 = Vector((math.sin(yaw2), -math.cos(yaw2), 0.0))
    eye2 = Vector((p2.x, p2.y, p2.z + h2 * 0.91))
    chest2 = Vector((p2.x, p2.y, p2.z + h2 * 0.76))

    if framing == "BIRDS_EYE_OVERHEAD":
        cam_pos = Vector((p1.x, p1.y - 0.85, p1.z + h1 + 1.15))
        look_at = chest1
    elif framing == "HIGH_ANGLE_ON_ACTOR":
        cam_pos = Vector((p1.x, p1.y - 1.55, p1.z + h1 + 0.55))
        look_at = Vector((p1.x, p1.y, p1.z + h1 * 0.82))
    elif framing == "LOW_ANGLE_HERO":
        cam_pos = Vector((p1.x, p1.y - 1.25, p1.z + h1 * 0.48))
        look_at = eye1
    elif framing == "FACE_CLOSE_UP":
        cam_pos = Vector((p1.x, p1.y - 0.95, eye1.z + 0.02))
        look_at = eye1
    elif framing == "FACE_CLOSE_UP_ACTOR_2":
        cam_pos = Vector((p2.x, p2.y - 0.95, eye2.z + 0.02))
        look_at = eye2
    elif framing == "EXTREME_CLOSE_UP_ACTOR_1":
        # 3/4 frontal macro shot on Actor 1's eyes along his gaze direction
        offset_dir = (fwd1 * 0.55 + Vector((0.0, -0.35, 0.0))).normalized()
        cam_pos = eye1 + offset_dir * 0.68
        look_at = eye1
    elif framing == "EXTREME_CLOSE_UP_ACTOR_2":
        # 3/4 frontal macro shot on Actor 2's eyes along his gaze direction
        offset_dir = (fwd2 * 0.55 + Vector((0.0, -0.35, 0.0))).normalized()
        cam_pos = eye2 + offset_dir * 0.68
        look_at = eye2
    elif framing == "DOOR_ENTRANCE":
        door_target = Vector((min(p2.x, -2.4), p2.y, p2.z + h2 * 0.82))
        cam_pos = Vector((-0.25, 0.35, eye1.z - 0.05))
        look_at = door_target
    elif framing == "MEDIUM_TWO":
        mid_eye = (eye1 + eye2) * 0.5
        mid_chest = (chest1 + chest2) * 0.5
        look_at = (mid_eye + mid_chest) * 0.5
        dist = max(1.85, (p1 - p2).length * 2.1)
        cam_pos = Vector((look_at.x, look_at.y - dist, look_at.z + 0.04))
    elif framing == "TIGHT_MEDIUM_TWO":
        mid_eye = (eye1 + eye2) * 0.5
        look_at = Vector((mid_eye.x, mid_eye.y, mid_eye.z - 0.08))
        dist = max(1.45, (p1 - p2).length * 1.68)
        cam_pos = Vector((look_at.x, look_at.y - dist, look_at.z + 0.02))
    elif framing == "OTS_1_TO_2":
        cam_pos = Vector((p1.x + 0.25, p1.y - 0.45, eye1.z + 0.04))
        look_at = eye2
    elif framing == "OTS_2_TO_1":
        cam_pos = Vector((p2.x - 0.25, p2.y - 0.45, eye2.z + 0.04))
        look_at = eye1
    elif framing == "FULL_BODY_ACTOR_1":
        cam_pos = Vector((p1.x, p1.y - 2.6, p1.z + h1 * 0.55))
        look_at = Vector((p1.x, p1.y, p1.z + h1 * 0.55))
    elif framing == "FULL_BODY_ACTOR_2":
        cam_pos = Vector((p2.x, p2.y - 2.6, p2.z + h2 * 0.55))
        look_at = Vector((p2.x, p2.y, p2.z + h2 * 0.55))
    elif framing == "ORBIT_LEFT":
        cam_pos = Vector((p1.x - 1.5, p1.y - 1.1, eye1.z + 0.05))
        look_at = eye1
    elif framing == "ORBIT_RIGHT":
        cam_pos = Vector((p1.x + 1.5, p1.y - 1.1, eye1.z + 0.05))
        look_at = eye1
    elif framing == "WIDE_MASTER":
        mid = (chest1 + chest2) * 0.5 if a2 else chest1
        cam_pos = Vector((mid.x, mid.y - 4.2, mid.z + 0.9))
        look_at = mid
    else:
        cam_pos = Vector((p1.x, p1.y - 1.8, eye1.z))
        look_at = eye1

    return cam_pos, look_at


def normalize_spec(raw):
    """Normalizes any LLM-generated previs_spec (beats/camera_beats, dict/list actors, time/time_sec)."""
    if not isinstance(raw, dict):
        return DEFAULT_SPEC
    spec = dict(raw)
    spec["duration_sec"] = float(spec.get("duration_sec") or spec.get("duration") or 8.0)
    spec["fps"] = int(spec.get("fps") or 24)

    # Normalize actors (can be list or dict)
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
                "height_m": float(v.get("height_m") or v.get("height") or 1.84),
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
                "height_m": float(v.get("height_m") or v.get("height") or 1.84),
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
                    look_val = [look_val[0], look_val[1], 1.6]
                kf["look_at"] = look_val
                pos_val = kf.get("pos", [0.0, 1.2, 0.0])
                if len(pos_val) == 2:
                    pos_val = [pos_val[0], pos_val[1], 0.0]
                kf["pos"] = pos_val
        spec["actors"] = norm_actors

    # Normalize camera_beats / beats
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
    build_environment(scene, spec.get("environment", {}), fps)

    # 2. Build & Animate Actors
    actor_objs = {}
    for a_spec in spec.get("actors", []):
        aid = a_spec.get("id", "actor_1")
        aname = a_spec.get("name", aid)
        color = a_spec.get("color", [0.9, 0.5, 0.2])
        height_m = float(a_spec.get("height_m", 1.84))

        actor = build_human_actor(aname, color, height_m=height_m)
        actor["height_m"] = height_m
        actor_objs[aid] = actor

        kfs = a_spec.get("keyframes", [])
        if not kfs:
            s_pos = a_spec.get("start_pos", [0.0, 1.2, 0.0])
            s_look = a_spec.get("start_look_at", [0.0, -2.0, 1.5])
            kfs = [{"time_sec": 0.0, "pos": s_pos, "look_at": s_look}]

        for kf in kfs:
            f_num = max(1, min(total_frames, int(float(kf.get("time_sec", 0.0)) * fps) + 1))
            pos = Vector(kf.get("pos", [0.0, 1.2, 0.0]))
            look = Vector(kf.get("look_at", [0.0, -2.0, 1.5]))
            dx = look.x - pos.x
            dy = look.y - pos.y
            yaw = math.atan2(dx, -dy) if (abs(dx) > 1e-4 or abs(dy) > 1e-4) else 0.0

            actor.location = pos
            actor.rotation_euler = Euler((0.0, 0.0, yaw), 'XYZ')
            actor.keyframe_insert("location", frame=f_num)
            actor.keyframe_insert("rotation_euler", frame=f_num)

        if actor.animation_data and actor.animation_data.action:
            for fc in actor.animation_data.action.fcurves:
                for kp in fc.keyframe_points:
                    kp.interpolation = 'BEZIER'
                    kp.easing = 'EASE_IN_OUT'

    # 3. Create Camera & Helper Look-At Empty for Per-Frame Exact Tracking
    bpy.ops.object.camera_add(location=(0, -1.5, 1.8))
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

    keyframe_records = []
    prev_cam_pos = None
    prev_look_at = None
    prev_lens = 45.0

    for idx, b in enumerate(beats):
        f_num = max(1, min(total_frames, int(float(b.get("time_sec", 0.0)) * fps) + 1))
        if idx == 0:
            f_num = 1
        elif idx == len(beats) - 1 and f_num < total_frames and b.get("transition") != "CUT":
            f_num = total_frames

        scene.frame_set(f_num)
        framing = b.get("framing", "MEDIUM_TWO")
        if framing == "CUSTOM" and "cam_pos" in b and "look_at" in b:
            cam_pos = Vector(b["cam_pos"])
            look_at = Vector(b["look_at"])
        else:
            cam_pos, look_at = compute_framing_vectors(framing, actor_objs, scene)

        lens_mm = float(b.get("lens_mm", 45.0))
        transition = str(b.get("transition", "SMOOTH")).upper()

        # If this beat is an instant editorial CUT, lock the previous state at (f_num - 1)
        if transition == "CUT" and prev_cam_pos is not None and f_num > 2:
            cam.location = prev_cam_pos
            cam.data.lens = prev_lens
            look_empty.location = prev_look_at
            cam.keyframe_insert("location", frame=f_num - 1)
            cam.data.keyframe_insert("lens", frame=f_num - 1)
            look_empty.keyframe_insert("location", frame=f_num - 1)

        cam.location = cam_pos
        cam.data.lens = lens_mm
        look_empty.location = look_at

        cam.keyframe_insert("location", frame=f_num)
        cam.data.keyframe_insert("lens", frame=f_num)
        look_empty.keyframe_insert("location", frame=f_num)

        # If this is the last beat and it was a CUT before the end of the timeline, hold it until total_frames
        if idx == len(beats) - 1 and f_num < total_frames:
            cam.keyframe_insert("location", frame=total_frames)
            cam.data.keyframe_insert("lens", frame=total_frames)
            look_empty.keyframe_insert("location", frame=total_frames)

        prev_cam_pos = cam_pos.copy()
        prev_look_at = look_at.copy()
        prev_lens = lens_mm

        keyframe_records.append((f_num, f"cindy_beat{idx+1}_{framing.lower()}", b.get("name", f"Beat {idx+1}")))

    # Smooth interpolation on camera position and look_empty position
    for obj_anim in (cam, look_empty):
        if obj_anim.animation_data and obj_anim.animation_data.action:
            for fc in obj_anim.animation_data.action.fcurves:
                for kp in fc.keyframe_points:
                    kp.interpolation = 'BEZIER'
                    kp.easing = 'EASE_IN_OUT'

    # Bake exact Look-At rotation on EVERY SINGLE FRAME so subject never drifts!
    for f in range(1, total_frames + 1):
        scene.frame_set(f)
        direction = look_empty.location - cam.location
        cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
        cam.keyframe_insert("rotation_euler", frame=f)

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

    # Render Full MP4 Video
    ts = int(time.time())
    mp4_name = f"cindy_previs_{ts}.mp4"
    mp4_path = os.path.join(OUTPUT_DIR, mp4_name)
    latest_mp4_path = os.path.join(OUTPUT_DIR, "director_confrontation_previz_v3.mp4")

    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.filepath = mp4_path

    bpy.ops.render.render(animation=True)

    import shutil
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
        "stills": rendered_stills,
        "spec": spec
    }
    with open(os.path.join(OUTPUT_DIR, f"blender_guide_{ts}_meta.json"), "w", encoding="utf-8") as mf:
        json.dump(meta_out, mf, indent=2, ensure_ascii=False)
    with open(os.path.join(OUTPUT_DIR, "latest_previs_result.json"), "w", encoding="utf-8") as lf:
        json.dump(meta_out, lf, indent=2, ensure_ascii=False)

    print("[CINDY_PREVIS_SUCCESS]", json.dumps(meta_out, ensure_ascii=False))


if __name__ == "__main__":
    spec_to_run = DEFAULT_SPEC
    if os.path.exists(SPEC_FILE):
        try:
            with open(SPEC_FILE, "r", encoding="utf-8") as f:
                spec_to_run = json.load(f)
        except Exception as e:
            print("Warning: failed to load spec file, using default:", e)
    generate_previs_from_spec(spec_to_run)
