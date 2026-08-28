```python
import streamlit as st
import pandas as pd
from datetime import timedelta

# =========================================================
# 기본 설정
# =========================================================
st.set_page_config(
    page_title="서울 기온 랭킹",
    page_icon="🌡️",
    layout="centered"
)

# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>
    .stApp {
        background:
            radial-gradient(circle at 10% 0%, rgba(255, 180, 80, 0.13), transparent 30%),
            radial-gradient(circle at 90% 10%, rgba(80, 150, 255, 0.13), transparent 30%),
            #f7f8fc;
    }

    .main-title {
        font-size: 42px;
        font-weight: 800;
        letter-spacing: -2px;
        margin-bottom: 5px;
        color: #171923;
    }

    .subtitle {
        font-size: 16px;
        color: #6b7280;
        margin-bottom: 28px;
    }

    .hero {
        background: rgba(255,255,255,0.86);
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 24px;
        padding: 28px 24px;
        box-shadow: 0 12px 35px rgba(20,30,60,0.07);
        margin: 18px 0;
    }

    .rank-label {
        color: #6b7280;
        font-size: 15px;
        font-weight: 600;
        margin-bottom: 3px;
    }

    .rank-number {
        font-size: 64px;
        line-height: 1;
        font-weight: 900;
        letter-spacing: -4px;
        color: #111827;
    }

    .rank-unit {
        font-size: 22px;
        font-weight: 700;
        color: #6b7280;
        margin-left: 5px;
    }

    .rank-desc {
        color: #4b5563;
        font-size: 15px;
        margin-top: 10px;
    }

    .metric-card {
        background: rgba(255,255,255,0.9);
        border-radius: 18px;
        padding: 18px;
        border: 1px solid rgba(0,0,0,0.06);
        box-shadow: 0 6px 20px rgba(20,30,60,0.05);
        min-height: 110px;
    }

    .metric-title {
        color: #6b7280;
        font-size: 13px;
        font-weight: 600;
    }

    .metric-value {
        color: #111827;
        font-size: 27px;
        font-weight: 800;
        margin-top: 5px;
    }

    .metric-sub {
        color: #9ca3af;
        font-size: 12px;
        margin-top: 3px;
    }

    .hot {
        color: #e85d04;
    }

    .cold {
        color: #2563eb;
    }

    .normal {
        color: #111827;
    }

    .info-box {
        background: rgba(255,255,255,0.75);
        border-radius: 16px;
        padding: 17px 19px;
        border: 1px solid rgba(0,0,0,0.05);
        color: #4b5563;
        font-size: 13px;
        line-height: 1.7;
        margin-top: 18px;
    }

    div[data-testid="stDateInput"] label {
        font-weight: 700;
    }

    footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# 데이터 불러오기
# 반드시 seoul.csv 사용
# =========================================================
@st.cache_data
def load_data():
    df = pd.read_csv("seoul.csv")

    # 날짜 앞쪽에 들어있는 탭/공백 제거
    df["날짜"] = (
        df["날짜"]
        .astype(str)
        .str.strip()
    )

    df["날짜"] = pd.to_datetime(
        df["날짜"],
        errors="coerce"
    )

    df["평균기온"] = pd.to_numeric(
        df["평균기온"],
        errors="coerce"
    )

    df["최저기온"] = pd.to_numeric(
        df["최저기온"],
        errors="coerce"
    )

    df["최고기온"] = pd.to_numeric(
        df["최고기온"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["날짜", "평균기온"]
    )

    df = df.sort_values("날짜").reset_index(drop=True)

    return df


df = load_data()


# =========================================================
# 역사적 기간 계산
# 선택한 날짜 구간과 동일한 길이의 모든 기간을 비교
# =========================================================
@st.cache_data
def calculate_periods(data, days):
    temp = data[["날짜", "평균기온"]].copy()

    # 날짜를 인덱스로 설정
    temp = temp.set_index("날짜")

    # 일별 데이터가 존재하는 날짜만 사용
    daily = temp["평균기온"].sort_index()

    periods = []

    dates = daily.index

    if len(dates) < days:
        return pd.DataFrame()

    # 가능한 모든 시작일 탐색
    for i in range(len(dates) - days + 1):
        window_dates = dates[i:i + days]

        # 정확히 연속된 날짜인지 확인
        if (
            window_dates[-1] - window_dates[0]
            != timedelta(days=days - 1)
        ):
            continue

        values = daily.loc[window_dates]

        # 결측치가 있는 기간은 제외
        if values.isna().any():
            continue

        periods.append({
            "start": window_dates[0],
            "end": window_dates[-1],
            "avg": values.mean(),
            "min": values.min(),
            "max": values.max()
        })

    result = pd.DataFrame(periods)

    if not result.empty:
        result = result.sort_values(
            "avg",
            ascending=False
        ).reset_index(drop=True)

        result["rank_hot"] = result.index + 1

        result = result.sort_values(
            "avg",
            ascending=True
        ).reset_index(drop=True)

        result["rank_cold"] = result.index + 1

    return result


# =========================================================
# 제목
# =========================================================
st.markdown(
    '<div class="main-title">🌡️ 서울 기온 랭킹</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    '원하는 기간을 선택하면 서울의 역대 기온과 비교해 봅니다.'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# 날짜 선택
# =========================================================
min_date = df["날짜"].min().date()
max_date = df["날짜"].max().date()

col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input(
        "📅 시작 날짜",
        value=max_date - timedelta(days=6),
        min_value=min_date,
        max_value=max_date,
        format="YYYY-MM-DD"
    )

with col2:
    end_date = st.date_input(
        "📅 종료 날짜",
        value=max_date,
        min_value=min_date,
        max_value=max_date,
        format="YYYY-MM-DD"
    )


# =========================================================
# 날짜 오류 체크
# =========================================================
if start_date > end_date:
    st.error("시작 날짜가 종료 날짜보다 늦을 수 없습니다.")
    st.stop()


# =========================================================
# 선택 기간 데이터
# =========================================================
selected_start = pd.Timestamp(start_date)
selected_end = pd.Timestamp(end_date)

selected = df[
    (df["날짜"] >= selected_start) &
    (df["날짜"] <= selected_end)
].copy()

expected_days = (end_date - start_date).days + 1

# 데이터가 빠진 날이 있는 경우
actual_days = len(selected)

if actual_days == 0:
    st.warning("선택한 기간에 기온 데이터가 없습니다.")
    st.stop()

if actual_days < expected_days:
    st.warning(
        f"선택한 기간은 {expected_days}일이지만 "
        f"기온 데이터가 {actual_days}일만 존재합니다. "
        "완전한 기간끼리 비교하기 위해 랭킹 계산에서 제외합니다."
    )
    st.stop()


# =========================================================
# 선택 기간 통계
# =========================================================
selected_avg = selected["평균기온"].mean()
selected_min = selected["최저기온"].min()
selected_max = selected["최고기온"].max()

period_days = expected_days


# =========================================================
# 전체 역사 기간 계산
# =========================================================
with st.spinner("서울의 역대 기온을 비교하고 있습니다..."):
    historical = calculate_periods(
        df,
        period_days
    )


if historical.empty:
    st.error("비교할 수 있는 역사적 기간이 충분하지 않습니다.")
    st.stop()


# =========================================================
# 선택 기간과 같은 날짜 구간을 역사 데이터에서 찾기
# =========================================================
matching = historical[
    (historical["start"] == selected_start) &
    (historical["end"] == selected_end)
]

# 선택 기간 자체가 역사 데이터에 포함되어 있으면
# 해당 평균기온으로 정확하게 순위 계산
if not matching.empty:
    hot_rank = int(
        (historical["avg"] > selected_avg).sum()
    ) + 1

    cold_rank = int(
        (historical["avg"] < selected_avg).sum()
    ) + 1
else:
    hot_rank = int(
        (historical["avg"] > selected_avg).sum()
    ) + 1

    cold_rank = int(
        (historical["avg"] < selected_avg).sum()
    ) + 1


total_periods = len(historical)


# =========================================================
# 백분위
# =========================================================
hot_percentile = (
    (total_periods - hot_rank + 1)
    / total_periods
) * 100


# =========================================================
# 결과 문구
# =========================================================
if hot_rank <= max(10, int(total_periods * 0.01)):
    rank_class = "hot"
    emoji = "🔥"
    rank_message = "역대급으로 더운 기간입니다."
elif hot_rank <= int(total_periods * 0.25):
    rank_class = "hot"
    emoji = "☀️"
    rank_message = "평년보다 꽤 따뜻한 기간입니다."
elif hot_rank >= int(total_periods * 0.75):
    rank_class = "cold"
    emoji = "🧊"
    rank_message = "상대적으로 서늘한 기간입니다."
else:
    rank_class = "normal"
    emoji = "🌤️"
    rank_message = "역사적으로 중간 정도의 기온입니다."


# =========================================================
# 메인 랭킹 카드
# =========================================================
st.markdown(
    f"""
    <div class="hero">
        <div class="rank-label">
            {emoji} 선택한 {period_days}일의 역대 기온 순위
        </div>

        <div>
            <span class="rank-number {rank_class}">
                {hot_rank}
            </span>
            <span class="rank-unit">위</span>
        </div>

        <div class="rank-desc">
            전체 {total_periods:,}개의 역사적 {period_days}일 기간과 비교한 결과입니다.<br>
            <b>{rank_message}</b>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 핵심 수치
# =========================================================
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">평균기온</div>
            <div class="metric-value">{selected_avg:.1f}℃</div>
            <div class="metric-sub">선택 기간 평균</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">최고기온</div>
            <div class="metric-value">{selected_max:.1f}℃</div>
            <div class="metric-sub">기간 중 최고</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">최저기온</div>
            <div class="metric-value">{selected_min:.1f}℃</div>
            <div class="metric-sub">기간 중 최저</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# 선택 기간
# =========================================================
st.markdown(
    f"""
    <div class="info-box">
        📍 <b>선택 기간</b>　
        {start_date.strftime("%Y년 %m월 %d일")}
        ~
        {end_date.strftime("%Y년 %m월 %d일")}
        <br>
        📊 이 기간의 평균기온은 <b>{selected_avg:.1f}℃</b>입니다.
        역대 같은 길이의 기간 중
        <b>{hot_rank:,}위</b>에 해당합니다.
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 역사적 TOP 10
# =========================================================
st.markdown("### 🏆 가장 더웠던 기간 TOP 10")

top10 = historical.nlargest(10, "avg").copy()

display_top10 = pd.DataFrame({
    "순위": range(1, len(top10) + 1),
    "기간": (
        top10["start"].dt.strftime("%Y-%m-%d")
        + " ~ "
        + top10["end"].dt.strftime("%Y-%m-%d")
    ),
    "평균기온": top10["avg"].round(1).astype(str) + "℃"
})

st.dataframe(
    display_top10,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# 선택 기간의 일별 데이터
# =========================================================
with st.expander("📈 선택 기간의 일별 기온 보기"):
    chart_data = selected[
        ["날짜", "평균기온", "최저기온", "최고기온"]
    ].copy()

    chart_data = chart_data.set_index("날짜")

    st.line_chart(
        chart_data,
        use_container_width=True
    )


# =========================================================
# 데이터 정보
# =========================================================
with st.expander("ℹ️ 데이터 정보"):
    st.write(
        f"""
        - 데이터 기간: **{df["날짜"].min().strftime("%Y-%m-%d")} ~ {df["날짜"].max().strftime("%Y-%m-%d")}**
        - 총 관측일: **{len(df):,}일**
        - 비교 방식: **선택한 기간과 동일한 길이의 연속 기간**
        - 랭킹 기준: **기간 평균기온**
        - 데이터 파일: **seoul.csv**
        """
    )

st.caption(
    "※ 기상 관측 데이터의 결측일은 비교에서 제외됩니다."
)
```
