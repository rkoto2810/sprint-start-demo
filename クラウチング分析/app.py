# ============================ app.py ============================
"""
Sprint-Start Demo — Streamlit Front-End
--------------------------------------

* 4 フェーズ（Set / Drive / Air / Landing）の静止画像をアップロード
* MediaPipe Pose で骨格を推定し，角度を即時表示
* ✔ チェックで骨格ラインのオン・オフ
"""

# ────────────────────────────────────────────────────────────────
#  0. 事前セットアップ：モデルキャッシュ先を /tmp に
# ────────────────────────────────────────────────────────────────
import os, tempfile

os.environ["MEDIAPIPE_CACHE_DIR"] = tempfile.mkdtemp(prefix="mp_cache_")

# ────────────────────────────────────────────────────────────────
#  1. インポート
# ────────────────────────────────────────────────────────────────
from __future__ import annotations

import pathlib
import tempfile
from typing import Callable, Any

import streamlit as st
from PIL import Image

from analysis.set_analysis import analyze_set_image
from analysis.drive_analysis import analyze_drive_image
from analysis.air_analysis import analyze_air_image
from analysis.landing_analysis import analyze_landing_image

ROOT = pathlib.Path(__file__).parent
ASSETS = ROOT / "assets"          # 参考画像を置く場合用（無くても OK）

st.set_page_config(page_title="クラウチングスタート解析", layout="wide")
st.title("クラウチングスタート 画像解析ツール")

# ────────────────────────────────────────────────────────────────
#  2. 共通ヘルパー
# ────────────────────────────────────────────────────────────────
def _process_upload(
    label: str,
    analyzer: Callable[..., dict[str, Any] | None],
    *,
    analyzer_kwargs: dict[str, Any] | None = None,
    metrics: list[tuple[str, str]] | None = None,
    show_skel: bool,
) -> None:
    """アップロード → 解析 → 結果表示（Streamlit 共通処理）"""
    file = st.file_uploader(label, ["jpg", "jpeg", "png"])
    if not file:
        return

    # 一時ファイルへ保存
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(file.read())
        img_path = tmp.name

    # 解析
    kwargs = analyzer_kwargs or {}
    kwargs["with_overlay"] = show_skel
    res = analyzer(img_path, **kwargs)

    # 表示用画像選択
    if res and show_skel and "overlay" in res:
        img_show = Image.fromarray(res["overlay"][:, :, ::-1])  # BGR → RGB
    else:
        img_show = Image.open(img_path)

    st.image(img_show, caption="骨格オーバーレイ" if show_skel else "入力画像")

    # メトリクス表示
    if res:
        if metrics:
            cols = st.columns(len(metrics))
            for (key, label_txt), col in zip(metrics, cols):
                col.metric(label_txt, f"{res[key]:.1f}°")
        else:
            st.write(res)
    else:
        st.error("骨格検出に失敗しました。")


# ────────────────────────────────────────────────────────────────
#  3. UI レイアウト
# ────────────────────────────────────────────────────────────────
tabs = st.tabs(["Set", "Drive", "Air", "Landing"])

# --------------------------- Set ------------------------------- #
with tabs[0]:
    st.header("Set (クラウチング姿勢)")
    if (ASSETS / "ref_set.jpg").exists():
        st.image(ASSETS / "ref_set.jpg", caption="参考姿勢", use_column_width=True)

    show_skel = st.checkbox("骨格ラインを表示する", value=True, key="set_skel")
    front_leg = st.radio("前脚を選択", ("左", "右"), horizontal=True, key="set_leg")

    _process_upload(
        "Set フェーズ画像をアップロード",
        analyze_set_image,
        analyzer_kwargs={"front_leg": "left" if front_leg == "左" else "right"},
        metrics=[
            ("rear_knee", "後脚膝角"),
            ("front_knee", "前脚膝角"),
            ("torso_forward", "体幹前傾角"),
        ],
        show_skel=show_skel,
    )

# --------------------------- Drive ----------------------------- #
with tabs[1]:
    st.header("Drive (押し出し)")
    if (ASSETS / "ref_drive.jpg").exists():
        st.image(ASSETS / "ref_drive.jpg", caption="参考姿勢", use_column_width=True)

    show_skel = st.checkbox("骨格ラインを表示する", value=True, key="drive_skel")
    front_leg = st.radio("前脚を選択", ("左", "右"), horizontal=True, key="drive_leg")

    _process_upload(
        "Drive フェーズ画像をアップロード",
        analyze_drive_image,
        analyzer_kwargs={"front_leg": "left" if front_leg == "左" else "right"},
        metrics=[("tibia_angle", "脛骨角")],
        show_skel=show_skel,
    )

# --------------------------- Air ------------------------------- #
with tabs[2]:
    st.header("Air (浮遊)")
    if (ASSETS / "ref_air.jpg").exists():
        st.image(ASSETS / "ref_air.jpg", caption="参考姿勢", use_column_width=True)

    show_skel = st.checkbox("骨格ラインを表示する", value=True, key="air_skel")
    direction = st.radio("走行方向", ("自動", "右へ", "左へ"), horizontal=True, key="air_dir")
    dir_kw = {"自動": "auto", "右へ": "right", "左へ": "left"}[direction]

    _process_upload(
        "Air フェーズ画像をアップロード",
        analyze_air_image,
        analyzer_kwargs={"direction": dir_kw},
        metrics=[
            ("upper", "体幹前傾"),
            ("lower", "後脚角"),
            ("hip_angle", "くの字角"),
        ],
        show_skel=show_skel,
    )

# --------------------------- Landing --------------------------- #
with tabs[3]:
    st.header("Landing (接地)")
    if (ASSETS / "ref_landing.jpg").exists():
        st.image(ASSETS / "ref_landing.jpg", caption="参考姿勢", use_column_width=True)

    show_skel = st.checkbox("骨格ラインを表示する", value=True, key="land_skel")
    front_leg = st.radio("着地脚を選択", ("左", "右"), horizontal=True, key="land_leg")

    _process_upload(
        "Landing フェーズ画像をアップロード",
        analyze_landing_image,
        analyzer_kwargs={"front_leg": "left" if front_leg == "左" else "right"},
        metrics=[
            ("front_knee", "膝屈曲"),
            ("shin_angle", "脛前傾"),
            ("torso_forward", "体幹前傾"),
        ],
        show_skel=show_skel,
    )
