# ============================ analysis/set_analysis.py ============================
"""
クラウチングスタートの **Set**（クラウチング姿勢）静止画像を解析し，
次の 3 つの角度 [deg] を返します。

    rear_knee      : 後脚（トレイル脚）膝角
    front_knee     : 前脚（リード脚）膝角
    torso_forward  : 体幹前傾角（肩–腰–膝）

戻り値は dict で，オプションで骨格ラインを描画した画像も含められます::

    {
        "rear_knee": <float>,
        "front_knee": <float>,
        "torso_forward": <float>,
        "overlay": np.ndarray | None  # with_overlay=True の場合のみ
    }

Pose 検出に失敗した場合は **None** を返します。
"""

from __future__ import annotations

import cv2
import numpy as np
import mediapipe as mp

from .common_pose import detect_pose_bgr  # MediaPipe + オーバーレイ

mp_pose = mp.solutions.pose


# --------------------------------------------------------------------------- #
#  補助関数
# --------------------------------------------------------------------------- #
def _angle(a_xy: list[float], b_xy: list[float], c_xy: list[float]) -> float:
    """3 点 A-B-C の内角 ABC を度数で返す。"""
    a, b, c = map(np.asarray, (a_xy, b_xy, c_xy))
    ba, bc = a - b, c - b
    cosang = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    return float(np.degrees(np.arccos(np.clip(cosang, -1.0, 1.0))))


def _get_xy(lms, name: str, w: int, h: int) -> list[float]:
    """MediaPipe のランドマーク → 画素座標 [x, y]"""
    idx = getattr(mp_pose.PoseLandmark, name).value
    lm = lms.landmark[idx]
    return [lm.x * w, lm.y * h]


# --------------------------------------------------------------------------- #
#  メイン関数
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
        解析対象の静止画像 (jpg/png) パス。
    front_leg : {'left', 'right'}
        アスリートの **前脚 (リード脚)** 側。
    with_overlay : bool, default False
        True の場合，骨格ラインを描画した画像を 'overlay' キーで返す。

    Returns
    -------
    dict | None
        成功時: 角度辞書 (＋ overlay)。失敗時: None
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")

    lms, annotated = detect_pose_bgr(img, static=True)
    if lms is None:  # 骨格検出失敗
        return None

    h, w = img.shape[:2]
    g = lambda n: _get_xy(lms, n, w, h)

    if front_leg.lower() == "left":
        rear = ("RIGHT_HIP", "RIGHT_KNEE", "RIGHT_HEEL")
        front = ("LEFT_HIP", "LEFT_KNEE", "LEFT_HEEL")
        torso = ("LEFT_SHOULDER", "LEFT_HIP", "LEFT_KNEE")
    else:
        rear = ("LEFT_HIP", "LEFT_KNEE", "LEFT_HEEL")
        front = ("RIGHT_HIP", "RIGHT_KNEE", "RIGHT_HEEL")
        torso = ("RIGHT_SHOULDER", "RIGHT_HIP", "RIGHT_KNEE")

    result: dict[str, float | np.ndarray] = {
        "rear_knee": _angle(g(rear[0]), g(rear[1]), g(rear[2])),
        "front_knee": _angle(g(front[0]), g(front[1]), g(front[2])),
        "torso_forward": _angle(g(torso[0]), g(torso[1]), g(torso[2])),
    }
    if with_overlay:
        result["overlay"] = annotated

    return result
