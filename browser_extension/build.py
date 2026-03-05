import os, shutil, json

# Fix: always run from the folder where build.py lives
os.chdir(os.path.dirname(os.path.abspath(__file__)))

BROWSERS = {
    "edge": "manifest.edge.json",
    "firefox": "manifest.firefox.json"
}

FILES = ["background.js", "content.js", "popup.html", "popup.js" , "warning.html", "warning.js"]

for browser, manifest_src in BROWSERS.items():
    out = f"dist/{browser}"
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)

    # Copy manifest as manifest.json
    shutil.copy(manifest_src, os.path.join(out, "manifest.json"))

    # Copy all extension files
    for f in FILES:
        shutil.copy(f, os.path.join(out, f))

    # Copy icons folder
    shutil.copytree("icons", os.path.join(out, "icons"))

    print(f"✅ Built {browser} → dist/{browser}/")

print("\nDone! Load dist/edge/ in Edge, dist/firefox/ in Firefox.")