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

# The export's UI is in Russian, so its post dates read "окт 24, 2026 2:37 am".
# Only the month and year are kept -- a painting is dated by when it was made,
# not to the minute.
RU_MONTHS = {
    "янв": (1, "January"), "фев": (2, "February"), "мар": (3, "March"),
    "апр": (4, "April"), "май": (5, "May"), "июн": (6, "June"),
    "июл": (7, "July"), "авг": (8, "August"), "сен": (9, "September"),
    "окт": (10, "October"), "ноя": (11, "November"), "дек": (12, "December"),
}


MONTH_NUM = {name: num for num, name in RU_MONTHS.values()}


def override_date(s):
    """'July 2024' -> ('July 2024', '2024-07'). Month and year only, so the ISO
    form stops at the month rather than inventing a day."""
    m = re.match(r"\s*([A-Z][a-z]+)\s+(\d{4})\s*$", s)
    if not m or m.group(1) not in MONTH_NUM:
        return "", ""
    return ("%s %s" % (m.group(1), m.group(2)),
            "%s-%02d" % (m.group(2), MONTH_NUM[m.group(1)]))


def parse_post_date(s):
    """'окт 24, 2026 2:37 am' -> ('October 2026', '2026-10-24'), or ('', '').

    Returns empty strings rather than guessing if the format ever changes, so
    a missing date simply isn't rendered.
    """
    m = re.match(r"\s*([а-я]{3})\s+(\d{1,2}),\s*(\d{4})", s)
    if not m or m.group(1) not in RU_MONTHS:
        return "", ""
    num, name = RU_MONTHS[m.group(1)]
    return ("%s %s" % (name, m.group(3)),
            "%s-%02d-%02d" % (m.group(3), num, int(m.group(2))))

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
# The merged post's own title and caption are dropped, so if its caption said
# something worth keeping, carry that sentence over via CAPTION_EDITS on the
# target (see the Cigar Galaxy) -- and remember to delete the merged slug's own
# CAPTION_EDITS entry, or the unknown-slug guard will fail the build.
MERGE_INTO = {
    "17970471571710256.webp": "17991007885468360.webp",
    # The early M82 attempt becomes the second view of the finished M82, so the
    # two versions sit in one panel and you swipe between them. Export order
    # puts the newer post first, which is the one that shows on the card.
    "17969617705730105.webp": "17968986481731950.webp",
}

# not paintings; kept out of the gallery
EXCLUDE = {"18100029988294296.webp": "introduction post - offered as about-section source"}

# Sofia prefers real measurements over paper-size names. Keys are matched
# against the already-tidied size, lowercased.
SIZE_NORMALISE = {
    "postcard size": "10.5 × 14.8 cm",
    "a6": "10.5 × 14.8 cm",
    "a5": "14.8 × 21 cm",
    "a4": "21 × 29.7 cm",
    "a2": "42 × 59.4 cm",
}

# Sizes Sofia gave directly, for paintings whose caption never stated one.
# slug -> a SIZE_NORMALISE key or a literal measurement.
#
# This is the one sanctioned exception to "take dimensions only from the
# captions": the rule exists so nothing gets looked up or guessed, and here
# Sofia is the source herself. Do not "correct" these back to empty because
# the caption doesn't mention them -- record new ones here the same way.
SIZE_OVERRIDE = {
    "sunset": "a6",
}

# Dates Sofia corrected by hand, slug -> "Month YYYY". Same exception as
# SIZE_OVERRIDE: the export only knows when a post went up, which can be months
# after the painting was made. Her correction wins over the parsed post date.
DATE_OVERRIDE = {
    "a-guinea-pig": "July 2024",
    "another-guinea-pig": "July 2024",
}

# Slugs whose Instagram caption is dropped: the painting is shown with its
# medium, size and date only. Sofia's call -- these four captions were casual
# asides rather than anything she wants on the site. The medium/size line is
# still extracted from the caption first, so nothing is lost there.
NO_CAPTION = {
    "a-walk",
    "sunset",
    "a-guinea-pig",
    "another-guinea-pig",
}

# Captions Sofia rewrote herself, slug -> the full replacement text. Used
# instead of the export's caption, and CAPTION_EDITS is skipped for these.
# Her words, supplied verbatim -- don't tidy or re-edit them.
CAPTION_REPLACE = {
    "m16-the-eagle-nebula":
        "M16, the Eagle Nebula (also known as the Pillars of Creation),"
        " 42 × 59.4 cm. This is my biggest watercolour painting to date.",
}

# Literal snips applied to a caption's prose, slug -> [(find, replace), ...].
# Sofia asked for the birthday mentions out: a gift occasion (and a friend's
# Instagram handle) isn't something she wants on a site PhD panels will read.
# Each snip removes only the birthday clause, keeping what the caption says
# about the painting itself. The build fails if any `find` no longer matches,
# so a reworded export can't silently leave a mention in.
CAPTION_EDITS = {
    "m104-the-sombrero-galaxy": [
        (", which I gave to the incredible (!!!) @emma89harris for her"
         " birthday earlier this year.", "."),
        # "an A5" -> "a 14.8": the article has to change with it, because A5
        # begins with a vowel sound and "fourteen" does not.
        ("an A5 painting", "a 14.8 × 21 cm painting"),
    ],
    "the-cigar-galaxy-m82": [
        # The early attempt is now this entry's second view (see MERGE_INTO),
        # and its own caption went with its entry. This sentence is that
        # caption, verbatim minus the birthday line, so the second image is
        # explained rather than just appearing.
        ("I finished this version last week.",
         "I finished this version last week.\n"
         "This was one of my first attempts at painting M82, the Cigar"
         " Galaxy."),
    ],
    "northern-lights-over-chocorua-lake": [
        ("This A5 watercolour", "This 14.8 × 21 cm watercolour"),
    ],
}

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
    # tidy first so the lookup keys are canonical ("A6 size" -> "A6")
    size = tidy_size(size)
    return medium, SIZE_NORMALISE.get(size.lower(), size)


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
        # EXIF capture date. It sits one level deeper than its label:
        #   <div class="_a6-q">Дата</div><div><div class="_a6-q">2025:09:10 …
        # Only about a third of posts carry one, and it is when the *photograph*
        # was taken, which is not the same as when the post went up. Kept only
        # because an exact match identifies the same photograph when swapping in
        # high-resolution originals (see DEFERRED.md). Never sort by it.
        taken = re.search(
            r'<div class="_a6-q">(\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2})</div>', b)
        # The post date, which is what the site displays. Unlike `taken` this is
        # present on every post and runs strictly newest-first, matching the
        # export order.
        posted = re.search(r'<div class="_3-94 _a6-o">([^<]+)</div>', b)
        shown, iso = parse_post_date(posted.group(1) if posted else "")
        posts.append({
            "media": [m.split("/")[-1] for m in
                      re.findall(r'href="media/posts/([^"]+)"', b)],
            "caption": strip_tags(h2.group(1)) if h2 else "",
            "taken": taken.group(1) if taken else "",
            "posted": shown,
            "postedISO": iso,
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
        posted, posted_iso = p["posted"], p["postedISO"]
        if slug in DATE_OVERRIDE:
            posted, posted_iso = override_date(DATE_OVERRIDE[slug])
            if not posted:
                problems.append("DATE_OVERRIDE for %s is not 'Month YYYY': %r"
                                % (slug, DATE_OVERRIDE[slug]))

        if slug in SIZE_OVERRIDE:
            # through the same lookup as the captions, so "a6" renders exactly
            # as the other 10.5 × 14.8 cm pieces do
            raw = SIZE_OVERRIDE[slug]
            size = SIZE_NORMALISE.get(raw.lower(), tidy_size(raw))

        if slug in CAPTION_REPLACE:
            prose = CAPTION_REPLACE[slug]
        else:
            for find, repl in CAPTION_EDITS.get(slug, ()):
                if find not in prose:
                    problems.append("CAPTION_EDITS text not found for %s: %r"
                                    % (slug, find))
                else:
                    prose = prose.replace(find, repl, 1).strip()

        entries.append({
            "slug": slug,
            "title": title,
            "section": section,
            "order": order,
            "caption": "" if slug in NO_CAPTION else prose,
            "hashtags": sorted(set(tags)),
            "medium": medium,
            "size": size,
            "takenRaw": p["taken"],
            "posted": posted,
            "postedISO": posted_iso,
            "sourceImages": media,
            "images": existing.get(slug, []),
        })

    # apply requested position swaps, then lock the gallery to `order`
    by_slug = {x["slug"]: x for x in entries}
    for s in sorted(NO_CAPTION - set(by_slug)):
        problems.append("NO_CAPTION refers to unknown slug: %s" % s)
    for s in sorted(set(CAPTION_EDITS) - set(by_slug)):
        problems.append("CAPTION_EDITS refers to unknown slug: %s" % s)
    for s in sorted(set(CAPTION_REPLACE) - set(by_slug)):
        problems.append("CAPTION_REPLACE refers to unknown slug: %s" % s)
    for s in sorted(set(SIZE_OVERRIDE) - set(by_slug)):
        problems.append("SIZE_OVERRIDE refers to unknown slug: %s" % s)
    for s in sorted(set(DATE_OVERRIDE) - set(by_slug)):
        problems.append("DATE_OVERRIDE refers to unknown slug: %s" % s)

    # Backstop for CAPTION_EDITS: nothing that reaches the site may mention a
    # birthday, however the caption gets reworded upstream.
    for x in entries:
        if re.search(r"birthday|bday|b-day", x["caption"], re.I):
            problems.append("birthday still mentioned in caption: %s" % x["slug"])
        # Sizes are given in centimetres everywhere, prose included.
        m = re.search(r"\b(A[0-9]|postcard)\b", x["caption"], re.I)
        if m:
            problems.append("paper-size name %r left in caption: %s"
                            % (m.group(0), x["slug"]))
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
            print("   %-44s | %-28s | %-14s | %-15s | %d img" % (
                e["title"], e["medium"] or "-", e["size"] or "-",
                e["posted"] or "NO DATE", len(e["sourceImages"])))
        print()

    undated = [e["title"] for e in entries if not e["posted"]]
    if undated:
        problems.append("no post date parsed for: %s" % ", ".join(undated))
    if problems:
        print("PROBLEMS:")
        for x in problems:
            print("  !", x)
        sys.exit(1)
    print("All titles verified against caption text.")


if __name__ == "__main__":
    main()
