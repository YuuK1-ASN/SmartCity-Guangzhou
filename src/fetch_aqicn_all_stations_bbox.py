# -*- coding: utf-8 -*-
"""
抓取广州范围内的AQICN监测站，并保存到data/raw/aqicn_stations_bbox.csv。
运行前需要设置AQICN_TOKEN环境变量。
"""
import csv, time, requests
from pathlib import Path
from common import get_required_env

ROOT = Path(__file__).resolve().parents[1]
RAW  = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

GZ_BBOX = (22.8, 112.8, 24.1, 113.9)
CELL = 0.2

OUT_CSV = RAW / "aqicn_stations_bbox.csv"

def cells(minlat, minlon, maxlat, maxlon, step):
    lat = minlat
    while lat < maxlat - 1e-9:
        lon = minlon
        while lon < maxlon - 1e-9:
            yield (lat, lon, min(lat+step, maxlat), min(lon+step, maxlon))
            lon += step
        lat += step

def fetch_bounds_cell(a,b,x,y, token):
    url = f"https://api.waqi.info/map/bounds/?latlng={a},{b},{x},{y}&token={token}"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    j = r.json()
    if j.get("status") != "ok":
        raise RuntimeError(f"AQICN 返回异常: {j.get('data')}")
    return j.get("data", [])

def main():
    token = get_required_env("AQICN_TOKEN")
    print("抓取 AQICN 广州 bbox 内所有监测站 …")
    seen = set()
    rows = []
    for (a,b,x,y) in cells(*GZ_BBOX, CELL):
        data = fetch_bounds_cell(a,b,x,y, token)
        for it in data:
            uid = it.get("uid")
            if uid in seen: 
                continue
            seen.add(uid)
            name = (it.get("station") or {}).get("name","")
            lat  = it.get("lat")
            lon  = it.get("lon")
            if uid is None or lat is None or lon is None:
                continue
            rows.append((uid, name, lat, lon))
        time.sleep(0.2)

    rows.sort(key=lambda t: t[0])
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["uid","name","lat","lon"])
        w.writerows(rows)

    print(f"OK: {len(rows)} 站  ->  {OUT_CSV}")

if __name__ == "__main__":
    main()
