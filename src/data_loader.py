"""데이터 로딩 모듈 - 엑셀 다중 업로드 및 병합"""
from __future__ import annotations

from typing import Optional
import io
import pandas as pd
import streamlit as st

from src.data_cleaning import clean, get_missing_critical_cols
from src.dummy_data import generate_dummy_data


def read_excel_file(file_obj: "st.runtime.uploaded_file_manager.UploadedFile") -> Optional[pd.DataFrame]:
    """업로드된 엑셀 파일 하나를 DataFrame으로 읽는다."""
    try:
        df = pd.read_excel(io.BytesIO(file_obj.read()), engine="openpyxl")
        if df.empty:
            st.warning(f"'{file_obj.name}' 파일이 비어 있습니다. 건너뜁니다.")
            return None
        return df
    except Exception as e:
        st.warning(f"'{file_obj.name}' 읽기 실패: {e}")
        return None


def merge_excel_files(
    uploaded_files: list,
) -> tuple[Optional[pd.DataFrame], list[str]]:
    """여러 엑셀 파일을 읽고 병합한다.

    Returns:
        merged_df: 병합·정제된 DataFrame (실패 시 None)
        warnings: 처리 중 발생한 경고 메시지 목록
    """
    warnings: list[str] = []
    frames: list[pd.DataFrame] = []

    for f in uploaded_files:
        raw = read_excel_file(f)
        if raw is None:
            warnings.append(f"'{f.name}': 읽기 실패 또는 빈 파일")
            continue
        cleaned = clean(raw)
        missing = get_missing_critical_cols(cleaned)
        if missing:
            warnings.append(
                f"'{f.name}': 핵심 컬럼 없음 ({', '.join(missing)}) — 가능한 컬럼만 사용"
            )
        frames.append(cleaned)

    if not frames:
        return None, warnings

    try:
        merged = pd.concat(frames, ignore_index=True)
    except Exception as e:
        warnings.append(f"병합 실패: {e}")
        return None, warnings

    return merged, warnings


def load_data(
    uploaded_files: list,
) -> tuple[pd.DataFrame, bool, list[str]]:
    """메인 데이터 로딩 진입점.

    Args:
        uploaded_files: st.file_uploader 결과

    Returns:
        df: 최종 DataFrame
        is_dummy: 더미 데이터 사용 여부
        messages: 경고/안내 메시지 목록
    """
    messages: list[str] = []

    if uploaded_files:
        merged, warnings = merge_excel_files(uploaded_files)
        messages.extend(warnings)

        if merged is not None and not merged.empty:
            return merged, False, messages

        messages.append("업로드 파일 처리 실패 — 더미 데이터로 대체합니다.")

    df = generate_dummy_data()
    return df, True, messages
