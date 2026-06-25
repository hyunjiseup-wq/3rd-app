"""차트 생성 모듈 - Plotly 기반 시각화 함수 모음"""
from __future__ import annotations

from typing import Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 공통 색상 팔레트 — 색상환을 고르게 분산해 범주별 명확한 구분
PRIMARY   = "#2F6B5F"  # 다크 틸 (테마 기준색 유지)
SECONDARY = "#E07B54"  # 웜 오렌지
ACCENT    = "#4B8FC7"  # 미디엄 블루
PALETTE   = [
    PRIMARY,    # 다크 틸
    SECONDARY,  # 오렌지
    ACCENT,     # 블루
    "#D4A843",  # 앰버/골드
    "#9B6BC9",  # 퍼플
    "#6BAF5A",  # 리프 그린
]

# True/False 비교 차트: 틸(True) vs 오렌지(False) — 보색 대비
BOOL_COLOR_MAP = {True: PRIMARY, False: SECONDARY, "True": PRIMARY, "False": SECONDARY}


def _base_layout(fig: go.Figure, title: str) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color="#1F2933")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="sans-serif", color="#1F2933"),
        margin=dict(t=50, b=40, l=20, r=20),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(gridcolor="#E8EEEC", linecolor="#D0DEDA")
    fig.update_yaxes(gridcolor="#E8EEEC", linecolor="#D0DEDA")
    return fig


def make_bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: Optional[str] = None,
    barmode: str = "group",
    orientation: str = "v",
) -> go.Figure:
    """그룹별 막대 차트."""
    fig = px.bar(
        df,
        x=x,
        y=y,
        color=color,
        barmode=barmode,
        orientation=orientation,
        color_discrete_sequence=PALETTE,
        text_auto=".1f",
    )
    return _base_layout(fig, title)


def make_box_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: Optional[str] = None,
    points: str = "outliers",
) -> go.Figure:
    """박스플롯 차트."""
    fig = px.box(
        df,
        x=x,
        y=y,
        color=color,
        points=points,
        color_discrete_sequence=PALETTE,
    )
    return _base_layout(fig, title)


def make_scatter_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: Optional[str] = None,
    size: Optional[str] = None,
    trendline: bool = False,
    opacity: float = 0.6,
) -> go.Figure:
    """산점도 차트."""
    tl = "ols" if trendline else None
    fig = px.scatter(
        df,
        x=x,
        y=y,
        color=color,
        size=size,
        trendline=tl,
        opacity=opacity,
        color_discrete_sequence=PALETTE,
    )
    return _base_layout(fig, title)


def make_line_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: Optional[str] = None,
    markers: bool = True,
) -> go.Figure:
    """라인 차트."""
    fig = px.line(
        df,
        x=x,
        y=y,
        color=color,
        markers=markers,
        color_discrete_sequence=PALETTE,
    )
    return _base_layout(fig, title)


def make_grouped_bar_bool(
    df: pd.DataFrame,
    bool_col: str,
    metric_col: str,
    title: str,
    label_true: str = "사용",
    label_false: str = "미사용",
) -> go.Figure:
    """bool 컬럼 기준 두 그룹의 수치 비교 막대 차트."""
    agg = (
        df.groupby(bool_col)[metric_col]
        .agg(["mean", "std", "count"])
        .reset_index()
    )
    agg["label"] = agg[bool_col].map({True: label_true, False: label_false})
    fig = px.bar(
        agg,
        x="label",
        y="mean",
        error_y="std",
        color="label",
        color_discrete_map={label_true: PRIMARY, label_false: SECONDARY},
        text="mean",
        text_auto=".1f",
    )
    return _base_layout(fig, title)


def make_violin_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: Optional[str] = None,
) -> go.Figure:
    """바이올린 플롯."""
    fig = px.violin(
        df,
        x=x,
        y=y,
        color=color,
        box=True,
        points="outliers",
        color_discrete_sequence=PALETTE,
    )
    return _base_layout(fig, title)


def make_heatmap(
    df: pd.DataFrame,
    x: str,
    y: str,
    value: str,
    title: str,
) -> go.Figure:
    """피벗 히트맵."""
    pivot = df.pivot_table(index=y, columns=x, values=value, aggfunc="mean")
    fig = px.imshow(
        pivot,
        color_continuous_scale=[[0, ACCENT], [0.5, SECONDARY], [1, PRIMARY]],
        text_auto=".1f",
    )
    return _base_layout(fig, title)
