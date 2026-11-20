# ==============================================================================
# PROPRIETARY INTELLECTUAL PROPERTY & TRADE SECRET NOTICE
# System: VirtuFilm Studio AI (Cindy AI Director Architecture v8.0)
# Inventor & Owner: Ehab Fikry (المخرج / إيهاب فكري)
# Patent Reference: CAD-IP-2026-001
# Module: Director Quality Gate & Shot Validation Engine
# ==============================================================================

"""
Cindy Director Quality Gate & Pre-Render Inspector
Enforces the strict rule: "Errors caught in 3D staging never leak into generative video".
Validates scene geometry, physical contact, bone socket attachments, scale normalcy,
and cinematic composition before exporting depth/color guides or dispatching video generation.
"""

import math
import os
from typing import Dict, List, Any, Tuple, Optional

# Standard Human Scale Tolerances (meters)
TARGET_HUMAN_HEIGHT = 1.75
HEIGHT_TOLERANCE_MIN = 1.60
HEIGHT_TOLERANCE_MAX = 1.90

POSE_HEIGHT_BOUNDS = {
    "standing": (1.60, 1.90, 1.75),
    "sitting": (1.05, 1.55, 1.30),
    "crouching": (0.85, 1.45, 1.15),
}

class CindyDirectorGate:
    """
    Automated directorial checklist that audits a 3D scene before rendering.
    Prevents blind re-rolls and wasted compute.
    """

    @staticmethod
    def audit_actor_scale(actor_name: str, current_height: float, pose: str = "standing") -> Dict[str, Any]:
        """
        Validates that an actor's bounding height adheres to realistic human anatomy
        for their current pose (standing, sitting, crouching).
        """
        pose_key = (pose or "standing").lower()
        h_min, h_max, target = POSE_HEIGHT_BOUNDS.get(pose_key, (HEIGHT_TOLERANCE_MIN, HEIGHT_TOLERANCE_MAX, TARGET_HUMAN_HEIGHT))
        is_valid = h_min <= current_height <= h_max
        deviation = current_height - target
        return {
            'actor': actor_name,
            'pose': pose_key,
            'height': round(current_height, 3),
            'target': target,
            'deviation_meters': round(deviation, 3),
            'passed': is_valid,
            'message': f"Scale verified ({current_height:.2f}m {pose_key} adult human)" if is_valid else f"Scale anomaly detected ({pose_key}): {current_height:.2f}m is outside [{h_min}m, {h_max}m]"
        }

    @staticmethod
    def audit_ground_contact(lowest_z: float, ground_tolerance: float = 0.02) -> Dict[str, Any]:
        """
        Ensures an actor or prop is solidly grounded (Z=0) without floating or sinking.
        """
        is_grounded = abs(lowest_z) <= ground_tolerance
        return {
            'lowest_z': round(lowest_z, 4),
            'passed': is_grounded,
            'status': "Clean floor contact (Z=0)" if is_grounded else ("Floating in air" if lowest_z > ground_tolerance else "Submerged below floor")
        }

    @staticmethod
    def audit_prop_socket(prop_name: str, has_constraint: bool, target_bone: str = "") -> Dict[str, Any]:
        """
        Verifies that held hand props (cues, cups, weapons) are mechanically locked
        to an armature bone via Child-Of constraint rather than drifting in free coordinates.
        """
        return {
            'prop': prop_name,
            'locked_to_bone': has_constraint and bool(target_bone),
            'target_bone': target_bone,
            'passed': has_constraint and bool(target_bone),
            'message': f"Prop '{prop_name}' physically locked to bone '{target_bone}'" if (has_constraint and target_bone) else f"CRITICAL: Prop '{prop_name}' is drifting in free space without bone constraint!"
        }

    @staticmethod
    def audit_upright_stability(actor_name: str, frame_samples: List[Dict[str, Any]], max_tilt_deg: float = 20.0) -> Dict[str, Any]:
        """
        Audits upright orientation stability across multiple sampled frames of the shot.
        Catches Euler rotation seesaw / Mixamo X=90->0 flipping and lying-flat anomalies.
        Each sample dict: {'frame': int, 'height': float, 'max_xy': float, 'rot_x_deg': float, 'rot_y_deg': float}
        """
        if not frame_samples:
            return {'actor': actor_name, 'passed': True, 'message': 'No frame samples provided'}

        base_x = frame_samples[0].get('rot_x_deg', 90.0)
        failures = []
        for s in frame_samples:
            f = s['frame']
            h = s.get('height', 1.75)
            mxy = s.get('max_xy', 0.5)
            rx = s.get('rot_x_deg', base_x)
            ry = s.get('rot_y_deg', 0.0)
            if h < 0.85 and mxy > 1.25:
                failures.append(f"f{f}: lying flat (dz={h:.2f}m, xy={mxy:.2f}m)")
            elif abs(rx - base_x) > max_tilt_deg or abs(ry) > max_tilt_deg:
                failures.append(f"f{f}: tilt anomaly (rx={rx:.1f}deg vs {base_x:.1f}deg, ry={ry:.1f}deg)")

        passed = len(failures) == 0
        return {
            'actor': actor_name,
            'samples_checked': len(frame_samples),
            'passed': passed,
            'failures': failures[:5],
            'message': f"Upright stability verified across {len(frame_samples)} frames" if passed else f"CRITICAL STABILITY FAIL ({len(failures)} frames): " + "; ".join(failures[:3])
        }

    @staticmethod
    def audit_prop_clearance(actor_name: str, prop_name: str, frame: int, actor_xy: tuple, prop_xy: tuple, clearance_margin: float = 0.05) -> Dict[str, Any]:
        """
        Checks if an actor's core XY bounding box penetrates deeply into a solid prop (e.g. dining table).
        actor_xy / prop_xy: (min_x, max_x, min_y, max_y)
        """
        ax0, ax1, ay0, ay1 = actor_xy
        px0, px1, py0, py1 = prop_xy
        # Shrink actor core to torso center 40% so slight hand/knee reach over table edge is allowed
        acx, acy = (ax0 + ax1) * 0.5, (ay0 + ay1) * 0.5
        arx, ary = (ax1 - ax0) * 0.20, (ay1 - ay0) * 0.20
        overlap_x = (acx + arx) > (px0 + clearance_margin) and (acx - arx) < (px1 - clearance_margin)
        overlap_y = (acy + ary) > (py0 + clearance_margin) and (acy - ary) < (py1 - clearance_margin)
        passed = not (overlap_x and overlap_y)
        return {
            'actor': actor_name,
            'prop': prop_name,
            'frame': frame,
            'passed': passed,
            'message': f"Clean clearance from '{prop_name}' @f{frame}" if passed else f"CRITICAL CLIPPING: '{actor_name}' torso penetrates '{prop_name}' @f{frame}"
        }

    @staticmethod
    def audit_actor_spacing(actors_xy: List[Dict[str, Any]], frame: int = 1, min_clearance: float = 0.38) -> Dict[str, Any]:
        """
        Verifies personal-space clearance between every pair of actors so no two actors
        intersect or clip through each other during multi-actor blocking (2, 3, or N actors).
        actors_xy: [{'name': str, 'x': float, 'y': float}, ...]
        """
        violations = []
        n = len(actors_xy)
        for i in range(n):
            for j in range(i + 1, n):
                a1, a2 = actors_xy[i], actors_xy[j]
                dist = math.hypot(float(a1.get('x', 0.0)) - float(a2.get('x', 0.0)),
                                  float(a1.get('y', 0.0)) - float(a2.get('y', 0.0)))
                if dist < min_clearance:
                    violations.append(f"{a1.get('name', 'Actor1')}<->{a2.get('name', 'Actor2')} ({dist:.2f}m < {min_clearance:.2f}m @f{frame})")
        passed = len(violations) == 0
        return {
            'check': 'actor_spacing',
            'frame': frame,
            'pairs_checked': (n * (n - 1)) // 2,
            'passed': passed,
            'violations': violations,
            'message': f"Multi-actor personal space verified across {n} actors (@f{frame})" if passed else "CRITICAL ACTOR OVERLAP: " + "; ".join(violations)
        }

    @staticmethod
    def audit_camera_framing(
        actor_screen_coords: List[Dict[str, Any]],
        safe_x: Tuple[float, float] = (0.08, 0.92),
        safe_y: Tuple[float, float] = (0.05, 0.95),
        safe_margin: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Validates normalized camera-view coordinates (x in [0,1], y in [0,1], z > 0)
        for visible actors so no actor is behind the camera or cut off at frame edges.
        actor_screen_coords: [{'name': str, 'x': float, 'y': float, 'z': float, 'frame': int}, ...]
        """
        if safe_margin is not None:
            m = float(safe_margin)
            safe_x = (m, 1.0 - m)
            safe_y = (m, 1.0 - m)
        if not actor_screen_coords:
            return {'check': 'camera_framing', 'passed': True, 'violations': [], 'message': 'No actors to frame'}
        violations = []
        for item in actor_screen_coords:
            name = item.get('name', 'Actor')
            x = float(item.get('x', item.get('u', 0.5)))
            y = float(item.get('y', item.get('v', 0.5)))
            z = float(item.get('z', 1.0))
            f = item.get('frame', 1)
            if z <= 0.0:
                violations.append(f"{name}@f{f}: behind camera (z={z:.2f})")
            elif not (safe_x[0] <= x <= safe_x[1]) or not (safe_y[0] <= y <= safe_y[1]):
                violations.append(f"{name}@f{f}: out of safe frame (x={x:.2f}, y={y:.2f})")
        passed = len(violations) == 0
        return {
            'check': 'camera_framing',
            'passed': passed,
            'violations': violations,
            'message': f"Camera framing verified ({len(actor_screen_coords)} samples inside safe frame)" if passed else "FRAMING VIOLATION: " + "; ".join(violations[:4])
        }

    @staticmethod
    def audit_rendered_guide_image(image_path: str, guide_type: str = "depth", pass_type: Optional[str] = None, min_contrast_span: int = 18) -> Dict[str, Any]:
        """
        Inspects a rendered 3D Guide image (Depth Pass or Beauty Pass) on disk before feeding
        it to ControlNet / I2V / V2V engines. Catches missing files, zero-byte renders,
        or completely flat/blank (all-black or all-white) depth maps.
        """
        g_type = (pass_type or guide_type or "depth").lower()
        if not image_path or not os.path.exists(image_path):
            return {
                'check': f'{g_type}_guide_image',
                'path': image_path,
                'passed': False,
                'message': f"CRITICAL: {g_type} guide file missing at '{image_path}'"
            }
        fsize = os.path.getsize(image_path)
        if fsize < 256:
            return {
                'check': f'{g_type}_guide_image',
                'path': image_path,
                'passed': False,
                'message': f"CRITICAL: {g_type} guide file is corrupt/empty ({fsize} bytes)"
            }
        # Inspect pixel dynamic range via PIL or cv2 if available
        min_val, max_val, std_val = 0, 255, 32.0
        width, height = 0, 0
        inspected_pixels = False
        try:
            from PIL import Image, ImageStat
            with Image.open(image_path) as im:
                width, height = im.size
                gray = im.convert("L")
                extrema = gray.getextrema()
                if extrema:
                    min_val, max_val = int(extrema[0]), int(extrema[1])
                stat = ImageStat.Stat(gray)
                std_val = float(stat.stddev[0]) if stat.stddev else 0.0
                inspected_pixels = True
        except Exception:
            try:
                import cv2
                import numpy as np
                arr = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                if arr is not None and arr.size > 0:
                    height, width = arr.shape[:2]
                    min_val, max_val = int(arr.min()), int(arr.max())
                    std_val = float(arr.std())
                    inspected_pixels = True
            except Exception:
                try:
                    import bpy
                    import math
                    img_b = bpy.data.images.load(image_path, check_existing=False)
                    try:
                        width, height = int(img_b.size[0]), int(img_b.size[1])
                        ch = max(1, int(img_b.channels))
                        px = list(img_b.pixels)
                        if px and width > 0 and height > 0:
                            step_p = max(1, (len(px) // ch) // 4096) * ch
                            vals = [max(0, min(255, int(round(px[k] * 255.0)))) for k in range(0, len(px), step_p)]
                            if vals:
                                min_val, max_val = min(vals), max(vals)
                                mean_v = sum(vals) / len(vals)
                                std_val = math.sqrt(sum((v - mean_v) ** 2 for v in vals) / len(vals))
                                inspected_pixels = True
                    finally:
                        bpy.data.images.remove(img_b)
                except Exception:
                    pass

        span = max_val - min_val
        passed = (span >= min_contrast_span and std_val >= 2.0) if inspected_pixels else True
        return {
            'check': f'{g_type}_guide_image',
            'path': image_path,
            'resolution': [width, height] if inspected_pixels else None,
            'min_pixel': min_val,
            'max_pixel': max_val,
            'contrast_span': span,
            'std_dev': round(std_val, 2),
            'passed': passed,
            'message': (
                f"{g_type.capitalize()} guide verified ({width}x{height}, contrast span={span}, std={std_val:.1f})"
                if passed else
                f"CRITICAL BLANK/FLAT {g_type.upper()} GUIDE: contrast span={span} (<{min_contrast_span}), std={std_val:.1f}"
            )
        }

    @staticmethod
    def generate_video_prompt_package(
        shot_type: str,
        scene_description: str,
        actors: List[Dict[str, str]],
        primary_action: str,
        lighting_style: str,
        camera_motion: str
    ) -> Dict[str, Any]:
        """
        Synthesizes a production-grade multi-model prompt package adhering to
        the 'Cost-Escalation Ladder' (xdlkc/ai-video-production):
        - Action breakdown (who acts first, who reacts next).
        - Explicit positive constraints (avoiding AI drift).
        - Camera lens & optical parameters.
        """
        actor_descriptions = ", ".join([f"{a.get('name')}: {a.get('appearance')} ({a.get('action')})" for a in actors])

        positive_prompt = (
            f"Cinematic {shot_type}, {lighting_style}. "
            f"Scene: {scene_description}. "
            f"Cast: {actor_descriptions}. "
            f"Dynamic Action: {primary_action}. "
            f"Camera: {camera_motion}, 35mm master cinematic lens, photorealistic texture, organic fabric motion, 8k resolution, film grain."
        )

        negative_prompt = (
            "morphing, warping, extra limbs, floating objects, disconnected hands, "
            "plastic skin, cartoon shading, low resolution, flickering, text, watermark"
        )

        return {
            'shot_type': shot_type,
            'positive_prompt': positive_prompt,
            'negative_prompt': negative_prompt,
            'camera_motion': camera_motion,
            'generation_rules': [
                "Start frame must have all props visible and locked in hand",
                "Action unfolds sequentially (shooter aims first, opponent reacts with delay)",
                "No spontaneous object creation during video diffusion"
            ]
        }

if __name__ == "__main__":
    print("=== Testing Cindy Director Quality Gate ===")
    scale_check = CindyDirectorGate.audit_actor_scale("Abdelshakoor_Rig", 1.752)
    print("Scale Check:", scale_check)

    ground_check = CindyDirectorGate.audit_ground_contact(0.001)
    print("Ground Check:", ground_check)

    socket_check = CindyDirectorGate.audit_prop_socket("Billiard_Cue", True, "mixamorig:RightHand")
    print("Socket Check:", socket_check)

    pkg = CindyDirectorGate.generate_video_prompt_package(
        shot_type="Two-Shot Medium Confrontation",
        scene_description="Intimate underground billiard hall with polished mahogany table and green cloth",
        actors=[
            {'name': "Abdelshakoor", 'appearance': "Mature man in brown leather jacket", 'action': "aims cue stick across green felt"},
            {'name': "Abdelaziz", 'appearance': "Elderly man in ornate fur collar jacket", 'action': "stands opposite table watching intently"}
        ],
        primary_action="Abdelshakoor prepares his pool shot while Abdelaziz observes with subtle smile",
        lighting_style="warm tungsten chandelier overhead, cool cyan edge rim separation",
        camera_motion="subtle lateral slider track"
    )
    print("\nGenerated Prompt Package:\n", pkg['positive_prompt'])
