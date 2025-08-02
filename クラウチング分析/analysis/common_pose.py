# analysis/common_pose.py
import cv2, mediapipe as mp

mp_pose     = mp.solutions.pose
mp_drawing  = mp.solutions.drawing_utils
_CONNECTION = mp_pose.POSE_CONNECTIONS
_DRAW_SPEC  = mp_drawing.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=2)

def detect_pose_bgr(img_bgr, static=True):
    """MediaPipe で骨格検出 → (landmarks | None, annotated_BGR) を返す"""
    with mp_pose.Pose(
            static_image_mode=static,
            model_complexity=2,                 # ⬅ ここで精度優先
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7) as pose:
        res = pose.process(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))

    if res.pose_landmarks is None:
        return None, img_bgr

    annotated = img_bgr.copy()
    mp_drawing.draw_landmarks(
        annotated, res.pose_landmarks, _CONNECTION,
        landmark_drawing_spec=_DRAW_SPEC,
        connection_drawing_spec=_DRAW_SPEC)
    return res.pose_landmarks, annotated
