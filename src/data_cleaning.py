"""데이터 정제 모듈 - 컬럼 정규화, 타입 변환, 결측 처리"""
from __future__ import annotations

from typing import Optional
import numpy as np
import pandas as pd

COLUMN_ALIASES: dict[str, list[str]] = {
    "session_id": ["session_id", "session", "세션", "세션id", "게임id"],
    "player_id": ["player_id", "player", "플레이어", "사용자", "참가자", "player_no"],
    "date": ["date", "session_date", "날짜", "측정일", "게임일", "game_date"],
    "location_name": ["location_name", "location", "장소", "필드명", "field", "필드"],
    "latitude": ["latitude", "lat", "위도"],
    "longitude": ["longitude", "lon", "lng", "경도"],
    "front_grip_used": ["front_grip_used", "front_grip", "전방손잡이", "포어그립", "수직손잡이", "fg_used"],
    "pistol_grip_type": ["pistol_grip_type", "pistol_grip", "권총손잡이", "피스톨그립", "grip_type"],
    "stock_used": ["stock_used", "stock", "개머리판", "스톡", "st_used"],
    "stock_type": ["stock_type", "스톡종류", "개머리판종류"],
    "shooting_grip": ["shooting_grip", "grip_style", "사격그립", "그립자세", "grip"],
    "stance": ["stance", "자세", "사격자세", "position"],
    "distance_m": ["distance_m", "distance", "거리", "사거리_m", "사거리", "dist_m", "dist"],
    "target_type": ["target_type", "target", "표적", "타겟"],
    "rounds_fired": ["rounds_fired", "shots", "발사수", "사격수", "rounds", "fired"],
    "hit_count": ["hit_count", "hits", "명중수", "히트수", "hit"],
    "miss_count": ["miss_count", "misses", "빗나간수", "miss"],
    "accuracy_pct": ["accuracy_pct", "accuracy", "정확도", "명중률", "hit_rate"],
    "split_time_sec": ["split_time_sec", "split_time", "스플릿", "분할시간"],
    "shots_per_sec": ["shots_per_sec", "rate_of_fire", "초당발사", "발사속도"],
    "reaction_time_sec": ["reaction_time_sec", "reaction_time", "반응시간"],
    "avg_group_size_cm": ["avg_group_size_cm", "group_size", "집탄군", "탄착군크기"],
    "equipment_weight_g": ["equipment_weight_g", "weight", "장비무게", "중량"],
    "experience_level": ["experience_level", "experience", "숙련도", "레벨", "exp_level"],
    "indoor_outdoor": ["indoor_outdoor", "environment", "실내외", "환경"],
    "temperature_2m": ["temperature_2m", "temperature", "기온", "온도", "temp"],
    "relative_humidity_2m": ["relative_humidity_2m", "humidity", "습도", "상대습도"],
    "wind_speed_10m": ["wind_speed_10m", "wind_speed", "풍속", "바람"],
    "precipitation": ["precipitation", "rain", "강수량", "비"],
}

NUMERIC_COLS = [
    "latitude", "longitude", "distance_m", "rounds_fired", "hit_count",
    "miss_count", "accuracy_pct", "split_time_sec", "shots_per_sec",
    "reaction_time_sec", "avg_group_size_cm", "equipment_weight_g",
    "temperature_2m", "relative_humidity_2m", "wind_speed_10m", "precipitation",
]

BOOL_COLS = ["front_grip_used", "stock_used"]

CATEGORICAL_COLS = [
    "pistol_grip_type", "stock_type", "shooting_grip", "stance",
    "experience_level", "indoor_outdoor", "target_type",
]


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """컬럼명을 소문자/공백→언더스코어로 정규화하고 별칭을 매핑한다."""
    rename_map: dict[str, str] = {}
    lower_cols = {c.lower().strip().replace(" ", "_"): c for c in df.columns}

    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            key = alias.lower().strip().replace(" ", "_")
            if key in lower_cols and canonical not in rename_map.values():
                rename_map[lower_cols[key]] = canonical
                break

    return df.rename(columns=rename_map)


def coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """숫자 컬럼을 강제 변환하고 변환 불가 값은 NaN으로 처리한다."""
    df = df.copy()
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def coerce_bool(df: pd.DataFrame) -> pd.DataFrame:
    """불리언 컬럼을 True/False로 통일한다."""
    df = df.copy()
    truthy = {"true", "1", "yes", "y", "예", "사용", "있음"}
    for col in BOOL_COLS:
        if col in df.columns:
            df[col] = df[col].astype(str).str.lower().str.strip().isin(truthy)
    return df


def coerce_dates(df: pd.DataFrame) -> pd.DataFrame:
    """날짜 컬럼을 파이썬 date 객체로 통일한다."""
    df = df.copy()
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    return df


def fill_missing(df: pd.DataFrame) -> pd.DataFrame:
    """필수 파생 컬럼이 없으면 계산하거나 기본값으로 채운다."""
    df = df.copy()

    if "rounds_fired" in df.columns and "hit_count" in df.columns:
        if "accuracy_pct" not in df.columns:
            df["accuracy_pct"] = (df["hit_count"] / df["rounds_fired"] * 100).round(2)
        if "miss_count" not in df.columns:
            df["miss_count"] = (df["rounds_fired"] - df["hit_count"]).clip(lower=0)

    cat_defaults: dict[str, str] = {
        "pistol_grip_type": "unknown",
        "stock_type": "none",
        "shooting_grip": "unknown",
        "stance": "standing",
        "experience_level": "beginner",
        "indoor_outdoor": "outdoor",
        "target_type": "static_paper",
    }
    for col, default in cat_defaults.items():
        if col in df.columns:
            df[col] = df[col].fillna(default).astype(str)

    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """전체 정제 파이프라인을 순서대로 실행한다."""
    df = normalize_column_names(df)
    df = coerce_dates(df)
    df = coerce_bool(df)
    df = coerce_numeric(df)
    df = fill_missing(df)
    return df


def get_missing_critical_cols(df: pd.DataFrame) -> list[str]:
    """분석에 필요한 핵심 컬럼 중 없는 것을 반환한다."""
    critical = ["rounds_fired", "hit_count", "accuracy_pct"]
    return [c for c in critical if c not in df.columns]
