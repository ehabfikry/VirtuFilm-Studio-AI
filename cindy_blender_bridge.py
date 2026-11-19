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
Version: 5.4 (Director Studio Physical & Spatial Engine Edition)
=============================================================================
Provides film directors with effortless 3D scene building, actor blocking,
camera navigation, multi-beat compound motion recording, AI depth export,
and automated physical scale, contact, and bone-socket constraint engines.
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
    "version": (5, 4, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Cindy Director",
    "description": "Physical staging, normalized human scale, bone sockets, and compound cinematic motion suite",
    "category": "Render",
}

OUTPUT_BASE_DIR = r"C:\Users\DELL\Desktop\Cindy-AI-Director\outputs\blender_guides"
SCENE_PRESET_PATH = r"D:\Blender\scenes\compound_camera_shot.blend"

# Standard Physical Human Target Scale (1.75 meters tall adult)
TARGET_HUMAN_HEIGHT = 1.75

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

SHOT_PRESET_ITEMS = [
    ('EXTREME_WIDE', "Extreme Wide Shot (Establishing)", "Shows the entire environment, character is small in frame"),
    ('WIDE', "Wide Shot (Full Body)", "Full actor visible from head to toe with surrounding environment"),
    ('MEDIUM_WIDE', "Medium Wide Shot (Cowboy / Knees Up)", "Frames actor from mid-thigh/knees up"),
    ('MEDIUM', "Medium Shot (Waist Up)", "Standard conversational framing from waist up"),
    ('MEDIUM_CLOSE_UP', "Medium Close-Up (Chest Up)", "Captures facial emotion and upper torso"),
    ('CLOSE_UP', "Close-Up (Head & Shoulders)", "Direct emotional connection on actor face"),
    ('EXTREME_CLOSE_UP', "Extreme Close-Up (Eyes / Detail)", "Choke shot on eyes, mouth, or specific prop"),
    ('DUTCH_ANGLE', "Dutch Angle (Dramatic Tension)", "Canted camera angle for psychological suspense"),
    ('OVER_THE_SHOULDER', "Over-the-Shoulder (Dialogue)", "Classic two-person dialogue perspective"),
    ('LOW_ANGLE_HERO', "Low Angle (Hero / Powerful)", "Looking up at character making them feel dominant"),
]

# Physical prop presets with exact real-world dimensions (Width, Depth, Height in meters)
PROP_PRESETS = {
    'BILLIARD_TABLE': {
        'name': "Billiard / Pool Table",
        'dim': (2.40, 1.30, 0.82),
        'surface_height': 0.82,
        'description': "Tournament pool table with felt bed and rails"
    },
    'ARMCHAIR': {
        'name': "Living Armchair",
        'dim': (0.85, 0.80, 1.05),
        'surface_height': 0.45,
        'description': "Standard armchair with 0.45m seat height"
    },
    'DINING_TABLE': {
        'name': "Dining Table",
        'dim': (1.80, 0.90, 0.76),
        'surface_height': 0.76,
        'description': "Standard dining table at 0.76m height"
    },
    'OFFICE_DESK': {
        'name': "Office Desk",
        'dim': (1.40, 0.75, 0.75),
        'surface_height': 0.75,
        'description': "Standard office desk"
    }
}

# Auto-Discovery Directories
CHARACTER_LIBRARY_DIR = r"C:\Users\DELL\Downloads\شخصيات_المشروع"
ENVIRONMENT_LIBRARY_DIR = r"C:\Users\DELL\Downloads\مكتبة_البيئات_والعوالم"

def _normalize_character_scale(armature_obj, target_height=TARGET_HUMAN_HEIGHT):
    """
    Measures the true evaluated bounding height of an armature/mesh and scales it
    strictly to the target human height (default 1.75m).
    """
    if not armature_obj:
        return
    dg = bpy.context.evaluated_depsgraph_get()
    child_meshes = [c for c in armature_obj.children if c.type == 'MESH']
    if not child_meshes:
        return

    # Calculate world Z height
    all_z = []
    for m in child_meshes:
        eval_m = m.evaluated_get(dg)
        for v in eval_m.data.vertices:
            all_z.append((eval_m.matrix_world @ v.co).z)

    if not all_z:
        return

    current_height = max(all_z) - min(all_z)
    if current_height > 0.05:
        scale_factor = target_height / current_height
        armature_obj.scale *= scale_factor
        bpy.context.view_layer.update()
        print(f"[Cindy Engine] Scaled {armature_obj.name} from {current_height:.2f}m to {target_height:.2f}m (Factor: {scale_factor:.3f})")

def _snap_object_to_ground(obj):
    """
    Evaluates the bottom-most vertex coordinate of an object/armature hierarchy
    and places it precisely at floor level (Z = 0.0).
    """
    if not obj:
        return
    dg = bpy.context.evaluated_depsgraph_get()
    meshes = []
    if obj.type == 'MESH':
        meshes.append(obj)
    elif obj.type == 'ARMATURE':
        meshes.extend([c for c in obj.children if c.type == 'MESH'])

    if not meshes:
        return

    all_z = []
    for m in meshes:
        eval_m = m.evaluated_get(dg)
        for v in eval_m.data.vertices:
            all_z.append((eval_m.matrix_world @ v.co).z)

    if all_z:
        lowest_z = min(all_z)
        obj.location.z -= lowest_z
        bpy.context.view_layer.update()
        print(f"[Cindy Engine] Snapped {obj.name} to ground (Z=0.0). Adjusted Z by {-lowest_z:.3f}m")

def _attach_prop_to_hand(armature_obj, prop_obj, hand_bone="RightHand"):
    """
    Uses a robust Child Of bone constraint to attach a prop to an actor's hand,
    ensuring it follows natural arm and body motion without flying in space.
    """
    if not armature_obj or not prop_obj:
        return False

    # Check for bone name variants (Mixamo standard)
    target_bone = None
    possible_names = [hand_bone, f"mixamorig:{hand_bone}", f"mixamorig:{hand_bone}Index1", "RightHand", "mixamorig:RightHand"]
    for b in armature_obj.pose.bones:
        if any(name.lower() in b.name.lower() for name in possible_names):
            target_bone = b.name
            break

    if not target_bone:
        return False

    # Remove previous Child Of constraints targeting this armature
    for c in list(prop_obj.constraints):
        if c.type == 'CHILD_OF':
            prop_obj.constraints.remove(c)

    # Add Child Of Constraint
    con = prop_obj.constraints.new(type='CHILD_OF')
    con.target = armature_obj
    con.subtarget = target_bone
    con.inverse_matrix = armature_obj.matrix_world.inverted() @ prop_obj.matrix_world

    print(f"[Cindy Engine] Successfully attached {prop_obj.name} to {armature_obj.name} -> {target_bone}")
    return True

# =============================================================================
# OPERATORS: PHYSICAL ATTACHMENT & STAGING
# =============================================================================

class CINDY_OT_AttachPropToHand(bpy.types.Operator):
    bl_idname = "cindy.attach_prop_to_hand"
    bl_label = "Attach Prop to Hand (Bone Socket)"
    bl_description = "Physically attach selected prop to the active character's hand bone using Child-Of constraint"
    hand_choice: bpy.props.EnumProperty(
        name="Hand",
        items=[('RightHand', "Right Hand", "Attach to right hand"), ('LeftHand', "Left Hand", "Attach to left hand")],
        default='RightHand'
    )

    def execute(self, context):
        sel = context.selected_objects
        arm = next((o for o in sel if o.type == 'ARMATURE'), None)
        prop = next((o for o in sel if o.type == 'MESH' and o.parent != arm), None)

        if not arm or not prop:
            self.report({'WARNING'}, "Select an Armature actor AND a Prop object!")
            return {'CANCELLED'}

        success = _attach_prop_to_hand(arm, prop, self.hand_choice)
        if success:
            self.report({'INFO'}, f"Attached {prop.name} cleanly to {arm.name}'s {self.hand_choice}!")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Could not locate hand bone in armature!")
            return {'CANCELLED'}

class CINDY_OT_NormalizeScale(bpy.types.Operator):
    bl_idname = "cindy.normalize_scale"
    bl_label = "Normalize Human Scale (1.75m)"
    bl_description = "Mathematically calibrate the active actor to true adult human height (1.75m)"

    def execute(self, context):
        obj = context.active_object
        if not obj:
            self.report({'WARNING'}, "Select an actor armature first!")
            return {'CANCELLED'}

        arm = obj if obj.type == 'ARMATURE' else obj.find_armature()
        if arm:
            _normalize_character_scale(arm, TARGET_HUMAN_HEIGHT)
            _snap_object_to_ground(arm)
            self.report({'INFO'}, f"Normalized {arm.name} to adult human scale (1.75m) and grounded to floor!")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Selected object has no armature to scale!")
            return {'CANCELLED'}

class CINDY_OT_SnapToFloor(bpy.types.Operator):
    bl_idname = "cindy.snap_to_floor"
    bl_label = "Snap to Floor (Z=0)"
    bl_description = "Snap the bottom vertices of the selected actor or prop directly onto the ground (Z=0)"

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type == 'CAMERA':
            self.report({'WARNING'}, "Select an actor or prop first!")
            return {'CANCELLED'}

        _snap_object_to_ground(obj)
        self.report({'INFO'}, f"Snapped {obj.name} cleanly to floor (Z=0)")
        return {'FINISHED'}

class CINDY_OT_CreateBilliardStage(bpy.types.Operator):
    bl_idname = "cindy.create_billiard_stage"
    bl_label = "Stage Billiard Table (Standard Dimensions)"
    bl_description = "Construct an authentic tournament billiard table (2.4m x 1.3m x 0.82m) with Simonis green felt, mahogany rails, and aramith pool balls"

    def execute(self, context):
        # Mahogany wood
        mahogany_mat = bpy.data.materials.new("Mahogany_Polished")
        m_bsdf = mahogany_mat.node_tree.nodes.get("Principled BSDF")
        m_bsdf.inputs['Base Color'].default_value = (0.07, 0.02, 0.01, 1.0)
        m_bsdf.inputs['Roughness'].default_value = 0.2

        # Felt
        felt_mat = bpy.data.materials.new("Tournament_Green_Felt")
        fl_bsdf = felt_mat.node_tree.nodes.get("Principled BSDF")
        fl_bsdf.inputs['Base Color'].default_value = (0.015, 0.16, 0.05, 1.0)
        fl_bsdf.inputs['Roughness'].default_value = 0.85

        # Base Table
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.77))
        base_table = bpy.context.active_object
        base_table.name = "Billiard_Table_Base"
        base_table.scale = (2.2, 1.2, 0.08)
        base_table.data.materials.append(mahogany_mat)

        # Felt Surface Bed
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.82))
        felt_bed = bpy.context.active_object
        felt_bed.name = "Billiard_Felt_Surface"
        felt_bed.scale = (2.0, 1.0, 0.02)
        felt_bed.data.materials.append(felt_mat)

        # Rails
        for sy in [-0.55, 0.55]:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, sy, 0.835))
            rail = bpy.context.active_object
            rail.scale = (2.2, 0.10, 0.04)
            rail.data.materials.append(mahogany_mat)

        for sx in [-1.05, 1.05]:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, 0, 0.835))
            rail = bpy.context.active_object
            rail.scale = (0.10, 1.2, 0.04)
            rail.data.materials.append(mahogany_mat)

        # 4 Legs
        for lx in [-0.85, 0.85]:
            for ly in [-0.4, 0.4]:
                bpy.ops.mesh.primitive_cylinder_add(radius=0.075, depth=0.73, location=(lx, ly, 0.365))
                leg = bpy.context.active_object
                leg.data.materials.append(mahogany_mat)

        # Pool Balls
        ball_r = 0.0285
        ball_z = 0.83 + ball_r
        balls = [
            ("Cue_Ball_White", (0.95, 0.95, 0.92, 1.0), (-0.45, 0.0, ball_z)),
            ("Ball_8_Black", (0.015, 0.015, 0.015, 1.0), (0.25, 0.0, ball_z)),
            ("Ball_Solid_Red", (0.85, 0.06, 0.06, 1.0), (0.35, 0.08, ball_z)),
            ("Ball_Solid_Yellow", (0.90, 0.80, 0.05, 1.0), (0.35, -0.08, ball_z)),
            ("Ball_Striped_Blue", (0.05, 0.15, 0.85, 1.0), (0.45, 0.0, ball_z))
        ]
        for b_name, b_col, b_loc in balls:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=ball_r, location=b_loc)
            b_obj = bpy.context.active_object
            b_mat = bpy.data.materials.new(b_name + "_Mat")
            bs = b_mat.node_tree.nodes.get("Principled BSDF")
            bs.inputs['Base Color'].default_value = b_col
            bs.inputs['Roughness'].default_value = 0.08
            b_obj.data.materials.append(b_mat)

        self.report({'INFO'}, "Created Standard Tournament Billiard Table with Official Aramith Balls!")
        return {'FINISHED'}

# =============================================================================
# OPERATORS: EFFORTLESS ELEMENT MOVEMENT & ORIENTATION
# =============================================================================

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

        cam = context.scene.camera
        other_actor = None
        for o in context.scene.objects:
            if o != obj and (o.type == 'ARMATURE' or (o.type == 'MESH' and 'Actor' in o.name)):
                other_actor = o
                break

        if self.target_type == 'CAMERA' and cam:
            target_pos = cam.matrix_world.translation
        elif other_actor:
            target_pos = other_actor.matrix_world.translation
        else:
            self.report({'WARNING'}, "No other actor or camera found to face!")
            return {'CANCELLED'}

        dir_vec = target_pos - obj.matrix_world.translation
        dir_vec.z = 0
        if dir_vec.length > 0.001:
            target_angle = math.atan2(dir_vec.y, dir_vec.x) - math.pi / 2
            obj.rotation_euler.z = target_angle
            self.report({'INFO'}, f"Turned {obj.name} to face target!")
        return {'FINISHED'}

class CINDY_OT_ToggleGizmo(bpy.types.Operator):
    bl_idname = "cindy.toggle_gizmo"
    bl_label = "Translate Gizmo (Arrows)"
    bl_description = "Activate the 3D translation arrows so the director can drag elements effortlessly"

    def execute(self, context):
        for space in context.area.spaces:
            if space.type == 'VIEW_3D':
                space.show_gizmo = True
                space.show_gizmo_object_translate = True
                space.show_gizmo_object_rotate = False
                space.show_gizmo_object_scale = False
        bpy.ops.wm.tool_set_by_id(name="builtin.move")
        self.report({'INFO'}, "Move Arrows Activated! Drag element anywhere.")
        return {'FINISHED'}

class CINDY_OT_ToggleCameraView(bpy.types.Operator):
    bl_idname = "cindy.toggle_camera_view"
    bl_label = "Look Through Camera"
    bl_description = "Toggle between 3D Director View and Camera Viewfinder (Numpad 0)"

    def execute(self, context):
        bpy.ops.view3d.view_camera()
        return {'FINISHED'}

class CINDY_OT_WalkNavigation(bpy.types.Operator):
    bl_idname = "cindy.walk_navigation"
    bl_label = "Walk / Fly Camera (WASD)"
    bl_description = "Fly camera interactively using WASD keys and mouse look. Left Click = Lock position. Right Click / Esc = Cancel."

    def execute(self, context):
        bpy.ops.view3d.walk('INVOKE_DEFAULT')
        return {'FINISHED'}

class CINDY_OT_AlignCamToView(bpy.types.Operator):
    bl_idname = "cindy.align_cam_to_view"
    bl_label = "Snap Camera to My View"
    bl_description = "Move and align the director camera exactly to what you are currently seeing in the 3D Viewport"

    def execute(self, context):
        bpy.ops.view3d.camera_to_view()
        self.report({'INFO'}, "Camera aligned exactly to your current viewpoint!")
        return {'FINISHED'}

class CINDY_OT_LockCameraAim(bpy.types.Operator):
    bl_idname = "cindy.lock_camera_aim"
    bl_label = "Lock Camera Aim onto Target"
    bl_description = "Keeps the camera aimed dead-center at the selected actor or prop no matter how the camera moves"

    def execute(self, context):
        cam = context.scene.camera
        target = context.active_object
        if not cam or not target or target == cam:
            self.report({'WARNING'}, "Select a target actor or prop first!")
            return {'CANCELLED'}

        for c in list(cam.constraints):
            if c.type == 'TRACK_TO':
                cam.constraints.remove(c)

        con = cam.constraints.new(type='TRACK_TO')
        con.target = target
        con.track_axis = 'TRACK_NEGATIVE_Z'
        con.up_axis = 'UP_Y'
        self.report({'INFO'}, f"Camera locked onto {target.name}!")
        return {'FINISHED'}

class CINDY_OT_UnlockCameraAim(bpy.types.Operator):
    bl_idname = "cindy.unlock_camera_aim"
    bl_label = "Free Camera Aim"
    bl_description = "Remove camera track target and allow free manual panning"

    def execute(self, context):
        cam = context.scene.camera
        if not cam:
            return {'CANCELLED'}
        for c in list(cam.constraints):
            if c.type == 'TRACK_TO':
                cam.constraints.remove(c)
        self.report({'INFO'}, "Camera aim freed!")
        return {'FINISHED'}

class CINDY_OT_FrameShot(bpy.types.Operator):
    bl_idname = "cindy.frame_shot"
    bl_label = "Apply Shot Preset"
    bl_description = "Instantly snap the camera to a standard cinematic framing preset"
    shot_type: bpy.props.EnumProperty(items=SHOT_PRESET_ITEMS, default='MEDIUM')

    def execute(self, context):
        cam = context.scene.camera
        actor = context.active_object
        if not actor or actor.type == 'CAMERA':
            for o in context.scene.objects:
                if o.type == 'ARMATURE' or (o.type == 'MESH' and 'Actor' in o.name):
                    actor = o
                    break
        if not actor or not cam:
            self.report({'WARNING'}, "Select an actor first to frame the shot!")
            return {'CANCELLED'}

        actor_pos = actor.matrix_world.translation.copy()
        forward = Vector((0.0, -1.0, 0.0))
        forward.rotate(actor.matrix_world.to_euler())
        forward.z = 0
        if forward.length > 0.001:
            forward.normalize()
        else:
            forward = Vector((0.0, -1.0, 0.0))

        lens_map = {
            'EXTREME_WIDE': 24.0, 'WIDE': 28.0, 'MEDIUM_WIDE': 35.0,
            'MEDIUM': 50.0, 'MEDIUM_CLOSE_UP': 65.0, 'CLOSE_UP': 85.0,
            'EXTREME_CLOSE_UP': 105.0, 'DUTCH_ANGLE': 35.0,
            'OVER_THE_SHOULDER': 50.0, 'LOW_ANGLE_HERO': 28.0
        }
        dist_map = {
            'EXTREME_WIDE': 7.5, 'WIDE': 4.5, 'MEDIUM_WIDE': 3.2,
            'MEDIUM': 2.5, 'MEDIUM_CLOSE_UP': 1.8, 'CLOSE_UP': 1.3,
            'EXTREME_CLOSE_UP': 0.8, 'DUTCH_ANGLE': 2.5,
            'OVER_THE_SHOULDER': 1.9, 'LOW_ANGLE_HERO': 2.2
        }
        height_map = {
            'EXTREME_WIDE': 2.4, 'WIDE': 1.5, 'MEDIUM_WIDE': 1.4,
            'MEDIUM': 1.45, 'MEDIUM_CLOSE_UP': 1.55, 'CLOSE_UP': 1.6,
            'EXTREME_CLOSE_UP': 1.65, 'DUTCH_ANGLE': 1.4,
            'OVER_THE_SHOULDER': 1.6, 'LOW_ANGLE_HERO': 0.5
        }

        dist = dist_map.get(self.shot_type, 2.5)
        h = height_map.get(self.shot_type, 1.45)
        cam.data.lens = lens_map.get(self.shot_type, 50.0)

        if self.shot_type == 'OVER_THE_SHOULDER':
            right_vec = Vector((forward.y, -forward.x, 0.0))
            cam_pos = actor_pos + (forward * dist) + (right_vec * 0.45)
            cam_pos.z = h
        elif self.shot_type == 'DUTCH_ANGLE':
            cam_pos = actor_pos + (forward * dist)
            cam_pos.z = h
            cam.rotation_euler.y = math.radians(-15.0)
        elif self.shot_type == 'LOW_ANGLE_HERO':
            cam_pos = actor_pos + (forward * dist)
            cam_pos.z = h
        else:
            cam_pos = actor_pos + (forward * dist)
            cam_pos.z = h

        cam.location = cam_pos
        con = next((c for c in cam.constraints if c.type == 'TRACK_TO'), None)
        if not con:
            con = cam.constraints.new(type='TRACK_TO')
            con.target = actor
            con.track_axis = 'TRACK_NEGATIVE_Z'
            con.up_axis = 'UP_Y'

        self.report({'INFO'}, f"Framed: {self.shot_type} (Lens: {int(cam.data.lens)}mm)")
        return {'FINISHED'}

class CINDY_OT_SetLens(bpy.types.Operator):
    bl_idname = "cindy.set_lens"
    bl_label = "Set Camera Lens"
    bl_description = "Change camera focal length (e.g., 24mm wide, 50mm natural, 85mm portrait)"
    focal_length: bpy.props.FloatProperty(default=50.0)

    def execute(self, context):
        cam = context.scene.camera
        if cam and cam.type == 'CAMERA':
            cam.data.lens = self.focal_length
            self.report({'INFO'}, f"Focal length set to {int(self.focal_length)}mm")
            return {'FINISHED'}
        self.report({'WARNING'}, "No active camera found!")
        return {'CANCELLED'}

# =============================================================================
# OPERATORS: COMPOUND MOTION RECORDING & TIMELINE
# =============================================================================

class CINDY_OT_RecordStartBeat(bpy.types.Operator):
    bl_idname = "cindy.record_start_beat"
    bl_label = "Record Start Beat (Frame 1)"
    bl_description = "Saves current camera and actor positions as the opening frame of the shot"

    def execute(self, context):
        scene = context.scene
        scene.frame_set(1)
        cam = scene.camera
        if not cam:
            self.report({'ERROR'}, "No active camera in scene!")
            return {'CANCELLED'}

        cam.keyframe_insert(data_path="location", frame=1)
        cam.keyframe_insert(data_path="rotation_euler", frame=1)
        if cam.data:
            cam.data.keyframe_insert(data_path="lens", frame=1)

        for obj in scene.objects:
            if obj.type in {'MESH', 'ARMATURE', 'EMPTY'} and not obj.name.startswith(('Lamp', 'Floor', 'Light')):
                obj.keyframe_insert(data_path="location", frame=1)
                obj.keyframe_insert(data_path="rotation_euler", frame=1)

        self.report({'INFO'}, "Recorded Start Beat at Frame 1!")
        return {'FINISHED'}

class CINDY_OT_RecordNextBeat(bpy.types.Operator):
    bl_idname = "cindy.record_next_beat"
    bl_label = "Record Next Beat"
    bl_description = "Records current position into the timeline with chosen transition style"

    def execute(self, context):
        scene = context.scene
        cam = scene.camera
        if not cam:
            self.report({'ERROR'}, "No active camera in scene!")
            return {'CANCELLED'}

        cur_frame = scene.frame_current
        duration = max(5, scene.cindy_beat_duration)
        target_frame = cur_frame + duration

        scene.frame_set(target_frame)
        cam.keyframe_insert(data_path="location", frame=target_frame)
        cam.keyframe_insert(data_path="rotation_euler", frame=target_frame)
        if cam.data:
            cam.data.keyframe_insert(data_path="lens", frame=target_frame)

        for obj in scene.objects:
            if obj.type in {'MESH', 'ARMATURE', 'EMPTY'} and not obj.name.startswith(('Lamp', 'Floor', 'Light')):
                obj.keyframe_insert(data_path="location", frame=target_frame)
                obj.keyframe_insert(data_path="rotation_euler", frame=target_frame)

        if scene.frame_end < target_frame:
            scene.frame_end = target_frame

        self.report({'INFO'}, f"Recorded Next Beat at Frame {target_frame} (+{duration}f)")
        return {'FINISHED'}

class CINDY_OT_PlayShot(bpy.types.Operator):
    bl_idname = "cindy.play_shot"
    bl_label = "Play / Pause Shot"
    bl_description = "Toggle animation playback of the recorded cinematic camera moves"

    def execute(self, context):
        bpy.ops.screen.animation_play()
        return {'FINISHED'}

class CINDY_OT_ResetTimeline(bpy.types.Operator):
    bl_idname = "cindy.reset_timeline"
    bl_label = "Rewind to Start (Frame 1)"
    bl_description = "Jump back to Frame 1 to review from opening shot"

    def execute(self, context):
        context.scene.frame_set(1)
        return {'FINISHED'}

class CINDY_OT_ApplyCompoundMove(bpy.types.Operator):
    bl_idname = "cindy.apply_compound_move"
    bl_label = "Apply Compound Camera Move"
    bl_description = "Generate multi-beat cinematic camera motion onto the active camera"

    def execute(self, context):
        scene = context.scene
        cam = scene.camera
        if not cam:
            self.report({'ERROR'}, "No camera in scene!")
            return {'CANCELLED'}

        preset = scene.cindy_compound_move
        duration = scene.cindy_move_duration
        start_frame = scene.frame_current
        end_frame = start_frame + duration

        target = context.active_object if (context.active_object and context.active_object != cam) else None
        target_loc = target.matrix_world.translation if target else Vector((0.0, 0.0, 1.2))

        # Clear existing camera animation
        cam.animation_data_clear()
        if cam.data:
            cam.data.animation_data_clear()

        if preset == 'CRANE_PUSH_IN':
            cam.location = target_loc + Vector((-3.5, -4.5, 3.8))
            cam.data.lens = 28.0
            cam.keyframe_insert(data_path="location", frame=start_frame)
            cam.data.keyframe_insert(data_path="lens", frame=start_frame)

            cam.location = target_loc + Vector((-0.4, -1.4, 1.35))
            cam.data.lens = 65.0
            cam.keyframe_insert(data_path="location", frame=end_frame)
            cam.data.keyframe_insert(data_path="lens", frame=end_frame)

        elif preset == 'CRANE_PULL_OUT':
            cam.location = target_loc + Vector((-0.2, -1.2, 1.4))
            cam.data.lens = 70.0
            cam.keyframe_insert(data_path="location", frame=start_frame)
            cam.data.keyframe_insert(data_path="lens", frame=start_frame)

            cam.location = target_loc + Vector((-4.0, -5.5, 4.2))
            cam.data.lens = 24.0
            cam.keyframe_insert(data_path="location", frame=end_frame)
            cam.data.keyframe_insert(data_path="lens", frame=end_frame)

        elif preset == 'VERTIGO_DOLLY_ZOOM':
            init_dist = 4.5
            final_dist = 1.3
            cam.location = target_loc + Vector((0.0, -init_dist, 1.45))
            cam.data.lens = 85.0
            cam.keyframe_insert(data_path="location", frame=start_frame)
            cam.data.keyframe_insert(data_path="lens", frame=start_frame)

            cam.location = target_loc + Vector((0.0, -final_dist, 1.45))
            cam.data.lens = 24.0
            cam.keyframe_insert(data_path="location", frame=end_frame)
            cam.data.keyframe_insert(data_path="lens", frame=end_frame)

        elif preset == 'HERO_ORBIT_360':
            orbit_radius = 3.0
            orbit_h = 1.45
            for i in range(5):
                angle = (i / 4.0) * (2.0 * math.pi)
                f = start_frame + int((i / 4.0) * duration)
                x = target_loc.x + orbit_radius * math.sin(angle)
                y = target_loc.y - orbit_radius * math.cos(angle)
                cam.location = Vector((x, y, orbit_h))
                cam.keyframe_insert(data_path="location", frame=f)

        con = next((c for c in cam.constraints if c.type == 'TRACK_TO'), None)
        if not con:
            con = cam.constraints.new(type='TRACK_TO')
            con.target = target if target else None
            con.track_axis = 'TRACK_NEGATIVE_Z'
            con.up_axis = 'UP_Y'

        scene.frame_start = start_frame
        scene.frame_end = end_frame
        scene.frame_set(start_frame)
        self.report({'INFO'}, f"Generated {preset} ({duration}f)!")
        return {'FINISHED'}

# =============================================================================
# OPERATORS: CHARACTER & ENVIRONMENT ASSET PIPELINE
# =============================================================================

class CINDY_OT_LoadProjectCharacter(bpy.types.Operator):
    bl_idname = "cindy.load_project_character"
    bl_label = "Load Character & Motion (Clean Mixamo)"
    bl_description = "Import selected character FBX, normalize scale to 1.75m, snap to ground, and link verified textures"

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

        old_objs = set(bpy.data.objects)
        old_actions = set(bpy.data.actions)

        bpy.ops.import_scene.fbx(filepath=full_path)

        new_objs = [o for o in bpy.data.objects if o not in old_objs]
        new_actions = [a for a in bpy.data.actions if a not in old_actions]

        arm = next((o for o in new_objs if o.type == 'ARMATURE'), None)
        meshes = [o for o in new_objs if o.type == 'MESH']

        if arm and len(new_actions) > 1:
            mixamo_act = next((a for a in new_actions if 'mixamo' in a.name.lower()), None)
            if not mixamo_act:
                mixamo_act = min(new_actions, key=lambda a: a.frame_range[1] - a.frame_range[0])
            if arm.animation_data:
                arm.animation_data.action = mixamo_act
            for a in new_actions:
                if a != mixamo_act:
                    bpy.data.actions.remove(a, do_unlink=True)

        if arm and arm.animation_data and arm.animation_data.action:
            act = arm.animation_data.action
            scene.frame_start = max(1, int(act.frame_range[0]))
            scene.frame_end = max(2, int(act.frame_range[1]))
            scene.frame_current = scene.frame_start

        # Texture linking
        char_dir = os.path.join(CHARACTER_LIBRARY_DIR, sub)
        tex_path = None
        if os.path.exists(char_dir):
            for fname in os.listdir(char_dir):
                fl = fname.lower()
                if fl.endswith(('.png', '.jpg', '.jpeg')) and 'basecolor' in fl:
                    tex_path = os.path.join(char_dir, fname)
                    break
        if tex_path and meshes:
            try:
                img_data = bpy.data.images.load(tex_path, check_existing=True)
                for m in meshes:
                    mat = bpy.data.materials.new(name=f"Mat_{m.name}")
                    nodes = mat.node_tree.nodes
                    links = mat.node_tree.links
                    nodes.clear()
                    n_out = nodes.new(type='ShaderNodeOutputMaterial')
                    n_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
                    n_tex = nodes.new(type='ShaderNodeTexImage')
                    n_tex.image = img_data
                    links.new(n_tex.outputs['Color'], n_bsdf.inputs['Base Color'])
                    links.new(n_bsdf.outputs['BSDF'], n_out.inputs['Surface'])
                    n_bsdf.inputs['Roughness'].default_value = 0.55
                    m.data.materials.clear()
                    m.data.materials.append(mat)
            except Exception:
                pass

        # Normalize Scale to 1.75m and snap to ground
        if arm:
            _normalize_character_scale(arm, TARGET_HUMAN_HEIGHT)
            _snap_object_to_ground(arm)
        elif meshes:
            for m in meshes:
                _snap_object_to_ground(m)

        self.report({'INFO'}, f"Loaded & Normalized {fbx_file} (1.75m adult) successfully!")
        return {'FINISHED'}

class CINDY_OT_ApplyEnvironmentWorld(bpy.types.Operator):
    bl_idname = "cindy.apply_environment_world"
    bl_label = "Apply Selected HDRI / EXR"
    bl_description = "Apply the chosen 360-degree panorama as the cinematic world lighting environment"

    def execute(self, context):
        scene = context.scene
        cat = scene.cindy_env_category
        fname = scene.cindy_env_file
        if not fname or fname == 'NONE':
            self.report({'ERROR'}, "No valid HDRI/EXR selected!")
            return {'CANCELLED'}

        full_path = os.path.join(ENVIRONMENT_LIBRARY_DIR, "3_بانوراما_إضاءة_HDRI", cat, fname)
        if not os.path.exists(full_path):
            self.report({'ERROR'}, f"File not found: {full_path}")
            return {'CANCELLED'}

        world = scene.world if scene.world else bpy.data.worlds.new("Cindy_Environment")
        scene.world = world
        world.use_nodes = True
        nodes = world.node_tree.nodes
        links = world.node_tree.links
        nodes.clear()

        n_out = nodes.new(type='ShaderNodeOutputWorld')
        n_bg = nodes.new(type='ShaderNodeBackground')
        n_env = nodes.new(type='ShaderNodeTexEnvironment')
        n_bg.inputs['Strength'].default_value = 1.0

        try:
            n_env.image = bpy.data.images.load(full_path, check_existing=True)
            links.new(n_env.outputs['Color'], n_bg.inputs['Color'])
            links.new(n_bg.outputs['Background'], n_out.inputs['Surface'])
            self.report({'INFO'}, f"Applied environment: {fname}")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load HDR image: {e}")
            return {'CANCELLED'}

# =============================================================================
# PANEL UI: DIRECTOR STUDIO INTERFACE
# =============================================================================

def _get_character_folder_items(self, context):
    items = []
    if os.path.exists(CHARACTER_LIBRARY_DIR):
        for root, dirs, files in os.walk(CHARACTER_LIBRARY_DIR):
            if any(f.lower().endswith('.fbx') for f in files):
                rel = os.path.relpath(root, CHARACTER_LIBRARY_DIR)
                label = rel.replace('\\', ' > ')
                items.append((rel, label, f"Folder: {label}"))
    return items if items else [('NONE', "No Characters Found", "")]

def _get_character_motion_items(self, context):
    items = []
    sub = getattr(context.scene, 'cindy_char_folder', '')
    if sub and sub != 'NONE':
        target_dir = os.path.join(CHARACTER_LIBRARY_DIR, sub)
        if os.path.exists(target_dir):
            for f in sorted(os.listdir(target_dir)):
                if f.lower().endswith('.fbx'):
                    items.append((f, f.replace('.fbx', ''), f"Clip: {f}"))
    return items if items else [('NONE', "No Clips Found", "")]

def _get_environment_category_items(self, context):
    items = []
    hdri_base = os.path.join(ENVIRONMENT_LIBRARY_DIR, "3_بانوراما_إضاءة_HDRI")
    if os.path.exists(hdri_base):
        for d in sorted(os.listdir(hdri_base)):
            p = os.path.join(hdri_base, d)
            if os.path.isdir(p):
                items.append((d, d, f"Category: {d}"))
    return items if items else [('NONE', "No Environment Categories", "")]

def _get_environment_file_items(self, context):
    items = []
    cat = getattr(context.scene, 'cindy_env_category', '')
    if cat and cat != 'NONE':
        target_dir = os.path.join(ENVIRONMENT_LIBRARY_DIR, "3_بانوراما_إضاءة_HDRI", cat)
        if os.path.exists(target_dir):
            for f in sorted(os.listdir(target_dir)):
                if f.lower().endswith(('.hdr', '.exr')):
                    items.append((f, f, f"Environment: {f}"))
    return items if items else [('NONE', "No HDRI/EXR Found", "")]


def _get_3d_asset_items(self, context):
    items = []
    exts = ('.gltf', '.glb', '.fbx', '.obj')
    search_roots = ["4_أثاث_وديكورات_3D_Props", "1_داخلي_Interiors", "2_خارجي_Exteriors"]
    for sub in search_roots:
        base = os.path.join(ENVIRONMENT_LIBRARY_DIR, sub)
        if not os.path.exists(base):
            continue
        for root, dirs, files in os.walk(base):
            for f in sorted(files):
                if f.lower().endswith(exts):
                    full = os.path.join(root, f)
                    rel = os.path.relpath(full, ENVIRONMENT_LIBRARY_DIR)
                    label = os.path.splitext(f)[0]
                    items.append((rel, label, f"3D Asset: {rel}"))
    return items[:120] if items else [('NONE', "No 3D Props/Locations Found", "")]


class CINDY_OT_LoadEnvironmentAsset(bpy.types.Operator):
    bl_idname = "cindy.load_environment_asset"
    bl_label = "Import 3D Prop / Location (Z=0)"
    bl_description = "Import selected 3D location or furniture prop from the Environments Library and snap to floor"

    def execute(self, context):
        rel = getattr(context.scene, 'cindy_3d_asset', 'NONE')
        if not rel or rel == 'NONE':
            self.report({'ERROR'}, "No 3D asset selected!")
            return {'CANCELLED'}
        full_path = os.path.join(ENVIRONMENT_LIBRARY_DIR, rel)
        if not os.path.exists(full_path):
            self.report({'ERROR'}, f"Asset not found: {full_path}")
            return {'CANCELLED'}

        old_objs = set(bpy.data.objects)
        ext = os.path.splitext(full_path)[1].lower()
        try:
            if ext in ('.gltf', '.glb'):
                bpy.ops.import_scene.gltf(filepath=full_path)
            elif ext == '.fbx':
                bpy.ops.import_scene.fbx(filepath=full_path)
            elif ext == '.obj':
                bpy.ops.wm.obj_import(filepath=full_path)
        except Exception as e:
            self.report({'ERROR'}, f"Import failed: {e}")
            return {'CANCELLED'}

        new_objs = [o for o in bpy.data.objects if o not in old_objs]
        roots = [o for o in new_objs if o.parent not in new_objs]
        for r in roots:
            _snap_object_to_ground(r)
        self.report({'INFO'}, f"Imported & Grounded 3D Asset: {os.path.basename(full_path)}")
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Section 6: AI Video Engine Export (Beauty + 8-bit Depth + Director Gate + 7-Part Prompt -> Cindy App)
# ---------------------------------------------------------------------------

BLENDER_GUIDES_OUT_DIR = r"C:\Users\DELL\Desktop\Cindy-AI-Director\outputs\blender_guides"

def _render_calibrated_depth_pass_53(scene, out_path, near_clip=0.45, far_clip=8.0):
    """Blender 5.3 compatible 8-bit linear depth pass via EEVEE material_override."""
    mat_name = "Cindy_Depth_Override_Mat"
    mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    n_cam = nodes.new(type='ShaderNodeCameraData')
    n_map = nodes.new(type='ShaderNodeMapRange')
    n_map.clamp = True
    n_map.inputs['From Min'].default_value = near_clip
    n_map.inputs['From Max'].default_value = far_clip
    n_map.inputs['To Min'].default_value = 1.0  # Near = White (ControlNet Depth standard)
    n_map.inputs['To Max'].default_value = 0.0  # Far = Black
    n_emit = nodes.new(type='ShaderNodeEmission')
    n_out = nodes.new(type='ShaderNodeOutputMaterial')

    links.new(n_cam.outputs['View Z Depth'], n_map.inputs['Value'])
    links.new(n_map.outputs['Result'], n_emit.inputs['Color'])
    links.new(n_emit.outputs['Emission'], n_out.inputs['Surface'])

    vl = bpy.context.view_layer
    old_override = vl.material_override
    old_filepath = scene.render.filepath
    old_format = scene.render.image_settings.file_format
    old_color_mode = scene.render.image_settings.color_mode

    try:
        vl.material_override = mat
        scene.render.filepath = out_path
        scene.render.image_settings.file_format = 'PNG'
        scene.render.image_settings.color_mode = 'BW'
        bpy.ops.render.render(write_still=True)
    finally:
        vl.material_override = old_override
        scene.render.filepath = old_filepath
        scene.render.image_settings.file_format = old_format
        scene.render.image_settings.color_mode = old_color_mode


def _detect_actor_pose(obj, frame):
    """Detect whether an armature is standing, sitting, or crouching at a given frame."""
    names = []
    ad = getattr(obj, "animation_data", None)
    if ad:
        if ad.action:
            names.append(ad.action.name.lower())
        for track in ad.nla_tracks:
            if track.mute:
                continue
            for strip in track.strips:
                if strip.frame_start <= frame <= strip.frame_end:
                    names.append(strip.name.lower())
                    if strip.action:
                        names.append(strip.action.name.lower())
    joined = " ".join(names)
    if any(k in joined for k in ("sit", "chair", "couch", "bench")):
        return "sitting"
    if any(k in joined for k in ("crouch", "kneel", "squat")):
        return "crouching"
    return "standing"


def _measure_armature_bounds(context, obj):
    """Return (min_z, max_z, height, dx, dy) of an armature's evaluated child meshes."""
    context.view_layer.update()
    depsgraph = context.evaluated_depsgraph_get()
    child_meshes = [c for c in obj.children_recursive if c.type == 'MESH' and not c.hide_viewport]
    targets = child_meshes if child_meshes else [obj]
    min_x, max_x = float('inf'), float('-inf')
    min_y, max_y = float('inf'), float('-inf')
    min_z, max_z = float('inf'), float('-inf')
    for t in targets:
        eval_t = t.evaluated_get(depsgraph)
        for corner in eval_t.bound_box:
            wc = eval_t.matrix_world @ Vector(corner)
            min_x, max_x = min(min_x, wc.x), max(max_x, wc.x)
            min_y, max_y = min(min_y, wc.y), max(max_y, wc.y)
            min_z, max_z = min(min_z, wc.z), max(max_z, wc.z)
    if min_z == float('inf'):
        return 0.0, 1.75, 1.75, 0.5, 0.5
    return min_z, max_z, max(0.0, max_z - min_z), max(0.0, max_x - min_x), max(0.0, max_y - min_y)


def _auto_fix_actor_physics(context, obj, target_standing_height=1.75):
    """
    Cindy Active Brain Auto-Fix:
    1. Detects & restores Mixamo Y-up -> Z-up upright orientation if X-rotation (90 deg) was wiped.
    2. Normalizes abnormal scale on the standing frame so adult human height ~= 1.75m.
    3. Grounds the actor cleanly to Z=0.0 across key animation frames (preventing Mixamo Sitting hip-drop).
    Returns a list of applied fix descriptions.
    """
    import math
    scene = context.scene
    orig_frame = scene.frame_current
    fixes = []

    f_start = scene.frame_start
    f_end = scene.frame_end
    f_mid = (f_start + f_end) // 2

    ad = getattr(obj, "animation_data", None)
    key_frames = sorted(set([f_start, f_mid, f_end, orig_frame]))
    if ad and ad.nla_tracks:
        for track in ad.nla_tracks:
            for strip in track.strips:
                fs = int(max(f_start, min(f_end, strip.frame_start)))
                fe = int(max(f_start, min(f_end, strip.frame_end)))
                key_frames.extend([fs, fe])
        key_frames = sorted(set(key_frames))

    has_anim = bool(ad and (ad.action is not None or len(ad.nla_tracks) > 0))

    # 1. Upright check: catch wiped Mixamo FBX X=90deg rotation (actor lying flat: dz << max(dx, dy))
    scene.frame_set(f_start)
    pose_start = _detect_actor_pose(obj, f_start)
    _, _, h_start, dx, dy = _measure_armature_bounds(context, obj)
    if pose_start == "standing" and h_start < 0.90 and max(dx, dy) > 1.25 and abs(obj.rotation_euler.x) < 0.2:
        for kf in key_frames:
            scene.frame_set(kf)
            obj.rotation_euler.x = math.radians(90.0)
            if has_anim or len(key_frames) > 1:
                obj.keyframe_insert(data_path="rotation_euler", index=0, frame=kf)
        fixes.append(f"{obj.name}: restored Mixamo upright X=90deg (was lying flat dz={h_start:.2f}m, max_xy={max(dx,dy):.2f}m)")
        scene.frame_set(f_start)
        _, _, h_start, dx, dy = _measure_armature_bounds(context, obj)

    # 2. Scale check on frame_start (standing)
    if pose_start == "standing" and (h_start < 1.50 or h_start > 2.00) and h_start > 0.05:
        sf = target_standing_height / h_start
        obj.scale = (obj.scale.x * sf, obj.scale.y * sf, obj.scale.z * sf)
        fixes.append(f"{obj.name}: rescaled {h_start:.2f}m -> {target_standing_height:.2f}m (factor {sf:.3f})")

    # 3. Multi-frame floor grounding (catches Mixamo Sitting/Crouching sinking below Z=0)
    for kf in key_frames:
        scene.frame_set(kf)
        min_z, _, _, _, _ = _measure_armature_bounds(context, obj)
        if abs(min_z) > 0.03:
            obj.location.z -= min_z
            if has_anim or len(key_frames) > 1:
                obj.keyframe_insert(data_path="location", index=2, frame=kf)
            fixes.append(f"{obj.name} @f{kf}: grounded Z by {-min_z:+.3f}m")

    scene.frame_set(orig_frame)
    context.view_layer.update()
    return fixes


def _run_scene_audit_and_extract(context, auto_fix=True):
    """Audit visible armatures & props via CindyDirectorGate (with Active Auto-Fix) and extract real scene metadata."""
    import sys
    repo_dir = r"C:\Users\DELL\Desktop\Cindy-AI-Director"
    if repo_dir not in sys.path:
        sys.path.append(repo_dir)
    from cindy_director_gate import CindyDirectorGate

    scene = context.scene
    actors = []
    audit_checks = []
    auto_fixes_applied = []
    all_passed = True

    for obj in scene.objects:
        if obj.type == 'ARMATURE' and not obj.hide_viewport:
            if auto_fix:
                applied = _auto_fix_actor_physics(context, obj)
                auto_fixes_applied.extend(applied)

            name = obj.name.replace('RIG_', '').replace('CHAR_', '').replace('_', ' ').strip().capitalize()
            pose = _detect_actor_pose(obj, scene.frame_current)
            min_z, max_z, height, _, _ = _measure_armature_bounds(context, obj)

            scale_res = CindyDirectorGate.audit_actor_scale(name, height, pose=pose)
            ground_res = CindyDirectorGate.audit_ground_contact(min_z, ground_tolerance=0.05)
            audit_checks.append(scale_res)
            audit_checks.append(ground_res)
            if not scale_res['passed'] or not ground_res['passed']:
                all_passed = False

            held_prop = ""
            for other in scene.objects:
                for const in other.constraints:
                    if const.type == 'CHILD_OF' and const.target == obj:
                        held_prop = other.name.replace('_', ' ')
                        prop_res = CindyDirectorGate.audit_prop_socket(held_prop, True, const.subtarget or "Bone")
                        audit_checks.append(prop_res)
                        break

            actors.append({
                'name': name,
                'appearance': f"Character {name} staged ({pose}) at {height:.2f}m physical scale",
                'locked_prop': held_prop
            })

    return actors, {
        'passed': all_passed,
        'actor_count': len(actors),
        'auto_fixes_applied': auto_fixes_applied,
        'checks': audit_checks
    }


class CINDY_OT_SynthesizeVideoPrompt(bpy.types.Operator):
    """Audit 3D scene, render Beauty + 8-bit Depth passes, synthesize 7-part prompt, and export directly to Cindy AI Director App"""
    bl_idname = "cindy.synthesize_video_prompt"
    bl_label = "Export Guide + Depth + Prompt to Cindy App"
    bl_options = {'REGISTER', 'UNDO'}

    target_engine: bpy.props.EnumProperty(
        name="Target Engine",
        items=[
            ('WAN_2_2', "Wan 2.2 (Alibaba)", "Wan 2.2 I2V / T2V Production Prompt"),
            ('SEEDANCE_2_5', "Seedance 2.0 (Doubao)", "Seedance Structured Delimiters"),
            ('HUNYUAN_VIDEO', "HunyuanVideo 13B", "Tencent Hunyuan Cinema Optics")
        ],
        default='WAN_2_2'
    )

    render_passes: bpy.props.BoolProperty(
        name="Render Beauty & Depth Passes",
        default=True
    )

    def execute(self, context):
        import sys, json, time
        repo_dir = r"C:\Users\DELL\Desktop\Cindy-AI-Director"
        if repo_dir not in sys.path:
            sys.path.append(repo_dir)
        from cindy_prompt_grammar import CindyPromptGrammar

        scene = context.scene
        cam = scene.camera
        lens_mm = round(float(cam.data.lens), 1) if (cam and cam.data) else 38.0
        lens_str = f"{int(lens_mm)}mm prime lens"

        # 1. Run Director Quality Gate & extract real actors
        actors, audit_report = _run_scene_audit_and_extract(context)
        if not actors:
            actors = [{'name': "Subject", 'appearance': "Primary character staged in 3D frame", 'locked_prop': ""}]

        # Detect environment name from World HDRI or scene name
        env_desc = f"3D staged interior set ({scene.name}), physically grounded lighting and perspective"
        if scene.world and scene.world.use_nodes:
            for n in scene.world.node_tree.nodes:
                if n.type == 'TEX_ENVIRONMENT' and n.image:
                    env_desc = f"Cinematic set lit by {n.image.name} environment, physically accurate shadows and depth"
                    break

        move_preset = getattr(scene, 'cindy_compound_move', 'STEADY_TRACK')
        payload = CindyPromptGrammar.build_seven_part_prompt(
            visual_style="Cinematic 35mm film still, natural chiaroscuro lighting, rich tactile textures, photorealistic skin and fabric",
            shot_type=f"3D Previz-grounded camera composition ({lens_str})",
            camera_lens=lens_str,
            camera_motion=f"Steady controlled cinema camera ({move_preset.replace('_', ' ').lower()}), zero handheld jitter",
            scene_environment=env_desc,
            cast_and_props=actors,
            chronological_beats=[
                {'time': "0.0-0.5s", 'actor': "Scene", 'action': "opens locked to 3D guide framing and spatial depth"},
                {'time': "0.5-2.5s", 'actor': actors[0]['name'], 'action': "performs motivated physical action while maintaining exact spatial grounding"},
                {'time': "1.5-3.5s", 'actor': actors[1]['name'] if len(actors) > 1 else actors[0]['name'], 'action': "reacts naturally with subtle micro-expressions"}
            ],
            target_model=self.target_engine
        )

        # 2. Export Beauty + Depth + JSON Manifest to Cindy App (outputs/blender_guides/)
        os.makedirs(BLENDER_GUIDES_OUT_DIR, exist_ok=True)
        beauty_file = "blender_bridge_beauty.jpg"
        depth_file = "blender_bridge_depth.png"
        beauty_path = os.path.join(BLENDER_GUIDES_OUT_DIR, beauty_file)
        depth_path = os.path.join(BLENDER_GUIDES_OUT_DIR, depth_file)

        if self.render_passes and cam:
            old_fp = scene.render.filepath
            old_fmt = scene.render.image_settings.file_format
            old_res_x, old_res_y = scene.render.resolution_x, scene.render.resolution_y
            try:
                scene.render.resolution_x = 1280
                scene.render.resolution_y = 720
                scene.render.filepath = beauty_path
                scene.render.image_settings.file_format = 'JPEG'
                bpy.ops.render.render(write_still=True)
                _render_calibrated_depth_pass_53(scene, depth_path, near_clip=0.45, far_clip=8.0)
            finally:
                scene.render.filepath = old_fp
                scene.render.image_settings.file_format = old_fmt
                scene.render.resolution_x = old_res_x
                scene.render.resolution_y = old_res_y

        manifest = {
            "exported_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "source": "cindy_blender_bridge_v8",
            "title": scene.name,
            "lens_focal_length_mm": lens_mm,
            "frame": scene.frame_current,
            "duration_sec": round((scene.frame_end - scene.frame_start) / max(1, scene.render.fps), 2),
            "stills": [{"url": f"/outputs/blender_guides/{beauty_file}", "frame": scene.frame_current}] if os.path.exists(beauty_path) else [],
            "depth_url": f"/outputs/blender_guides/{depth_file}" if os.path.exists(depth_path) else "",
            "meta": {
                "lens_focal_length_mm": lens_mm,
                "frame": scene.frame_current,
                "duration_sec": round((scene.frame_end - scene.frame_start) / max(1, scene.render.fps), 2),
                "resolution": [1280, 720],
                "shot_type": f"Blender 3D Guide ({lens_str})",
                "actors": [a['name'] for a in actors]
            },
            "prompt_package": payload,
            "audit": audit_report
        }

        manifest_path = os.path.join(BLENDER_GUIDES_OUT_DIR, "latest_previs_result.json")
        with open(manifest_path, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, ensure_ascii=False, indent=2)

        try:
            context.window_manager.clipboard = payload['positive_prompt']
        except Exception:
            pass

        gate_status = "PASS" if audit_report['passed'] else "WARN"
        self.report({'INFO'}, f"Exported Guide + Depth + {self.target_engine} Prompt to Cindy App! [Gate: {gate_status}]")
        return {'FINISHED'}


class CINDY_OT_ExportDepthVideo(bpy.types.Operator):
    """Render full animated Beauty MP4 + Calibrated 8-bit Depth MP4 sequence for V2V ControlNet/Wan pipelines"""
    bl_idname = "cindy.export_depth_video"
    bl_label = "Export Animated Depth + Beauty Video (MP4)"
    bl_options = {'REGISTER', 'UNDO'}

    max_frames: bpy.props.IntProperty(name="Max Frames", default=72, min=12, max=240)

    def execute(self, context):
        import subprocess, shutil, tempfile, json, time
        scene = context.scene
        cam = scene.camera
        if not cam:
            self.report({'ERROR'}, "No active camera in scene!")
            return {'CANCELLED'}

        os.makedirs(BLENDER_GUIDES_OUT_DIR, exist_ok=True)
        fps = max(1, int(scene.render.fps))
        f_start = scene.frame_start
        f_end = min(scene.frame_end, f_start + self.max_frames - 1)

        tmp_beauty = tempfile.mkdtemp(prefix="cindy_beauty_")
        tmp_depth = tempfile.mkdtemp(prefix="cindy_depth_")
        beauty_mp4 = os.path.join(BLENDER_GUIDES_OUT_DIR, "blender_bridge_beauty.mp4")
        depth_mp4 = os.path.join(BLENDER_GUIDES_OUT_DIR, "blender_bridge_depth.mp4")

        old_fp = scene.render.filepath
        old_fmt = scene.render.image_settings.file_format
        old_cm = scene.render.image_settings.color_mode
        old_rx, old_ry = scene.render.resolution_x, scene.render.resolution_y
        old_cur = scene.frame_current
        vl = bpy.context.view_layer
        old_override = vl.material_override

        try:
            scene.render.resolution_x = 960
            scene.render.resolution_y = 540
            scene.render.image_settings.file_format = 'PNG'

            # 1. Render Beauty PNG sequence
            scene.render.image_settings.color_mode = 'RGB'
            for f in range(f_start, f_end + 1):
                scene.frame_set(f)
                scene.render.filepath = os.path.join(tmp_beauty, f"frame_{f - f_start:04d}.png")
                bpy.ops.render.render(write_still=True)

            # 2. Render Calibrated 8-bit Depth PNG sequence (Blender 5.3 material_override)
            mat_name = "Cindy_Depth_Override_Mat"
            mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(name=mat_name)
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            nodes.clear()
            n_cam = nodes.new(type='ShaderNodeCameraData')
            n_map = nodes.new(type='ShaderNodeMapRange')
            n_map.clamp = True
            n_map.inputs['From Min'].default_value = 0.45
            n_map.inputs['From Max'].default_value = 8.0
            n_map.inputs['To Min'].default_value = 1.0
            n_map.inputs['To Max'].default_value = 0.0
            n_emit = nodes.new(type='ShaderNodeEmission')
            n_out = nodes.new(type='ShaderNodeOutputMaterial')
            links.new(n_cam.outputs['View Z Depth'], n_map.inputs['Value'])
            links.new(n_map.outputs['Result'], n_emit.inputs['Color'])
            links.new(n_emit.outputs['Emission'], n_out.inputs['Surface'])

            vl.material_override = mat
            scene.render.image_settings.color_mode = 'BW'
            for f in range(f_start, f_end + 1):
                scene.frame_set(f)
                scene.render.filepath = os.path.join(tmp_depth, f"frame_{f - f_start:04d}.png")
                bpy.ops.render.render(write_still=True)

            # 3. Assemble MP4s using ffmpeg (fallback to cv2 if available)
            ffmpeg_exe = shutil.which("ffmpeg")
            if ffmpeg_exe:
                for src_dir, dst_mp4 in [(tmp_beauty, beauty_mp4), (tmp_depth, depth_mp4)]:
                    subprocess.run([
                        ffmpeg_exe, "-y", "-framerate", str(fps),
                        "-i", os.path.join(src_dir, "frame_%04d.png"),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", dst_mp4
                    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                import cv2, glob
                for src_dir, dst_mp4 in [(tmp_beauty, beauty_mp4), (tmp_depth, depth_mp4)]:
                    imgs = sorted(glob.glob(os.path.join(src_dir, "frame_*.png")))
                    if imgs:
                        first = cv2.imread(imgs[0])
                        h, w = first.shape[:2]
                        vw = cv2.VideoWriter(dst_mp4, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
                        for p in imgs:
                            vw.write(cv2.imread(p))
                        vw.release()

            # 4. Update latest_previs_result.json with video_url & depth_video_url
            manifest_path = os.path.join(BLENDER_GUIDES_OUT_DIR, "latest_previs_result.json")
            manifest = {}
            if os.path.exists(manifest_path):
                try:
                    with open(manifest_path, "r", encoding="utf-8") as fh:
                        manifest = json.load(fh)
                except Exception:
                    manifest = {}

            manifest["exported_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            manifest["video_url"] = "/outputs/blender_guides/blender_bridge_beauty.mp4"
            manifest["depth_video_url"] = "/outputs/blender_guides/blender_bridge_depth.mp4"
            manifest["frame_count"] = (f_end - f_start + 1)
            with open(manifest_path, "w", encoding="utf-8") as fh:
                json.dump(manifest, fh, ensure_ascii=False, indent=2)

            self.report({'INFO'}, f"Exported Animated Beauty + Depth MP4 ({f_end - f_start + 1}f @ {fps}fps) to Cindy App!")
            return {'FINISHED'}
        finally:
            vl.material_override = old_override
            scene.render.filepath = old_fp
            scene.render.image_settings.file_format = old_fmt
            scene.render.image_settings.color_mode = old_cm
            scene.render.resolution_x, scene.render.resolution_y = old_rx, old_ry
            scene.frame_set(old_cur)
            shutil.rmtree(tmp_beauty, ignore_errors=True)
            shutil.rmtree(tmp_depth, ignore_errors=True)


class CINDY_PT_DirectorPanel(bpy.types.Panel):
    bl_label = "Cindy AI Director — Studio Suite"
    bl_idname = "CINDY_PT_director_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Cindy Director'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Section 1: Character & Motion Library
        box = layout.box()
        box.label(text="1. Character & Motion Library", icon='OUTLINER_OB_ARMATURE')
        box.prop(scene, "cindy_char_folder", text="Folder")
        box.prop(scene, "cindy_char_motion", text="Clip")
        row = box.row(align=True)
        row.operator("cindy.load_project_character", text="Import Character (1.75m)", icon='IMPORT')

        # Section 2: Physical Staging & Constraints (The New Rigging Core!)
        box_phys = layout.box()
        box_phys.label(text="2. Physical Staging & Bone Sockets", icon='CONSTRAINT')
        row_p = box_phys.row(align=True)
        row_p.operator("cindy.normalize_scale", text="Normalize (1.75m)", icon='ARROW_LEFTRIGHT')
        row_p.operator("cindy.snap_to_floor", text="Snap to Ground (Z=0)", icon='SNAP_ON')
        
        row_socket = box_phys.row(align=True)
        row_socket.operator("cindy.attach_prop_to_hand", text="Attach Prop to Hand", icon='LINKED')
        box_phys.operator("cindy.create_billiard_stage", text="Stage Tournament Billiard Table", icon='TABLE')

        # Section 3: Environment HDRI & 3D Props/Locations
        box_env = layout.box()
        box_env.label(text="3. Environment HDRI & 3D Locations/Props", icon='WORLD')
        box_env.prop(scene, "cindy_env_category", text="HDRI Type")
        box_env.prop(scene, "cindy_env_file", text="HDRI")
        box_env.operator("cindy.apply_environment_world", text="Apply HDRI to Stage", icon='SHADING_RENDERED')
        box_env.separator()
        box_env.prop(scene, "cindy_3d_asset", text="3D Prop/Loc")
        box_env.operator("cindy.load_environment_asset", text="Import 3D Prop / Location (Z=0)", icon='IMPORT')

        # Section 4: Framing & Cinematic Camera
        box_cam = layout.box()
        box_cam.label(text="4. Camera Framing & Viewfinder", icon='CAMERA_DATA')
        row_c = box_cam.row(align=True)
        row_c.operator("cindy.toggle_camera_view", text="Viewfinder", icon='VIEW_CAMERA')
        row_c.operator("cindy.align_cam_to_view", text="Snap to View", icon='VIEW_PAN')
        
        box_cam.label(text="Cinematic Framing Presets:")
        grid = box_cam.grid_flow(columns=2, align=True)
        for shot_id, label, desc in SHOT_PRESET_ITEMS[:6]:
            op = grid.operator("cindy.frame_shot", text=label.split('(')[0].strip())
            op.shot_type = shot_id

        # Section 5: Compound Motion
        box_mov = layout.box()
        box_mov.label(text="5. Compound Cinematic Moves", icon='ANIM')
        box_mov.prop(scene, "cindy_compound_move", text="Preset")
        box_mov.prop(scene, "cindy_move_duration", text="Duration (Frames)")
        box_mov.operator("cindy.apply_compound_move", text="Generate Camera Move", icon='PLAY')

        # Section 6: AI Video Engine & Prompt Bridge (Previz -> Wan2.2 / Seedance / Hunyuan)
        box_ai = layout.box()
        box_ai.label(text="6. AI Video Engine Export (Previz Grounding)", icon='OUTLINER_OB_CAMERA')
        box_ai.prop(scene, "cindy_target_video_engine", text="Engine")
        op_synth = box_ai.operator("cindy.synthesize_video_prompt", text="Export Keyframe + Depth + 7-Part Prompt", icon='TEXT')
        op_synth.target_engine = scene.cindy_target_video_engine
        box_ai.operator("cindy.export_depth_video", text="Export Animated Depth + Beauty MP4 (V2V)", icon='RENDER_ANIMATION')

def register():
    bpy.types.Scene.cindy_compound_move = bpy.props.EnumProperty(items=COMPOUND_MOVE_ITEMS, default='CRANE_PUSH_IN')
    bpy.types.Scene.cindy_move_duration = bpy.props.IntProperty(default=90, min=15, max=600)
    bpy.types.Scene.cindy_beat_duration = bpy.props.IntProperty(default=30, min=5, max=300)
    bpy.types.Scene.cindy_char_folder = bpy.props.EnumProperty(items=_get_character_folder_items)
    bpy.types.Scene.cindy_char_motion = bpy.props.EnumProperty(items=_get_character_motion_items)
    bpy.types.Scene.cindy_env_category = bpy.props.EnumProperty(items=_get_environment_category_items)
    bpy.types.Scene.cindy_env_file = bpy.props.EnumProperty(items=_get_environment_file_items)
    bpy.types.Scene.cindy_3d_asset = bpy.props.EnumProperty(items=_get_3d_asset_items)
    bpy.types.Scene.cindy_target_video_engine = bpy.props.EnumProperty(
        items=[
            ('WAN_2_2', "Wan 2.2 (Alibaba)", "Wan 2.2 Production Prompt"),
            ('SEEDANCE_2_5', "Seedance 2.0 (Doubao)", "Seedance Delimiters"),
            ('HUNYUAN_VIDEO', "HunyuanVideo 13B", "Hunyuan Optics")
        ],
        default='WAN_2_2'
    )

    bpy.utils.register_class(CINDY_OT_AttachPropToHand)
    bpy.utils.utils_register_class = getattr(bpy.utils, "register_class")
    for cls in [
        CINDY_OT_NormalizeScale,
        CINDY_OT_SnapToFloor,
        CINDY_OT_CreateBilliardStage,
        CINDY_OT_TurnObject,
        CINDY_OT_FaceTarget,
        CINDY_OT_ToggleGizmo,
        CINDY_OT_ToggleCameraView,
        CINDY_OT_WalkNavigation,
        CINDY_OT_AlignCamToView,
        CINDY_OT_LockCameraAim,
        CINDY_OT_UnlockCameraAim,
        CINDY_OT_FrameShot,
        CINDY_OT_SetLens,
        CINDY_OT_RecordStartBeat,
        CINDY_OT_RecordNextBeat,
        CINDY_OT_PlayShot,
        CINDY_OT_ResetTimeline,
        CINDY_OT_ApplyCompoundMove,
        CINDY_OT_LoadProjectCharacter,
        CINDY_OT_ApplyEnvironmentWorld,
        CINDY_OT_LoadEnvironmentAsset,
        CINDY_OT_SynthesizeVideoPrompt,
        CINDY_OT_ExportDepthVideo,
        CINDY_PT_DirectorPanel
    ]:
        try:
            bpy.utils.register_class(cls)
        except Exception:
            pass

def unregister():
    for cls in [
        CINDY_PT_DirectorPanel,
        CINDY_OT_ExportDepthVideo,
        CINDY_OT_SynthesizeVideoPrompt,
        CINDY_OT_LoadEnvironmentAsset,
        CINDY_OT_ApplyEnvironmentWorld,
        CINDY_OT_LoadProjectCharacter,
        CINDY_OT_ApplyCompoundMove,
        CINDY_OT_ResetTimeline,
        CINDY_OT_PlayShot,
        CINDY_OT_RecordNextBeat,
        CINDY_OT_RecordStartBeat,
        CINDY_OT_SetLens,
        CINDY_OT_FrameShot,
        CINDY_OT_UnlockCameraAim,
        CINDY_OT_LockCameraAim,
        CINDY_OT_AlignCamToView,
        CINDY_OT_WalkNavigation,
        CINDY_OT_ToggleCameraView,
        CINDY_OT_ToggleGizmo,
        CINDY_OT_FaceTarget,
        CINDY_OT_TurnObject,
        CINDY_OT_CreateBilliardStage,
        CINDY_OT_SnapToFloor,
        CINDY_OT_NormalizeScale,
        CINDY_OT_AttachPropToHand
    ]:
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass

if __name__ == "__main__":
    register()
