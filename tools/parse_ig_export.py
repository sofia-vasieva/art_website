"""Parse the Instagram HTML export into gallery.json.

Content rule (from Sofia): invent nothing. Every title must be traceable to
words she already wrote in the caption. Each TITLES entry carries a `verify`
term that must literally appear in that post's caption, or the build fails.
"""
import html
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORT = os.path.join(HERE, "posts", "posts_1.html")
OUT = os.path.join(HERE, "gallery.json")

# key: first media filename -> (title, verify-substring, section)
TITLES = {
    "18077009021742341.jpg": ("The Cosmic Reef Nebula", "cosmic reef", "deepsky"),
    "18077769806740616.jpg": ("The Sunflower Galaxy (M63)", "sunflower galaxy", "deepsky"),
    "18115171588969654.jpg": ("Centaurus A", "centaurus a", "deepsky"),
    "18352826488219962.jpg": ("The Southern Pinwheel Galaxy (M83)", "southern pinwheel", "deepsky"),
    "17994646487943628.jpg": ("The Black Eye Galaxy (M64)", "black eye galaxy", "deepsky"),
    "18106470298747369.heic": ("NGC 1501, the Camel's Eye Nebula", "ngc 1501", "deepsky"),
    "17854226916584718.heic": ("The Cartwheel Galaxy", "cartwheel galaxy", "deepsky"),
    "18184636510336861.jpg": ("M100, the Mirror Galaxy", "m100", "deepsky"),
    "18042339107382928.jpg": ("The Helix Nebula (NGC 7293)", "helix nebula", "deepsky"),
    "18014592155603929.jpg": ("The Triangulum Galaxy (M33)", "triangulum galaxy", "deepsky"),
    "17921554662153761.jpg": ("The Andromeda Galaxy (M31)", "andromeda galaxy", "deepsky"),
    "18042746882316907.jpg": ("The Pinwheel Galaxy (M101)", "pinwheel galaxy", "deepsky"),
    "17843597979334292.jpg": ("The Antennae Galaxies (NGC 4038/NGC 4039)", "antennae galaxies", "deepsky"),
    "17956171559717885.jpg": ("The Whirlpool Galaxy (M51)", "whirlpool galaxy", "deepsky"),
    "17976912746640448.jpg": ("The Orion Nebula (M42)", "orion nebula", "deepsky"),
    "18401078437009586.jpg": ("Hierarchical Bubble Structure", "hierarchicalbubblestructure", "deepsky"),
    "17946977120627132.jpg": ("The Ring Nebula (M57)", "ring nebula", "deepsky"),
    "18220254061150432.webp": ("The Crab Nebula (M1)", "crab nebula", "deepsky"),
    "17855536445761020.webp": ("M104, the Sombrero Galaxy", "sombrero galaxy", "deepsky"),
    "17991007885468360.webp": ("M16, the Eagle Nebula", "eagle nebula", "deepsky"),
    "17968986481731950.webp": ("The Cigar Galaxy (M82)", "cigar galaxy", "deepsky"),
    "17969617705730105.webp": ("The Cigar Galaxy (M82), an early attempt", "cigar galaxy", "deepsky"),
    # other work
    "18123778063380671.jpg": ("Another guinea pig", "guinea pig", "other"),
    "18036178498996164.jpg": ("A guinea pig", "guinea pig", "other"),
    "18011479976048402.jpg": ("Theodoros the frog", "theodoros", "other"),
    "17937878366333633.webp": ("Northern lights over Chocorua Lake", "northern lights", "other"),
    "17943810971147949.webp": ("Sunset", "sunset", "other"),
    # Author-chosen title, not derived from the caption. The painting is a
    # landscape -- a child walking up a path through a field under a sky that
    # goes from daylight to stars -- which the caption never says. Sofia named
    # it. `verify` still anchors the entry to the right post; don't "correct"
    # the title back towards the caption wording.
    "18003102209336565.jpg": ("A walk", "nephew", "other"),
    # process
    "17901750338543138.webp": ("Watercolour tip: starting a galaxy", "watercolour tip", "process"),
}

# posts folded into another entry as extra views: {media -> target media}
MERGE_INTO = {"17970471571710256.webp": "17991007885468360.webp"}

# not paintings; kept out of the gallery
EXCLUDE = {"18100029988294296.webp": "introduction post - offered as about-section source"}

# Sofia asked for "postcard size" to read as the actual A6 measurements.
SIZE_NORMALISE = {"postcard size": "10.5 × 14.8 cm"}

# pairs of slugs whose positions in the gallery are swapped
SWAP_ORDER = [("a-guinea-pig", "another-guinea-pig")]

SIZE_RE = re.compile(
    r"(?ix)"
    r"( A[2-6]\b(?:\ size)?"
    r"| postcard\ size"
    r"| \d{1,3}(?:[.,]\d)?\s*[x×]\s*\d{1,3}(?:[.,]\d)?\s*(?:cm)?"
    r")")


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def slugify(s):
    s = s.lower().replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


# A line that says nothing but the medium and size, e.g.
# "Watercolour on paper, 10.5 x 14.8 cm" or "(A4, watercolour)".
# Those are shown as separate metadata, so they are dropped from the prose.
SPEC_ONLY_RE = re.compile(
    r"(?ix)^[\s(\[]*"
    r"(?:(?:watercolour|on|paper|black|size|postcard|cm|A[2-6]"
    r"|\d{1,3}(?:[.,]\d)?|[x×,.\-]|\s)+)"
    r"[\s)\].]*$")


def is_spec_only(line):
    s = line.strip()
    if not s or not re.search(r"(?i)watercolour|cm|A[2-6]|postcard", s):
        return False
    # must contain no word outside the allowed vocabulary
    return bool(SPEC_ONLY_RE.match(s))


def split_caption(cap):
    """Separate trailing hashtag blocks, and drop medium/size-only lines."""
    body, tags = [], []
    for ln in cap.split("\n"):
        words = ln.strip().split()
        if words and all(w.startswith("#") for w in words):
            tags += [w.lstrip("#") for w in words]
        elif is_spec_only(ln):
            continue
        else:
            body.append(ln)
    if body:
        m = re.search(r"((?:\s#[\w]+)+)\s*$", body[-1])
        if m:
            tags += [w.lstrip("#") for w in m.group(1).split()]
            body[-1] = body[-1][: m.start()].rstrip()
    # a trailing "(A4, watercolour)" on the last prose line is metadata too
    if body:
        m = re.search(r"\s*\(([^()]*)\)\s*\.?\s*$", body[-1])
        if m and is_spec_only(m.group(1)):
            body[-1] = body[-1][: m.start()].rstrip()
    prose = re.sub(r"\n{3,}", "\n\n", "\n".join(body).strip())
    return prose, tags


def find_medium_and_size(cap):
    """Pull medium/size ONLY from what the caption literally says."""
    medium = "Watercolour" if re.search(r"(?i)watercolour", cap) else ""
    if re.search(r"(?i)black paper", cap):
        medium = (medium + " on black paper").strip()
    elif re.search(r"(?i)on paper", cap):
        medium = (medium + " on paper").strip()
    m = SIZE_RE.search(cap)
    size = re.sub(r"\s+", " ", m.group(1).strip()) if m else ""
    size = SIZE_NORMALISE.get(size.lower(), size)
    return medium, tidy_size(size)


def tidy_size(size):
    """Formatting only: the captions write the same measurement several ways
    (10.5x14.8cm / 10.5 x 14.8 cm / 10.5 × 14.8 cm). Render them identically."""
    if not size:
        return size
    m = re.match(r"(?i)^\s*(\d{1,3}(?:[.,]\d)?)\s*[x×]\s*(\d{1,3}(?:[.,]\d)?)\s*(?:cm)?\s*$",
                 size)
    if m:
        return "%s × %s cm" % (m.group(1).replace(",", "."),
                                    m.group(2).replace(",", "."))
    return re.sub(r"(?i)^(A[2-6])\s+size$", r"\1", size.strip())


def load_existing_images():
    """Keep already-built image records so re-parsing doesn't force a rebuild."""
    if not os.path.exists(OUT):
        return {}
    try:
        old = json.load(open(OUT, encoding="utf-8"))
    except (ValueError, OSError):
        return {}
    return {x["slug"]: x.get("images", []) for x in old.get("entries", [])}


def main():
    existing = load_existing_images()
    raw = open(EXPORT, encoding="utf-8", errors="replace").read()
    blocks = [b for b in re.split(
        r'(?=<div class="pam _3-95 _2ph- _a6-g uiBoxWhite noborder">)', raw)
        if "media/posts/" in b]

    posts = []
    for b in blocks:
        h2 = re.search(r"(?s)<h2[^>]*>(.*?)</h2>", b)
        # The date sits one level deeper than the label:
        #   <div class="_a6-q">Дата</div><div><div class="_a6-q">2025:09:10 …
        # Only about a third of posts carry one, and it is the photo's capture
        # date, not the post date -- so it is NOT a reliable sort key. It is
        # kept because an exact match identifies the same photograph when
        # swapping in high-resolution originals (see DEFERRED.md).
        taken = re.search(
            r'<div class="_a6-q">(\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2})</div>', b)
        posts.append({
            "media": [m.split("/")[-1] for m in
                      re.findall(r'href="media/posts/([^"]+)"', b)],
            "caption": strip_tags(h2.group(1)) if h2 else "",
            "taken": taken.group(1) if taken else "",
        })

    by_media = {p["media"][0]: p for p in posts}
    entries, problems = [], []

    for order, p in enumerate(posts):
        key = p["media"][0]
        if key in EXCLUDE or key in MERGE_INTO:
            continue
        if key not in TITLES:
            problems.append("no title mapped for %s: %r" % (key, p["caption"][:60]))
            continue
        title, verify, section = TITLES[key]
        flat = p["caption"].lower()
        if verify.lower() not in flat and verify.lower() not in flat.replace(" ", ""):
            problems.append("TITLE NOT IN CAPTION for %s: need %r" % (key, verify))
            continue

        prose, tags = split_caption(p["caption"])
        medium, size = find_medium_and_size(p["caption"])

        media = list(p["media"])
        for extra, target in MERGE_INTO.items():
            if target == key and extra in by_media:
                media += by_media[extra]["media"]

        slug = slugify(title)
        entries.append({
            "slug": slug,
            "title": title,
            "section": section,
            "order": order,
            "caption": prose,
            "hashtags": sorted(set(tags)),
            "medium": medium,
            "size": size,
            "takenRaw": p["taken"],
            "sourceImages": media,
            "images": existing.get(slug, []),
        })

    # apply requested position swaps, then lock the gallery to `order`
    by_slug = {x["slug"]: x for x in entries}
    for a, b in SWAP_ORDER:
        if a in by_slug and b in by_slug:
            by_slug[a]["order"], by_slug[b]["order"] = \
                by_slug[b]["order"], by_slug[a]["order"]
        else:
            problems.append("SWAP_ORDER refers to unknown slug: %s / %s" % (a, b))
    entries.sort(key=lambda x: x["order"])

    data = {
        "artist": "Sofia Vasieva",
        "copyright": "© Sofia Vasieva 2024–2026. Please do not reproduce without permission.",
        "youtube": "https://youtube.com/@raysescaping4526",
        "instagram": "https://www.instagram.com/rays.escaping/",
        # Quiet footer asides to Sofia's other sites. One line each; the block
        # disappears if the list is empty. Add the science site here when
        # sofiavasieva.com exists -- no code change needed.
        "elsewhere": [
            {"text": "I also put music out",
             "label": "sofiavasievamusic.com",
             "url": "https://sofiavasievamusic.com"},
        ],
        "about": "",
        "entries": entries,
    }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("posts parsed     : %d" % len(posts))
    print("excluded         : %d  %s" % (len(EXCLUDE), list(EXCLUDE)))
    print("merged as extras : %d" % len(MERGE_INTO))
    print("entries written  : %d  -> %s\n" % (len(entries), OUT))
    for sec in ("deepsky", "other", "process"):
        sel = [e for e in entries if e["section"] == sec]
        print("[%s]  %d" % (sec, len(sel)))
        for e in sel:
            print("   %-44s | %-28s | %-14s | %d img" % (
                e["title"], e["medium"] or "-", e["size"] or "-", len(e["sourceImages"])))
        print()
    if problems:
        print("PROBLEMS:")
        for x in problems:
            print("  !", x)
        sys.exit(1)
    print("All titles verified against caption text.")


if __name__ == "__main__":
    main()
