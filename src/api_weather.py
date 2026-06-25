"""Open-Meteo API 연동 모듈 - Geocoding + Historical Weather"""
from __future__ import annotations

from typing import Optional
import numpy as np
import pandas as pd
import requests
import streamlit as st

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
HISTORICAL_URL = "https://archive-api.open-meteo.com/v1/archive"
TIMEOUT_SEC = 10

WEATHER_VARIABLES = [
    "temperature_2m_mean",
    "relative_humidity_2m_mean",
    "wind_speed_10m_mean",
    "precipitation_sum",
]


@st.cache_data(ttl=3600)
def geocode_location(location_name: str) -> Optional[tuple[float, float]]:
    """위치명으로 위도/경도를 조회한다."""
    try:
        resp = requests.get(
            GEOCODING_URL,
            params={"name": location_name, "count": 1, "language": "ko"},
            timeout=TIMEOUT_SEC,
        )
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results")
        if not results:
            return None
        return results[0]["latitude"], results[0]["longitude"]
    except Exception:
        return None


@st.cache_data(ttl=3600)
def fetch_historical_weather(
    lat: float,
    lon: float,
    start_date: str,
    end_date: str,
) -> Optional[pd.DataFrame]:
    """Open-Meteo Historical Weather API에서 일별 날씨를 가져온다.

    Returns a DataFrame with columns: date, temperature_2m, relative_humidity_2m,
    wind_speed_10m, precipitation — or None on failure.
    """
    try:
        resp = requests.get(
            HISTORICAL_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "start_date": start_date,
                "end_date": end_date,
                "daily": ",".join(WEATHER_VARIABLES),
                "timezone": "Asia/Seoul",
            },
            timeout=TIMEOUT_SEC,
        )
        resp.raise_for_status()
        data = resp.json()

        daily = data.get("daily")
        if not daily:
            return None

        df = pd.DataFrame(
            {
                "date": pd.to_datetime(daily.get("time", [])),
                "temperature_2m": daily.get("temperature_2m_mean", []),
                "relative_humidity_2m": daily.get("relative_humidity_2m_mean", []),
                "wind_speed_10m": daily.get("wind_speed_10m_mean", []),
                "precipitation": daily.get("precipitation_sum", []),
            }
        )
        df["date"] = df["date"].dt.date
        return df
    except Exception:
        return None


def enrich_with_weather(df: pd.DataFrame) -> tuple[pd.DataFrame, bool]:
    """데이터프레임의 위치/날짜 기준으로 날씨 컬럼을 채운다.

    Returns:
        enriched_df: 날씨가 채워진 데이터프레임
        api_success: API 연동 성공 여부
    """
    weather_cols = ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "precipitation"]

    # 이미 날씨 컬럼이 있으면 패스
    has_weather = all(c in df.columns for c in weather_cols)
    if has_weather and df[weather_cols].notna().all().all():
        return df, True

    try:
        if "date" not in df.columns or "latitude" not in df.columns:
            return df, False

        dates = pd.to_datetime(df["date"])
        start_date = dates.min().strftime("%Y-%m-%d")
        end_date = dates.max().strftime("%Y-%m-%d")

        lat = float(df["latitude"].median())
        lon = float(df["longitude"].median())

        # API 호출 (최대 1년 범위)
        weather_df = fetch_historical_weather(lat, lon, start_date, end_date)

        if weather_df is None or weather_df.empty:
            return df, False

        df = df.copy()
        df["_date_key"] = pd.to_datetime(df["date"]).dt.date
        weather_df = weather_df.rename(columns={"date": "_date_key"})

        merged = df.merge(weather_df, on="_date_key", how="left", suffixes=("", "_api"))
        df = df.drop(columns=["_date_key"])

        for col in weather_cols:
            api_col = f"{col}_api"
            if api_col in merged.columns:
                if col not in merged.columns:
                    merged[col] = merged[api_col]
                else:
                    merged[col] = merged[col].fillna(merged[api_col])
                merged = merged.drop(columns=[api_col])

        merged = merged.drop(columns=["_date_key"], errors="ignore")
        return merged, True

    except Exception:
        return df, False


def make_dummy_weather(n: int, indoor_mask: pd.Series, seed: int = 99) -> pd.DataFrame:
    """API 실패 시 사용할 더미 날씨 데이터프레임 반환."""
    rng = np.random.default_rng(seed)
    temps = rng.uniform(5, 35, n)
    humidity = rng.uniform(30, 90, n)
    wind = np.where(indoor_mask, rng.uniform(0, 0.5, n), rng.uniform(0, 12, n))
    precip = np.where(
        indoor_mask,
        0.0,
        rng.uniform(0, 5, n) * rng.choice([0, 1], n, p=[0.8, 0.2]),
    )
    return pd.DataFrame(
        {
            "temperature_2m": np.round(temps, 1),
            "relative_humidity_2m": np.round(humidity, 1),
            "wind_speed_10m": np.round(wind, 2),
            "precipitation": np.round(precip, 2),
        }
    )
