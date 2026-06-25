# 에어소프트 성능 대시보드

에어소프트 플레이어의 **전방 손잡이·개머리판 사용 여부** 및 **사격 그립**에 따른
사격 속도·정확도·성능 변화를 탐색하는 Streamlit 대시보드입니다.

> **이 저장소에는 민감한 원본 데이터 파일을 포함하지 않습니다.**
> 앱은 업로드된 엑셀 파일이 없을 경우 자동으로 더미 데이터를 생성하여 실행됩니다.

---

## 대시보드가 보여주는 것

| 섹션 | 내용 |
|------|------|
| 데이터 상태 | 업로드/더미 구분, 행·컬럼 수, API 연결 상태 |
| KPI 카드 | 평균 정확도, shots/sec, split time, 탄착군, 세션·플레이어 수 |
| 장비 비교 | front_grip / stock 사용 여부별 정확도·속도 |
| 그립 비교 | shooting_grip 유형별 accuracy, split time, shots/sec |
| 환경 영향 | 풍속×정확도, 기온×속도, 거리×정확도 산점도 |
| 데이터 미리보기 | 필터 적용 데이터, CSV 다운로드 |

---

## 데이터 컬럼 설명

| 컬럼 | 설명 |
|------|------|
| `session_id` | 세션 고유 ID |
| `player_id` | 플레이어 고유 ID |
| `date` | 게임 날짜 |
| `location_name` | 장소명 |
| `latitude` / `longitude` | 위도 / 경도 |
| `front_grip_used` | 전방손잡이(포어그립) 사용 여부 (True/False) |
| `pistol_grip_type` | 권총손잡이 유형 (standard/ergonomic/vertical_angle/unknown) |
| `stock_used` | 개머리판(스톡) 사용 여부 (True/False) |
| `stock_type` | 개머리판 유형 (fixed/adjustable/folding/none) |
| `shooting_grip` | 사격 그립 자세 (c-clamp/magwell/traditional/thumb-over-bore/unknown) |
| `stance` | 사격 자세 (standing/kneeling/prone/barricade) |
| `distance_m` | 사격 거리 (m) |
| `rounds_fired` | 총 발사 수 |
| `hit_count` | 명중 수 |
| `accuracy_pct` | 명중률 (%) = hit_count / rounds_fired × 100 |
| `split_time_sec` | 연속 사격 간격 (초) |
| `shots_per_sec` | 초당 사격 수 |
| `avg_group_size_cm` | 평균 탄착군 크기 (cm) |
| `experience_level` | 숙련도 (beginner/intermediate/advanced) |
| `indoor_outdoor` | 실내/실외 |
| `temperature_2m` | 기온 °C (Open-Meteo API) |
| `relative_humidity_2m` | 상대습도 % |
| `wind_speed_10m` | 풍속 m/s |
| `precipitation` | 강수량 mm |

---

## 더미 데이터 사용 방식

엑셀 파일 업로드 없이 앱을 실행하면 `src/dummy_data.py`의 `generate_dummy_data()` 함수가
**350행의 예시 데이터**를 자동 생성합니다.

더미 데이터에는 다음과 같은 약한 경향성이 포함되어 있습니다.

- 숙련도(experience_level)가 높을수록 평균 정확도 소폭 증가
- 풍속(wind_speed_10m)이 높을수록 실외 정확도 소폭 감소
- `front_grip_used=True`이면 split_time_sec 소폭 감소
- `stock_used=True`이면 avg_group_size_cm 소폭 감소
- `distance_m`이 길수록 accuracy_pct 감소

> **주의:** 더미 데이터는 실제 성능 검증 데이터가 아닙니다.
> 시각화 목적으로 생성된 예시이며 과학적 결론으로 해석하지 마세요.

---

## 외부 API: Open-Meteo

API key 없이 무료로 사용할 수 있는 [Open-Meteo](https://open-meteo.com/) 를 사용합니다.

- **Geocoding API** — 위치명 → 위도/경도 변환
- **Historical Weather API** — 날짜·위치 기준 과거 날씨 데이터 조회
  - 조회 항목: 기온, 상대습도, 풍속, 강수량
- `@st.cache_data(ttl=3600)` 캐싱 적용 (1시간)
- API 실패 시 앱이 종료되지 않으며, 더미 날씨 값으로 대체됩니다.

---

## 로컬 실행 방법

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 앱 실행
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 이 자동으로 열립니다.
엑셀 파일 없이 실행하면 더미 데이터로 동작합니다.

---

## GitHub 업로드 방법

### GitHub CLI 사용 (권장)

```bash
# GitHub CLI 로그인 (최초 1회)
gh auth login

# 로컬 git 초기화
git init
git add .
git commit -m "Initial Streamlit airsoft performance dashboard"

# GitHub 새 저장소 생성 및 push
gh repo create airsoft-performance-dashboard --public --source=. --remote=origin --push
```

### GitHub CLI 없이 (대체 방법)

```bash
git init
git add .
git commit -m "Initial Streamlit airsoft performance dashboard"

git remote add origin https://github.com/YOUR_USERNAME/airsoft-performance-dashboard.git
git branch -M main
git push -u origin main
```

> `YOUR_USERNAME` 부분을 본인의 GitHub 사용자명으로 바꾸세요.

---

## Streamlit Cloud 배포 방법

1. [Streamlit Cloud](https://streamlit.io/cloud) 접속
2. GitHub 계정 연결
3. `airsoft-performance-dashboard` 저장소 선택
4. Branch: `main`
5. Main file path: `app.py`
6. **Deploy** 클릭
7. 배포 URL 확인 (예: `https://your-app.streamlit.app`)
8. 앱 실행 후 더미 데이터 안내 메시지가 뜨는지 확인
9. 엑셀 업로드 테스트
10. 외부 API 실패 시에도 앱이 죽지 않는지 확인

---

## 배포 체크리스트

배포 후 앱이 데이터를 못 찾는 경우:

1. 원본 데이터 파일을 저장소에 올릴 계획인지 확인
2. 민감 데이터라면 올리지 말고 앱의 업로드 기능 또는 더미 데이터 자동 생성 기능 사용
3. `data/` 폴더에는 `.gitkeep`만 커밋되어 있는지 확인
4. `requirements.txt`가 루트에 있는지 확인
5. `app.py` 경로가 Streamlit Cloud 설정과 일치하는지 확인

---

## 민감 데이터 주의사항

- `data/` 폴더의 `.xlsx`, `.xls`, `.csv`, `.parquet`, `.db`, `.sqlite` 파일은 `.gitignore`에 포함되어 있습니다.
- `.streamlit/secrets.toml` 도 `.gitignore`에 포함됩니다.
- 원본 성능 데이터는 저장소에 커밋하지 마세요.
- 배포 환경에서는 앱의 파일 업로드 기능을 사용하거나 더미 데이터로 동작합니다.

---

## 프로젝트 구조

```
airsoft-performance-dashboard/
├─ app.py                  # 메인 Streamlit 앱
├─ README.md
├─ requirements.txt
├─ .gitignore
├─ .streamlit/
│  └─ config.toml          # 테마 설정
├─ src/
│  ├─ __init__.py
│  ├─ data_loader.py       # 엑셀 로딩 및 병합
│  ├─ data_cleaning.py     # 컬럼 정규화 및 정제
│  ├─ dummy_data.py        # 더미 데이터 생성
│  ├─ api_weather.py       # Open-Meteo API 연동
│  └─ charts.py            # Plotly 차트 함수
└─ data/
   └─ .gitkeep             # data 폴더 유지용 빈 파일
```
