# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import math
import re
from datetime import datetime
from pathlib import Path

import folium
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import st_folium


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
AQICN_STATIONS = RAW / "aqicn_stations_bbox.csv"
METRO_LINES = RAW / "gz_metro_lines.geojson"
METRO_STATIONS = RAW / "gz_metro_stations.csv"
GZ_BOUNDS = [[22.8, 112.8], [24.1, 113.9]]
GZ_CENTER = [23.1291, 113.2644]
LINE_22_OPEN_MAX_LAT = 23.11
LINE_14_PHASE2_POINTS = [
    ("乐嘉路", 23.17377, 113.25538),
    ("云霄路", 23.1867, 113.2622),
    ("新市墟", 23.1984, 113.2682),
    ("马务", 23.2095, 113.2734),
    ("鹤边", 23.2193, 113.2785),
    ("鹤龙", 23.2302, 113.2821),
    ("彭边", 23.2362, 113.2832),
    ("嘉禾望岗", 23.239942, 113.283733),
]
MANUAL_METRO_STATIONS = [
    {"id": "manual-14-lejialu", "name": "乐嘉路", "lat": 23.17377, "lon": 113.25538, "line": "广州地铁14号线"},
    {"id": "manual-14-yunxiaolu", "name": "云霄路", "lat": 23.1867, "lon": 113.2622, "line": "广州地铁14号线"},
    {"id": "manual-14-xinshixu", "name": "新市墟", "lat": 23.1984, "lon": 113.2682, "line": "广州地铁14号线"},
    {"id": "manual-14-mawu", "name": "马务", "lat": 23.2095, "lon": 113.2734, "line": "广州地铁14号线"},
    {"id": "manual-14-hebian", "name": "鹤边", "lat": 23.2193, "lon": 113.2785, "line": "广州地铁14号线"},
    {"id": "manual-14-helong", "name": "鹤龙", "lat": 23.2302, "lon": 113.2821, "line": "广州地铁14号线"},
    {"id": "manual-14-pengbian", "name": "彭边", "lat": 23.2362, "lon": 113.2832, "line": "广州地铁14号线"},
]


WEATHER_CODE = {
    0: ("晴", "适合出门", "sunny"),
    1: ("大致晴朗", "适合出门", "sunny"),
    2: ("局部多云", "注意体感变化", "cloudy"),
    3: ("阴", "注意体感变化", "overcast"),
    45: ("雾", "注意能见度", "fog"),
    48: ("雾凇", "注意能见度", "fog"),
    51: ("小毛毛雨", "可能需要伞", "rain"),
    53: ("毛毛雨", "建议带伞", "rain"),
    55: ("较强毛毛雨", "建议带伞", "rain"),
    56: ("冻毛毛雨", "谨慎出门", "rain"),
    57: ("强冻毛毛雨", "谨慎出门", "rain"),
    61: ("小雨", "建议带伞", "rain"),
    63: ("中雨", "建议带伞", "rain"),
    65: ("大雨", "减少户外停留", "heavy_rain"),
    66: ("冻雨", "谨慎出门", "heavy_rain"),
    67: ("强冻雨", "谨慎出门", "heavy_rain"),
    71: ("小雪", "注意路面", "snow"),
    73: ("中雪", "注意路面", "snow"),
    75: ("大雪", "谨慎出门", "snow"),
    77: ("雪粒", "注意路面", "snow"),
    80: ("阵雨", "建议带伞", "rain"),
    81: ("较强阵雨", "建议带伞", "rain"),
    82: ("强阵雨", "减少户外停留", "heavy_rain"),
    85: ("小阵雪", "注意路面", "snow"),
    86: ("强阵雪", "谨慎出门", "snow"),
    95: ("雷雨", "减少户外停留", "thunder"),
    96: ("雷雨伴小冰雹", "尽量避开户外", "thunder"),
    99: ("雷雨伴冰雹", "尽量避开户外", "thunder"),
}

WEATHER_STYLE = {
    "sunny": {"bg": "#f59e0b", "fg": "#fff7ed", "badge": "#92400e"},
    "cloudy": {"bg": "#475569", "fg": "#f8fafc", "badge": "#1e293b"},
    "overcast": {"bg": "#4b5563", "fg": "#f9fafb", "badge": "#1f2937"},
    "fog": {"bg": "#6b7280", "fg": "#f9fafb", "badge": "#374151"},
    "rain": {"bg": "#475569", "fg": "#f8fafc", "badge": "#1e3a8a"},
    "heavy_rain": {"bg": "#334155", "fg": "#f8fafc", "badge": "#0f172a"},
    "snow": {"bg": "#64748b", "fg": "#f8fafc", "badge": "#1e40af"},
    "thunder": {"bg": "#4338ca", "fg": "#eef2ff", "badge": "#312e81"},
    "unknown": {"bg": "#64748b", "fg": "#f8fafc", "badge": "#334155"},
}

WEATHER_ICON = {
    "sunny": "☀",
    "cloudy": "☁",
    "overcast": "☁",
    "fog": "雾",
    "rain": "☂",
    "heavy_rain": "雨",
    "snow": "雪",
    "thunder": "雷",
    "unknown": "?",
}

METRO_LINE_COLORS = {
    "1号线": "#F3D03E",
    "2号线": "#00629B",
    "3号线": "#EF7C1C",
    "3号线北延段": "#EF7C1C",
    "3号线支线": "#EF7C1C",
    "4号线": "#00843D",
    "5号线": "#C5003E",
    "6号线": "#80225F",
    "7号线": "#97D700",
    "8号线": "#0095DA",
    "9号线": "#71C5E8",
    "10号线": "#7D9BC1",
    "11号线": "#FAC525",
    "12号线": "#59621D",
    "13号线": "#8E8C13",
    "14号线": "#81312F",
    "15号线": "#AE8A79",
    "16号线": "#9E652E",
    "17号线": "#8B84D7",
    "18号线": "#003DA5",
    "19号线": "#BB29BB",
    "20号线": "#D9017A",
    "21号线": "#201747",
    "22号线": "#C65A1E",
    "广佛线": "#C4D600",
    "APM线": "#00B5E2",
    "佛山地铁2号线": "#E95A0C",
    "佛山地铁3号线": "#009FE3",
    "东莞轨道交通2号线": "#D6001C",
}


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 2rem;
            max-width: 1500px;
        }
        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 10px 12px;
            min-height: 82px;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.55rem;
            line-height: 1.15;
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            overflow: hidden;
        }
        .map-hint {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            color: #374151;
            font-size: 0.95rem;
            font-weight: 600;
            line-height: 1.35;
            margin: 0.75rem 0 0.85rem 0;
            padding: 10px 12px;
        }
        .forecast-title-row {
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            gap: 12px;
            margin-top: 1.15rem;
        }
        .forecast-title-row h3 {
            margin: 0;
        }
        .forecast-help {
            color: #64748b;
            font-size: 0.9rem;
            white-space: nowrap;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def load_aqicn_stations() -> pd.DataFrame:
    df = pd.read_csv(AQICN_STATIONS)
    required = {"uid", "name", "lat", "lon"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"AQICN 站点文件缺少字段: {', '.join(sorted(missing))}")
    df = df.dropna(subset=["uid", "lat", "lon"]).copy()
    df["uid"] = df["uid"].astype(int)
    return df.sort_values("uid").reset_index(drop=True)


@st.cache_data(show_spinner=False)
def load_metro_stations() -> pd.DataFrame:
    df = pd.read_csv(METRO_STATIONS)
    required = {"id", "name", "lat", "lon"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"地铁站点文件缺少字段: {', '.join(sorted(missing))}")
    df = df.dropna(subset=["id", "name", "lat", "lon"]).copy()
    df["id"] = df["id"].astype(str)
    manual = pd.DataFrame(MANUAL_METRO_STATIONS)
    missing_manual = manual.loc[~manual["name"].isin(df["name"])]
    if not missing_manual.empty:
        df = pd.concat([df, missing_manual], ignore_index=True)
    df["label"] = df["name"].astype(str) + " #" + df["id"]
    return df.sort_values(["name", "id"]).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def load_metro_lines() -> dict:
    return json.loads(METRO_LINES.read_text(encoding="utf-8"))


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0088
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    value = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(value))


def nearest_row(df: pd.DataFrame, lat: float, lon: float) -> tuple[pd.Series, float]:
    distances = df.apply(lambda row: haversine_km(lat, lon, float(row["lat"]), float(row["lon"])), axis=1)
    index = distances.idxmin()
    return df.loc[index], float(distances.loc[index])


def weather_text(code: int) -> tuple[str, str, str]:
    return WEATHER_CODE.get(int(code), ("未知", "查看小时预报", "unknown"))


def weather_style(category: str) -> dict[str, str]:
    return WEATHER_STYLE.get(category, WEATHER_STYLE["unknown"])


def metro_line_color(name: str) -> str:
    if "广佛线" in name or "地铁广佛线" in name:
        return METRO_LINE_COLORS["广佛线"]
    if "珠江新城旅客自动输送系统" in name or "APM" in name:
        return METRO_LINE_COLORS["APM线"]
    for key in ["佛山地铁2号线", "佛山地铁3号线", "东莞轨道交通2号线"]:
        if key in name:
            return METRO_LINE_COLORS[key]
    match = re.search(r"广州地铁(\d+)号线", name)
    if match:
        key = f"{match.group(1)}号线"
        return METRO_LINE_COLORS.get(key, "#2563eb")
    for key, color in sorted(METRO_LINE_COLORS.items(), key=lambda item: len(item[0]), reverse=True):
        if key in name:
            return color
    return "#2563eb"


@st.cache_data(ttl=900, show_spinner=False)
def fetch_weather(lat: float, lon: float) -> dict:
    response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,weather_code,wind_speed_10m",
            "hourly": "temperature_2m,apparent_temperature,precipitation_probability,precipitation,rain,weather_code,wind_speed_10m,relative_humidity_2m",
            "forecast_hours": 24,
            "timezone": "Asia/Shanghai",
        },
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def hourly_table(weather: dict) -> pd.DataFrame:
    hourly = weather["hourly"]
    df = pd.DataFrame(hourly)
    df = df.head(12).copy()
    df["时间"] = pd.to_datetime(df["time"]).dt.strftime("%m-%d %H:%M")
    labels = df["weather_code"].map(lambda code: weather_text(int(code))[0])
    return pd.DataFrame(
        {
            "时间": df["时间"],
            "天气情况": labels,
            "温度/体感": df["temperature_2m"].round(1).astype(str) + " / " + df["apparent_temperature"].round(1).astype(str) + " C",
            "降雨概率": df["precipitation_probability"].astype(int).astype(str) + "%",
            "降雨量": df["precipitation"].round(1),
            "风速": df["wind_speed_10m"].round(1).astype(str) + " km/h",
        }
    )


def forecast_grid(weather: dict) -> pd.DataFrame:
    hourly = weather["hourly"]
    df = pd.DataFrame(hourly).head(12).copy()
    times = pd.to_datetime(df["time"]).dt.strftime("%H:%M").tolist()
    rows = {
        "天气": [weather_text(int(code))[0] for code in df["weather_code"]],
        "气温": [f"{value:.1f} C" for value in df["temperature_2m"]],
        "体感": [f"{value:.1f} C" for value in df["apparent_temperature"]],
        "降雨": [f"{value:.1f} mm" for value in df["precipitation"]],
        "风速": [f"{value:.1f} km/h" for value in df["wind_speed_10m"]],
    }
    return pd.DataFrame(rows, index=times).T


def draw_line_feature(feature: dict, map_obj: folium.Map) -> None:
    properties = feature.get("properties") or {}
    geometry = feature.get("geometry") or {}
    name = properties.get("name") or properties.get("ref") or "地铁线路"
    color = metro_line_color(name)
    geometry_type = geometry.get("type")
    coordinates = geometry.get("coordinates") or []

    if geometry_type == "LineString":
        segments = [coordinates]
    elif geometry_type == "MultiLineString":
        segments = coordinates
    else:
        raise ValueError(f"不支持的线路类型: {geometry_type}")

    for segment in segments:
        if "22号线" in name and any(lat > LINE_22_OPEN_MAX_LAT for _, lat in segment):
            continue
        points = [(lat, lon) for lon, lat in segment]
        folium.PolyLine(points, color=color, weight=4, opacity=0.85, tooltip=name).add_to(map_obj)


def draw_manual_operating_segments(map_obj: folium.Map) -> None:
    line_14_points = [(lat, lon) for _, lat, lon in LINE_14_PHASE2_POINTS]
    folium.PolyLine(
        line_14_points,
        color=METRO_LINE_COLORS["14号线"],
        weight=4,
        opacity=0.9,
        tooltip="广州地铁14号线（二期运营段：乐嘉路-嘉禾望岗）",
    ).add_to(map_obj)


def station_from_click(click_info: dict | None, metro_stations: pd.DataFrame) -> pd.Series | None:
    if not click_info:
        return None
    clicked = click_info.get("last_object_clicked")
    if not clicked:
        return None
    lat = clicked.get("lat")
    lon = clicked.get("lng")
    if lat is None or lon is None:
        return None
    station, distance = nearest_row(metro_stations, float(lat), float(lon))
    if distance > 0.08:
        return None
    return station


def render_map(metro_lines: dict, metro_stations: pd.DataFrame, selected_station: pd.Series, nearest_monitor: pd.Series) -> dict | None:
    city_map = folium.Map(location=[float(selected_station["lat"]), float(selected_station["lon"])], zoom_start=13, tiles="CartoDB positron")

    for feature in metro_lines.get("features", []):
        draw_line_feature(feature, city_map)
    draw_manual_operating_segments(city_map)

    station_group = folium.FeatureGroup(name="地铁站点", show=True)
    for row in metro_stations.itertuples(index=False):
        is_selected = row.id == selected_station["id"]
        folium.CircleMarker(
            location=[float(row.lat), float(row.lon)],
            radius=8 if is_selected else 4,
            color="#dc2626" if is_selected else "#1d4ed8",
            fill=True,
            fill_opacity=0.95 if is_selected else 0.75,
            tooltip=f"地铁站: {row.name}",
        ).add_to(station_group)
    station_group.add_to(city_map)

    folium.Marker(
        location=[float(nearest_monitor["lat"]), float(nearest_monitor["lon"])],
        tooltip=f"最近空气监测站: {nearest_monitor['name']}",
        icon=folium.Icon(color="green", icon="info-sign"),
    ).add_to(city_map)

    folium.LayerControl(collapsed=True).add_to(city_map)
    return st_folium(
        city_map,
        key="destination_map",
        height=610,
        use_container_width=True,
        returned_objects=["last_object_clicked", "last_object_clicked_tooltip"],
    )


def render_destination_weather(station: pd.Series, monitor: pd.Series, monitor_distance: float, weather: dict) -> pd.DataFrame:
    current = weather["current"]
    label, advice, category = weather_text(int(current["weather_code"]))
    style = weather_style(category)
    updated = current.get("time")
    if updated:
        updated = datetime.fromisoformat(updated).strftime("%m-%d %H:%M")
    else:
        updated = "未知"

    st.markdown(
        f"""
        <div style="padding:22px 24px;border-radius:8px;background:{style['bg']};color:{style['fg']};margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;gap:18px;">
          <div>
            <div style="font-size:16px;opacity:0.9;">{station['name']} 目的地天气</div>
            <div style="font-size:44px;font-weight:750;line-height:1.12;">{label}</div>
            <div style="font-size:22px;font-weight:650;margin-top:6px;">{advice}</div>
          </div>
          <div style="min-width:92px;height:92px;border-radius:8px;background:{style['badge']};display:flex;align-items:center;justify-content:center;font-size:34px;font-weight:800;color:{style['fg']};">
            {WEATHER_ICON.get(category, "?")}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("当前温度", f"{current['temperature_2m']:.1f} C")
    col2.metric("体感温度", f"{current['apparent_temperature']:.1f} C")
    col3.metric("当前降雨", f"{current['precipitation']:.1f} mm")
    col4.metric("风速", f"{current['wind_speed_10m']:.1f} km/h")

    st.caption(f"天气取自最近空气监测站：{monitor['name']}，距离地铁站约 {monitor_distance:.1f} 公里。预报更新时间：{updated}。")
    st.markdown(
        """
        <div class="forecast-title-row">
          <h3>未来 12 小时天气预报</h3>
          <span class="forecast-help">拖动表格底部横条查看更多信息</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.dataframe(forecast_grid(weather), use_container_width=True, height=230)


def main() -> None:
    st.set_page_config(page_title="广州市精确天气", page_icon="GZ", layout="wide")
    inject_styles()
    metro_stations = load_metro_stations()
    aqicn_stations = load_aqicn_stations()
    metro_lines = load_metro_lines()

    if "selected_station_id" not in st.session_state:
        st.session_state.selected_station_id = metro_stations.iloc[0]["id"]

    labels = metro_stations["label"].tolist()
    selected_index = int(metro_stations.index[metro_stations["id"] == st.session_state.selected_station_id][0])

    left, right = st.columns([0.46, 0.54], gap="large")
    with left:
        st.title("广州市精确天气")
        st.caption("先选一个目的地地铁站，页面会显示站点附近的实时天气、晴雨类别和未来小时预报。")
        selected_label = st.selectbox("目的地搜索", labels, index=selected_index)
        st.session_state.selected_station_id = metro_stations.loc[metro_stations["label"] == selected_label, "id"].iloc[0]

    selected_station = metro_stations.loc[metro_stations["id"] == st.session_state.selected_station_id].iloc[0]
    nearest_monitor, monitor_distance = nearest_row(aqicn_stations, float(selected_station["lat"]), float(selected_station["lon"]))

    with right:
        st.markdown('<div class="map-hint">点击地图上的地铁站也可以切换目的地</div>', unsafe_allow_html=True)
        map_result = render_map(metro_lines, metro_stations, selected_station, nearest_monitor)

    clicked_station = station_from_click(map_result, metro_stations)
    if clicked_station is not None and clicked_station["id"] != st.session_state.selected_station_id:
        st.session_state.selected_station_id = clicked_station["id"]
        st.rerun()

    selected_station = metro_stations.loc[metro_stations["id"] == st.session_state.selected_station_id].iloc[0]
    nearest_monitor, monitor_distance = nearest_row(aqicn_stations, float(selected_station["lat"]), float(selected_station["lon"]))
    weather = fetch_weather(float(nearest_monitor["lat"]), float(nearest_monitor["lon"]))

    with left:
        render_destination_weather(selected_station, nearest_monitor, monitor_distance, weather)


if __name__ == "__main__":
    main()
