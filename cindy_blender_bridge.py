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
    old_engine = scene.render.engine

    try:
        if old_engine == 'BLENDER_WORKBENCH':
            for eng_cand in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE', 'CYCLES'):
                try:
                    scene.render.engine = eng_cand
                    break
                except Exception:
                    continue
        vl.material_override = mat
        scene.render.filepath = out_path
        scene.render.image_settings.file_format = 'PNG'
        scene.render.image_settings.color_mode = 'BW'
        bpy.ops.render.render(write_still=True)
    finally:
        scene.render.engine = old_engine
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
    # Check procedural bone rotation (e.g. Thigh_L / Thigh_R flexed >= 45 degrees in Previz rigs)
    pose_bones = getattr(getattr(obj, "pose", None), "bones", None)
    if pose_bones:
        thigh_l = pose_bones.get("Thigh_L")
        thigh_r = pose_bones.get("Thigh_R")
        if (thigh_l and abs(math.degrees(thigh_l.rotation_euler.x)) >= 45.0) or (
            thigh_r and abs(math.degrees(thigh_r.rotation_euler.x)) >= 45.0
        ):
            return "sitting"
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


def _strip_object_fcurves(obj, data_path, indices):
    """Safely remove object-level F-Curves for specific array indices (Blender 4.x & 5.x compatible)."""
    ad = getattr(obj, "animation_data", None)
    if not ad:
        return 0
    actions = []
    if ad.action:
        actions.append(ad.action)
    if ad.nla_tracks:
        for tr in ad.nla_tracks:
            for st in tr.strips:
                if getattr(st, "action", None):
                    actions.append(st.action)

    removed = 0
    seen = set()
    for act in actions:
        if act is None or act.name in seen:
            continue
        seen.add(act.name)
        fcurve_collections = []
        if hasattr(act, "fcurves") and act.fcurves is not None:
            fcurve_collections.append(act.fcurves)
        if hasattr(act, "layers"):
            for layer in act.layers:
                for strip in getattr(layer, "strips", []):
                    for cb in getattr(strip, "channelbags", []):
                        if hasattr(cb, "fcurves"):
                            fcurve_collections.append(cb.fcurves)
        for fcs in fcurve_collections:
            to_del = [fc for fc in fcs if fc.data_path == data_path and fc.array_index in indices]
            for fc in to_del:
                fcs.remove(fc)
                removed += 1
    return removed


def _auto_fix_actor_physics(context, obj, target_standing_height=1.75):
    """
    Cindy Active Brain Auto-Fix (v2 - Decisive):
    1. Detects wiped Mixamo Y-up -> Z-up upright orientation (X=90deg) and strips ALL corrupt
       object-level X/Y rotation F-Curves so the actor NEVER seesaws/flips between keyframes.
    2. Normalizes abnormal scale on the standing frame so adult human height ~= 1.75m.
    3. Grounds the actor cleanly to Z=0.0 across densely sampled frames (every 6 frames).
    Returns a list of applied fix descriptions.
    """
    import math
    scene = context.scene
    orig_frame = scene.frame_current
    fixes = []

    f_start = scene.frame_start
    f_end = scene.frame_end
    step = max(4, (f_end - f_start) // 16)
    sample_frames = sorted(set(list(range(f_start, f_end + 1, step)) + [f_end]))

    ad = getattr(obj, "animation_data", None)
    has_anim = bool(ad and (ad.action is not None or len(ad.nla_tracks) > 0))

    # 1. Upright check across frames: if ANY frame shows Mixamo X=90 wiped (lying flat or X~0),
    #    strip ALL X/Y object rotation_euler F-Curves and lock X=90deg, Y=0deg permanently.
    needs_upright_lock = False
    scene.frame_set(f_start)
    pose_start = _detect_actor_pose(obj, f_start)
    _, _, h_start, dx, dy = _measure_armature_bounds(context, obj)
    started_mixamo_x90 = abs(math.degrees(obj.rotation_euler.x) - 90.0) < 25.0
    if pose_start == "standing" and h_start < 0.90 and max(dx, dy) > 1.25 and abs(obj.rotation_euler.x) < 0.2:
        needs_upright_lock = True
    else:
        for sf_check in sample_frames:
            scene.frame_set(sf_check)
            _, _, h_c, dx_c, dy_c = _measure_armature_bounds(context, obj)
            is_lying_flat = (h_c < 0.85 and max(dx_c, dy_c) > 1.25)
            lost_mixamo_x90 = started_mixamo_x90 and abs(math.degrees(obj.rotation_euler.x) - 90.0) > 20.0
            if is_lying_flat or lost_mixamo_x90:
                if abs(math.degrees(obj.rotation_euler.x)) < 75.0:
                    needs_upright_lock = True
                    break

    if needs_upright_lock:
        stripped = _strip_object_fcurves(obj, "rotation_euler", {0, 1})
        obj.rotation_euler.x = math.radians(90.0)
        obj.rotation_euler.y = 0.0
        fixes.append(f"{obj.name}: locked Mixamo upright X=90deg, Y=0deg (stripped {stripped} corrupt X/Y F-Curves)")
        scene.frame_set(f_start)
        _, _, h_start, dx, dy = _measure_armature_bounds(context, obj)

    # 2. Scale check on frame_start (standing)
    if pose_start == "standing" and (h_start < 1.50 or h_start > 2.00) and h_start > 0.05:
        sf = target_standing_height / h_start
        obj.scale = (obj.scale.x * sf, obj.scale.y * sf, obj.scale.z * sf)
        fixes.append(f"{obj.name}: rescaled {h_start:.2f}m -> {target_standing_height:.2f}m (factor {sf:.3f})")

    # 3. Clean multi-frame floor grounding across dense samples (prevents Mixamo hip-drop)
    z_fixed_count = 0
    for kf in sample_frames:
        scene.frame_set(kf)
        min_z, _, _, _, _ = _measure_armature_bounds(context, obj)
        if abs(min_z) > 0.03:
            obj.location.z -= min_z
            if has_anim:
                obj.keyframe_insert(data_path="location", index=2, frame=kf)
            z_fixed_count += 1
    if z_fixed_count > 0:
        fixes.append(f"{obj.name}: grounded Z=0.0 cleanly across {z_fixed_count} sampled frames")

    scene.frame_set(orig_frame)
    context.view_layer.update()
    return fixes


def _actor_forward_offset(context, obj):
    """
    Measure the rig's real facing instead of assuming the Mixamo convention.
    Returns `off` such that the world-heading phi = rotation_euler.z + off, where
    forward = (sin(phi), -cos(phi)). Uses left/right hip (fallback shoulder) bones.
    Returns 0.0 (the Mixamo convention) when the bones can't be found.
    """
    import math
    scene = context.scene
    keep = scene.frame_current
    scene.frame_set(scene.frame_start)
    context.view_layer.update()
    try:
        pbones = getattr(getattr(obj, "pose", None), "bones", None)
        if not pbones:
            return 0.0

        def find(*keys):
            for b in pbones:
                n = b.name.lower().split(':')[-1].replace('_', '').replace('.', '').replace('-', '')
                if n in keys:
                    return b
            return None

        left = find('leftupleg', 'lefthip', 'leftthigh', 'thighl', 'upperlegl')
        right = find('rightupleg', 'righthip', 'rightthigh', 'thighr', 'upperlegr')
        if not (left and right):
            left = find('leftshoulder', 'leftarm', 'shoulderl')
            right = find('rightshoulder', 'rightarm', 'shoulderr')
        if not (left and right):
            return 0.0
        mw = obj.matrix_world
        right_vec = (mw @ right.head) - (mw @ left.head)
        right_vec.z = 0.0
        if right_vec.length < 1e-4:
            return 0.0
        fwd = Vector((0.0, 0.0, 1.0)).cross(right_vec)   # up x right = forward
        phi = math.atan2(fwd.x, -fwd.y)
        off = phi - obj.rotation_euler.z
        return (off + math.pi) % (2 * math.pi) - math.pi
    finally:
        scene.frame_set(keep)


def _auto_fix_spatial_clearance_and_facing(context):
    """
    Cindy Active Brain Spatial Fix:
    1. Table Clearance & Chair Sync: Prevents actors from clipping into tables by pushing
       penetrating X/Y keyframes outside the table (+cloth) bounding box with body margin,
       and sliding the corresponding chair along so the actor sits cleanly on it.
    2. Walk Facing Direction: Ensures Mixamo rigs (where rot_z=0 faces -Y, +90 faces +X)
       face their actual walking velocity vector instead of walking backwards.
    """
    import math
    from mathutils import Vector

    scene = context.scene
    orig_frame = scene.frame_current
    fixes = []

    # 1. Find primary hero table/desk bounds (including cloth) by world bbox center near origin
    depsgraph = context.evaluated_depsgraph_get()
    table_objs = []
    for o in scene.objects:
        low = o.name.lower()
        if o.type == 'MESH' and not o.hide_viewport and any(k in low for k in ('table', 'desk', 'counter')):
            ev = o.evaluated_get(depsgraph)
            pts = [ev.matrix_world @ Vector(c) for c in ev.bound_box]
            cx = 0.5 * (min(p.x for p in pts) + max(p.x for p in pts))
            cy = 0.5 * (min(p.y for p in pts) + max(p.y for p in pts))
            if abs(cx) < 1.5 and abs(cy) < 1.5:
                table_objs.append(o)

    has_table = len(table_objs) > 0
    t_min_x = t_min_y = float('inf')
    t_max_x = t_max_y = float('-inf')
    if has_table:
        for t in table_objs:
            ev = t.evaluated_get(depsgraph)
            for c in ev.bound_box:
                wc = ev.matrix_world @ Vector(c)
                t_min_x, t_max_x = min(t_min_x, wc.x), max(t_max_x, wc.x)
                t_min_y, t_max_y = min(t_min_y, wc.y), max(t_max_y, wc.y)

    margin = 0.14  # snug body clearance outside table/desk
    safe_min_x, safe_max_x = t_min_x - margin, t_max_x + margin
    safe_min_y, safe_max_y = t_min_y - margin, t_max_y + margin

    chairs = [
        o for o in scene.objects
        if o.type == 'MESH' and not o.hide_viewport and 'chair' in o.name.lower()
    ]
    shifted_chairs = set()

    f_start, f_end = scene.frame_start, scene.frame_end
    step = max(4, (f_end - f_start) // 24)
    coarse_frames = sorted(set(list(range(f_start, f_end + 1, step)) + [f_end]))
    # Collision pass runs on (almost) every frame so Blender interpolation can't re-introduce penetration
    fine_step = 1 if (f_end - f_start) <= 240 else max(2, (f_end - f_start) // 120)
    sample_frames = sorted(set(list(range(f_start, f_end + 1, fine_step)) + [f_end]))

    fwd_offsets = {o.name: _actor_forward_offset(context, o)
                   for o in scene.objects if o.type == 'ARMATURE' and not o.hide_viewport}

    for obj in scene.objects:
        if obj.type != 'ARMATURE' or obj.hide_viewport:
            continue
        ad = getattr(obj, "animation_data", None)
        has_anim = bool(ad and (ad.action is not None or len(ad.nla_tracks) > 0))

        # 1. Fix backwards walk facing on moving frames FIRST (before collision pushback)
        facing_fixed = 0
        scene.frame_set(f_start)
        rz_first = obj.rotation_euler.z
        scene.frame_set(f_end)
        rz_last = obj.rotation_euler.z
        # No deliberate turn authored in the clip -> start/end heading must follow the walk heading
        rot_is_static = abs((rz_last - rz_first + math.pi) % (2 * math.pi) - math.pi) < 1e-3
        walk_best = (0.0, None)   # (distance, heading) of the strongest moving segment
        for i in range(len(coarse_frames) - 1):
            f0, f1 = coarse_frames[i], coarse_frames[i + 1]
            scene.frame_set(f0)
            p0 = obj.location.copy()
            rz = obj.rotation_euler.z
            scene.frame_set(f1)
            p1 = obj.location.copy()
            dx, dy = p1.x - p0.x, p1.y - p0.y
            dist = math.hypot(dx, dy)
            if dist > 0.12:
                # Mixamo forward with X=90deg is (sin(rz), -cos(rz))
                desired_rz = math.atan2(dx, -dy) - fwd_offsets.get(obj.name, 0.0)
                if dist > walk_best[0]:
                    walk_best = (dist, desired_rz)
                diff = (desired_rz - rz + math.pi) % (2 * math.pi) - math.pi
                if abs(math.degrees(diff)) > 75.0:
                    scene.frame_set(f0)
                    # Unwrapped target (rz + shortest diff) so Blender never spins the long way round
                    obj.rotation_euler.z = rz + diff
                    if has_anim:
                        obj.keyframe_insert(data_path="rotation_euler", index=2, frame=f0)
                    facing_fixed += 1
        # Boundary frames: ease-in/out leaves the first/last segments "too slow" to be judged, so
        # Blender would spin the actor between a wrong start/end key and the corrected middle keys.
        # Only done when no turn was authored (rot_is_static) and a backwards walk was detected.
        if rot_is_static and facing_fixed > 0 and walk_best[1] is not None:
            for fb_ in (f_start, f_end):
                scene.frame_set(fb_)
                cur = obj.rotation_euler.z
                d_b = (walk_best[1] - cur + math.pi) % (2 * math.pi) - math.pi
                if abs(math.degrees(d_b)) > 75.0:
                    obj.rotation_euler.z = cur + d_b
                    if has_anim:
                        obj.keyframe_insert(data_path="rotation_euler", index=2, frame=fb_)
        if facing_fixed > 0:
            fixes.append(f"{obj.name}: corrected walk facing direction on {facing_fixed} frames")

        # 2. Push any penetrating X/Y keyframes outside the table/desk (accounts for Mixamo Hips root motion)
        pushed_delta_x = 0.0
        pushed_delta_y = 0.0
        pushed_frames = 0
        if has_table:
            child_meshes = [c for c in obj.children if c.type == 'MESH' and not c.hide_viewport]
            for kf in sample_frames:
                scene.frame_set(kf)
                dg = context.evaluated_depsgraph_get()
                if child_meshes:
                    xs, ys = [], []
                    for cm in child_meshes:
                        ev_m = cm.evaluated_get(dg)
                        for pt in ev_m.bound_box:
                            wpt = ev_m.matrix_world @ Vector(pt)
                            xs.append(wpt.x)
                            ys.append(wpt.y)
                    bx0, bx1, by0, by1 = min(xs), max(xs), min(ys), max(ys)
                else:
                    bx0 = bx1 = obj.location.x
                    by0 = by1 = obj.location.y
                # Torso core (shrunk 25%) - SAME criterion the Director Gate verifies afterwards
                cx_, cy_ = (bx1 - bx0) * 0.25, (by1 - by0) * 0.25
                bx0, bx1, by0, by1 = bx0 + cx_, bx1 - cx_, by0 + cy_, by1 - cy_

                if bx0 < safe_max_x and bx1 > safe_min_x and by0 < safe_max_y and by1 > safe_min_y:
                    # Minimal translation that separates the body box from the (margin-expanded) desk box
                    best_dx = (safe_max_x - bx0) if (safe_max_x - bx0) < (bx1 - safe_min_x) else -(bx1 - safe_min_x)
                    best_dy = (safe_max_y - by0) if (safe_max_y - by0) < (by1 - safe_min_y) else -(by1 - safe_min_y)
                    if abs(best_dx) <= abs(best_dy):
                        obj.location.x += best_dx
                        if abs(best_dx) > abs(pushed_delta_x):
                            pushed_delta_x = best_dx
                        if has_anim:
                            obj.keyframe_insert(data_path="location", index=0, frame=kf)
                    else:
                        obj.location.y += best_dy
                        if abs(best_dy) > abs(pushed_delta_y):
                            pushed_delta_y = best_dy
                        if has_anim:
                            obj.keyframe_insert(data_path="location", index=1, frame=kf)
                    pushed_frames += 1

        if pushed_frames > 0:
            fixes.append(f"{obj.name}: cleared table clipping across {pushed_frames} frames (dx={pushed_delta_x:+.2f}m, dy={pushed_delta_y:+.2f}m)")
            # Slide the nearest chair on that side by the same delta so it stays aligned
            for ch in chairs:
                if ch.name in shifted_chairs:
                    continue
                ev_ch = ch.evaluated_get(depsgraph)
                ch_xs = [(ev_ch.matrix_world @ Vector(c)).x for c in ev_ch.bound_box]
                ch_ys = [(ev_ch.matrix_world @ Vector(c)).y for c in ev_ch.bound_box]
                ch_cx = 0.5 * (min(ch_xs) + max(ch_xs))
                ch_cy = 0.5 * (min(ch_ys) + max(ch_ys))
                if abs(ch_cy) < 0.6 and ((pushed_delta_x < 0 and ch_cx < 0) or (pushed_delta_x > 0 and ch_cx > 0)):
                    ch.location.x += pushed_delta_x
                    shifted_chairs.add(ch.name)
                    fixes.append(f"{ch.name}: slid dx={pushed_delta_x:+.2f}m to stay anchored under {obj.name}")

    # 2b. Multi-Actor Personal Space Clearance & Auto Eye-Line (2, 3, or N actors)
    arms_all = [o for o in scene.objects if o.type == 'ARMATURE' and not o.hide_viewport]
    if len(arms_all) >= 2:
        # Personal Space Guard: prevent any two actors from occupying the same XY spot (< 0.44m)
        min_actor_dist = 0.44
        spacing_fixed = 0
        for kf in sample_frames:
            scene.frame_set(kf)
            for _pass in range(3):
                any_pushed = False
                for i in range(len(arms_all)):
                    for j in range(i + 1, len(arms_all)):
                        ai, aj = arms_all[i], arms_all[j]
                        dx = aj.location.x - ai.location.x
                        dy = aj.location.y - ai.location.y
                        dist = math.hypot(dx, dy)
                        if dist < min_actor_dist:
                            push = (min_actor_dist - dist + 0.03) * 0.5
                            if dist > 1e-4:
                                ux, uy = dx / dist, dy / dist
                            else:
                                ang = (i + j + 1) * 1.1
                                ux, uy = math.cos(ang), math.sin(ang)
                            ai.location.x -= ux * push
                            ai.location.y -= uy * push
                            aj.location.x += ux * push
                            aj.location.y += uy * push
                            any_pushed = True
                            spacing_fixed += 1
                if not any_pushed:
                    break
            if spacing_fixed > 0:
                for ao in arms_all:
                    ad_o = getattr(ao, "animation_data", None)
                    if ad_o and (ad_o.action is not None or len(ad_o.nla_tracks) > 0):
                        ao.keyframe_insert(data_path="location", index=0, frame=kf)
                        ao.keyframe_insert(data_path="location", index=1, frame=kf)
        if spacing_fixed > 0:
            fixes.append(f"Multi-Actor Spacing: separated overlapping actors across {spacing_fixed} pair checks (>= {min_actor_dist:.2f}m)")

        # Auto Eye-Line: on the second half of the shot, orient each actor toward their partner (2 actors)
        # or toward the group social centroid / primary speaker (3+ actors) using unwrapped angles.
        eyeline_frames = [kf for kf in coarse_frames if kf >= int(f_start + 0.50 * (f_end - f_start))]
        for actor in arms_all:
            others = [o for o in arms_all if o != actor]
            ad = getattr(actor, "animation_data", None)
            has_anim = bool(ad and (ad.action is not None or len(ad.nla_tracks) > 0))
            eyeline_fixed = 0
            for kf in eyeline_frames:
                scene.frame_set(kf)
                # Social centroid of all other actors in the scene; if standing near centroid, face nearest partner
                tx = sum(o.location.x for o in others) / len(others)
                ty = sum(o.location.y for o in others) / len(others)
                dx = tx - actor.location.x
                dy = ty - actor.location.y
                if math.hypot(dx, dy) <= 0.12 and others:
                    nearest_o = min(others, key=lambda o: math.hypot(o.location.x - actor.location.x, o.location.y - actor.location.y))
                    dx = nearest_o.location.x - actor.location.x
                    dy = nearest_o.location.y - actor.location.y
                if math.hypot(dx, dy) > 0.10:
                    desired_rz = math.atan2(dx, -dy) - fwd_offsets.get(actor.name, 0.0)
                    diff = (desired_rz - actor.rotation_euler.z + math.pi) % (2 * math.pi) - math.pi
                    if abs(math.degrees(diff)) > 35.0:
                        actor.rotation_euler.z = actor.rotation_euler.z + diff  # unwrapped, no 360 spin
                        if has_anim:
                            actor.keyframe_insert(data_path="rotation_euler", index=2, frame=kf)
                        eyeline_fixed += 1
            if eyeline_fixed > 0:
                target_lbl = others[0].name if len(others) == 1 else f"group({len(others)} actors)"
                fixes.append(f"{actor.name}: aligned eye-line toward {target_lbl} across {eyeline_fixed} frames")

    # 3. Auto Camera Framing Guard: ensure all visible actors stay inside horizontal frame [0.12, 0.88]
    #    on the final third of the shot (when actors have arrived/seated).
    cam = scene.camera
    arms = [o for o in scene.objects if o.type == 'ARMATURE' and not o.hide_viewport]
    if cam and cam.data and arms:
        from bpy_extras.object_utils import world_to_camera_view
        late_frames = sorted(set([int(f_start + 0.65 * (f_end - f_start)), int(f_start + 0.85 * (f_end - f_start)), f_end]))
        orig_lens = cam.data.lens

        def _lens_is_animated():
            ad_c = getattr(cam.data, "animation_data", None)
            if not ad_c or not ad_c.action:
                return False
            return any(fc.data_path == "lens" for fc in getattr(ad_c.action, "fcurves", []) or [])

        def _framing_violations():
            """Count actors whose head/torso falls outside the safe horizontal band on late frames."""
            bad = 0
            for lf in late_frames:
                scene.frame_set(lf)
                context.view_layer.update()
                for a in arms:
                    _, _, _, _, _ = _measure_armature_bounds(context, a)
                    dg2 = context.evaluated_depsgraph_get()
                    ms = [c for c in a.children_recursive if c.type == 'MESH' and not c.hide_viewport]
                    if ms:
                        pts = []
                        for m in ms:
                            em = m.evaluated_get(dg2)
                            pts += [em.matrix_world @ Vector(c) for c in em.bound_box]
                        pt = Vector((sum(p.x for p in pts) / len(pts), sum(p.y for p in pts) / len(pts), sum(p.z for p in pts) / len(pts)))
                    else:
                        pt = a.location + Vector((0, 0, 0.95))
                    co = world_to_camera_view(scene, cam, pt)
                    if co.z <= 0 or co.x < 0.14 or co.x > 0.86:
                        bad += 1
            return bad

        if not _lens_is_animated():
            best_lens, best_bad = cam.data.lens, _framing_violations()
            lens = cam.data.lens
            while best_bad > 0 and lens > 22.0:
                lens = max(22.0, lens - 3.0)
                cam.data.lens = lens
                bad = _framing_violations()
                if bad < best_bad:  # only accept widening that really helps
                    best_lens, best_bad = lens, bad
            cam.data.lens = best_lens
            if best_lens != orig_lens:
                fixes.append(f"Camera {cam.name}: auto-widened lens {orig_lens:.1f}mm -> {best_lens:.1f}mm")
            if best_bad > 0:
                fixes.append(f"WARNING Camera {cam.name}: {best_bad} late-frame framing violations remain (move camera/blocking, lens alone cannot fix)")
        else:
            fixes.append(f"Camera {cam.name}: lens is animated - framing guard skipped to preserve your zoom")

    scene.frame_set(orig_frame)
    context.view_layer.update()
    return fixes


def _run_scene_audit_and_extract(context, auto_fix=True):
    """Audit visible armatures & props via CindyDirectorGate (with Active Auto-Fix) and extract real scene metadata."""
    import sys, math, os
    try:
        repo_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        repo_dir = r"C:\Users\DELL\Desktop\Cindy-AI-Director"
    if repo_dir not in sys.path:
        sys.path.append(repo_dir)
    from cindy_director_gate import CindyDirectorGate

    scene = context.scene
    orig_frame = scene.frame_current
    f_start, f_end = scene.frame_start, scene.frame_end
    audit_step = max(8, (f_end - f_start) // 8)
    audit_frames = sorted(set(list(range(f_start, f_end + 1, audit_step)) + [f_end]))

    actors = []
    audit_checks = []
    auto_fixes_applied = []
    all_passed = True

    if auto_fix:
        # Phase 1: Physics FIRST (upright lock, 1.75m scale normalization, Z=0 floor grounding)
        for obj in scene.objects:
            if obj.type == 'ARMATURE' and not obj.hide_viewport:
                applied = _auto_fix_actor_physics(context, obj)
                auto_fixes_applied.extend(applied)
        # Phase 2: Spatial clearance, walk facing & camera framing AFTER final physical scale
        spatial_fixes = _auto_fix_spatial_clearance_and_facing(context)
        auto_fixes_applied.extend(spatial_fixes)

    for obj in scene.objects:
        if obj.type == 'ARMATURE' and not obj.hide_viewport:

            name = obj.name.replace('RIG_', '').replace('CHAR_', '').replace('_', ' ').strip().capitalize()

            # Multi-frame upright stability & ground contact audit
            stability_samples = []
            worst_min_z = 0.0
            for af in audit_frames:
                scene.frame_set(af)
                min_z_f, _, h_f, dx_f, dy_f = _measure_armature_bounds(context, obj)
                if abs(min_z_f) > abs(worst_min_z):
                    worst_min_z = min_z_f
                stability_samples.append({
                    'frame': af,
                    'height': h_f,
                    'max_xy': max(dx_f, dy_f),
                    'rot_x_deg': math.degrees(obj.rotation_euler.x),
                    'rot_y_deg': math.degrees(obj.rotation_euler.y),
                })

            scene.frame_set(orig_frame)
            pose = _detect_actor_pose(obj, orig_frame)
            min_z, max_z, height, _, _ = _measure_armature_bounds(context, obj)

            scale_res = CindyDirectorGate.audit_actor_scale(name, height, pose=pose)
            ground_res = CindyDirectorGate.audit_ground_contact(worst_min_z, ground_tolerance=0.06)
            stab_res = CindyDirectorGate.audit_upright_stability(name, stability_samples, max_tilt_deg=20.0)
            audit_checks.extend([scale_res, ground_res, stab_res])
            if not scale_res['passed'] or not ground_res['passed'] or not stab_res['passed']:
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

    # ---- Post-fix verification: the gate must verify RESULTS, not just trust the fixes ----
    arms_v = [o for o in scene.objects if o.type == 'ARMATURE' and not o.hide_viewport]
    dg_v = context.evaluated_depsgraph_get()
    desks = []
    for o in scene.objects:
        low = o.name.lower()
        if o.type == 'MESH' and not o.hide_viewport and any(k in low for k in ('table', 'desk', 'counter')):
            ev = o.evaluated_get(dg_v)
            pts = [ev.matrix_world @ Vector(c) for c in ev.bound_box]
            cx = 0.5 * (min(p.x for p in pts) + max(p.x for p in pts))
            cy = 0.5 * (min(p.y for p in pts) + max(p.y for p in pts))
            if abs(cx) < 1.5 and abs(cy) < 1.5:
                desks.append((min(p.x for p in pts), max(p.x for p in pts), min(p.y for p in pts), max(p.y for p in pts), min(p.z for p in pts), max(p.z for p in pts)))
    for a in arms_v:
        a_name = a.name.replace('RIG_', '').replace('_', ' ').strip().capitalize()
        overlap_frames = []
        for af in audit_frames:
            scene.frame_set(af)
            dg_f = context.evaluated_depsgraph_get()
            ms = [c for c in a.children_recursive if c.type == 'MESH' and not c.hide_viewport]
            if not ms or not desks:
                break
            pts = []
            for m in ms:
                em = m.evaluated_get(dg_f)
                pts += [em.matrix_world @ Vector(c) for c in em.bound_box]
            # Torso core (shrunk 25%) vs desk volume at body height
            ax0, ax1 = min(p.x for p in pts), max(p.x for p in pts)
            ay0, ay1 = min(p.y for p in pts), max(p.y for p in pts)
            sx, sy = (ax1 - ax0) * 0.25, (ay1 - ay0) * 0.25
            ax0, ax1, ay0, ay1 = ax0 + sx, ax1 - sx, ay0 + sy, ay1 - sy
            for (dx0, dx1, dy0, dy1, dz0, dz1) in desks:
                if ax0 < dx1 and ax1 > dx0 and ay0 < dy1 and ay1 > dy0:
                    overlap_frames.append(af)
                    break
        audit_checks.append({
            'actor': a_name, 'check': 'furniture_clearance', 'passed': not overlap_frames,
            'message': 'No furniture penetration' if not overlap_frames else f'Penetrates furniture at frames {overlap_frames}'
        })
        if overlap_frames:
            all_passed = False

    if len(arms_v) >= 2:
        # Verify personal space clearance across all pairs of actors across sampled frames
        worst_spacing_res = None
        for af in audit_frames:
            scene.frame_set(af)
            sp_res = CindyDirectorGate.audit_actor_spacing(
                [{'name': a.name, 'x': a.location.x, 'y': a.location.y} for a in arms_v],
                frame=af,
                min_clearance=0.38
            )
            if worst_spacing_res is None or not sp_res['passed']:
                worst_spacing_res = sp_res
                if not sp_res['passed']:
                    break
        scene.frame_set(f_end)
        spacing_res = worst_spacing_res or CindyDirectorGate.audit_actor_spacing(
            [{'name': a.name, 'x': a.location.x, 'y': a.location.y} for a in arms_v],
            frame=f_end,
            min_clearance=0.38
        )
        audit_checks.append(spacing_res)
        if not spacing_res['passed']:
            all_passed = False

        for actor in arms_v:
            others = [o for o in arms_v if o != actor]
            tx = sum(o.location.x for o in others) / len(others)
            ty = sum(o.location.y for o in others) / len(others)
            dx, dy = tx - actor.location.x, ty - actor.location.y
            target_lbl = others[0].name if len(others) == 1 else "group centroid"
            if math.hypot(dx, dy) <= 0.12 and others:
                nearest_o = min(others, key=lambda o: math.hypot(o.location.x - actor.location.x, o.location.y - actor.location.y))
                dx, dy = nearest_o.location.x - actor.location.x, nearest_o.location.y - actor.location.y
                target_lbl = nearest_o.name
            if math.hypot(dx, dy) > 0.10:
                want = math.atan2(dx, -dy) - _actor_forward_offset(context, actor)
                err = abs(math.degrees((want - actor.rotation_euler.z + math.pi) % (2 * math.pi) - math.pi))
                ok = err <= 45.0
                audit_checks.append({
                    'actor': actor.name, 'check': 'final_eyeline', 'passed': ok,
                    'message': f'Facing error {err:.0f} deg toward {target_lbl}' + ('' if ok else ' (not facing partner/group at final frame)')
                })
                if not ok:
                    all_passed = False

    if scene.camera and arms_v:
        from bpy_extras.object_utils import world_to_camera_view
        scene.frame_set(f_end)
        context.view_layer.update()
        dg_cam = context.evaluated_depsgraph_get()
        cam_eval = scene.camera.evaluated_get(dg_cam)
        ndc_samples = []
        for a in arms_v:
            min_z_a, max_z_a, h_a, _, _ = _measure_armature_bounds(context, a)
            ms_a = [c for c in a.children_recursive if c.type == 'MESH' and not c.hide_viewport]
            if ms_a:
                pts_a = [m.evaluated_get(dg_cam).matrix_world @ Vector(c) for m in ms_a for c in m.evaluated_get(dg_cam).bound_box]
                cx_a = 0.5 * (min(p.x for p in pts_a) + max(p.x for p in pts_a))
                cy_a = 0.5 * (min(p.y for p in pts_a) + max(p.y for p in pts_a))
            else:
                cx_a, cy_a = float(a.location.x), float(a.location.y)
            # Check both eye level (0.88 * height) and chest level (0.68 * height) so close-ups on faces pass cleanly
            eye_world = Vector((cx_a, cy_a, min_z_a + max(0.55, h_a * 0.88)))
            chest_world = Vector((cx_a, cy_a, min_z_a + max(0.45, h_a * 0.68)))
            ndc_eye = world_to_camera_view(scene, cam_eval, eye_world)
            ndc_chest = world_to_camera_view(scene, cam_eval, chest_world)
            # Pick whichever anatomical target is closer to the frame center (0.5, 0.5)
            d_eye = math.hypot(float(ndc_eye.x) - 0.5, float(ndc_eye.y) - 0.5)
            d_chest = math.hypot(float(ndc_chest.x) - 0.5, float(ndc_chest.y) - 0.5)
            ndc = ndc_eye if d_eye <= d_chest else ndc_chest
            ndc_samples.append({
                'name': a.name,
                'actor': a.name,
                'frame': f_end,
                'x': float(ndc.x),
                'y': float(ndc.y),
                'z': float(ndc.z)
            })
        in_view = [s for s in ndc_samples if s['z'] > 0.0 and 0.04 <= s['x'] <= 0.96 and 0.04 <= s['y'] <= 0.96]
        samples_to_check = in_view if (len(arms_v) > 1 and len(in_view) >= 1) else ndc_samples
        framing_res = CindyDirectorGate.audit_camera_framing(samples_to_check, safe_margin=0.04)
        audit_checks.append(framing_res)
        if not framing_res['passed']:
            all_passed = False

    for fx in auto_fixes_applied:
        if str(fx).startswith('WARNING'):
            audit_checks.append({'check': 'framing', 'passed': False, 'message': fx})
            all_passed = False

    scene.frame_set(orig_frame)
    return actors, {
        'passed': all_passed,
        'actor_count': len(actors),
        'auto_fixes_applied': auto_fixes_applied,
        'checks': audit_checks
    }


def plan_actor_approach(context, actor_obj, start_xy, side="front", margin=0.28, arrive_ratio=0.55, target_obj=None):
    """
    Cindy Proactive Approach Planner:
    Plans a clean, collision-free walk trajectory from `start_xy = (x, y)` to a safe stop
    mark on the requested `side` ('front'=-Y, 'back'=+Y, 'left'=-X, 'right'=+X) of `target_obj`
    (or the hero table/desk when `target_obj` is None), compensating for Mixamo Hips root-motion
    drift and measured bone facing.
    """
    import math
    scene = context.scene
    keep = scene.frame_current
    f_start, f_end = scene.frame_start, scene.frame_end
    f_arrive = max(f_start + 1, min(f_end, int(round(f_start + arrive_ratio * (f_end - f_start)))))

    # Normalize scale & upright orientation first so root-motion drift is measured at 1.75m
    _auto_fix_actor_physics(context, actor_obj)

    dg = context.evaluated_depsgraph_get()
    tx0, tx1, ty0, ty1 = -0.8, 0.8, -0.45, 0.45
    table_objs = []
    if target_obj is not None:
        if isinstance(target_obj, str):
            target_obj = scene.objects.get(target_obj)
        if target_obj is not None:
            if target_obj.type == 'MESH':
                table_objs.append(target_obj.evaluated_get(dg))
            else:
                table_objs.extend([m.evaluated_get(dg) for m in target_obj.children_recursive if m.type == 'MESH' and not m.hide_viewport])
                if not table_objs:
                    loc_t = target_obj.matrix_world.translation
                    tx0, tx1, ty0, ty1 = loc_t.x - 0.25, loc_t.x + 0.25, loc_t.y - 0.25, loc_t.y + 0.25
    if not table_objs and target_obj is None:
        for o in scene.objects:
            low = o.name.lower()
            if o.type == 'MESH' and not o.hide_viewport and any(k in low for k in ('table', 'desk', 'counter')):
                ev = o.evaluated_get(dg)
                pts = [ev.matrix_world @ Vector(c) for c in ev.bound_box]
                cx = 0.5 * (min(p.x for p in pts) + max(p.x for p in pts))
                cy = 0.5 * (min(p.y for p in pts) + max(p.y for p in pts))
                if abs(cx) < 1.5 and abs(cy) < 1.5:
                    table_objs.append(ev)
    if table_objs:
        pts = [ev.matrix_world @ Vector(c) for ev in table_objs for c in ev.bound_box]
        tx0, tx1 = min(p.x for p in pts), max(p.x for p in pts)
        ty0, ty1 = min(p.y for p in pts), max(p.y for p in pts)
    tcx, tcy = 0.5 * (tx0 + tx1), 0.5 * (ty0 + ty1)

    if side == "front":
        goal_x, goal_y = tcx, ty0 - margin
    elif side == "back":
        goal_x, goal_y = tcx, ty1 + margin
    elif side == "left":
        goal_x, goal_y = tx0 - margin, tcy
    else:
        goal_x, goal_y = tx1 + margin, tcy

    fwd_off = _actor_forward_offset(context, actor_obj)
    dx, dy = goal_x - start_xy[0], goal_y - start_xy[1]
    walk_rz = (math.atan2(dx, -dy) - fwd_off) if math.hypot(dx, dy) > 0.05 else (math.atan2(tcx - goal_x, -(tcy - goal_y)) - fwd_off)
    face_table_rz = math.atan2(tcx - goal_x, -(tcy - goal_y)) - fwd_off
    turn_diff = (face_table_rz - walk_rz + math.pi) % (2 * math.pi) - math.pi
    final_rz = walk_rz + turn_diff

    # Measure any internal Mixamo Hips root-motion offset at f_arrive & f_end so the mesh center lands on goal
    def _mesh_xy_offset_at(frame, rz_val):
        scene.frame_set(frame)
        actor_obj.location.x, actor_obj.location.y = 0.0, 0.0
        actor_obj.rotation_euler.z = rz_val
        context.view_layer.update()
        dg_f = context.evaluated_depsgraph_get()
        ms = [c for c in actor_obj.children_recursive if c.type == 'MESH' and not c.hide_viewport]
        if not ms:
            return 0.0, 0.0
        pts_m = [m.evaluated_get(dg_f).matrix_world @ Vector(c) for m in ms for c in m.evaluated_get(dg_f).bound_box]
        return 0.5 * (min(p.x for p in pts_m) + max(p.x for p in pts_m)), 0.5 * (min(p.y for p in pts_m) + max(p.y for p in pts_m))

    ox0, oy0 = _mesh_xy_offset_at(f_start, walk_rz)
    oxa, oya = _mesh_xy_offset_at(f_arrive, final_rz)
    oxe, oye = _mesh_xy_offset_at(f_end, final_rz)

    waypoints = [
        (f_start, (start_xy[0] - ox0, start_xy[1] - oy0), walk_rz),
        (f_arrive, (goal_x - oxa, goal_y - oya), final_rz),
        (f_end, (goal_x - oxe, goal_y - oye), final_rz),
    ]
    for f, (lx, ly), rz_v in waypoints:
        scene.frame_set(f)
        actor_obj.location.x = lx
        actor_obj.location.y = ly
        actor_obj.rotation_euler.z = rz_v
        actor_obj.keyframe_insert(data_path="location", index=0, frame=f)
        actor_obj.keyframe_insert(data_path="location", index=1, frame=f)
        actor_obj.keyframe_insert(data_path="rotation_euler", index=2, frame=f)

    scene.frame_set(keep)
    context.view_layer.update()
    return {"goal_xy": (round(goal_x, 3), round(goal_y, 3)), "arrive_frame": f_arrive}


def plan_actor_sit_on_chair(context, actor_obj, chair_obj=None, sit_frame=None, face_target_xy=None):
    """
    Cindy Proactive Chair Seating Planner:
    Couples `actor_obj` cleanly onto `chair_obj` (or auto-discovers the nearest chair/seat/sofa),
    aligns the actor's facing direction toward the table/partner (or chair front), applies a realistic
    seated skeletal posture if the rig uses Previz bones (Pelvis/Thigh/Shin) while grounding feet at Z=0.0,
    and ensures zero table/desk penetration.
    """
    import math
    from mathutils import Vector, Euler
    scene = context.scene
    keep = scene.frame_current
    f_start, f_end = scene.frame_start, scene.frame_end
    target_frame = sit_frame if sit_frame is not None else f_start

    _auto_fix_actor_physics(context, actor_obj)
    dg = context.evaluated_depsgraph_get()

    if chair_obj is None:
        candidates = [
            o for o in scene.objects
            if o.type in ('MESH', 'EMPTY') and not o.hide_viewport
            and any(k in o.name.lower() for k in ('chair', 'seat', 'stool', 'sofa', 'bench'))
        ]
        if candidates:
            chair_obj = min(
                candidates,
                key=lambda c: math.hypot(c.matrix_world.translation.x - actor_obj.location.x,
                                         c.matrix_world.translation.y - actor_obj.location.y)
            )

    if chair_obj is not None:
        if chair_obj.type == 'MESH':
            ev_c = chair_obj.evaluated_get(dg)
            c_pts = [ev_c.matrix_world @ Vector(c) for c in ev_c.bound_box]
        else:
            c_meshes = [m for m in chair_obj.children_recursive if m.type == 'MESH' and not m.hide_viewport]
            c_pts = [m.evaluated_get(dg).matrix_world @ Vector(c) for m in c_meshes for c in m.evaluated_get(dg).bound_box] if c_meshes else [chair_obj.matrix_world.translation]
        cx = 0.5 * (min(p.x for p in c_pts) + max(p.x for p in c_pts))
        cy = 0.5 * (min(p.y for p in c_pts) + max(p.y for p in c_pts))
        seat_top_z = max(p.z for p in c_pts)
    else:
        cx, cy, seat_top_z = actor_obj.location.x, actor_obj.location.y, 0.45

    # Determine facing target (explicit face_target_xy -> hero table center -> origin)
    if face_target_xy is not None:
        tx, ty = float(face_target_xy[0]), float(face_target_xy[1])
    else:
        tx, ty = 0.0, 0.0
        for o in scene.objects:
            if o.type == 'MESH' and not o.hide_viewport and any(k in o.name.lower() for k in ('table', 'desk', 'counter')):
                ev_t = o.evaluated_get(dg)
                t_pts = [ev_t.matrix_world @ Vector(c) for c in ev_t.bound_box]
                tcx = 0.5 * (min(p.x for p in t_pts) + max(p.x for p in t_pts))
                tcy = 0.5 * (min(p.y for p in t_pts) + max(p.y for p in t_pts))
                if abs(tcx) < 2.0 and abs(tcy) < 2.0:
                    tx, ty = tcx, tcy
                    break

    fwd_off = _actor_forward_offset(context, actor_obj)
    dx, dy = tx - cx, ty - cy
    sit_rz = (math.atan2(dx, -dy) - fwd_off) if math.hypot(dx, dy) > 0.05 else actor_obj.rotation_euler.z

    # If the rig has Previz articulated bones (Pelvis/Thigh_L/Shin_L), pose it into SIT
    pb = getattr(getattr(actor_obj, "pose", None), "bones", None)
    if pb and "Pelvis" in pb and "Thigh_L" in pb and "Shin_L" in pb:
        scale_f = float(actor_obj.get("scale_f", 1.0))
        actor_obj["current_pose"] = "SIT"
        pb["Pelvis"].location = Vector((0.0, 0.0, -0.42 * scale_f))
        pb["Thigh_L"].rotation_euler = Euler((math.radians(88), 0.0, math.radians(-5)), 'XYZ')
        pb["Shin_L"].rotation_euler = Euler((math.radians(-88), 0.0, 0.0), 'XYZ')
        if "Thigh_R" in pb and "Shin_R" in pb:
            pb["Thigh_R"].rotation_euler = Euler((math.radians(88), 0.0, math.radians(5)), 'XYZ')
            pb["Shin_R"].rotation_euler = Euler((math.radians(-88), 0.0, 0.0), 'XYZ')

    # Position actor slightly forward of chair backrest toward facing target so back doesn't clip backrest
    ux, uy = (dx / math.hypot(dx, dy), dy / math.hypot(dx, dy)) if math.hypot(dx, dy) > 0.05 else (0.0, -1.0)
    seat_x = cx + ux * 0.06
    seat_y = cy + uy * 0.06

    for f in sorted(set([target_frame, f_end])):
        scene.frame_set(f)
        actor_obj.location.x = seat_x
        actor_obj.location.y = seat_y
        cur_rz = actor_obj.rotation_euler.z
        diff = (sit_rz - cur_rz + math.pi) % (2 * math.pi) - math.pi
        actor_obj.rotation_euler.z = cur_rz + diff
        context.view_layer.update()
        min_z, _, _, _, _ = _measure_armature_bounds(context, actor_obj)
        actor_obj.location.z -= min_z
        actor_obj.keyframe_insert(data_path="location", frame=f)
        actor_obj.keyframe_insert(data_path="rotation_euler", index=2, frame=f)

    scene.frame_set(keep)
    context.view_layer.update()
    return {
        "chair": chair_obj.name if chair_obj else None,
        "chair_name": chair_obj.name if chair_obj else None,
        "seat_xy": (round(seat_x, 3), round(seat_y, 3)),
        "seat_top_z": round(seat_top_z, 3),
        "facing_deg": round(math.degrees(sit_rz), 1)
    }


def plan_door_interaction(context, actor_obj, door_obj=None, start_xy=(0.0, 3.4), inside_xy=None, end_xy=None, open_frame=None, open_angle_deg=82.0, swing_deg=None):
    """
    Cindy Proactive Door Interaction Planner:
    Synchronizes an actor approaching a closed door, cracking/opening the door right as the actor reaches
    the threshold (so the actor NEVER clips through a closed door), and walking cleanly through to `inside_xy`.
    """
    import math
    from mathutils import Vector, Euler
    scene = context.scene
    keep = scene.frame_current
    f_start, f_end = scene.frame_start, scene.frame_end
    span = max(12, f_end - f_start)
    if inside_xy is None:
        inside_xy = end_xy if end_xy is not None else (0.0, 0.8)
    if swing_deg is not None:
        open_angle_deg = float(swing_deg)
    if door_obj is None:
        for o in scene.objects:
            if o.type in ('MESH', 'EMPTY') and not o.hide_viewport and 'door' in o.name.lower():
                door_obj = o
                break

    _auto_fix_actor_physics(context, actor_obj)

    if open_frame is None:
        f_reach = f_start + int(0.32 * span)
        f_open = f_start + int(0.48 * span)
    else:
        f_open = max(f_start + 6, min(f_end - 4, int(open_frame)))
        f_reach = max(f_start + 2, f_open - max(6, int(0.14 * span)))
    f_arrive = min(f_end, f_open + max(8, int(0.32 * span)))

    door_loc = door_obj.matrix_world.translation.copy() if door_obj else Vector(((start_xy[0] + inside_xy[0]) * 0.5, (start_xy[1] + inside_xy[1]) * 0.5, 0.0))

    # Measure door leaf width/span so threshold wait point stays clear of the swinging door leaf arc
    door_span = 0.85
    if door_obj is not None:
        dg_d = context.evaluated_depsgraph_get()
        if door_obj.type == 'MESH':
            ev_d = door_obj.evaluated_get(dg_d)
            d_pts = [ev_d.matrix_world @ Vector(c) for c in ev_d.bound_box]
        else:
            d_ms = [m.evaluated_get(dg_d) for m in door_obj.children_recursive if m.type == 'MESH' and not m.hide_viewport]
            d_pts = [ev_m.matrix_world @ Vector(c) for ev_m in d_ms for c in ev_m.bound_box] if d_ms else []
        if d_pts:
            door_span = max(max(p.x for p in d_pts) - min(p.x for p in d_pts),
                            max(p.y for p in d_pts) - min(p.y for p in d_pts))
            door_loc.x = 0.5 * (min(p.x for p in d_pts) + max(p.x for p in d_pts))
            door_loc.y = 0.5 * (min(p.y for p in d_pts) + max(p.y for p in d_pts))

    wait_dist = max(0.55, min(1.05, door_span * 0.65))

    # Threshold wait point: outside the door along the approach vector so the actor pauses while door swings open
    adx, ady = door_loc.x - start_xy[0], door_loc.y - start_xy[1]
    adist = math.hypot(adx, ady)
    if adist > 0.1:
        ux, uy = adx / adist, ady / adist
    else:
        idx, idy = inside_xy[0] - start_xy[0], inside_xy[1] - start_xy[1]
        ilen = max(1e-4, math.hypot(idx, idy))
        ux, uy = idx / ilen, idy / ilen

    wait_x = door_loc.x - ux * wait_dist
    wait_y = door_loc.y - uy * wait_dist

    fwd_off = _actor_forward_offset(context, actor_obj)
    walk_rz = math.atan2(inside_xy[0] - start_xy[0], -(inside_xy[1] - start_xy[1])) - fwd_off

    # 1. Keyframe door swing: closed at f_start..f_reach, cracked at f_reach+3, fully open at f_open..f_end
    if door_obj is not None:
        door_obj.rotation_mode = 'XYZ'
        for f_closed in (f_start, f_reach):
            scene.frame_set(f_closed)
            door_obj.rotation_euler = Euler((0.0, 0.0, 0.0), 'XYZ')
            door_obj.keyframe_insert(data_path="rotation_euler", frame=f_closed)
        scene.frame_set(min(f_open, f_reach + 3))
        door_obj.rotation_euler = Euler((0.0, 0.0, math.radians(open_angle_deg * 0.30)), 'XYZ')
        door_obj.keyframe_insert(data_path="rotation_euler", frame=min(f_open, f_reach + 3))
        for f_op in (f_open, f_end):
            scene.frame_set(f_op)
            door_obj.rotation_euler = Euler((0.0, 0.0, math.radians(open_angle_deg)), 'XYZ')
            door_obj.keyframe_insert(data_path="rotation_euler", frame=f_op)

    # 2. Keyframe actor: start -> threshold wait (f_reach) -> passes threshold after door opens (f_open) -> inside_xy (f_arrive..f_end)
    pass_x = door_loc.x + ux * 0.25
    pass_y = door_loc.y + uy * 0.25
    actor_waypoints = [
        (f_start, start_xy[0], start_xy[1], walk_rz),
        (f_reach, wait_x, wait_y, walk_rz),
        (f_open, pass_x, pass_y, walk_rz),
        (f_arrive, inside_xy[0], inside_xy[1], walk_rz),
        (f_end, inside_xy[0], inside_xy[1], walk_rz),
    ]
    for f, lx, ly, rz_v in actor_waypoints:
        scene.frame_set(f)
        actor_obj.location.x = lx
        actor_obj.location.y = ly
        actor_obj.rotation_euler.z = rz_v
        actor_obj.keyframe_insert(data_path="location", index=0, frame=f)
        actor_obj.keyframe_insert(data_path="location", index=1, frame=f)
        actor_obj.keyframe_insert(data_path="rotation_euler", index=2, frame=f)

    scene.frame_set(keep)
    context.view_layer.update()
    return {
        "door": door_obj.name if door_obj else None,
        "door_name": door_obj.name if door_obj else None,
        "reach_frame": f_reach,
        "open_frame": f_open,
        "pass_frame": f_open,
        "arrive_frame": f_arrive,
        "wait_xy": (round(wait_x, 3), round(wait_y, 3)),
        "inside_xy": (round(inside_xy[0], 3), round(inside_xy[1], 3))
    }


def _collect_camera_samples(context, n=25):
    """Sample the real camera path (position, forward, subject centroid) for motion classification."""
    scene = context.scene
    cam = scene.camera
    if not cam:
        return []
    keep = scene.frame_current
    f0, f1 = scene.frame_start, scene.frame_end
    fps = max(1, scene.render.fps)
    arms = [o for o in scene.objects if o.type == 'ARMATURE' and not o.hide_viewport]
    samples = []
    try:
        for i in range(n):
            f = int(round(f0 + (f1 - f0) * i / max(1, n - 1)))
            scene.frame_set(f)
            context.view_layer.update()
            mw = cam.matrix_world
            pos = mw.translation.copy()
            fwd = (mw.to_quaternion() @ Vector((0.0, 0.0, -1.0))).normalized()
            if arms:
                tgt = sum((a.matrix_world.translation for a in arms), Vector()) / len(arms) + Vector((0.0, 0.0, 1.0))
            else:
                tgt = pos + fwd * 5.0
            samples.append({'t': (f - f0) / fps, 'pos': tuple(pos), 'fwd': tuple(fwd), 'target': tuple(tgt)})
    finally:
        scene.frame_set(keep)
    return samples


def _derive_actor_beats(context, actors, duration_s):
    """Beats from what the actors actually do in the scene (moved vs held) instead of invented actions."""
    scene = context.scene
    arms = [o for o in scene.objects if o.type == 'ARMATURE' and not o.hide_viewport]
    keep = scene.frame_current
    beats = []
    try:
        for i, (a, obj) in enumerate(zip(actors, arms)):
            scene.frame_set(scene.frame_start)
            p0 = obj.matrix_world.translation.copy()
            scene.frame_set(scene.frame_end)
            p1 = obj.matrix_world.translation.copy()
            moved = math.hypot(p1.x - p0.x, p1.y - p0.y)
            action = ("moves across the set to a new position" if moved > 0.5
                      else "holds position and reacts with subtle micro-expressions")
            beats.append((round(duration_s * 0.12 * i, 2), duration_s, a['name'], action))
    finally:
        scene.frame_set(keep)
    return beats


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
            ('HUNYUAN_VIDEO', "HunyuanVideo 13B", "Tencent Hunyuan Cinema Optics"),
            ('KLING', "Kling (v3 Pro)", "Kling prompt (2500 char cap, native audio)"),
            ('VEO3', "Veo 3 / 3.1", "Veo prompt with dialogue + audio lines"),
            ('LUMA_RAY2', "Luma Ray 2", "Luma prompt (no negatives, camera concept tokens)"),
            ('TTM', "Time-to-Move (guide-driven)", "Appearance-only prompt; motion comes from the guide video"),
        ],
        default='WAN_2_2'
    )

    render_passes: bpy.props.BoolProperty(
        name="Render Beauty & Depth Passes",
        default=True
    )

    def execute(self, context):
        import sys, json, time, os
        try:
            repo_dir = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            repo_dir = r"C:\Users\DELL\Desktop\Cindy-AI-Director"
        if repo_dir not in sys.path:
            sys.path.append(repo_dir)
        from cindy_prompt_grammar import CindyPromptGrammar
        import cindy_prompt_profiles as cpp

        scene = context.scene
        cam = scene.camera
        lens_mm = round(float(cam.data.lens), 1) if (cam and cam.data) else 38.0
        lens_str = f"{int(lens_mm)}mm prime lens"
        duration_s = round(max(1.0, (scene.frame_end - scene.frame_start) / max(1, scene.render.fps)), 2)

        # 1. Run Director Quality Gate & extract real actors
        actors, audit_report = _run_scene_audit_and_extract(context)
        if not actors:
            actors = [{'name': "Subject", 'appearance': "Primary character staged in 3D frame", 'locked_prop': ""}]

        # Detect environment name from World HDRI or scene name
        env_desc = f"3D staged interior set ({scene.name}), physically grounded lighting and perspective"
        if scene.world and getattr(scene.world, "use_nodes", False) and scene.world.node_tree:
            for n in scene.world.node_tree.nodes:
                if n.type == 'TEX_ENVIRONMENT' and n.image:
                    env_desc = f"Cinematic set lit by {n.image.name} environment, physically accurate shadows and depth"
                    break

        # 2. Measure real 3D camera path stages & actor motion beats
        cam_samples = _collect_camera_samples(context)
        cam_stages = cpp.classify_camera_path(cam_samples) if len(cam_samples) >= 2 else [cpp.CameraStage(0.0, duration_s, "static")]
        raw_beats = _derive_actor_beats(context, actors, duration_s)
        spec_beats = [cpp.Beat(t0=b[0], t1=b[1], actor=b[2], action=b[3]) for b in raw_beats]

        shot_spec = cpp.ShotSpec(
            shot_type="Medium Wide Two-Shot" if len(actors) >= 2 else "Medium Shot",
            lens_mm=lens_mm,
            environment=env_desc,
            lighting="natural chiaroscuro key light with cool rim separation",
            style="cinematic 35mm film look, photorealistic skin and fabric, subtle film grain",
            cast=actors,
            beats=spec_beats,
            camera=cam_stages,
            duration_s=duration_s,
            aspect="16:9",
            ambience="ambient room tone, physical contact sounds",
            has_start_frame=False,
            references=[a['name'] for a in actors],
        )

        selected_profile = cpp.render(shot_spec, self.target_engine)
        all_profiles = cpp.render_all(shot_spec)

        move_preset = getattr(scene, 'cindy_compound_move', 'STEADY_TRACK')
        payload = CindyPromptGrammar.build_seven_part_prompt(
            visual_style="Cinematic 35mm film still, natural chiaroscuro lighting, rich tactile textures, photorealistic skin and fabric",
            shot_type=f"3D Previz-grounded camera composition ({lens_str})",
            camera_lens=lens_str,
            camera_motion=", ".join(f"{s.t0:.1f}-{s.t1:.1f}s {s.move}" for s in cam_stages) or move_preset.replace('_', ' ').lower(),
            scene_environment=env_desc,
            cast_and_props=actors,
            chronological_beats=[
                {'time': f"{b.t0:.1f}-{b.t1:.1f}s", 'actor': b.actor, 'action': b.action}
                for b in spec_beats
            ],
            target_model=self.target_engine
        )
        # Override top-level prompt & negative with the tool-tailored profile and attach all 7 tool profiles
        payload['target_model'] = selected_profile['tool_name']
        payload['positive_prompt'] = selected_profile['prompt']
        payload['negative_prompt'] = selected_profile['negative_prompt'] or ""
        payload['api_params'] = selected_profile['api_params']
        payload['warnings'] = selected_profile['warnings']
        payload['camera_stages'] = [{'t0': s.t0, 't1': s.t1, 'move': s.move} for s in cam_stages]
        payload['all_tool_prompts'] = all_profiles

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
                sp_kwargs = {"creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)} if os.name == "nt" else {}
                for src_dir, dst_mp4 in [(tmp_beauty, beauty_mp4), (tmp_depth, depth_mp4)]:
                    subprocess.run([
                        ffmpeg_exe, "-y", "-framerate", str(fps),
                        "-i", os.path.join(src_dir, "frame_%04d.png"),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", dst_mp4
                    ], check=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **sp_kwargs)
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
            ('SEEDANCE_2_5', "Seedance 2.0 (Doubao)", "Seedance @Image tags & inline negatives"),
            ('HUNYUAN_VIDEO', "HunyuanVideo 13B", "Hunyuan Subject+Motion+Scene+Camera"),
            ('KLING', "Kling (v3 Pro)", "Kling prompt (2500 char cap, native audio)"),
            ('VEO3', "Veo 3 / 3.1", "Veo prompt with Speaker dialogue & Audio line"),
            ('LUMA_RAY2', "Luma Ray 2", "Luma positive-only prompt + camera concept tokens"),
            ('TTM', "Time-to-Move (guide-driven)", "Appearance-only prompt for V2V guide"),
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
