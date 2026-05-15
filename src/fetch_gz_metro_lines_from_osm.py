from __future__ import annotations
import json
import requests
from pathlib import Path
import pandas as pd
from common import RAW, GZ_BBOX, GZ_LINE_COLORS

OVERPASS_ENDPOINT = "https://overpass-api.de/api/interpreter"

OUT_LINES = RAW / "gz_metro_lines.geojson"
OUT_STATIONS = RAW / "gz_metro_stations.csv"

def overpass_query(q: str):
    response = requests.post(OVERPASS_ENDPOINT, data={"data": q}, timeout=60)
    response.raise_for_status()
    return response.json()

def build_bbox(b):
    return f"({b[1]},{b[0]},{b[3]},{b[2]})"

def fetch_lines_and_stations(bbox):
    bb = build_bbox(bbox)
    q_lines = f"""
[out:json][timeout:60];
rel{bb}["type"="route"]["route"="subway"];
out ids tags bb;
way(r);
out ids tags geom;
"""
    q_st = f"""
[out:json][timeout:60];
node{bb}["railway"="station"]["subway"="yes"];
out center tags;
"""
    j_lines = overpass_query(q_lines)
    j_st = overpass_query(q_st)

    features = []
    for el in j_lines.get("elements", []):
        if el.get("type") == "way" and "geometry" in el:
            name = el.get("tags", {}).get("name", "")
            line = el.get("tags", {}).get("ref", name)
            coords = [(p["lon"], p["lat"]) for p in el["geometry"]]
            color = None
            for k,v in GZ_LINE_COLORS.items():
                if k in name or k in line:
                    color = v
                    break
            features.append({
                "type":"Feature",
                "properties":{"name": name, "ref": line, "color": color},
                "geometry":{"type":"LineString","coordinates":coords}
            })

    Path(OUT_LINES).write_text(json.dumps({"type":"FeatureCollection","features":features}, ensure_ascii=False), encoding="utf-8")
    recs = []
    for el in j_st.get("elements", []):
        if el.get("type")=="node":
            tags = el.get("tags",{})
            recs.append({
                "id": el.get("id"),
                "name": tags.get("name",""),
                "lat": el.get("lat"),
                "lon": el.get("lon"),
                "line": tags.get("line","")
            })
    pd.DataFrame(recs).to_csv(OUT_STATIONS, index=False, encoding="utf-8-sig")

def main():
    print("抓取地铁线路与站点（OSM / Overpass）...")
    fetch_lines_and_stations(GZ_BBOX)
    print(f"线路保存 -> {OUT_LINES}")
    print(f"站点保存 -> {OUT_STATIONS}")

if __name__ == "__main__":
    main()
