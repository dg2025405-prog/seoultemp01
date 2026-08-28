import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="서울 기온 랭킹",
    page_icon="🌡️",
    layout="centered"
)

# 제목
st.title("🌡️ 서울 기온 랭킹")
st.write("날짜를 선택하면 해당 기간이 역대 기온 중 몇 위인지 확인할 수 있습니다.")

# ---------------------------------------------------------
# 데이터 불러오기
# 파일은 반드시 seoul.csv
# ---------------------------------------------------------
try:
    df = pd.read_csv("seoul.csv")
except Exception as e:
    st.error("seoul.csv 파일을 찾을 수 없습니다.")
    st.stop()

# 필요한 컬럼 확인
required_columns = ["날짜", "평균기온", "최저기온", "최고기온"]

for column in required_columns:
    if column not in df.columns:
        st.error("CSV 파일에 필요한 컬럼이 없습니다: " + column)
        st.stop()

# 날짜 처리
df["날짜"] = df["날짜"].astype(str).str.strip()
df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")

# 기온 숫자 처리
df["평균기온"] = pd.to_numeric(df["평균기온"], errors="coerce")
df["최저기온"] = pd.to_numeric(df["최저기온"], errors="coerce")
df["최고기온"] = pd.to_numeric(df["최고기온"], errors="coerce")

# 사용할 데이터만 남김
df = df.dropna(
    subset=["날짜", "평균기온"]
)

df = df.sort_values("날짜").reset_index(drop=True)

# 데이터가 없는 경우
if len(df) == 0:
    st.error("읽을 수 있는 기온 데이터가 없습니다.")
    st.stop()

# ---------------------------------------------------------
# 날짜 범위
# ---------------------------------------------------------
first_date = df["날짜"].min().date()
last_date = df["날짜"].max().date()

st.subheader("📅 비교할 기간")

col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input(
        "시작 날짜",
        value=first_date,
        min_value=first_date,
        max_value=last_date
    )

with col2:
    end_date = st.date_input(
        "종료 날짜",
        value=last_date,
        min_value=first_date,
        max_value=last_date
    )

# 날짜 순서 확인
if start_date > end_date:
    st.error("시작 날짜가 종료 날짜보다 늦습니다.")
    st.stop()

# ---------------------------------------------------------
# 선택한 기간
# ---------------------------------------------------------
start = pd.Timestamp(start_date)
end = pd.Timestamp(end_date)

selected = df[
    (df["날짜"] >= start) &
    (df["날짜"] <= end)
].copy()

number_of_days = (end_date - start_date).days + 1

# 데이터가 모든 날짜에 있는지 확인
if len(selected) != number_of_days:
    st.warning(
        "선택한 기간에 데이터가 없는 날짜가 있습니다. "
        "모든 날짜의 데이터가 존재하는 기간을 선택해주세요."
    )
    st.stop()

# 선택 기간 평균기온
selected_average = selected["평균기온"].mean()

# 최고/최저
selected_high = selected["최고기온"].max()
selected_low = selected["최저기온"].min()

# ---------------------------------------------------------
# 역사적 동일 길이 기간 계산
# ---------------------------------------------------------
dates = df["날짜"].tolist()
temperatures = df["평균기온"].tolist()

historical_periods = []

# 모든 가능한 기간 확인
for i in range(len(df) - number_of_days + 1):

    period = df.iloc[i:i + number_of_days]

    # 날짜가 실제로 연속되어 있는지 확인
    first = period.iloc[0]["날짜"]
    last = period.iloc[-1]["날짜"]

    actual_days = (last - first).days + 1

    if actual_days != number_of_days:
        continue

    # 평균기온 계산
    average = period["평균기온"].mean()

    if pd.isna(average):
        continue

    historical_periods.append({
        "시작": first,
        "종료": last,
        "평균기온": average
    })

historical = pd.DataFrame(historical_periods)

# 역사 데이터가 없는 경우
if len(historical) == 0:
    st.error("비교할 수 있는 역사적 기간이 없습니다.")
    st.stop()

# ---------------------------------------------------------
# 순위 계산
# ---------------------------------------------------------

# 평균기온이 높은 순서
historical = historical.sort_values(
    "평균기온",
    ascending=False
).reset_index(drop=True)

# 선택 기간보다 평균기온이 높은 기간의 개수 + 1
rank = (
    historical["평균기온"] > selected_average
).sum() + 1

total = len(historical)

# 상위 몇 %
top_percent = (rank / total) * 100

# ---------------------------------------------------------
# 결과
# ---------------------------------------------------------
st.divider()

st.subheader("🏆 결과")

st.metric(
    "역대 기온 순위",
    f"{rank:,}위 / {total:,}개 기간"
)

st.write(
    f"선택한 **{number_of_days}일**의 평균기온은 "
    f"**{selected_average:.1f}℃**입니다."
)

# 순위에 따른 메시지
if rank == 1:
    st.success("🔥 역대 가장 더운 기간입니다!")
elif rank <= 10:
    st.success("🔥 역대 TOP 10에 들어가는 매우 더운 기간입니다!")
elif rank <= total * 0.05:
    st.info("☀️ 역대 상위 5%에 해당하는 더운 기간입니다.")
elif rank <= total * 0.25:
    st.info("🌤️ 평년보다 따뜻한 편에 해당합니다.")
elif rank >= total * 0.75:
    st.info("🧊 비교적 서늘한 기간에 해당합니다.")
else:
    st.write("🌤️ 역사적으로 중간 정도의 기온입니다.")

# ---------------------------------------------------------
# 선택 기간 상세 정보
# ---------------------------------------------------------
st.divider()

st.subheader("📊 선택 기간 정보")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "평균기온",
        f"{selected_average:.1f}℃"
    )

with c2:
    st.metric(
        "최고기온",
        f"{selected_high:.1f}℃"
    )

with c3:
    st.metric(
        "최저기온",
        f"{selected_low:.1f}℃"
    )

# ---------------------------------------------------------
# 역대 TOP 10
# ---------------------------------------------------------
st.divider()

st.subheader("🔥 역대 가장 더웠던 기간 TOP 10")

top10 = historical.head(10).copy()

top10["기간"] = (
    top10["시작"].dt.strftime("%Y-%m-%d")
    + " ~ "
    + top10["종료"].dt.strftime("%Y-%m-%d")
)

top10["평균기온"] = (
    top10["평균기온"].round(1).astype(str) + "℃"
)

top10 = top10.reset_index(drop=True)

top10.index = top10.index + 1

top10 = top10[["기간", "평균기온"]]

st.dataframe(
    top10,
    use_container_width=True
)

# ---------------------------------------------------------
# 선택 기간 일별 기온
# ---------------------------------------------------------
st.divider()

with st.expander("📈 선택 기간의 일별 기온 보기"):

    chart = selected[
        ["날짜", "평균기온"]
    ].copy()

    chart = chart.set_index("날짜")

    st.line_chart(chart)

# ---------------------------------------------------------
# 데이터 정보
# ---------------------------------------------------------
st.divider()

st.caption(
    "데이터 기간: "
    + first_date.strftime("%Y-%m-%d")
    + " ~ "
    + last_date.strftime("%Y-%m-%d")
)

st.caption(
    "비교 기준: 선택한 기간과 동일한 날짜 수의 연속 기간 중 평균기온"
)
