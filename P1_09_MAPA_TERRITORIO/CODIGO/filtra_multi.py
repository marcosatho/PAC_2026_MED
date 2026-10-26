import json, os
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mapa_datos.json")
d = json.load(open(p, encoding="utf-8"))
n0 = len(d["multi_geo"]["features"])
d["multi_geo"]["features"] = [f for f in d["multi_geo"]["features"] if f["properties"]["b"] > 1 or f["properties"]["c"] > 1]
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("features multi:", n0, "->", len(d["multi_geo"]["features"]), "| MB:", round(os.path.getsize(p) / 1048576, 2),
      "| multi_geo MB:", round(len(json.dumps(d["multi_geo"], separators=(",", ":"))) / 1048576, 2))
