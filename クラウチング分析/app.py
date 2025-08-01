# app.py  ―  説明文付きフルバージョン
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
import streamlit as st, tempfile, pathlib
from PIL import Image

# 解析モジュール
from analysis.set_analysis     import analyze_set_image
from analysis.drive_analysis   import analyze_drive_image
from analysis.air_analysis     import analyze_air_image
from analysis.landing_analysis import analyze_landing_image

ROOT   = pathlib.Path(__file__).parent
ASSETS = ROOT / "assets"   # ref_set.jpg などを置いたフォルダ

st.set_page_config(page_title="クラウチングスタート解析", layout="wide")
st.title("クラウチングスタート 画像解析ツール")
st.caption("※60 fps 以上の動画をコマ送りして得たスクリーンショットを推奨します。")

tabs = st.tabs(["① Set", "② Drive", "③ Air", "④ Landing"])

# ─────────────────────────────── ① Set
with tabs[0]:
    st.header("① Set 局面")
    st.image(str(ASSETS / "ref_set.jpg"), caption="参考：Set のスクリーンショット例")

    st.markdown("""
**撮影のポイント**  
* 腰を上げて静止したフレームを選ぶ  
* カメラは身体真横・腰の高さ  
* 60 fps 以上推奨（30 fps 以下だとズレが大）  
* 前脚がどちらかを下で選択
""")

    front_leg = st.radio("前脚を選択", ("左", "右"))
    up_file   = st.file_uploader("Set 画像をアップロード", ["jpg", "jpeg", "png"])

    if up_file:
        # 一時ファイルへ保存 → パスで解析関数に渡す
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(up_file.read())
            img_path = tmp.name

        st.image(Image.open(img_path), caption="入力画像")
        res = analyze_set_image(img_path, "left" if front_leg == "左" else "right")

        if res:
            c1, c2, c3 = st.columns(3)
            c1.metric("後脚膝角",  f"{res['rear_knee']:.1f}°")
            c2.metric("前脚膝角",  f"{res['front_knee']:.1f}°")
            c3.metric("体幹前傾角",f"{res['torso_forward']:.1f}°")
        else:
            st.error("骨格検出に失敗しました。")

# ─────────────────────────────── ② Drive
with tabs[1]:
    st.header("② Drive 局面")
    st.image(str(ASSETS / "ref_drive.jpg"),
             caption="60 fps 以上の動画で『スネが最も倒れた』フレームを使用")

    st.markdown("脛骨前傾角を測りたい脚を選択して画像をアップロードしてください。")

    drv_leg = st.radio("測定脚", ("左", "右"))
    drv_file = st.file_uploader("Drive 画像", ["jpg", "jpeg", "png"], key="drv")

    if drv_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(drv_file.read())
            img_path = tmp.name

        st.image(Image.open(img_path), caption="入力画像")
        res = analyze_drive_image(img_path, "left" if drv_leg == "左" else "right")
        if res:
            st.metric("脛骨角", f"{res['tibia_angle']:.1f}°")
        else:
            st.error("骨格検出に失敗しました。")

# ─────────────────────────────── ③ Air
with tabs[2]:
    st.header("③ Air 局面")
    st.image(str(ASSETS / "ref_air.jpg"),
             caption="股関節が最も伸びきったフレームを使用")

    st.markdown("進行方向が不明なら **自動判定** のままで OK です。")
    air_dir = st.radio("進行方向", ("右向き", "左向き", "自動判定"))
    air_file = st.file_uploader("Air 画像", ["jpg", "jpeg", "png"], key="air")

    if air_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(air_file.read())
            img_path = tmp.name

        st.image(Image.open(img_path), caption="入力画像")
        dir_arg = {"右向き": "right", "左向き": "left"}.get(air_dir, "auto")
        res = analyze_air_image(img_path, dir_arg)
        if res:
            c1, c2, c3 = st.columns(3)
            c1.metric("上半身角", f"{res['upper']:.1f}°")
            c2.metric("下半身角", f"{res['lower']:.1f}°")
            c3.metric("くの字角", f"{res['kunoji']:.1f}°")
        else:
            st.error("骨格検出に失敗しました。")

# ─────────────────────────────── ④ Landing
with tabs[3]:
    st.header("④ Landing 局面")
    st.image(str(ASSETS / "ref_landing.jpg"),
             caption="1歩目着地直後のフレームを使用")

    st.markdown("""
**評価項目**  
* 乗り込み判定（COM が足首より前か）  
* 脛骨角（35〜45° が理想）  
* 膝間距離（≤10 %Ht）  
* 脛‐体幹差（≤5°）
""")

    height_cm = st.number_input("選手身長 (cm)", 100, 250, 170)
    land_leg  = st.radio("着地脚", ("左", "右"))
    land_file = st.file_uploader("Landing 画像", ["jpg", "jpeg", "png"], key="land")

    if land_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(land_file.read())
            img_path = tmp.name

        st.image(Image.open(img_path), caption="入力画像")
        res = analyze_landing_image(
            img_path,
            landing_leg="left" if land_leg == "左" else "right",
            height_cm=height_cm,
            parallax=False)

        if res:
            c1, c2, c3 = st.columns(3)
            c1.metric("乗り込み判定", res['com_grade'])
            c2.metric("脛骨角", f"{res['shin_angle']:.1f}°", delta=res['shin_comment'])
            c3.metric("膝間距離", f"{res['knee_gap_perc']:.1f} %Ht", delta=res['knee_comment'])
            st.metric("脛‐体幹差", f"{res['shin_trunk']:.1f}°", delta=res['diff_comment'])
        else:
            st.error("骨格検出に失敗しました。")
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
