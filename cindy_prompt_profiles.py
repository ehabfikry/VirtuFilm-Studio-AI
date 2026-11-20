# ==============================================================================
# Cindy AI Director - Per-Tool Prompt Profiles
# ------------------------------------------------------------------------------
# One neutral ShotSpec (what the director wants) -> one tailored payload per
# generation tool (how THAT tool wants to be asked). Pure Python, no bpy.
#
# Each profile records an `evidence` level so nobody mistakes a guess for a spec:
#   "repo"       - taken from how cindy_server.py actually calls the endpoint
#   "web"        - taken from public docs/guides (secondary summaries, re-verify
#                  against the provider's current docs before relying on limits)
#   "inference"  - design decision derived from how the tool works
# ==============================================================================
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple


# ----------------------------------------------------------------------------- spec
@dataclass
class Beat:
    t0: float
    t1: float
    actor: str
    action: str


@dataclass
class CameraStage:
    t0: float
    t1: float
    move: str          # canonical move, see CANONICAL_MOVES


@dataclass
class ShotSpec:
    shot_type: str = "Medium two-shot"
    lens_mm: float = 35.0
    environment: str = ""
    lighting: str = ""
    style: str = "cinematic, photorealistic skin and fabric, subtle film grain"
    cast: List[Dict[str, str]] = field(default_factory=list)     # name, appearance, locked_prop
    beats: List[Beat] = field(default_factory=list)
    camera: List[CameraStage] = field(default_factory=list)
    duration_s: float = 5.0
    aspect: str = "16:9"
    dialogue: List[Tuple[str, str]] = field(default_factory=list)
    ambience: str = ""
    has_start_frame: bool = True                                  # image-to-video?
    references: List[str] = field(default_factory=list)           # actor names, in image order


CANONICAL_MOVES = (
    "static", "push_in", "pull_out", "pan_left", "pan_right", "tilt_up", "tilt_down",
    "truck_left", "truck_right", "crane_up", "crane_down", "orbit_left", "orbit_right",
    "handheld", "track_follow",
)

UNIVERSAL_NEGATIVES = (
    "morphing, warping, sudden disappearances, spontaneous objects, floating items, detached hands, "
    "extra limbs, fingers merging, plastic skin, cartoon shading, text, watermark, logo, "
    "duplicated characters, flickering background, low resolution, blurry details"
)
POSITIVE_CONSTRAINTS = (
    "steady controlled camera, consistent character identity and clothing throughout, "
    "anatomically natural movement, clean photorealistic image"
)
# For guide-driven tools (TTM): motion/camera come from the guide video, so say nothing about them
POSITIVE_CONSTRAINTS_APPEARANCE = (
    "consistent character identity and clothing, anatomically natural proportions, clean photorealistic image"
)


# ----------------------------------------------------------------------------- profiles
def _snap(options, d):
    # ties round UP: never cut an action short to save a second
    return min(options, key=lambda x: (abs(x - d), -x))


@dataclass
class ToolProfile:
    id: str
    name: str
    evidence: str
    order: List[str]                      # section order for text-to-video
    i2v_order: Optional[List[str]] = None  # section order when a start frame exists
    drop_order: List[str] = field(default_factory=list)   # what to sacrifice first when over budget
    words: Optional[Tuple[int, int]] = None
    i2v_max_words: Optional[int] = None
    max_chars: Optional[int] = None
    negative: str = "param"               # "param" | "inline" | "none"
    extra_negative: str = ""
    timing_cues: bool = False
    background_motion: bool = False
    audio: str = "none"                   # "none" | "ambient" | "native"
    camera_in_prompt: bool = True
    motion_in_prompt: bool = True
    camera_vocab: Dict[str, Optional[str]] = field(default_factory=dict)
    approx_moves: Tuple[str, ...] = ()    # moves with no native term -> warn
    max_distinct_camera: Optional[int] = None
    max_duration: Optional[float] = None
    params: Callable[[ShotSpec, "ToolProfile"], Tuple[Dict[str, Any], List[str]]] = None
    notes: str = ""


def _aspect(spec, allowed):
    if spec.aspect in allowed:
        return spec.aspect, []
    return allowed[0], [f"aspect {spec.aspect} unsupported -> {allowed[0]}"]


def _p_wan(spec, p):
    ar, w = _aspect(spec, ("16:9", "9:16", "1:1"))
    return {"aspect_ratio": ar}, w


def _p_hunyuan(spec, p):
    return {}, []


def _p_kling(spec, p):
    ar, w = _aspect(spec, ("16:9", "9:16", "1:1"))
    d = 10 if spec.duration_s >= 8 else 5          # mirrors cindy_server.py
    if abs(d - spec.duration_s) > 1:
        w.append(f"duration {spec.duration_s:g}s -> {d}s (server maps to 5 or 10)")
    return {"duration": str(d), "aspect_ratio": ar, "cfg_scale": 0.5,
            "generate_audio": bool(spec.dialogue or spec.ambience)}, w


def _p_veo(spec, p):
    ar, w = _aspect(spec, ("16:9", "9:16"))
    d = _snap([4, 6, 8], spec.duration_s)
    if abs(d - spec.duration_s) > 0.5:
        w.append(f"duration {spec.duration_s:g}s -> {d}s (Veo allows 4/6/8)")
    return {"duration": f"{d}s", "aspect_ratio": ar}, w


def _p_luma(spec, p):
    ar, w = _aspect(spec, ("16:9", "9:16", "1:1"))
    d = 9 if spec.duration_s >= 8 else 5           # mirrors cindy_server.py
    if abs(d - spec.duration_s) > 1:
        w.append(f"duration {spec.duration_s:g}s -> {d}s (server maps to 5 or 9)")
    return {"duration": f"{d}s", "aspect_ratio": ar}, w


def _p_seedance(spec, p):
    d = int(min(max(round(spec.duration_s), 2), 30))   # mirrors cindy_server.py
    w = []
    if len(spec.references) > 9:
        w.append("more than 9 image references: public guides cap @Image tags at 9")
    return {"duration": d, "aspect_ratio": spec.aspect, "generate_audio": True, "resolution": "720p"}, w


def _p_none(spec, p):
    return {}, []


PROFILES: Dict[str, ToolProfile] = {}


def _reg(p: ToolProfile):
    PROFILES[p.id] = p


_reg(ToolProfile(
    id="WAN_2_2", name="Wan 2.2", evidence="web",
    order=["tags", "subject", "motion", "scene", "camera", "lighting", "style"],
    i2v_order=["motion", "camera"],
    drop_order=["style", "lighting"], words=(80, 120), i2v_max_words=100,
    negative="param", extra_negative="jittery camera, sudden jump cuts, subtitles",
    timing_cues=True, background_motion=True, audio="none", max_duration=5.0,
    camera_vocab={
        "static": "static locked-off shot", "push_in": "slow dolly in", "pull_out": "slow dolly out",
        "pan_left": "pan left", "pan_right": "pan right", "tilt_up": "tilt up", "tilt_down": "tilt down",
        "truck_left": "lateral tracking shot to the left", "truck_right": "lateral tracking shot to the right",
        "crane_up": "crane up", "crane_down": "crane down",
        "orbit_left": "orbital arc to the left", "orbit_right": "orbital arc to the right",
        "handheld": "handheld", "track_follow": "tracking shot"},
    params=_p_wan,
    notes="Layered directing-script prose; chronological motion; keep clips <=5s; I2V prompts describe motion only."))

_reg(ToolProfile(
    id="HUNYUAN_VIDEO", name="HunyuanVideo", evidence="web",
    order=["subject", "motion", "scene", "tags", "camera", "lighting", "style"],
    i2v_order=["motion", "camera"],
    drop_order=["style", "lighting"], negative="param", extra_negative="jittery motion, abrupt camera cuts",
    audio="none", max_duration=5.0,
    camera_vocab={
        "static": "static shot", "push_in": "zoom in", "pull_out": "zoom out",
        "pan_left": "pan left", "pan_right": "pan right", "tilt_up": "tilt up", "tilt_down": "tilt down",
        "truck_left": "tracking shot to the left", "truck_right": "tracking shot to the right",
        "crane_up": "camera rises smoothly", "crane_down": "camera descends smoothly",
        "orbit_left": "around left", "orbit_right": "around right",
        "handheld": "handheld shot", "track_follow": "tracking shot"},
    approx_moves=("push_in", "pull_out", "truck_left", "truck_right", "crane_up", "crane_down", "track_follow"),
    params=_p_hunyuan,
    notes="Subject+Motion+Scene+Shot+Camera+Lighting+Style; one continuous unhurried action; no native dolly/crane term."))

_reg(ToolProfile(
    id="KLING", name="Kling (v3 Pro)", evidence="web",
    order=["tags", "subject", "motion", "scene", "camera", "lighting", "style", "audio"],
    i2v_order=["motion", "camera", "audio"],
    drop_order=["style", "lighting", "audio"], max_chars=2500, negative="param",
    audio="native",
    camera_vocab={
        "static": "static camera", "push_in": "the camera slowly pushes in", "pull_out": "the camera slowly pulls back",
        "pan_left": "the camera pans left", "pan_right": "the camera pans right",
        "tilt_up": "the camera tilts up", "tilt_down": "the camera tilts down",
        "truck_left": "the camera tracks left", "truck_right": "the camera tracks right",
        "crane_up": "the camera cranes up", "crane_down": "the camera cranes down",
        "orbit_left": "the camera orbits left around the subjects", "orbit_right": "the camera orbits right around the subjects",
        "handheld": "handheld camera", "track_follow": "tracking shot following the subject"},
    params=_p_kling,
    notes="prompt capped at 2500 chars; native audio; negative_prompt + cfg_scale 0.5."))

_reg(ToolProfile(
    id="VEO3", name="Veo 3 / 3.1", evidence="web",
    order=["tags", "subject", "scene", "motion", "camera", "lighting", "style", "audio"],
    i2v_order=["motion", "camera", "audio"],
    drop_order=["style", "lighting"], negative="param", extra_negative="subtitles, caption text",
    audio="native",
    camera_vocab={
        "static": "static camera", "push_in": "dolly in", "pull_out": "dolly out",
        "pan_left": "pan left", "pan_right": "pan right", "tilt_up": "tilt up", "tilt_down": "tilt down",
        "truck_left": "tracking shot to the left", "truck_right": "tracking shot to the right",
        "crane_up": "crane shot rising", "crane_down": "crane shot descending",
        "orbit_left": "arc shot to the left", "orbit_right": "arc shot to the right",
        "handheld": "handheld", "track_follow": "tracking shot"},
    params=_p_veo,
    notes="Dialogue as Speaker: \"line\"; Audio: line for ambience; duration 4/6/8s; 16:9 or 9:16."))

_reg(ToolProfile(
    id="LUMA_RAY2", name="Luma Ray 2", evidence="web",
    order=["subject", "motion", "scene", "lighting", "style", "constraints_pos", "camera"],
    i2v_order=["motion", "constraints_pos", "camera"],
    drop_order=["constraints_pos", "style"], negative="none", audio="none", max_distinct_camera=2,
    camera_vocab={m: m for m in ("static", "push_in", "pull_out", "pan_left", "pan_right", "tilt_up",
                                 "tilt_down", "truck_left", "truck_right", "crane_up", "crane_down",
                                 "orbit_left", "orbit_right", "handheld")} | {"track_follow": None},
    params=_p_luma,
    notes="No negative prompts: constraints are rewritten positively. Camera concepts are tokens; few combine well."))

_reg(ToolProfile(
    id="SEEDANCE_2_5", name="Seedance", evidence="web",
    order=["refs", "subject", "motion", "scene", "camera", "lighting", "style", "constraints_inline"],
    i2v_order=["refs", "motion", "camera", "constraints_inline"],
    drop_order=["style", "lighting"], words=(60, 100), negative="inline", audio="ambient",
    camera_vocab={
        "static": "static camera", "push_in": "smooth push-in", "pull_out": "smooth pull-back",
        "pan_left": "pan left", "pan_right": "pan right", "tilt_up": "tilt up", "tilt_down": "tilt down",
        "truck_left": "lateral tracking to the left", "truck_right": "lateral tracking to the right",
        "crane_up": "crane up", "crane_down": "crane down",
        "orbit_left": "smooth orbit camera movement to the left", "orbit_right": "smooth orbit camera movement to the right",
        "handheld": "handheld", "track_follow": "tracking shot"},
    params=_p_seedance,
    notes="@Image1.. tags map references to actors; negatives appended inline after ' - '."))

_reg(ToolProfile(
    id="TTM", name="Time-to-Move (guide-driven)", evidence="inference",
    order=["subject", "scene", "lighting", "style", "constraints_pos"],
    drop_order=["style"], negative="none", audio="none",
    camera_in_prompt=False, motion_in_prompt=False, params=_p_none,
    notes="Motion + camera come from the Blender guide video, so the prompt only describes appearance."))

ALIASES = {"WAN": "WAN_2_2", "HUNYUAN": "HUNYUAN_VIDEO", "SEEDANCE": "SEEDANCE_2_5", "LUMA": "LUMA_RAY2",
           "VEO": "VEO3", "VEO_3": "VEO3", "KLING_3": "KLING"}


# ----------------------------------------------------------------------------- rendering
def _words(text):
    return len(re.findall(r"\S+", text))


def _sentence(s, cap=True):
    s = s.strip().rstrip(".")
    if not s:
        return ""
    return (s[0].upper() + s[1:] if cap else s) + "."


def _fmt_t(t):
    return f"{t:.1f}".rstrip("0").rstrip(".")


def _build_sections(spec: ShotSpec, p: ToolProfile, warnings: List[str]) -> Dict[str, str]:
    S: Dict[str, str] = {}
    i2v = spec.has_start_frame

    S["tags"] = _sentence(f"Cinematic {spec.shot_type.lower()}, {int(round(spec.lens_mm))}mm lens")

    cast = []
    for c in spec.cast:
        bit = f"{c.get('name', 'Actor')}, {c.get('appearance', '').strip()}".rstrip(", ")
        if c.get("locked_prop"):
            bit += f", holding {c['locked_prop']}"
        cast.append(bit)
    S["subject"] = _sentence("; ".join(cast))

    if p.motion_in_prompt and spec.beats:
        beats = sorted(spec.beats, key=lambda b: b.t0)
        parts, prev_end = [], None
        for i, b in enumerate(beats):
            if p.timing_cues:
                parts.append(f"{_fmt_t(b.t0)}-{_fmt_t(b.t1)}s: {b.actor} {b.action}")
            else:
                lead = "First, " if i == 0 else ("Meanwhile, " if prev_end is not None and b.t0 < prev_end else "Then, ")
                parts.append(f"{lead}{b.actor} {b.action}")
            prev_end = b.t1
        S["motion"] = _sentence(". ".join(x.rstrip(".") for x in parts))
    else:
        S["motion"] = ""

    scene = spec.environment.strip()
    if scene and p.background_motion:
        scene += ", with subtle ambient background motion"
    S["scene"] = _sentence(scene)
    S["lighting"] = _sentence(spec.lighting)
    S["style"] = _sentence(spec.style)

    # camera
    S["camera"] = ""
    if p.camera_in_prompt and spec.camera:
        used, phrases, approx = [], [], []
        for st in spec.camera:
            term = p.camera_vocab.get(st.move)
            if term is None:
                warnings.append(f"{p.name}: no term for camera move '{st.move}' - skipped")
                continue
            if st.move in p.approx_moves:
                approx.append(st.move)
            used.append(st.move)
            phrases.append((st, term))
        if approx:
            warnings.append(f"{p.name}: approximated camera moves {sorted(set(approx))} (no native term)")
        if p.max_distinct_camera and len(set(used)) > p.max_distinct_camera:
            warnings.append(f"{p.name}: {len(set(used))} distinct camera moves in one clip; "
                            f"it composes ~{p.max_distinct_camera} well - consider splitting the shot")
        if len(phrases) > 1 and spec.duration_s / len(phrases) < 2.0:
            warnings.append(f"{p.name}: {len(phrases)} camera stages in {spec.duration_s:g}s (<2s each) - will blur together")
        if p.id == "LUMA_RAY2":
            S["camera"] = _sentence(", ".join(dict.fromkeys(t for _, t in phrases)), cap=False)  # tokens are case-sensitive
        elif len(phrases) == 1:
            S["camera"] = _sentence(f"Camera: {phrases[0][1]}")
        else:
            S["camera"] = _sentence("Camera: " + "; ".join(
                (f"{_fmt_t(st.t0)}-{_fmt_t(st.t1)}s {t}" if p.timing_cues else t) for st, t in phrases))

    # audio
    aud = []
    if p.audio == "native":
        for who, line in spec.dialogue:
            aud.append(f'{who}: "{line}"')
        if spec.ambience:
            aud.append(f"Audio: {spec.ambience}")
    elif p.audio == "ambient" and spec.ambience:
        aud.append(f"Ambience: {spec.ambience}")
    elif spec.dialogue or spec.ambience:
        if spec.dialogue:
            warnings.append(f"{p.name}: no native audio - dialogue dropped (add it in post / TTS)")
    S["audio"] = _sentence(" ".join(aud)) if aud else ""

    # references (seedance @tags)
    if spec.references:
        tags = [f"@Image{i + 1} for {n}'s identity" for i, n in enumerate(spec.references)]
        S["refs"] = _sentence("Using " + " and ".join(tags))
    else:
        S["refs"] = ""

    S["constraints_pos"] = _sentence(POSITIVE_CONSTRAINTS if p.camera_in_prompt else POSITIVE_CONSTRAINTS_APPEARANCE)
    inline = ["no logo", "no text on screen", "avoid jitter", "avoid bent limbs", "avoid temporal flicker", "avoid identity drift"]
    if "music" not in spec.ambience.lower():
        inline.insert(0, "no music")
    S["constraints_inline"] = "- " + ", ".join(inline) + "."
    return S


def render(spec: ShotSpec, tool_id: str) -> Dict[str, Any]:
    """Render one ShotSpec for one tool. Returns prompt, negative (or None), api params, warnings."""
    tid = ALIASES.get(tool_id.upper(), tool_id.upper())
    if tid not in PROFILES:
        raise KeyError(f"unknown tool '{tool_id}'. Known: {sorted(PROFILES)}")
    p = PROFILES[tid]
    warnings: List[str] = []
    S = _build_sections(spec, p, warnings)

    order = list(p.i2v_order if (spec.has_start_frame and p.i2v_order) else p.order)
    if spec.has_start_frame and not p.i2v_order:
        pass

    def compose(keys):
        return " ".join(S[k] for k in keys if S.get(k)).strip()

    def over(text):
        n = _words(text)
        if spec.has_start_frame and p.i2v_max_words and n > p.i2v_max_words:
            return True
        if (not spec.has_start_frame) and p.words and n > p.words[1]:
            return True
        if p.max_chars and len(text) > p.max_chars:
            return True
        return False

    keys = list(order)
    for k in p.drop_order:
        if not over(compose(keys)):
            break
        if k in keys:
            keys.remove(k)
            warnings.append(f"{p.name}: dropped '{k}' to fit the length budget")
    prompt = compose(keys)
    if p.max_chars and len(prompt) > p.max_chars:
        cut = prompt[: p.max_chars]
        cut = cut[: cut.rfind(".") + 1] or cut
        warnings.append(f"{p.name}: hard-truncated to {len(cut)} chars (limit {p.max_chars})")
        prompt = cut
    if not spec.has_start_frame and p.words and _words(prompt) < p.words[0]:
        warnings.append(f"{p.name}: prompt is {_words(prompt)} words (<{p.words[0]}); model will improvise - add detail")

    negative: Optional[str] = None
    if p.negative == "param":
        negative = ", ".join(x for x in (UNIVERSAL_NEGATIVES, p.extra_negative) if x)
    # "inline" tools already carry their negatives as the 'constraints_inline' section in `order`

    if p.max_duration and spec.duration_s > p.max_duration:
        warnings.append(f"{p.name}: {spec.duration_s:g}s exceeds the recommended {p.max_duration:g}s clip length")

    params, w2 = p.params(spec, p)
    warnings += w2
    return {
        "tool": p.id, "tool_name": p.name, "evidence": p.evidence, "mode": "i2v" if spec.has_start_frame else "t2v",
        "prompt": prompt, "negative_prompt": negative, "api_params": params,
        "word_count": _words(prompt), "char_count": len(prompt),
        "warnings": warnings, "sections_used": keys, "notes": p.notes,
    }


def render_all(spec: ShotSpec, tools: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
    return {t: render(spec, t) for t in (tools or list(PROFILES))}


def endpoint_to_tool_id(endpoint: str) -> Optional[str]:
    """Map a fal.ai / Cindy server endpoint or model key to a canonical ToolProfile id."""
    ep = (endpoint or "").lower()
    if "seedance" in ep:
        return "SEEDANCE_2_5"
    if "luma" in ep or "ray-2" in ep or "ray2" in ep or "dream-machine" in ep:
        return "LUMA_RAY2"
    if "veo" in ep:
        return "VEO3"
    if "kling" in ep:
        return "KLING"
    if "hunyuan" in ep:
        return "HUNYUAN_VIDEO"
    if "wan" in ep:
        return "WAN_2_2"
    if "ttm" in ep or "time-to-move" in ep:
        return "TTM"
    return None


def apply_endpoint_prompt_profile(
    endpoint: str,
    req_body: Dict[str, Any],
    custom_params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Normalize a live server `req_body` in-place (and return profile metadata/warnings)
    so every outgoing request to fal.ai / RunPod obeys the target tool's prompt grammar:
      - Translates canonical `camera_motion` into the tool's native vocabulary
      - Strips `negative_prompt` for no-negative tools (Luma Ray 2, TTM)
      - Converts negatives to inline `- no logo...` + `@Image1` tags for Seedance
      - Enforces tool-specific negative stacks (Wan, Hunyuan, Kling, Veo 3)
      - Enforces character limits (Kling 2500-char cap) and default cfg_scale
    """
    custom_params = custom_params or {}
    tid = endpoint_to_tool_id(endpoint)
    if not tid or tid not in PROFILES:
        return {"tool": None, "warnings": []}

    p = PROFILES[tid]
    warnings: List[str] = []
    prompt = str(req_body.get("prompt") or "").strip()

    # 1. Translate camera_motion using the tool's camera vocabulary
    raw_cam = str(custom_params.get("camera_motion") or "").strip().lower().replace(" ", "_").replace("-", "_")
    if raw_cam and raw_cam != "none":
        # If cindy_server appended `, <raw_cam>` already, replace it with the tool's native term
        raw_orig = str(custom_params.get("camera_motion") or "").strip()
        suffix = f", {raw_orig}"
        if prompt.endswith(suffix):
            prompt = prompt[: -len(suffix)].rstrip()
        if p.camera_in_prompt:
            term = p.camera_vocab.get(raw_cam, raw_orig)
            if term:
                if p.id == "LUMA_RAY2":
                    prompt = f"{prompt.rstrip('.')}. {term}."
                else:
                    prompt = f"{prompt.rstrip('.')}. Camera: {term}."

    # 2. Seedance multi-reference @Image1.. tags when image_urls are supplied without @Image tags
    if p.id == "SEEDANCE_2_5":
        imgs = req_body.get("image_urls") or custom_params.get("image_urls") or []
        if isinstance(imgs, list) and len(imgs) >= 1 and "@Image1" not in prompt:
            tags = " and ".join(f"@Image{i + 1}" for i in range(min(len(imgs), 9)))
            prompt = f"Using {tags} as visual reference. {prompt}"

    # 3. Negative prompt handling per tool architecture
    user_neg = str(custom_params.get("negative_prompt") or "").strip()
    if p.negative == "none":
        req_body.pop("negative_prompt", None)
    elif p.negative == "inline":
        req_body.pop("negative_prompt", None)
        if " - no logo" not in prompt.lower() and "avoid jitter" not in prompt.lower():
            inline = "- no music, no logo, no text on screen, avoid jitter, avoid bent limbs, avoid temporal flicker, avoid identity drift."
            prompt = f"{prompt.rstrip()} {inline}".strip()
    elif p.negative == "param":
        tailored_neg = ", ".join(x for x in (UNIVERSAL_NEGATIVES, p.extra_negative) if x)
        req_body["negative_prompt"] = user_neg if user_neg else tailored_neg

    # 4. Character cap enforcement (e.g. Kling 2500 chars)
    if p.max_chars and len(prompt) > p.max_chars:
        cut = prompt[: p.max_chars]
        cut = cut[: cut.rfind(".") + 1] or cut
        warnings.append(f"{p.name}: truncated prompt to {len(cut)} chars (limit {p.max_chars})")
        prompt = cut

    # 5. Tool-specific API parameter defaults
    if p.id == "KLING":
        req_body.setdefault("cfg_scale", 0.5)
    elif p.id == "VEO3" and "duration" in req_body:
        try:
            d_val = float(str(req_body["duration"]).rstrip("s"))
            req_body["duration"] = f"{_snap([4, 6, 8], d_val)}s"
        except ValueError:
            pass

    req_body["prompt"] = prompt
    return {"tool": p.id, "tool_name": p.name, "warnings": warnings}


# ----------------------------------------------------------------------------- camera analysis
def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _norm(a):
    return math.sqrt(_dot(a, a))


def classify_camera_path(samples: List[Dict[str, Any]], min_stage_s: float = 0.6) -> List[CameraStage]:
    """
    Turn sampled camera motion into canonical stages.
    samples: [{'t': sec, 'pos': (x,y,z), 'fwd': (x,y,z unit), 'target': (x,y,z)}] sorted by t.
    Conventions (Z up): right = fwd x up; orbit_left = camera moving to ITS left around the target.
    """
    labels: List[Tuple[float, float, str]] = []
    for a, b in zip(samples, samples[1:]):
        dt = max(b["t"] - a["t"], 1e-6)
        d = _sub(b["pos"], a["pos"])
        speed = _norm(d) / dt
        fwd = a["fwd"]
        right = (fwd[1] * 1.0 - fwd[2] * 0.0, -(fwd[0] * 1.0), 0.0)     # fwd x up(0,0,1)
        rn = _norm(right) or 1.0
        right = (right[0] / rn, right[1] / rn, 0.0)
        f, r, u = _dot(d, fwd), _dot(d, right), d[2]
        yaw = math.degrees(math.atan2(b["fwd"][1], b["fwd"][0]) - math.atan2(fwd[1], fwd[0]))
        yaw = (yaw + 180) % 360 - 180
        pitch = math.degrees(math.asin(max(-1, min(1, b["fwd"][2]))) - math.asin(max(-1, min(1, fwd[2]))))

        ra = _sub(a["pos"], a["target"]); rb = _sub(b["pos"], b["target"])
        ang_a, ang_b = math.atan2(ra[1], ra[0]), math.atan2(rb[1], rb[0])
        daz = math.degrees((ang_b - ang_a + math.pi) % (2 * math.pi) - math.pi)
        rad_a, rad_b = math.hypot(ra[0], ra[1]), math.hypot(rb[0], rb[1])
        rad_change = abs(rad_b - rad_a) / max(rad_a, 1e-6)

        if speed < 0.05:
            if abs(yaw) / dt > 4.0 or abs(pitch) / dt > 4.0:    # degrees per second
                if abs(yaw) >= abs(pitch):
                    lab = "pan_left" if yaw > 0 else "pan_right"
                else:
                    lab = "tilt_up" if pitch > 0 else "tilt_down"
            else:
                lab = "static"
        elif abs(daz) / dt > 6.0 and rad_change < 0.25 and abs(daz) * math.pi / 180 * rad_a > 0.6 * _norm(d):
            lab = "orbit_left" if daz < 0 else "orbit_right"
        else:
            mags = {"f": abs(f), "r": abs(r), "u": abs(u)}
            dom = max(mags, key=mags.get)
            if mags[dom] < 0.55 * _norm(d):
                lab = "track_follow"
            elif dom == "f":
                lab = "push_in" if f > 0 else "pull_out"
            elif dom == "r":
                lab = "truck_right" if r > 0 else "truck_left"
            else:
                lab = "crane_up" if u > 0 else "crane_down"
        labels.append((a["t"], b["t"], lab))

    merged: List[List[Any]] = []
    for t0, t1, lab in labels:
        if merged and merged[-1][2] == lab:
            merged[-1][1] = t1
        else:
            merged.append([t0, t1, lab])
    changed = True
    while changed and len(merged) > 1:        # absorb blips shorter than min_stage_s
        changed = False
        for i, (t0, t1, lab) in enumerate(merged):
            if (t1 - t0) < min_stage_s:
                j = i - 1 if i > 0 else i + 1
                merged[j][0], merged[j][1] = min(merged[j][0], t0), max(merged[j][1], t1)
                del merged[i]
                changed = True
                break
        k = 0
        while k < len(merged) - 1:
            if merged[k][2] == merged[k + 1][2]:
                merged[k][1] = merged[k + 1][1]
                del merged[k + 1]
            else:
                k += 1
    return [CameraStage(t0=m[0], t1=m[1], move=m[2]) for m in merged]


if __name__ == "__main__":
    spec = ShotSpec(
        environment="modern office with a steel desk and warm window light",
        lighting="soft key from camera left, cool rim from behind",
        cast=[{"name": "Abdelaziz", "appearance": "young man in a flowered shirt and flared jeans"},
              {"name": "Abdelshakoor", "appearance": "older man in a worn brown leather jacket"}],
        beats=[Beat(0, 2.5, "Abdelaziz", "walks toward the desk"), Beat(1.5, 4.5, "Abdelshakoor", "rises from his chair and smiles")],
        camera=[CameraStage(0, 2, "push_in"), CameraStage(2, 4, "orbit_left"), CameraStage(4, 5, "crane_up")],
        duration_s=5, has_start_frame=False, ambience="quiet office room tone",
        references=["Abdelaziz", "Abdelshakoor"])
    for tid, out in render_all(spec).items():
        print(f"\n=== {out['tool_name']} [{out['evidence']}] {out['word_count']}w ===")
        print(out["prompt"])
        print("neg:", out["negative_prompt"], "| params:", out["api_params"])
        for w in out["warnings"]:
            print("  !", w)
