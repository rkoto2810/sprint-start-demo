# ============================ analysis/set_analysis.py ============================
"""
Analyse a crouch-start **Set**-phase still image and return three key angles
(degrees):

    rear_knee      – rear/trail leg knee flexion
    front_knee     – front/lead leg knee flexion
    torso_forward  – trunk-lean (shoulder-hip-knee)

Returned dict::

    {
        "rear_knee":      <float>,
        "front_knee":     <float>,
        "torso_forward":  <float>,
        "overlay": np.ndarray | None      # only when with_overlay=True
    }

If pose detection fails the function returns **None**.
"""

from __future__ import annotations

import cv2
import numpy as np
import mediapipe as mp

from .common_pose import detect_pose_bgr   # MediaPipe + skeleton overlay helper

mp_pose = mp.solutions.pose


# --------------------------------------------------------------------------- #
#  helpers
# --------------------------------------------------------------------------- #
def _angle(a_xy: list[float], b_xy: list[float], c_xy: list[float]) -> float:
    """Inner angle ABC (deg)."""
    a, b, c = map(np.asarray, (a_xy, b_xy, c_xy))
    ba, bc = a - b, c - b
    cosang = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    return float(np.degrees(np.arccos(np.clip(cosang, -1.0, 1.0))))


def _get_xy(lms, name: str, w: int, h: int) -> list[float]:
    idx = getattr(mp_pose.PoseLandmark, name).value
    lm = lms.landmark[idx]
    return [lm.x * w, lm.y * h]


# --------------------------------------------------------------------------- #
#  main
# --------------------------------------------------------------------------- #
def analyze_set_image(
    image_path: str,
    front_leg: str = "left",
    *,
    with_overlay: bool = False,
) -> dict[str, float | np.ndarray] | None:
    """
    Parameters
    ----------
    image_path : str
        Path to the still frame (jpg/png) showing the Set position.
    front_leg : {'left', 'right'}
        Athlete's **front/lead** leg side.
    with_overlay : bool, default False
        If True, include a skeleton-overlayed frame under key ``'overlay'``.

    Returns
    -------
    dict | None
        Angle measurements; ``None`` if pose detection failed.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")

    lms, annotated = detect_pose_bgr(img, static=True)  # MediaPipe pose
    if lms is None:                                     # detection failed
        return None

    h, w = img.shape[:2]
    g = lambda n: _get_xy(lms, n, w, h)                 # landmark → xy

    # landmark sets depending on lead leg
    if front_leg.lower() == "left":
        rear  = ("RIGHT_HIP", "RIGHT_KNEE", "RIGHT_HEEL")
        front = ("LEFT_HIP",  "LEFT_KNEE",  "LEFT_HEEL")
        torso = ("LEFT_SHOULDER", "LEFT_HIP", "LEFT_KNEE")
    else:
        rear  = ("LEFT_HIP",  "LEFT_KNEE",  "LEFT_HEEL")
        front = ("RIGHT_HIP", "RIGHT_KNEE", "RIGHT_HEEL")
        torso = ("RIGHT_SHOULDER", "RIGHT_HIP", "RIGHT_KNEE")

    result: dict[str, float | np.ndarray] = {
        "rear_knee":     _angle(g(rear[0]),  g(rear[1]),  g(rear[2])),
        "front_knee":    _angle(g(front[0]), g(front[1]), g(front[2])),
        "torso_forward": _angle(g(torso[0]), g(torso[1]), g(torso[2])),
    }
    if with_overlay:
        result["overlay"] = annotated                   # BGR image

    return result
