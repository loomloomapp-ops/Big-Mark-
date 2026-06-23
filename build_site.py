#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build BIG-MARK landing page from the Flampt Webflow template (1:1 visuals + animations),
recoloured to the BIG-MARK gold/graphite brand and re-contented in Polish.
Run from project root. Produces ./index.html
"""
import re, os
from bs4 import BeautifulSoup, NavigableString

ROOT = os.path.dirname(os.path.abspath(__file__))
TPL_DIR = os.path.join(ROOT, "assets", "Flampt Webflow Website Copier")
TPL = os.path.join(TPL_DIR, "index.html")
ASSET_PREFIX = "assets/Flampt%20Webflow%20Website%20Copier/"

LOGO = "assets/big-mark_logo_transparent.png"
LOGO_WHITE = "assets/big-mark_logo_white.png"
def PH(n): return f"assets/photos/gallery-{n:02d}.jpeg"

soup = BeautifulSoup(open(TPL, encoding="utf-8").read(), "html.parser")
report = {"set": 0, "miss": 0}

# ---------- helpers ----------
def set_text(el, text):
    """Replace all contents of el with a single text string."""
    if el is None:
        report["miss"] += 1; return False
    el.clear()
    el.append(NavigableString(text))
    report["set"] += 1
    return True

def section(cls):
    for s in soup.find_all("section"):
        if cls in " ".join(s.get("class", [])):
            return s
    return None

def find_text(scope, text, tag=None):
    """Find the first element whose stripped text == text."""
    if scope is None: return None
    for el in scope.find_all(tag or True):
        if el.string and el.string.strip() == text:
            return el
    # fallback: element whose get_text == text
    for el in scope.find_all(tag or True):
        if el.get_text(strip=True) == text:
            return el
    return None

def replace_by_text(scope, mapping, tag=None):
    """Replace elements found by their current exact text."""
    for old, new in mapping.items():
        el = find_text(scope, old, tag)
        if el is not None:
            set_text(el, new)
        else:
            report["miss"] += 1

def set_img(img, src, alt):
    if img is None:
        report["miss"] += 1; return
    img["src"] = src
    img["alt"] = alt
    for a in ("srcset", "sizes", "loading"):
        if a in img.attrs and a != "loading":
            del img.attrs[a]
    img["loading"] = "lazy"
    report["set"] += 1

# =====================================================================
# 1) ASSET PATHS — prefix template-relative refs with the template folder
# =====================================================================
for tag in soup.find_all(["img", "script", "link", "source", "a", "video"]):
    for attr in ("src", "href"):
        v = tag.get(attr)
        if v and re.match(r'^(css/|js/|images/|media/)', v):
            tag[attr] = ASSET_PREFIX + v
    # srcset
    ss = tag.get("srcset")
    if ss:
        tag["srcset"] = re.sub(r'(^|,\s*)(images/)', lambda m: m.group(1) + ASSET_PREFIX + "images/", ss)

# inline style url(images/..)
for tag in soup.find_all(style=True):
    tag["style"] = re.sub(r'url\((images/)', "url(" + ASSET_PREFIX + r"\1", tag["style"])

# =====================================================================
# 2) HEAD — title / description / og / lang
# =====================================================================
html_tag = soup.find("html")
if html_tag: html_tag["lang"] = "pl"
if soup.title: soup.title.string = "BIG-MARK — Remonty mieszkań i wykończenia wnętrz Lublin"
for m in soup.find_all("meta"):
    if m.get("name") == "description" or m.get("property") == "og:description":
        m["content"] = ("Remonty mieszkań, łazienek, układanie płytek, elektryka G1, ogrzewanie gazowe G3 "
                        "i prace wykończeniowe w Lublinie i okolicach. Zostaw zgłoszenie do BIG-MARK.")
    if m.get("property") == "og:title":
        m["content"] = "BIG-MARK — Remonty mieszkań i wykończenia wnętrz Lublin"
    if m.get("property") in ("og:image",) and m.get("content"):
        m["content"] = PH(1)

# ---------- favicon: BIG-MARK emblem (replaces the template's Flampt icons) ----------
for link in soup.find_all("link"):
    rels = link.get("rel") or []
    if "shortcut" in rels or "icon" in rels or "apple-touch-icon" in rels:
        link.decompose()
_head = soup.head
for _attrs in (
    {"rel": "icon", "type": "image/png", "sizes": "256x256", "href": "assets/favicon-256.png"},
    {"rel": "icon", "type": "image/png", "sizes": "32x32",   "href": "assets/favicon-32.png"},
    {"rel": "apple-touch-icon", "sizes": "180x180",          "href": "assets/apple-touch-icon.png"},
):
    _head.append(soup.new_tag("link", **_attrs))

# brand colour override + custom additions (popup / sticky / form) injected at end of <head>
OVERRIDE_CSS = """
/* ===== BIG-MARK brand override (gold/graphite) =====
   real Webflow var names are --_colors---* (with prefix) */
:root, body{
  --_colors---neon-lime:#E49C0C;
  --_colors---deep-plum:#232220;
  --_colors---mist-white:#FBF7EF;
  --_colors---slate-charcoal:#33302A;
}
.rt-change-color-orange{ color:#E49C0C !important; }

/* ===== Header: big logo, compact harmonious bar ===== */
.rt-site-logo{ height:118px !important; width:auto !important; }
.rt-navbar-wrapper-v4{ padding-top:.4rem !important; padding-bottom:.4rem !important; align-items:center; }
.rt-navbar-top-tag{ font-size:.82rem; }
@media (max-width:767px){ .rt-site-logo{ height:64px !important; } }

/* ===== Logo: two images toggled by scroll — white over the glassy hero header,
   gold/graphite once the header turns solid white on scroll.
   The template's IX2 navbar interaction injects an inline `filter:invert(100%)`
   on scroll (it was meant for the original dark template logo). That inversion
   turns our gold/graphite PNG into a white/blue ghost, so we hard-disable any
   filtering on the logo — !important beats the inline style IX2 sets. ===== */
.rt-brand-logo{ display:inline-flex; align-items:center; }
.bm-logo{ display:block; filter:none !important; -webkit-filter:none !important; }
.rt-brand-logo .bm-logo-dark{ display:none; }
.bm-scrolled .rt-brand-logo .bm-logo-light{ display:none; }
.bm-scrolled .rt-brand-logo .bm-logo-dark{ display:block; }

/* ===== Header: glassy transparent blur at the top (template look kept), turning a
   clean SOLID white on scroll. The white-on-scroll overrides ALL three navbar layers
   incl. the navy tint on rt-navbar-wrapper-v6, so no blue ghost remains. ===== */
.rt-navbar-v7{ transition:background-color .3s ease, box-shadow .3s ease; }
.bm-scrolled .rt-navbar-outer-wrapper-v1{ background-color:#fff !important;
  box-shadow:0 10px 34px -16px rgba(20,18,15,.22); border-bottom:1px solid rgba(20,18,15,.08); }
.bm-scrolled .rt-navbar-wrapper-v6{ background-color:#fff !important; background-image:none !important; }
.bm-scrolled .rt-navbar-v7{ background-color:#fff !important; background-image:none !important;
  -webkit-backdrop-filter:none !important; backdrop-filter:none !important; }
.bm-scrolled .rt-navigation-link-v1, .bm-scrolled .rt-navbar-top-tag{ color:#232220 !important; }

/* ===== Header nav links: thin gold accent underline on hover ===== */
.rt-navigation-link-v1{ position:relative; }
.rt-navigation-link-v1::after{ content:""; position:absolute; left:0; right:0; bottom:-7px; height:2px;
  background:#E49C0C; border-radius:2px; transform:scaleX(0); transform-origin:left center;
  transition:transform .28s cubic-bezier(.2,.7,.2,1); }
.rt-navigation-link-v1:hover::after{ transform:scaleX(1); }
.rt-navigation-link-v1:hover{ color:#E49C0C !important; }

/* ===== Footer: trimmer height ===== */
.rt-footer-bottom-wrapper{ padding-top:3rem !important; padding-bottom:2.4rem !important; }
.bm-footer-logo{ height:200px; width:auto; max-width:100%; margin:-14px 0 8px -10px; display:block; }
.bm-footer-copy{ color:rgba(35,34,32,.6); font-size:.9rem; }
/* left-align footer columns near the logo with even gaps + 2-line description */
.rt-footer-content-wrap{ justify-content:flex-start !important; gap:4.75rem !important; flex-wrap:wrap; }
.rt-footer-col-v1{ max-width:25rem !important; }
.rt-footer-description-gap{ max-width:24rem; }
.rt-footer-grid-wrapper{ grid-column-gap:4.5rem !important; grid-template-columns:repeat(3,auto) !important; }
/* footer map */
.bm-footer-map{ flex:1 1 24rem; min-width:18rem; max-width:34rem; }
.bm-footer-map iframe{ width:100%; height:240px; border:0; display:block; border-radius:1rem;
  box-shadow:0 18px 40px -28px rgba(20,18,15,.35); filter:grayscale(.15); }
@media (max-width:767px){ .bm-footer-logo{ height:150px; } .rt-footer-content-wrap{ gap:2.5rem !important; }
  .rt-footer-grid-wrapper{ grid-column-gap:2.5rem !important; } .bm-footer-map{ flex-basis:100%; }
  .bm-footer-map iframe{ height:200px; } }

/* ===== Hero headline: exactly two lines ===== */
.rt-hero-left-content-wrapper h1{ max-width:none; }
.bm-hero-eyebrow{ opacity:.8 !important; }
.bm-hl{ display:block; opacity:0; transform:translateY(30px);
  animation:bmHeroIn .85s cubic-bezier(.2,.7,.2,1) forwards; }
.bm-hl:nth-child(2){ animation-delay:.14s; }
@keyframes bmHeroIn{ to{ opacity:1; transform:none; } }
@media (min-width:600px){ .bm-hl{ white-space:nowrap; } }
/* hero h1 line break "Remonty mieszkań" / "w Lublinie" — mobile only; desktop stays one line */
.bm-br-m{ display:none; }
@media (max-width:599px){ .bm-br-m{ display:inline; } }
@media (prefers-reduced-motion:reduce){ .bm-hl{ opacity:1; transform:none; animation:none; } }

/* ===== Flampt-style rounded white transition + PRZEWIŃ W DÓŁ badge =====
   Rotating dark glass disc sits BEHIND the white transition; a centred white
   "tent" mask pokes up to notch the disc, with a static dark arrow in the notch
   — pixel-matched to the template. */
.bm-transition-wrap{ position:relative; margin-top:-118px; z-index:15; }
/* white panel: straight top (rounded far corners), covers the disc below the seam */
.bm-hero-transition{ position:relative; z-index:3; height:118px; background:#fff;
  border-top-left-radius:3.125rem; border-top-right-radius:3.125rem; }
/* dark rotating disc, mostly above the seam, its bottom hidden behind the white panel */
.bm-sd-badge{ position:absolute; left:50%; top:0; transform:translate(-50%,-64%);
  width:136px; height:136px; border-radius:50%; cursor:pointer; padding:0;
  background:rgba(0,0,0,.2); -webkit-backdrop-filter:blur(25px); backdrop-filter:blur(25px);
  border:.5px solid rgba(255,255,255,.1); display:block; z-index:2;
  box-shadow:0 18px 40px -20px rgba(20,18,15,.4); }
.bm-sd-ring{ position:absolute; inset:0; width:100%; height:100%; animation:bmSpin 20s linear infinite; }
.bm-sd-ring text{ fill:#fff; font-size:11px; font-weight:500; letter-spacing:1.2px; font-family:'Inter',sans-serif; }
/* white tent mask: base on the seam, peak rising into the disc bottom (the notch) */
.bm-sd-mask{ position:absolute; left:50%; top:0; transform:translate(-50%,-99%);
  width:150px; height:auto; z-index:4; pointer-events:none; display:block; }
/* static dark down-arrow seated in the notch */
.bm-sd-arrow{ position:absolute; left:50%; top:0; transform:translate(-50%,-3px);
  z-index:5; display:flex; align-items:center; justify-content:center; cursor:pointer; }
.bm-sd-arrow img{ width:14px; height:18px; display:block; }
@keyframes bmSpin{ to{ transform:rotate(-360deg); } }
@media (max-width:991px){
  .bm-transition-wrap{ margin-top:-86px; }
  .bm-hero-transition{ height:86px; border-top-left-radius:2rem; border-top-right-radius:2rem; }
  .bm-sd-badge{ width:112px; height:112px; }
  .bm-sd-ring text{ font-size:10px; letter-spacing:.8px; }
  .bm-sd-mask{ width:124px; }
}
@media (max-width:600px){
  .bm-transition-wrap{ margin-top:-58px; }
  .bm-hero-transition{ height:58px; border-top-left-radius:1.4rem; border-top-right-radius:1.4rem; }
  .bm-sd-badge{ width:88px; height:88px; }
  .bm-sd-ring text{ font-size:8.5px; letter-spacing:.5px; }
  .bm-sd-mask{ width:98px; }
}
@media (prefers-reduced-motion:reduce){ .bm-sd-ring{ animation:none; } }

/* ===== Hero: clean graphite gradient overlays (was muddy brown #52270f) ===== */
.rt-hero-v1-left-linear{ background-image:linear-gradient(90deg, rgba(20,18,15,.84), rgba(20,18,15,.46) 46%, rgba(20,18,15,0)) !important; }
.rt-hero-v1-right-linear{ background-image:linear-gradient(90deg, rgba(20,18,15,0), rgba(20,18,15,.5)) !important; }
.rt-hero-v1-top-linear{ background-image:linear-gradient(rgba(20,18,15,.66), rgba(20,18,15,.34) 24%, rgba(20,18,15,0) 52%) !important; }

/* ===== Hero right card: neutral glass (remove green), spacing, tighter caption ===== */
.rt-hero-right-content-wrapper{ background-color:rgba(18,16,13,.32) !important; background-image:none !important;
  -webkit-backdrop-filter:blur(16px); backdrop-filter:blur(16px); border:1px solid rgba(255,255,255,.14); }
.rt-hero-video-description{ margin-top:18px !important; }
.rt-hero-video-description .rt-text-color-white{ line-height:1.24 !important; }

/* ===== About-us: remove image cutout mask + one-line stat label ===== */
.rt-about-us-image-wrapper.rt-mask-v5{ -webkit-mask-image:none !important; mask-image:none !important; }
.rt-overlap-bottom{ white-space:nowrap !important; }

/* ===== About-us stat card: glassmorphism, nudged onto the photo ===== */
.rt-about-us-left-overlap-box{ inset:auto auto 7% 6% !important; max-width:18rem !important;
  background-color:rgba(24,21,17,.42) !important; background-image:none !important;
  -webkit-backdrop-filter:blur(18px) saturate(120%); backdrop-filter:blur(18px) saturate(120%);
  border:1px solid rgba(255,255,255,.22);
  border-top-left-radius:1rem; border-top-right-radius:1rem; border-bottom-left-radius:1rem; border-bottom-right-radius:1rem;
  box-shadow:0 24px 50px -24px rgba(20,18,15,.55); padding:1.6rem 1.7rem !important; }
.rt-about-us-left-overlap-box .rt-font-size-48{ color:#fff !important; }
.rt-about-us-left-overlap-box .rt-overlap-bottom,
.rt-about-us-left-overlap-box .rt-overlap-bottom .rt-text-style-h5,
.rt-about-us-left-overlap-box .rt-overlap-bottom div{ color:rgba(255,255,255,.8) !important; }
@media (max-width:600px){ .rt-about-us-left-overlap-box{ inset:auto auto 5% 5% !important; padding:1.2rem 1.3rem !important; } }

/* ===== Buttons: hover fill colour #2C2C2C + keep label readable (white) ===== */
.rt-button-overlap, .rt-button-overlap-v1{ background-color:#2C2C2C !important; }
.rt-button:hover .rt-text-style-button,
.rt-button:hover .rt-button-color-change,
a:hover > .rt-text-style-button.rt-button-color-change{ color:#fff !important; }

/* ===== Prace specjalistyczne: drop the corner cut-out (subtract) on the image ===== */
.rt-image-mask-wrapper.rt-mask-v2{ -webkit-mask-image:none !important; mask-image:none !important; }

/* ===== Usługi: header (left title + right CTA) + uniform card grid ===== */
.bm-uslugi-head, .bm-uslugi-grid{ width:100%; }
.bm-uslugi-head{ display:flex; align-items:flex-end; justify-content:space-between; gap:30px; flex-wrap:wrap; margin-bottom:44px; }
.bm-uslugi-head-left{ min-width:0; }
.bm-eyebrow{ display:inline-flex; align-items:center; gap:10px; font-weight:600; font-size:.78rem; letter-spacing:.14em;
  text-transform:uppercase; color:#E49C0C; margin-bottom:16px; }
.bm-eyebrow::before{ content:""; width:13px; height:13px; background:#E49C0C; border-radius:50%; flex:none; }
/* Usługi eyebrow: dark label text, accent dot kept */
.bm-uslugi-head-left .bm-eyebrow{ color:#2C2C2C; }
.bm-uslugi-title{ font-family:inherit; font-size:clamp(1.4rem,2.3vw,2.15rem); line-height:1.12; color:#232220; margin:0; font-weight:600; }
@media (min-width:780px){ .bm-uslugi-title{ white-space:nowrap; } }
.bm-uslugi-cta{ display:inline-flex; align-items:center; gap:10px; background:#E49C0C; color:#232220; font-weight:600;
  font-size:1rem; border:none; border-radius:999px; padding:15px 26px; cursor:pointer; white-space:nowrap;
  transition:transform .2s, background .2s, color .2s; font-family:inherit; }
.bm-uslugi-cta:hover{ transform:translateY(-2px); background:#2C2C2C; color:#fff; }
.bm-uslugi-cta svg{ width:18px; height:18px; }
.bm-uslugi-grid{ display:grid; grid-template-columns:repeat(3,1fr); gap:22px; }
.bm-svc-card{ position:relative; border-radius:22px; overflow:hidden; aspect-ratio:1/1; cursor:pointer;
  box-shadow:0 18px 40px -28px rgba(46,33,12,.42); transition:transform .35s, box-shadow .35s; }
.bm-svc-card:hover{ transform:translateY(-4px); box-shadow:0 28px 56px -30px rgba(46,33,12,.5); }
.bm-svc-card:focus-visible{ outline:3px solid #E49C0C; outline-offset:3px; }
.bm-svc-img{ position:absolute; inset:0; }
.bm-svc-img img{ width:100%; height:100%; object-fit:cover; transition:transform .7s cubic-bezier(.2,.7,.2,1); }
.bm-svc-card:hover .bm-svc-img img{ transform:scale(1.07); }
.bm-svc-card::after{ content:""; position:absolute; inset:0; z-index:1;
  background:linear-gradient(180deg, rgba(20,18,14,.05) 28%, rgba(20,18,14,.86)); }
.bm-svc-body{ position:absolute; left:0; right:0; bottom:0; z-index:2; padding:24px; color:#fff; }
.bm-svc-body h3{ color:#fff; font-family:inherit; font-weight:600; font-size:1.35rem; margin:0; line-height:1.15; }
.bm-svc-body p{ color:rgba(255,255,255,.86); font-size:.92rem; margin:0; max-height:0; opacity:0; overflow:hidden;
  transform:translateY(6px); transition:max-height .45s ease, opacity .35s ease, transform .35s ease, margin-top .45s ease; }
.bm-svc-card:hover .bm-svc-body p{ max-height:140px; opacity:1; transform:none; margin-top:9px; }
.bm-svc-arrow{ position:absolute; top:18px; right:18px; z-index:3; width:42px; height:42px; border-radius:50%;
  background:#E49C0C; color:#232220; display:flex; align-items:center; justify-content:center;
  transform:translateY(-8px) scale(.82); opacity:0; transition:.3s; }
.bm-svc-card:hover .bm-svc-arrow{ transform:none; opacity:1; }
.bm-svc-arrow svg{ width:18px; height:18px; }
@media (max-width:991px){ .bm-uslugi-grid{ grid-template-columns:repeat(2,1fr); } }
@media (max-width:600px){ .bm-uslugi-grid{ grid-template-columns:1fr; } .bm-uslugi-head{ align-items:flex-start; }
  .bm-uslugi-cta{ width:100%; justify-content:center; } }

/* ===== Nasze realizacje: category tabs + uniform image grid ===== */
.bm-real-wrap{ width:100%; }
.bm-real-tabs{ display:flex; flex-wrap:wrap; gap:10px; margin:6px 0 30px; }
.bm-real-tab{ border:1.5px solid rgba(255,255,255,.26); background:transparent; color:rgba(255,255,255,.82); font-family:inherit;
  font-weight:600; font-size:.95rem; padding:10px 22px; border-radius:999px; cursor:pointer;
  transition:background .2s, color .2s, border-color .2s; }
.bm-real-tab:hover{ border-color:#E49C0C; color:#fff; }
.bm-real-tab.is-active{ background:#E49C0C; border-color:#E49C0C; color:#232220; }
.bm-real-grid{ display:grid; grid-template-columns:repeat(3,1fr); gap:22px; }
.bm-real-card{ position:relative; border-radius:20px; overflow:hidden; aspect-ratio:4/3; cursor:pointer;
  box-shadow:0 18px 40px -28px rgba(46,33,12,.42); transition:transform .35s, box-shadow .35s; }
.bm-real-card:hover{ transform:translateY(-4px); box-shadow:0 28px 56px -30px rgba(46,33,12,.5); }
.bm-real-card:focus-visible{ outline:3px solid #E49C0C; outline-offset:3px; }
.bm-real-card.is-hidden{ display:none; }
.bm-real-img{ position:absolute; inset:0; }
.bm-real-img img{ width:100%; height:100%; object-fit:cover; transition:transform .7s cubic-bezier(.2,.7,.2,1); }
.bm-real-card:hover .bm-real-img img{ transform:scale(1.06); }
.bm-real-card::after{ content:""; position:absolute; inset:0; z-index:1;
  background:linear-gradient(180deg, rgba(20,18,14,0) 40%, rgba(20,18,14,.82)); }
.bm-real-cap{ position:absolute; left:0; right:0; bottom:0; z-index:2; padding:20px 22px; color:#fff; }
.bm-real-loc{ display:block; font-size:.78rem; font-weight:600; letter-spacing:.1em; text-transform:uppercase;
  color:#F0A818; margin-bottom:6px; }
.bm-real-cap h3{ color:#fff; font-family:inherit; font-weight:600; font-size:1.18rem; margin:0; line-height:1.2; }
@media (max-width:991px){ .bm-real-grid{ grid-template-columns:repeat(2,1fr); } }
@media (max-width:600px){ .bm-real-grid{ grid-template-columns:1fr; } }

/* ===== Opinie: clean, readable Google-style review cards ===== */
.bm-rev-wrap{ width:100%; flex-direction:column !important; }
.bm-rev-head{ max-width:46rem; margin:0 auto 40px; text-align:center; }
.bm-rev-head .bm-eyebrow{ justify-content:center; }
.bm-rev-title{ font-family:inherit; font-size:clamp(1.7rem,3vw,2.6rem); line-height:1.12; color:#232220; margin:0 0 12px; font-weight:600; }
.bm-rev-sub{ color:#6b6459; font-size:1rem; margin:0; }
.bm-rev-glink{ display:inline-flex; align-items:center; gap:9px; margin-top:16px; font-weight:600; font-size:.95rem;
  color:#232220; border:1.5px solid rgba(35,34,32,.16); border-radius:999px; padding:9px 18px; transition:.2s; }
.bm-rev-glink:hover{ border-color:#E49C0C; background:#fff; }
.bm-rev-glink svg{ width:18px; height:18px; }
/* single-row carousel with arrows */
.bm-rev-carousel{ position:relative; width:100%; }
.bm-rev-track{ display:flex; gap:22px; width:100%; overflow-x:auto; scroll-snap-type:x mandatory;
  scroll-behavior:smooth; padding:6px 2px 18px; scrollbar-width:none; -ms-overflow-style:none; }
.bm-rev-track::-webkit-scrollbar{ display:none; }
.bm-rev-nav{ position:absolute; top:calc(50% - 9px); transform:translateY(-50%); width:50px; height:50px; border-radius:50%;
  background:#fff; border:1px solid rgba(35,34,32,.12); color:#232220; cursor:pointer; z-index:4;
  display:flex; align-items:center; justify-content:center; box-shadow:0 12px 30px -12px rgba(20,18,15,.28); transition:.2s; }
.bm-rev-nav:hover{ background:#E49C0C; border-color:#E49C0C; }
.bm-rev-nav svg{ width:22px; height:22px; }
.bm-rev-prev{ left:-22px; } .bm-rev-next{ right:-22px; }
.bm-rev-next svg{ transform:rotate(180deg); }
.bm-rev-card{ scroll-snap-align:start; flex:0 0 calc((100% - 44px)/3); min-width:300px;
  background:#fff; border:1px solid rgba(35,34,32,.1); border-radius:18px; padding:24px;
  box-shadow:0 16px 38px -30px rgba(46,33,12,.4); display:flex; flex-direction:column; gap:14px; }
.bm-rev-top{ display:flex; align-items:center; gap:12px; }
.bm-rev-av{ width:46px; height:46px; border-radius:50%; background:#E49C0C; color:#232220; font-weight:700;
  font-size:1.2rem; display:flex; align-items:center; justify-content:center; flex:none; }
.bm-rev-id{ display:flex; flex-direction:column; line-height:1.25; min-width:0; }
.bm-rev-id b{ color:#232220; font-size:1.02rem; }
.bm-rev-id span{ color:#8c8578; font-size:.84rem; }
.bm-rev-g{ width:22px; height:22px; margin-left:auto; flex:none; }
.bm-rev-stars{ display:flex; gap:3px; color:#FBBC05; }
.bm-rev-stars svg{ width:18px; height:18px; }
.bm-rev-text{ color:#4a463f; font-size:.98rem; line-height:1.55; margin:0; }
@media (max-width:991px){ .bm-rev-card{ flex:0 0 calc((100% - 22px)/2); } .bm-rev-prev{ left:-10px; } .bm-rev-next{ right:-10px; } }
@media (max-width:600px){ .bm-rev-card{ flex:0 0 86%; } .bm-rev-nav{ display:none; } }

/* ===== More breathing room between Opinie and Zostaw zgłoszenie ===== */
.rt-testimonial-slider{ padding-bottom:6.5rem !important; }
.rt-cta{ padding-top:5rem !important; }
@media (max-width:600px){ .rt-testimonial-slider{ padding-bottom:4rem !important; } }

/* ===== CTA container: drop the baked-in corner subtract (cta.avif had a transparent notch) ===== */
.rt-cta-main-wrapper{ background-image:none !important; background-color:var(--_colors---mist-white) !important; }
/* CTA lead paragraph: two lines, 80% opacity */
.bm-cta-lead{ color:rgba(35,34,32,.8) !important; }
.bm-cta-lead br{ display:block; }
/* desktop only: each sentence on its own single line (2 lines total). The text
   column is wide enough (632px) for both sentences, but the paragraph is capped
   at 528px — lift that cap and stop wrapping so the <br> yields exactly two lines.
   Mobile (<=600px) keeps the flowing one-paragraph version untouched. */
@media (min-width:601px){ .bm-cta-lead{ max-width:none !important; white-space:nowrap; } }
@media (max-width:600px){ .bm-cta-lead br{ display:none; } }

/* ===== Hero right: photo-montage at reference size (reads as video) ===== */
.rt-hero-background-video.bm-slideshow{ position:relative; width:100%; }
.bm-slideshow.paused img{ animation-play-state:paused; }
.bm-slideshow img{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; opacity:0; animation:bmKen 30s infinite; will-change:opacity,transform; }
.bm-slideshow img:nth-child(1){ animation-delay:0s; }
.bm-slideshow img:nth-child(2){ animation-delay:6s; }
.bm-slideshow img:nth-child(3){ animation-delay:12s; }
.bm-slideshow img:nth-child(4){ animation-delay:18s; }
.bm-slideshow img:nth-child(5){ animation-delay:24s; }
@keyframes bmKen{ 0%{opacity:0;transform:scale(1.05)} 3%{opacity:1} 17%{opacity:1;transform:scale(1.12)} 20%{opacity:0;transform:scale(1.12)} 100%{opacity:0} }
@media (prefers-reduced-motion:reduce){ .bm-slideshow img{ animation:none } .bm-slideshow img:nth-child(1){ opacity:1 } }

/* ===== BIG-MARK lead form (uses native template field look) ===== */
.bm-form{display:flex;flex-direction:column;gap:14px;width:100%}
.bm-form .bm-row{display:flex;gap:14px;flex-wrap:wrap}
.bm-form .bm-row > *{flex:1;min-width:160px}
.bm-form input,.bm-form textarea{
  width:100%;padding:15px 18px;border-radius:12px;border:1.5px solid rgba(255,255,255,.22);
  background:rgba(255,255,255,.06);color:#fff;font-family:inherit;font-size:1rem;outline:none;
}
.bm-form input::placeholder,.bm-form textarea::placeholder{color:rgba(255,255,255,.55)}
.bm-form input:focus,.bm-form textarea:focus{border-color:#E49C0C;box-shadow:0 0 0 4px rgba(228,156,12,.18)}
.bm-form textarea{min-height:96px;resize:vertical}
.bm-form .bm-check{display:flex;gap:10px;align-items:flex-start;color:rgba(255,255,255,.8);font-size:.9rem;cursor:pointer}
.bm-form .bm-check input{width:20px;height:20px;flex:none;accent-color:#E49C0C}
.bm-form .bm-check a{color:#E49C0C;text-decoration:underline}
.bm-form button{
  background:#E49C0C;color:#232220;border:none;border-radius:999px;padding:16px 28px;font-weight:700;
  font-size:1rem;cursor:pointer;transition:transform .2s,background .2s;font-family:inherit;
}
.bm-form button:hover{transform:translateY(-2px);background:#C5850A}
.bm-form.bm-light input,.bm-form.bm-light textarea{background:#fff;color:#232220;border-color:rgba(40,36,28,.2)}
.bm-form.bm-light input::placeholder,.bm-form.bm-light textarea::placeholder{color:#8c8578}
.bm-form.bm-light .bm-check{color:#6b6459}
.bm-field-error{border-color:#cf4b2e !important;box-shadow:0 0 0 4px rgba(207,75,46,.14) !important}
.bm-success{display:none;text-align:center;color:inherit;padding:18px 0}
.bm-success.show{display:block}
.bm-success .bm-tick{width:64px;height:64px;border-radius:50%;background:#E49C0C;color:#232220;display:flex;align-items:center;justify-content:center;margin:0 auto 14px;font-size:30px}

/* ===== popup ===== */
.bm-overlay{position:fixed;inset:0;z-index:9999;background:rgba(20,16,10,.6);backdrop-filter:blur(4px);
  display:flex;align-items:center;justify-content:center;padding:20px;opacity:0;visibility:hidden;transition:.3s}
.bm-overlay.open{opacity:1;visibility:visible}
.bm-modal{background:#232220;color:#fff;border-radius:24px;max-width:480px;width:100%;padding:38px;position:relative;
  transform:translateY(24px) scale(.97);transition:transform .35s cubic-bezier(.4,0,.2,1);max-height:92vh;overflow:auto}
.bm-overlay.open .bm-modal{transform:none}
.bm-modal h3{font-size:1.6rem;margin:0 0 6px}
.bm-modal p.bm-sub{color:rgba(255,255,255,.7);margin:0 0 20px;font-size:.95rem}
.bm-close{position:absolute;top:14px;right:14px;width:40px;height:40px;border-radius:50%;border:none;
  background:rgba(255,255,255,.1);color:#fff;font-size:22px;cursor:pointer}
.bm-close:hover{background:rgba(255,255,255,.2)}
.bm-modal .bm-alt{margin-top:16px;text-align:center;font-size:.9rem;color:rgba(255,255,255,.6)}
.bm-modal .bm-alt a{color:#E49C0C;font-weight:600}

/* ===== sticky mobile CTA + floating widget ===== */
.bm-mobilebar{position:fixed;left:0;right:0;bottom:0;z-index:9000;display:none;gap:10px;
  padding:10px 14px calc(10px + env(safe-area-inset-bottom));background:rgba(35,34,32,.96);backdrop-filter:blur(10px)}
.bm-mobilebar a,.bm-mobilebar button{flex:1;border:none;border-radius:999px;padding:14px;font-weight:700;font-size:.95rem;
  text-align:center;cursor:pointer;font-family:inherit;text-decoration:none;display:flex;align-items:center;justify-content:center;gap:8px}
.bm-mobilebar .bm-mc-main{background:#E49C0C;color:#232220}
.bm-mobilebar .bm-mc-wa{background:#1f8a4c;color:#fff;flex:none;width:52px}
.bm-mobilebar .bm-mc-call{background:#fff;color:#232220;flex:none;width:52px}
/* hide "Made in Webflow" badge */
.w-webflow-badge{ display:none !important; }
.bm-fab{position:fixed;right:24px;bottom:24px;z-index:9000;display:flex;flex-direction:column;gap:12px;align-items:flex-end;
  opacity:0;visibility:hidden;transform:translateY(18px);transition:opacity .3s,transform .3s,visibility .3s}
.bm-fab.bm-show{opacity:1;visibility:visible;transform:none}
.bm-fab a{width:56px;height:56px;border-radius:50%;display:flex;align-items:center;justify-content:center;
  box-shadow:0 14px 30px -10px rgba(0,0,0,.4);transition:transform .2s;text-decoration:none}
.bm-fab a:hover{transform:scale(1.08)}
.bm-fab .bm-fwa{background:#1f8a4c}
.bm-fab .bm-fcall{background:#E49C0C}
.bm-fab a svg{width:26px;height:26px}
@media(max-width:767px){ .bm-mobilebar{display:flex} .bm-fab{display:none} body{padding-bottom:72px} }

/* =====================================================================
   MOBILE-ONLY refinements (≤767px) — BIG-MARK
   ===================================================================== */

/* (1a) Burger-menu social icons (Facebook + WhatsApp) */
.bm-nav-social{ display:flex; gap:12px; margin-top:14px; flex-wrap:wrap; }
.bm-nav-social-link{ width:46px; height:46px; border-radius:50%; display:flex; align-items:center;
  justify-content:center; background:#232220; color:#fff; transition:transform .2s, background .2s, color .2s; }
.bm-nav-social-link:hover{ transform:translateY(-2px); background:#E49C0C; color:#232220; }
.bm-nav-social-link svg{ width:21px; height:21px; display:block; }
.bm-nav-social-wa{ background:#1f8a4c; }
.bm-nav-social-wa:hover{ background:#E49C0C; color:#232220; }

/* (6) Opinie pagination dots — visible only on mobile (arrows are hidden there) */
.bm-rev-dots{ display:none; }
.bm-rev-dot{ width:9px; height:9px; padding:0; border:none; border-radius:50%; cursor:pointer;
  background:rgba(35,34,32,.2); transition:background .2s, transform .2s; }
.bm-rev-dot.is-active{ background:#E49C0C; transform:scale(1.25); }

@media (max-width:767px){
  /* (1a) Whole hero text block (eyebrow + heading + paragraph + buttons) nudged lower.
     transform (not margin) so it shifts visually WITHOUT growing the hero box —
     the white transition panel + "przewiń w dół" disc stay exactly where they were. */
  .rt-hero-left-content-wrapper{ transform:translateY(120px); }

  /* (1b) Hero banner buttons -> full width, stacked; offer nudged a bit lower */
  .rt-hero-button-wrapper{ flex-direction:column; align-items:stretch; width:100%; gap:12px; margin-top:22px; }
  .rt-hero-button-wrapper > div{ width:100%; }
  .rt-hero-button-wrapper .rt-button,
  .rt-hero-button-wrapper .rt-button-v5{ width:100%; display:flex; justify-content:center; text-align:center; }

  /* (1c) "Przewiń w dół" badge moment dropped lower — extend the dark hero
     photo so the WHOLE seam (white transition panel + rotating disc + notch) moves
     down together and the disc keeps straddling the dark/white edge, exactly like
     desktop. (Padding on the bg box stretches the absolute photo + gradients; the
     hero content stays top-aligned, so only dark space is added beneath it.)
     +80px beyond the previous drop, per request. */
  .rt-hero-background{ padding-bottom:260px; }

  /* (2) About-us: heading -> image -> text -> button (button full width) */
  .rt-about-us-main-wrapper{ display:flex; flex-direction:column; align-items:stretch; gap:1.4rem; }
  .rt-about-us-right{ display:contents; }
  .rt-about-us-right > .rt-hero-top-subtext{ order:1; }
  .rt-about-us-right > h2{ order:2; margin-top:-0.95rem; }   /* tighten eyebrow -> heading */
  .rt-about-us-left{ order:3; width:100%; }
  .rt-about-us-right > .rt-abouts-us-right-description{ order:4; }
  .rt-about-us-right > .rt-right-middle-content-wrapper{ order:5; }
  .rt-about-us-right > .bm-about-cta{ order:6; width:100%; margin-top:-0.7rem; }   /* tighten text -> button */
  .bm-about-cta .bm-about-btn{ width:100%; display:flex; justify-content:center; text-align:center; }

  /* (3) Usługi: CTA moved below the grid; cards overlap on scroll */
  .rt-service-main-wrapper{ display:flex; flex-direction:column; }
  .bm-uslugi-head{ display:contents; }
  .bm-uslugi-head-left{ order:1; margin-bottom:22px; }
  .bm-uslugi-grid{ order:2; display:block; }
  .bm-uslugi-cta{ order:3; width:100%; justify-content:center; margin-top:26px; }
  .bm-uslugi-grid .bm-svc-card{ position:sticky; top:84px; margin-bottom:18px;
    box-shadow:0 22px 48px -24px rgba(20,18,15,.55); }
  .bm-uslugi-grid .bm-svc-card:nth-child(2){ top:98px; }
  .bm-uslugi-grid .bm-svc-card:nth-child(3){ top:112px; }
  .bm-uslugi-grid .bm-svc-card:nth-child(4){ top:126px; }
  .bm-uslugi-grid .bm-svc-card:nth-child(5){ top:140px; }
  .bm-uslugi-grid .bm-svc-card:nth-child(6){ top:154px; }
  /* touch has no hover -> always reveal the card description */
  .bm-uslugi-grid .bm-svc-body p{ max-height:140px; opacity:1; transform:none; margin-top:9px; }
  .bm-uslugi-grid .bm-svc-arrow{ opacity:1; transform:none; }

  /* (4) Prace specjalistyczne: no image-switching on tap + hide switching images */
  .rt-why-choose-bottom-right{ display:none !important; }
  .rt-why-choose-left-top-item-one{ pointer-events:none; min-width:0; }
  /* row 01 carried an IX2 "active" inline transform (+1.5625rem to the right) that
     pushed its long label off-screen — reset it so every row lines up + wraps */
  .rt-why-choose-left-text{ transform:none !important; min-width:0; }
  .rt-why-choose-left-text .rt-text-style-h3{ overflow-wrap:anywhere; font-weight:400 !important; }

  /* (5) Realizacje: cards overlap on scroll; CTA moved below + full width */
  .rt-featured-project-main-wrapper{ display:flex; flex-direction:column; }
  .rt-featured-project-top-content{ display:contents; }
  .rt-featured-project-top-left{ order:1; }
  .rt-featured-project-bottom-content-main{ order:2; margin-top:1.5rem; }   /* heading -> categories gap */
  .rt-blog-top-right-wrapper-v1{ order:3; width:100%; margin-top:26px; align-items:stretch; }
  .rt-blog-top-right-wrapper-v1 .bm-real-btn{ width:100%; display:flex; justify-content:center; text-align:center; }
  .bm-real-grid{ display:block; }
  .bm-real-grid .bm-real-card{ position:sticky; top:88px; margin-bottom:18px;
    box-shadow:0 22px 48px -24px rgba(20,18,15,.55); }

  /* (6) show the dots on mobile */
  .bm-rev-dots{ display:flex; justify-content:center; gap:9px; margin-top:6px; }

  /* (6b) tighter gap between Opinie and the "Zostaw zgłoszenie" block */
  .rt-testimonial-slider{ padding-bottom:2rem !important; }
  .rt-cta{ padding-top:2rem !important; }

  /* (7) CTA "Zostaw zgłoszenie": taller container + full-width button */
  .rt-cta-main-wrapper{ flex-direction:column; }
  .rt-cta-middle-text-content{ padding-top:3rem; padding-bottom:3.25rem; gap:1.15rem; }
  .bm-cta-btn-wrap{ width:100%; }
  .bm-cta-btn{ width:100%; display:flex; justify-content:center; text-align:center; }

  /* FAQ: CTA button full width */
  .bm-faq-btn-wrap{ width:100%; }
  .bm-faq-btn{ width:100%; display:flex; justify-content:center; text-align:center; }

  /* (8) Footer: stop content spilling off the right edge + centre everything */
  .rt-footer-content-wrap{ max-width:100%; gap:2.25rem !important; align-items:center; }
  .rt-footer-grid-wrapper{ grid-template-columns:repeat(2,minmax(0,1fr)) !important;
    grid-column-gap:1.5rem !important; grid-row-gap:2rem !important; width:100%; max-width:100%;
    justify-items:center; text-align:center; }
  .rt-footer-col-v1, .rt-footer-description-gap, .bm-footer-map{ max-width:100% !important; min-width:0 !important; }
  .bm-footer-map{ flex-basis:100% !important; width:100%; }
  .rt-footer-v1, .rt-footer-bottom-wrapper{ overflow-x:clip; }
  /* centre each footer column + its content */
  .rt-footer-col-v1, .rt-footer-col-v2, .rt-footer-col{ align-items:center; text-align:center; }
  .bm-footer-logo{ margin-left:0 !important; margin-right:0 !important; }
  .rt-footer-links{ align-items:center; }
  .rt-footer-links a, .rt-footer-link{ justify-content:center; text-align:center; }
  .rt-footer-left-social-media-wrapper{ flex-direction:column; align-items:center; justify-content:center; }
  .rt-footer-social-media-wrapper{ justify-content:center; }
  .rt-footer-bottom-content{ justify-content:center; text-align:center; }
  .bm-footer-copy{ width:100%; text-align:center; }
}

@media (max-width:479px){
  .rt-footer-grid-wrapper{ grid-template-columns:1fr !important; }
}

/* =====================================================================
   PREMIUM PRELOADER — "Złoty refleks"
   Brand intro: logo resolves from soft->sharp, a gold light sheen sweeps
   across it (masked to the logo silhouette), a thin gold accent line draws
   beneath, then the white panel lifts away with a rounded edge to reveal the
   site — echoing the site's signature rounded white transition.
   Everything is tunable via the CSS variables below.
   ===================================================================== */
:root{
  --bm-pl-bg:#ffffff;                              /* preloader background        */
  --bm-pl-accent:#E49C0C;                          /* brand gold (sheen + line)   */
  --bm-pl-logo:190px;                              /* logo width (desktop)        */
  --bm-pl-in:1.15s;                                /* intro / focus-resolve speed */
  --bm-pl-exit:.85s;                               /* curtain-lift speed          */
  --bm-pl-ease:cubic-bezier(.22,.61,.36,1);        /* intro easing                */
  --bm-pl-min:1900;                                /* min visible time, ms (JS)   */
}
.bm-pl{
  position:fixed; inset:0; z-index:100000;
  display:flex; align-items:center; justify-content:center;
  background:var(--bm-pl-bg);
  transition:transform var(--bm-pl-exit) cubic-bezier(.76,0,.24,1),
             border-radius var(--bm-pl-exit) cubic-bezier(.76,0,.24,1);
  will-change:transform;
}
.bm-pl-stage{ position:relative; display:flex; flex-direction:column; align-items:center; gap:20px;
  transition:opacity .4s ease, transform .5s var(--bm-pl-ease); }
.bm-pl-logo{ position:relative; width:var(--bm-pl-logo); aspect-ratio:1/1;
  opacity:0; transform:scale(.94); filter:blur(7px);
  animation:bmPlIn var(--bm-pl-in) var(--bm-pl-ease) forwards; }
.bm-pl-img{ width:100%; height:100%; object-fit:contain; display:block; }
/* gold light sheen, clipped to the logo silhouette via the PNG alpha mask */
.bm-pl-sheen{ position:absolute; inset:0; pointer-events:none; opacity:0;
  -webkit-mask:url("assets/big-mark_logo_transparent.png") center/contain no-repeat;
          mask:url("assets/big-mark_logo_transparent.png") center/contain no-repeat;
  background:linear-gradient(115deg, transparent 40%, rgba(255,255,255,.55) 47%,
    rgba(255,255,255,.92) 50%, var(--bm-pl-accent) 50.5%, rgba(255,255,255,.92) 53%,
    transparent 60%);
  background-size:260% 100%;
  animation:bmPlSheen 1.25s cubic-bezier(.5,0,.3,1) .5s forwards; }
/* thin gold accent line drawing in beneath the logo */
.bm-pl-line{ width:0; height:2px; border-radius:2px; background:var(--bm-pl-accent); opacity:0;
  animation:bmPlLine 1.3s var(--bm-pl-ease) .35s forwards; }
@keyframes bmPlIn{ to{ opacity:1; transform:scale(1); filter:blur(0); } }
@keyframes bmPlSheen{ 0%{ opacity:0; background-position:170% 0; }
  14%{ opacity:1; } 86%{ opacity:1; } 100%{ opacity:0; background-position:-70% 0; } }
@keyframes bmPlLine{ 0%{ width:0; opacity:0; } 35%{ opacity:.9; } 100%{ width:56px; opacity:.9; } }
/* exit: curtain lifts up, bottom edge arching, revealing the site */
.bm-pl.bm-pl-done{ transform:translateY(-100%);
  border-bottom-left-radius:38%; border-bottom-right-radius:38%; }
.bm-pl.bm-pl-done .bm-pl-stage{ opacity:0; transform:translateY(-14px); }
/* scroll is locked only while the intro is on screen */
html.bm-pl-lock, html.bm-pl-lock body{ overflow:hidden !important; }
@media (max-width:991px){ :root{ --bm-pl-logo:166px; } }
@media (max-width:600px){ :root{ --bm-pl-logo:134px; } }
@media (prefers-reduced-motion:reduce){
  .bm-pl-logo{ animation:none; opacity:1; transform:none; filter:none; }
  .bm-pl-sheen, .bm-pl-line{ animation:none; opacity:0; }
  .bm-pl{ transition:opacity .45s ease; }
  .bm-pl.bm-pl-done{ transform:none; border-radius:0; opacity:0; }
}
"""
style_tag = soup.new_tag("style")
style_tag.string = OVERRIDE_CSS
soup.head.append(style_tag)

# =====================================================================
# 3) REMOVE unwanted sections (block their whole wrapper)
#    blog, video, marquee, feature-v4 sections -> drop
# =====================================================================
def drop_section(cls, wrappers_up=1):
    s = section(cls)
    if s is None:
        report["miss"] += 1; return
    node = s
    for _ in range(wrappers_up):
        if node.parent and node.parent.name == "div":
            node = node.parent
    node.decompose()
    report["set"] += 1

for cls in ["rt-blog-v1", "rt-video", "rt-marquee-v1", "rt-feature-v4"]:
    drop_section(cls, wrappers_up=1)

# =====================================================================
# 4) NAVBAR
# =====================================================================
# remove the top dark strip of the header entirely
top_strip = section("rt-navbar-top")
if top_strip is not None:
    top_strip.decompose(); report["set"] += 1

# logo — single <img> whose src is swapped by JS on scroll: white over the dark
# hero (top), original gold/graphite once the navbar turns solid. Bulletproof
# (no opacity/stacking tricks).
brand = soup.select_one("a.rt-brand-logo")
if brand is not None:
    brand["href"] = "#top"
    base_img = brand.find("img")
    cls = (base_img.get("class") if base_img else None) or ["rt-site-logo"]
    brand.clear()
    # Two stacked logos toggled by scroll state: white over the glassy hero header,
    # gold/graphite once the header turns solid white on scroll.
    light = soup.new_tag("img", src=LOGO_WHITE); light["alt"] = "BIG-MARK"
    light["class"] = list(cls) + ["bm-logo", "bm-logo-light"]
    dark = soup.new_tag("img", src=LOGO); dark["alt"] = "BIG-MARK"
    dark["class"] = list(cls) + ["bm-logo", "bm-logo-dark"]; dark["loading"] = "eager"
    brand.append(light); brand.append(dark)

# rebuild main menu links
menu_holder = soup.find("nav", class_="rt-navbar-v1-menu-holder")
inner = None
if menu_holder:
    inner = menu_holder.find("div", class_="rt-navbar-inner-menu-wrapper")
NAV = [("Dlaczego my", "#dlaczego"), ("Usługi", "#uslugi"), ("Realizacje", "#realizacje"),
       ("Opinie", "#opinie"), ("FAQ", "#faq"), ("Kontakt", "#kontakt")]
if inner:
    inner.clear()
    for label, href in NAV:
        a = soup.new_tag("a", href=href)
        a["class"] = "rt-navigation-link-v1 w-inline-block"
        d = soup.new_tag("div"); d.string = label
        a.append(d); inner.append(a)
    report["set"] += 1

# follow-us heading + social + contact box (inside menu)
replace_by_text(menu_holder or soup, {"Follow us": "Obserwuj nas"})
# social icons (shown in the burger menu) — rebuild as Facebook + WhatsApp with
# inline SVGs. The template's original markup put the href on the OUTER wrapper,
# so the old per-anchor logic wiped them all; build a clean wrapper instead.
follow = soup.select_one(".rt-nav-bottom-follow-content")
if follow is not None:
    old = follow.select_one(".rt-nav-social-icon-wrapper")
    if old is not None:
        old.decompose()
    FB_SVG = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
              '<path d="M22 12.06C22 6.5 17.52 2 12 2S2 6.5 2 12.06c0 5 3.66 9.15 8.44 9.94v-7.03H7.9v-2.9h2.54V9.85c0-2.51 1.49-3.9 3.78-3.9 1.09 0 2.24.2 2.24.2v2.46h-1.26c-1.24 0-1.63.77-1.63 1.56v1.87h2.78l-.44 2.9h-2.34V22C18.34 21.21 22 17.06 22 12.06z"/></svg>')
    WA_SVG = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
              '<path d="M.057 24l1.687-6.163a11.867 11.867 0 0 1-1.587-5.946C.16 5.335 5.495 0 12.05 0a11.817 11.817 0 0 1 8.413 3.488 11.824 11.824 0 0 1 3.48 8.414c-.003 6.557-5.338 11.892-11.893 11.892a11.9 11.9 0 0 1-5.688-1.448L.057 24zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884a9.86 9.86 0 0 0 1.51 5.26l-.999 3.648 3.737-.981zm11.387-5.464c-.074-.124-.272-.198-.57-.347-.297-.149-1.758-.868-2.031-.967-.272-.099-.47-.149-.669.149-.198.297-.768.967-.941 1.165-.173.198-.347.223-.644.074-.297-.149-1.255-.462-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.521.151-.172.2-.296.3-.495.099-.198.05-.372-.025-.521-.075-.148-.669-1.611-.916-2.206-.242-.579-.487-.501-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.626.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413z"/></svg>')
    SOCIAL = ('<div class="w-layout-hflex rt-nav-social-icon-wrapper bm-nav-social">'
              f'<a class="rt-social-media-icon-wrapper bm-nav-social-link w-inline-block" '
              f'href="https://www.facebook.com/share/g/1EL1bzxpEm/" target="_blank" '
              f'rel="noopener" aria-label="Facebook">{FB_SVG}</a>'
              f'<a class="rt-social-media-icon-wrapper bm-nav-social-link bm-nav-social-wa w-inline-block" '
              f'href="https://wa.me/48729405452" target="_blank" rel="noopener" '
              f'aria-label="WhatsApp">{WA_SVG}</a>'
              '</div>')
    follow.append(BeautifulSoup(SOCIAL, "html.parser"))
    report["set"] += 1
# contact box tel/email
cbox = soup.find("div", class_="rt-nav-contact-box")
if cbox:
    a_list = cbox.find_all("a")
    if len(a_list) >= 1: a_list[0]["href"] = "tel:+48729405452"; set_text(a_list[0], "+48 729 405 452")
    if len(a_list) >= 2: a_list[1]["href"] = "mailto:vmtkavenko@gmail.com"; set_text(a_list[1], "vmtkavenko@gmail.com")

# all "Get free quote" / nav CTA buttons -> "Zostaw zgłoszenie" + popup trigger
for d in soup.find_all("div", class_="rt-text-style-button"):
    if d.get_text(strip=True) in ("Get free quote", "Get a free inspection", "Lets connect"):
        set_text(d, "Zostaw zgłoszenie")
# the navbar/hero CTA anchors -> popup
for a in soup.find_all("a", href=True):
    if a["href"] in ("/inquiry-form", "/contact-one", "/contact-us"):
        a["href"] = "#kontakt"; a["data-bm-popup"] = "1"

# =====================================================================
# 5) HERO
# =====================================================================
hero = section("rt-hero-v1")
if hero:
    hero_eyebrow = hero.find(class_="rt-text-style-h6")
    set_text(hero_eyebrow, "Remonty i wykończenia • Lublin i okolice")
    if hero_eyebrow is not None:
        hero_eyebrow["class"] = hero_eyebrow.get("class", []) + ["bm-hero-eyebrow"]
    h1 = hero.find("h1")
    if h1:
        h1.clear()
        l1 = soup.new_tag("span"); l1["class"] = "bm-hl"
        l1.append(NavigableString("Remonty mieszkań "))
        br = soup.new_tag("br"); br["class"] = "bm-br-m"; l1.append(br)   # break only on mobile
        l1.append(NavigableString("w Lublinie"))
        l2 = soup.new_tag("span"); l2["class"] = "bm-hl"; l2.string = "bez niedokończonych prac"
        h1.append(l1); h1.append(l2)
        h1["class"] = (h1.get("class") or []) + ["bm-hero-h1"]  # on-load reveal (above the fold)
        report["set"] += 1
    set_text(hero.find("p"), "BIG-MARK wykonuje remonty, wykończenia i prace specjalistyczne — "
                             "dokładnie, bez zbędnych problemów i bez ukrytych niespodzianek.")
    btns = hero.find_all("div", class_="rt-text-style-button")
    if len(btns) >= 1: set_text(btns[0], "Zostaw zgłoszenie")
    if len(btns) >= 2: set_text(btns[1], "Napisz na WhatsApp")
    btn_links = hero.find_all("a")
    # first hero button -> popup, second -> whatsapp
    hero_btn_as = [a for a in btn_links if a.find("div", class_="rt-text-style-button")]
    if len(hero_btn_as) >= 1: hero_btn_as[0]["href"] = "#kontakt"; hero_btn_as[0]["data-bm-popup"] = "1"
    if len(hero_btn_as) >= 2:
        hero_btn_as[1]["href"] = "https://wa.me/48729405452"; hero_btn_as[1]["target"] = "_blank"
    # video description
    desc = hero.find(class_="rt-hero-video-description")
    if desc: set_text(desc.find("div"), "Zobacz, jak pracujemy — dokładnie i z dbałością o detale.")

# hero background image -> client-chosen photo gallery-06
bg = soup.find("img", class_="rt-hero-background-image-v1")
if bg:
    bg["src"] = PH(6)
    bg["alt"] = "Nowoczesna kuchnia po remoncie — BIG-MARK Lublin"
    bg.attrs.pop("srcset", None); bg.attrs.pop("sizes", None)

# replace hero background VIDEO with a square photo-montage (reads as video)
vid = soup.find(class_="rt-hero-background-video")
if vid:
    show = soup.new_tag("div")
    show["class"] = ["rt-hero-background-video", "rt-border-radius", "rt-overflow-hidden", "bm-slideshow"]
    for g, alt in [(1, "Łazienka z lastryko po remoncie"), (8, "Łazienka z lamelami drewnianymi"),
                   (9, "Umywalka i okrągłe lustro"), (2, "Kuchnia po remoncie"), (6, "Kuchnia premium z wyspą")]:
        im = soup.new_tag("img", src=PH(g))
        im["alt"] = alt + " — BIG-MARK Lublin"
        im["loading"] = "lazy"
        show.append(im)
    vid.replace_with(show)
    report["set"] += 1

# =====================================================================
# 6) COUNTER (Liczby)
# =====================================================================
cnt = section("rt-counter")
if cnt:
    # drop the leftover scroll-down arrow that sits under "Prace specjalistyczne"
    for ar in cnt.select(".rt-hero-down-arrow-wrapper"):
        ar.decompose()
    set_text(cnt.find(class_="rt-text-style-h6"), "Liczby i fakty")
    h2 = cnt.find("h2")
    set_text(h2, "Konkrety zamiast obietnic — remonty prowadzone spokojnie, dokładnie i do końca.")
    replace_by_text(cnt, {
        "Projects completed": "Prac doprowadzonych do końca",
        "Years of experience": "Średnia ocena klientów",
        "Happy clients": "Ukrytych niespodzianek",
        "Quality focused": "Certyfikaty instalacyjne G1 / G3",
    })

# =====================================================================
# 7) ABOUT (Dlaczego nam ufają)
# =====================================================================
ab = section("rt-about-us")
if ab:
    replace_by_text(ab, {"About us": "Dlaczego nam ufają", "Learn more": "Zostaw zgłoszenie"})
    abh2 = ab.find("h2")
    set_text(abh2, "Remont prowadzony spokojnie, z odpowiedzialnością i do końca")
    if abh2 is not None:
        abh2["scroll-text"] = "1"             # match lower blocks' heading reveal
        abh2.attrs.pop("data-w-id", None)     # drop conflicting IX2 fade
        if abh2.get("style") and "opacity" in abh2["style"]:
            del abh2["style"]
    set_text(ab.find("p"), "Bierzemy na siebie całość prac — także te trudniejsze, przy których inni "
                           "wykonawcy rezygnują. Bez chaosu, bez znikania i bez zostawiania rzeczy „na później”.")
    replace_by_text(ab, {
        "Customer satisfaction rate": "Prac doprowadzonych do końca",
        "Expert craftsmanship": "Dokładne wykończenie i dbałość o detal",
        "Customer-focused service": "Łatwa, spokojna komunikacja na każdym etapie",
    })
    main = ab.find("img")
    if main: main["src"] = PH(2); main["alt"] = "Nowoczesna kuchnia po remoncie — BIG-MARK"; main.attrs.pop("srcset", None)
    # 98% -> 100%
    pct = find_text(ab, "98%")
    if pct: set_text(pct, "100%")
    # remove the customer-avatar circles (people)
    cw = ab.select_one(".rt-about-us-client-wrapper")
    if cw is not None: cw.decompose()
    # tag the CTA button wrapper so the mobile reorder can move + stretch it
    for a in ab.find_all("a"):
        if a.get_text(strip=True) == "Zostaw zgłoszenie":
            a["class"] = (a.get("class") or []) + ["bm-about-btn"]
            if a.parent is not None and a.parent.name == "div":
                a.parent["class"] = (a.parent.get("class") or []) + ["bm-about-cta"]
            break

# =====================================================================
# 8) SERVICES (Usługi)
# =====================================================================
sv = section("rt-services")
if sv:
    main = sv.select_one(".rt-service-main-wrapper")
    if main is not None:
        SVC = [
            ("Remonty mieszkań", 4, "Kompleksowe prace remontowe i wykończeniowe — od przygotowania powierzchni po finalne wykończenie."),
            ("Remont łazienki", 1, "Płytki, instalacje, zabudowy, montaż elementów i dopracowane detale."),
            ("Układanie płytek", 8, "Precyzyjnie w łazienkach, kuchniach, korytarzach i innych pomieszczeniach."),
            ("Panele i laminat", 7, "Montaż paneli i laminatu z dbałością o równe wykończenia, listwy i detale."),
            ("Szpachlowanie i malowanie", 10, "Gładzie, przygotowanie ścian oraz malowanie wnętrz."),
            ("Projekt i wizualizacje", 2, "Pomoc w zaplanowaniu układu, stylu i rozwiązań przed rozpoczęciem prac."),
        ]
        arrow_up = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
                    'stroke-linecap="round" stroke-linejoin="round"><line x1="7" y1="17" x2="17" y2="7"></line>'
                    '<polyline points="7 7 17 7 17 17"></polyline></svg>')
        cards = "".join(
            f'<article class="bm-svc-card" data-bm-popup="1" role="button" tabindex="0" '
            f'aria-label="{t} — zostaw zgłoszenie"><div class="bm-svc-img"><img src="{PH(g)}" '
            f'alt="{t} — BIG-MARK Lublin" loading="lazy"></div>'
            f'<span class="bm-svc-arrow">{arrow_up}</span>'
            f'<div class="bm-svc-body"><h3>{t}</h3><p>{d}</p></div></article>'
            for t, g, d in SVC)
        SERVICES = (
            '<div class="bm-uslugi-head">'
            '<div class="bm-uslugi-head-left"><div class="bm-eyebrow">Usługi</div>'
            '<h2 class="bm-uslugi-title" scroll-text="1">Kompleksowo lub pojedynczo — remonty i wykończenia</h2></div>'
            '<button class="bm-uslugi-cta" data-bm-popup="1" type="button">Zostaw zgłoszenie '
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            'stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line>'
            '<polyline points="12 5 19 12 12 19"></polyline></svg></button></div>'
            f'<div class="bm-uslugi-grid">{cards}</div>')
        main.clear()
        main.append(BeautifulSoup(SERVICES, "html.parser"))
        report["set"] += 1

# =====================================================================
# 9) WHY-CHOOSE (Prace specjalistyczne)
# =====================================================================
wc = section("rt-why-choose")
if wc:
    replace_by_text(wc, {"Why choose us": "Prace specjalistyczne"})
    h2 = wc.find("h2")
    set_text(h2, "Więcej niż standardowy remont — także prace specjalistyczne, z uprawnieniami")
    replace_by_text(wc, {
        "Expert roofing team": "Instalacja elektryczna — certyfikat G1",
        "Premium materials": "Ogrzewanie gazowe — certyfikat G3",
        "Reliable & timely service": "Zabudowy gipsowo-kartonowe i sufity",
        "Customer Satisfaction": "Meble na wymiar i montaż okien",
    })
    imgs = wc.find_all("img")
    wmap = {0: 6, 1: 3, 2: 5, 3: 8, 4: 9}
    for idx, g in wmap.items():
        if idx < len(imgs): set_img(imgs[idx], PH(g), "Realizacja BIG-MARK — wykończenie wnętrza")

# =====================================================================
# 10) FEATURED PROJECTS (Realizacje)
# =====================================================================
fp = section("rt-featured-project")
if fp:
    replace_by_text(fp, {"Featured projects": "Nasze realizacje", "View all projects": "Zostaw zgłoszenie"})
    set_text(fp.find("h2"), "Realizacje, które bronią się w detalu")
    # tag the top-right CTA button so mobile can move it below the gallery + stretch it
    for a in fp.find_all("a"):
        if a.get_text(strip=True) == "Zostaw zgłoszenie":
            a["class"] = (a.get("class") or []) + ["bm-real-btn"]
            break
    # rebuild the collection list -> uniform tabbed gallery
    dynlist = fp.select_one(".w-dyn-list")
    if dynlist is not None:
        REAL = [
            ("Remont łazienki z lastryko", 1, "lazienki", "Łazienka • Lublin"),
            ("Łazienka z lamelami i kabiną", 8, "lazienki", "Łazienka • Lublin"),
            ("Łazienka — umywalka i lustro", 9, "lazienki", "Łazienka • Lublin"),
            ("Kuchnia z ciemną zabudową", 2, "kuchnie", "Kuchnia • Lublin"),
            ("Kuchnia premium z wyspą", 6, "kuchnie", "Kuchnia • Lublin"),
            ("Salon po generalnym remoncie", 3, "mieszkania", "Mieszkanie • Lublin"),
            ("Generalny remont mieszkania", 4, "mieszkania", "Mieszkanie • Lublin"),
            ("Pokój z panelami i malowaniem", 5, "mieszkania", "Mieszkanie • Lublin"),
            ("Korytarz i układanie paneli", 7, "mieszkania", "Mieszkanie • Lublin"),
            ("Przedpokój z zabudową na wymiar", 10, "mieszkania", "Mieszkanie • Lublin"),
        ]
        TABS = [("Wszystkie", "all"), ("Łazienki", "lazienki"), ("Kuchnie", "kuchnie"), ("Mieszkania", "mieszkania")]
        tabs_html = "".join(
            f'<button class="bm-real-tab{" is-active" if i==0 else ""}" type="button" data-cat="{cat}">{lbl}</button>'
            for i, (lbl, cat) in enumerate(TABS))
        cards_html = "".join(
            f'<article class="bm-real-card" data-cat="{cat}" data-bm-popup="1" role="button" tabindex="0" '
            f'aria-label="{t} — zostaw zgłoszenie"><div class="bm-real-img"><img src="{PH(g)}" '
            f'alt="{t} — BIG-MARK Lublin" loading="lazy"></div>'
            f'<div class="bm-real-cap"><span class="bm-real-loc">{loc}</span><h3>{t}</h3></div>'
            f'</article>'
            for t, g, cat, loc in REAL)
        GAL = (f'<div class="bm-real-tabs">{tabs_html}</div>'
               f'<div class="bm-real-grid">{cards_html}</div>')
        dynlist.clear()
        dynlist["class"] = ["bm-real-wrap"]
        dynlist.append(BeautifulSoup(GAL, "html.parser"))
        report["set"] += 1

# =====================================================================
# 11) TESTIMONIALS (Opinie)
# =====================================================================
ts = section("rt-testimonial-slider")
if ts:
    main = ts.select_one(".rt-testimonial-slider-main")
    if main is not None:
        # Real verified Google reviews (verbatim; only obvious diacritic typos fixed).
        REVIEWS = [
            ("Wojtek Golebiowski", "Opinia z Google",
             "Zdecydowanie polecam tę ekipę budowlaną za pełen profesjonalizm i rzetelność. "
             "Prace zostały wykonane bardzo dokładnie, z dbałością o każdy detal. Wszystko "
             "przebiegało zgodnie z ustalonym harmonogramem i bez opóźnień. Świetny kontakt "
             "oraz gotowość do doradztwa na każdym etapie realizacji to duży atut. Solidna "
             "firma, której można w pełni zaufać."),
            ("Daniel Kuczek", "Opinia z Google",
             "Polecam tę firmę, pełen profesjonalizm, bardzo dobra komunikacja a przede "
             "wszystkim terminowość i jakość wykonanej pracy!"),
            ("Antoni Dybała", "Opinia z Google",
             "Serdecznie polecam. Remont wykonany w terminie i nie ma na co narzekać. Jednym "
             "słowem profesjonalista, któremu można powierzyć swoje zaufanie!"),
            ("Jacek Kluch", "Opinia z Google",
             "Prace remontowe wykonane zgodnie z założonym planem, czas i jakość wykonania "
             "na 6 gwiazdek, firma godna polecenia, polecam."),
            ("Levigor DM", "Opinia z Google",
             "Prace remontowe są doskonałe i wysokiej jakości. Poza tym działają szybko. "
             "Dałbym im sześć gwiazdek, gdyby ich ceny za remonty mieszkań były niższe. "
             "Ale chyba trzeba zapłacić więcej za jakość."),
        ]
        star = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
                '<path d="M12 2l2.9 6.26L22 9.27l-5 4.87L18.18 22 12 18.56 5.82 22 7 14.14l-5-4.87 '
                '7.1-1.01L12 2z"/></svg>')
        def initial(name): return name.strip()[0]
        cards = "".join(
            f'<article class="bm-rev-card"><div class="bm-rev-top">'
            f'<div class="bm-rev-av">{initial(n)}</div>'
            f'<div class="bm-rev-id"><b>{n}</b><span>{role}</span></div>'
            f'<svg class="bm-rev-g" viewBox="0 0 24 24" aria-hidden="true"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.27-4.74 3.27-8.1z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84A11 11 0 0 0 12 23z"/><path fill="#FBBC05" d="M5.84 14.1a6.6 6.6 0 0 1 0-4.2V7.06H2.18a11 11 0 0 0 0 9.88l3.66-2.84z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84C6.71 7.3 9.14 5.38 12 5.38z"/></svg>'
            f'</div>'
            f'<div class="bm-rev-stars">{star*5}</div>'
            f'<p class="bm-rev-text">{txt}</p></article>'
            for n, role, txt in REVIEWS)
        GMAPS = ("https://www.google.com/maps/place/Remont+mieszkania+Firma+Big-Mark/"
                 "@51.2601994,22.5394963,17z/data=!4m6!3m5!1s0x47239b27c9080613:0xa61f9c742f53fbd1"
                 "!8m2!3d51.2601994!4d22.5394963!16s%2Fg%2F11vxjrvjd7")
        chev = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
                'stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>')
        HEAD = ('<div class="bm-rev-head"><div class="bm-eyebrow">Opinie</div>'
                '<h2 class="bm-rev-title" scroll-text="1">Co mówią klienci BIG-MARK</h2>'
                '<p class="bm-rev-sub">Prawdziwe opinie osób, dla których wykonaliśmy remont '
                'w Lublinie i okolicach.</p>'
                f'<a class="bm-rev-glink" href="{GMAPS}" target="_blank" rel="noopener">'
                '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.27-4.74 3.27-8.1z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84A11 11 0 0 0 12 23z"/><path fill="#FBBC05" d="M5.84 14.1a6.6 6.6 0 0 1 0-4.2V7.06H2.18a11 11 0 0 0 0 9.88l3.66-2.84z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84C6.71 7.3 9.14 5.38 12 5.38z"/></svg>'
                'Zobacz wszystkie opinie w Google</a></div>')
        CAROUSEL = (f'<div class="bm-rev-carousel">'
                    f'<button class="bm-rev-nav bm-rev-prev" type="button" aria-label="Poprzednie opinie">{chev}</button>'
                    f'<div class="bm-rev-track">{cards}</div>'
                    f'<button class="bm-rev-nav bm-rev-next" type="button" aria-label="Następne opinie">{chev}</button>'
                    f'</div>'
                    f'<div class="bm-rev-dots" role="tablist" aria-label="Strony opinii"></div>')
        main.clear()
        main["class"] = ["bm-rev-wrap"]
        main.append(BeautifulSoup(HEAD + CAROUSEL, "html.parser"))
        report["set"] += 1

# =====================================================================
# 12) CTA (Zostaw zgłoszenie) + inject form
# =====================================================================
cta = section("rt-cta")
if cta:
    replace_by_text(cta, {"Lets connect": "Zostaw zgłoszenie"})
    set_text(cta.find("h2"), "Opisz, co chcesz zrobić — wrócimy z konkretną odpowiedzią")
    cp = cta.find("p")
    if cp is not None:
        cp.clear()
        cp.append(NavigableString("Remont łazienki, mieszkania, płytki, instalacje, zabudowy czy pojedyncza praca?"))
        cp.append(soup.new_tag("br"))
        cp.append(NavigableString("Napisz krótko, czego potrzebujesz — albo zadzwoń lub napisz na WhatsApp."))
        cp["class"] = (cp.get("class") or []) + ["bm-cta-lead"]
        report["set"] += 1
    imgs = cta.find_all("img")
    if len(imgs) > 0: set_img(imgs[0], PH(2), "Kuchnia po remoncie — BIG-MARK")
    if len(imgs) > 1: set_img(imgs[1], PH(1), "Łazienka po remoncie — BIG-MARK")
    cta["id"] = "kontakt"
    # tag the CTA button wrapper + button for a full-width mobile stretch
    for a in cta.find_all("a"):
        if a.get_text(strip=True) == "Zostaw zgłoszenie":
            a["class"] = (a.get("class") or []) + ["bm-cta-btn"]
            if a.parent is not None and a.parent.name == "div":
                a.parent["class"] = (a.parent.get("class") or []) + ["bm-cta-btn-wrap"]
            break

# =====================================================================
# 13) FAQ
# =====================================================================
fq = section("rt-faq-v4")
if fq:
    replace_by_text(fq, {"FAQ": "FAQ"})
    set_text(fq.find("h2"), "Szybkie odpowiedzi na najczęstsze pytania")
    set_text(fq.find("p"), "Masz inne pytanie? Zadzwoń lub napisz na WhatsApp — bez zobowiązań.")
    # tag the FAQ CTA button for a full-width mobile stretch
    for a in fq.find_all("a"):
        if a.get_text(strip=True) == "Zostaw zgłoszenie":
            a["class"] = (a.get("class") or []) + ["bm-faq-btn"]
            if a.parent is not None and a.parent.name == "div":
                a.parent["class"] = (a.parent.get("class") or []) + ["bm-faq-btn-wrap"]
            break
    qa = [
        ("How do I know if my roof needs repair or replacement?", "Ile kosztuje remont?",
         "Look for leaks", "Cena zależy od zakresu prac, metrażu, materiałów i terminu. Po krótkiej rozmowie "
         "lub oględzinach przygotowujemy jasną wycenę i dobieramy rozwiązania pod Twój budżet."),
        ("What roofing materials do you offer?", "Ile trwa wykonanie prac?",
         "We provide options", "Termin zależy od zakresu remontu. Pracujemy sprawnie, ale bez pośpiechu kosztem "
         "jakości. Przed startem ustalamy realny harmonogram, żeby uniknąć niespodzianek."),
        ("How long does a roof installation take?", "Czy pracujecie tylko w Lublinie?",
         "Most roof installations", "Głównie działamy w Lublinie i okolicach, ale przy większych realizacjach "
         "możemy omówić pracę również w innych częściach Polski."),
        ("Do you provide free roof inspections or estimates?", "Czy można zamówić tylko jedną usługę?",
         "Yes, we offer", "Tak. Możesz zlecić zarówno kompleksowy remont mieszkania, jak i pojedyncze prace: "
         "łazienkę, płytki, malowanie, elektrykę, hydraulikę, zabudowy GK, montaż okien czy meble na wymiar."),
        ("Will my daily routine be affected during roofing work?", "Czy pomagacie z doborem materiałów?",
         "Roofing work may", "Tak. Pomagamy dobrać materiały, rozwiązania techniczne i warianty wykończenia "
         "tak, aby pasowały do budżetu, stylu i codziennego użytkowania."),
    ]
    for old_q, new_q, ans_prefix, new_a in qa:
        el = find_text(fq, old_q)
        if el: set_text(el, new_q)
        for p in fq.find_all("p"):
            if p.get_text(strip=True).startswith(ans_prefix):
                set_text(p, new_a); break

# =====================================================================
# 14) FOOTER
# =====================================================================
ft = section("rt-footer-v1")
if ft:
    replace_by_text(ft, {
        "Your trusted roofing partner": "Wykonawca remontowy z Lublina",
        "Protecting your home, with guaranteed quality.":
            "Remonty mieszkań, łazienek i prace wykończeniowe — dokładnie, spokojnie i do końca.",
        "Quick links": "Nawigacja", "Useful links": "Informacje", "Get in touch": "Kontakt",
        "Home": "Dlaczego my", "About us": "Usługi", "Services": "Realizacje", "Porfolio": "Opinie",
        "License": "FAQ", "Style guide": "Prace specjalistyczne", "Changelog": "Polityka prywatności",
        "404": "Kontakt",
        "Call us": "Zadzwoń", "(888) 123 4567": "+48 729 405 452",
        "Email us": "Napisz", "info@example.com": "vmtkavenko@gmail.com",
        "Follow us :": "Obserwuj nas:",
    })
    # footer quick/useful link hrefs
    fmap = {"Dlaczego my": "#dlaczego", "Usługi": "#uslugi", "Realizacje": "#realizacje",
            "Opinie": "#opinie", "FAQ": "#faq", "Prace specjalistyczne": "#specjalistyczne",
            "Polityka prywatności": "#", "Kontakt": "#kontakt"}
    for a in ft.find_all("a"):
        t = a.get_text(strip=True)
        if t in fmap: a["href"] = fmap[t]
    # contact links
    for a in ft.find_all("a", href=True):
        if a.get_text(strip=True) == "+48 729 405 452": a["href"] = "tel:+48729405452"
        if a.get_text(strip=True) == "vmtkavenko@gmail.com": a["href"] = "mailto:vmtkavenko@gmail.com"
    # add the BIG-MARK logo at the top of the first footer column (footer is light/cream)
    col1 = ft.select_one(".rt-footer-col-v1")
    if col1 is not None:
        # drop the "Wykonawca remontowy z Lublina" text heading — the logo replaces it
        h3 = col1.select_one(".rt-text-style-h3")
        if h3 is not None: h3.decompose()
        limg = soup.new_tag("img", src=LOGO)
        limg["alt"] = "BIG-MARK"; limg["class"] = ["bm-footer-logo"]; limg["loading"] = "lazy"
        col1.insert(0, limg)
    # add a Google map of the BIG-MARK location at the end of the footer columns
    content_wrap = ft.select_one(".rt-footer-content-wrap")
    if content_wrap is not None:
        FMAP_EMBED = "https://www.google.com/maps?q=51.2601994,22.5394963&z=15&hl=pl&output=embed"
        MAP = (f'<div class="bm-footer-map"><iframe src="{FMAP_EMBED}" loading="lazy" '
               f'referrerpolicy="no-referrer-when-downgrade" allowfullscreen="" '
               f'title="BIG-MARK — Lublin, mapa"></iframe></div>')
        content_wrap.append(BeautifulSoup(MAP, "html.parser"))
        report["set"] += 1
    # bottom bar: drop "Designed by / License / Style guide", use our copyright
    bottom = ft.select_one(".rt-footer-bottom-content")
    if bottom is not None:
        bottom.clear()
        cp = soup.new_tag("div"); cp["class"] = ["bm-footer-copy"]
        cp.string = "© 2026 BIG-MARK. Wszystkie prawa zastrzeżone."
        bottom.append(cp)

# =====================================================================
# 14b) Prefix-based replacement of leftover roofing copy
# =====================================================================
PREFIX_MAP = {
    "Skilled professionals delivering":
        "Kompleksowe prace remontowe i wykończeniowe w mieszkaniach — od przygotowania powierzchni po finalne wykończenie.",
    "Complete roof replacement":
        "Remont łazienki: płytki, instalacje, zabudowy, montaż elementów i dopracowane detale.",
    "Strong, weather-resistant":
        "Precyzyjne układanie płytek w łazienkach, kuchniach, korytarzach i innych pomieszczeniach.",
    "Premium roofing solutions":
        "Montaż paneli i laminatu z dbałością o równe wykończenia, listwy i detale.",
    "Reliable roofing systems":
        "Przygotowanie ścian, gładzie, szpachlowanie oraz malowanie wnętrz.",
    "roofs installed and protected":
        "remont mieszkania po pojedyncze prace wykończeniowe — w jednym miejscu.",
    "Expert roofing with": "Także instalacja wodna, ",
    "trusted quality": "kostka brukowa",
    "and lasting results.": " i ściany dekoracyjne",
    "Transparent communication and dependable support":
        "Jasne ustalenia i spokojny kontakt na każdym etapie prac.",
}
for node in list(soup.find_all(string=True)):
    if node.parent.name in ("script", "style"):
        continue
    s = node.strip()
    for pref, new in PREFIX_MAP.items():
        if s.startswith(pref):
            node.replace_with(NavigableString(new)); report["set"] += 1
            break

# =====================================================================
# 15) Global cleanup of leftover template links
# =====================================================================
for a in soup.find_all("a", href=True):
    h = a["href"]
    if h.startswith("/") or "flampt.webflow.io" in h or "radianttemplates" in h:
        a["href"] = "#top"
    if "facebook.com" in h and "share/g" not in h:
        a["href"] = "https://www.facebook.com/share/g/1EL1bzxpEm/"

# ---- REORDER: move "Liczby" (counter) down, between "Okremi roboty"
#      (why-choose) and "Nasze realizacje" (featured-project) ----
def body_block(sec):
    node = sec
    while node.parent is not None and node.parent is not soup.body:
        node = node.parent
    return node

cnt_sec = section("rt-counter")
fp_sec = section("rt-featured-project")
if cnt_sec is not None and fp_sec is not None:
    cb = body_block(cnt_sec)
    fb = body_block(fp_sec)
    cb.extract()
    fb.insert_before(cb)
    report["set"] += 1

# Flampt-style rounded white transition at the bottom of the hero + a custom
# Polish "PRZEWIŃ W DÓŁ" rotating badge (replaces the template's English one)
old_badge = soup.find("div", class_="rt-scroll-button")
if old_badge is not None:
    old_badge.decompose()
hero_bg = soup.find("div", class_="rt-hero-background")
if hero_bg is not None:
    # 1:1 with the Flampt template: a straight-top white transition panel PLUS a
    # centred white "tent" mask that pokes up to notch the rotating dark glass
    # circle, with a static dark down-arrow sitting in the notch. Reuses the
    # template's own mask + arrow SVGs so the shape is pixel-identical; only the
    # circular text is localised to Polish.
    MASK = ASSET_PREFIX + "images/69c502671e56351ee61de530_Mask%20group%201%20%281%29.svg"
    ARROW = ASSET_PREFIX + "images/69a7ad05845cad119b1ae8f2_down%20arrow%20%281%29.svg"
    BADGE = ('<div class="bm-transition-wrap">'
      '<div class="bm-hero-transition"></div>'
      '<button class="bm-sd-badge" data-bm-scrolldown="1" aria-label="Przewiń w dół">'
      '<svg class="bm-sd-ring" viewBox="0 0 160 160" aria-hidden="true">'
      '<defs><path id="bmSdCircle" d="M80,20 a60,60 0 1,1 -0.1,0"/></defs>'
      '<text><textPath href="#bmSdCircle" textLength="377" lengthAdjust="spacing">PRZEWIŃ W DÓŁ • PRZEWIŃ W DÓŁ • </textPath></text>'
      '</svg>'
      '</button>'
      f'<img class="bm-sd-mask" src="{MASK}" alt="" aria-hidden="true">'
      f'<a class="bm-sd-arrow" href="#dlaczego" data-bm-scrolldown="1" aria-label="Przewiń w dół"><img src="{ARROW}" alt=""></a>'
      '</div>')
    hero_bg.insert_after(BeautifulSoup(BADGE, "html.parser"))
    report["set"] += 1

# section ids for anchor nav
ids = {"rt-hero-v1": "top", "rt-about-us": "dlaczego", "rt-services": "uslugi",
       "rt-why-choose": "specjalistyczne", "rt-featured-project": "realizacje",
       "rt-testimonial-slider": "opinie", "rt-faq-v4": "faq", "rt-counter": "liczby"}
for cls, _id in ids.items():
    s = section(cls)
    if s is not None and not s.get("id"):
        s["id"] = _id

# =====================================================================
# 16) Append popup + sticky bar + floating widget + JS
# =====================================================================
EXTRA_HTML = """
<script>
/* Dedicated, isolated scroll state — independent of every other script, so it can
   never be blocked by an error elsewhere. Toggles .bm-scrolled (solid-white header)
   AND sets each logo's inline display directly (inline beats the stylesheet):
   white logo over the glassy hero header, gold once the header turns white. */
(function(){
  try{
    function apply(){
      var y = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0;
      var on = y > 60;
      document.documentElement.classList.toggle('bm-scrolled', on);
      var light=document.querySelector('.bm-logo-light'), dark=document.querySelector('.bm-logo-dark');
      if(light&&dark){ light.style.display = on ? 'none' : 'block'; dark.style.display = on ? 'block' : 'none'; }
    }
    window.addEventListener('scroll', apply, {passive:true});
    window.addEventListener('resize', apply, {passive:true});
    window.addEventListener('load', apply);
    if(document.readyState!=='loading') apply();
    else document.addEventListener('DOMContentLoaded', apply);
    apply(); setTimeout(apply,200); setTimeout(apply,800); setTimeout(apply,1800);
  }catch(e){}
})();
</script>
<div class="bm-overlay" id="bmOverlay">
  <div class="bm-modal" role="dialog" aria-modal="true">
    <button class="bm-close" id="bmClose" aria-label="Zamknij">&times;</button>
    <h3>Zostaw zgłoszenie</h3>
    <p class="bm-sub">Napisz krótko, czego potrzebujesz — wrócimy z konkretną odpowiedzią.</p>
    <form class="bm-form" novalidate>
      <input type="text" name="name" placeholder="Imię" autocomplete="given-name">
      <input type="tel" name="phone" placeholder="Telefon" autocomplete="tel">
      <textarea name="message" placeholder="Np. remont łazienki, płytki, kabina prysznicowa."></textarea>
      <label class="bm-check"><input type="checkbox" name="privacy"><span>Akceptuję <a href="#" target="_blank">politykę prywatności</a>.</span></label>
      <button type="submit">Wyślij zgłoszenie</button>
    </form>
    <div class="bm-success"><div class="bm-tick">&#10003;</div><b>Dziękujemy.</b><div>Zgłoszenie zostało przygotowane — skontaktujemy się z Tobą możliwie szybko.</div></div>
    <p class="bm-alt">albo <a href="tel:+48729405452">zadzwoń</a> lub <a href="https://wa.me/48729405452" target="_blank">napisz na WhatsApp</a></p>
  </div>
</div>

<div class="bm-mobilebar">
  <button class="bm-mc-main" data-bm-popup="1">Zostaw zgłoszenie</button>
  <a class="bm-mc-wa" href="https://wa.me/48729405452" target="_blank" aria-label="WhatsApp">
    <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor"><path d="M.057 24l1.687-6.163a11.867 11.867 0 0 1-1.587-5.946C.16 5.335 5.495 0 12.05 0a11.817 11.817 0 0 1 8.413 3.488 11.824 11.824 0 0 1 3.48 8.414c-.003 6.557-5.338 11.892-11.893 11.892a11.9 11.9 0 0 1-5.688-1.448L.057 24z"/></svg>
  </a>
  <a class="bm-mc-call" href="tel:+48729405452" aria-label="Zadzwoń">
    <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.81.36 1.6.7 2.34a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.74-1.74a2 2 0 0 1 2.11-.45c.74.34 1.53.57 2.34.7A2 2 0 0 1 22 16.92z"/></svg>
  </a>
</div>

<div class="bm-fab">
  <a class="bm-fwa" href="https://wa.me/48729405452" target="_blank" aria-label="WhatsApp">
    <svg viewBox="0 0 24 24" fill="#fff"><path d="M.057 24l1.687-6.163a11.867 11.867 0 0 1-1.587-5.946C.16 5.335 5.495 0 12.05 0a11.817 11.817 0 0 1 8.413 3.488 11.824 11.824 0 0 1 3.48 8.414c-.003 6.557-5.338 11.892-11.893 11.892a11.9 11.9 0 0 1-5.688-1.448L.057 24z"/></svg>
  </a>
  <a class="bm-fcall" href="tel:+48729405452" aria-label="Zadzwoń">
    <svg viewBox="0 0 24 24" fill="none" stroke="#232220" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.81.36 1.6.7 2.34a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.74-1.74a2 2 0 0 1 2.11-.45c.74.34 1.53.57 2.34.7A2 2 0 0 1 22 16.92z"/></svg>
  </a>
</div>

<script>
(function(){
  var ov=document.getElementById('bmOverlay');
  function open(){ov.classList.add('open');document.body.style.overflow='hidden';}
  function close(){ov.classList.remove('open');document.body.style.overflow='';}
  document.getElementById('bmClose').addEventListener('click',close);
  ov.addEventListener('click',function(e){if(e.target===ov)close();});
  document.addEventListener('keydown',function(e){if(e.key==='Escape')close();});
  document.querySelectorAll('[data-bm-popup]').forEach(function(b){
    b.addEventListener('click',function(e){e.preventDefault();open();});
    if(b.getAttribute('role')==='button'){
      b.addEventListener('keydown',function(e){
        if(e.key==='Enter'||e.key===' '){e.preventDefault();open();}
      });
    }
  });
  // navbar: white logo over hero, original (gold) logo + solid bar once scrolled.
  // IntersectionObserver is the primary trigger (fires even if scroll events don't),
  // with a window-scroll fallback. Both call the same idempotent setter.
  var navOuter=document.querySelector('.rt-navbar-outer-wrapper-v1');
  function setScrolled(on){
    document.documentElement.classList.toggle('bm-scrolled', on);
    if(navOuter) navOuter.classList.toggle('bm-scrolled', on);
  }
  var bmSentinel=document.createElement('div');
  bmSentinel.style.cssText='position:absolute;top:0;left:0;width:1px;height:80px;pointer-events:none;opacity:0;';
  document.body.appendChild(bmSentinel);
  if('IntersectionObserver' in window){
    new IntersectionObserver(function(e){ setScrolled(!e[0].isIntersecting); },{threshold:0}).observe(bmSentinel);
  }
  window.addEventListener('scroll',function(){ setScrolled(window.scrollY>70); },{passive:true});
  setScrolled(window.scrollY>70);
  // opinie carousel arrows + mobile pagination dots
  document.querySelectorAll('.bm-rev-carousel').forEach(function(c){
    var track=c.querySelector('.bm-rev-track');
    var prev=c.querySelector('.bm-rev-prev'), next=c.querySelector('.bm-rev-next');
    function step(){ var card=track.querySelector('.bm-rev-card'); return card?card.offsetWidth+22:340; }
    if(prev)prev.addEventListener('click',function(){track.scrollBy({left:-step(),behavior:'smooth'});});
    if(next)next.addEventListener('click',function(){track.scrollBy({left:step(),behavior:'smooth'});});
    // pagination dots — one per card, synced to scroll position (visible on mobile)
    var dotsWrap=c.parentElement.querySelector('.bm-rev-dots');
    var cards=track.querySelectorAll('.bm-rev-card');
    if(dotsWrap&&cards.length){
      cards.forEach(function(card,i){
        var d=document.createElement('button');
        d.type='button'; d.className='bm-rev-dot'; d.setAttribute('aria-label','Opinia '+(i+1));
        d.addEventListener('click',function(){ track.scrollTo({left:card.offsetLeft-track.offsetLeft,behavior:'smooth'}); });
        dotsWrap.appendChild(d);
      });
      var dots=dotsWrap.querySelectorAll('.bm-rev-dot');
      function syncDots(){
        var center=track.scrollLeft+track.clientWidth/2, best=0, bd=1e9;
        cards.forEach(function(card,i){
          var cc=card.offsetLeft-track.offsetLeft+card.offsetWidth/2, dd=Math.abs(cc-center);
          if(dd<bd){bd=dd;best=i;}
        });
        dots.forEach(function(d,i){ d.classList.toggle('is-active',i===best); });
      }
      track.addEventListener('scroll',function(){ window.requestAnimationFrame(syncDots); },{passive:true});
      syncDots();
    }
  });
  // realizacje category tabs
  var tabs=document.querySelectorAll('.bm-real-tab');
  var rcards=document.querySelectorAll('.bm-real-card');
  tabs.forEach(function(t){
    t.addEventListener('click',function(){
      tabs.forEach(function(x){x.classList.remove('is-active');});
      t.classList.add('is-active');
      var cat=t.getAttribute('data-cat');
      rcards.forEach(function(c){
        var show=(cat==='all'||c.getAttribute('data-cat')===cat);
        c.classList.toggle('is-hidden',!show);
      });
    });
  });
  document.querySelectorAll('.bm-form').forEach(function(f){
    var wrap=f.parentElement, succ=wrap.querySelector('.bm-success');
    f.addEventListener('submit',function(e){
      e.preventDefault();var ok=true;
      var n=f.querySelector('[name=name]'),p=f.querySelector('[name=phone]'),c=f.querySelector('[name=privacy]');
      [n,p].forEach(function(i){i.classList.remove('bm-field-error');});
      if(!n.value.trim()){n.classList.add('bm-field-error');ok=false;}
      if((p.value.replace(/[^0-9]/g,'')).length<9){p.classList.add('bm-field-error');ok=false;}
      if(!c.checked){ok=false;c.parentElement.style.color='#cf4b2e';}
      if(!ok)return;
      f.style.display='none';if(succ)succ.classList.add('show');
      var alt=wrap.querySelector('.bm-alt');if(alt)alt.style.display='none';
    });
  });
  // scroll-down badge -> smooth scroll to next section
  var sd=document.querySelector('[data-bm-scrolldown]');
  if(sd){ sd.addEventListener('click',function(){ var t=document.getElementById('dlaczego'); if(t) t.scrollIntoView({behavior:'smooth'}); }); }
  // floating widget appears only after the hero (from the second block)
  var fab=document.querySelector('.bm-fab');
  function fabToggle(){ if(!fab)return; if(window.scrollY > window.innerHeight*0.85){ fab.classList.add('bm-show'); } else { fab.classList.remove('bm-show'); } }
  window.addEventListener('scroll',fabToggle,{passive:true}); fabToggle();
})();
</script>
"""
soup.body.append(BeautifulSoup(EXTRA_HTML, "html.parser"))

# =====================================================================
# 17) Premium preloader — inserted at the very top of <body> so it paints
#     before anything else (no FOUC). Self-contained markup + controller.
# =====================================================================
PRELOADER_HTML = """
<div id="bm-preloader" class="bm-pl" role="status" aria-live="polite" aria-label="Ładowanie strony BIG-MARK">
  <div class="bm-pl-stage">
    <div class="bm-pl-logo">
      <img class="bm-pl-img" src="assets/big-mark_logo_transparent.png" alt="BIG-MARK" decoding="async" fetchpriority="high"/>
      <span class="bm-pl-sheen" aria-hidden="true"></span>
    </div>
    <span class="bm-pl-line" aria-hidden="true"></span>
  </div>
</div>
<script>
/* Preloader controller — independent & fail-safe: it NEVER traps the page.
   Waits for window load, holds a minimum on-screen time so the brand intro
   always completes (no flash on fast loads), then lifts the curtain and
   removes itself from the DOM so scroll/clicks/animations stay untouched. */
(function(){
  try{
    var pl = document.getElementById('bm-preloader');
    if(!pl){ return; }
    var root = document.documentElement;
    root.classList.add('bm-pl-lock');
    var minMs = parseInt(getComputedStyle(root).getPropertyValue('--bm-pl-min'), 10) || 1800;
    var start = Date.now(), done = false;
    function unlock(){ root.classList.remove('bm-pl-lock'); }
    function remove(){ if(pl && pl.parentNode){ pl.parentNode.removeChild(pl); pl = null; } }
    function hide(){
      if(done){ return; } done = true;
      var wait = Math.max(0, minMs - (Date.now() - start));
      setTimeout(function(){
        if(!pl){ return; }
        pl.classList.add('bm-pl-done');
        unlock();
        var gone = false, fin = function(){ if(gone){ return; } gone = true; remove(); };
        pl.addEventListener('transitionend', function(e){ if(e.propertyName === 'transform'){ fin(); } });
        setTimeout(fin, 1400); /* fallback if transitionend never fires */
      }, wait);
    }
    if(document.readyState === 'complete'){ hide(); }
    else { window.addEventListener('load', hide); }
    setTimeout(hide, 7000); /* hard safety: reveal no matter what */
  }catch(e){
    try{ var p = document.getElementById('bm-preloader'); if(p && p.parentNode){ p.parentNode.removeChild(p); } }catch(_){}
    document.documentElement.classList.remove('bm-pl-lock');
  }
})();
</script>
"""
soup.body.insert(0, BeautifulSoup(PRELOADER_HTML, "html.parser"))

# =====================================================================
# write
# =====================================================================
out = os.path.join(ROOT, "index.html")
open(out, "w", encoding="utf-8").write(str(soup))
print(f"WROTE {out}  ({os.path.getsize(out)} bytes)")
print(f"set={report['set']}  miss={report['miss']}")
