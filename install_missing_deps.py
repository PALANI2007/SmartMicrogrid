"""
Install specific missing transitive dependencies for vite + react + tailwind.
"""
import json, os, tarfile, io, urllib.request, ssl, shutil
from pathlib import Path

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

REGISTRY = "https://registry.npmjs.org"
FRONTEND = Path("d:/Project/SmartMicrogrid/frontend")
NM = FRONTEND / "node_modules"

def fetch(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, context=ssl_ctx, timeout=30) as r:
        return json.loads(r.read())

def get_tarball_url(name, version=None):
    enc = name.replace("/", "%2F")
    meta = fetch(f"{REGISTRY}/{enc}")
    v = version or meta["dist-tags"]["latest"]
    if v not in meta["versions"]:
        # find closest
        vs = [x for x in meta["versions"] if x.startswith(v.split(".")[0])]
        v = vs[-1] if vs else meta["dist-tags"]["latest"]
    pkg = meta["versions"][v]
    return pkg["dist"]["tarball"], v

def install_pkg(name, version=None):
    if name.startswith("@"):
        scope, pkg = name.split("/", 1)
        dest = NM / scope / pkg
    else:
        dest = NM / name
    
    if dest.exists():
        print(f"  [EXISTS] {name}")
        return
    
    print(f"  [GET] {name}@{version or 'latest'}")
    url, v = get_tarball_url(name, version)
    dest.mkdir(parents=True, exist_ok=True)
    
    with urllib.request.urlopen(url, context=ssl_ctx, timeout=60) as r:
        data = r.read()
    
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        for m in tar.getmembers():
            if "/" in m.name:
                parts = m.name.split("/", 1)
                if parts[0] == "package" and len(parts) > 1:
                    m.name = parts[1]
                    target = dest / m.name
                    if m.isdir():
                        target.mkdir(parents=True, exist_ok=True)
                    elif m.isfile():
                        target.parent.mkdir(parents=True, exist_ok=True)
                        with tar.extractfile(m) as src:
                            target.write_bytes(src.read())
    print(f"  [OK] {name}@{v}")

# Critical missing packages for vite 4.x + @vitejs/plugin-react 4.x
MISSING = [
    # esbuild for Windows x64
    ("esbuild", "0.18.20"),
    ("@esbuild/win32-x64", "0.18.20"),
    # rollup  
    ("rollup", "3.29.5"),
    ("@rollup/rollup-win32-x64-msvc", "4.47.0"),
    # postcss deps
    ("picocolors", None),
    ("source-map-js", None),
    ("nanoid", None),
    # react refresh for vite plugin
    ("react-refresh", "0.14.2"),
    # tailwind deps
    ("glob", None),
    ("fast-glob", None),
    ("micromatch", None),
    ("normalize-path", None),
    ("picomatch", None),
    ("merge2", None),
    ("@alloc/quick-lru", None),
    ("readdirp", None),
    ("anymatch", None),
    ("braces", None),
    ("fill-range", None),
    ("to-regex-range", None),
    ("is-number", None),
    ("chokidar", None),
    ("fsevents", None),
    ("is-binary-path", None),
    ("binary-extensions", None),
    # autoprefixer/postcss
    ("fraction.js", None),
    ("normalize-range", None),
    ("browserslist", None),
    ("caniuse-lite", None),
    ("electron-to-chromium", None),
    ("node-releases", None),
    ("update-browserslist-db", None),
    ("escalade", None),
    # recharts deps
    ("d3-array", None),
    ("d3-color", None),
    ("d3-format", None),
    ("d3-interpolate", None),
    ("d3-path", None),
    ("d3-scale", None),
    ("d3-shape", None),
    ("d3-time", None),
    ("d3-time-format", None),
    ("victory-vendor", None),
    ("clsx", None),
    ("eventemitter3", None),
    ("lodash", None),
    # react-router-dom
    ("@remix-run/router", None),
    ("react-router", None),
    # react-i18next deps
    ("html-parse-stringify", None),
    ("void-elements", None),
    # lucide-react - already top-level but needs to be standalone
]

print(f"Installing {len(MISSING)} transitive packages...\n")
for name, ver in MISSING:
    try:
        install_pkg(name, ver)
    except Exception as e:
        print(f"  [SKIP] {name}: {e}")

print("\nDone!")
