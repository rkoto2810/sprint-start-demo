import cv2
import numpy as np
import mediapipe as mp

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    return np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))

def analyze_set_image(image_path, front_leg="left"):
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=True)

    image = cv2.imread(image_path)
    if image is None:
        return None

    results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    if not results.pose_landmarks:
        return None

    landmarks = results.pose_landmarks.landmark

    def get_coords(lm):
        return [lm.x, lm.y]

    if front_leg == "left":
        hip_f = get_coords(landmarks[mp_pose.PoseLandmark.LEFT_HIP])
        knee_f = get_coords(landmarks[mp_pose.PoseLandmark.LEFT_KNEE])
        ankle_f = get_coords(landmarks[mp_pose.PoseLandmark.LEFT_ANKLE])

        hip_r = get_coords(landmarks[mp_pose.PoseLandmark.RIGHT_HIP])
        knee_r = get_coords(landmarks[mp_pose.PoseLandmark.RIGHT_KNEE])
        ankle_r = get_coords(landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE])

        shoulder = get_coords(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER])
    else:
        hip_f = get_coords(landmarks[mp_pose.PoseLandmark.RIGHT_HIP])
        knee_f = get_coords(landmarks[mp_pose.PoseLandmark.RIGHT_KNEE])
        ankle_f = get_coords(landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE])

        hip_r = get_coords(landmarks[mp_pose.PoseLandmark.LEFT_HIP])
        knee_r = get_coords(landmarks[mp_pose.PoseLandmark.LEFT_KNEE])
        ankle_r = get_coords(landmarks[mp_pose.PoseLandmark.LEFT_ANKLE])

        shoulder = get_coords(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER])

    front_knee_angle = calculate_angle(hip_f, knee_f, ankle_f)
    rear_knee_angle  = calculate_angle(hip_r, knee_r, ankle_r)

    shoulder_to_hip = np.array(hip_f) - np.array(shoulder)
    horizontal = np.array([1, 0])
    trunk_angle = np.degrees(np.arccos(np.clip(
        np.dot(shoulder_to_hip, horizontal) /
        (np.linalg.norm(shoulder_to_hip) * np.linalg.norm(horizontal)), -1.0, 1.0)))

    return {
        "rear_knee": rear_knee_angle,
        "front_knee": front_knee_angle,
        "torso_forward": trunk_angle
    }
