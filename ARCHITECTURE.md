# 架构说明

## 文件职责

- `webapp/app_main.py`：Streamlit网页入口，负责搜索地铁站、匹配最近监测站、请求天气预报、渲染小时预报和地图。
- `src/common.py`：保存项目路径、广州范围、线路颜色和通用环境变量读取函数。
- `src/fetch_gz_metro_lines_from_osm.py`：从OpenStreetMap Overpass接口抓取广州地铁线路和站点。
- `src/fetch_aqicn_all_stations_bbox.py`：从AQICN接口抓取广州范围内的空气监测站。
- `启动网页.bat`：Windows下双击启动网页，会自动创建虚拟环境并安装依赖。
- `data/raw/gz_metro_lines.geojson`：广州地铁线路数据。
- `data/raw/gz_metro_stations.csv`：广州地铁站点数据。
- `data/raw/aqicn_stations_bbox.csv`：广州及周边空气监测站数据。
- `requirements.txt`：运行网页需要的Python依赖。

## 调用关系

`webapp/app_main.py`直接读取`data/raw`里的CSV和GeoJSON文件。用户搜索或点击地铁站后，网页可以计算最近的空气监测站，再用该监测站的经纬度请求Open-Meteo天气接口，把当前天气和小时预报展示出来。

抓取脚本只负责更新`data/raw`数据，不参与网页运行。网页可以在不重新抓取数据的情况下直接打开已有数据。
