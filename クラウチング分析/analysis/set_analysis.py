import cv2
import numpy as np
import mediapipe as mp

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    ba = a - b
    bc = c - b
    
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)

def analyze_set_image(img_path, front_leg="left"):
    image = cv2.imread(img_path)
    if image is None:
        return None

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=True)
    results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    if not results.pose_landmarks:
        return None

    lm = results.pose_landmarks.landmark

    def get_point(landmark):
        return [lm[landmark].x * image.shape[1], lm[landmark].y * image.shape[0]]

    left_hip = get_point(mp_pose.PoseLandmark.LEFT_HIP)
    left_knee = get_point(mp_pose.PoseLandmark.LEFT_KNEE)
    left_ankle = get_point(mp_pose.PoseLandmark.LEFT_ANKLE)

    right_hip = get_point(mp_pose.PoseLandmark.RIGHT_HIP)
    right_knee = get_point(mp_pose.PoseLandmark.RIGHT_KNEE)
    right_ankle = get_point(mp_pose.PoseLandmark.RIGHT_ANKLE)

    left_shoulder = get_point(mp_pose.PoseLandmark.LEFT_SHOULDER)
    right_shoulder = get_point(mp_pose.PoseLandmark.RIGHT_SHOULDER)

    # 前脚・後脚を判別
    if front_leg == "left":
        front_knee = calculate_angle(left_hip, left_knee, left_ankle)
        rear_knee = calculate_angle(right_hip, right_knee, right_ankle)
        hip = left_hip
        shoulder = left_shoulder
    else:
        front_knee = calculate_angle(right_hip, right_knee, right_ankle)
        rear_knee = calculate_angle(left_hip, left_knee, left_ankle)
        hip = right_hip
        shoulder = right_shoulder

    # 体幹前傾角（肩→股関節→水平）
    shoulder_to_hip = np.array(hip) - np.array(shoulder)
    horizontal = np.array([1.0, 0.0])
    cosine = np.dot(shoulder_to_hip, horizontal) / np.linalg.norm(shoulder_to_hip)
    trunk_angle = np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))

    return {
        "rear_knee": rear_knee,
        "front_knee": front_knee,
        "torso_forward": trunk_angle
    }
