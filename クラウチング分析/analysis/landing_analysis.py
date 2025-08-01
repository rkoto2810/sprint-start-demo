# analysis/landing_analysis.py  ― COM-offset を 3 段階評価に変更
import cv2, numpy as np, mediapipe as mp
mp_pose = mp.solutions.pose
_dist = lambda a,b: np.linalg.norm(np.array(a)-np.array(b))
_ang  = lambda a,b: np.degrees(np.arctan2(abs(b[1]-a[1]), abs(b[0]-a[0])))

def analyze_landing_image(path, *, landing_leg="left",
                          height_cm=170, parallax=False):

    # ---------- MediaPipe ----------
    with mp_pose.Pose(static_image_mode=True) as pose:
        img=cv2.imread(path); h,w=img.shape[:2]
        res=pose.process(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
    if res.pose_landmarks is None: return None
    lm=res.pose_landmarks.landmark
    g=lambda n:[lm[getattr(mp_pose.PoseLandmark,n).value].x*w,
                lm[getattr(mp_pose.PoseLandmark,n).value].y*h]

    # ---------- スケール ----------
    px2cm = height_cm / max(abs(g("RIGHT_HEEL")[1]-g("RIGHT_EAR")[1]),1)

    if landing_leg=="left":
        ankle,knee   = g("LEFT_ANKLE"), g("LEFT_KNEE")
        opp_knee     = g("RIGHT_KNEE")
        shd,hip      = g("LEFT_SHOULDER"), g("LEFT_HIP")
    else:
        ankle,knee   = g("RIGHT_ANKLE"), g("RIGHT_KNEE")
        opp_knee     = g("LEFT_KNEE")
        shd,hip      = g("RIGHT_SHOULDER"), g("RIGHT_HIP")

    # COM 位置（0.4 上半身 + 0.6 下半身）
    upper = [(g("LEFT_SHOULDER")[0]+g("RIGHT_SHOULDER")[0])/2,
             (g("LEFT_SHOULDER")[1]+g("RIGHT_SHOULDER")[1])/2]
    lower = [(g("LEFT_HIP")[0]+g("RIGHT_HIP")[0])/2,
             (g("LEFT_HIP")[1]+g("RIGHT_HIP")[1])/2]
    com   = [0.4*upper[0]+0.6*lower[0], 0.4*upper[1]+0.6*lower[1]]

    # ---------- 指標 ----------
    # COM が足首より前 (=+), 後ろ (=-)
    com_dx_px = com[0] - ankle[0]
    # 符号だけ判定に使えばスケール誤差を受けにくい
    if   com_dx_px >  0: com_grade = "○ 乗り込み良好"
    elif -5 < com_dx_px <= 0: com_grade = "△ ややブレーキ"
    else: com_grade = "× ブレーキ大"

    shin_angle = _ang(knee, ankle)
    trunk      = _ang(shd , hip)
    diff       = abs(shin_angle - trunk)
    knee_gap_cm= _dist(knee, opp_knee)*px2cm
    knee_per   = knee_gap_cm / height_cm * 100
    if parallax: knee_gap_cm *=.7; knee_per *=.7  # 任意補正

    # 簡易コメント
    sh_comment = "✅ 良好" if 35<=shin_angle<=45 else "⚠ 要改善"
    kn_comment = "✅ 良好" if knee_per<=10        else "⚠ 要改善"
    df_comment = "✅ 良好" if diff<=5             else "⚠ 要改善"

    return {
        "com_grade"     : com_grade,
        "shin_angle"    : shin_angle,
        "knee_gap_perc" : knee_per,
        "shin_trunk"    : diff,
        "shin_comment"  : sh_comment,
        "knee_comment"  : kn_comment,
        "diff_comment"  : df_comment
    }
