"""
Extended auto-install loop: run until vite starts cleanly.
"""
import json, tarfile, io, urllib.request, ssl, subprocess, re
from pathlib import Path

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE
REGISTRY = "https://registry.npmjs.org"
NM = Path("d:/Project/SmartMicrogrid/frontend/node_modules")
NODE = r"C:\Users\palan\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
VITE = str(NM / "vite" / "bin" / "vite.js")


def install(name):
    if name.startswith("@"):
        scope, pkg = name.split("/", 1)
        dest = NM / scope / pkg
    else:
        dest = NM / name
    if dest.exists():
        return False
    enc = name.replace("/", "%2F")
    req = urllib.request.Request(f"{REGISTRY}/{enc}", headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, context=ssl_ctx, timeout=30) as r:
        meta = json.loads(r.read())
    v = meta["dist-tags"]["latest"]
    tarball = meta["versions"][v]["dist"]["tarball"]
    dest.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(tarball, context=ssl_ctx, timeout=60) as r:
        data = r.read()
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        for m in tar.getmembers():
            if "/" in m.name:
                parts = m.name.split("/", 1)
                if parts[0] == "package" and len(parts) > 1:
                    m.name = parts[1]
                    t = dest / m.name
                    if m.isdir():
                        t.mkdir(parents=True, exist_ok=True)
                    elif m.isfile():
                        t.parent.mkdir(parents=True, exist_ok=True)
                        with tar.extractfile(m) as src:
                            t.write_bytes(src.read())
    print(f"  [OK] {name}@{v}", flush=True)
    return True


def find_missing(output):
    missing = set()
    for m in re.findall(r"Cannot find (?:module|package) '([^']+)'", output):
        if not m.startswith(".") and not m.startswith("/") and not m.startswith("node:"):
            missing.add(m)
    return missing


def try_vite(timeout=8):
    try:
        result = subprocess.run(
            [NODE, VITE, "--host", "0.0.0.0", "--port", "5173"],
            capture_output=True, text=True, timeout=timeout,
            cwd="d:/Project/SmartMicrogrid/frontend",
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired as e:
        return (e.stdout or "") + (e.stderr or "")
    except Exception as e:
        return str(e)


print("Running extended auto-install loop (up to 30 iterations)...\n")
for i in range(30):
    output = try_vite(timeout=8)
    missing = find_missing(output)
    if not missing:
        if "ready in" in output:
            print(f"\nSUCCESS! Vite starts cleanly after {i+1} iterations!")
        else:
            print(f"\nNo more missing modules but vite crashed for another reason:")
            print(output[-400:])
        break
    print(f"Iter {i+1}: installing {missing}", flush=True)
    for pkg in missing:
        try:
            install(pkg)
        except Exception as e:
            print(f"  [FAIL] {pkg}: {e}")
else:
    print("\nHit 30 iterations. Running final check...")

print("\n=== Final vite check ===")
out = try_vite(timeout=6)
print(out[:600])
