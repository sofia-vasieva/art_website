"""Build web image derivatives from the source images, and record them in gallery.json.

- detects the TRUE format (Instagram mislabels some JPEGs as .webp / .heic)
- applies EXIF orientation, then strips all metadata (GPS included)
- converts to sRGB via the embedded ICC profile when there is one
- emits thumb / display / full in both JPEG and WebP, never upscaling
- emits a tiny blurred placeholder (inline base64) for fast first paint
"""
import base64
import io
import json
import os
import sys

from PIL import Image, ImageCms, ImageOps

sys.stdout.reconfigure(encoding="utf-8")
Image.MAX_IMAGE_PIXELS = None

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIRS = [os.path.join(HERE, "posts"), os.path.join(HERE, "posts", "202207")]
GALLERY = os.path.join(HERE, "gallery.json")

SIZES = {"thumb": 640, "display": 1600, "full": 2560}
JPEG_Q = {"thumb": 82, "display": 86, "full": 88}
WEBP_Q = {"thumb": 78, "display": 80, "full": 82}

SRGB = ImageCms.createProfile("sRGB")


def locate(name):
    for d in SRC_DIRS:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(name)


def load_normalised(path):
    """Open, orient, convert to sRGB RGB, strip everything else."""
    im = Image.open(path)
    true_format = im.format
    im = ImageOps.exif_transpose(im)

    icc = im.info.get("icc_profile")
    if icc:
        try:
            src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
            im = ImageCms.profileToProfile(im, src, SRGB, outputMode="RGB")
        except Exception as exc:
            print("      ICC conversion skipped (%s)" % exc)
            im = im.convert("RGB")
    else:
        im = im.convert("RGB")

    clean = Image.new("RGB", im.size)
    clean.putdata(list(im.getdata()))
    return clean, true_format


def fit(im, long_edge):
    """Resize so the long edge is at most long_edge. Never upscales."""
    w, h = im.size
    scale = long_edge / max(w, h)
    if scale >= 1:
        return im.copy()
    return im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)


def placeholder(im):
    tiny = fit(im, 20)
    buf = io.BytesIO()
    tiny.save(buf, "JPEG", quality=40)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def main():
    data = json.load(open(GALLERY, encoding="utf-8"))
    for d in SIZES:
        os.makedirs(os.path.join(HERE, "images", d), exist_ok=True)

    total = 0
    for entry in data["entries"]:
        entry["images"] = []
        for idx, src_name in enumerate(entry["sourceImages"], start=1):
            path = locate(src_name)
            im, true_format = load_normalised(path)
            stem = entry["slug"] if len(entry["sourceImages"]) == 1 \
                else "%s-%d" % (entry["slug"], idx)

            ext_claimed = src_name.rsplit(".", 1)[-1].lower()
            note = "" if ext_claimed in ("jpg", "jpeg") and true_format == "JPEG" \
                else "  [.%s was really %s]" % (ext_claimed, true_format)
            print("  %-46s %5dx%-5d%s" % (stem, im.width, im.height, note))

            rec = {"w": im.width, "h": im.height, "lqip": placeholder(im)}
            for name, edge in SIZES.items():
                out = fit(im, edge)
                jpg = os.path.join(HERE, "images", name, stem + ".jpg")
                web = os.path.join(HERE, "images", name, stem + ".webp")
                out.save(jpg, "JPEG", quality=JPEG_Q[name],
                         optimize=True, progressive=True)
                out.save(web, "WEBP", quality=WEBP_Q[name], method=6)
                rec[name] = {
                    "jpg": "images/%s/%s.jpg" % (name, stem),
                    "webp": "images/%s/%s.webp" % (name, stem),
                    "w": out.width,
                    "h": out.height,
                }
            entry["images"].append(rec)
            total += 1

    with open(GALLERY, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    size_mb = sum(
        os.path.getsize(os.path.join(dp, f))
        for d in SIZES
        for dp, _, fs in os.walk(os.path.join(HERE, "images", d))
        for f in fs) / 1e6
    print("\n%d source images -> %d files, %.1f MB total"
          % (total, total * len(SIZES) * 2, size_mb))


if __name__ == "__main__":
    main()
