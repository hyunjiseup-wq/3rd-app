"""더미 데이터 생성 모듈 - 에어소프트 플레이어 성능 데이터"""
from __future__ import annotations

import numpy as np
import pandas as pd


LOCATIONS = [
    {"name": "Seoul Indoor Range", "lat": 37.5665, "lon": 126.9780, "type": "indoor"},
    {"name": "Incheon Field", "lat": 37.4563, "lon": 126.7052, "type": "outdoor"},
    {"name": "Suwon CQB Arena", "lat": 37.2636, "lon": 127.0286, "type": "indoor"},
    {"name": "Busan Forest Field", "lat": 35.1796, "lon": 129.0756, "type": "outdoor"},
    {"name": "Daejeon Tactical", "lat": 36.3504, "lon": 127.3845, "type": "indoor"},
    {"name": "Gwangju Outdoor", "lat": 35.1595, "lon": 126.8526, "type": "outdoor"},
]

EXPERIENCE_LEVELS = ["beginner", "intermediate", "advanced"]
PISTOL_GRIP_TYPES = ["standard", "ergonomic", "vertical_angle", "unknown"]
STOCK_TYPES = ["fixed", "adjustable", "folding", "none"]
SHOOTING_GRIPS = ["c-clamp", "magwell", "traditional", "thumb-over-bore", "unknown"]
STANCES = ["standing", "kneeling", "prone", "barricade"]
TARGET_TYPES = ["static_paper", "reactive_steel", "moving_target", "multi_zone"]


def generate_dummy_data(n_rows: int = 350, seed: int = 42) -> pd.DataFrame:
    """약한 상관관계를 포함한 에어소프트 성능 더미 데이터 생성."""
    rng = np.random.default_rng(seed)

    # 기본 속성
    n = n_rows
    session_ids = [f"S{str(i+1).zfill(4)}" for i in range(n)]
    player_ids = [f"P{str(rng.integers(1, 51)).zfill(3)}" for _ in range(n)]

    dates = pd.to_datetime(
        rng.integers(
            pd.Timestamp("2024-01-01").value,
            pd.Timestamp("2025-12-31").value,
            n,
        )
    )

    # 위치
    loc_idx = rng.integers(0, len(LOCATIONS), n)
    location_names = [LOCATIONS[i]["name"] for i in loc_idx]
    latitudes = [LOCATIONS[i]["lat"] + rng.uniform(-0.05, 0.05) for i in loc_idx]
    longitudes = [LOCATIONS[i]["lon"] + rng.uniform(-0.05, 0.05) for i in loc_idx]
    indoor_outdoor = [LOCATIONS[i]["type"] for i in loc_idx]

    # 장비
    front_grip_used = rng.choice([True, False], n, p=[0.6, 0.4])
    pistol_grip_types = rng.choice(PISTOL_GRIP_TYPES, n, p=[0.4, 0.3, 0.2, 0.1])
    stock_used = rng.choice([True, False], n, p=[0.7, 0.3])
    stock_types = np.where(
        stock_used,
        rng.choice(["fixed", "adjustable", "folding"], n, p=[0.3, 0.5, 0.2]),
        "none",
    )

    # 사격 스타일
    shooting_grips = rng.choice(SHOOTING_GRIPS, n, p=[0.25, 0.15, 0.35, 0.15, 0.10])
    stances = rng.choice(STANCES, n, p=[0.4, 0.3, 0.2, 0.1])
    experience_levels = rng.choice(EXPERIENCE_LEVELS, n, p=[0.3, 0.45, 0.25])

    # 환경
    distances = rng.uniform(5, 50, n)
    target_types = rng.choice(TARGET_TYPES, n)
    equipment_weights = rng.uniform(2500, 5500, n)

    # 날씨 (더미; 실제 API 연동 전)
    temperatures = rng.uniform(5, 35, n)
    humidities = rng.uniform(30, 90, n)
    wind_speeds = np.where(
        np.array(indoor_outdoor) == "indoor",
        rng.uniform(0, 0.5, n),
        rng.uniform(0, 12, n),
    )
    precipitations = np.where(
        np.array(indoor_outdoor) == "indoor",
        0.0,
        rng.uniform(0, 5, n) * rng.choice([0, 1], n, p=[0.8, 0.2]),
    )

    # 숙련도 기반 기본 정확도
    exp_bonus = np.where(
        np.array(experience_levels) == "advanced",
        rng.uniform(10, 18, n),
        np.where(
            np.array(experience_levels) == "intermediate",
            rng.uniform(3, 8, n),
            0.0,
        ),
    )

    # 거리에 따른 정확도 패널티
    dist_penalty = distances * rng.uniform(0.3, 0.7, n)

    # 야외 풍속 패널티
    wind_penalty = np.where(
        np.array(indoor_outdoor) == "outdoor",
        wind_speeds * rng.uniform(0.3, 0.8, n),
        0.0,
    )

    # 기본 정확도
    base_accuracy = rng.uniform(45, 75, n) + exp_bonus - dist_penalty * 0.5 - wind_penalty * 0.4
    base_accuracy = np.clip(base_accuracy, 20, 98)

    # 발사 수
    rounds_fired = rng.integers(15, 60, n)
    hit_counts = np.round(rounds_fired * base_accuracy / 100).astype(int)
    hit_counts = np.clip(hit_counts, 0, rounds_fired)
    miss_counts = rounds_fired - hit_counts
    accuracy_pct = hit_counts / rounds_fired * 100

    # 시간 관련
    base_split = rng.uniform(0.3, 1.2, n)
    # front_grip → split_time 소폭 감소
    split_bonus = np.where(front_grip_used, rng.uniform(0.03, 0.10, n), 0.0)
    split_time_sec = np.clip(base_split - split_bonus, 0.1, 2.0)

    total_time_sec = split_time_sec * rounds_fired + rng.uniform(0.5, 3.0, n)
    shots_per_sec = rounds_fired / total_time_sec

    reaction_time_sec = rng.uniform(0.15, 0.6, n) - np.where(
        np.array(experience_levels) == "advanced", rng.uniform(0.05, 0.15, n), 0.0
    )
    reaction_time_sec = np.clip(reaction_time_sec, 0.1, 1.0)

    # stock_used → group size 소폭 감소
    base_group = rng.uniform(3, 20, n) + distances * rng.uniform(0.05, 0.15, n)
    stock_bonus = np.where(stock_used, rng.uniform(0.5, 2.5, n), 0.0)
    avg_group_size_cm = np.clip(base_group - stock_bonus, 1.0, 35.0)

    df = pd.DataFrame(
        {
            "session_id": session_ids,
            "player_id": player_ids,
            "date": dates.date,
            "location_name": location_names,
            "latitude": np.round(latitudes, 4),
            "longitude": np.round(longitudes, 4),
            "front_grip_used": front_grip_used,
            "pistol_grip_type": pistol_grip_types,
            "stock_used": stock_used,
            "stock_type": stock_types,
            "shooting_grip": shooting_grips,
            "stance": stances,
            "distance_m": np.round(distances, 1),
            "target_type": target_types,
            "rounds_fired": rounds_fired,
            "hit_count": hit_counts,
            "miss_count": miss_counts,
            "accuracy_pct": np.round(accuracy_pct, 2),
            "split_time_sec": np.round(split_time_sec, 3),
            "shots_per_sec": np.round(shots_per_sec, 3),
            "reaction_time_sec": np.round(reaction_time_sec, 3),
            "avg_group_size_cm": np.round(avg_group_size_cm, 2),
            "equipment_weight_g": np.round(equipment_weights, 0),
            "experience_level": experience_levels,
            "indoor_outdoor": indoor_outdoor,
            "temperature_2m": np.round(temperatures, 1),
            "relative_humidity_2m": np.round(humidities, 1),
            "wind_speed_10m": np.round(wind_speeds, 2),
            "precipitation": np.round(precipitations, 2),
        }
    )

    return df
