"""Generate index.html and one static page per painting from gallery.json.

Pages are plain HTML so the site works with JavaScript disabled and each
piece has its own shareable URL.
"""
import html
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GALLERY = os.path.join(HERE, "gallery.json")

TAGLINE = ("Watercolour paintings of galaxies, nebulae and other deep-sky "
           "objects.")

SECTIONS = [
    ("deepsky", "Deep sky", ""),
    ("other", "Other work", ""),
    ("process", "Process", "How some of these are built up."),
]


def e(s):
    return html.escape(s or "", quote=True)


def head(title, desc, prefix, extra=""):
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<link rel="stylesheet" href="%sassets/style.css">
%s</head>
<body>
""" % (e(title), e(desc), prefix, extra)


def foot(data, prefix, with_js=False):
    js = '<script src="%sassets/app.js" defer></script>' % prefix if with_js else ""
    return """<footer class="site-foot"><div class="wrap">
<p>%s</p>
<p><a href="%s">Instagram</a> &nbsp;&middot;&nbsp; <a href="%s">YouTube</a></p>
</div></footer>
%s</body>
</html>
""" % (e(data["copyright"]), e(data["instagram"]), e(data["youtube"]), js)


def meta_line(entry):
    bits = [b for b in (entry.get("medium"), entry.get("size")) if b]
    return " &middot; ".join(e(b) for b in bits)


def card(entry, prefix):
    im = entry["images"][0]
    ratio = (im["h"] / im["w"] * 100) if im["w"] else 75
    alt = "%s, watercolour painting by Sofia Vasieva" % entry["title"]
    return """<a class="card" href="%spaintings/%s.html"
   data-display="%s%s" data-title="%s" data-alt="%s">
  <picture>
    <source type="image/webp" srcset="%s%s">
    <img class="card-img" src="%s%s" width="%d" height="%d" alt="%s" loading="lazy"
         style="background-image:url(%s);aspect-ratio:%d/%d">
  </picture>
  <div class="card-body">
    <h3 class="card-title">%s</h3>
    <p class="card-meta">%s</p>
  </div>
</a>
""" % (prefix, e(entry["slug"]),
       prefix, e(im["display"]["jpg"]), e(entry["title"]), e(alt),
       prefix, e(im["thumb"]["webp"]),
       prefix, e(im["thumb"]["jpg"]), im["thumb"]["w"], im["thumb"]["h"], e(alt),
       im["lqip"], im["w"], im["h"],
       e(entry["title"]), meta_line(entry) or "&nbsp;")


def caption_html(text):
    out = []
    for para in [p for p in text.split("\n") if p.strip()]:
        out.append("<p>%s</p>" % e(para.strip()))
    return "\n".join(out)


def build_index(data):
    entries = data["entries"]
    parts = [head("%s — watercolour paintings of deep-sky objects" % data["artist"],
                  TAGLINE, "")]
    parts.append("""<header class="site-head"><div class="wrap">
<h1 class="site-title">%s</h1>
<p class="site-tagline">%s</p>
<nav class="site-links">
  <a href="#deepsky">Deep sky</a>
  <a href="#other">Other work</a>
  <a href="#about">About</a>
  <a href="%s">Instagram</a>
  <a href="%s">YouTube</a>
</nav>
</div></header>
<main>
""" % (e(data["artist"]), e(TAGLINE), e(data["instagram"]), e(data["youtube"])))

    for key, label, note in SECTIONS:
        sel = [x for x in entries if x["section"] == key]
        if not sel:
            continue
        parts.append('<section class="section" id="%s"><div class="wrap">' % key)
        parts.append('<div class="section-head"><h2>%s</h2><span class="count">%d</span></div>'
                     % (e(label), len(sel)))
        if note:
            parts.append('<p class="section-note">%s</p>' % e(note))
        parts.append('<div class="grid">')
        parts += [card(x, "") for x in sel]
        parts.append("</div></div></section>")

    about = data.get("about", "").strip()
    parts.append('<section class="section" id="about"><div class="wrap">')
    parts.append('<div class="section-head"><h2>About</h2></div>')
    if about:
        parts.append('<div class="about">%s</div>' % caption_html(about))
    else:
        parts.append('<div class="about about-stub">This section is still to be '
                     'written.</div>')
    parts.append("</div></section>")
    parts.append("</main>")
    parts.append(foot(data, "", with_js=True))

    path = os.path.join(HERE, "index.html")
    open(path, "w", encoding="utf-8").write("".join(parts))
    return path


def build_piece(data, entry, prev_e, next_e):
    desc = (entry["caption"].split("\n")[0] or entry["title"])[:180]
    parts = [head("%s — %s" % (entry["title"], data["artist"]), desc, "../")]
    parts.append('<div class="wrap"><a class="back" href="../index.html#%s">&larr; All work</a></div>'
                 % e(entry["section"]))
    parts.append('<main class="piece"><div class="wrap">')

    for i, im in enumerate(entry["images"]):
        cls = "piece-figure" + (" piece-extra" if i else "")
        alt = "%s, watercolour painting by Sofia Vasieva" % entry["title"]
        parts.append("""<figure class="%s">
<picture><source type="image/webp" srcset="../%s">
<img src="../%s" width="%d" height="%d" alt="%s" %s></picture>
</figure>
""" % (cls, e(im["display"]["webp"]), e(im["display"]["jpg"]),
       im["display"]["w"], im["display"]["h"], e(alt),
       'loading="lazy"' if i else ""))

    parts.append("<h1>%s</h1>" % e(entry["title"]))
    ml = meta_line(entry)
    if ml:
        parts.append('<p class="piece-meta">%s</p>' % ml)
    parts.append('<div class="piece-caption">%s</div>' % caption_html(entry["caption"]))

    parts.append('<nav class="piece-nav">')
    if prev_e:
        parts.append('<a href="%s.html"><span class="dir">Previous</span>%s</a>'
                     % (e(prev_e["slug"]), e(prev_e["title"])))
    else:
        parts.append("<span></span>")
    if next_e:
        parts.append('<a href="%s.html" style="text-align:right"><span class="dir">Next</span>%s</a>'
                     % (e(next_e["slug"]), e(next_e["title"])))
    else:
        parts.append("<span></span>")
    parts.append("</nav>")

    parts.append("</div></main>")
    parts.append(foot(data, "../"))

    path = os.path.join(HERE, "paintings", entry["slug"] + ".html")
    open(path, "w", encoding="utf-8").write("".join(parts))
    return path


def main():
    data = json.load(open(GALLERY, encoding="utf-8"))
    missing = [x["title"] for x in data["entries"] if not x["images"]]
    if missing:
        print("ERROR: no images built for: %s" % missing)
        print("Run tools/build_images.py first.")
        sys.exit(1)

    os.makedirs(os.path.join(HERE, "paintings"), exist_ok=True)
    open(os.path.join(HERE, ".nojekyll"), "w").close()

    idx = build_index(data)
    print("wrote %s" % os.path.relpath(idx, HERE))

    wanted = {x["slug"] + ".html" for x in data["entries"]}
    pdir = os.path.join(HERE, "paintings")
    stale = [f for f in os.listdir(pdir) if f.endswith(".html") and f not in wanted]
    for f in stale:
        os.remove(os.path.join(pdir, f))
    if stale:
        print("pruned %d stale page(s): %s" % (len(stale), ", ".join(stale)))

    n = 0
    for key, _label, _note in SECTIONS:
        sel = [x for x in data["entries"] if x["section"] == key]
        for i, entry in enumerate(sel):
            build_piece(data, entry,
                        sel[i - 1] if i else None,
                        sel[i + 1] if i + 1 < len(sel) else None)
            n += 1
    print("wrote %d painting pages" % n)


if __name__ == "__main__":
    main()
