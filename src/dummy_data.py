"""더미 데이터 생성 모듈 - 에어소프트 플레이어 성능 데이터 (가상/더미 전용)

주의: 이 데이터는 에어소프트 스포츠 시각화 목적의 더미 데이터입니다.
실제 화기 개조·위력 증가·불법 무기 제작과 무관하며, 실제 성능 검증 결과가 아닙니다.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


# 컬럼명 영문 유지 (app.py 전체에서 참조), 표시값만 한글
LOCATIONS = [
    {"name": "서울 실내 레인지", "lat": 37.5665, "lon": 126.9780, "type": "실내"},
    {"name": "인천 야외 필드",   "lat": 37.4563, "lon": 126.7052, "type": "실외"},
    {"name": "수원 CQB 아레나", "lat": 37.2636, "lon": 127.0286, "type": "실내"},
    {"name": "부산 포레스트 필드", "lat": 35.1796, "lon": 129.0756, "type": "실외"},
    {"name": "대전 택티컬 존",   "lat": 36.3504, "lon": 127.3845, "type": "실내"},
    {"name": "광주 야외 필드",   "lat": 35.1595, "lon": 126.8526, "type": "실외"},
]

EXPERIENCE_LEVELS  = ["초보", "중급", "고급"]
PISTOL_GRIP_TYPES  = ["표준형", "인체공학형", "수직각도형", "기타"]
STOCK_TYPES_LIST   = ["고정형", "조절형", "접이식"]
SHOOTING_GRIPS     = ["C-클램프", "매그웰", "전통형", "썸오버보어", "기타"]
STANCES            = ["서서쏴", "무릎쏴", "엎드려쏴", "엄폐물활용"]
TARGET_TYPES       = ["고정표적", "반응표적(철판)", "이동표적", "다중구역"]
OPTICS_TYPES       = ["단렌즈 스코프", "복합 조준경", "홀로사이트", "도트사이트"]


def generate_dummy_data(n_rows: int = 350, seed: int = 42) -> pd.DataFrame:
    """약한 상관관계를 포함한 에어소프트 성능 더미 데이터 생성.

    파츠 교환 효과는 더미 데이터 생성을 위한 약한 가정이며,
    실제 장비 개조나 성능 향상을 보장하지 않습니다.
    """
    rng = np.random.default_rng(seed)
    n = n_rows

    # ── 기본 식별자 ───────────────────────────────────
    session_ids = [f"S{str(i+1).zfill(4)}" for i in range(n)]
    player_ids  = [f"P{str(rng.integers(1, 51)).zfill(3)}" for _ in range(n)]

    dates = pd.to_datetime(
        rng.integers(
            pd.Timestamp("2024-01-01").value,
            pd.Timestamp("2025-12-31").value,
            n,
        )
    )

    # ── 위치 ─────────────────────────────────────────
    loc_idx       = rng.integers(0, len(LOCATIONS), n)
    location_names = [LOCATIONS[i]["name"] for i in loc_idx]
    latitudes      = [LOCATIONS[i]["lat"] + rng.uniform(-0.05, 0.05) for i in loc_idx]
    longitudes     = [LOCATIONS[i]["lon"] + rng.uniform(-0.05, 0.05) for i in loc_idx]
    indoor_outdoor = [LOCATIONS[i]["type"] for i in loc_idx]   # "실내" / "실외"

    # ── 일반 장비 ─────────────────────────────────────
    front_grip_used   = rng.choice([True, False], n, p=[0.6, 0.4])
    pistol_grip_types = rng.choice(PISTOL_GRIP_TYPES, n, p=[0.4, 0.3, 0.2, 0.1])
    stock_used        = rng.choice([True, False], n, p=[0.7, 0.3])
    stock_types       = np.where(
        stock_used,
        rng.choice(STOCK_TYPES_LIST, n, p=[0.3, 0.5, 0.2]),
        "없음",
    )

    # ── 조준경 ───────────────────────────────────────
    optics_used  = rng.choice([True, False], n, p=[0.55, 0.45])
    optics_types = np.where(
        optics_used,
        rng.choice(OPTICS_TYPES, n, p=[0.20, 0.15, 0.35, 0.30]),
        "맨눈",
    )

    # ── 장비 파츠 교환 (더미 데이터 가상 분포) ──────────
    barrel_replaced  = rng.choice([True, False], n, p=[0.30, 0.70])
    hopup_replaced   = rng.choice([True, False], n, p=[0.30, 0.70])
    motor_replaced   = rng.choice([True, False], n, p=[0.20, 0.80])
    spring_replaced  = rng.choice([True, False], n, p=[0.15, 0.85])
    gearbox_replaced = rng.choice([True, False], n, p=[0.15, 0.85])
    battery_changed  = rng.choice([True, False], n, p=[0.35, 0.65])
    magazine_changed = rng.choice([True, False], n, p=[0.35, 0.65])

    parts_replaced_count = (
        barrel_replaced.astype(int)
        + hopup_replaced.astype(int)
        + motor_replaced.astype(int)
        + spring_replaced.astype(int)
        + gearbox_replaced.astype(int)
        + battery_changed.astype(int)
        + magazine_changed.astype(int)
    )
    part_replaced_any = parts_replaced_count > 0
    part_setup_type   = np.where(
        parts_replaced_count == 0, "순정",
        np.where(parts_replaced_count <= 2, "일부 교환", "다수 교환"),
    )

    # ── 사격 스타일 ───────────────────────────────────
    shooting_grips  = rng.choice(SHOOTING_GRIPS, n, p=[0.25, 0.15, 0.35, 0.15, 0.10])
    stances         = rng.choice(STANCES, n, p=[0.4, 0.3, 0.2, 0.1])
    experience_levels = rng.choice(EXPERIENCE_LEVELS, n, p=[0.3, 0.45, 0.25])

    # ── 환경 ─────────────────────────────────────────
    distances         = rng.uniform(5, 50, n)
    target_types      = rng.choice(TARGET_TYPES, n)
    temperatures      = rng.uniform(5, 35, n)
    humidities        = rng.uniform(30, 90, n)
    wind_speeds       = np.where(
        np.array(indoor_outdoor) == "실내",
        rng.uniform(0, 0.5, n),
        rng.uniform(0, 12, n),
    )
    precipitations    = np.where(
        np.array(indoor_outdoor) == "실내",
        0.0,
        rng.uniform(0, 5, n) * rng.choice([0, 1], n, p=[0.8, 0.2]),
    )

    # ── 정확도 보정 인자 ──────────────────────────────
    exp_bonus = np.where(
        np.array(experience_levels) == "고급",
        rng.uniform(10, 18, n),
        np.where(np.array(experience_levels) == "중급", rng.uniform(3, 8, n), 0.0),
    )
    dist_penalty  = distances * rng.uniform(0.3, 0.7, n)
    wind_penalty  = np.where(
        np.array(indoor_outdoor) == "실외",
        wind_speeds * rng.uniform(0.3, 0.8, n),
        0.0,
    )
    optics_bonus  = np.where(
        optics_used, rng.uniform(2, 8, n) * (distances / 50.0), 0.0
    )
    # 파츠 교환 → 정확도 아주 소폭 보정 (더미 가정, 실제 검증 아님)
    parts_acc_bonus = np.clip(
        np.where(hopup_replaced, rng.uniform(0, 2.0, n), 0.0)
        + np.where(part_replaced_any, rng.uniform(0, 1.5, n), 0.0),
        0, 3.0,
    )

    base_accuracy = np.clip(
        rng.uniform(45, 75, n)
        + exp_bonus
        - dist_penalty * 0.5
        - wind_penalty * 0.4
        + optics_bonus
        + parts_acc_bonus,
        20, 98,
    )

    rounds_fired = rng.integers(15, 60, n)
    hit_counts   = np.clip(np.round(rounds_fired * base_accuracy / 100).astype(int), 0, rounds_fired)
    miss_counts  = rounds_fired - hit_counts
    accuracy_pct = hit_counts / rounds_fired * 100

    # ── 시간 지표 ─────────────────────────────────────
    split_bonus   = np.where(front_grip_used, rng.uniform(0.03, 0.10, n), 0.0)
    split_time_sec = np.clip(rng.uniform(0.3, 1.2, n) - split_bonus, 0.1, 2.0)

    total_time_sec = split_time_sec * rounds_fired + rng.uniform(0.5, 3.0, n)
    base_shots_per_sec = rounds_fired / total_time_sec

    # 모터/배터리 교환 → 초당 발사 수 아주 소폭 보정 (더미 가정)
    parts_speed_bonus = np.clip(
        np.where(motor_replaced,  rng.uniform(0, 0.08, n), 0.0)
        + np.where(battery_changed, rng.uniform(0, 0.07, n), 0.0),
        0, 0.15,
    )
    shots_per_sec = np.clip(base_shots_per_sec + parts_speed_bonus, 0.5, 15.0)

    reaction_time_sec = np.clip(
        rng.uniform(0.15, 0.6, n) - np.where(
            np.array(experience_levels) == "고급", rng.uniform(0.05, 0.15, n), 0.0
        ),
        0.1, 1.0,
    )

    # ── 탄착군 ────────────────────────────────────────
    base_group        = rng.uniform(3, 20, n) + distances * rng.uniform(0.05, 0.15, n)
    stock_bonus       = np.where(stock_used,      rng.uniform(0.5, 2.5, n), 0.0)
    optics_grp_bonus  = np.where(optics_used,     rng.uniform(0.5, 2.0, n), 0.0)
    # 배럴 교환 → 탄착군 아주 소폭 감소 (더미 가정)
    barrel_grp_bonus  = np.clip(
        np.where(barrel_replaced, rng.uniform(0, 1.5, n), 0.0), 0, 1.5
    )
    avg_group_size_cm = np.clip(
        base_group - stock_bonus - optics_grp_bonus - barrel_grp_bonus, 1.0, 35.0
    )

    # ── 장비 무게 ─────────────────────────────────────
    # 파츠 교환/추가 시 약간 무게 증가 (더미 가정)
    parts_weight_bonus = np.clip(
        np.where(gearbox_replaced, rng.uniform(0, 150, n), 0.0)
        + parts_replaced_count * rng.uniform(0, 60, n),
        0, 300,
    )
    equipment_weights = np.clip(rng.uniform(2500, 5500, n) + parts_weight_bonus, 2500, 5800)

    # ── DataFrame 조립 ────────────────────────────────
    return pd.DataFrame(
        {
            "session_id":          session_ids,
            "player_id":           player_ids,
            "date":                dates.date,
            "location_name":       location_names,
            "latitude":            np.round(latitudes, 4),
            "longitude":           np.round(longitudes, 4),
            "front_grip_used":     front_grip_used,
            "pistol_grip_type":    pistol_grip_types,
            "stock_used":          stock_used,
            "stock_type":          stock_types,
            "optics_used":         optics_used,
            "optics_type":         optics_types,
            "part_replaced_any":   part_replaced_any,
            "barrel_replaced":     barrel_replaced,
            "hopup_replaced":      hopup_replaced,
            "motor_replaced":      motor_replaced,
            "spring_replaced":     spring_replaced,
            "gearbox_replaced":    gearbox_replaced,
            "battery_changed":     battery_changed,
            "magazine_changed":    magazine_changed,
            "parts_replaced_count": parts_replaced_count,
            "part_setup_type":     part_setup_type,
            "shooting_grip":       shooting_grips,
            "stance":              stances,
            "distance_m":          np.round(distances, 1),
            "target_type":         target_types,
            "rounds_fired":        rounds_fired,
            "hit_count":           hit_counts,
            "miss_count":          miss_counts,
            "accuracy_pct":        np.round(accuracy_pct, 2),
            "split_time_sec":      np.round(split_time_sec, 3),
            "shots_per_sec":       np.round(shots_per_sec, 3),
            "reaction_time_sec":   np.round(reaction_time_sec, 3),
            "avg_group_size_cm":   np.round(avg_group_size_cm, 2),
            "equipment_weight_g":  np.round(equipment_weights, 0),
            "experience_level":    experience_levels,
            "indoor_outdoor":      indoor_outdoor,
            "temperature_2m":      np.round(temperatures, 1),
            "relative_humidity_2m": np.round(humidities, 1),
            "wind_speed_10m":      np.round(wind_speeds, 2),
            "precipitation":       np.round(precipitations, 2),
        }
    )
