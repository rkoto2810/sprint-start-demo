import cv2, numpy as np, mediapipe as mp

mp_pose = mp.solutions.pose

def _horiz_angle(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    return np.degrees(np.arctan2(abs(dy), abs(dx)))

def _inner_angle(a, b, c):
    ba, bc = np.array(a) - np.array(b), np.array(c) - np.array(b)
    cosang = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    return np.degrees(np.arccos(np.clip(cosang, -1, 1)))

def analyze_air_image(path: str, direction="auto"):
    with mp_pose.Pose(static_image_mode=True) as pose:
        img = cv2.imread(path)
        if img is None:
            return None
        h, w = img.shape[:2]
        res = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    if res.pose_landmarks is None:
        return None

    lm = res.pose_landmarks.landmark
    get = lambda n: [lm[getattr(mp_pose.PoseLandmark, n).value].x * w,
                     lm[getattr(mp_pose.PoseLandmark, n).value].y * h]

    # 1️⃣ 進行方向判定
    if direction == "auto":
        votes = sum(1 if get(r)[0] > get(l)[0] else -1
                    for r,l in (("RIGHT_HIP","LEFT_HIP"),
                                ("RIGHT_SHOULDER","LEFT_SHOULDER"),
                                ("RIGHT_ANKLE","LEFT_ANKLE")))
        rightward = votes > 0
    else:
        rightward = (direction.lower() == "right")

    # 2️⃣ ベースランドマーク
    shd, hip = (get("RIGHT_SHOULDER"), get("RIGHT_HIP")) if rightward else \
               (get("LEFT_SHOULDER") , get("LEFT_HIP"))

    # 3️⃣ “後ろ脚” 足首を自動選択
    ankle_R, ankle_L = get("RIGHT_ANKLE"), get("LEFT_ANKLE")
    ankle_back = ankle_L if rightward else ankle_R   # 仮
    # 後方判定: 右向き→x小さい方 / 左向き→x大きい方
    if rightward:
        ankle_back = ankle_R if ankle_R[0] < ankle_L[0] else ankle_L
    else:
        ankle_back = ankle_R if ankle_R[0] > ankle_L[0] else ankle_L

    upper  = _horiz_angle(shd, hip)
    lower  = _horiz_angle(hip, ankle_back)
    kunoji = _inner_angle(shd, hip, ankle_back)

    return {"upper": upper, "lower": lower, "kunoji": kunoji}
