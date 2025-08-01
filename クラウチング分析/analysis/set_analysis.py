# set_analysis.py  ― 角度数値を返すだけ
import cv2
import numpy as np
import mediapipe as mp

mp_pose = mp.solutions.pose

def calculate_angle(a, b, c):
    a, b, c = map(np.array, (a, b, c))
    ba, bc = a - b, c - b
    cosang = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    return np.degrees(np.arccos(np.clip(cosang, -1.0, 1.0)))

def analyze_set_image(image_path: str, front_leg: str = "left"):
    """画像 1 枚から後脚膝角・前脚膝角・体幹前傾角のみ返す"""
    with mp_pose.Pose(static_image_mode=True) as pose:
        img = cv2.imread(image_path)
        res = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    if res.pose_landmarks is None:
        return None   # 検出失敗時

    lm, h, w = res.pose_landmarks.landmark, *img.shape[:2]
    get_xy = lambda name: [lm[getattr(mp_pose.PoseLandmark, name).value].x * w,
                           lm[getattr(mp_pose.PoseLandmark, name).value].y * h]

    if front_leg.lower() == "left":
        rear = ["RIGHT_HIP", "RIGHT_KNEE", "RIGHT_HEEL"]
        front = ["LEFT_HIP",  "LEFT_KNEE",  "LEFT_HEEL"]
        torso = ["LEFT_SHOULDER", "LEFT_HIP", "LEFT_KNEE"]
    else:
        rear = ["LEFT_HIP", "LEFT_KNEE", "LEFT_HEEL"]
        front = ["RIGHT_HIP", "RIGHT_KNEE", "RIGHT_HEEL"]
        torso = ["RIGHT_SHOULDER", "RIGHT_HIP", "RIGHT_KNEE"]

    return {
        "rear_knee":  calculate_angle(get_xy(rear[0]),  get_xy(rear[1]),  get_xy(rear[2])),
        "front_knee": calculate_angle(get_xy(front[0]), get_xy(front[1]), get_xy(front[2])),
        "torso_forward": calculate_angle(get_xy(torso[0]), get_xy(torso[1]), get_xy(torso[2]))
    }
