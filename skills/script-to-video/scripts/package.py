"""Collect the finished project into deliver/<slug>/ and deliver/<slug>.zip, with an MD5 for the video (free).

Includes: the final video (+ .srt captions), thumbnails, shotlist.json, prompts/, pictures/, clips/, voice/, music/,
PRODUCTION-LOG.md and SOCIAL.md (if present), and a README listing what is inside.
usage: package.py SHOTLIST.json FINAL.mp4 [--extra file ...]
"""
import os, sys, shutil, hashlib, zipfile, argparse, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_shotlist, probe_duration


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("shotlist"); ap.add_argument("final"); ap.add_argument("--extra", nargs="*", default=[])
    A = ap.parse_args()
    S = load_shotlist(A.shotlist); root = S["_root"]; slug = S.get("slug", "video")
    dst = os.path.join(root, "deliver", slug)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)
    vid = os.path.join(dst, f"{slug}.mp4"); shutil.copy2(A.final, vid)
    srt = os.path.splitext(A.final)[0] + ".srt"
    if os.path.exists(srt):
        shutil.copy2(srt, os.path.join(dst, f"{slug}.srt"))
    for d in ("pictures", "clips", "voice", "music", "prompts", "thumbnails", "stems"):
        src = os.path.join(root, d)
        if os.path.isdir(src) and os.listdir(src):
            shutil.copytree(src, os.path.join(dst, d))
    for f in ["BRIEF.md", "shotlist.json", "PRODUCTION-LOG.md", "SOCIAL.md", "layout-guide.png"] + A.extra:
        p = f if os.path.isabs(f) else os.path.join(root, f)
        if os.path.exists(p):
            shutil.copy2(p, dst)
    m = md5(vid)
    inside = sorted(os.path.relpath(os.path.join(a, f), dst) for a, _, fs in os.walk(dst) for f in fs)
    open(os.path.join(dst, "README.txt"), "w").write(
        f"{S.get('title', slug)}\n\nVideo: {slug}.mp4  ({probe_duration(vid):.2f} s, {S['_fmt']['W']}x{S['_fmt']['H']})\nMD5: {m}\n\n"
        "Contents:\n" + "\n".join("  " + i for i in inside) + "\n")
    z = os.path.join(root, "deliver", f"{slug}.zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for a, _, fs in os.walk(dst):
            for f in fs:
                p = os.path.join(a, f); zf.write(p, os.path.join(slug, os.path.relpath(p, dst)))
    print(json.dumps({"folder": dst, "zip": z, "video_md5": m, "files": len(inside) + 1}, indent=1))


if __name__ == "__main__":
    main()
