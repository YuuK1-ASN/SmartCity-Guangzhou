# 广州市精确天气

这是一个面向广州出行的网页。由于广州市面积较大且天气多变，经常遇到目的地和现在所在地天气状况不一致的情况，但目前主流天气预报app几乎都没有精确查看精确的目的地天气能力，专业气象网页如windy则不易精确定位目的地地铁站。于是我编写了一个网页，用户可以搜索或点击目的地地铁站，页面会自动找到附近空气监测站，并显示该位置的实时天气、晴雨类别和未来小时预报。方便用户的出行。

## 技术架构

- Python负责读取本地数据，并请求Open-Meteo天气预报接口。
- Streamlit负责网页界面。
- Folium负责地图展示。
- CSV和GeoJSON保存已经抓取好的广州地铁与空气监测站数据。

## 本地运行方法

### Windows新手配置教程

1. 安装Python3.13。
   可以去Python官网下载安装包。安装时请勾选 `Add python.exe to PATH`。

2. 打开命令提示符或PowerShell，进入项目文件夹。

```powershell
cd "你的项目文件夹路径"
```

如果项目放在桌面，可以类似这样：

```powershell
cd "C:\Users\你的用户名\Desktop\SmartCity-Guangzhou"
```

3. 创建虚拟环境。
   虚拟环境相当于给这个项目单独准备一个Python小房间，避免和电脑里其他Python项目互相影响。

```powershell
py -3.13 -m venv .venv
```

4. 安装项目依赖。

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

如果下载很慢，可以先设置清华源：

```powershell
.\.venv\Scripts\python.exe -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

5. 启动网页。

```powershell
.\.venv\Scripts\python.exe -m streamlit run webapp\app_main.py
```

6. 浏览器打开终端里显示的网址。
   通常是：

```text
http://localhost:8501
```

### 已经配置过虚拟环境时

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run webapp\app_main.py
```

天气数据来自Open-Meteo，不需要token。AQICN token只在重新抓取空气监测站列表时使用。

## 数据更新方法

重新抓取广州地铁数据：

```powershell
.\.venv\Scripts\python.exe src\fetch_gz_metro_lines_from_osm.py
```

重新抓取空气监测站：

```powershell
$env:AQICN_TOKEN="AQICN_TOKEN值"
.\.venv\Scripts\python.exe src\fetch_aqicn_all_stations_bbox.py
```

## 部署方法

可以部署到Streamlit Community Cloud。入口文件填写：

```text
webapp/app_main.py
```

部署页面本身不需要配置 token。

## 测试方法

```powershell
.\.venv\Scripts\python.exe -m compileall src webapp
```

网页人工检查：

```powershell
.\.venv\Scripts\python.exe -m streamlit run webapp\app_main.py
```

## 已完成功能

- 支持搜索广州地铁站。
- 支持点击地图上的地铁站切换目的地。
- 自动找到目的地附近的空气监测站。
- 展示晴雨类别、出行建议、当前温度、体感温度、降雨和风速。
- 展示未来12小时天气预报，并直接写出天气情况。
