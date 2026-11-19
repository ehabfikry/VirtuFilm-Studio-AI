# ==============================================================================
# PROPRIETARY INTELLECTUAL PROPERTY & TRADE SECRET NOTICE
# System: VirtuFilm Studio AI (Cindy AI Director Architecture v8.0)
# Inventor & Owner: Ehab Fikry (المخرج / إيهاب فكري)
# Patent Reference: CAD-IP-2026-001
# Module: Multi-Model Prompt Engineering & Video Generation Grammar
# ==============================================================================

"""
Cindy Director Multi-Model Prompt Grammar Library.
Formulates deterministic, production-grade prompt payloads tailored specifically
for modern AI video engines (Wan 2.2, HunyuanVideo, Seedance, CogVideoX, ComfyUI).

Incorporates:
1. Seven-Part Production Prompt Syntax (Style, Lens, Blocking, Cast, Chronology, Sound, Negative Constraints).
2. Model-Specific Pitfall Avoidance Rules (Preventing spontaneous object creation & collective action artifacts).
3. 3D-Grounded Camera & Composition Specifications (Eye-line, 38%/62% focal rule, metric depth).
"""

from typing import Dict, List, Any, Optional

class CindyPromptGrammar:
    """
    Standard Prompt Synthesis & Dispatcher Engine for Cindy AI Director.
    Generates exact payload strings adhering to individual AI video model requirements.
    """

    # Model Profiles and their specific token tolerances & strengths
    SUPPORTED_MODELS = {
        'WAN_2_2': {
            'name': "Wan 2.2 (Alibaba)",
            'default_fps': 24,
            'default_frames': 49,  # ~2.04s standard burst
            'optimal_lens': "35mm - 50mm",
            'prefers_timing_cues': True,
            'negative_weight_support': True
        },
        'HUNYUAN_VIDEO': {
            'name': "Tencent HunyuanVideo (13B)",
            'default_fps': 24,
            'default_frames': 73,  # ~3.04s standard burst
            'optimal_lens': "Cinema Prime",
            'prefers_timing_cues': True,
            'negative_weight_support': True
        },
        'SEEDANCE_2_5': {
            'name': "ByteDance Seedance (Doubao)",
            'default_fps': 25,
            'default_frames': 75,
            'optimal_lens': "35mm",
            'prefers_timing_cues': True,
            'negative_weight_support': False
        },
        'COMFYUI_SD15': {
            'name': "ComfyUI DreamShaper / SD1.5",
            'default_fps': 30,
            'default_frames': 90,
            'optimal_lens': "50mm",
            'prefers_timing_cues': False,
            'negative_weight_support': True
        }
    }

    # Universal Production Negative Prompts (Derived from Pitfalls Analysis)
    UNIVERSAL_NEGATIVES = (
        "morphing, warping, sudden disappearances, spontaneous objects, "
        "floating items, detached hands, extra limbs, fingers merging, "
        "plastic skin, oversaturated cartoon shading, text, watermark, logo, "
        "unnatural fast twitch, duplicated characters, flickering background, "
        "low resolution, blurry details, muddy textures"
    )

    @classmethod
    def build_seven_part_prompt(
        cls,
        visual_style: str,
        shot_type: str,
        camera_lens: str,
        camera_motion: str,
        scene_environment: str,
        cast_and_props: List[Dict[str, str]],
        chronological_beats: List[Dict[str, str]],
        audio_design: str = "ambient room tone, physical contact sounds, no dialogue",
        target_model: str = "WAN_2_2"
    ) -> Dict[str, Any]:
        """
        Builds the complete Seven-Part Cinematic Prompt:
        [1. Style] [2. Camera/Optics] [3. Environment] [4. Characters & Fixed Props]
        [5. Chronological Seconds] [6. Sound/Atmosphere] [7. Strict Constraints]
        """
        model_info = cls.SUPPORTED_MODELS.get(target_model, cls.SUPPORTED_MODELS['WAN_2_2'])

        # 1. Visual Style
        part_1_style = f"【Style】{visual_style.strip()}."

        # 2. Camera & Optics
        part_2_camera = (
            f"【Camera】{shot_type.strip()}, Lens: {camera_lens.strip()}, "
            f"Camera Movement: {camera_motion.strip()}. Depth of field is physically accurate, subject sharp, background softly diffused."
        )

        # 3. Environment & Spatial Layout
        part_3_env = f"【Environment & Staging】{scene_environment.strip()}."

        # 4. Cast & Locked Props
        cast_items = []
        for c in cast_and_props:
            actor_name = c.get('name', 'Actor')
            desc = c.get('appearance', '')
            held_prop = c.get('locked_prop', '')
            prop_str = f" firmly holding {held_prop}" if held_prop else ""
            cast_items.append(f"{actor_name}: {desc}{prop_str}")
        part_4_cast = f"【Cast & Fixed Props】{'; '.join(cast_items)}."

        # 5. Chronological Micro-Actions (Preventing simultaneous collective movement)
        beat_strings = []
        for beat in chronological_beats:
            time_sec = beat.get('time', '0-2s')
            actor = beat.get('actor', '')
            action = beat.get('action', '')
            beat_strings.append(f"{time_sec}: {actor} {action}")
        part_5_action = f"【Chronological Action】{'; '.join(beat_strings)}."

        # 6. Audio
        part_6_audio = f"【Audio Ambience】{audio_design.strip()}."

        # 7. Model-Specific Negative & Invariant Constraints
        part_7_constraints = (
            "【Constraints】All props and characters must be visible and identical to the opening guide frame. "
            "No new characters or objects appear spontaneously. Character identity, clothing, and anatomy remain consistent throughout the shot."
        )

        # Full concatenated prompt
        full_positive = f"{part_1_style} {part_2_camera} {part_3_env} {part_4_cast} {part_5_action} {part_6_audio} {part_7_constraints}"

        return {
            'target_model': model_info['name'],
            'fps': model_info['default_fps'],
            'frames': model_info['default_frames'],
            'positive_prompt': full_positive,
            'negative_prompt': cls.UNIVERSAL_NEGATIVES,
            'sections': {
                'style': part_1_style,
                'camera': part_2_camera,
                'environment': part_3_env,
                'cast': part_4_cast,
                'action': part_5_action,
                'audio': part_6_audio,
                'constraints': part_7_constraints
            }
        }

    @classmethod
    def get_billiard_reference_package(cls, target_model: str = "WAN_2_2") -> Dict[str, Any]:
        """
        Generates the standard reference prompt package for the Billiard Scene
        using the tested characters (Abdelaziz & Abdelshakoor).
        """
        return cls.build_seven_part_prompt(
            visual_style="Cinematic 35mm film still, warm tungsten chiaroscuro lighting, rich 8k texture, organic fabric folds, subtle film grain",
            shot_type="Medium Wide Two-Shot, low-angle perspective looking across table",
            camera_lens="38mm anamorphic prime lens (f/2.4 DoF)",
            camera_motion="Slow cinematic horizontal slider push-in (no shaky cam, steady mechanical track)",
            scene_environment="Vintage underground billiard hall with polished dark oak parquet floor and tournament green felt table illuminated by double overhead green enamel lamps",
            cast_and_props=[
                {
                    'name': "Abdelshakoor",
                    'appearance': "Mature man with weather-beaten features in worn brown leather jacket",
                    'locked_prop': "Canadian maple billiard cue stick aligned with cue ball"
                },
                {
                    'name': "Abdelaziz",
                    'appearance': "Elderly man with graying mustache in flamboyant ornate embroidered coat with fur collar",
                    'locked_prop': "personal cue resting on floor"
                }
            ],
            chronological_beats=[
                {'time': "0.0-0.5s", 'actor': "Scene", 'action': "begins in locked focus matching Blender 3D guide frame exactly"},
                {'time': "0.5-2.0s", 'actor': "Abdelshakoor", 'action': "smoothly draws back the cue stick in steady aim, his eyes locked on the white ball"},
                {'time': "1.2-2.8s", 'actor': "Abdelaziz", 'action': "smiles subtly across the table, watching the shot with calm amusement"}
            ],
            audio_design="Low rumble of vintage ventilation, crisp chalk click, distant quiet jazz piano, no vocal speech",
            target_model=target_model
        )

if __name__ == "__main__":
    pkg = CindyPromptGrammar.get_billiard_reference_package("WAN_2_2")
    print(f"=== Synthesized Seven-Part Prompt Package ({pkg['target_model']}) ===")
    print("\n[Positive Prompt]:\n", pkg['positive_prompt'])
    print("\n[Negative Prompt]:\n", pkg['negative_prompt'])
