import streamlit as st
import csv
from datetime import date, datetime, timedelta
from pathlib import Path
import html
import math

# =========================================================
# 기본 설정
# =========================================================

st.set_page_config(
    page_title="서울 기온 랭킹",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DATA_FILE = Path("seoul.csy")


# =========================================================
# 스타일
# =========================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont,
                     "Segoe UI", sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 10% 0%, rgba(99,102,241,.10), transparent 28%),
            radial-gradient(circle at 90% 10%, rgba(14,165,233,.10), transparent 28%),
            #f7f8fc;
    }

    .main .block-container {
        max-width: 1100px;
        padding-top: 2.2rem;
        padding-bottom: 4rem;
    }

    .hero {
        background: linear-gradient(135deg, #111827 0%, #1e293b 55%, #334155 100%);
        border-radius: 28px;
        padding: 38px 38px 34px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 18px 50px rgba(15,23,42,.18);
        position: relative;
        overflow: hidden;
    }

    .hero:after {
        content: "🌡️";
        position: absolute;
        right: 35px;
        top: 22px;
        font-size: 88px;
        opacity: .12;
    }

    .hero-kicker {
        font-size: 13px;
        font-weight: 700;
        letter-spacing: .12em;
        text-transform: uppercase;
        color: #93c5fd;
        margin-bottom: 9px;
    }

    .hero-title {
        font-size: clamp(30px, 5vw, 52px);
        line-height: 1.08;
        font-weight: 800;
        letter-spacing: -.045em;
        margin: 0;
    }

    .hero-desc {
        margin-top: 14px;
        color: #cbd5e1;
        font-size: 16px;
        line-height: 1.65;
        max-width: 720px;
    }

    .panel {
        background: rgba(255,255,255,.90);
        border: 1px solid #e5e7eb;
        border-radius: 24px;
        padding: 24px;
        box-shadow: 0 8px 30px rgba(15,23,42,.06);
        margin-bottom: 20px;
    }

    .section-title {
        font-size: 18px;
        font-weight: 800;
        color: #111827;
        margin-bottom: 5px;
    }

    .section-sub {
        color: #64748b;
        font-size: 13px;
        margin-bottom: 18px;
    }

    .result-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 26px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 12px 40px rgba(15,23,42,.07);
    }

    .rank-label {
        color: #64748b;
        font-size: 14px;
        font-weight: 700;
        letter-spacing: .03em;
    }

    .rank-number {
        font-size: clamp(58px, 10vw, 100px);
        font-weight: 800;
        line-height: 1;
        letter-spacing: -.06em;
        color: #111827;
        margin: 8px 0;
    }

    .rank-number span {
        font-size: .32em;
        letter-spacing: -.01em;
        margin-left: 5px;
        color: #64748b;
    }

    .temperature {
        font-size: 34px;
        font-weight: 800;
        color: #2563eb;
        margin-top: 8px;
    }

    .period-text {
        color: #64748b;
        font-size: 14px;
        margin-top: 7px;
    }

    .badge {
        display: inline-block;
        padding: 7px 13px;
        border-radius: 999px;
        background: #eff6ff;
        color: #2563eb;
        font-size: 12px;
        font-weight: 800;
        margin-top: 14px;
    }

    .stat-box {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 20px;
        padding: 20px;
        height: 100%;
    }

    .stat-title {
        color: #64748b;
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .stat-value {
        color: #111827;
        font-size: 27px;
        font-weight: 800;
        letter-spacing: -.03em;
    }

    .stat-note {
        color: #94a3b8;
        font-size: 12px;
        margin-top: 5px;
    }

    .champion {
        background: linear-gradient(135deg, #fef3c7, #fff7ed);
        border: 1px solid #fbbf24;
        border-radius: 24px;
        padding: 25px;
        text-align: center;
        margin: 18px 0;
    }

    .champion-title {
        font-size: 28px;
        font-weight: 800;
        color: #92400e;
    }

    .champion-desc {
        color: #92400e;
        margin-top: 7px;
    }

    .info {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 18px;
        padding: 15px 18px;
        color: #1e40af;
        font-size: 13px;
        line-height: 1.6;
    }

    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 12px;
        padding-top: 20px;
    }

    div[data-testid="stDateInput"] label {
        font-weight: 700;
        color: #334155;
    }

    @media (max-width: 640px) {
        .main .block-container {
            padding: 1rem 0.8rem 3rem;
        }

        .hero {
            border-radius: 22px;
            padding: 27px 23px;
        }

        .hero:after {
            right: 15px;
            top: 20px;
            font-size: 60px;
        }

        .panel {
            padding: 18px;
            border-radius: 20px;
        }

        .result-card {
            padding: 22px 12px;
        }
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# 데이터 읽기
# =========================================================

@st.cache_data
def load_weather_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            "seoul.csy 파일을 찾을 수 없습니다. "
            "app.py와 같은 폴더에 seoul.csy를 넣어주세요."
        )

    records = {}

    with open(DATA_FILE, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            raw_date = (row.get("날짜") or "").strip()
            raw_temp = (row.get("평균기온") or "").strip()

            if not raw_date or not raw_temp:
                continue

            try:
                # 데이터에 포함될 수 있는 탭/공백 제거
                raw_date = raw_date.strip()

                # YYYY-MM-DD 형태
                dt = datetime.strptime(raw_date[:10], "%Y-%m-%d").date()
                temp = float(raw_temp)

                records[dt] = temp

            except (ValueError, TypeError):
                continue

    if not records:
        raise ValueError("읽을 수 있는 기온 데이터가 없습니다.")

    return records


# =========================================================
# 연속 기간 계산
# =========================================================

@st.cache_data
def prepare_calendar_data(records):
    min_date = min(records.keys())
    max_date = max(records.keys())

    dates = []
    values = []

    current = min_date

    while current <= max_date:
        dates.append(current)

        if current in records:
            values.append(records[current])
        else:
            values.append(None)

        current += timedelta(days=1)

    return min_date, max_date, dates, values


# =========================================================
# 누적합 생성
# =========================================================

@st.cache_data
def make_prefix_arrays(values):
    """
    missing value(None)가 있는 경우에도
    기간별 합계와 유효 데이터 개수를 빠르게 계산.
    """
    prefix_sum = [0.0]
    prefix_count = [0]

    for value in values:
        if value is None:
            prefix_sum.append(prefix_sum[-1])
            prefix_count.append(prefix_count[-1])
        else:
            prefix_sum.append(prefix_sum[-1] + value)
            prefix_count.append(prefix_count[-1] + 1)

    return prefix_sum, prefix_count


# =========================================================
# 기간 평균
# =========================================================

def period_stats(
    start_date,
    end_date,
    records
):
    current = start_date
    total = 0.0
    count = 0
    total_days = 0

    min_temp = None
    max_temp = None

    while current <= end_date:
        total_days += 1

        if current in records:
            value = records[current]
            total += value
            count += 1

            if min_temp is None or value < min_temp:
                min_temp = value

            if max_temp is None or value > max_temp:
                max_temp = value

        current += timedelta(days=1)

    if count == 0:
        return None

    return {
        "mean": total / count,
        "count": count,
        "total_days": total_days,
        "min": min_temp,
        "max": max_temp,
        "complete": count == total_days,
    }


# =========================================================
# 동일 길이 역사 기간 랭킹
# =========================================================

@st.cache_data
def calculate_historical_ranking(
    selected_start,
    selected_end,
    min_date,
    max_date,
    dates,
    values,
    prefix_sum,
    prefix_count
):
    duration = (selected_end - selected_start).days + 1

    total_calendar_days = len(dates)

    if duration > total_calendar_days:
        return None

    # 선택 기간의 인덱스
    try:
        selected_index = (selected_start - min_date).days
    except Exception:
        return None

    if selected_index < 0:
        return None

    selected_end_index = selected_index + duration - 1

    if selected_end_index >= total_calendar_days:
        return None

    selected_sum = (
        prefix_sum[selected_end_index + 1]
        - prefix_sum[selected_index]
    )

    selected_count = (
        prefix_count[selected_end_index + 1]
        - prefix_count[selected_index]
    )

    # 선택 기간에 결측치가 있으면 정확한 비교 불가
    if selected_count != duration:
        return {
            "valid": False,
            "duration": duration,
            "reason": "selected_missing",
        }

    selected_mean = selected_sum / selected_count

    historical = []

    # 모든 가능한 동일 길이 기간을 순회
    last_start_index = total_calendar_days - duration

    for i in range(last_start_index + 1):
        j = i + duration

        count = prefix_count[j] - prefix_count[i]

        # 결측치가 있는 기간은 순위에서 제외
        if count != duration:
            continue

        total = prefix_sum[j] - prefix_sum[i]
        mean = total / duration

        historical.append(
            (
                mean,
                dates[i],
                dates[j - 1]
            )
        )

    if not historical:
        return None

    # 평균기온이 높은 순서
    historical.sort(key=lambda x: x[0], reverse=True)

    # 같은 평균값은 같은 순위
    rank = 1
    for idx, item in enumerate(historical):
        if item[0] > selected_mean:
            rank = idx + 1
        else:
            break

    # 정확한 백분위
    n = len(historical)

    better_count = sum(
        1 for item in historical
        if item[0] > selected_mean
    )

    percentile = ((n - better_count) / n) * 100

    # 최고/최저 기간
    hottest = historical[0]
    coldest = historical[-1]

    return {
        "valid": True,
        "selected_mean": selected_mean,
        "rank": rank,
        "total_periods": n,
        "percentile": percentile,
        "duration": duration,
        "hottest": hottest,
        "coldest": coldest,
        "historical": historical,
    }


# =========================================================
# 시작
# =========================================================

try:
    records = load_weather_data()
    min_date, max_date, dates, values = prepare_calendar_data(records)
    prefix_sum, prefix_count = make_prefix_arrays(values)

except Exception as e:
    st.error(str(e))
    st.stop()


# =========================================================
# 헤더
# =========================================================

st.markdown("""
<div class="hero">
    <div class="hero-kicker">SEOUL TEMPERATURE ARCHIVE</div>
    <div class="hero-title">이 기간, 역대 몇 위였을까?</div>
    <div class="hero-desc">
        서울의 과거 기온 데이터를 바탕으로 원하는 두 날짜를 선택해보세요.
        같은 기간 길이의 모든 역사적 기간과 비교해
        선택한 기간의 평균기온이 얼마나 특별했는지 보여드립니다.
    </div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# 데이터 정보
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-title">관측 기간</div>
        <div class="stat-value">{min_date.year} — {max_date.year}</div>
        <div class="stat-note">서울 기온 데이터</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-title">데이터 일수</div>
        <div class="stat-value">{len(records):,}일</div>
        <div class="stat-note">평균기온 기록 기준</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-title">비교 기준</div>
        <div class="stat-value">같은 기간 길이</div>
        <div class="stat-note">공정한 역사 비교</div>
    </div>
    """, unsafe_allow_html=True)


st.write("")


# =========================================================
# 날짜 선택
# =========================================================

st.markdown("""
<div class="panel">
    <div class="section-title">📅 비교할 기간을 선택하세요</div>
    <div class="section-sub">
        시작일과 종료일을 포함한 기간의 평균기온을 계산합니다.
    </div>
</div>
""", unsafe_allow_html=True)

c1, c2 = st.columns(2)

default_start = date(2025, 8, 1)
default_end = date(2025, 8, 15)

if default_start < min_date:
    default_start = min_date

if default_end > max_date:
    default_end = max_date

with c1:
    selected_start = st.date_input(
        "시작일",
        value=default_start,
        min_value=min_date,
        max_value=max_date,
        format="YYYY-MM-DD",
    )

with c2:
    selected_end = st.date_input(
        "종료일",
        value=default_end,
        min_value=min_date,
        max_value=max_date,
        format="YYYY-MM-DD",
    )


# =========================================================
# 날짜 검증
# =========================================================

if selected_start > selected_end:
    st.error("시작일이 종료일보다 늦습니다. 날짜를 다시 선택해주세요.")
    st.stop()


# =========================================================
# 선택 기간 기본 통계
# =========================================================

stats = period_stats(
    selected_start,
    selected_end,
    records
)

if stats is None:
    st.error("선택한 기간에는 기온 데이터가 없습니다.")
    st.stop()

if not stats["complete"]:
    missing = stats["total_days"] - stats["count"]

    st.warning(
        f"선택 기간에 기온 데이터가 없는 날짜가 {missing}일 있습니다. "
        "정확한 역대 순위를 계산하려면 모든 날짜의 데이터가 필요합니다."
    )
    st.stop()


# =========================================================
# 랭킹 계산
# =========================================================

result = calculate_historical_ranking(
    selected_start,
    selected_end,
    min_date,
    max_date,
    dates,
    values,
    prefix_sum,
    prefix_count,
)


if result is None:
    st.error("역사적 비교 기간을 계산할 수 없습니다.")
    st.stop()

if not result["valid"]:
    st.warning(result["reason"])
    st.stop()


rank = result["rank"]
total_periods = result["total_periods"]
mean_temp = result["selected_mean"]
duration = result["duration"]
percentile = result["percentile"]

# =========================================================
# 결과 카드
# =========================================================

st.write("")
st.markdown("""
<div class="section-title">🏆 역사 속에서의 위치</div>
<div class="section-sub">
    선택한 기간과 길이가 같은 모든 연속 기간을 비교했습니다.
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="result-card">
    <div class="rank-label">역대 평균기온 순위</div>
    <div class="rank-number">
        {rank}<span>위</span>
    </div>
    <div class="temperature">
        {mean_temp:.1f}℃
    </div>
    <div class="period-text">
        {selected_start.strftime("%Y년 %m월 %d일")}
        —
        {selected_end.strftime("%Y년 %m월 %d일")}
        · {duration}일
    </div>
    <div class="badge">
        역대 {total_periods:,}개 동일기간 비교
    </div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# 특별 기록
# =========================================================

if rank == 1:
    st.markdown("""
    <div class="champion">
        <div class="champion-title">👑 역대 1위입니다!</div>
        <div class="champion-desc">
            선택한 기간은 같은 길이의 역사적 기간 중
            평균기온이 가장 높았습니다.
        </div>
    </div>
    """, unsafe_allow_html=True)

elif rank <= 10:
    st.markdown(f"""
    <div class="champion">
        <div class="champion-title">🔥 역대 TOP 10</div>
        <div class="champion-desc">
            전체 역사에서 상위 {rank}위에 해당하는 아주 따뜻한 기간입니다.
        </div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# 보조 지표
# =========================================================

st.write("")

a, b, c = st.columns(3)

with a:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-title">상위 위치</div>
        <div class="stat-value">상위 {percentile:.1f}%</div>
        <div class="stat-note">평균기온이 높은 쪽 기준</div>
    </div>
    """, unsafe_allow_html=True)

with b:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-title">기간 최저기온</div>
        <div class="stat-value">{stats["min"]:.1f}℃</div>
        <div class="stat-note">선택 기간 일평균 중 최저</div>
    </div>
    """, unsafe_allow_html=True)

with c:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-title">기간 최고기온</div>
        <div class="stat-value">{stats["max"]:.1f}℃</div>
        <div class="stat-note">선택 기간 일평균 중 최고</div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# 역사적 최고 / 최저
# =========================================================

st.write("")

hottest = result["hottest"]
coldest = result["coldest"]

x, y = st.columns(2)

with x:
    st.markdown(f"""
    <div class="panel">
        <div class="section-title">🔥 가장 더웠던 동일기간</div>
        <div class="section-sub">
            {duration}일 동안의 평균기온이 가장 높았던 기간
        </div>
        <div style="font-size:30px;font-weight:800;color:#dc2626;">
            {hottest[0]:.1f}℃
        </div>
        <div style="margin-top:8px;color:#64748b;font-size:14px;">
            {hottest[1].strftime("%Y-%m-%d")}
            —
            {hottest[2].strftime("%Y-%m-%d")}
        </div>
    </div>
    """, unsafe_allow_html=True)

with y:
    st.markdown(f"""
    <div class="panel">
        <div class="section-title">❄️ 가장 추웠던 동일기간</div>
        <div class="section-sub">
            {duration}일 동안의 평균기온이 가장 낮았던 기간
        </div>
        <div style="font-size:30px;font-weight:800;color:#2563eb;">
            {coldest[0]:.1f}℃
        </div>
        <div style="margin-top:8px;color:#64748b;font-size:14px;">
            {coldest[1].strftime("%Y-%m-%d")}
            —
            {coldest[2].strftime("%Y-%m-%d")}
        </div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# 선택 기간 일별 차트
# =========================================================

chart_data = {}

current = selected_start

while current <= selected_end:
    if current in records:
        chart_data[current.strftime("%m-%d")] = records[current]

    current += timedelta(days=1)

st.write("")

st.markdown("""
<div class="panel">
    <div class="section-title">📈 선택 기간의 일별 평균기온</div>
    <div class="section-sub">
        선택한 기간 동안 기온이 어떻게 움직였는지 확인할 수 있습니다.
    </div>
</div>
""", unsafe_allow_html=True)

st.line_chart(
    chart_data,
    height=330,
    use_container_width=True,
)


# =========================================================
# 계산 방법
# =========================================================

st.write("")

with st.expander("ℹ️ 순위는 어떻게 계산하나요?"):
    st.markdown(f"""
**예를 들어 10일을 선택했다면**, 과거 데이터에서 가능한 모든 **10일 연속 기간**을 찾아 평균기온을 계산합니다.

그다음:

1. 선택한 10일의 평균기온을 계산
2. 과거의 모든 10일 기간의 평균기온을 계산
3. 평균기온이 높은 순으로 정렬
4. 선택한 기간의 순위를 결정

따라서 **기간의 길이가 다른 기간을 억지로 비교하지 않습니다.**

현재 선택 기간:

- 기간: **{duration}일**
- 평균기온: **{mean_temp:.1f}℃**
- 순위: **{rank}위 / {total_periods:,}개**
- 위치: **상위 {percentile:.1f}%**

데이터가 하루라도 빠져 있는 역사적 기간은 공정한 비교를 위해 순위 계산에서 제외합니다.
""")


# =========================================================
# 푸터
# =========================================================

st.markdown("""
<div class="footer">
    Seoul Temperature Archive · Historical temperature ranking
</div>
""", unsafe_allow_html=True)
