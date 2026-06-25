"""에어소프트 플레이어 성능 대시보드 - 메인 애플리케이션"""
from __future__ import annotations

import io
from typing import Optional
import numpy as np
import pandas as pd
import streamlit as st

from src.data_loader import load_data
from src.api_weather import enrich_with_weather, make_dummy_weather
from src.charts import (
    make_bar_chart,
    make_box_chart,
    make_grouped_bar_bool,
    make_scatter_chart,
    make_violin_chart,
)

# ──────────────────────────────────────────────
# 페이지 설정
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="에어소프트 성능 대시보드",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 추가 CSS (카드형 KPI, 여백 조정)
st.markdown(
    """
    <style>
    .kpi-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 18px 14px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(47,107,95,0.10);
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #2F6B5F;
        line-height: 1.1;
    }
    .kpi-label {
        font-size: 0.82rem;
        color: #4A6F68;
        margin-top: 4px;
    }
    .status-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.80rem;
        font-weight: 600;
    }
    .badge-dummy { background:#FFF3CD; color:#856404; }
    .badge-real  { background:#D1E7DD; color:#0A3622; }
    .badge-api-ok   { background:#D1E7DD; color:#0A3622; }
    .badge-api-fail { background:#F8D7DA; color:#721C24; }
    section[data-testid="stSidebar"] { background: #EBF3F1; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────
# 헤더
# ──────────────────────────────────────────────
st.title("🎯 에어소프트 성능 대시보드")
st.markdown(
    """
    이 대시보드는 에어소프트 플레이어의 **장비 사용 여부**와 **사격 그립 유형**에 따른
    속도·정확도 변화를 탐색하기 위한 예시 분석 화면입니다.
    현재 데이터는 업로드된 엑셀 또는 자동 생성된 **더미 데이터**를 사용합니다.
    """
)

# ──────────────────────────────────────────────
# 사이드바: 파일 업로드
# ──────────────────────────────────────────────
with st.sidebar:
    st.header("📂 데이터 업로드")
    uploaded_files = st.file_uploader(
        "엑셀 파일을 하나 이상 선택하세요",
        type=["xlsx", "xls"],
        accept_multiple_files=True,
        help="형식이 다른 파일도 자동으로 병합됩니다.",
    )
    st.markdown("---")
    st.caption(
        "업로드하지 않으면 자동으로 더미 데이터를 생성합니다.\n\n"
        "민감한 원본 데이터는 저장소에 커밋하지 마세요."
    )

# ──────────────────────────────────────────────
# 데이터 로딩
# ──────────────────────────────────────────────
df_raw, is_dummy, load_messages = load_data(uploaded_files)

# 날씨 API 연동
with st.spinner("날씨 데이터 연동 중..."):
    indoor_mask = (df_raw.get("indoor_outdoor", pd.Series(["outdoor"] * len(df_raw))) == "indoor")
    df_enriched, api_success = enrich_with_weather(df_raw)

    if not api_success:
        weather_cols = ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "precipitation"]
        missing_w = [c for c in weather_cols if c not in df_enriched.columns or df_enriched[c].isna().all()]
        if missing_w:
            dummy_w = make_dummy_weather(len(df_enriched), indoor_mask)
            for col in weather_cols:
                if col not in df_enriched.columns:
                    df_enriched[col] = dummy_w[col].values
                else:
                    df_enriched[col] = df_enriched[col].fillna(dummy_w[col].values)

df = df_enriched.copy()

# ──────────────────────────────────────────────
# 섹션 1: 데이터 상태 안내
# ──────────────────────────────────────────────
st.markdown("## 1. 데이터 상태")
col_s1, col_s2, col_s3, col_s4 = st.columns(4)

with col_s1:
    badge_cls = "badge-dummy" if is_dummy else "badge-real"
    badge_txt = "더미 데이터" if is_dummy else "업로드 데이터"
    st.markdown(
        f'<div class="kpi-card"><span class="status-badge {badge_cls}">{badge_txt}</span>'
        f'<div class="kpi-label">데이터 소스</div></div>',
        unsafe_allow_html=True,
    )
with col_s2:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-value">{len(df):,}</div>'
        f'<div class="kpi-label">총 행 수</div></div>',
        unsafe_allow_html=True,
    )
with col_s3:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-value">{df.shape[1]}</div>'
        f'<div class="kpi-label">컬럼 수</div></div>',
        unsafe_allow_html=True,
    )
with col_s4:
    api_cls = "badge-api-ok" if api_success else "badge-api-fail"
    api_txt = "API 연결 성공" if api_success else "API 연결 실패"
    st.markdown(
        f'<div class="kpi-card"><span class="status-badge {api_cls}">{api_txt}</span>'
        f'<div class="kpi-label">Open-Meteo 날씨 API</div></div>',
        unsafe_allow_html=True,
    )

if is_dummy:
    st.info(
        "현재 **자동 생성된 더미 데이터**를 사용 중입니다. "
        "사이드바에서 엑셀 파일을 업로드하면 실제 데이터로 전환됩니다.",
        icon="ℹ️",
    )

if not api_success:
    st.warning(
        "외부 날씨 API 연결 실패: 더미/기존 값을 사용합니다. "
        "(인터넷 연결을 확인하거나 잠시 후 다시 시도하세요.)",
        icon="⚠️",
    )

for msg in load_messages:
    st.warning(msg)

st.markdown("---")

# ──────────────────────────────────────────────
# 사이드바: 필터
# ──────────────────────────────────────────────
with st.sidebar:
    st.header("🔧 필터")

    # 날짜
    if "date" in df.columns:
        dates_valid = pd.to_datetime(df["date"], errors="coerce").dropna()
        if not dates_valid.empty:
            min_d = dates_valid.min().date()
            max_d = dates_valid.max().date()
            date_range = st.date_input("날짜 범위", value=(min_d, max_d))
        else:
            date_range = None
    else:
        date_range = None

    # 실내/실외
    io_opts = sorted(df["indoor_outdoor"].dropna().unique().tolist()) if "indoor_outdoor" in df.columns else []
    io_sel = st.multiselect("실내/실외", options=io_opts, default=io_opts)

    # 숙련도
    exp_opts = sorted(df["experience_level"].dropna().unique().tolist()) if "experience_level" in df.columns else []
    exp_sel = st.multiselect("숙련도", options=exp_opts, default=exp_opts)

    # 전방손잡이
    fg_opts = ["전체", "사용 (True)", "미사용 (False)"]
    fg_sel = st.selectbox("전방손잡이 사용", fg_opts)

    # 개머리판
    st_opts = ["전체", "사용 (True)", "미사용 (False)"]
    st_sel = st.selectbox("개머리판 사용", st_opts)

    # 사격 그립
    grip_opts = sorted(df["shooting_grip"].dropna().unique().tolist()) if "shooting_grip" in df.columns else []
    grip_sel = st.multiselect("사격 그립", options=grip_opts, default=grip_opts)

    # 거리
    if "distance_m" in df.columns:
        dmin, dmax = float(df["distance_m"].min()), float(df["distance_m"].max())
        dist_range = st.slider("거리 (m)", dmin, dmax, (dmin, dmax), step=1.0)
    else:
        dist_range = None


def apply_filters(data: pd.DataFrame) -> pd.DataFrame:
    d = data.copy()

    if date_range and "date" in d.columns and len(date_range) == 2:
        d["_dt"] = pd.to_datetime(d["date"], errors="coerce")
        d = d[(d["_dt"].dt.date >= date_range[0]) & (d["_dt"].dt.date <= date_range[1])]
        d = d.drop(columns=["_dt"])

    if io_sel and "indoor_outdoor" in d.columns:
        d = d[d["indoor_outdoor"].isin(io_sel)]

    if exp_sel and "experience_level" in d.columns:
        d = d[d["experience_level"].isin(exp_sel)]

    if fg_sel != "전체" and "front_grip_used" in d.columns:
        fg_val = True if "True" in fg_sel else False
        d = d[d["front_grip_used"] == fg_val]

    if st_sel != "전체" and "stock_used" in d.columns:
        st_val = True if "True" in st_sel else False
        d = d[d["stock_used"] == st_val]

    if grip_sel and "shooting_grip" in d.columns:
        d = d[d["shooting_grip"].isin(grip_sel)]

    if dist_range and "distance_m" in d.columns:
        d = d[(d["distance_m"] >= dist_range[0]) & (d["distance_m"] <= dist_range[1])]

    return d


dff = apply_filters(df)

if dff.empty:
    st.error("선택한 필터 조건에 맞는 데이터가 없습니다. 필터를 조정해 주세요.")
    st.stop()

# ──────────────────────────────────────────────
# 섹션 2: KPI 카드
# ──────────────────────────────────────────────
st.markdown("## 2. 주요 성과 지표 (KPI)")


def kpi_card(label: str, value: str) -> str:
    return (
        f'<div class="kpi-card">'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-label">{label}</div>'
        f"</div>"
    )


kpi_cols = st.columns(6)
kpis = [
    ("평균 정확도 (%)", f'{dff["accuracy_pct"].mean():.1f}' if "accuracy_pct" in dff else "—"),
    ("평균 shots/sec", f'{dff["shots_per_sec"].mean():.2f}' if "shots_per_sec" in dff else "—"),
    ("평균 split time (s)", f'{dff["split_time_sec"].mean():.3f}' if "split_time_sec" in dff else "—"),
    ("평균 탄착군 (cm)", f'{dff["avg_group_size_cm"].mean():.1f}' if "avg_group_size_cm" in dff else "—"),
    ("총 세션 수", f'{len(dff):,}'),
    ("총 플레이어 수", f'{dff["player_id"].nunique():,}' if "player_id" in dff else "—"),
]
for col, (label, value) in zip(kpi_cols, kpis):
    col.markdown(kpi_card(label, value), unsafe_allow_html=True)

st.markdown("---")

# ──────────────────────────────────────────────
# 섹션 3: 장비 사용 여부별 성능 비교
# ──────────────────────────────────────────────
st.markdown("## 3. 장비 사용 여부별 성능 비교")

tab_fg, tab_st = st.tabs(["전방손잡이 (Front Grip)", "개머리판 (Stock)"])

with tab_fg:
    if "front_grip_used" in dff.columns and not dff["front_grip_used"].isna().all():
        c1, c2 = st.columns(2)
        with c1:
            if "accuracy_pct" in dff.columns:
                fig = make_grouped_bar_bool(dff, "front_grip_used", "accuracy_pct",
                                            "전방손잡이 사용 여부 × 정확도 (%)",
                                            "전방손잡이 사용", "전방손잡이 미사용")
                st.plotly_chart(fig)
        with c2:
            if "shots_per_sec" in dff.columns:
                fig = make_grouped_bar_bool(dff, "front_grip_used", "shots_per_sec",
                                            "전방손잡이 사용 여부 × shots/sec",
                                            "전방손잡이 사용", "전방손잡이 미사용")
                st.plotly_chart(fig)

        if "split_time_sec" in dff.columns:
            fig = make_box_chart(
                dff, x="front_grip_used", y="split_time_sec",
                title="전방손잡이 사용 여부별 split time 분포",
                color="front_grip_used",
            )
            st.plotly_chart(fig)
    else:
        st.info("front_grip_used 컬럼이 없거나 필터 후 데이터가 없습니다.")

with tab_st:
    if "stock_used" in dff.columns and not dff["stock_used"].isna().all():
        c1, c2 = st.columns(2)
        with c1:
            if "avg_group_size_cm" in dff.columns:
                fig = make_grouped_bar_bool(dff, "stock_used", "avg_group_size_cm",
                                            "개머리판 사용 여부 × 평균 탄착군 크기 (cm)",
                                            "개머리판 사용", "개머리판 미사용")
                st.plotly_chart(fig)
        with c2:
            if "accuracy_pct" in dff.columns:
                fig = make_grouped_bar_bool(dff, "stock_used", "accuracy_pct",
                                            "개머리판 사용 여부 × 정확도 (%)",
                                            "개머리판 사용", "개머리판 미사용")
                st.plotly_chart(fig)
    else:
        st.info("stock_used 컬럼이 없거나 필터 후 데이터가 없습니다.")

st.markdown("---")

# ──────────────────────────────────────────────
# 섹션 4: 사격 그립별 비교
# ──────────────────────────────────────────────
st.markdown("## 4. 사격 그립별 비교")

if "shooting_grip" in dff.columns:
    grip_agg = (
        dff.groupby("shooting_grip")[
            [c for c in ["accuracy_pct", "split_time_sec", "shots_per_sec"] if c in dff.columns]
        ]
        .mean()
        .reset_index()
    )

    metric_tabs = []
    if "accuracy_pct" in grip_agg.columns:
        metric_tabs.append("정확도")
    if "split_time_sec" in grip_agg.columns:
        metric_tabs.append("split time")
    if "shots_per_sec" in grip_agg.columns:
        metric_tabs.append("shots/sec")

    if metric_tabs:
        tabs = st.tabs(metric_tabs)
        tab_map = dict(zip(metric_tabs, tabs))

        if "정확도" in tab_map and "accuracy_pct" in grip_agg.columns:
            with tab_map["정확도"]:
                fig = make_bar_chart(grip_agg, x="shooting_grip", y="accuracy_pct",
                                     title="사격 그립별 평균 정확도 (%)")
                st.plotly_chart(fig)
                if "accuracy_pct" in dff.columns:
                    fig2 = make_violin_chart(dff, x="shooting_grip", y="accuracy_pct",
                                             title="사격 그립별 정확도 분포",
                                             color="shooting_grip")
                    st.plotly_chart(fig2)

        if "split time" in tab_map and "split_time_sec" in grip_agg.columns:
            with tab_map["split time"]:
                fig = make_bar_chart(grip_agg, x="shooting_grip", y="split_time_sec",
                                     title="사격 그립별 평균 split time (초)")
                st.plotly_chart(fig)

        if "shots/sec" in tab_map and "shots_per_sec" in grip_agg.columns:
            with tab_map["shots/sec"]:
                fig = make_bar_chart(grip_agg, x="shooting_grip", y="shots_per_sec",
                                     title="사격 그립별 평균 shots/sec")
                st.plotly_chart(fig)
else:
    st.info("shooting_grip 컬럼이 없습니다.")

st.markdown("---")

# ──────────────────────────────────────────────
# 섹션 5: 환경 조건 영향
# ──────────────────────────────────────────────
st.markdown("## 5. 환경 조건 영향")

env_c1, env_c2 = st.columns(2)
with env_c1:
    if "wind_speed_10m" in dff.columns and "accuracy_pct" in dff.columns:
        fig = make_scatter_chart(
            dff, x="wind_speed_10m", y="accuracy_pct",
            title="풍속 × 정확도 (실내/실외 구분)",
            color="indoor_outdoor" if "indoor_outdoor" in dff.columns else None,
            trendline=True, opacity=0.55,
        )
        st.plotly_chart(fig)

with env_c2:
    if "temperature_2m" in dff.columns and "shots_per_sec" in dff.columns:
        fig = make_scatter_chart(
            dff, x="temperature_2m", y="shots_per_sec",
            title="기온 × shots/sec (실내/실외 구분)",
            color="indoor_outdoor" if "indoor_outdoor" in dff.columns else None,
            trendline=True, opacity=0.55,
        )
        st.plotly_chart(fig)

if "distance_m" in dff.columns and "accuracy_pct" in dff.columns:
    fig = make_scatter_chart(
        dff, x="distance_m", y="accuracy_pct",
        title="사격 거리 × 정확도",
        color="experience_level" if "experience_level" in dff.columns else None,
        trendline=True, opacity=0.55,
    )
    st.plotly_chart(fig)

st.markdown("---")

# ──────────────────────────────────────────────
# 섹션 6: 원본/정제 데이터 미리보기 및 다운로드
# ──────────────────────────────────────────────
st.markdown("## 6. 데이터 미리보기")

with st.expander("필터 적용 데이터 미리보기 (처음 200행)", expanded=False):
    st.dataframe(dff.head(200))

csv_buf = io.StringIO()
dff.to_csv(csv_buf, index=False, encoding="utf-8-sig")
st.download_button(
    label="📥 CSV 다운로드 (필터 적용)",
    data=csv_buf.getvalue().encode("utf-8-sig"),
    file_name="airsoft_performance_filtered.csv",
    mime="text/csv",
)

st.markdown("---")

# ──────────────────────────────────────────────
# 섹션 7: 해석 주의사항
# ──────────────────────────────────────────────
st.markdown("## 7. 해석 주의사항")
st.info(
    """
    **이 대시보드에 대하여:**

    - 이 저장소에는 민감한 원본 데이터 파일을 포함하지 않습니다.
    - 더미 데이터는 실제 과학적 성능 검증 데이터가 아닙니다. 시각화 목적으로 생성된 예시입니다.
    - 차트에서 보이는 경향은 인과관계가 아닌 상관관계이며, 과학적 결론으로 해석하지 마세요.
    - 이 프로젝트는 에어소프트 스포츠/취미 활동의 장비 사용 유형 탐색을 목적으로 합니다.
    - 실제 화기 개조, 위력 증가, 살상력, 불법 무기 제작과 관련된 정보를 다루지 않습니다.
    """,
    icon="ℹ️",
)

with st.expander("컬럼 설명"):
    st.markdown(
        """
        | 컬럼 | 설명 |
        |------|------|
        | `front_grip_used` | 전방손잡이(포어그립) 사용 여부 |
        | `pistol_grip_type` | 권총손잡이 유형 (standard/ergonomic/vertical_angle) |
        | `stock_used` | 개머리판(스톡) 사용 여부 |
        | `stock_type` | 개머리판 유형 (fixed/adjustable/folding/none) |
        | `shooting_grip` | 사격 그립 자세 (c-clamp/magwell/traditional 등) |
        | `accuracy_pct` | 명중률 (%) = hit_count / rounds_fired × 100 |
        | `shots_per_sec` | 초당 사격 수 |
        | `split_time_sec` | 연속 사격 간격 (초) |
        | `avg_group_size_cm` | 평균 탄착군 크기 (cm) |
        | `temperature_2m` | 지상 2m 기온 (°C) |
        | `wind_speed_10m` | 지상 10m 풍속 (m/s) |
        """
    )
