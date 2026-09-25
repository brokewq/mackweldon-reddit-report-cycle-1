"""Render index.html for the Mack Weldon Cycle 01 Reddit report."""
from collections import Counter, OrderedDict
from datetime import date, timedelta
from html import escape as e
from pathlib import Path

from PIL import Image
from data import DOUBLE, FEED, KW, OWN, POST_DATES, POSTS, SURF, THEMES

ROOT = Path(__file__).resolve().parent.parent
AR = ('<svg class="ar" viewBox="0 0 12 12" aria-hidden="true"><path d="M3 9l6-6M4 3h5v5" fill="none" '
      'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')
POSTS = POSTS[1:] + POSTS[:1]  # lead with the stronger threads; "sweat a lot" (P1) goes last
P = {p["id"]: p for p in POSTS}
NUM = {p["id"]: i for i, p in enumerate(POSTS, 1)}

# ---------- numbers ----------
views = sum(p["views"] for p in POSTS)
us_views = sum(p["views"] * p["us"] / 100 for p in POSTS)
us_share = us_views / views

n_rank = len(KW)
n_unique = len({k for _, k, _, _ in KW})
n_posts = len(POSTS)
n_comments = len(FEED)
subs = OrderedDict()
for p in POSTS:
    subs.setdefault(p["sub"], [0, 0])[0] += 1
for _, s, _ in FEED:
    subs.setdefault(s, [0, 0])[1] += 1
n_subs = len(subs)
top3 = [p for p in POSTS if p["rank"] and p["rank"] <= 3]
n_first = sum(1 for p in POSTS if p["rank"] == 1)
kw_by_post = {p["id"]: [k for k in KW if k[0] == p["id"]] for p in POSTS}
surf = Counter(s for *_, s in KW)
theme_n = Counter(P[pid]["theme"] for pid, *_ in KW)
kw_posts = {}
for pid, k, _, _ in KW:
    kw_posts.setdefault(k, []).append(pid)

assert n_rank == 67 and n_comments == 28 and n_subs == 12, (n_rank, n_comments, n_subs)


def fmt_m(v):
    return f"{v / 1e6:.2f}M"


def fmt_k(v):
    return f"{round(v / 1000):,}K"


def wbr(sub):
    """Allow line breaks at word boundaries inside subreddit names."""
    import re
    s = re.sub(r"(?<=[a-z])(?=[A-Z])", "<wbr>", sub)
    for w in ("fashion", "advice"):
        s = s.replace(w, "<wbr>" + w)
    return s.replace("r/<wbr>", "r/")


def short(pid):
    return P[pid]["title"].split("?")[0] + "?"


# ---------- hero ----------
seg = "".join(
    f'<i style="flex:{p["views"]};background:{THEMES[p["theme"]][1]}" title="{e(short(p["id"]))}: {p["vlabel"]} views"></i>'
    for p in sorted(POSTS, key=lambda p: -p["views"]))

hero = f'''
<header class="hero"><div class="hero-rings"></div><div class="hero-inner">
  <div class="brandrow"><img class="brandmark" src="m81-logo.png" alt="M81"><div class="bl1"><b>M81</b></div><span class="for">Prepared for Mack Weldon</span></div>
  <div class="kicker">Cycle 01 &nbsp;·&nbsp; Reddit report</div>
  <h1>Mack Weldon<br><i>on</i> <span class="hl">Reddit</span></h1>
  <p class="claim">Every post and branded comment that went live for Mack Weldon this cycle, how far those threads travelled on Reddit, and every Google search where they now sit on page one. Each ranking is backed by a live results-page capture.</p>
  <div class="reach">
    <div class="reach-main">
      <div class="eyebrow">Total views on our threads</div>
      <div class="reach-n">{fmt_m(views)}</div>
      <div class="reach-sub">across {n_posts} posts in four weeks &nbsp;·&nbsp; <b>{us_share:.0%}</b> from the United States</div>
      <div class="reach-strip">{seg}</div>
      <div class="reach-leg">Views by post. One thread, <b>“{e(short("P3"))}”</b>, reached {P["P3"]["vlabel"]} on its own.</div>
    </div>
    <div class="herostats">
      <div><b>{n_rank}</b><span>Google rankings</span><em>{n_unique} distinct searches</em></div>
      <div><b>{n_comments}</b><span>Branded comments</span><em>in {n_subs} communities</em></div>
      <div><b>{len(top3)}<small>/{n_posts}</small></b><span>Posts in subreddit top 3</span><em>{n_first} hit #1 the day they went up</em></div>
      <div><b>{n_posts}</b><span>Posts live</span><em>5 product themes</em></div>
    </div>
  </div>
  <p class="prepared">29 Aug to 25 Sep 2026 &nbsp;·&nbsp; Google &nbsp;·&nbsp; United States &nbsp;·&nbsp; Rankings captured 25 Sep 2026</p>
</div></header>
<nav class="topnav"><div class="topnav-in"><a href="#glance">At a glance</a><a href="#own">Keywords we own</a><a href="#posts">Posts and rankings</a><a href="#comments">Branded comments</a><a href="#ahead">Looking ahead</a><a href="#method">Method</a></div></nav>
'''

# ---------- at a glance ----------
mx = max(p["views"] for p in POSTS)
reach_rows = ""
for p in sorted(POSTS, key=lambda p: -p["views"]):
    rk = f'<span class="rk r{min(p["rank"], 4)}">#{p["rank"]} in sub</span>' if p["rank"] else ""
    reach_rows += (f'<a class="vb" href="#{p["id"].lower()}"><span class="vb-t">{e(short(p["id"]))}<em>{p["sub"]}</em></span>'
                   f'<span class="vb-bar"><i style="width:{max(p["views"] / mx * 100, 1.2):.1f}%;background:{THEMES[p["theme"]][1]}"></i></span>'
                   f'<span class="vb-n">{p["vlabel"]}</span><span class="vb-r">{rk}</span></a>')

rank_cells = ""
for p in sorted([p for p in POSTS if p["rank"]], key=lambda p: p["rank"]):
    cls = "gold" if p["rank"] == 1 else ("hot" if p["rank"] <= 3 else "")
    rank_cells += (f'<a class="rc {cls}" href="#{p["id"].lower()}"><b>#{p["rank"]}</b><em class="rc-d">post of the day</em>'
                   f'<strong>{e(p["nick"])}</strong><span>{wbr(p["sub"])}</span></a>')

us_min = min(p["us"] for p in POSTS)
us_top = P["P3"]
us_facts = (
    f'<div class="usf"><b>{n_posts}/{n_posts}</b><span><strong>The US led the audience on every thread.</strong> On all eight, no other country came out ahead of it.</span></div>'
    f'<div class="usf"><b>{us_min:.0f}%+</b><span><strong>A majority on every thread.</strong> The US share never dropped below {us_min:.0f}% of a post\'s views.</span></div>'
    f'<div class="usf"><b>≈{fmt_k(us_top["views"] * us_top["us"] / 100)}</b><span><strong>US views on one thread alone.</strong> “{e(short("P3"))}” reached {us_top["vlabel"]} views, {us_top["us"]:.0f}% of them in the US.</span></div>'
)

surf_order = ["C", "D", "O", "A"]
surf_col = {"C": "var(--accent)", "D": "var(--navy)", "O": "#e9b48a", "A": "var(--green)"}
surf_bar = "".join(f'<i style="flex:{surf[s]};background:{surf_col[s]}" title="{SURF[s]}: {surf[s]}"></i>' for s in surf_order)
surf_leg = "".join(f'<div class="pl-item"><i class="sw" style="background:{surf_col[s]}"></i><b>{surf[s]}</b><span>{SURF[s]}</span></div>' for s in surf_order)

tmax = max(theme_n.values())
theme_rows = ""
for key, n in theme_n.most_common():
    name, col = THEMES[key]
    theme_rows += (f'<div class="th"><span class="th-t"><i style="background:{col}"></i>{name}</span>'
                   f'<span class="th-bar"><i style="width:{n / tmax * 100:.0f}%;background:{col}"></i></span><span class="th-n">{n}</span></div>')

smax = max(a + b for a, b in subs.values())
fp_rows = ""
for s, (np_, nc) in sorted(subs.items(), key=lambda kv: (-(kv[1][0] + kv[1][1]), kv[0].lower())):
    fp_rows += (f'<div class="fp-row"><span class="fp-sub">{s}</span><span class="fp-bar">'
                + (f'<i class="seg a" style="width:{np_ / smax * 100:.1f}%" title="Posts: {np_}"></i>' if np_ else "")
                + (f'<i class="seg n" style="width:{nc / smax * 100:.1f}%" title="Comments: {nc}"></i>' if nc else "")
                + f'</span><span class="fp-n">{np_ + nc}</span></div>')

by_day_c = Counter(d for d, _, _ in FEED)
mfa = [p for p in POSTS if p["sub"] == "r/malefashionadvice"]
mfa_n = len(mfa)
mfa_rank = sum(len(kw_by_post[p["id"]]) for p in mfa)
mfa_share = sum(p["views"] for p in mfa) / views
kmax = max(len(v) for v in kw_by_post.values())


glance = f'''
<div class="wrap" id="glance">
  <section class="block"><div class="block-head"><h2>At a glance</h2><p>Mack Weldon, 29 Aug to 25 Sep 2026. Most important first: how many people saw the threads, where they placed, and where they now rank on Google.</p></div>

    <div class="chartcard">
      <div class="chart-head"><div><div class="eyebrow">Reach on Reddit</div><div class="chart-title">{fmt_m(views)} views across {n_posts} threads</div></div>
        <div class="legend">{"".join(f'<span><i class="dot" style="background:{c}"></i>{n}</span>' for n, c in THEMES.values())}</div></div>
      <div class="vbs">{reach_rows}</div>
      <p class="cardnote">Views as shown in each thread's Reddit Post Insights at the time of capture. Click a row to jump to the post.</p>
    </div>

    <div class="chartcard wide">
      <div class="wide-head"><div><div class="eyebrow">Front page of the community</div>
        <div class="chart-title">{len(top3)} of {n_posts} posts made their subreddit's top 3 posts of the day</div>
        <p class="wide-sub">Reddit ranks every post in a subreddit against the others posted that day. Two of our threads finished <b>#1 of the day</b> and three more made the <b>top 3</b>.</p></div></div>
      <div class="rcs">{rank_cells}</div>
    </div>

    <div class="chartcard wide split">
      <div class="split-l">
        <div class="eyebrow">Who saw it</div>
        <div class="chart-title">The US is Mack Weldon's audience here</div>
        <div class="bigs">
          <div><b class="acc">{us_share:.0%}</b><span>of views from the US</span></div>
          <div><b>≈{fmt_k(us_views)}</b><span>US views</span></div>
        </div>
        <p class="cardnote">US share of each thread's views, from Reddit Post Insights.</p>
      </div>
      <div class="split-r">{us_facts}</div>
    </div>

    <div class="duo2">
      <div class="chartcard">
        <div class="eyebrow">On Google</div>
        <div class="chart-title">{n_rank} page-one rankings for {n_unique} distinct searches</div>
        <div class="pl-bar">{surf_bar}</div>
        <div class="pl-leg">{surf_leg}</div>
        <p class="cardnote">Where our thread appears on the results page. “What people are saying” is Google's carousel of trending Reddit and forum threads, shown near the top of the page.</p>
      </div>
      <div class="chartcard">
        <div class="eyebrow">Rankings by theme</div>
        <div class="chart-title">Three Mack Weldon product lines in the conversation</div>
        <div class="ths">{theme_rows}</div>
        <div class="procchips"><span class="procchip">Underwear &amp; boxer briefs</span><span class="procchip">Sweatpants &amp; joggers</span><span class="procchip">T-shirts</span></div>
      </div>
    </div>

    <div class="fp one">
      <div class="fp-col"><div class="fp-head"><div><div class="eyebrow">Subreddit footprint</div><div class="chart-title">{n_posts + n_comments} placements in {n_subs} communities</div></div>
        <div class="legend"><span><i class="dot a"></i>Posts</span><span><i class="dot n"></i>Branded comments</span></div></div>{fp_rows}</div>
    </div>
  </section>
</div>
'''

# ---------- keywords we own ----------
def dots(pids):
    return "".join(f'<a class="own-p" href="#{pid.lower()}"><span>{NUM[pid]}</span>{e(short(pid))}<em>{P[pid]["sub"]}</em></a>' for pid in pids)


own_cards = ""
for o in OWN:
    own_cards += (f'<article class="own-c"><a class="own-img" href="shots/s{o["img"]:02d}.webp" data-kw="{e(o["kw"])}" data-pl="3 of our threads on page one">'
                  f'<img src="thumbs/t{o["img"]:02d}.webp" alt="Google results for {e(o["kw"])}" loading="lazy"><span class="own-zoom">View capture {AR}</span></a>'
                  f'<div class="own-b"><div class="own-slots"><i></i><i></i><i></i><span>3 of our threads</span></div>'
                  f'<h3>“{e(o["kw"])}”</h3><p>{e(o["line"])}</p><div class="own-ps">{dots(o["posts"])}</div></div></article>')
dbl = ""
for o in DOUBLE:
    dbl += (f'<a class="dbl" href="shots/s{o["img"]:02d}.webp" data-kw="{e(o["kw"])}" data-pl="2 of our threads on page one">'
            f'<span class="dbl-img"><img src="thumbs/t{o["img"]:02d}.webp" alt="Google results for {e(o["kw"])}" loading="lazy"></span>'
            f'<span class="dbl-b"><span class="own-slots sm"><i></i><i></i><span>2 threads</span></span><b>“{e(o["kw"])}”</b>'
            f'<em>{" + ".join(e(P[p]["nick"]) for p in o["posts"])}</em></span></a>')

own = f'''
<section class="ownband" id="own"><div class="ownband-in">
  <div class="eyebrow">Keywords we own</div>
  <h2>When people ask Google about <span>boxer briefs</span>, Reddit answers with our threads.</h2>
  <p class="own-lead">For these searches it isn't one of our threads on page one, it's several. Every card in the discussion carousel is one of our threads, so whichever one a shopper opens, they land in a conversation where Mack Weldon comes up.</p>
  <div class="own-grid">{own_cards}</div>
  <div class="dbl-head"><span class="eyebrow">Two threads on page one</span></div>
  <div class="dbl-grid">{dbl}</div>
</div></section>
'''

# ---------- posts ----------
band = f'''
<section class="brand" id="posts">
  <div class="band"><div class="band-in">
    <div class="band-top"><div><div class="eyebrow">Posts and rankings</div><h2>Eight threads,<br>{fmt_m(views)} views</h2></div>
      <div class="band-procs"><div class="eyebrow">Themes targeted</div><div>{"".join(f'<span class="proc">{n}</span>' for n, _ in THEMES.values())}</div></div></div>
    <div class="band-stats">
      <div><b>{n_posts}</b><span>Posts live</span></div>
      <div><b>{fmt_m(views)}</b><span>Views</span></div>
      <div><b>{n_rank}</b><span>Google rankings</span></div>
      <div><b>{n_first}</b><span>#1 posts of the day</span></div>
    </div>
  </div></div>
  <div class="wrap">
    <div class="block"><div class="block-head"><h3>Keyword coverage by post</h3><p>Each keyword below was searched on Google and captured with our thread on the first page.</p></div>
    <div class="cov"><div class="cov-head"><span>Post</span><span>Keywords ranking</span></div>{{cov}}</div></div>
    {{cards}}
  </div>
</section>
'''
kmax = max(len(v) for v in kw_by_post.values())
cov = ""
for p in sorted(POSTS, key=lambda p: (-len(kw_by_post[p["id"]]), -p["views"])):
    n = len(kw_by_post[p["id"]])
    cov += (f'<a class="cov-row" href="#{p["id"].lower()}"><span class="cov-t">{e(p["title"])}<em>{p["sub"]} · {p["vlabel"]} views</em></span>'
            f'<span class="cov-bar"><i style="width:{n / kmax * 100:.0f}%"></i></span><span class="cov-n">{n}</span></a>')

cards = ""
for i, p in enumerate(POSTS, 1):
    name, col = THEMES[p["theme"]]
    rows = ""
    for j, (pid, k, img, s) in enumerate(kw_by_post[p["id"]], 1):
        others = [x for x in kw_posts[k] if x != pid]
        tag = f'<em class="also">{len(others) + 1} of our threads rank here</em>' if others else ""
        rows += (f'<a class="lg-row" href="shots/s{img:02d}.webp" data-kw="{e(k)}" data-pl="{SURF[s]}">'
                 f'<span class="lg-i">{j:02d}</span><span class="lg-k">{e(k)}{tag}</span>'
                 f'<span class="lg-s s{s}">{SURF[s]}</span>'
                 f'<span class="lg-t"><img src="thumbs/t{img:02d}.webp" alt="Google results for {e(k)}" loading="lazy"></span>'
                 f'<span class="lg-v">View {AR}</span></a>')
    rank = (f'<div class="ribbon{" gold" if p["rank"] == 1 else ""}"><b>#{p["rank"]}</b> post on {p["sub"]} the day it went up</div>'
            if p["rank"] else "")
    stats = (f'<div class="pstat"><b>{p["vlabel"]}</b><span>Views</span></div>'
             f'<div class="pstat"><b>{len(kw_by_post[p["id"]])}</b><span>Keywords ranking</span></div>'
             f'<div class="pstat"><b>{p["us"]:.0f}%</b><span>US audience</span></div>'
             + "".join(f'<div class="pstat"><b>{v}</b><span>{l}</span></div>' for v, l in p.get("extra", [])))
    note = f'<p class="pnote">{e(p["note"])}</p>' if p.get("note") else ""
    if p.get("highlight"):
        rank += ('<div class="spot"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4h10v3a5 5 0 0 1-10 0V4Z M17 5h3v1.5A3.5 3.5 0 0 1 16.6 10 M7 5H4v1.5A3.5 3.5 0 0 0 7.4 10 M12 12v4 M9.5 16h5v4h-5z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
                 '<span>Our comment held a <b>top-3 spot</b> in this thread for the first <b>12 hours</b></span></div>')
    iw, ih = Image.open(ROOT / "ins" / f"i{p['ins']:02d}.webp").size
    wide = " wide" if iw / ih > 0.6 else ""
    cards += f'''
<article class="card post" id="{p["id"].lower()}" style="--tc:{col}">
  <div class="ph">
    <a class="ins{wide}" href="ins/i{p["ins"]:02d}.webp" data-kw="Post insights: {e(p["title"])}" data-pl="Reddit Post Insights">
      <img src="ins/i{p["ins"]:02d}.webp" alt="Reddit Post Insights for {e(p["title"])}" loading="lazy"><span class="ins-cap">Reddit Post Insights {AR}</span></a>
    <div class="ph-b">
      <div class="card-meta"><span class="pnum">Post {i:02d}</span><span class="sub">{p["sub"]}</span><span class="pill">{name}</span></div>
      <h3 class="ptitle"><a href="{p["url"]}" target="_blank" rel="noopener">{e(p["title"])} {AR}</a></h3>
      <div class="ribrow">{rank}</div>
      <div class="pstats">{stats}</div>
      {note}
    </div>
  </div>
  <div class="lg"><div class="lg-head"><span>#</span><span>Keyword searched on Google</span><span>Where we appear</span><span>Capture</span><span></span></div>{rows}</div>
</article>'''

posts_html = band.replace("{cov}", cov).replace("{cards}", cards)

# ---------- comments ----------
chips = "".join(f'<span class="subchip">{s}<b>{nc}</b></span>'
                for s, (np_, nc) in sorted(subs.items(), key=lambda kv: (-kv[1][1], kv[0].lower())) if nc)
trs = ""
for n, (dt, s, url) in enumerate(FEED, 1):
    dd = date.fromisoformat(dt)
    trs += (f'<tr><td class="num">{n:02d}</td><td class="date">{dd.day} {"Aug" if dd.month == 8 else "Sep"}</td>'
            f'<td><span class="sub-sm">{s}</span></td><td class="repcell"><a href="{url}" target="_blank" rel="noopener">View comment {AR}</a></td></tr>')
comments = f'''
<div class="wrap" id="comments"><section class="block"><div class="block-head"><h2>Branded comments</h2><p>{n_comments} comments placed in live threads where someone asked a question Mack Weldon can answer, across {n_subs} communities.</p></div>
  <div class="metrics">
    <div class="metric"><div class="mval">{n_comments}</div><div class="mlab">Branded comments</div></div>
    <div class="metric"><div class="mval">{n_subs}</div><div class="mlab">Communities</div></div>
    <div class="metric"><div class="mval">{subs["r/MensUnderwearGuide"][1]}</div><div class="mlab">In r/MensUnderwearGuide</div><div class="mnote">The largest single community</div></div>
    <div class="metric"><div class="mval">{by_day_c["2026-09-24"]}</div><div class="mlab">Placed on 24 Sep</div><div class="mnote">The busiest day of the cycle</div></div>
  </div>
  <div class="subchips">{chips}</div>
  <div class="table-wrap"><table><thead><tr><th>#</th><th>Date</th><th>Subreddit</th><th>Link</th></tr></thead><tbody>{trs}</tbody></table></div>
</section></div>
'''

# ---------- looking ahead + footer ----------
ahead = f'''
<div class="wrap" id="ahead"><section class="block"><div class="block-head"><h2>Looking ahead</h2></div>
  <div class="signoff"><div class="signoff-text">
    <p>This cycle taught us a lot about how these niches work. Google keeps returning to a handful of communities per category (our {mfa_n} r/malefashionadvice threads alone produced {mfa_rank} of the {n_rank} rankings), titles phrased the way people actually search pick up the most keywords, and a cluster of threads on one theme can take the entire discussion carousel. Our next batch of posts will be built around those learnings, and will carry the same approach into more of the Mack Weldon range.</p>
    <p class="ah-thanks">It's been a great first cycle working with your team. Thank you for the trust, and here's to cycle two.</p>
  </div></div>
</section></div>

<footer id="method"><div class="m81card"><div class="m81-watermark">M81 MEDIA</div><div class="m81card-inner">
  <div class="m81-lock"><img src="m81-logo.png" alt="M81"><span class="bname">M81</span></div>
  <div class="m81-method"><p class="fineprint"><strong>Method.</strong> Each ranking was captured from a live google.com results page on 25 Sep 2026. The dark panel on the right of every screenshot is the raw data for that search. A keyword counts as ranking when our thread appears on the first page, and it is counted once for each of our threads that appears, so a search where three threads rank counts three times ({n_rank} rankings, {n_unique} distinct searches). Views, subreddit rank and audience come from each thread's Reddit Post Insights at the time of capture. Rankings shift by location, device and date, so each capture is a snapshot from the day it was run.</p>
  <div class="src"><span>Search engine: Google</span><span>Location: United States</span><span>Device: Desktop</span><span>Captured: 25 Sep 2026</span><span>Period: 29 Aug to 25 Sep 2026</span></div></div>
</div></div></footer>
'''

lightbox = '''
<div class="lb" id="lb" hidden><button class="lb-x" aria-label="Close">Close</button><button class="lb-prev" aria-label="Previous">Prev</button><button class="lb-next" aria-label="Next">Next</button>
<figure><figcaption><span id="lb-pl"></span><b id="lb-kw"></b><em id="lb-ct"></em></figcaption><div class="lb-stage"><span class="lb-msg lb-wait">Loading capture</span><span class="lb-msg lb-fail">This capture did not load. Refresh the page and try again.</span><img id="lb-img" alt=""></div></figure></div>
<script>(function () {
  var tiles = Array.prototype.slice.call(document.querySelectorAll('a[data-kw]'));
  var lb = document.getElementById('lb'), img = document.getElementById('lb-img');
  var kw = document.getElementById('lb-kw'), pl = document.getElementById('lb-pl'), ct = document.getElementById('lb-ct');
  var cur = 0;
  function show(i) {
    cur = (i + tiles.length) % tiles.length;
    var t = tiles[cur], src = t.getAttribute('href');
    lb.classList.add('loading'); lb.classList.remove('failed');
    lb.classList.toggle('tall', /^ins\\//.test(src));
    img.onload = function () { lb.classList.remove('loading'); };
    img.onerror = function () { if (img.getAttribute('src')) { lb.classList.remove('loading'); lb.classList.add('failed'); } };
    img.src = src;
    var nx = tiles[(cur + 1) % tiles.length]; if (nx) { new Image().src = nx.getAttribute('href'); }
    img.alt = t.dataset.kw;
    kw.textContent = t.dataset.kw; pl.textContent = t.dataset.pl;
    ct.textContent = (cur + 1) + ' / ' + tiles.length;
    lb.hidden = false; document.body.style.overflow = 'hidden';
  }
  function close() { lb.hidden = true; img.removeAttribute('src'); document.body.style.overflow = ''; }
  tiles.forEach(function (t, i) { t.addEventListener('click', function (ev) { ev.preventDefault(); show(i); }); });
  lb.querySelector('.lb-x').addEventListener('click', close);
  lb.querySelector('.lb-prev').addEventListener('click', function () { show(cur - 1); });
  lb.querySelector('.lb-next').addEventListener('click', function () { show(cur + 1); });
  lb.addEventListener('click', function (ev) { if (ev.target === lb) close(); });
  document.addEventListener('keydown', function (ev) {
    if (lb.hidden) return;
    if (ev.key === 'Escape') close();
    if (ev.key === 'ArrowLeft') show(cur - 1);
    if (ev.key === 'ArrowRight') show(cur + 1);
  });
})();</script>
'''

css = (ROOT / "build" / "style.css").read_text()
html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mack Weldon: Reddit Report, Cycle 01 | M81</title>
<meta name="description" content="Mack Weldon on Reddit, Cycle 01: {fmt_m(views)} views, {n_rank} Google rankings, {n_posts} posts and {n_comments} branded comments.">
<link rel="icon" href="m81-logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet">
<style>{css}</style></head><body>
{hero}{glance}{own}{posts_html}{comments}{ahead}{lightbox}</body></html>'''
(ROOT / "index.html").write_text(html)
print(f"views {views:,}  us {us_share:.1%} ({us_views:,.0f})  rankings {n_rank}  unique {n_unique}  surf {dict(surf)}  themes {dict(theme_n)}")
