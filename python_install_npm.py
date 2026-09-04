"""
Enhanced npm package installer - installs packages with their dependencies.
Uses Python's urllib to bypass undici network issues.
"""
import json
import os
import sys
import tarfile
import io
import urllib.request
import ssl
import shutil
from pathlib import Path
import re

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

REGISTRY = "https://registry.npmjs.org"
FRONTEND = Path("d:/Project/SmartMicrogrid/frontend")
NODE_MODULES = FRONTEND / "node_modules"
BIN_DIR = NODE_MODULES / ".bin"

installed = {}  # name -> version

def fetch_json(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, context=ssl_ctx, timeout=30) as r:
        return json.loads(r.read())

def get_package_meta(name):
    enc = name.replace("/", "%2F")
    return fetch_json(f"{REGISTRY}/{enc}")

def resolve_version(info, spec):
    """Resolve a version spec to an actual version."""
    if not spec or spec in ("*", "latest"):
        return info["dist-tags"]["latest"]
    if spec in info["dist-tags"]:
        return info["dist-tags"][spec]
    
    # Handle ranges
    clean = re.sub(r'^[\^~>=<]', '', spec).strip()
    clean = re.sub(r' .*$', '', clean)  # handle "^1.0 || ^2.0" - just take first
    
    versions = list(info["versions"].keys())
    
    # Exact match
    if clean in info["versions"]:
        return clean
    
    # Find best matching semver
    major = clean.split(".")[0] if clean else "0"
    candidates = [v for v in versions if v.startswith(major + ".") and not ("-" in v and "alpha" not in v and "beta" not in v)]
    if candidates:
        return candidates[-1]
    
    return info["dist-tags"].get("latest", versions[-1])

def download_and_extract(tarball_url, dest_dir):
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    with urllib.request.urlopen(tarball_url, context=ssl_ctx, timeout=60) as r:
        data = r.read()
    
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        for member in tar.getmembers():
            # Strip leading 'package/' prefix
            if "/" in member.name:
                parts = member.name.split("/", 1)
                if parts[0] == "package":
                    member.name = parts[1] if len(parts) > 1 else member.name
                else:
                    continue
            else:
                continue
            
            target = dest_dir / member.name
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                target.parent.mkdir(parents=True, exist_ok=True)
                with tar.extractfile(member) as src:
                    target.write_bytes(src.read())

def install(name, spec="latest", depth=0, parent=None):
    """Install a package and its dependencies."""
    indent = "  " * depth
    
    if depth > 5:
        return  # prevent infinite recursion
    
    # Check if already installed
    if name in installed:
        return
    
    # Platform packages - skip if wrong platform
    skip_names = [
        "@esbuild/linux", "@esbuild/darwin", "@esbuild/android", "@esbuild/freebsd",
        "@esbuild/netbsd", "@esbuild/openbsd", "@esbuild/sunos",
        "@rollup/rollup-linux", "@rollup/rollup-darwin", "@rollup/rollup-android",
        "@rollup/rollup-freebsd",
    ]
    for s in skip_names:
        if name.startswith(s):
            print(f"{indent}[SKIP-PLATFORM] {name}")
            return
    
    print(f"{indent}[INSTALL] {name}@{spec}")
    
    try:
        meta = get_package_meta(name)
    except Exception as e:
        print(f"{indent}[ERROR] Cannot fetch {name}: {e}")
        return
    
    version = resolve_version(meta, spec)
    pkg = meta["versions"].get(version)
    
    if not pkg:
        # Try latest
        version = meta["dist-tags"]["latest"]
        pkg = meta["versions"][version]
    
    installed[name] = version
    
    # Get destination
    if name.startswith("@"):
        scope, pkg_name = name.split("/", 1)
        dest = NODE_MODULES / scope / pkg_name
    else:
        dest = NODE_MODULES / name
    
    if dest.exists():
        print(f"{indent}[EXISTS] {name}@{version}")
        return
    
    # Download
    tarball = pkg.get("dist", {}).get("tarball")
    if tarball:
        try:
            download_and_extract(tarball, dest)
            print(f"{indent}[OK] {name}@{version}")
        except Exception as e:
            print(f"{indent}[ERROR] Download failed for {name}: {e}")
            return
    
    # Install bin scripts
    if "bin" in pkg:
        BIN_DIR.mkdir(exist_ok=True)
        bins = pkg["bin"]
        if isinstance(bins, str):
            bins = {name.split("/")[-1]: bins}
        for bin_name, bin_path in bins.items():
            bin_file = dest / bin_path.lstrip("./")
            link = BIN_DIR / bin_name
            if not link.exists() and bin_file.exists():
                # Create a .cmd wrapper
                cmd_link = BIN_DIR / (bin_name + ".cmd")
                cmd_link.write_text(
                    f'@node "%~dp0..\\{name.replace("/", chr(92))}\\{bin_path.lstrip("./")}" %*\n'
                )
    
    # Install dependencies
    deps = pkg.get("dependencies", {})
    for dep_name, dep_spec in deps.items():
        if dep_name not in installed:
            install(dep_name, dep_spec, depth + 1, name)

def main():
    NODE_MODULES.mkdir(exist_ok=True)
    BIN_DIR.mkdir(exist_ok=True)
    
    with open(FRONTEND / "package.json") as f:
        pkg = json.load(f)
    
    # All deps needed for dev
    all_deps = {}
    all_deps.update(pkg.get("dependencies", {}))
    all_deps.update(pkg.get("devDependencies", {}))
    
    print(f"Installing {len(all_deps)} top-level packages with deps...\n")
    
    for name, spec in all_deps.items():
        install(name, spec, 0)
    
    print(f"\n✅ Installed {len(installed)} packages total")
    
    # Write .bin wrappers for key tools
    key_bins = {
        "vite": ("vite", "node_modules/vite/bin/vite.js"),
        "tsc": ("typescript", "node_modules/typescript/bin/tsc"),
    }
    for bin_name, (_, bin_path) in key_bins.items():
        cmd = BIN_DIR / (bin_name + ".cmd")
        if not cmd.exists():
            full = FRONTEND / bin_path
            if full.exists():
                cmd.write_text(f'@node "%~dp0..\\{bin_path.replace("/", chr(92))}" %*\n')

if __name__ == "__main__":
    main()
