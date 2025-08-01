# analysis/drive_analysis.py
"""
Drive（飛び出し）局面：脛骨前傾角だけを返すモジュール
-------------------------------------------------------
- MediaPipe Pose でランドマーク取得
- ユーザーが指定した脚 (left / right) の膝―足首ベクトルを使用
- 水平線に対する鋭角 (0°〜90°) を返す
  * 撮影方向（右撮り / 左撮り）に依存しない
"""

import cv2
import numpy as np
import mediapipe as mp


def _horizontal_shin_angle(knee_xy, ankle_xy) -> float:
    """
    膝→足首ベクトルと水平線の鋭角を返す（0°=水平、90°=垂直）
    dx, dy の符号を無視し、常に 0〜90° の範囲に収める
    """
    dx, dy = ankle_xy[0] - knee_xy[0], ankle_xy[1] - knee_xy[1]
    angle_rad = np.arctan2(abs(dy), abs(dx))  # abs で向きを無視
    return np.degrees(angle_rad)              # 常に 0〜90°


def analyze_drive_image(image_path: str, front_leg: str = "left"):
    """
    Parameters
    ----------
    image_path : str
        静止画ファイルパス
    front_leg : 'left' or 'right'
        脛骨前傾角を測定する脚（ユーザー指定）

    Returns
    -------
    dict | None
        {'tibia_angle': float}  or  None（検出失敗）
    """
    mp_pose = mp.solutions.pose
    with mp_pose.Pose(static_image_mode=True) as pose:
        img_bgr = cv2.imread(image_path)
        if img_bgr is None:
            return None
        h, w = img_bgr.shape[:2]
        res = pose.process(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))

    if res.pose_landmarks is None:
        return None

    lm = res.pose_landmarks.landmark
    mp_lm = mp_pose.PoseLandmark
    get_xy = lambda name: [lm[getattr(mp_lm, name).value].x * w,
                           lm[getattr(mp_lm, name).value].y * h]

    if front_leg.lower() == "left":
        knee_xy, ankle_xy = get_xy("LEFT_KNEE"), get_xy("LEFT_ANKLE")
    else:
        knee_xy, ankle_xy = get_xy("RIGHT_KNEE"), get_xy("RIGHT_ANKLE")

    tibial_angle = _horizontal_shin_angle(knee_xy, ankle_xy)

    return {"tibia_angle": tibial_angle}
