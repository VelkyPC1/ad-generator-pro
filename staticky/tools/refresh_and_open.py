"""Po každom generovaní: poskladá manifest z FS (všetky bannery, nie len posledný --templates beh)
a otvorí bannery v dashboarde. Volané automaticky z generate_ads.py.
Použitie: python3 tools/refresh_and_open.py <outputs_dir> [--no-open]
"""
import sys, os, re, json, glob, subprocess, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

def rebuild_manifest(outputs_dir: Path):
    """Prepíše manifest.json kompletným zoznamom PNG z FS (fix: --templates prepisuje len časť)."""
    old = {}
    mp = outputs_dir / "manifest.json"
    if mp.exists():
        try: old = json.loads(mp.read_text(encoding="utf-8"))
        except Exception: old = {}
    # Údaje o generovaní (model, provider, rozlíšenie, cena) zo starého manifestu zachovať — FS ich nepozná
    keep = {}
    for r in old.get("results", []):
        extra = {k: r[k] for k in ("model", "provider", "tier", "cost_usd") if k in r}
        if extra and r.get("file"):
            keep[os.path.abspath(r["file"])] = extra
    results = []
    for png in sorted(glob.glob(str(outputs_dir / "*" / "*_v*_img*.png"))):
        base = os.path.basename(png)
        if "_clean" in base:
            continue
        folder = os.path.basename(os.path.dirname(png))         # napr. 201-premium-dokaz-kalu-1x1
        m = re.match(r"(\d+)-(.+)", folder)
        if not m:
            continue
        vm = re.search(r"_(v\d+_img\d+)\.png$", base)
        # Vizuálny štýl zo sidecar súboru, ktorý zapísal generate_ads.py (staré bannery ho nemajú)
        style_file = Path(os.path.dirname(png)) / "visual-style.txt"
        style_id = style_file.read_text(encoding="utf-8").strip() if style_file.exists() else None
        results.append({
            "template": int(m.group(1)),
            "name": m.group(2),
            "variation": vm.group(1) if vm else "v1_img1",
            "file": os.path.abspath(png),
            "visual_style": style_id,
            **keep.get(os.path.abspath(png), {}),
        })
    if not results:
        return False
    brand = old.get("brand")
    if not brand or brand == "unknown":
        parts = outputs_dir.parts
        brand = parts[parts.index("brands") + 1] if "brands" in parts else "unknown"
    manifest = {
        "brand": brand,
        "provider": old.get("provider", "google"),
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "resolution": old.get("resolution", "1K"),
        "total_generated": len(results),
        "total_failed": old.get("total_failed", 0),
        "visual_styles": sorted({r["visual_style"] for r in results if r.get("visual_style")}),
        "results": sorted(results, key=lambda r: r["template"]),
    }
    mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ↻ Manifest prestavaný z FS: {len(results)} bannerov ({[r['template'] for r in manifest['results']]})")
    return True

def refresh_and_open(outputs_dir: str, do_open=True):
    outputs_dir = Path(outputs_dir).resolve()
    rebuild_manifest(outputs_dir)
    subprocess.run(["python3", "tools/build_dashboard.py"], cwd=REPO, check=False)
    if do_open:
        subprocess.run(["bash", "tools/serve_dashboard.sh"], cwd=REPO, check=False)
    else:
        print("  (dashboard prestavaný, neotváram — --no-open)")

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--no-open"]
    refresh_and_open(args[0], do_open="--no-open" not in sys.argv)
