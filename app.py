import requests
import urllib3
import pandas as pd
import streamlit as st
import folium
import plotly.express as px
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster, MiniMap, Fullscreen

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="台灣空氣品質監測儀表板",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# API
# =========================
API_KEY = "a654c490-1802-48ee-b439-88cc499d3591"
API_URL = f"https://data.moenv.gov.tw/api/v2/aqx_p_432?language=zh&api_key={API_KEY}"

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>
/* FORCE LIGHT MODE STYLE */
html, body, [class*="css"] {
    color: #172033 !important;
}

/* App background */
.stApp {
    background: linear-gradient(
        180deg,
        #eef7f6 0%,
        #f6f8fb 45%,
        #ffffff 100%
    ) !important;

    color: #172033 !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #ffffff !important;
    color: #172033 !important;
    border-right: 1px solid #e2e8f0 !important;
}

/* Sidebar text */
section[data-testid="stSidebar"] * {
    color: #172033 !important;
}

/* Input */
.stTextInput input {
    background: white !important;
    color: #172033 !important;
    border: 2px solid #dbe4f0 !important;
}

/* Placeholder */
.stTextInput input::placeholder {
    color: #94a3b8 !important;
}

/* Selectbox */
div[data-baseweb="select"] > div {
    background: white !important;
    color: #172033 !important;
}

/* Selectbox text */
div[data-baseweb="select"] span,
div[data-baseweb="select"] div {
    color: #172033 !important;
}

/* Slider */
.stSlider * {
    color: #172033 !important;
}

/* Radio */
.stRadio * {
    color: #172033 !important;
}

/* Metric cards */
.metric-card {
    background: white !important;
    color: #172033 !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    background: white !important;
    color: #172033 !important;
}

/* Markdown */
.stMarkdown,
.stMarkdown * {
    color: #172033 !important;
}

:root {
    --primary: #0f766e;
    --secondary: #2563eb;
    --bg: #f4f7fb;
    --card: #ffffff;
    --text: #172033;
    --muted: #64748b;
    --border: #e2e8f0;
}

.stApp {
    background: linear-gradient(
        180deg,
        #eef7f6 0%,
        #f6f8fb 45%,
        #ffffff 100%
    );
}

section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid var(--border);
}

.hero {
    padding: 35px;
    border-radius: 28px;

    background:
        radial-gradient(circle at top right,
        rgba(255,255,255,.25),
        transparent 30%),
        linear-gradient(135deg,#0f766e 0%,#2563eb 100%);

    color: white;
    margin-bottom: 25px;

    box-shadow: 0 18px 40px rgba(15,118,110,.25);
}

.hero h1 {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 10px;
}

.hero p {
    font-size: 17px;
    opacity: .95;
}

.pill-row {
    margin-top: 20px;
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}

.pill {
    padding: 10px 18px;
    border-radius: 999px;
    background: rgba(255,255,255,.18);
    border: 1px solid rgba(255,255,255,.25);
    color: white;
    font-weight: 600;
    transition: 0.3s;
    cursor: pointer;
}

.pill:hover {
    background: rgba(255,255,255,.32);
    transform: translateY(-2px);
}

.metric-card {
    background: white;
    padding: 22px;
    border-radius: 22px;
    border: 1px solid var(--border);

    box-shadow:
        0 10px 25px rgba(15,23,42,.08);

    min-height: 130px;
    height: 180px;

    display: flex;
    flex-direction: column;
    justify-content: center;
}

.metric-card h3 {
    color: var(--muted);
    font-size: 15px;
    margin-bottom: 10px;
}

.metric-card p {
    font-size: 28px;
    line-height: 1.2;
    word-break: break-word;
}

.metric-card small {
    color: var(--muted);
}

.section-title {
    font-size: 28px;
    font-weight: 850;
    margin: 28px 0 18px 0;
    color: var(--text);
}

.legend {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 15px;
}

.legend span {
    background: white;
    border-radius: 999px;
    border: 1px solid var(--border);
    padding: 8px 12px;
    font-size: 13px;
}

.dot {
    width: 11px;
    height: 11px;
    border-radius: 999px;
    display: inline-block;
}

.footer {
    text-align: center;
    padding: 30px;
    color: #64748b;
    margin-top: 20px;
}

.stTextInput input {
    border: 2px solid #dbe4f0 !important;
    border-radius: 7px !important;
    padding: 12px !important;
    background-color: white !important;
    box-shadow: none !important;
}

/* SELECTBOX + MULTISELECT */
div[data-baseweb="select"] > div {
    border: 2px solid #dbe4f0 !important;
    border-radius: 7px !important;
    background: white !important;
    box-shadow: none !important;
    transition: none !important;
}

/* Khi hover */
div[data-baseweb="select"] > div:hover {
    border: 2px solid #dbe4f0 !important;
    box-shadow: none !important;
}

/* Khi focus/click */
div[data-baseweb="select"] > div:focus-within {
    border: 2px solid #dbe4f0 !important;
    box-shadow: none !important;
    outline: none !important;
}

/* Remove blue glow */
div[data-baseweb="select"] *:focus {
    box-shadow: none !important;
    outline: none !important;
}

</style>
""", unsafe_allow_html=True)

# =========================
# HERO
# =========================
st.markdown("""
<div class="hero">

<h1>🌿 台灣空氣品質監測儀表板</h1>

<p>Air Quality OpenData Dynamic Dashboard</p>

<p>
即時監控 AQI、PM2.5、污染物、
互動地圖與數據分析
</p>

<div class="pill-row">

<a href="https://data.gov.tw/dataset/40448"
target="_blank"
style="text-decoration:none;">
    <span class="pill">即時 OpenData</span>
</a>

<a href="#map-section"
style="text-decoration:none;">
    <span class="pill">互動地圖</span>
</a>

<a href="#filter-section"
style="text-decoration:none;">
    <span class="pill">多條件篩選</span>
</a>

<a href="#chart-section"
style="text-decoration:none;">
    <span class="pill">圖表分析</span>
</a>

</div>

</div>
""", unsafe_allow_html=True)

# =========================
# LOAD DATA
# =========================
urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)

@st.cache_data(ttl=1800)
def load_data():

    try:
        response = requests.get(
            API_URL,
            timeout=15,
            verify=False
        )

        response.raise_for_status()

        data = response.json()

        if isinstance(data, dict):
            records = data.get("records", [])
        else:
            records = data

        return pd.DataFrame(records)

    except requests.exceptions.RequestException as e:

        st.error(f"API 載入失敗: {e}")

        return pd.DataFrame()

# refresh button
if st.sidebar.button("🔄 重新整理資料", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

df = load_data()

# =========================
# NUMERIC
# =========================
numeric_fields = [
    "aqi",
    "pm2.5",
    "pm10",
    "so2",
    "co",
    "o3",
    "o3_8hr",
    "no2",
    "nox",
    "wind_speed",
    "longitude",
    "latitude"
]

for col in numeric_fields:
    if col in df.columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

# =========================
# AQI FUNCTIONS
# =========================
def get_color(aqi):

    if pd.isna(aqi):
        return "gray"

    if aqi <= 50:
        return "green"

    elif aqi <= 100:
        return "orange"

    elif aqi <= 150:
        return "red"

    elif aqi <= 200:
        return "purple"

    return "darkred"


def get_aqi_level(aqi):

    if pd.isna(aqi):
        return "無資料"

    if aqi <= 50:
        return "良好"

    elif aqi <= 100:
        return "普通"

    elif aqi <= 150:
        return "敏感族群不健康"

    elif aqi <= 200:
        return "不健康"

    return "非常不健康"

df["aqi_level"] = df["aqi"].apply(get_aqi_level)

# =========================
# FILTER SECTION
# =========================
st.markdown(
    '<div id="filter-section"></div>',
    unsafe_allow_html=True
)

st.sidebar.title("🔎 搜尋與篩選")

keyword = st.sidebar.text_input(
    "輸入縣市或測站名稱"
)

city_list = ["全部"] + sorted(
    df["county"].dropna().unique().tolist()
)

selected_city = st.sidebar.selectbox(
    "選擇縣市",
    city_list
)

status_list = [
    "全部",
    "良好",
    "普通",
    "敏感族群不健康",
    "不健康",
    "非常不健康"
]

selected_status = st.sidebar.selectbox(
    "選擇空氣品質狀態",
    status_list
)

aqi_range = st.sidebar.slider(
    "AQI 範圍",
    0,
    300,
    (0, 300)
)

analyze_field = st.sidebar.selectbox(
    "選擇分析欄位",
    [
        "aqi",
        "pm2.5",
        "pm10",
        "so2",
        "co",
        "o3",
        "o3_8hr",
        "no2",
        "nox",
        "wind_speed"
    ]
)

map_mode = st.sidebar.radio(
    "地圖顯示模式",
    ["單點標記", "群組標記"]
)

# =========================
# FILTER DATA
# =========================
df_show = df.copy()

if selected_city != "全部":
    df_show = df_show[
        df_show["county"] == selected_city
    ]

if selected_status != "全部":
    df_show = df_show[
        df_show["status"] == selected_status
    ]

df_show = df_show[
    df_show["aqi"].between(
        aqi_range[0],
        aqi_range[1]
    )
]

if keyword:
    df_show = df_show[
        df_show["county"].str.contains(
            keyword,
            na=False
        )
        |
        df_show["sitename"].str.contains(
            keyword,
            na=False
        )
    ]

# =========================
# METRICS
# =========================
total_sites = len(df_show)

avg_aqi = round(
    df_show["aqi"].mean(),
    1
)

max_aqi_value = df_show["aqi"].max()

if pd.isna(max_aqi_value):
    max_aqi = 0
else:
    max_aqi = int(max_aqi_value)

bad_sites = len(
    df_show[df_show["aqi"] > 100]
)

if "publishtime" in df_show.columns and not df_show["publishtime"].dropna().empty:

    latest_time_raw = df_show["publishtime"].dropna().iloc[0]

    latest_time = (
        str(latest_time_raw)
        .replace("/", "-")
        .replace("  ", " ")
    )

    # cắt còn 1 dòng đẹp hơn
    latest_time = latest_time[:16]

else:
    latest_time = "無資料"
    

col1, col2, col3, col4, col5 = st.columns(5)

metrics = [
    ("測站數量", total_sites, "符合目前篩選"),
    ("平均 AQI", avg_aqi, "越低越好"),
    ("最高 AQI", max_aqi, "目前最高測站"),
    ("AQI >100", bad_sites, "需注意測站"),
    ("更新時間", latest_time, "OpenData 發布")
]

for col, item in zip(
    [col1,col2,col3,col4,col5],
    metrics
):

    title, value, helper = item

    with col:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{title}</h3>
            <p>{value}</p>
            <small>{helper}</small>
        </div>
        """, unsafe_allow_html=True)

# =========================
# MAP SECTION
# =========================
st.markdown(
    '''
    <div id="map-section"
    class="section-title">
    🗺️ 空氣品質地圖
    </div>
    ''',
    unsafe_allow_html=True
)

st.markdown("""
<div class="legend">

<span>
<i class="dot"
style="background:green"></i>
良好 0-50
</span>

<span>
<i class="dot"
style="background:orange"></i>
普通 51-100
</span>

<span>
<i class="dot"
style="background:red"></i>
敏感族群不健康
</span>

<span>
<i class="dot"
style="background:purple"></i>
不健康
</span>

<span>
<i class="dot"
style="background:darkred"></i>
非常不健康
</span>

</div>
""", unsafe_allow_html=True)

m = folium.Map(
    location=[23.7,121],
    zoom_start=7,
    tiles="CartoDB positron"
)

Fullscreen().add_to(m)

MiniMap().add_to(m)

marker_group = (
    MarkerCluster().add_to(m)
    if map_mode == "群組標記"
    else m
)

for _, row in df_show.iterrows():

    if (
        pd.notna(row["latitude"])
        and
        pd.notna(row["longitude"])
    ):

        popup_text = f"""
        <div style="font-size:14px">
        <h4>{row.get("sitename","")}</h4>

        <b>縣市：</b>
        {row.get("county","")}<br>

        <b>AQI：</b>
        {row.get("aqi","")}<br>

        <b>狀態：</b>
        {row.get("status","")}<br>

        <b>PM2.5：</b>
        {row.get("pm2.5","")}<br>

        <b>PM10：</b>
        {row.get("pm10","")}<br>

        <b>更新時間：</b>
        {row.get("publishtime","")}
        </div>
        """

        folium.CircleMarker(
            location=[
                row["latitude"],
                row["longitude"]
            ],
            radius=8,
            color=get_color(row["aqi"]),
            fill=True,
            fill_color=get_color(row["aqi"]),
            fill_opacity=0.85,
            popup=folium.Popup(
                popup_text,
                max_width=320
            )
        ).add_to(marker_group)

st_folium(
    m,
    use_container_width=True,
    height=620
)

# =========================
# CHART SECTION
# =========================
st.markdown(
    '''
    <div id="chart-section"
    class="section-title">
    📊 數據分析圖表
    </div>
    ''',
    unsafe_allow_html=True
)

chart_col1, chart_col2 = st.columns(2)

top15 = (
    df_show
    .dropna(subset=[analyze_field])
    .sort_values(
        by=analyze_field,
        ascending=False
    )
    .head(15)
)

with chart_col1:

    fig_bar = px.bar(
        top15,
        x="sitename",
        y=analyze_field,
        color=analyze_field,
        text=analyze_field,
        title=f"{analyze_field} 前15測站"
    )

    fig_bar.update_layout(
        height=450
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

with chart_col2:

    status_count = (
        df_show["status"]
        .value_counts()
        .reset_index()
    )

    status_count.columns = [
        "status",
        "count"
    ]

    fig_pie = px.pie(
        status_count,
        names="status",
        values="count",
        hole=.5,
        title="空氣品質比例"
    )

    fig_pie.update_layout(
        height=450
    )

    st.plotly_chart(
        fig_pie,
        use_container_width=True
    )

# =========================
# TABLE
# =========================
st.markdown(
    '<div class="section-title">📋 原始資料表</div>',
    unsafe_allow_html=True
)

display_cols = [
    "sitename",
    "county",
    "aqi",
    "aqi_level",
    "status",
    "pollutant",
    "pm2.5",
    "pm10",
    "so2",
    "co",
    "o3",
    "no2",
    "wind_speed",
    "publishtime"
]

csv = (
    df_show[display_cols]
    .to_csv(index=False)
    .encode("utf-8-sig")
)

st.download_button(
    "⬇️ 下載 CSV",
    csv,
    "taiwan_air_quality.csv",
    "text/csv",
    use_container_width=True
)

st.dataframe(
    df_show[display_cols],
    use_container_width=True,
    height=420
)


# =========================
# FOOTER
# =========================
st.markdown("""
<div class="footer">

資料來源：
環境部 OpenData 空氣品質 AQI

</div>
""", unsafe_allow_html=True)