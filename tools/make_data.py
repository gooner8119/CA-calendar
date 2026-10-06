#!/usr/bin/env python3
"""아티팩트 db에서 내려받은 문서 폴더로 data.js 를 만든다.

사용법: python3 tools/make_data.py <events 폴더> <deals 폴더> <meta/status.json> [출력 data.js]
- events 폴더: 문서 하나당 <문서 id>.json (ArtifactData list 의 out_dir 결과)
- deals 폴더:  문서 하나당 <접수번호>.json
- status.json: meta/status 문서
"""
import json, os, sys

def load_dir(d):
    out = {}
    for f in sorted(os.listdir(d)):
        if f.endswith(".json"):
            doc = json.load(open(os.path.join(d, f), encoding="utf-8"))
            if isinstance(doc, dict) and set(doc) >= {"id", "data"} and isinstance(doc["data"], dict):
                doc = doc["data"]
            out[f[:-5]] = doc
    return out

def main():
    ev_dir, deal_dir, meta_path = sys.argv[1:4]
    out = sys.argv[4] if len(sys.argv) > 4 else "data.js"
    events = [dict(v, id=k) for k, v in load_dir(ev_dir).items()]
    events.sort(key=lambda e: (e.get("date", ""), e.get("name", "")))
    deals = load_dir(deal_dir)
    meta = json.load(open(meta_path, encoding="utf-8"))
    if set(meta) >= {"id", "data"}:
        meta = meta["data"]
    bad = [e["id"] for e in events if not e.get("date") or not e.get("code")]
    if bad:
        sys.exit("date/code 가 없는 일정: %s" % bad[:5])
    if len(events) < 50:
        sys.exit("일정이 %d건뿐입니다. 내려받기가 덜 된 것 같아 중단합니다." % len(events))
    snap = {"events": events, "deals": deals, "meta": meta, "at": meta.get("lastUpdate", "")}
    with open(out, "w", encoding="utf-8") as f:
        f.write("window.__SNAP=" + json.dumps(snap, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print("events %d, deals %d, at %s -> %s" % (len(events), len(deals), snap["at"], out))

if __name__ == "__main__":
    main()
