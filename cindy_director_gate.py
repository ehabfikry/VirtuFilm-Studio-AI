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
from typing import Dict, List, Any

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
