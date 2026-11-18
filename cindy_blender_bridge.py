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

"""
=============================================================================
Cindy AI Director — Blender 3D Virtual Staging & Infinite Camera Motion Suite
Version: 5.0 (Director Studio Edition)
=============================================================================
Provides film directors with effortless 3D scene building, actor blocking,
camera navigation, multi-beat compound motion recording, and AI depth export.
"""

import bpy
import os
import json
import time
import math
from mathutils import Vector, Euler

bl_info = {
    "name": "Cindy AI Director — Virtual Staging & Camera Motion Suite",
    "author": "Google DeepMind / Antigravity Team",
    "version": (5, 3, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Cindy Director",
    "description": "Effortless scene building, actor blocking, camera framing, and infinite compound motion suite",
    "category": "Render",
}

OUTPUT_BASE_DIR = r"C:\Users\DELL\Desktop\Cindy-AI-Director\outputs\blender_guides"
SCENE_PRESET_PATH = r"D:\Blender\scenes\compound_camera_shot.blend"

COMPOUND_MOVE_ITEMS = [
    ('CRANE_PUSH_IN', "Crane Down + Push In", "Plunges from high-wide down into an intense close-up"),
    ('CRANE_PULL_OUT', "Crane Up + Pull Out", "Starts tight, pulls back into high omniscient wide reveal"),
    ('SPACE_WINDOW_DIVE', "Cosmic Window Dive -> Extreme Close-Up", "Dives from high aerial exterior straight through window into tight face close-up"),
    ('WHIP_PAN_RIGHT', "Whip Pan Right (90 deg)", "Violent 90-degree rotational snap right with heavy blur"),
    ('WHIP_PAN_LEFT', "Whip Pan Left (90 deg)", "Violent 90-degree rotational snap left with heavy blur"),
    ('VERTIGO_DOLLY_ZOOM', "Vertigo / Dolly Zoom (Hitchcock)", "Dolly in while zooming wide: subject scale locked, background warps!"),
    ('HERO_ARC_180', "180 deg Dramatic Arc Reveal", "Half-circle orbital arc tracking around subject"),
    ('HERO_ORBIT_360', "360 deg Full Hero Orbit", "Full 360-degree circular rotation around subject"),
    ('DUTCH_CREEP', "Low Dutch Creep (-15 deg Noir)", "Low ground skimming with -15 deg Dutch tilt for noir tension"),
    ('PARALLAX_PILLARS', "Parallax Reveal Past Columns", "Lateral tracking behind foreground architecture"),
]

TRANSITION_STYLE_ITEMS = [
    ('SMOOTH', "Smooth Cinematic (Push / Crane / Arc)", "Natural organic acceleration and deceleration"),
    ('WHIP', "Whip Pan (Fast Snap)", "Exponential acceleration with sudden rapid rotation"),
    ('LINEAR', "Linear Tracking (Dolly / Slider)", "Constant velocity mechanical track"),
]

def ensure_output_dir():
    if not os.path.exists(OUTPUT_BASE_DIR):
        os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)
    return OUTPUT_BASE_DIR

def ensure_camera(scene):
    cam = scene.camera
    if not cam or cam.type != 'CAMERA':
        cam = scene.objects.get("Cinema_Camera") or scene.objects.get("Camera")
        if not cam:
            bpy.ops.object.camera_add(location=(0, -5.0, 1.6), rotation=(math.radians(88), 0, 0))
            cam = bpy.context.active_object
            cam.name = "Cinema_Camera"
        scene.camera = cam

    # Set cinema standards
    cam.data.sensor_width = 36.0
    cam.data.passepartout_alpha = 0.92
    cam.data.show_composition_thirds = True
    cam.data.show_composition_center = True
    return cam

def get_target_location(scene):
    if bpy.context.active_object and bpy.context.active_object.type != 'CAMERA':
        return bpy.context.active_object.location.copy()
    if scene.objects.get("Actor_1_Body"):
        return scene.objects["Actor_1_Body"].location.copy()
    if scene.objects.get("Character_Body"):
        return scene.objects["Character_Body"].location.copy()
    return Vector((0.0, 0.0, 1.2))

def create_or_get_collection(name, parent_col=None):
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
        if parent_col:
            parent_col.children.link(col)
        else:
            bpy.context.scene.collection.children.link(col)
    return col

# =============================================================================
# OPERATORS: STAGE SETUP & SCENE BUILDER
# =============================================================================

class CINDY_OT_NewDirectorStage(bpy.types.Operator):
    bl_idname = "cindy.new_director_stage"
    bl_label = "Create Clean Director Stage"
    bl_description = "Clear default scene and create a professional studio stage with 3-point lighting and Cinema Camera"

    def execute(self, context):
        scene = context.scene

        # Remove default cube if present
        default_cube = scene.objects.get("Cube")
        if default_cube:
            bpy.data.objects.remove(default_cube, do_unlink=True)

        stage_col = create_or_get_collection("Cindy_Stage")

        # Studio Floor
        floor = scene.objects.get("Studio_Floor")
        if not floor:
            bpy.ops.mesh.primitive_cylinder_add(radius=10.0, depth=0.1, location=(0, 0, -0.05))
            floor = context.active_object
            floor.name = "Studio_Floor"
            for c in floor.users_collection:
                c.objects.unlink(floor)
            stage_col.objects.link(floor)

            mat_floor = bpy.data.materials.new(name="Mat_Studio_Floor")
            mat_floor.use_nodes = True
            bsdf = mat_floor.node_tree.nodes.get("Principled BSDF")
            if bsdf:
                bsdf.inputs['Base Color'].default_value = (0.12, 0.13, 0.15, 1.0)
                bsdf.inputs['Roughness'].default_value = 0.4
            floor.data.materials.append(mat_floor)

        # 3-Point Lighting
        lights_data = [
            ("Key_Light_Warm", (4.5, -4.0, 4.2), 750, (1.0, 0.92, 0.8)),
            ("Fill_Light_Cool", (-4.5, -3.5, 3.2), 350, (0.75, 0.85, 1.0)),
            ("Rim_Light_Edge", (0.0, 4.5, 3.8), 500, (0.9, 0.95, 1.0)),
        ]
        for l_name, l_loc, l_power, l_color in lights_data:
            light_obj = scene.objects.get(l_name)
            if not light_obj:
                bpy.ops.object.light_add(type='AREA', radius=2.5, location=l_loc)
                light_obj = context.active_object
                light_obj.name = l_name
                light_obj.data.energy = l_power
                light_obj.data.color = l_color
                for c in light_obj.users_collection:
                    c.objects.unlink(light_obj)
                stage_col.objects.link(light_obj)

        # Cinema Camera
        cam = ensure_camera(scene)
        cam.location = Vector((0.0, -5.2, 1.55))
        cam.rotation_euler = Euler((math.radians(88), 0, 0), 'XYZ')
        cam.data.lens = 35.0

        # Enable Move Gizmo
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.show_gizmo = True
                        space.show_gizmo_object_translate = True

        self.report({'INFO'}, "Clean Director Stage ready: Floor, 3-Point Lighting & Cinema Camera active!")
        return {'FINISHED'}

class CINDY_OT_AddActor(bpy.types.Operator):
    bl_idname = "cindy.add_actor"
    bl_label = "Add Actor to Stage"
    bl_description = "Add a stylized actor mannequin with gaze indicator to stage your scene"
    actor_id: bpy.props.IntProperty(default=1)

    def execute(self, context):
        scene = context.scene
        actors_col = create_or_get_collection("Cindy_Actors")

        profiles = {
            1: ("Actor_1_Lead", (0.0, 2.5, 0.0), (0.95, 0.55, 0.15)),      # Warm Amber Lead
            2: ("Actor_2_Guest", (1.8, 1.8, 0.0), (0.15, 0.65, 0.95)),     # Cyan Guest
            3: ("Actor_3_Extra", (-1.8, 2.0, 0.0), (0.9, 0.25, 0.25)),     # Crimson
            4: ("Actor_4_Support", (0.0, 4.0, 0.0), (0.2, 0.8, 0.4)),      # Emerald Green
        }
        name, def_loc, color_rgb = profiles.get(self.actor_id, (f"Actor_{self.actor_id}", (0, 2, 0), (0.8, 0.8, 0.8)))

        body = scene.objects.get(f"{name}_Body")
        if not body:
            # Torso / Body (Capsule/Cylinder)
            bpy.ops.mesh.primitive_cylinder_add(radius=0.26, depth=1.1, location=(def_loc[0], def_loc[1], def_loc[2] + 0.6))
            body = context.active_object
            body.name = f"{name}_Body"

            mat = bpy.data.materials.new(name=f"Mat_{name}")
            mat.diffuse_color = (color_rgb[0], color_rgb[1], color_rgb[2], 1.0)
            body.data.materials.append(mat)

            # Head (Sphere)
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.19, location=(def_loc[0], def_loc[1], def_loc[2] + 1.42))
            head = context.active_object
            head.name = f"{name}_Head"
            head.data.materials.append(mat)
            head.parent = body

            # Gaze Visor (Small cone pointing forward -Y so director clearly sees actor facing direction)
            bpy.ops.mesh.primitive_cone_add(radius1=0.07, depth=0.20, location=(def_loc[0], def_loc[1] - 0.20, def_loc[2] + 1.42), rotation=(math.radians(90), 0, 0))
            visor = context.active_object
            visor.name = f"{name}_GazeVisor"
            mat_visor = bpy.data.materials.new(name=f"Mat_{name}_Visor")
            mat_visor.diffuse_color = (0.08, 0.08, 0.08, 1.0)
            visor.data.materials.append(mat_visor)
            visor.parent = body

            for c in body.users_collection: c.objects.unlink(body)
            for c in head.users_collection: c.objects.unlink(head)
            for c in visor.users_collection: c.objects.unlink(visor)
            actors_col.objects.link(body)
            actors_col.objects.link(head)
            actors_col.objects.link(visor)

            self.report({'INFO'}, f"Spawned {name} on stage!")
        else:
            self.report({'INFO'}, f"{name} selected!")

        bpy.ops.object.select_all(action='DESELECT')
        body.select_set(True)
        context.view_layer.objects.active = body
        return {'FINISHED'}

class CINDY_OT_AddProp(bpy.types.Operator):
    bl_idname = "cindy.add_prop"
    bl_label = "Add Prop"
    bl_description = "Add basic staging props (Table, Chair, Doorway) into your scene"
    prop_type: bpy.props.StringProperty(default='TABLE')

    def execute(self, context):
        scene = context.scene
        props_col = create_or_get_collection("Cindy_Props")

        if self.prop_type == 'TABLE':
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 1.5, 0.72))
            prop = context.active_object
            prop.name = "Prop_Table"
            prop.scale = (1.5, 0.8, 0.06)
            bpy.ops.object.transform_apply(scale=True)
            mat = bpy.data.materials.new("Mat_Table")
            mat.diffuse_color = (0.28, 0.18, 0.12, 1.0)
            prop.data.materials.append(mat)

        elif self.prop_type == 'CHAIR':
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 2.1, 0.45))
            prop = context.active_object
            prop.name = "Prop_Chair"
            prop.scale = (0.45, 0.45, 0.05)
            bpy.ops.object.transform_apply(scale=True)
            mat = bpy.data.materials.new("Mat_Chair")
            mat.diffuse_color = (0.18, 0.18, 0.22, 1.0)
            prop.data.materials.append(mat)

        elif self.prop_type == 'DOORWAY':
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-2.5, 3.0, 1.3))
            prop = context.active_object
            prop.name = "Prop_DoorWall"
            prop.scale = (1.8, 0.2, 2.6)
            bpy.ops.object.transform_apply(scale=True)
            mat = bpy.data.materials.new("Mat_Wall")
            mat.diffuse_color = (0.5, 0.5, 0.55, 1.0)
            prop.data.materials.append(mat)

        for c in prop.users_collection:
            c.objects.unlink(prop)
        props_col.objects.link(prop)

        bpy.ops.object.select_all(action='DESELECT')
        prop.select_set(True)
        context.view_layer.objects.active = prop
        self.report({'INFO'}, f"Added {prop.name} to stage!")
        return {'FINISHED'}

# =============================================================================
# OPERATORS: EFFORTLESS ELEMENT MOVEMENT & ORIENTATION
# =============================================================================

class CINDY_OT_SnapToFloor(bpy.types.Operator):
    bl_idname = "cindy.snap_to_floor"
    bl_label = "Drop to Floor (Z=0)"
    bl_description = "Snap the bottom of the selected actor or prop directly onto the ground (Z=0)"

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type == 'CAMERA':
            self.report({'WARNING'}, "Select an actor or prop first!")
            return {'CANCELLED'}

        if obj.type == 'MESH':
            bbox_corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
            min_z = min([c.z for c in bbox_corners])
            obj.location.z -= min_z
            context.view_layer.update()
            self.report({'INFO'}, f"Dropped {obj.name} cleanly to floor (Z=0)")
        return {'FINISHED'}

class CINDY_OT_TurnObject(bpy.types.Operator):
    bl_idname = "cindy.turn_object"
    bl_label = "Turn Object"
    bl_description = "Rotate selected actor or prop in 45 or 180 degree steps"
    angle_deg: bpy.props.FloatProperty(default=45.0)

    def execute(self, context):
        obj = context.active_object
        if not obj:
            self.report({'WARNING'}, "Select an actor or prop first!")
            return {'CANCELLED'}

        obj.rotation_euler.z += math.radians(self.angle_deg)
        self.report({'INFO'}, f"Rotated {obj.name} by {int(self.angle_deg)} deg")
        return {'FINISHED'}

class CINDY_OT_FaceTarget(bpy.types.Operator):
    bl_idname = "cindy.face_target"
    bl_label = "Turn to Face Target"
    bl_description = "Turn the selected actor to look directly at another actor or the camera"
    target_type: bpy.props.StringProperty(default='OTHER_ACTOR')

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type == 'CAMERA':
            self.report({'WARNING'}, "Select an actor first!")
            return {'CANCELLED'}

        target_pos = None
        if self.target_type == 'CAMERA':
            cam = ensure_camera(context.scene)
            target_pos = cam.location.copy()
        else:
            # Find the other actor
            for o in context.scene.objects:
                if o != obj and "Actor_" in o.name and "_Body" in o.name:
                    target_pos = o.location.copy()
                    break

        if not target_pos:
            target_pos = Vector((0, 0, 1.2))

        dx = target_pos.x - obj.location.x
        dy = target_pos.y - obj.location.y
        obj.rotation_euler.z = math.atan2(dx, -dy)
        self.report({'INFO'}, f"{obj.name} turned to face target!")
        return {'FINISHED'}

class CINDY_OT_ToggleGizmo(bpy.types.Operator):
    bl_idname = "cindy.toggle_gizmo"
    bl_label = "Toggle 3D Move Arrows"
    bl_description = "Show or hide 3D move and rotate arrows to freely drag actors with mouse"

    def execute(self, context):
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.show_gizmo = True
                        curr = space.show_gizmo_object_translate
                        space.show_gizmo_object_translate = not curr
                        space.show_gizmo_object_rotate = not curr
                        self.report({'INFO'}, f"3D Move/Rotate Arrows: {'ON' if not curr else 'OFF'}")
        return {'FINISHED'}

# =============================================================================
# OPERATORS: CAMERA FREEDOM, FRAMING & TARGET LOCK
# =============================================================================

class CINDY_OT_ToggleCameraView(bpy.types.Operator):
    bl_idname = "cindy.toggle_camera_view"
    bl_label = "Toggle Camera View"
    bl_description = "Switch between looking through the cinema lens and free 3D orbit view"

    def execute(self, context):
        ensure_camera(context.scene)
        bpy.ops.view3d.view_camera()
        return {'FINISHED'}

class CINDY_OT_WalkNavigation(bpy.types.Operator):
    bl_idname = "cindy.walk_navigation"
    bl_label = "Fly / Walk Mode (WASD)"
    bl_description = "Walk through the scene like a first-person video game: W/A/S/D to move, Mouse to look around"

    def execute(self, context):
        bpy.ops.view3d.walk('INVOKE_DEFAULT')
        return {'FINISHED'}

class CINDY_OT_AlignCamToView(bpy.types.Operator):
    bl_idname = "cindy.align_cam_to_view"
    bl_label = "Snap Camera to My View"
    bl_description = "Move active cinema camera to match your current viewport viewpoint immediately"

    def execute(self, context):
        cam = ensure_camera(context.scene)
        bpy.ops.view3d.camera_to_view()
        self.report({'INFO'}, "Camera moved to your current viewpoint!")
        return {'FINISHED'}

class CINDY_OT_LockCameraAim(bpy.types.Operator):
    bl_idname = "cindy.lock_camera_aim"
    bl_label = "Lock Camera Aim to Selected"
    bl_description = "Keep camera continuously aimed at selected actor while you drag camera anywhere"

    def execute(self, context):
        cam = ensure_camera(context.scene)
        target_obj = context.active_object
        if not target_obj or target_obj == cam:
            target_obj = context.scene.objects.get("Actor_1_Lead_Body") or context.scene.objects.get("Actor_1_Body")
        if not target_obj:
            self.report({'WARNING'}, "Select an actor or target first!")
            return {'CANCELLED'}

        track = cam.constraints.get("Cindy_Track_To")
        if not track:
            track = cam.constraints.new(type='TRACK_TO')
            track.name = "Cindy_Track_To"
            track.track_axis = 'TRACK_NEGATIVE_Z'
            track.up_axis = 'UP_Y'
        track.target = target_obj
        context.view_layer.update()
        self.report({'INFO'}, f"Camera locked onto target: {target_obj.name}")
        return {'FINISHED'}

class CINDY_OT_UnlockCameraAim(bpy.types.Operator):
    bl_idname = "cindy.unlock_camera_aim"
    bl_label = "Free / Unlock Camera Aim"
    bl_description = "Bake current camera angle and remove tracking constraint for manual rotation"

    def execute(self, context):
        cam = ensure_camera(context.scene)
        track = cam.constraints.get("Cindy_Track_To")
        if track:
            cam.rotation_euler = cam.matrix_world.to_euler()
            cam.constraints.remove(track)
            context.view_layer.update()
            self.report({'INFO'}, "Camera aim unlocked! Free rotation restored.")
        else:
            self.report({'INFO'}, "Camera aim is already unlocked.")
        return {'FINISHED'}

class CINDY_OT_FrameShot(bpy.types.Operator):
    bl_idname = "cindy.frame_shot"
    bl_label = "Director Framing Preset"
    bl_description = "Instantly position and angle camera for standard cinema coverage"
    shot_type: bpy.props.StringProperty(default='TWO_SHOT')

    def execute(self, context):
        scene = context.scene
        cam = ensure_camera(scene)

        # Unlock tracking so presets position freely
        track = cam.constraints.get("Cindy_Track_To")
        if track:
            cam.constraints.remove(track)

        a1 = scene.objects.get("Actor_1_Lead_Body") or scene.objects.get("Actor_1_Body") or scene.objects.get("Character_Body")
        a2 = scene.objects.get("Actor_2_Guest_Body") or scene.objects.get("Actor_2_Body")

        p1 = a1.location.copy() if a1 else Vector((0.0, 2.5, 0.6))
        p2 = a2.location.copy() if a2 else Vector((1.8, 1.8, 0.6))

        # 1. TWO SHOT
        if self.shot_type == 'TWO_SHOT':
            mid = (p1 + p2) * 0.5
            mid.z = 1.3
            cam.location = mid + Vector((-0.4, -4.2, 0.25))
            direction = mid - cam.location
            cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
            cam.data.lens = 35.0
            self.report({'INFO'}, "Framed: Balanced Cinema Two-Shot (35mm)")

        # 2. OTS: 1 TO 2
        elif self.shot_type == 'OTS_1_TO_2':
            cam.location = p1 + Vector((-0.45, -0.85, 0.75))
            target = p2 + Vector((0, 0, 0.7))
            direction = target - cam.location
            cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
            cam.data.lens = 50.0
            self.report({'INFO'}, "Framed: Over-the-Shoulder Actor 1 -> 2 (50mm)")

        # 3. OTS: 2 TO 1 (REVERSE)
        elif self.shot_type == 'OTS_2_TO_1':
            cam.location = p2 + Vector((0.45, -0.85, 0.75))
            target = p1 + Vector((0, 0, 0.7))
            direction = target - cam.location
            cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
            cam.data.lens = 50.0
            self.report({'INFO'}, "Framed: Reverse OTS Actor 2 -> 1 (50mm)")

        # 4. CLOSE UP TARGET
        elif self.shot_type == 'CLOSE_UP':
            target = get_target_location(scene) + Vector((0, 0, 0.25))
            cam.location = target + Vector((0.0, -1.8, 0.05))
            direction = target - cam.location
            cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
            cam.data.lens = 85.0
            self.report({'INFO'}, "Framed: Dramatic Close-Up (85mm Prime)")

        # 5. MEDIUM SHOT
        elif self.shot_type == 'MEDIUM_SHOT':
            target = get_target_location(scene) + Vector((0, 0, 0.1))
            cam.location = target + Vector((0.0, -3.0, 0.2))
            direction = target - cam.location
            cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
            cam.data.lens = 50.0
            self.report({'INFO'}, "Framed: Cinema Medium Shot (50mm Prime)")

        # 6. WIDE MASTER
        elif self.shot_type == 'WIDE':
            mid = (p1 + p2) * 0.5
            mid.z = 1.0
            cam.location = mid + Vector((0.0, -7.5, 3.2))
            direction = mid - cam.location
            cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
            cam.data.lens = 24.0
            self.report({'INFO'}, "Framed: Wide Master Establishing Shot (24mm Prime)")

        return {'FINISHED'}

class CINDY_OT_SetLens(bpy.types.Operator):
    bl_idname = "cindy.set_lens"
    bl_label = "Set Cinema Prime Lens"
    bl_description = "Switch camera focal length to industry cinema primes"
    lens: bpy.props.FloatProperty(name="Focal Length", default=50.0)

    def execute(self, context):
        cam = ensure_camera(context.scene)
        cam.data.lens = self.lens
        self.report({'INFO'}, f"Lens set to {int(self.lens)}mm Cinema Prime")
        return {'FINISHED'}

# =============================================================================
# OPERATORS: INFINITE MULTI-BEAT KEYFRAME CHOREOGRAPHER
# =============================================================================

class CINDY_OT_RecordStartBeat(bpy.types.Operator):
    bl_idname = "cindy.record_start_beat"
    bl_label = "Set Shot Start (Frame 1)"
    bl_description = "Lock the current camera position as Beat 1 (Start of shot at 0.0s)"

    def execute(self, context):
        scene = context.scene
        cam = ensure_camera(scene)

        # Clear existing animation to start fresh
        if cam.animation_data:
            cam.animation_data_clear()

        scene.frame_start = 1
        scene.frame_current = 1
        scene.frame_end = 1
        scene.cindy_beat_count = 1

        cam.keyframe_insert("location", frame=1)
        cam.keyframe_insert("rotation_euler", frame=1)
        cam.data.keyframe_insert("lens", frame=1)

        self.report({'INFO'}, "Beat 1 (Start) recorded at Frame 1 (0.0s)!")
        return {'FINISHED'}

class CINDY_OT_RecordNextBeat(bpy.types.Operator):
    bl_idname = "cindy.record_next_beat"
    bl_label = "Record Next Beat (Append)"
    bl_description = "Move camera to your next angle, set duration and style, and click to append to shot sequence"

    def execute(self, context):
        scene = context.scene
        cam = ensure_camera(scene)

        fps = scene.render.fps
        duration_sec = scene.cindy_beat_duration
        duration_frames = max(4, int(duration_sec * fps))

        prev_frame = scene.frame_current
        next_frame = prev_frame + duration_frames

        cam.keyframe_insert("location", frame=next_frame)
        cam.keyframe_insert("rotation_euler", frame=next_frame)
        cam.data.keyframe_insert("lens", frame=next_frame)

        # Apply interpolation style to the new segment
        style = scene.cindy_transition_style
        if cam.animation_data and cam.animation_data.action:
            for fc in cam.animation_data.action.fcurves:
                for kp in fc.keyframe_points:
                    if kp.co[0] >= prev_frame and kp.co[0] <= next_frame:
                        if style == 'SMOOTH':
                            kp.interpolation = 'BEZIER'
                            kp.easing = 'EASE_IN_OUT'
                        elif style == 'WHIP':
                            kp.interpolation = 'BEZIER'
                            kp.easing = 'EASE_IN'
                        elif style == 'LINEAR':
                            kp.interpolation = 'LINEAR'

        scene.frame_end = next_frame
        scene.frame_current = next_frame
        scene.cindy_beat_count += 1

        total_sec = round(next_frame / fps, 1)
        self.report({'INFO'}, f"Beat {scene.cindy_beat_count} recorded at {total_sec}s (+{round(duration_sec, 1)}s, {style})")
        return {'FINISHED'}

class CINDY_OT_PlayShot(bpy.types.Operator):
    bl_idname = "cindy.play_shot"
    bl_label = "Play / Preview Shot"
    bl_description = "Play the choreographed camera movement from start to end"

    def execute(self, context):
        context.scene.frame_current = context.scene.frame_start
        bpy.ops.screen.animation_play()
        return {'FINISHED'}

class CINDY_OT_ResetTimeline(bpy.types.Operator):
    bl_idname = "cindy.reset_timeline"
    bl_label = "Clear Timeline Animation"
    bl_description = "Clear all camera keyframes and reset timeline to fresh shot"

    def execute(self, context):
        cam = context.scene.camera
        if cam and cam.animation_data:
            cam.animation_data_clear()
        context.scene.frame_current = 1
        context.scene.frame_start = 1
        context.scene.frame_end = 120
        context.scene.cindy_beat_count = 0
        context.scene.cindy_sequence_count = 0
        self.report({'INFO'}, "Cleared all camera movements. Timeline reset to clean state!")
        return {'FINISHED'}

# =============================================================================
# OPERATORS: PRESET COMPOUND MOVES (WORK ON ANY TARGET)
# =============================================================================

class CINDY_OT_ApplyCompoundMove(bpy.types.Operator):
    bl_idname = "cindy.apply_compound_move"
    bl_label = "Apply Compound Move"
    bl_description = "Generate a professional compound camera movement on the timeline"

    def execute(self, context):
        scene = context.scene
        cam = ensure_camera(scene)

        fps = scene.render.fps
        move_type = scene.cindy_compound_move
        duration_sec = scene.cindy_compound_duration
        chain_mode = scene.cindy_chain_mode
        frames_count = max(5, int(duration_sec * fps))

        tgt = get_target_location(scene)

        # Timeline setup
        if not chain_mode or not cam.animation_data or not cam.animation_data.action:
            cam.animation_data_clear()
            f_start = 1
            f_end = 1 + frames_count
            scene.frame_start = 1
            scene.frame_end = f_end
            scene.cindy_sequence_count = 1
        else:
            f_start = scene.frame_end
            f_end = f_start + frames_count
            scene.frame_end = f_end
            scene.cindy_sequence_count += 1

        scene.frame_current = f_start

        # Helper for exact per-frame spherical arc + exact target tracking
        def bake_spherical_trajectory(pos_start, look_start, lens_start, pos_end, look_end, lens_end, roll_start_deg=0.0, roll_end_deg=0.0, ease_mode='SMOOTH'):
            rel_a = pos_start - look_start
            rel_b = pos_end - look_end
            r_a = math.hypot(rel_a.x, rel_a.y)
            r_b = math.hypot(rel_b.x, rel_b.y)
            theta_a = math.atan2(rel_a.x, -rel_a.y)
            theta_b = math.atan2(rel_b.x, -rel_b.y)
            d_theta = (theta_b - theta_a + math.pi) % (2.0 * math.pi) - math.pi
            if move_type == 'HERO_ORBIT_360':
                d_theta = 2.0 * math.pi
            elif move_type == 'HERO_ARC_180':
                d_theta = math.pi

            for f in range(f_start, f_end + 1):
                raw_t = (f - f_start) / float(max(1, f_end - f_start))
                if ease_mode == 'WHIP':
                    u = raw_t * raw_t * (3.0 - 2.0 * raw_t) ** 2
                else:
                    # Quintic zero-jerk smoothstep
                    u = raw_t * raw_t * raw_t * (raw_t * (raw_t * 6.0 - 15.0) + 10.0)

                l_curr = look_start.lerp(look_end, u)
                if r_a > 0.2 and r_b > 0.2 and (r_a / r_b > 2.5 or r_b / r_a > 2.5):
                    r_curr = math.exp(math.log(r_a) + (math.log(r_b) - math.log(r_a)) * u)
                else:
                    r_curr = r_a + (r_b - r_a) * u

                th_curr = theta_a + d_theta * u
                z_curr = rel_a.z + (rel_b.z - rel_a.z) * u

                c_pos = Vector((
                    l_curr.x + r_curr * math.sin(th_curr),
                    l_curr.y - r_curr * math.cos(th_curr),
                    max(0.18, l_curr.z + z_curr)
                ))
                cam.location = c_pos
                cam.data.lens = lens_start + (lens_end - lens_start) * u

                direction = l_curr - c_pos
                if direction.length > 0.001:
                    eul = direction.to_track_quat('-Z', 'Y').to_euler('XYZ')
                else:
                    eul = cam.rotation_euler.copy()

                roll_deg = roll_start_deg + (roll_end_deg - roll_start_deg) * u
                eul.y += math.radians(roll_deg)
                cam.rotation_euler = eul

                cam.keyframe_insert("location", frame=f)
                cam.keyframe_insert("rotation_euler", frame=f)
                cam.data.keyframe_insert("lens", frame=f)

        eye_tgt = tgt + Vector((0.0, 0.0, 0.35))
        chest_tgt = tgt + Vector((0.0, 0.0, 0.15))

        # 1. CRANE DOWN + PUSH IN
        if move_type == 'CRANE_PUSH_IN':
            bake_spherical_trajectory(
                eye_tgt + Vector((-1.6, -4.5, 2.2)), chest_tgt, 32.0,
                eye_tgt + Vector((-0.15, -1.05, 0.02)), eye_tgt, 65.0
            )

        # 2. CRANE UP + PULL OUT (REVEAL)
        elif move_type == 'CRANE_PULL_OUT':
            bake_spherical_trajectory(
                eye_tgt + Vector((0.0, -1.05, 0.02)), eye_tgt, 65.0,
                eye_tgt + Vector((0.0, -6.5, 3.6)), chest_tgt, 24.0
            )

        # 3. COSMIC WINDOW DIVE -> EXTREME CLOSE-UP
        elif move_type == 'SPACE_WINDOW_DIVE':
            bake_spherical_trajectory(
                eye_tgt + Vector((0.0, -12.0, 6.5)), eye_tgt, 18.0,
                eye_tgt + Vector((0.0, -0.68, 0.01)), eye_tgt, 85.0
            )

        # 4. WHIP PAN RIGHT
        elif move_type == 'WHIP_PAN_RIGHT':
            rot_curr = cam.rotation_euler.copy()
            for f in range(f_start, f_end + 1):
                raw_t = (f - f_start) / float(max(1, f_end - f_start))
                u = raw_t * raw_t * (3.0 - 2.0 * raw_t) ** 2
                cam.rotation_euler = Euler((rot_curr.x, rot_curr.y, rot_curr.z - math.radians(85.0 * u)), 'XYZ')
                cam.keyframe_insert("rotation_euler", frame=f)
                cam.keyframe_insert("location", frame=f)

        # 5. WHIP PAN LEFT
        elif move_type == 'WHIP_PAN_LEFT':
            rot_curr = cam.rotation_euler.copy()
            for f in range(f_start, f_end + 1):
                raw_t = (f - f_start) / float(max(1, f_end - f_start))
                u = raw_t * raw_t * (3.0 - 2.0 * raw_t) ** 2
                cam.rotation_euler = Euler((rot_curr.x, rot_curr.y, rot_curr.z + math.radians(85.0 * u)), 'XYZ')
                cam.keyframe_insert("rotation_euler", frame=f)
                cam.keyframe_insert("location", frame=f)

        # 6. VERTIGO / HITCHCOCK DOLLY ZOOM (Mathematically Locked Subject Framing: Distance / FocalLength = Constant)
        elif move_type == 'VERTIGO_DOLLY_ZOOM':
            d_start = 5.2
            lens_start = 85.0
            ratio_k = d_start / lens_start
            d_end = 1.65
            for f in range(f_start, f_end + 1):
                raw_t = (f - f_start) / float(max(1, f_end - f_start))
                u = raw_t * raw_t * raw_t * (raw_t * (raw_t * 6.0 - 15.0) + 10.0)
                d_curr = d_start + (d_end - d_start) * u
                lens_curr = d_curr / ratio_k
                c_pos = eye_tgt + Vector((0.0, -d_curr, 0.04))
                cam.location = c_pos
                cam.data.lens = lens_curr
                direction = eye_tgt - c_pos
                cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler('XYZ')
                cam.keyframe_insert("location", frame=f)
                cam.keyframe_insert("rotation_euler", frame=f)
                cam.data.keyframe_insert("lens", frame=f)

        # 7. 180 DEGREE DRAMATIC ARC REVEAL
        elif move_type == 'HERO_ARC_180':
            r = 2.4
            bake_spherical_trajectory(
                eye_tgt + Vector((-r, 0.0, 0.12)), eye_tgt, 40.0,
                eye_tgt + Vector((r, 0.0, 0.05)), eye_tgt, 50.0
            )

        # 8. 360 FULL HERO ORBIT
        elif move_type == 'HERO_ORBIT_360':
            r = 2.6
            bake_spherical_trajectory(
                eye_tgt + Vector((0.0, -r, 0.15)), eye_tgt, 40.0,
                eye_tgt + Vector((0.0, -r, 0.15)), eye_tgt, 40.0
            )

        # 9. LOW DUTCH CREEP (NOIR TENSION)
        elif move_type == 'DUTCH_CREEP':
            bake_spherical_trajectory(
                chest_tgt + Vector((-1.6, -4.8, -0.45)), eye_tgt, 28.0,
                chest_tgt + Vector((-0.6, -1.8, -0.25)), eye_tgt, 38.0,
                roll_start_deg=-15.0, roll_end_deg=-9.0
            )

        # 10. PARALLAX REVEAL PAST PILLARS
        elif move_type == 'PARALLAX_PILLARS':
            bake_spherical_trajectory(
                eye_tgt + Vector((2.6, -3.8, 0.15)), eye_tgt, 45.0,
                eye_tgt + Vector((-2.2, -3.4, 0.10)), eye_tgt, 50.0
            )

        # Auto-play preview
        context.scene.frame_current = f_start
        try:
            bpy.ops.screen.animation_play()
        except Exception:
            pass

        move_dict = dict([(it[0], it[1]) for it in COMPOUND_MOVE_ITEMS])
        move_name = move_dict.get(move_type, move_type)
        self.report({'INFO'}, f"Applied: {move_name} ({round(duration_sec, 1)}s)")
        return {'FINISHED'}

# =============================================================================
# OPERATORS: EXPORT & SCENE PRESETS
# =============================================================================

def _cindy_subject_meshes(scene):
    """Meshes that define the shot's depth range: everything renderable except the stage floor."""
    out = []
    for o in scene.objects:
        if o.type != 'MESH' or o.hide_render:
            continue
        if o.name == "Studio_Floor":
            continue
        out.append(o)
    return out


def _cindy_shot_depth_range(camera, meshes, min_margin=0.1, margin_ratio=0.1):
    """Near/far (metres, camera space) fitted to the subject so the depth map uses its full contrast."""
    clip_near = camera.data.clip_start
    clip_far = min(camera.data.clip_end, 50.0)
    if not meshes:
        return clip_near, min(clip_far, 20.0)
    dg = bpy.context.evaluated_depsgraph_get()
    inv = camera.matrix_world.inverted()
    zs = []
    for m in meshes:
        ev = m.evaluated_get(dg)
        mw = ev.matrix_world
        for corner in ev.bound_box:
            zs.append(-(inv @ (mw @ Vector(corner))).z)
    zs = [z for z in zs if z > 0.01]
    if not zs:
        return clip_near, min(clip_far, 20.0)
    near, far = min(zs), max(zs)
    margin = max(min_margin, (far - near) * margin_ratio)
    return max(clip_near, near - margin), min(clip_far, far + margin)


def _cindy_render_depth_png(scene, depth_path, near, far):
    """Linear depth, white = near / black = far, fixed range (no per-frame normalisation).

    Blender 5.x removed Scene.node_tree, so this uses a material override + EEVEE instead of the
    compositor. It works on 4.2+ and 5.x. Every scene setting touched here is restored afterwards.
    """
    view_layer = bpy.context.view_layer
    r = scene.render
    saved = {
        "engine": r.engine,
        "filepath": r.filepath,
        "fmt": r.image_settings.file_format,
        "color_mode": r.image_settings.color_mode,
        "color_depth": r.image_settings.color_depth,
        "view_transform": scene.view_settings.view_transform,
        "look": scene.view_settings.look,
        "world": scene.world,
        "override": view_layer.material_override,
        "samples": scene.eevee.taa_render_samples,
    }
    mat = None
    world = None
    try:
        mat = bpy.data.materials.new("CindyDepth_TMP")
        mat.use_nodes = True
        nt = mat.node_tree
        for n in list(nt.nodes):
            nt.nodes.remove(n)
        cam_data = nt.nodes.new('ShaderNodeCameraData')
        map_range = nt.nodes.new('ShaderNodeMapRange')
        map_range.clamp = True
        map_range.inputs['From Min'].default_value = near
        map_range.inputs['From Max'].default_value = far
        map_range.inputs['To Min'].default_value = 1.0
        map_range.inputs['To Max'].default_value = 0.0
        emit = nt.nodes.new('ShaderNodeEmission')
        out_node = nt.nodes.new('ShaderNodeOutputMaterial')
        nt.links.new(cam_data.outputs['View Z Depth'], map_range.inputs['Value'])
        nt.links.new(map_range.outputs['Result'], emit.inputs['Color'])
        nt.links.new(emit.outputs['Emission'], out_node.inputs['Surface'])
        view_layer.material_override = mat

        world = bpy.data.worlds.new("CindyDepthBlack_TMP")
        world.use_nodes = True
        bg = world.node_tree.nodes.get('Background')
        if bg:
            bg.inputs['Color'].default_value = (0.0, 0.0, 0.0, 1.0)
            bg.inputs['Strength'].default_value = 1.0
        scene.world = world

        r.engine = 'BLENDER_EEVEE'
        scene.eevee.taa_render_samples = 1
        scene.view_settings.view_transform = 'Standard'
        scene.view_settings.look = 'None'
        r.image_settings.file_format = 'PNG'
        r.image_settings.color_mode = 'BW'
        r.image_settings.color_depth = '8'   # 8-bit: safe for PIL/Fal pipelines (16-bit gray gets clipped by PIL.convert)
        r.filepath = depth_path
        bpy.ops.render.render(write_still=True)
        return os.path.exists(depth_path)
    except Exception as e:
        print("Cindy depth render error:", e)
        return False
    finally:
        view_layer.material_override = saved["override"]
        scene.world = saved["world"]
        r.engine = saved["engine"]
        r.filepath = saved["filepath"]
        r.image_settings.file_format = saved["fmt"]
        r.image_settings.color_mode = saved["color_mode"]
        r.image_settings.color_depth = saved["color_depth"]
        scene.view_settings.view_transform = saved["view_transform"]
        scene.view_settings.look = saved["look"]
        scene.eevee.taa_render_samples = saved["samples"]
        if mat:
            bpy.data.materials.remove(mat)
        if world:
            bpy.data.worlds.remove(world)


def export_cindy_guides(context):
    scene = context.scene
    camera = ensure_camera(scene)

    out_dir = ensure_output_dir()
    timestamp = int(time.time())
    current_frame = scene.frame_current

    cam_data = camera.data
    cam_meta = {
        "timestamp": timestamp,
        "frame": current_frame,
        "lens_focal_length_mm": round(getattr(cam_data, 'lens', 50.0), 1),
        "sensor_width_mm": round(cam_data.sensor_width, 1),
        "camera_location": [round(v, 2) for v in camera.location],
        "camera_rotation_euler": [round(v, 2) for v in camera.rotation_euler],
        "aspect_ratio": f"{scene.render.resolution_x}:{scene.render.resolution_y}",
        "resolution": [scene.render.resolution_x, scene.render.resolution_y],
        "clip_start": cam_data.clip_start,
        "clip_end": cam_data.clip_end,
    }

    subject_meshes = _cindy_subject_meshes(scene)
    depth_near, depth_far = _cindy_shot_depth_range(camera, subject_meshes)
    cam_meta["depth_near_m"] = round(depth_near, 3)
    cam_meta["depth_far_m"] = round(depth_far, 3)
    cam_meta["depth_convention"] = "white=near, black=far, linear metres, fixed range per export"

    meta_file = os.path.join(out_dir, f"blender_guide_{timestamp}_meta.json")
    with open(meta_file, 'w', encoding='utf-8') as f:
        json.dump(cam_meta, f, indent=2, ensure_ascii=False)

    guide_file = os.path.join(out_dir, f"blender_guide_{timestamp}_rgb.jpg")
    orig_filepath = scene.render.filepath
    orig_file_format = scene.render.image_settings.file_format
    orig_engine = scene.render.engine

    try:
        scene.render.engine = 'BLENDER_WORKBENCH'
        scene.render.filepath = guide_file
        scene.render.image_settings.file_format = 'JPEG'
        scene.render.image_settings.quality = 90
        bpy.ops.render.render(write_still=True)
    except Exception as e:
        print("RGB Snapshot Error:", e)
    finally:
        scene.render.filepath = orig_filepath
        scene.render.image_settings.file_format = orig_file_format
        scene.render.engine = orig_engine

    depth_file = os.path.join(out_dir, f"blender_guide_{timestamp}_depth.png")
    depth_ok = _cindy_render_depth_png(scene, depth_file, depth_near, depth_far)
    if not depth_ok:
        return {"success": False, "error": "Depth render failed - see Blender console. RGB guide was saved."}

    return {
        "success": True,
        "timestamp": timestamp,
        "meta": cam_meta,
        "rgb_guide": guide_file,
        "depth_guide": depth_file,
        "directory": out_dir
    }

class CINDY_OT_ExportGuides(bpy.types.Operator):
    bl_idname = "cindy.export_guides"
    bl_label = "Export to Cindy AI (RGB + Depth)"
    bl_description = "Export 3D depth map, viewport framing and camera metadata to Cindy AI Director"

    def execute(self, context):
        res = export_cindy_guides(context)
        if res.get("success"):
            self.report({'INFO'}, f"Exported successfully! (Frame: {context.scene.frame_current})")
        else:
            self.report({'ERROR'}, res.get("error", "Export failed"))
        return {'FINISHED'}

class CINDY_OT_OpenCompoundScene(bpy.types.Operator):
    bl_idname = "cindy.open_compound_scene"
    bl_label = "Load Alley Compound Scene"
    bl_description = "Open the 3D cyber-noir alley compound camera trajectory scene"

    def execute(self, context):
        if os.path.exists(SCENE_PRESET_PATH):
            bpy.ops.wm.open_mainfile(filepath=SCENE_PRESET_PATH)
            self.report({'INFO'}, "Compound Shot Scene Loaded Successfully!")
        else:
            self.report({'ERROR'}, f"Scene file not found: {SCENE_PRESET_PATH}")
        return {'FINISHED'}

# =============================================================================
# DIRECTOR PANEL UI (100% CLEAN ENGLISH LABELS)
# =============================================================================


CHARACTER_LIBRARY_DIR = r"C:\Users\DELL\Downloads\شخصيات_المشروع"

CHARACTER_ITEMS = [
    ('1_عبدالعزيز\\المرحلة_1_الشاب', "1. Abdelaziz (Young - Afro)", "Young Abdelaziz character folder"),
    ('1_عبدالعزيز\\المرحلة_2_العجوز', "2. Abdelaziz (Mature / Disco)", "Mature Abdelaziz character folder"),
    ('2_عبدالشكور\\المرحلة_1_الشاب', "3. Abdelshakoor (Young)", "Young Abdelshakoor character folder"),
    ('2_عبدالشكور\\المرحلة_2_العجوز', "4. Abdelshakoor (Mature)", "Mature Abdelshakoor character folder"),
]

def _get_character_motion_items(self, context):
    items = []
    sub = getattr(context.scene, "cindy_char_folder", '1_عبدالعزيز\\المرحلة_1_الشاب')
    folder = os.path.join(CHARACTER_LIBRARY_DIR, sub)
    if os.path.exists(folder):
        for f in sorted(os.listdir(folder)):
            if f.lower().endswith('.fbx'):
                items.append((f, f[:-4], f"Load motion {f}"))
    if not items:
        items.append(('NONE', "No FBX Found", "No FBX files in directory"))
    return items


class CINDY_OT_LoadProjectCharacter(bpy.types.Operator):
    bl_idname = "cindy.load_project_character"
    bl_label = "Load Character & Motion (Clean Mixamo)"
    bl_description = "Import selected character FBX, strip unwanted embedded Tripo actions, lock Mixamo clip, and optimize 1024px VRAM textures"

    def execute(self, context):
        scene = context.scene
        sub = scene.cindy_char_folder
        fbx_file = scene.cindy_char_motion
        if not fbx_file or fbx_file == 'NONE':
            self.report({'ERROR'}, "No valid FBX motion selected!")
            return {'CANCELLED'}

        full_path = os.path.join(CHARACTER_LIBRARY_DIR, sub, fbx_file)
        if not os.path.exists(full_path):
            self.report({'ERROR'}, f"File not found: {full_path}")
            return {'CANCELLED'}

        # Record existing objects and actions before import
        old_objs = set(bpy.data.objects)
        old_actions = set(bpy.data.actions)

        bpy.ops.import_scene.fbx(filepath=full_path)

        new_objs = [o for o in bpy.data.objects if o not in old_objs]
        new_actions = [a for a in bpy.data.actions if a not in old_actions]

        # Find imported armature and mesh
        arm = next((o for o in new_objs if o.type == 'ARMATURE'), None)
        meshes = [o for o in new_objs if o.type == 'MESH']

        # Clean up unwanted built-in Tripo actions (keep only mixamo.com action if multiple exist)
        if arm and len(new_actions) > 1:
            mixamo_act = next((a for a in new_actions if 'mixamo' in a.name.lower()), None)
            if not mixamo_act:
                # Pick shortest specific clip rather than 696-frame default dance
                mixamo_act = min(new_actions, key=lambda a: a.frame_range[1] - a.frame_range[0])
            if arm.animation_data:
                arm.animation_data.action = mixamo_act
            for a in new_actions:
                if a != mixamo_act:
                    bpy.data.actions.remove(a, do_unlink=True)

        # Fit scene timeline to active action and snap feet to floor
        if arm and arm.animation_data and arm.animation_data.action:
            act = arm.animation_data.action
            scene.frame_start = max(1, int(act.frame_range[0]))
            scene.frame_end = max(2, int(act.frame_range[1]))
            scene.frame_current = scene.frame_start

            # Smooth keyframe interpolation for natural organic motion
            try:
                if hasattr(act, 'fcurves'):
                    for fc in act.fcurves:
                        for kp in fc.keyframe_points:
                            kp.interpolation = 'BEZIER'
            except Exception:
                pass

        # Optimize viewport texture VRAM limit to 1024px for smooth 30fps on Quadro P1000 (4GB)
        try:
            context.preferences.system.gl_texture_limit = 'CLAMP_1024'
        except Exception:
            pass

        # Ensure character stands cleanly on the floor (Z=0)
        if meshes:
            dg = context.evaluated_depsgraph_get()
            min_z = min(
                (m.evaluated_get(dg).matrix_world @ Vector(c)).z
                for m in meshes for c in m.evaluated_get(dg).bound_box
            )
            if arm:
                arm.location.z -= min_z
            else:
                for m in meshes:
                    m.location.z -= min_z

        self.report({'INFO'}, f"Loaded {fbx_file} ({scene.frame_end} frames) cleanly!")
        return {'FINISHED'}


class CINDY_OT_OptimizeViewportPerformance(bpy.types.Operator):
    bl_idname = "cindy.optimize_viewport_perf"
    bl_label = "Boost Viewport 30fps + Natural Camera Handheld"
    bl_description = "Optimize EEVEE & VRAM for Quadro P1000 4GB and add subtle organic handheld camera breathing"

    def execute(self, context):
        scene = context.scene
        cam = ensure_camera(scene)

        # 1. Hardware VRAM & EEVEE optimization for 4GB GPU
        try:
            context.preferences.system.gl_texture_limit = 'CLAMP_1024'
        except Exception:
            pass
        scene.eevee.taa_samples = 8
        scene.eevee.taa_render_samples = 16
        scene.render.fps = 30

        # 2. Configure 50mm f/2.0 Depth of Field on Cinema Camera
        cam.data.dof.use_dof = True
        cam.data.dof.aperture_fstop = 2.0
        cam.data.dof.focus_distance = 4.2

        self.report({'INFO'}, "Viewport optimized (1024px VRAM cap, 30fps, f/2.0 Cinema DoF active)!")
        return {'FINISHED'}


class CINDY_PT_DirectorPanel(bpy.types.Panel):
    bl_label = "Cindy AI Director"
    bl_idname = "CINDY_PT_director_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Cindy Director'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        cam = scene.camera

        # ---------------------------------------------------------------------
        # 1. Virtual Stage Setup
        # ---------------------------------------------------------------------
        box_stage = layout.box()
        box_stage.label(text="1. Virtual Stage Setup:", icon='SCENE_DATA')
        col_new = box_stage.column(align=True)
        col_new.scale_y = 1.3
        col_new.operator("cindy.new_director_stage", text="🎬 New Clean Director Stage", icon='RESTRICT_RENDER_OFF')
        box_stage.operator("cindy.open_compound_scene", text="Load Alley Preset Scene", icon='FILE_FOLDER')
        box_stage.operator("cindy.optimize_viewport_perf", text="⚡ Boost 30fps Performance (Quadro 4GB)", icon='SHADING_RENDERED')

        layout.separator()

        # ---------------------------------------------------------------------
        # 1B. Project Characters & Mixamo Motions (Abdelaziz & Abdelshakoor)
        # ---------------------------------------------------------------------
        box_chars = layout.box()
        box_chars.label(text="Project Characters & Motions:", icon='ARMATURE_DATA')
        box_chars.prop(scene, "cindy_char_folder", text="Character")
        box_chars.prop(scene, "cindy_char_motion", text="Motion")
        col_load_char = box_chars.column(align=True)
        col_load_char.scale_y = 1.3
        col_load_char.operator("cindy.load_project_character", text="🎭 Import Character & Lock Motion", icon='IMPORT')

        layout.separator()

        # ---------------------------------------------------------------------
        # 2. Scene Staging (Actors & Props)
        # ---------------------------------------------------------------------
        box_actors = layout.box()
        box_actors.label(text="2. Scene Staging (Actors & Props):", icon='COMMUNITY')

        row_a = box_actors.row(align=True)
        op_a1 = row_a.operator("cindy.add_actor", text="+ Actor 1 (Amber)", icon='USER')
        op_a1.actor_id = 1
        op_a2 = row_a.operator("cindy.add_actor", text="+ Actor 2 (Cyan)", icon='USER')
        op_a2.actor_id = 2

        row_a2 = box_actors.row(align=True)
        op_a3 = row_a2.operator("cindy.add_actor", text="+ Actor 3 (Red)", icon='USER')
        op_a3.actor_id = 3
        op_a4 = row_a2.operator("cindy.add_actor", text="+ Actor 4 (Green)", icon='USER')
        op_a4.actor_id = 4

        row_props = box_actors.row(align=True)
        op_tbl = row_props.operator("cindy.add_prop", text="+ Table", icon='FILE_3D')
        op_tbl.prop_type = 'TABLE'
        op_chr = row_props.operator("cindy.add_prop", text="+ Chair", icon='SNAP_VERTEX')
        op_chr.prop_type = 'CHAIR'
        op_dor = row_props.operator("cindy.add_prop", text="+ Doorway", icon='MOD_BUILD')
        op_dor.prop_type = 'DOORWAY'

        # Element Positioning Tools
        box_actors.separator()
        box_actors.label(text="Selected Element Tools:")
        box_actors.operator("cindy.toggle_gizmo", text="🎯 Toggle 3D Move Arrows (Gizmo)", icon='EMPTY_ARROWS')

        row_pos = box_actors.row(align=True)
        row_pos.operator("cindy.snap_to_floor", text="⬇️ Drop to Floor (Z=0)", icon='SNAP_ON')

        row_turn = box_actors.row(align=True)
        op_tl = row_turn.operator("cindy.turn_object", text="🔄 -45° Left")
        op_tl.angle_deg = -45.0
        op_tr = row_turn.operator("cindy.turn_object", text="🔄 +45° Right")
        op_tr.angle_deg = 45.0
        op_t18 = row_turn.operator("cindy.turn_object", text="🔄 180° Flip")
        op_t18.angle_deg = 180.0

        row_face = box_actors.row(align=True)
        op_fa = row_face.operator("cindy.face_target", text="👀 Face Other Actor", icon='TRACKING')
        op_fa.target_type = 'OTHER_ACTOR'
        op_fc = row_face.operator("cindy.face_target", text="📷 Face Camera", icon='CAMERA_DATA')
        op_fc.target_type = 'CAMERA'

        layout.separator()

        # ---------------------------------------------------------------------
        # 3. Camera Freedom & View Controls
        # ---------------------------------------------------------------------
        box_cam = layout.box()
        box_cam.label(text="3. Camera Freedom & Navigation:", icon='VIEW_CAMERA')

        row_nav = box_cam.row(align=True)
        row_nav.operator("cindy.toggle_camera_view", text="👁️ Toggle Cam View", icon='RESTRICT_VIEW_OFF')
        row_nav.operator("cindy.walk_navigation", text="🕹️ Fly/Walk (WASD)", icon='HAND')

        col_snap = box_cam.column(align=True)
        col_snap.scale_y = 1.3
        col_snap.operator("cindy.align_cam_to_view", text="📷 Snap Camera to My Current View", icon='CAMERA_DATA')

        # Camera Aim Tracking
        row_aim = box_cam.row(align=True)
        row_aim.operator("cindy.lock_camera_aim", text="🎯 Aim at Selected Target", icon='LOCKED')
        row_aim.operator("cindy.unlock_camera_aim", text="🔓 Unlock Aim", icon='UNLOCKED')

        # Framing Presets
        box_cam.separator()
        box_cam.label(text="Instant Cinema Framing Presets:")
        row_f1 = box_cam.row(align=True)
        op_two = row_f1.operator("cindy.frame_shot", text="Two-Shot (Actors)")
        op_two.shot_type = 'TWO_SHOT'
        op_ots1 = row_f1.operator("cindy.frame_shot", text="OTS: 1 -> 2")
        op_ots1.shot_type = 'OTS_1_TO_2'
        op_ots2 = row_f1.operator("cindy.frame_shot", text="OTS: 2 -> 1")
        op_ots2.shot_type = 'OTS_2_TO_1'

        row_f2 = box_cam.row(align=True)
        op_cu = row_f2.operator("cindy.frame_shot", text="Close-Up Target")
        op_cu.shot_type = 'CLOSE_UP'
        op_med = row_f2.operator("cindy.frame_shot", text="Medium Shot")
        op_med.shot_type = 'MEDIUM_SHOT'
        op_wide = row_f2.operator("cindy.frame_shot", text="Wide Master")
        op_wide.shot_type = 'WIDE'

        # Cinema Prime Lenses
        box_cam.separator()
        row_lenses = box_cam.row(align=True)
        op24 = row_lenses.operator("cindy.set_lens", text="24mm Wide")
        op24.lens = 24.0
        op35 = row_lenses.operator("cindy.set_lens", text="35mm Story")
        op35.lens = 35.0
        op50 = row_lenses.operator("cindy.set_lens", text="50mm Prime")
        op50.lens = 50.0
        op85 = row_lenses.operator("cindy.set_lens", text="85mm Portrait")
        op85.lens = 85.0

        if cam:
            box_cam.label(text=f"Active Lens: {round(cam.data.lens, 1)}mm Cinema Prime", icon='CHECKMARK')

        layout.separator()

        # ---------------------------------------------------------------------
        # 4. Multi-Beat Keyframe Choreographer (Infinite Freedom)
        # ---------------------------------------------------------------------
        box_choreog = layout.box()
        box_choreog.label(text="4. Multi-Beat Shot Choreographer:", icon='TIME')
        box_choreog.label(text="Create ANY compound motion with custom timing:")

        col_start = box_choreog.column(align=True)
        col_start.operator("cindy.record_start_beat", text="📍 1. Set Shot Start (Frame 1)", icon='RADIOBUT_ON')

        box_choreog.separator()
        box_choreog.label(text="Next Beat Settings:")
        row_beat_set = box_choreog.row(align=True)
        row_beat_set.prop(scene, "cindy_beat_duration", text="Duration (s)")
        box_choreog.prop(scene, "cindy_transition_style", text="Style")

        col_rec = box_choreog.column(align=True)
        col_rec.scale_y = 1.3
        col_rec.operator("cindy.record_next_beat", text="➕ 2. Record Next Beat (Append)", icon='KEYFRAME_HL')

        fps = scene.render.fps
        total_sec = round(scene.frame_end / fps, 1)
        curr_sec = round(scene.frame_current / fps, 1)
        info_row = box_choreog.row()
        info_row.label(text=f"Time: {curr_sec}s / {total_sec}s", icon='TIME')
        info_row.label(text=f"Beats: {scene.cindy_beat_count}", icon='SEQUENCE')

        row_ctrls = box_choreog.row(align=True)
        row_ctrls.operator("cindy.play_shot", text="▶️ Play Preview", icon='PLAY')
        row_ctrls.operator("cindy.reset_timeline", text="🗑️ Reset Timeline", icon='CANCEL')

        layout.separator()

        # ---------------------------------------------------------------------
        # 5. Cinematic Compound Moves Library (Presets)
        # ---------------------------------------------------------------------
        box_moves = layout.box()
        box_moves.label(text="5. Compound Moves Library (Presets):", icon='TRACKING')

        col_select = box_moves.column(align=True)
        col_select.label(text="Select Compound Camera Move:")
        col_select.prop(scene, "cindy_compound_move", text="")

        row_mset = box_moves.row(align=True)
        row_mset.prop(scene, "cindy_compound_duration", text="Duration (s)")
        row_mset.prop(scene, "cindy_chain_mode", text="Chain to Sequence")

        col_exec = box_moves.column(align=True)
        col_exec.scale_y = 1.3
        col_exec.operator("cindy.apply_compound_move", text="Apply Move to Timeline", icon='PLAY')

        layout.separator()

        # ---------------------------------------------------------------------
        # 6. Export to Cindy AI Studio
        # ---------------------------------------------------------------------
        col_btn = layout.column(align=True)
        col_btn.scale_y = 1.4
        col_btn.operator("cindy.export_guides", text="Export to Cindy AI Studio (RGB + Depth)", icon='EXPORT')
        layout.label(text="Target: outputs/blender_guides", icon='FILE_FOLDER')

def draw_cindy_header_button(self, context):
    layout = self.layout
    layout.separator()
    layout.operator("cindy.export_guides", text="Export to Cindy", icon='EXPORT')

def register():
    bpy.types.Scene.cindy_compound_move = bpy.props.EnumProperty(
        name="Compound Camera Move",
        description="Select a professional cinematic camera movement technique",
        items=COMPOUND_MOVE_ITEMS,
        default='CRANE_PUSH_IN'
    )
    bpy.types.Scene.cindy_compound_duration = bpy.props.FloatProperty(
        name="Duration",
        description="Duration of this camera movement in seconds",
        default=2.5,
        min=0.3,
        max=30.0
    )
    bpy.types.Scene.cindy_chain_mode = bpy.props.BoolProperty(
        name="Chain to Sequence",
        description="If checked, appends to the end of the existing shot. If unchecked, starts fresh from frame 1",
        default=False
    )
    bpy.types.Scene.cindy_sequence_count = bpy.props.IntProperty(
        name="Choreographed Sequences",
        default=0
    )

    # Multi-Beat Choreographer Properties
    bpy.types.Scene.cindy_beat_duration = bpy.props.FloatProperty(
        name="Beat Duration (s)",
        description="Duration of this shot movement in seconds",
        default=1.5,
        min=0.2,
        max=30.0
    )
    bpy.types.Scene.cindy_transition_style = bpy.props.EnumProperty(
        name="Transition Style",
        description="Motion easing curve style",
        items=TRANSITION_STYLE_ITEMS,
        default='SMOOTH'
    )
    bpy.types.Scene.cindy_beat_count = bpy.props.IntProperty(
        name="Beat Count",
        default=0
    )

    bpy.types.Scene.cindy_char_folder = bpy.props.EnumProperty(
        name="Character",
        description="Select character and age stage",
        items=CHARACTER_ITEMS,
        default='1_عبدالعزيز\\المرحلة_1_الشاب'
    )
    bpy.types.Scene.cindy_char_motion = bpy.props.EnumProperty(
        name="Motion Clip",
        description="Select Mixamo FBX animation clip",
        items=_get_character_motion_items
    )
    bpy.utils.register_class(CINDY_OT_LoadProjectCharacter)
    bpy.utils.register_class(CINDY_OT_OptimizeViewportPerformance)
    bpy.utils.register_class(CINDY_OT_NewDirectorStage)
    bpy.utils.register_class(CINDY_OT_AddActor)
    bpy.utils.register_class(CINDY_OT_AddProp)
    bpy.utils.register_class(CINDY_OT_SnapToFloor)
    bpy.utils.register_class(CINDY_OT_TurnObject)
    bpy.utils.register_class(CINDY_OT_FaceTarget)
    bpy.utils.register_class(CINDY_OT_ToggleGizmo)
    bpy.utils.register_class(CINDY_OT_ToggleCameraView)
    bpy.utils.register_class(CINDY_OT_WalkNavigation)
    bpy.utils.register_class(CINDY_OT_AlignCamToView)
    bpy.utils.register_class(CINDY_OT_LockCameraAim)
    bpy.utils.register_class(CINDY_OT_UnlockCameraAim)
    bpy.utils.register_class(CINDY_OT_FrameShot)
    bpy.utils.register_class(CINDY_OT_SetLens)
    bpy.utils.register_class(CINDY_OT_RecordStartBeat)
    bpy.utils.register_class(CINDY_OT_RecordNextBeat)
    bpy.utils.register_class(CINDY_OT_PlayShot)
    bpy.utils.register_class(CINDY_OT_ResetTimeline)
    bpy.utils.register_class(CINDY_OT_ApplyCompoundMove)
    bpy.utils.register_class(CINDY_OT_ExportGuides)
    bpy.utils.register_class(CINDY_OT_OpenCompoundScene)
    bpy.utils.register_class(CINDY_PT_DirectorPanel)
    try:
        bpy.types.VIEW3D_HT_header.append(draw_cindy_header_button)
    except Exception:
        pass

def unregister():
    try:
        bpy.types.VIEW3D_HT_header.remove(draw_cindy_header_button)
    except Exception:
        pass
    bpy.utils.unregister_class(CINDY_PT_DirectorPanel)
    bpy.utils.unregister_class(CINDY_OT_OpenCompoundScene)
    bpy.utils.unregister_class(CINDY_OT_ExportGuides)
    bpy.utils.unregister_class(CINDY_OT_ApplyCompoundMove)
    bpy.utils.unregister_class(CINDY_OT_ResetTimeline)
    bpy.utils.unregister_class(CINDY_OT_PlayShot)
    bpy.utils.unregister_class(CINDY_OT_RecordNextBeat)
    bpy.utils.unregister_class(CINDY_OT_RecordStartBeat)
    bpy.utils.unregister_class(CINDY_OT_SetLens)
    bpy.utils.unregister_class(CINDY_OT_FrameShot)
    bpy.utils.unregister_class(CINDY_OT_UnlockCameraAim)
    bpy.utils.unregister_class(CINDY_OT_LockCameraAim)
    bpy.utils.unregister_class(CINDY_OT_AlignCamToView)
    bpy.utils.unregister_class(CINDY_OT_WalkNavigation)
    bpy.utils.unregister_class(CINDY_OT_ToggleCameraView)
    bpy.utils.unregister_class(CINDY_OT_ToggleGizmo)
    bpy.utils.unregister_class(CINDY_OT_FaceTarget)
    bpy.utils.unregister_class(CINDY_OT_TurnObject)
    bpy.utils.unregister_class(CINDY_OT_SnapToFloor)
    bpy.utils.unregister_class(CINDY_OT_AddProp)
    bpy.utils.unregister_class(CINDY_OT_AddActor)
    bpy.utils.unregister_class(CINDY_OT_NewDirectorStage)
    bpy.utils.unregister_class(CINDY_OT_OptimizeViewportPerformance)
    bpy.utils.unregister_class(CINDY_OT_LoadProjectCharacter)
    del bpy.types.Scene.cindy_char_motion
    del bpy.types.Scene.cindy_char_folder

    del bpy.types.Scene.cindy_compound_move
    del bpy.types.Scene.cindy_compound_duration
    del bpy.types.Scene.cindy_chain_mode
    del bpy.types.Scene.cindy_sequence_count
    del bpy.types.Scene.cindy_beat_duration
    del bpy.types.Scene.cindy_transition_style
    del bpy.types.Scene.cindy_beat_count

if __name__ == "__main__":
    register()
    print("Cindy AI Director Blender Suite v5.0 Loaded Successfully!")
