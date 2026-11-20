"""
Regression tests for Cindy's Blender bridge (scene-independent, synthetic rigs).

Run:  blender -b --python-exit-code 1 -P tests/test_bridge_core.py
Exit code is non-zero if any test fails.
"""
import math
import os
import sys
import traceback

import bpy
from mathutils import Vector

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
import cindy_blender_bridge as cbb  # noqa: E402


# ----------------------------------------------------------------------------- builders
def new_scene(frames=60):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, frames
    return sc


def make_actor(name, flip_lr=False):
    """Mixamo-like rig: armature rotated X=90deg (Y-up local), mixamorig bones, 1.75m body mesh."""
    sc = bpy.context.scene
    data = bpy.data.armatures.new(name)
    arm = bpy.data.objects.new(name, data)
    sc.collection.objects.link(arm)
    arm.rotation_euler.x = math.pi / 2
    bpy.context.view_layer.objects.active = arm
    bpy.context.view_layer.update()
    bpy.ops.object.mode_set(mode='EDIT')
    sx = -1.0 if flip_lr else 1.0

    def bone(n, head, tail):
        b = data.edit_bones.new(n)
        b.head, b.tail = head, tail

    # local coords = (x_w, z_w, -y_w) because of the X=90deg rotation
    bone('mixamorig:Hips', (0, 1.0, 0), (0, 1.2, 0))
    bone('mixamorig:LeftUpLeg', (0.1 * sx, 0.95, 0), (0.1 * sx, 0.5, 0))
    bone('mixamorig:RightUpLeg', (-0.1 * sx, 0.95, 0), (-0.1 * sx, 0.5, 0))
    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.mesh.primitive_cube_add(size=1)
    body = bpy.context.active_object
    body.name = name + '_Body'
    body.scale = (0.5, 0.3, 1.75)
    body.location = (0, 0, 0.875)
    bpy.context.view_layer.update()
    body.parent = arm
    body.matrix_parent_inverse = arm.matrix_world.inverted()
    return arm


def make_desk(name='office_desk', size=(2.0, 1.0, 0.8)):
    bpy.ops.mesh.primitive_cube_add(size=1)
    d = bpy.context.active_object
    d.name = name
    d.scale = size
    d.location = (0, 0, size[2] / 2)
    bpy.context.view_layer.update()
    return d


def key_actor(arm, keys):
    """keys: list of (frame, (x, y, z), rz_radians)"""
    for f, loc, rz in keys:
        arm.location = loc
        arm.rotation_euler.z = rz
        arm.keyframe_insert(data_path="location", frame=f)
        arm.keyframe_insert(data_path="rotation_euler", index=2, frame=f)


def body_box(arm):
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for m in arm.children_recursive:
        if m.type == 'MESH':
            em = m.evaluated_get(dg)
            pts += [em.matrix_world @ Vector(c) for c in em.bound_box]
    x0, x1 = min(p.x for p in pts), max(p.x for p in pts)
    y0, y1 = min(p.y for p in pts), max(p.y for p in pts)
    sx, sy = (x1 - x0) * 0.25, (y1 - y0) * 0.25
    return x0 + sx, x1 - sx, y0 + sy, y1 - sy


def penetration_frames(arm, desk):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = desk.evaluated_get(dg)
    pts = [ev.matrix_world @ Vector(c) for c in ev.bound_box]
    dx0, dx1 = min(p.x for p in pts), max(p.x for p in pts)
    dy0, dy1 = min(p.y for p in pts), max(p.y for p in pts)
    bad = []
    sc = bpy.context.scene
    for f in range(sc.frame_start, sc.frame_end + 1):
        sc.frame_set(f)
        bx0, bx1, by0, by1 = body_box(arm)
        if bx0 < dx1 and bx1 > dx0 and by0 < dy1 and by1 > dy0:
            bad.append(f)
    return bad


def rz_keys(arm):
    ad = arm.animation_data
    fcs = getattr(ad.action, "fcurves", None)
    if fcs is None:  # layered actions (Blender 5)
        fcs = []
        for layer in ad.action.layers:
            for strip in layer.strips:
                for cb in strip.channelbags:
                    fcs += list(cb.fcurves)
    fc = next(f for f in fcs if f.data_path == "rotation_euler" and f.array_index == 2)
    return [(kp.co[0], kp.co[1]) for kp in fc.keyframe_points]


def run_audit():
    return cbb._run_scene_audit_and_extract(bpy.context, auto_fix=True)


def check(report, name):
    return [c for c in report['checks'] if c.get('check') == name]


# ----------------------------------------------------------------------------- tests
def test_walks_through_desk():
    sc = new_scene(60)
    desk = make_desk()
    a = make_actor('RIG_A')
    key_actor(a, [(1, (-3, 0, 0), math.pi / 2), (60, (3, 0, 0), math.pi / 2)])
    _, rep = run_audit()
    bad = penetration_frames(a, desk)
    assert not bad, f"actor still penetrates desk at frames {bad[:10]}"
    assert rep['passed'], f"gate failed: {[c for c in rep['checks'] if not c.get('passed', True)]}"


def test_backwards_walk_is_turned_forward_without_spin():
    sc = new_scene(60)
    a = make_actor('RIG_B')
    key_actor(a, [(1, (-2, 0, 0), -math.pi / 2), (60, (2, 0, 0), -math.pi / 2)])
    run_audit()
    keys = rz_keys(a)
    for (f0, v0), (f1, v1) in zip(keys, keys[1:]):
        assert abs(v1 - v0) <= math.pi + 1e-6, f"360-spin risk between f{f0:.0f}->f{f1:.0f}: {math.degrees(v1 - v0):.0f} deg"
    for f in (10, 30, 50, 60):   # includes the LAST frame
        sc.frame_set(f)
        heading = a.rotation_euler.z      # forward=(sin,-cos): +X motion means heading ~ +90deg
        err = abs(math.degrees((math.pi / 2 - heading + math.pi) % (2 * math.pi) - math.pi))
        assert err < 75, f"frame {f}: still walking backwards (heading error {err:.0f} deg)"


def test_scene_without_desk_or_camera_runs_clean():
    new_scene(48)
    make_actor('RIG_C')
    actors, rep = run_audit()
    assert rep['passed'] and len(actors) == 1


def test_idempotent_second_run_changes_nothing():
    sc = new_scene(60)
    make_desk()
    a = make_actor('RIG_D')
    key_actor(a, [(1, (-3, 0, 0), math.pi / 2), (60, (3, 0, 0), math.pi / 2)])
    run_audit()
    frames = (1, 10, 20, 30, 40, 50, 60)

    def snap():
        out = []
        for f in frames:
            sc.frame_set(f)
            out.append((a.location.x, a.location.y, a.rotation_euler.z))
        return out

    s1 = snap()
    _, rep2 = run_audit()
    s2 = snap()
    drift = max(abs(p - q) for r1, r2 in zip(s1, s2) for p, q in zip(r1, r2))
    assert drift < 1e-4, f"second run moved the actor by {drift:.4f}"


def test_forward_offset_is_measured_not_assumed():
    new_scene(10)
    a = make_actor('RIG_E')
    b = make_actor('RIG_F', flip_lr=True)
    oa = cbb._actor_forward_offset(bpy.context, a)
    ob = cbb._actor_forward_offset(bpy.context, b)
    assert abs(oa) < 1e-3, f"normal rig offset should be 0, got {math.degrees(oa):.1f} deg"
    assert abs(abs(ob) - math.pi) < 1e-3, f"flipped rig offset should be 180 deg, got {math.degrees(ob):.1f} deg"


def test_animated_lens_is_not_touched():
    sc = new_scene(60)
    a = make_actor('RIG_G')
    key_actor(a, [(1, (0, 0, 0), 0.0), (60, (0, 0, 0), 0.0)])
    cam_data = bpy.data.cameras.new('Cam')
    cam = bpy.data.objects.new('Cam', cam_data)
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.location = (0, -6, 1.6)
    cam.rotation_euler = (math.pi / 2, 0, 0)
    cam_data.lens = 50.0
    cam_data.keyframe_insert(data_path="lens", frame=1)
    cam_data.lens = 85.0
    cam_data.keyframe_insert(data_path="lens", frame=60)
    sc.frame_set(60)
    before = cam_data.lens
    run_audit()
    sc.frame_set(60)
    assert abs(cam_data.lens - before) < 1e-6, "animated lens was modified"


def test_two_actors_facing_away_end_up_facing_each_other():
    sc = new_scene(60)
    a = make_actor('RIG_H')
    b = make_actor('RIG_I')
    key_actor(a, [(1, (-1, -1.5, 0), -math.pi / 2), (60, (-1, -1.5, 0), -math.pi / 2)])
    key_actor(b, [(1, (1, -1.5, 0), math.pi / 2), (60, (1, -1.5, 0), math.pi / 2)])
    _, rep = run_audit()
    eye = check(rep, 'final_eyeline')
    assert eye and all(c['passed'] for c in eye), f"eye-line failed: {eye}"
    for arm in (a, b):
        keys = rz_keys(arm)
        for (f0, v0), (f1, v1) in zip(keys, keys[1:]):
            assert abs(v1 - v0) <= math.pi + 1e-6, f"{arm.name}: spin risk f{f0:.0f}->f{f1:.0f}"


def test_plan_actor_approach_avoids_desk():
    sc = new_scene(60)
    desk = make_desk()
    a = make_actor('RIG_Plan')
    res = cbb.plan_actor_approach(bpy.context, a, start_xy=(-2.2, -2.5), side="front", margin=0.35)
    assert res["goal_xy"][1] < -0.5, f"expected front stop mark y < -0.5, got {res['goal_xy']}"
    bad = penetration_frames(a, desk)
    assert not bad, f"planned trajectory still penetrates desk at frames {bad}"
    _, rep = run_audit()
    assert rep['passed'], f"gate failed on planned trajectory: {rep['checks']}"


def test_three_actors_blocking_spacing_and_centroid_eyeline():
    sc = new_scene(60)
    # 3 actors start overlapping near (0.0, -1.2) and facing outward
    a1 = make_actor('RIG_Tri1')
    a2 = make_actor('RIG_Tri2')
    a3 = make_actor('RIG_Tri3')
    key_actor(a1, [(1, (0.0, -1.2, 0.0), -math.pi), (60, (0.0, -1.2, 0.0), -math.pi)])
    key_actor(a2, [(1, (0.08, -1.2, 0.0), math.pi / 2), (60, (0.08, -1.2, 0.0), math.pi / 2)])
    key_actor(a3, [(1, (-0.05, -1.15, 0.0), -math.pi / 2), (60, (-0.05, -1.15, 0.0), -math.pi / 2)])
    _, rep = run_audit()
    spacing = check(rep, 'actor_spacing')
    assert spacing and all(c['passed'] for c in spacing), f"3-actor spacing failed: {spacing}"
    eye = check(rep, 'final_eyeline')
    assert len(eye) == 3 and all(c['passed'] for c in eye), f"3-actor centroid eye-line failed: {eye}"


def test_plan_actor_sit_on_chair():
    sc = new_scene(60)
    # Create a chair mesh at (0.0, -1.1, 0.0) with seat height ~0.48m
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -1.1, 0.24))
    chair = bpy.context.active_object
    chair.name = 'Chair_Hero'
    chair.scale = (0.50, 0.50, 0.48)
    bpy.context.view_layer.update()

    a = make_actor('RIG_Seated')
    res = cbb.plan_actor_sit_on_chair(bpy.context, a, chair_obj=chair, sit_frame=25, face_target_xy=(0.0, 0.5))
    assert res['chair_name'] == 'Chair_Hero', f"unexpected chair_name: {res}"
    sc.frame_set(60)
    bpy.context.view_layer.update()
    assert math.hypot(a.location.x - 0.0, a.location.y - (-1.1)) < 0.15, f"actor not on chair XY: {a.location}"
    min_z, _, _, _, _ = cbb._measure_armature_bounds(bpy.context, a)
    assert abs(min_z) <= 0.06, f"seated actor feet not grounded at Z=0: min_z={min_z}"


def test_plan_door_interaction():
    sc = new_scene(60)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 2.0, 1.05))
    door = bpy.context.active_object
    door.name = 'Door_Main'
    door.scale = (0.90, 0.10, 2.10)
    bpy.context.view_layer.update()

    a = make_actor('RIG_Entrant')
    res = cbb.plan_door_interaction(bpy.context, a, door_obj=door, start_xy=(0.0, 3.4), end_xy=(0.0, 0.6), swing_deg=85.0)
    assert res['door_name'] == 'Door_Main'
    f_reach = res['reach_frame']
    f_pass = res['pass_frame']
    sc.frame_set(1)
    rz_start = door.rotation_euler.z
    sc.frame_set(f_reach)
    rz_reach = door.rotation_euler.z
    sc.frame_set(f_pass)
    rz_pass = door.rotation_euler.z
    assert abs(rz_reach - rz_start) < 0.05, "door should still be closed at reach_frame"
    assert abs(math.degrees(rz_pass - rz_start)) > 60.0, f"door did not swing open by pass_frame: {math.degrees(rz_pass - rz_start)}"
    wait_dist = math.hypot(res['wait_xy'][0] - 0.0, res['wait_xy'][1] - 2.0)
    assert wait_dist >= 0.55, f"threshold wait_xy too close to swinging door leaf: {wait_dist:.3f}m"


def test_plan_actor_approach_custom_target_and_camera_framing_audit():
    sc = new_scene(60)
    # Create custom prop target away from origin
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.4, 0.8, 0.45))
    podium = bpy.context.active_object
    podium.name = 'Prop_Podium'
    podium.scale = (0.60, 0.50, 0.90)
    bpy.context.view_layer.update()

    a = make_actor('RIG_Speaker')
    res = cbb.plan_actor_approach(bpy.context, a, (-0.5, -1.5), side="front", margin=0.30, target_obj=podium)
    assert abs(res['goal_xy'][0] - 1.4) < 0.05, f"expected approach X near podium X=1.4, got {res['goal_xy']}"
    assert res['goal_xy'][1] < 0.55, f"expected approach Y in front of podium, got {res['goal_xy']}"

    # Add camera framing the actor and run full scene audit
    cam_data = bpy.data.cameras.new('Cam_Podium')
    cam = bpy.data.objects.new('Cam_Podium', cam_data)
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.location = (1.4, -2.6, 1.5)
    cam.rotation_euler = (math.radians(88.0), 0.0, 0.0)
    cam_data.lens = 35.0
    bpy.context.view_layer.update()

    _, rep = run_audit()
    cam_fr = check(rep, 'camera_framing')
    assert cam_fr and all(c['passed'] for c in cam_fr), f"camera_framing audit check missing or failed: {cam_fr}"


def test_director_gate_new_audits():
    from cindy_director_gate import CindyDirectorGate
    import tempfile

    # 1. audit_actor_spacing
    sp_fail = CindyDirectorGate.audit_actor_spacing([
        {'name': 'A', 'x': 0.0, 'y': 0.0},
        {'name': 'B', 'x': 0.15, 'y': 0.0},
        {'name': 'C', 'x': 1.0, 'y': 0.0},
    ], frame=30, min_clearance=0.40)
    assert not sp_fail['passed'], "expected spacing audit to fail on 0.15m overlap"

    sp_ok = CindyDirectorGate.audit_actor_spacing([
        {'name': 'A', 'x': -0.8, 'y': 0.0},
        {'name': 'B', 'x': 0.0, 'y': 0.6},
        {'name': 'C', 'x': 0.8, 'y': 0.0},
    ], frame=30, min_clearance=0.40)
    assert sp_ok['passed'], f"expected spacing audit to pass: {sp_ok}"

    # 2. audit_camera_framing
    fr_fail = CindyDirectorGate.audit_camera_framing([
        {'name': 'A', 'u': 0.03, 'v': 0.5, 'z': 2.5},
    ])
    assert not fr_fail['passed'], "expected edge crop u=0.03 to fail framing audit"

    fr_ok = CindyDirectorGate.audit_camera_framing([
        {'name': 'A', 'u': 0.38, 'v': 0.52, 'z': 2.5},
        {'name': 'B', 'u': 0.62, 'v': 0.50, 'z': 2.6},
    ])
    assert fr_ok['passed'], f"expected centered framing to pass: {fr_ok}"

    # 3. audit_rendered_guide_image using real PNGs saved via bpy.data.images
    with tempfile.TemporaryDirectory() as td:
        blank_p = os.path.join(td, "blank_depth.png")
        valid_p = os.path.join(td, "valid_depth.png")

        img_blank = bpy.data.images.new("BlankTest", width=64, height=64)
        img_blank.pixels = [0.0, 0.0, 0.0, 1.0] * (64 * 64)
        img_blank.filepath_raw = blank_p
        img_blank.file_format = 'PNG'
        img_blank.save()
        bpy.data.images.remove(img_blank)

        img_valid = bpy.data.images.new("ValidTest", width=64, height=64)
        px_v = []
        for y in range(64):
            for x in range(64):
                v = x / 63.0
                px_v.extend([v, v, v, 1.0])
        img_valid.pixels = px_v
        img_valid.filepath_raw = valid_p
        img_valid.file_format = 'PNG'
        img_valid.save()
        bpy.data.images.remove(img_valid)

        res_blank = CindyDirectorGate.audit_rendered_guide_image(blank_p, pass_type="depth")
        assert not res_blank['passed'], f"expected blank depth image to fail: {res_blank}"
        res_valid = CindyDirectorGate.audit_rendered_guide_image(valid_p, pass_type="depth")
        assert res_valid['passed'], f"expected gradient depth image to pass: {res_valid}"


TESTS = [
    test_walks_through_desk,
    test_backwards_walk_is_turned_forward_without_spin,
    test_scene_without_desk_or_camera_runs_clean,
    test_idempotent_second_run_changes_nothing,
    test_forward_offset_is_measured_not_assumed,
    test_animated_lens_is_not_touched,
    test_two_actors_facing_away_end_up_facing_each_other,
    test_plan_actor_approach_avoids_desk,
    test_three_actors_blocking_spacing_and_centroid_eyeline,
    test_plan_actor_sit_on_chair,
    test_plan_door_interaction,
    test_plan_actor_approach_custom_target_and_camera_framing_audit,
    test_director_gate_new_audits,
]

if __name__ == "__main__":
    failed = 0
    for t in TESTS:
        try:
            t()
            print(f"[PASS] {t.__name__}")
        except Exception as e:
            failed += 1
            print(f"[FAIL] {t.__name__}: {e}")
            if not isinstance(e, AssertionError):
                traceback.print_exc()
    print(f"=== {len(TESTS) - failed}/{len(TESTS)} passed ===")
    if failed:
        sys.exit(1)
