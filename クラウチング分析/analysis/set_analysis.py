import cv2
import numpy as np
import mediapipe as mp

# 角度を内角（0〜180度）として計算する
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))  # 数値誤差を防止
    return np.degrees(angle)

def analyze_set_image(image):
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=True)
    results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    if not results.pose_landmarks:
        return image, None, None, None

    landmarks = results.pose_landmarks.landmark

    # 必要なランドマーク
    hip_L = [landmarks[mp_pose.PoseLandmark.LEFT_HIP].x,
             landmarks[mp_pose.PoseLandmark.LEFT_HIP].y]
    knee_L = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE].x,
              landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y]
    ankle_L = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x,
               landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y]

    hip_R = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP].x,
             landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y]
    knee_R = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].x,
              landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].y]
    ankle_R = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].x,
               landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].y]

    # 膝の角度を内角で計算（前脚・後脚の判別は左脚が前と仮定）
    front_knee_angle = calculate_angle(hip_L, knee_L, ankle_L)
    rear_knee_angle = calculate_angle(hip_R, knee_R, ankle_R)

    # 体幹前傾角 = 肩 → 股関節 → 地面との角度
    shoulder_L = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x,
                  landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y]
    shoulder_to_hip = np.array(hip_L) - np.array(shoulder_L)
    horizontal = np.array([1, 0])  # 水平ベクトル

    cosine = np.dot(shoulder_to_hip, horizontal) / (np.linalg.norm(shoulder_to_hip) * np.linalg.norm(horizontal))
    trunk_angle = np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))

    return image, rear_knee_angle, front_knee_angle, trunk_angle
