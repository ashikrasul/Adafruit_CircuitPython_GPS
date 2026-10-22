"""Turn simple_test.py output into an HTML map.

Usage: python3 plot_track.py gps_log.txt [track_map.html]
"""
import json
import re
import sys

log_path = sys.argv[1]
out_path = sys.argv[2] if len(sys.argv) > 2 else "track_map.html"

text = open(log_path).read()
lats = re.findall(r"Latitude:\s*(-?\d+\.\d+)", text)
lons = re.findall(r"Longitude:\s*(-?\d+\.\d+)", text)
points = [[float(a), float(b)] for a, b in zip(lats, lons)]
if not points:
    sys.exit("No Latitude/Longitude lines found.")

html = """<!doctype html>
<html><head><meta charset="utf-8"><title>GPS Track</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>html,body,#map{height:100%;margin:0}</style></head>
<body><div id="map"></div><script>
const pts = POINTS;
const map = L.map('map');
// OSM's own tile server blocks pages opened from a local file, so use these.
const satellite = L.tileLayer(
  'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
  {maxZoom: 22, maxNativeZoom: 19, attribution: 'Tiles &copy; Esri'});
const streets = L.tileLayer(
  'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png',
  {maxZoom: 22, maxNativeZoom: 20, attribution: '&copy; OpenStreetMap &copy; CARTO'});
satellite.addTo(map);
L.control.layers({'Satellite': satellite, 'Streets': streets}).addTo(map);
const line = L.polyline(pts, {color: 'red', weight: 3}).addTo(map);
pts.forEach(p => L.circleMarker(p, {radius: 2, color: 'blue'}).addTo(map));
L.marker(pts[0]).addTo(map).bindPopup('Start');
L.marker(pts[pts.length - 1]).addTo(map).bindPopup('End');
map.fitBounds(line.getBounds(), {maxZoom: 21});
</script></body></html>
""".replace("POINTS", json.dumps(points))

open(out_path, "w").write(html)
print(f"Wrote {len(points)} points to {out_path}")
