# app.py  ―  全面置き換え用
# ------------------------------------------------------------
import streamlit as st
from pathlib import Path
from PIL import Image

# ---------- 解析モジュール ----------
from analysis.set_analysis     import analyze_set_image
from analysis.drive_analysis   import analyze_drive_image
from analysis.air_analysis     import analyze_air_image
from analysis.landing_analysis import analyze_landing_image

# ---------- 定数 ----------
ROOT   = Path(__file__).parent           # クローンした repo 内のクラウチング分析フォルダ
ASSETS = ROOT / "assets"                # ref_*.jpg を置いたフォルダ

st.set_page_config(page_title="クラウチング動作分析", layout="centered")
st.title("クラウチング動作　フォームチェック")

# ------------------------------------------------------------
# 4 つのタブ
tabs = st.tabs(["① Set", "② Drive", "③ Air", "④ Landing"])

# ---------- ① Set ----------
with tabs[0]:
    st.header("① Set 局面")
    st.image(str(ASSETS / "ref_set.jpg"),
             caption="参考：Set のスクリーンショット例")

    uploaded = st.file_uploader("Set の写真をアップロード", type=["jpg", "jpeg", "png"])
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="アップロード画像")           # ここは PIL.Image なのでそのまま OK
        angle = analyze_set_image(img)
        st.info(f"骨盤角度: **{angle:.1f}°**")

# ---------- ② Drive ----------
with tabs[1]:
    st.header("② Drive 局面")
    st.image(str(ASSETS / "ref_drive.jpg"),
             caption="参考：Drive のスクリーンショット例")

    uploaded = st.file_uploader("Drive の写真をアップロード", type=["jpg", "jpeg", "png"])
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="アップロード画像")
        angle = analyze_drive_image(img)
        st.info(f"股関節角度: **{angle:.1f}°**")

# ---------- ③ Air ----------
with tabs[2]:
    st.header("③ Air 局面")
    st.image(str(ASSETS / "ref_air.jpg"),
             caption="参考：Air のスクリーンショット例")

    uploaded = st.file_uploader("Air の写真をアップロード", type=["jpg", "jpeg", "png"])
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="アップロード画像")
        angle = analyze_air_image(img)
        st.info(f"体幹角度: **{angle:.1f}°**")

# ---------- ④ Landing ----------
with tabs[3]:
    st.header("④ Landing 局面")
    st.image(str(ASSETS / "ref_landing.jpg"),
             caption="参考：Landing のスクリーンショット例")

    uploaded = st.file_uploader("Landing の写真をアップロード", type=["jpg", "jpeg", "png"])
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="アップロード画像")
        angle = analyze_landing_image(img)
        st.info(f"膝角度: **{angle:.1f}°**")
# ------------------------------------------------------------
