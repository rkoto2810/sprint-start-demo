import cv2
import numpy as np
import mediapipe as mp

# 角度計算（内角、0〜180度）
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)

def analyze_set_image(image):
    height, width = image.shape[:2]  # 画像サイズ取得
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=True)
    results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    if not results.pose_landmarks:
        return image, None, None, None

    # 座標変換（正規化→ピクセル、Y軸反転）
    def get_point(landmark):
        return np.array([
            landmark.x * width,
            height - landmark.y * height  # 上が0に反転
        ])

    lm = results.pose_landmarks.landmark

    # 前脚（左）と後脚（右）の膝角度
    hip_L = get_point(lm[mp_pose.PoseLandmark.LEFT_HIP])
    knee_L = get_point(lm[mp_pose.PoseLandmark.LEFT_KNEE])
    ankle_L = get_point(lm[mp_pose.PoseLandmark.LEFT_ANKLE])

    hip_R = get_point(lm[mp_pose.PoseLandmark.RIGHT_HIP])
    knee_R = get_point(lm[mp_pose.PoseLandmark.RIGHT_KNEE])
    ankle_R = get_point(lm[mp_pose.PoseLandmark.RIGHT_ANKLE])

    front_knee_angle = calculate_angle(hip_L, knee_L, ankle_L)
    rear_knee_angle = calculate_angle(hip_R, knee_R, ankle_R)

    # 体幹前傾角 = 肩→股関節と「鉛直方向」との角度
    shoulder_L = get_point(lm[mp_pose.PoseLandmark.LEFT_SHOULDER])
    trunk_vec = hip_L - shoulder_L
    vertical = np.array([0, 1])  # 鉛直方向ベクトル（下向き）

    cos_trunk = np.dot(trunk_vec, vertical) / (np.linalg.norm(trunk_vec) * np.linalg.norm(vertical))
    trunk_angle = np.degrees(np.arccos(np.clip(cos_trunk, -1.0, 1.0)))  # 前傾していれば角度が大きくなる

    return image, round(rear_knee_angle, 1), round(front_knee_angle, 1), round(trunk_angle, 1)
