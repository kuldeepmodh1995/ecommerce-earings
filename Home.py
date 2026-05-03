import json
import streamlit as st
import streamlit.components.v1 as components
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from utils.data_manager import (
    load_products,
    save_order,
    load_hero_banners,
    load_shop_categories,
)

BASE_DIR = os.path.dirname(__file__)


def resolve_image(img_path: str) -> str:
    if img_path and img_path.startswith("app/static/"):
        return os.path.join(BASE_DIR, img_path[len("app/"):])
    return img_path


def resolve_banner_image_url(img_path: str) -> str:
    if img_path and img_path.startswith("app/static/"):
        return "/" + img_path
    return img_path


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Love Earrings",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
    unsafe_allow_html=True,
)

# ── CSS — Fresha-inspired light design system ─────────────────────────────────
st.markdown(
    """
<style>
  /* ── Design Tokens (Fresha) ── */
  :root {
    --color-midnight-ink: #0d0d0d;
    --color-canvas-white: #ffffff;
    --color-cloud-gray: #f2f2f2;
    --color-muted-stone: #767676;
    --color-silver-mist: #d3d3d3;
    --color-mercury-stroke: #e5e5e5;
    --color-sunset-gold: #ffc00a;
    --color-violet-impulse: #6950f3;
    --gradient-self-care-glow: radial-gradient(circle, rgb(239,105,151) 20vh, rgb(232,92,186) 40vh, rgb(184,76,220) 60vh);
    --radius-buttons: 999px;
    --radius-inputs: 999px;
    --radius-tags: 999px;
    --radius-cards: 8px;
    --radius-largecards: 12px;
    --radius-smallelements: 4px;
    --spacing-4: 4px; --spacing-8: 8px; --spacing-12: 12px; --spacing-16: 16px;
    --spacing-20: 20px; --spacing-24: 24px; --spacing-32: 32px;
    --spacing-40: 40px; --spacing-48: 48px; --spacing-64: 64px; --spacing-80: 80px;
    --section-gap: 24px; --card-padding: 32px; --element-gap: 8px;
  }

  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', ui-sans-serif, system-ui, sans-serif; box-sizing: border-box; }
  *, *::before, *::after { box-sizing: inherit; }
  body { background: #ffffff; }

  /* ── Remove Streamlit's default top whitespace ── */
  .block-container {
    padding-top: 0 !important; padding-left: 0 !important;
    padding-right: 0 !important; padding-bottom: 2rem !important;
    max-width: 100% !important;
  }
  section[data-testid="stMain"] > div { padding-left: 0 !important; padding-right: 0 !important; padding-top: 0 !important; }
  [data-testid="stMainBlockContainer"] { padding-top: 0 !important; }
  .stMainBlockContainer { padding-top: 0 !important; }
  header[data-testid="stHeader"] { display: none !important; }
  #stDecoration { display: none !important; }

  /* ── Collapse zero-height component iframe wrappers ── */
  [data-testid="stCustomComponentV1"] {
    min-height: 0 !important;
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
  }

  /* ── Hide sidebar completely ── */
  [data-testid="collapsedControl"] { display: none !important; }
  [data-testid="stSidebar"] { display: none !important; }

  /* ══════════════════════════════════════════════
     PROMO TICKER
     ══════════════════════════════════════════════ */
  .promo-ticker {
    background: var(--color-midnight-ink); color: var(--color-mercury-stroke);
    padding: 8px 0; overflow: hidden; white-space: nowrap;
    font-size: 0.68em; font-weight: 500; letter-spacing: 0.6px;
  }
  .promo-ticker-inner { display: inline-block; animation: ticker-scroll 32s linear infinite; }
  .promo-ticker-inner span { margin: 0 28px; opacity: 0.88; }
  .promo-ticker-inner span::before { content: '✦'; margin-right: 12px; color: var(--color-sunset-gold); }
  @keyframes ticker-scroll { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }

  /* ══════════════════════════════════════════════
     NAVBAR
     ══════════════════════════════════════════════ */
  .navbar-wrap {
    background: var(--color-canvas-white); border-bottom: 1px solid var(--color-mercury-stroke);
    padding: 0 14px; height: 54px;
    display: flex; align-items: center; justify-content: space-between;
    position: sticky; top: 0; z-index: 999;
    width: 100%; box-sizing: border-box;
  }
  .navbar-left { display: flex; align-items: center; }
  .navbar-brand {
    font-family: 'Inter', sans-serif; color: var(--color-midnight-ink);
    font-size: 1.15em; font-weight: 700; letter-spacing: 0.5px; white-space: nowrap;
    text-decoration: none;
    position: absolute; left: 50%; transform: translateX(-50%);
  }
  .navbar-right { display: flex; align-items: center; gap: 4px; }

  /* Hamburger */
  .hamburger-btn {
    background: none; border: none; cursor: pointer;
    padding: 8px 6px 8px 0; display: flex; flex-direction: column;
    gap: 5px; align-items: flex-start;
  }
  .hamburger-btn span {
    display: block; height: 1.5px; background: var(--color-midnight-ink);
    transition: all 0.3s;
  }
  .hamburger-btn span:nth-child(1) { width: 22px; }
  .hamburger-btn span:nth-child(2) { width: 16px; }
  .hamburger-btn span:nth-child(3) { width: 22px; }

  /* Nav overlay backdrop */
  .nav-overlay-bg {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.45); z-index: 9998;
    opacity: 0; pointer-events: none;
    transition: opacity 0.3s;
  }
  .nav-overlay-bg.open { opacity: 1; pointer-events: all; }

  /* Nav overlay panel */
  .nav-overlay {
    position: fixed; top: 0; left: 0; width: 82vw; max-width: 300px; height: 100%;
    background: var(--color-canvas-white); z-index: 9999;
    transform: translateX(-100%);
    transition: transform 0.32s cubic-bezier(0.4, 0, 0.2, 1);
    display: flex; flex-direction: column;
    box-shadow: 4px 0 32px rgba(0,0,0,0.12);
    overflow-y: auto;
  }
  .nav-overlay.open { transform: translateX(0); }

  .nav-overlay-header {
    display: flex; justify-content: space-between; align-items: center;
    padding: 16px 20px; border-bottom: 1px solid var(--color-mercury-stroke); flex-shrink: 0;
  }
  .nav-overlay-brand {
    font-family: 'Inter', sans-serif; font-size: 1.05em; font-weight: 700;
    color: var(--color-midnight-ink); letter-spacing: 0.5px;
  }
  .nav-close-btn {
    background: none; border: none; cursor: pointer; font-size: 1.4em;
    color: var(--color-midnight-ink); padding: 0 4px; line-height: 1; font-weight: 300;
  }
  .nav-overlay-links { padding: 4px 0; flex-shrink: 0; }
  .nav-overlay-links a {
    display: block; padding: 15px 24px;
    font-size: 0.88em; font-weight: 600; color: var(--color-midnight-ink);
    text-decoration: none; border-bottom: 1px solid var(--color-mercury-stroke);
    letter-spacing: 0.3px;
    transition: color 0.2s, background 0.2s;
  }
  .nav-overlay-links a:hover { background: var(--color-cloud-gray); color: var(--color-violet-impulse); }

  .nav-overlay-section { padding: 18px 24px; border-top: 1px solid var(--color-mercury-stroke); flex-shrink: 0; }
  .nav-overlay-section h4 {
    font-size: 0.64em; font-weight: 700; color: var(--color-muted-stone);
    letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 12px;
  }
  .nav-overlay-section a {
    display: block; padding: 10px 0;
    font-size: 0.84em; color: var(--color-muted-stone); text-decoration: none;
    border-bottom: 1px solid var(--color-mercury-stroke);
    letter-spacing: 0.3px; transition: color 0.2s;
  }
  .nav-overlay-section a:last-child { border-bottom: none; }
  .nav-overlay-section a:hover { color: var(--color-violet-impulse); }

  /* Navbar icon links (cart / wishlist) */
  .navbar-right { display: flex; align-items: center; gap: 10px; }
  .navbar-icon-link {
    text-decoration: none; color: var(--color-midnight-ink); font-size: 1.3em;
    font-weight: 500; padding: 6px 4px; transition: color 0.2s;
    white-space: nowrap; line-height: 1;
    min-width: 44px; min-height: 44px; display: flex; align-items: center; justify-content: center;
  }
  .navbar-icon-link:hover { color: var(--color-violet-impulse); }

  /* ══════════════════════════════════════════════
     FREE SHIPPING BAR
     ══════════════════════════════════════════════ */
  .free-shipping-bar {
    background: var(--color-cloud-gray); color: var(--color-muted-stone);
    text-align: center; padding: 8px 12px;
    font-size: 0.68em; font-weight: 500; letter-spacing: 0.5px;
    border-bottom: 1px solid var(--color-mercury-stroke);
  }

  /* ══════════════════════════════════════════════
     CONTENT PADDING
     ══════════════════════════════════════════════ */
  .content-pad { padding: 0 8px; }

  /* ══════════════════════════════════════════════
     PRODUCT GRID — 2 cols mobile, 4 cols tablet+
     ══════════════════════════════════════════════ */
  [data-testid="stHorizontalBlock"]:has(.product-card) { flex-wrap: wrap !important; }
  [data-testid="stHorizontalBlock"]:has(.product-card) > [data-testid="stColumn"] {
    min-width: 50% !important; flex: 0 0 50% !important;
    width: 50% !important; max-width: 50% !important;
    padding-left: 4px !important; padding-right: 4px !important;
    box-sizing: border-box !important;
  }
  /* JS-added class fallback for browsers where :has() doesn't apply */
  [data-testid="stHorizontalBlock"].has-product-cards { flex-wrap: wrap !important; }
  [data-testid="stHorizontalBlock"].has-product-cards > [data-testid="stColumn"] {
    min-width: 50% !important; flex: 0 0 50% !important;
    width: 50% !important; max-width: 50% !important;
    padding-left: 4px !important; padding-right: 4px !important;
    box-sizing: border-box !important;
  }

  /* ── Compact product card on mobile ── */
  @media (max-width: 599px) {
    .product-img-link img { aspect-ratio: 1/1 !important; }
    .product-info { padding: 5px 2px 2px !important; }
    .product-name { font-size: 0.65em !important; }
    .price-now { font-size: 0.72em !important; }
    .card-btn-wrap { padding: 0 2px 6px !important; }
    .card-btn-wrap .stButton > button { padding: 6px 4px !important; font-size: 0.58em !important; }
  }

  /* ══════════════════════════════════════════════
     PRODUCT CARD
     ══════════════════════════════════════════════ */
  .product-card { background: var(--color-canvas-white); overflow: hidden; margin-bottom: 10px; border-radius: var(--radius-largecards); }
  .product-img-link { display: block; overflow: hidden; position: relative; border-radius: var(--radius-cards); }
  .product-img-link img {
    width: 100%; aspect-ratio: 3/4; object-fit: cover; display: block;
    transition: transform 0.5s ease; border-radius: var(--radius-cards);
  }
  .product-img-link:hover img { transform: scale(1.04); }
  .product-info-link { text-decoration: none; display: block; }

  /* Badges */
  .badge {
    position: absolute; top: 8px; left: 8px;
    background: var(--color-midnight-ink); color: var(--color-canvas-white);
    padding: 2px 10px; font-size: .56em; font-weight: 700;
    letter-spacing: 0.6px; text-transform: uppercase;
    border-radius: var(--radius-tags);
  }
  .badge-new {
    position: absolute; top: 8px; left: 8px;
    background: var(--color-violet-impulse); color: var(--color-canvas-white);
    padding: 2px 10px; font-size: .56em; font-weight: 700; letter-spacing: 0.6px;
    border-radius: var(--radius-tags);
  }
  .badge-featured { display: none; }
  .badge-stock {
    position: absolute; bottom: 8px; left: 8px;
    background: rgba(255,255,255,0.92); color: var(--color-midnight-ink);
    padding: 2px 10px; font-size: .56em; font-weight: 600;
    border-radius: var(--radius-tags);
  }

  .product-info { padding: 8px 4px 4px; }
  .product-name {
    font-family: 'Inter', sans-serif; font-size: 0.70em; font-weight: 400;
    color: var(--color-midnight-ink); margin: 0 0 4px; line-height: 1.41;
  }
  .stars { display: none; }
  .price-wrap { display: flex; align-items: center; gap: 5px; margin-bottom: 7px; flex-wrap: wrap; }
  .price-now { font-size: 0.78em; font-weight: 600; color: var(--color-midnight-ink); }
  .price-was { font-size: .70em; color: var(--color-silver-mist); text-decoration: line-through; }
  .discount { font-size: .66em; color: var(--color-violet-impulse); font-weight: 600; }

  /* Add-to-cart button on card */
  .card-btn-wrap { padding: 0 4px 10px; }
  .card-btn-wrap .stButton > button {
    background: var(--color-midnight-ink) !important; color: var(--color-canvas-white) !important;
    border: none !important; border-radius: var(--radius-buttons) !important;
    font-size: 0.62em !important; font-weight: 600 !important;
    padding: 9px 4px !important; letter-spacing: 0.5px !important;
    width: 100% !important; text-transform: uppercase !important;
    font-family: 'Inter', sans-serif !important;
    min-height: 0 !important; line-height: 1.2 !important;
    transition: background 0.2s !important;
  }
  .card-btn-wrap .stButton > button:hover { background: #2a2a2a !important; }

  /* ══════════════════════════════════════════════
     CART / DETAIL PAGE
     ══════════════════════════════════════════════ */
  .cart-page div[data-testid="stHorizontalBlock"],
  .cart-page [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
  .cart-page div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"],
  .cart-page [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    min-width: 100% !important; flex: 0 0 100% !important;
    width: 100% !important; max-width: 100% !important;
  }
  .detail-page div[data-testid="stHorizontalBlock"],
  .detail-page [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
  .detail-page div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"],
  .detail-page [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    min-width: 100% !important; flex: 0 0 100% !important;
    width: 100% !important; max-width: 100% !important;
  }
  .value-props-row div[data-testid="stHorizontalBlock"],
  .value-props-row [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
  .value-props-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"],
  .value-props-row [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    min-width: 50% !important; flex: 0 0 50% !important;
    width: 50% !important; max-width: 50% !important;
    margin-bottom: 8px !important;
  }
  .cta-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(1),
  .cta-row [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1),
  .cta-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(3),
  .cta-row [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3) {
    display: none !important;
  }
  .cta-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2),
  .cta-row [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) {
    min-width: 100% !important; flex: 0 0 100% !important;
    width: 100% !important; max-width: 100% !important;
  }

  /* Filter bar */
  .filter-bar-wrap {
    padding: 10px 8px; background: var(--color-cloud-gray);
    border-bottom: 1px solid var(--color-mercury-stroke); margin-bottom: 14px;
  }
  .filter-bar-wrap div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"],
  .filter-bar-wrap [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    min-width: 33% !important; flex: 0 0 33% !important;
    width: 33% !important; max-width: 33% !important;
    padding-left: 3px !important; padding-right: 3px !important;
  }
  .filter-bar-wrap .stSelectbox label {
    font-size: 0.64em !important; color: var(--color-muted-stone) !important;
    text-transform: uppercase !important; letter-spacing: 0.6px !important;
  }
  .filter-bar-wrap .stSelectbox > div > div {
    border: 1px solid var(--color-silver-mist) !important;
    border-radius: var(--radius-inputs) !important;
    background: var(--color-canvas-white) !important; font-size: 0.78em !important;
    min-height: 34px !important;
  }

  /* ══════════════════════════════════════════════
     SECTION HEADINGS
     ══════════════════════════════════════════════ */
  .section-title {
    font-family: 'Inter', sans-serif; font-size: 1.45em; color: var(--color-midnight-ink);
    text-align: center; margin-bottom: 4px; padding: 0 8px;
    font-weight: 700; letter-spacing: -0.2px;
  }
  .section-sub {
    text-align: center; color: var(--color-muted-stone); margin-bottom: 16px; font-size: .70em;
    letter-spacing: 0.3px;
  }
  .divider { border: none; border-top: 1px solid var(--color-mercury-stroke); margin: 24px auto; width: 40px; }

  /* ══════════════════════════════════════════════
     IFRAME / CAROUSEL GAP FIX
     ══════════════════════════════════════════════ */
  [data-testid="stIFrame"] { margin-bottom: -20px !important; }
  [data-testid="stVerticalBlock"] > [data-testid="element-container"]:has([data-testid="stIFrame"]) { margin-bottom: 0 !important; padding-bottom: 0 !important; }

  /* ══════════════════════════════════════════════
     CATEGORY TILES
     ══════════════════════════════════════════════ */
  .cat-tiles-section { padding: 20px 10px 12px; background: var(--color-canvas-white); }
  .cat-tiles-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(88px, 1fr));
    gap: var(--element-gap); margin-top: 10px;
  }
  .cat-tile {
    background: var(--color-cloud-gray); padding: 14px 4px 10px; text-align: center;
    cursor: pointer; transition: background 0.2s;
    text-decoration: none; display: block;
    border-radius: var(--radius-cards);
  }
  .cat-tile:hover { background: var(--color-mercury-stroke); }
  .cat-tile-emoji { font-size: 1.5em; display: block; margin-bottom: 5px; }
  .cat-tile-img {
    width: 44px; height: 44px; object-fit: cover; border-radius: 50%;
    display: block; margin: 0 auto 5px;
  }
  .cat-tile-label {
    font-family: 'Inter', sans-serif; font-size: 0.60em;
    font-weight: 600; color: var(--color-midnight-ink); display: block;
    letter-spacing: 0.3px;
  }

  /* ══════════════════════════════════════════════
     TRUST SECTION
     ══════════════════════════════════════════════ */
  .trust-section { background: var(--color-cloud-gray); padding: 28px 10px 24px; margin: 16px 0 0; }
  .trust-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--element-gap); margin-top: 14px; }
  .trust-card { background: var(--color-canvas-white); padding: 16px 8px; text-align: center; border-radius: var(--radius-cards); }
  .trust-card-icon { font-size: 1.4em; margin-bottom: 8px; display: block; }
  .trust-card-title {
    font-family: 'Inter', sans-serif; font-size: 0.64em; font-weight: 700;
    color: var(--color-midnight-ink); margin-bottom: 4px;
    letter-spacing: 0.3px; display: block;
  }
  .trust-card-desc { font-size: 0.60em; color: var(--color-muted-stone); line-height: 1.5; }

  /* ══════════════════════════════════════════════
     BRAND STORY
     ══════════════════════════════════════════════ */
  .brand-story { background: var(--color-midnight-ink); color: var(--color-canvas-white); padding: 44px 16px; text-align: center; }
  .brand-story h2 {
    font-family: 'Inter', sans-serif; font-size: 1.35em; font-weight: 700;
    color: var(--color-canvas-white); margin-bottom: 14px; letter-spacing: -0.2px;
  }
  .brand-story p {
    font-size: 0.80em; line-height: 1.9; color: rgba(255,255,255,0.6);
    max-width: 460px; margin: 0 auto;
  }
  .brand-story-stats {
    display: flex; justify-content: center; gap: 32px; margin-top: 28px; flex-wrap: wrap;
  }
  .stat-item { text-align: center; }
  .stat-num {
    font-family: 'Inter', sans-serif; font-size: 1.7em; font-weight: 700;
    color: var(--color-violet-impulse); display: block;
  }
  .stat-label { font-size: 0.58em; color: rgba(255,255,255,0.45); letter-spacing: 0.5px; text-transform: uppercase; }

  /* ══════════════════════════════════════════════
     FOOTER
     ══════════════════════════════════════════════ */
  .footer-enhanced { background: var(--color-midnight-ink); padding: 36px 16px 18px; }
  .footer-brand { text-align: center; margin-bottom: 28px; }
  .footer-brand h3 {
    font-family: 'Inter', sans-serif; color: var(--color-canvas-white);
    font-size: 1.15em; font-weight: 700; margin-bottom: 6px; letter-spacing: 0.3px;
  }
  .footer-brand p { color: var(--color-muted-stone); font-size: 0.70em; }
  .footer-links-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px 16px; margin-bottom: 24px; }
  .footer-col h4 {
    color: var(--color-canvas-white); font-size: 0.66em; font-weight: 700; margin-bottom: 10px;
    text-transform: uppercase; letter-spacing: 0.8px;
  }
  .footer-col a {
    display: block; color: var(--color-muted-stone); text-decoration: none;
    font-size: 0.68em; margin-bottom: 7px; transition: color 0.2s;
  }
  .footer-col a:hover { color: var(--color-violet-impulse); }
  .footer-social { text-align: center; margin-bottom: 20px; }
  .footer-social h4 {
    color: var(--color-canvas-white); font-size: 0.66em; font-weight: 700; margin-bottom: 12px;
    text-transform: uppercase; letter-spacing: 0.8px;
  }
  .social-icons { display: flex; justify-content: center; gap: 10px; }
  .social-icon {
    width: 34px; height: 34px; border-radius: 50%;
    background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.11);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.95em; text-decoration: none; color: var(--color-muted-stone); transition: all 0.2s;
  }
  .social-icon:hover { background: rgba(105,80,243,0.2); color: var(--color-violet-impulse); }
  .footer-payment {
    text-align: center; margin-bottom: 16px; padding-top: 16px;
    border-top: 1px solid rgba(255,255,255,0.07);
  }
  .footer-payment p {
    color: var(--color-muted-stone); font-size: 0.62em; margin-bottom: 8px;
    letter-spacing: 0.3px; text-transform: uppercase;
  }
  .payment-icons { display: flex; justify-content: center; gap: 8px; flex-wrap: wrap; }
  .payment-icon {
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.12);
    padding: 4px 10px; font-size: 0.60em; color: var(--color-muted-stone);
    font-weight: 600; letter-spacing: 0.3px; border-radius: var(--radius-smallelements);
  }
  .footer-bottom {
    text-align: center; padding-top: 14px;
    border-top: 1px solid rgba(255,255,255,0.05); color: var(--color-muted-stone); font-size: 0.62em;
  }

  /* ══════════════════════════════════════════════
     CART DIALOG
     ══════════════════════════════════════════════ */
  .cart-dialog-item {
    background: var(--color-cloud-gray); padding: 12px 14px; margin-bottom: 8px;
    border-left: 3px solid var(--color-violet-impulse);
    border-radius: var(--radius-cards);
  }

  /* ══════════════════════════════════════════════
     WISHLIST PAGE
     ══════════════════════════════════════════════ */
  .wishlist-page { padding: 20px 10px 32px; }
  .wishlist-empty { text-align: center; padding: 48px 20px; }
  .wishlist-empty-icon { font-size: 3em; margin-bottom: 16px; }
  .wishlist-empty h3 {
    font-family: 'Inter', sans-serif; color: var(--color-midnight-ink);
    font-size: 1.5em; font-weight: 700; margin-bottom: 8px;
  }
  .wishlist-empty p { color: var(--color-muted-stone); font-size: 0.82em; }

  .wishlist-card-name { font-size: 0.76em; color: var(--color-midnight-ink); font-weight: 500; margin-bottom: 4px; }
  .wishlist-card-price { font-size: 0.76em; color: var(--color-violet-impulse); font-weight: 700; }

  /* ══════════════════════════════════════════════
     GLOBAL BUTTON RESETS
     ══════════════════════════════════════════════ */
  div[data-testid="stMainBlockContainer"] .stButton > button[kind="primary"],
  div[data-testid="stMainBlockContainer"] [data-testid="stBaseButton-primary"] {
    background: var(--color-midnight-ink) !important; color: var(--color-canvas-white) !important;
    border: none !important; border-radius: var(--radius-buttons) !important;
    font-weight: 600 !important; letter-spacing: 0.3px !important;
    transition: background 0.2s !important;
  }
  div[data-testid="stMainBlockContainer"] .stButton > button[kind="primary"]:hover,
  div[data-testid="stMainBlockContainer"] [data-testid="stBaseButton-primary"]:hover {
    background: #2a2a2a !important;
  }
  div[data-testid="stMainBlockContainer"] .stButton > button[kind="secondary"],
  div[data-testid="stMainBlockContainer"] [data-testid="stBaseButton-secondary"] {
    background: transparent !important; color: var(--color-violet-impulse) !important;
    border: 1px solid var(--color-violet-impulse) !important;
    border-radius: var(--radius-buttons) !important;
    font-weight: 500 !important;
  }
  .stTextInput > div > div > input {
    border: 1px solid var(--color-silver-mist) !important;
    border-radius: var(--radius-inputs) !important;
    font-size: 0.84em !important;
  }
  .stTextArea > div > div > textarea {
    border: 1px solid var(--color-silver-mist) !important;
    border-radius: var(--radius-cards) !important;
    font-size: 0.84em !important;
  }
  .stSelectbox > div > div {
    border-radius: var(--radius-inputs) !important;
  }

  /* ══════════════════════════════════════════════
     TABLET — min-width: 600px
     ══════════════════════════════════════════════ */
  @media (min-width: 600px) {
    .navbar-wrap { padding: 0 24px; height: 60px; }
    .navbar-brand { font-size: 1.25em; }
    .content-pad { padding: 0 14px; }
    [data-testid="stHorizontalBlock"]:has(.product-card) > [data-testid="stColumn"] {
      min-width: 25% !important; flex: 0 0 25% !important; width: 25% !important; max-width: 25% !important;
    }
    [data-testid="stHorizontalBlock"].has-product-cards > [data-testid="stColumn"] {
      min-width: 25% !important; flex: 0 0 25% !important; width: 25% !important; max-width: 25% !important;
    }
    .product-name { font-size: 0.74em; }
    .section-title { font-size: 1.75em; }
    .footer-links-grid { grid-template-columns: repeat(4, 1fr); }
    .trust-section { padding: 28px 14px 24px; }
    .cat-tiles-section { padding: 22px 14px 12px; }
    .filter-bar-wrap { padding: 10px 14px; }
    .wishlist-grid { grid-template-columns: repeat(3, 1fr); }
  }

  /* ══════════════════════════════════════════════
     LARGE TABLET — min-width: 768px
     ══════════════════════════════════════════════ */
  @media (min-width: 768px) {
    .navbar-brand { font-size: 1.35em; }
    .content-pad { padding: 0 22px; }
    .section-title { font-size: 1.92em; }
    .product-name { font-size: 0.78em; }
    .wishlist-grid { grid-template-columns: repeat(4, 1fr); }
  }

  /* ══════════════════════════════════════════════
     DESKTOP — min-width: 960px
     ══════════════════════════════════════════════ */
  @media (min-width: 960px) {
    .navbar-wrap { padding: 0 44px; height: 66px; }
    .navbar-brand { font-size: 1.45em; }
    .content-pad { padding: 0 44px; }
    [data-testid="stHorizontalBlock"]:has(.product-card) > [data-testid="stColumn"] {
      min-width: unset !important; max-width: unset !important; flex: 1 1 0 !important; width: auto !important;
    }
    [data-testid="stHorizontalBlock"].has-product-cards > [data-testid="stColumn"] {
      min-width: unset !important; max-width: unset !important; flex: 1 1 0 !important; width: auto !important;
    }
    .value-props-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"],
    .value-props-row [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
      min-width: unset !important; max-width: unset !important; flex: 1 1 0 !important; width: auto !important;
    }
    .cart-page div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"],
    .cart-page [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
      min-width: 0 !important; max-width: unset !important; width: auto !important; flex: revert !important;
    }
    .detail-page div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"],
    .detail-page [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
      min-width: 0 !important; max-width: unset !important; width: auto !important; flex: revert !important;
    }
    .cta-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(1),
    .cta-row [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1),
    .cta-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(3),
    .cta-row [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3) {
      display: block !important; min-width: unset !important; flex: 1 1 0 !important;
    }
    .cta-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2),
    .cta-row [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) {
      min-width: unset !important; flex: 1 1 0 !important; width: auto !important; max-width: unset !important;
    }
    .product-name { font-size: 0.82em; }
    .section-title { font-size: 2.1em; }
    .cat-tiles-section { padding: 28px 44px 14px; }
    .cat-tiles-grid { grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 14px; }
    .cat-tile { padding: 22px 10px 16px; }
    .cat-tile-img { width: 64px; height: 64px; }
    .cat-tile-emoji { font-size: 2.2em; }
    .cat-tile-label { font-size: 0.74em; }
    .trust-section { padding: 38px 44px 32px; }
    .brand-story { padding: 56px 44px; }
    .brand-story h2 { font-size: 1.75em; }
    .footer-enhanced { padding: 48px 44px 20px; }
    .filter-bar-wrap { padding: 12px 44px; }
    .wishlist-page { padding: 24px 44px 48px; }
  }
</style>
""",
    unsafe_allow_html=True,
)

# ── Session state ─────────────────────────────────────────────────────────────
if "cart" not in st.session_state:
    st.session_state.cart = []
if "wishlist" not in st.session_state:
    st.session_state.wishlist = set()
if "view" not in st.session_state:
    st.session_state.view = "home"
if "selected_product" not in st.session_state:
    st.session_state.selected_product = None
if "checkout_done" not in st.session_state:
    st.session_state.checkout_done = False
if "filter_cat" not in st.session_state:
    st.session_state.filter_cat = "All"
if "filter_color" not in st.session_state:
    st.session_state.filter_color = "All"
if "filter_price" not in st.session_state:
    st.session_state.filter_price = None
if "filter_sort" not in st.session_state:
    st.session_state.filter_sort = "Featured"

# ── Query-param redirect handler ──────────────────────────────────────────────
_product_id = st.query_params.get("product_id", "")
if _product_id:
    _all_p = load_products()
    _match = next((p for p in _all_p if str(p["id"]) == str(_product_id)), None)
    if _match:
        st.session_state.selected_product = _match
        st.session_state.view = "detail"
    st.query_params.clear()
    st.rerun()

_nav_redirect = st.query_params.get("nav_redirect", "")
if _nav_redirect:
    if _nav_redirect == "shop":
        st.session_state.view = "shop"
        st.session_state.filter_cat = "All"
        st.session_state.selected_product = None
    elif _nav_redirect.startswith("category:"):
        _cat = _nav_redirect[len("category:"):]
        st.session_state.view = "shop"
        st.session_state.filter_cat = _cat
        st.session_state.selected_product = None
    elif _nav_redirect == "home":
        st.session_state.view = "home"
        st.session_state.selected_product = None
    elif _nav_redirect == "wishlist":
        st.session_state.view = "wishlist"
        st.session_state.selected_product = None
    elif _nav_redirect == "cart":
        st.session_state.view = "cart"
        st.session_state.selected_product = None
    elif _nav_redirect == "manage":
        st.query_params.clear()
        st.switch_page("pages/1_Manage_Service.py")
    st.query_params.clear()
    st.rerun()


# ── Helpers ───────────────────────────────────────────────────────────────────
def add_to_cart(product, qty=1):
    for item in st.session_state.cart:
        if item["id"] == product["id"]:
            item["qty"] += qty
            return
    st.session_state.cart.append({**product, "qty": qty})


def cart_count():
    return sum(i["qty"] for i in st.session_state.cart)


def cart_total():
    return sum(i["price"] * i["qty"] for i in st.session_state.cart)


# ── Cart popup dialog ─────────────────────────────────────────────────────────
@st.dialog("Your Cart")
def cart_popup():
    if not st.session_state.cart:
        st.markdown(
            """<div style='text-align:center;padding:32px 0 24px'>
              <div style='font-size:2.8em;margin-bottom:12px'>🛒</div>
              <h3 style='font-family:"Inter",sans-serif;color:#0d0d0d;font-size:1.3em;font-weight:700;margin-bottom:6px'>Your cart is empty</h3>
              <p style='color:#767676;font-size:0.82em'>Discover our premium earring collection</p>
            </div>""",
            unsafe_allow_html=True,
        )
        if st.button("SHOP NOW", use_container_width=True, type="primary"):
            st.session_state.view = "shop"
            st.rerun()
        return

    for idx, item in enumerate(st.session_state.cart):
        st.markdown(
            f"""<div class="cart-dialog-item">
              <div style="font-weight:600;color:#0d0d0d;font-size:0.88em;margin-bottom:3px">{item['name']}</div>
              <div style="color:#6950f3;font-size:0.80em;font-weight:600">${item['price']:.2f}</div>
            </div>""",
            unsafe_allow_html=True,
        )
        col_minus, col_qty, col_plus, col_sub, col_del = st.columns([1, 1, 1, 2, 1])
        with col_minus:
            if st.button("−", key=f"minus_{idx}", use_container_width=True):
                if st.session_state.cart[idx]["qty"] > 1:
                    st.session_state.cart[idx]["qty"] -= 1
                else:
                    st.session_state.cart.pop(idx)
                st.rerun()
        with col_qty:
            st.markdown(
                f"<div style='text-align:center;font-weight:700;font-size:1em;padding-top:7px'>"
                f"{item['qty']}</div>",
                unsafe_allow_html=True,
            )
        with col_plus:
            if st.button("+", key=f"plus_{idx}", use_container_width=True):
                st.session_state.cart[idx]["qty"] += 1
                st.rerun()
        with col_sub:
            st.markdown(
                f"<div style='text-align:right;font-weight:700;color:#0d0d0d;padding-top:7px;font-size:0.92em'>"
                f"${item['price'] * item['qty']:.2f}</div>",
                unsafe_allow_html=True,
            )
        with col_del:
            if st.button("✕", key=f"rm_{idx}", use_container_width=True):
                st.session_state.cart.pop(idx)
                st.rerun()

    st.markdown("<hr style='border-color:#e5e5e5;margin:16px 0 12px'>", unsafe_allow_html=True)

    subtotal = cart_total()
    shipping = 0.0 if subtotal >= 35 else 4.99
    total = subtotal + shipping

    st.markdown(
        f"""<div style="background:#f2f2f2;padding:16px;border-radius:8px;border-left:3px solid #6950f3">
          <div style="display:flex;justify-content:space-between;margin-bottom:8px;font-size:0.85em">
            <span style="color:#767676">Subtotal</span>
            <strong>${subtotal:.2f}</strong>
          </div>
          <div style="display:flex;justify-content:space-between;margin-bottom:6px;font-size:0.85em">
            <span style="color:#767676">Shipping</span>
            <strong style="color:{'#6950f3' if shipping == 0 else '#0d0d0d'}">{'FREE' if shipping == 0 else f'${shipping:.2f}'}</strong>
          </div>
          {'<p style="color:#6950f3;font-size:0.74em;margin:4px 0 0">Add $' + f"{35 - subtotal:.2f}" + ' more for free shipping</p>' if shipping > 0 else ''}
          <hr style="border-color:#e5e5e5;margin:10px 0">
          <div style="display:flex;justify-content:space-between;font-size:1.05em">
            <strong>Total</strong>
            <strong style="color:#6950f3">${total:.2f}</strong>
          </div>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("PROCEED TO CHECKOUT", use_container_width=True, type="primary"):
        st.session_state.view = "cart"
        st.rerun()


# ── Hero banner carousel renderer ─────────────────────────────────────────────
def render_hero_carousel():
    banners = load_hero_banners()
    active = sorted(
        [b for b in banners if b.get("enabled", True)],
        key=lambda x: x.get("sequence", 999),
    )
    if not active:
        return

    slides_html = ""
    redirects = []
    for i, b in enumerate(active):
        img_url = resolve_banner_image_url(b.get("image", ""))
        active_class = "active" if i == 0 else ""
        redirect = b.get("redirect_to", "shop")
        redirects.append(redirect)
        slides_html += f"""
        <div class="slide {active_class}" data-idx="{i}">
          <img class="slide-bg" src="{img_url}" alt="{b.get('title', '')}">
          <div class="slide-overlay">
            <div class="slide-content">
              <h2>{b.get('subtitle', '')}</h2>
              <h1>{b.get('title', '')}</h1>
              <button class="shop-btn" onclick="handleClick(event,{i})">{b.get('button_text', 'Shop Now')}</button>
            </div>
          </div>
        </div>"""

    dots_html = "".join([
        f'<button class="dot {"active" if i == 0 else ""}" onclick="dotClick(event,{i})"></button>'
        for i in range(len(active))
    ])

    redirects_json = json.dumps(redirects)

    html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'Inter', ui-sans-serif, system-ui, sans-serif; overflow: hidden; background: transparent; }}

.carousel-container {{
  position: relative; width: 100%; height: 260px;
  overflow: hidden;
  background: radial-gradient(circle, rgb(239,105,151) 20vh, rgb(232,92,186) 40vh, rgb(184,76,220) 60vh);
}}
.slide {{
  position: absolute; inset: 0; opacity: 0;
  transition: opacity 0.8s ease-in-out; cursor: pointer;
}}
.slide.active {{ opacity: 1; }}
.slide-bg {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
.slide-overlay {{
  position: absolute; inset: 0;
  background: linear-gradient(0deg, rgba(13,13,13,0.78) 0%, rgba(13,13,13,0.35) 55%, transparent 100%);
  display: flex; align-items: flex-end; padding: 0 18px 28px;
}}
.slide-content {{ max-width: 100%; color: white; text-align: center; width: 100%; }}
.slide-content h2 {{
  font-size: 0.68em; font-weight: 400; opacity: 0.8;
  margin-bottom: 5px; letter-spacing: 0.5px;
  font-family: 'Inter', sans-serif;
}}
.slide-content h1 {{
  font-size: 1.55em; font-weight: 700; line-height: 1.1;
  margin-bottom: 16px; color: #fff;
  font-family: 'Inter', sans-serif; letter-spacing: -0.3px;
}}
.shop-btn {{
  background: #0d0d0d; color: #ffffff; border: none;
  padding: 10px 28px; font-size: 0.72em;
  font-weight: 600; cursor: pointer; letter-spacing: 0.3px;
  transition: all 0.2s; font-family: 'Inter', sans-serif;
  border-radius: 999px;
}}
.shop-btn:hover {{ background: #6950f3; color: #fff; }}
.nav-btn {{
  position: absolute; top: 50%; transform: translateY(-50%);
  background: rgba(255,255,255,0.15); backdrop-filter: blur(4px);
  border: 1px solid rgba(255,255,255,0.3); color: white;
  font-size: 1.2em; width: 32px; height: 32px;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  z-index: 10; transition: background 0.2s; line-height: 1;
  border-radius: 999px;
}}
.nav-btn:hover {{ background: rgba(105,80,243,0.5); }}
.nav-btn.prev {{ left: 10px; }}
.nav-btn.next {{ right: 10px; }}

@media (min-width: 380px) {{
  .carousel-container {{ height: 290px; }}
  .slide-content h1 {{ font-size: 1.75em; }}
}}
@media (min-width: 480px) {{
  .carousel-container {{ height: 340px; }}
  .slide-content h1 {{ font-size: 2.0em; }}
  .shop-btn {{ padding: 11px 32px; }}
}}
@media (min-width: 768px) {{
  .carousel-container {{ height: 420px; }}
  .slide-overlay {{
    background: linear-gradient(90deg, rgba(13,13,13,0.72) 0%, rgba(13,13,13,0.4) 50%, transparent 80%);
    align-items: center; padding: 0 48px;
  }}
  .slide-content {{ max-width: 55%; text-align: left; width: auto; }}
  .slide-content h1 {{ font-size: 2.4em; margin-bottom: 18px; }}
  .slide-content h2 {{ font-size: 0.88em; }}
  .shop-btn {{ padding: 12px 34px; font-size: 0.76em; }}
  .nav-btn {{ width: 42px; height: 42px; font-size: 1.5em; }}
}}
@media (min-width: 960px) {{
  .carousel-container {{ height: 500px; }}
  .slide-overlay {{ padding: 0 68px; }}
  .slide-content {{ max-width: 48%; }}
  .slide-content h1 {{ font-size: 2.9em; margin-bottom: 22px; }}
  .slide-content h2 {{ font-size: 0.96em; }}
  .shop-btn {{ padding: 13px 40px; font-size: 0.80em; }}
  .nav-btn {{ width: 48px; height: 48px; }}
  .nav-btn.prev {{ left: 14px; }}
  .nav-btn.next {{ right: 14px; }}
}}

.dots {{
  position: absolute; bottom: 18px; left: 50%; transform: translateX(-50%);
  display: flex; gap: 7px; z-index: 10;
}}
.dot {{
  width: 6px; height: 6px; border-radius: 50%;
  background: rgba(255,255,255,0.4); border: none; cursor: pointer;
  transition: all 0.3s; padding: 0;
}}
.dot.active {{ background: #ffffff; width: 22px; border-radius: 999px; }}
</style>
</head>
<body>
<div class="carousel-container" id="carousel">
  {slides_html}
  <button class="nav-btn prev" id="prevBtn">&#8249;</button>
  <button class="nav-btn next" id="nextBtn">&#8250;</button>
  <div class="dots">{dots_html}</div>
</div>
<script>
const redirects = {redirects_json};
const slides = document.querySelectorAll('.slide');
const dots = document.querySelectorAll('.dot');
let current = parseInt(localStorage.getItem('hero_slide') || '0');
if (current >= slides.length) current = 0;
let timer;

function goTo(n) {{
  slides[current].classList.remove('active');
  dots[current].classList.remove('active');
  current = ((n % slides.length) + slides.length) % slides.length;
  slides[current].classList.add('active');
  dots[current].classList.add('active');
  localStorage.setItem('hero_slide', current);
}}

function resetTimer() {{
  clearInterval(timer);
  timer = setInterval(() => goTo(current + 1), 5000);
}}

goTo(current);
resetTimer();

document.getElementById('prevBtn').addEventListener('click', (e) => {{
  e.stopPropagation(); goTo(current - 1); resetTimer();
}});
document.getElementById('nextBtn').addEventListener('click', (e) => {{
  e.stopPropagation(); goTo(current + 1); resetTimer();
}});

function handleClick(e, idx) {{ e.stopPropagation(); navigateTo(redirects[idx]); }}
function dotClick(e, idx) {{ e.stopPropagation(); goTo(idx); resetTimer(); }}

document.querySelectorAll('.slide').forEach((slide, i) => {{
  slide.addEventListener('click', () => navigateTo(redirects[i]));
}});

function navigateTo(redirect) {{
  if (!redirect) return;
  if (redirect.startsWith('http://') || redirect.startsWith('https://')) {{
    window.open(redirect, '_blank');
  }} else {{
    window.top.location.href = window.top.location.pathname + '?nav_redirect=' + encodeURIComponent(redirect);
  }}
}}

function reportHeight() {{
  const h = document.getElementById('carousel').offsetHeight;
  if (h > 0) {{
    window.parent.postMessage({{type: 'streamlit:setFrameHeight', height: h}}, '*');
  }}
}}
reportHeight();
setTimeout(reportHeight, 50);
setTimeout(reportHeight, 200);
setTimeout(reportHeight, 500);
setTimeout(reportHeight, 1000);
window.addEventListener('resize', function() {{ setTimeout(reportHeight, 50); }});
if (window.ResizeObserver) {{
  new ResizeObserver(reportHeight).observe(document.getElementById('carousel'));
}}
</script>
</body>
</html>
"""
    components.html(html, height=270, scrolling=False)


# ── Promo ticker ──────────────────────────────────────────────────────────────
def render_promo_ticker():
    promos = [
        "FREE SHIPPING on all orders over $35",
        "BUY 2 GET 10% OFF — Use code LOVE10",
        "NEW ARRIVALS — Hoops, Drops &amp; Chandeliers",
        "HYPOALLERGENIC &amp; SKIN-SAFE jewellery",
        "FREE GIFT WRAPPING on every order",
        "30-DAY HASSLE-FREE RETURNS",
        "4.8★ RATED by 10,000+ happy customers",
    ]
    items_html = "".join(f"<span>{p}</span>" for p in promos)
    ticker_content = items_html + items_html
    st.markdown(
        f'<div class="promo-ticker"><div class="promo-ticker-inner">{ticker_content}</div></div>',
        unsafe_allow_html=True,
    )


def render_free_shipping_bar():
    st.markdown(
        '<div class="free-shipping-bar">'
        '✦ FREE SHIPPING on orders over $35 &nbsp;&nbsp;·&nbsp;&nbsp; '
        '✦ Free gift wrapping &nbsp;&nbsp;·&nbsp;&nbsp; '
        '✦ 30-Day returns'
        '</div>',
        unsafe_allow_html=True,
    )


# ── Navbar with hamburger ─────────────────────────────────────────────────────
def render_navbar():
    cart_n = cart_count()
    wl_n = len(st.session_state.wishlist)
    cart_label = f"🛒 {cart_n}" if cart_n > 0 else "🛒"
    wl_label = f"♡ {wl_n}" if wl_n > 0 else "♡"

    # ── Self-contained JS snippets ──────────────────────────────────────────────
    # These run entirely in the parent window (where st.markdown HTML lives),
    # so they never depend on the components.html iframe being loaded first.
    _open_js = (
        "(function(){"
        "var o=document.getElementById('navOverlay'),"
        "b=document.getElementById('navBg');"
        "if(o)o.classList.add('open');"
        "if(b)b.classList.add('open');"
        "document.body.style.overflow='hidden';"
        "})()"
    )
    _close_js = (
        "(function(){"
        "var o=document.getElementById('navOverlay'),"
        "b=document.getElementById('navBg');"
        "if(o)o.classList.remove('open');"
        "if(b)b.classList.remove('open');"
        "document.body.style.overflow='';"
        "})()"
    )

    def _nav_js(dest):
        """Close the slide-in menu and navigate — zero iframe dependency."""
        return (
            "(function(){"
            "var o=document.getElementById('navOverlay'),"
            "b=document.getElementById('navBg');"
            "if(o)o.classList.remove('open');"
            "if(b)b.classList.remove('open');"
            "document.body.style.overflow='';"
            f"window.top.location.href=window.location.pathname+'?nav_redirect={dest}';"
            "})()"
        )

    st.markdown(
        f"""
<div class="navbar-wrap" id="main-navbar">
  <div class="navbar-left">
    <button class="hamburger-btn" onclick="{_open_js}" aria-label="Open menu">
      <span></span>
      <span></span>
      <span></span>
    </button>
  </div>
  <a href="?nav_redirect=home" target="_top" onclick="window.top.location.href=window.location.pathname+'?nav_redirect=home'; return false;" class="navbar-brand">💎 Love Earrings</a>
  <div class="navbar-right">
    <a href="?nav_redirect=wishlist" target="_top" onclick="window.top.location.href=window.location.pathname+'?nav_redirect=wishlist'; return false;" class="navbar-icon-link">{wl_label}</a>
    <a href="?nav_redirect=cart" target="_top" onclick="window.top.location.href=window.location.pathname+'?nav_redirect=cart'; return false;" class="navbar-icon-link">{cart_label}</a>
  </div>
</div>

<!-- Backdrop -->
<div class="nav-overlay-bg" id="navBg" onclick="{_close_js}"></div>

<!-- Slide-in menu -->
<div class="nav-overlay" id="navOverlay">
  <div class="nav-overlay-header">
    <span class="nav-overlay-brand">💎 Love Earrings</span>
    <button class="nav-close-btn" onclick="{_close_js}">✕</button>
  </div>
  <div class="nav-overlay-links">
    <a href="?nav_redirect=home" target="_top" onclick="{_nav_js('home')}; return false;" style="cursor:pointer">Home</a>
    <a href="?nav_redirect=shop" target="_top" onclick="{_nav_js('shop')}; return false;" style="cursor:pointer">Shop All</a>
    <a href="?nav_redirect=wishlist" target="_top" onclick="{_nav_js('wishlist')}; return false;" style="cursor:pointer">Wishlist</a>
    <a href="?nav_redirect=manage" target="_top" onclick="{_nav_js('manage')}; return false;" style="cursor:pointer">Manage Website</a>
  </div>
  <div class="nav-overlay-section">
    <h4>Shop by Category</h4>
    <a href="?nav_redirect=category:Studs" target="_top" onclick="{_nav_js('category:Studs')}; return false;" style="cursor:pointer">Studs</a>
    <a href="?nav_redirect=category:Hoops" target="_top" onclick="{_nav_js('category:Hoops')}; return false;" style="cursor:pointer">Hoops</a>
    <a href="?nav_redirect=category:Drops" target="_top" onclick="{_nav_js('category:Drops')}; return false;" style="cursor:pointer">Drops</a>
    <a href="?nav_redirect=category:Chandeliers" target="_top" onclick="{_nav_js('category:Chandeliers')}; return false;" style="cursor:pointer">Chandeliers</a>
    <a href="?nav_redirect=category:Dangles" target="_top" onclick="{_nav_js('category:Dangles')}; return false;" style="cursor:pointer">Dangles</a>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Inject sticky-navbar JS, link-intercept JS, and Escape-key handler
    components.html(
        """
<script>
(function() {
  var p = window.parent;

  /* ── Hamburger open / close (also used by Escape key) ────────────────────────
     The inline onclick on the hamburger/close/backdrop already handles clicks
     directly (no iframe dependency). This block only adds:
       • Escape key to close
       • MutationObserver fallback — re-attaches addEventListener as a
         belt-and-suspenders backup after every Streamlit rerender
  ──────────────────────────────────────────────────────────────────────────── */
  function openMenu() {
    var o = p.document.getElementById('navOverlay');
    var b = p.document.getElementById('navBg');
    if (o) o.classList.add('open');
    if (b) b.classList.add('open');
    p.document.body.style.overflow = 'hidden';
  }

  function closeMenu() {
    var o = p.document.getElementById('navOverlay');
    var b = p.document.getElementById('navBg');
    if (o) o.classList.remove('open');
    if (b) b.classList.remove('open');
    p.document.body.style.overflow = '';
  }

  /* Fallback addEventListener attachment — covers any edge case where the
     inline onclick attribute was stripped by a middleware / browser extension */
  function attachHandlers() {
    var hambtn   = p.document.querySelector('.hamburger-btn');
    var closebtn = p.document.querySelector('.nav-close-btn');
    var bg       = p.document.getElementById('navBg');

    if (hambtn && !hambtn._navAttached) {
      hambtn.addEventListener('click', openMenu);
      hambtn._navAttached = true;
    }
    if (closebtn && !closebtn._navAttached) {
      closebtn.addEventListener('click', closeMenu);
      closebtn._navAttached = true;
    }
    if (bg && !bg._navAttached) {
      bg.addEventListener('click', closeMenu);
      bg._navAttached = true;
    }
  }

  attachHandlers();
  setTimeout(attachHandlers, 200);

  /* Re-attach after every Streamlit rerender (DOM replacement) */
  if (!p._navMutationObserver) {
    p._navMutationObserver = new MutationObserver(function() {
      var hambtn = p.document.querySelector('.hamburger-btn');
      if (hambtn && !hambtn._navAttached) attachHandlers();
    });
    p._navMutationObserver.observe(p.document.body, { childList: true, subtree: true });
  }

  /* Escape key always closes the menu */
  if (!p._navEscInstalled) {
    p._navEscInstalled = true;
    p.document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') closeMenu();
    });
  }

  /* ── Sticky navbar ──────────────────────────────────────────────────────────
     position:sticky can break inside Streamlit's nested overflow containers.
     We implement it manually: once the user scrolls past the navbar's natural
     position, we switch it to position:fixed and insert a same-height spacer
     so the content below doesn't jump.
  ──────────────────────────────────────────────────────────────────────────── */
  function initStickyNav() {
    var nav = p.document.querySelector('.navbar-wrap');
    if (!nav || nav._stickyInit) return;
    nav._stickyInit = true;

    var getScrollY = function() {
      return p.window.pageYOffset || p.document.documentElement.scrollTop || 0;
    };

    // Measure where the navbar sits in the initial layout
    var navTop = nav.getBoundingClientRect().top + getScrollY();
    var navH   = nav.offsetHeight;
    var isFixed = false;

    function applyFixed() {
      if (isFixed) return;
      isFixed = true;
      nav.style.setProperty('position', 'fixed',  'important');
      nav.style.setProperty('top',      '0',      'important');
      nav.style.setProperty('left',     '0',      'important');
      nav.style.setProperty('right',    '0',      'important');
      nav.style.setProperty('width',    '100%',   'important');
      nav.style.setProperty('z-index',  '9999',   'important');
      if (!p.document.getElementById('__navbar_spacer__')) {
        var sp = p.document.createElement('div');
        sp.id = '__navbar_spacer__';
        sp.style.height = navH + 'px';
        nav.parentNode.insertBefore(sp, nav.nextSibling);
      }
    }

    function removeFixed() {
      if (!isFixed) return;
      isFixed = false;
      ['position','top','left','right','width','z-index'].forEach(function(prop) {
        nav.style.removeProperty(prop);
      });
      var sp = p.document.getElementById('__navbar_spacer__');
      if (sp) sp.remove();
    }

    function onScroll() {
      if (getScrollY() >= navTop) { applyFixed(); } else { removeFixed(); }
    }

    p.window.addEventListener('scroll', onScroll, { passive: true });
    onScroll(); // run once on init
  }

  setTimeout(initStickyNav, 200);
  setTimeout(initStickyNav, 700);
  setTimeout(initStickyNav, 1800);

  /* ── Product grid 2-col mobile fallback ─────────────────────────────────────
     Stamps .has-product-cards on every stHorizontalBlock that contains a
     .product-card, enabling the CSS 50%/25% column rules that mirror the
     :has(.product-card) selector (for browsers or environments where :has()
     doesn't fire reliably).
  ──────────────────────────────────────────────────────────────────────────── */
  function stampProductGridClass() {
    var blocks = p.document.querySelectorAll('[data-testid="stHorizontalBlock"]');
    blocks.forEach(function(block) {
      if (block.querySelector('.product-card') && !block.classList.contains('has-product-cards')) {
        block.classList.add('has-product-cards');
      }
    });
  }

  stampProductGridClass();
  setTimeout(stampProductGridClass, 300);
  setTimeout(stampProductGridClass, 800);
  setTimeout(stampProductGridClass, 2000);

  if (!p._productGridObserver) {
    p._productGridObserver = new MutationObserver(function() {
      stampProductGridClass();
    });
    p._productGridObserver.observe(p.document.body, { childList: true, subtree: true });
  }

  /* ── Navigation: all internal links use target="_top" (no JS interception needed) ── */

})();
</script>
""",
        height=1,
    )


# ── Section renderers ─────────────────────────────────────────────────────────
def render_category_tiles():
    cats = load_shop_categories()
    cats = sorted(
        [c for c in cats if c.get("enabled", True)],
        key=lambda x: x.get("sequence", 999),
    )

    tiles_html = ""
    for cat in cats:
        if cat.get("image"):
            icon = (
                f'<img src="{cat["image"]}" class="cat-tile-img" alt="{cat["name"]}">'
            )
        else:
            icon = f'<span class="cat-tile-emoji">{cat.get("emoji", "🏷️")}</span>'
        cat_redirect = cat["redirect_to"]
        tiles_html += (
            f'<a href="?nav_redirect={cat_redirect}" target="_top" class="cat-tile">'
            f'{icon}'
            f'<span class="cat-tile-label">{cat["name"]}</span>'
            f'</a>'
        )

    st.markdown(
        f"""<div class="cat-tiles-section">
          <h2 class="section-title" style="margin-bottom:2px">Shop by Category</h2>
          <p class="section-sub">Find your perfect style</p>
          <div class="cat-tiles-grid">{tiles_html}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def render_trust_section():
    st.markdown(
        """<div class="trust-section">
          <h2 class="section-title" style="margin-bottom:2px">Shop With Confidence</h2>
          <p class="section-sub">Quality and care in every piece</p>
          <div class="trust-cards">
            <div class="trust-card">
              <span class="trust-card-icon">🌿</span>
              <span class="trust-card-title">Skin Safe</span>
              <span class="trust-card-desc">Hypoallergenic materials, safe for sensitive skin</span>
            </div>
            <div class="trust-card">
              <span class="trust-card-icon">💎</span>
              <span class="trust-card-title">Premium Quality</span>
              <span class="trust-card-desc">Sterling silver, gold-plated &amp; genuine gemstones</span>
            </div>
            <div class="trust-card">
              <span class="trust-card-icon">✅</span>
              <span class="trust-card-title">Authenticity</span>
              <span class="trust-card-desc">Every piece quality-checked before it ships</span>
            </div>
          </div>
        </div>""",
        unsafe_allow_html=True,
    )


def render_brand_story():
    st.markdown(
        """<div class="brand-story">
          <h2>Because You Deserve to Shine</h2>
          <p>Our earrings are crafted for everyday moments — not just special occasions.
          Each piece is designed to be worn daily, loved forever, and passed on with pride.
          From minimalist studs to statement chandeliers, find the pair that tells your story.</p>
          <div class="brand-story-stats">
            <div class="stat-item">
              <span class="stat-num">10K+</span>
              <span class="stat-label">Happy Customers</span>
            </div>
            <div class="stat-item">
              <span class="stat-num">200+</span>
              <span class="stat-label">Unique Styles</span>
            </div>
            <div class="stat-item">
              <span class="stat-num">4.8★</span>
              <span class="stat-label">Avg. Rating</span>
            </div>
          </div>
        </div>""",
        unsafe_allow_html=True,
    )


def render_footer():
    st.markdown(
        """<div class="footer-enhanced">
          <div class="footer-brand">
            <h3>💎 Love Earrings</h3>
            <p>Crafted with love, worn with pride.</p>
          </div>
          <div class="footer-links-grid">
            <div class="footer-col">
              <h4>Shop</h4>
              <a href="?nav_redirect=shop" target="_top">All Earrings</a>
              <a href="?nav_redirect=category:Studs" target="_top">Studs</a>
              <a href="?nav_redirect=category:Hoops" target="_top">Hoops</a>
              <a href="?nav_redirect=category:Drops" target="_top">Drops</a>
              <a href="?nav_redirect=category:Chandeliers" target="_top">Chandeliers</a>
            </div>
            <div class="footer-col">
              <h4>Help</h4>
              <a href="#">FAQ</a>
              <a href="#">Contact Us</a>
              <a href="#">Track Order</a>
              <a href="#">Returns Portal</a>
            </div>
            <div class="footer-col">
              <h4>Policies</h4>
              <a href="#">Shipping &amp; Delivery</a>
              <a href="#">Return &amp; Exchange</a>
              <a href="#">Privacy Policy</a>
              <a href="#">Terms of Service</a>
            </div>
            <div class="footer-col">
              <h4>About</h4>
              <a href="#">Our Story</a>
              <a href="#">Sustainability</a>
              <a href="#">Gifting</a>
              <a href="#">Press</a>
            </div>
          </div>
          <div class="footer-social">
            <h4>Follow Us</h4>
            <div class="social-icons">
              <a href="#" class="social-icon" title="Instagram">📸</a>
              <a href="#" class="social-icon" title="Facebook">👍</a>
              <a href="#" class="social-icon" title="TikTok">🎵</a>
              <a href="#" class="social-icon" title="YouTube">▶️</a>
              <a href="#" class="social-icon" title="Pinterest">📌</a>
            </div>
          </div>
          <div class="footer-payment">
            <p>Secure Payment Methods</p>
            <div class="payment-icons">
              <span class="payment-icon">VISA</span>
              <span class="payment-icon">Mastercard</span>
              <span class="payment-icon">PayPal</span>
              <span class="payment-icon">Google Pay</span>
              <span class="payment-icon">Apple Pay</span>
            </div>
          </div>
          <div class="footer-bottom">
            © 2026 Love Earrings. All rights reserved.
          </div>
        </div>""",
        unsafe_allow_html=True,
    )


# ── Filter & sort helper ──────────────────────────────────────────────────────
def apply_filters(products):
    filtered = list(products)
    cat = st.session_state.filter_cat
    color = st.session_state.filter_color
    prange = st.session_state.filter_price
    sort = st.session_state.filter_sort

    if cat != "All":
        filtered = [p for p in filtered if p["category"] == cat]
    if color != "All":
        filtered = [p for p in filtered if color in p.get("colors", [])]
    if prange:
        filtered = [p for p in filtered if prange[0] <= p["price"] <= prange[1]]
    if sort == "Price: Low to High":
        filtered.sort(key=lambda x: x["price"])
    elif sort == "Price: High to Low":
        filtered.sort(key=lambda x: x["price"], reverse=True)
    elif sort == "Top Rated":
        filtered.sort(key=lambda x: x.get("rating", 0), reverse=True)
    else:
        filtered.sort(key=lambda x: (not x.get("featured", False), -x.get("rating", 0)))
    return filtered


# ── Product card renderer ─────────────────────────────────────────────────────
def render_product_card(p, col):
    with col:
        discount = 0
        if p.get("original_price", 0) > p["price"]:
            discount = int((1 - p["price"] / p["original_price"]) * 100)

        if p.get("featured") and discount == 0:
            left_badge = '<span class="badge-new">NEW</span>'
        elif discount:
            left_badge = f'<span class="badge">-{discount}%</span>'
        else:
            left_badge = ""

        stock = p.get("stock", 0)
        stock_badge = (
            f'<span class="badge-stock">Only {stock} left</span>'
            if 0 < stock < 10 else ""
        )

        orig_html = (
            f'<span class="price-was">${p["original_price"]:.2f}</span>'
            if p.get("original_price") else ""
        )
        disc_html = f'<span class="discount">{discount}% OFF</span>' if discount else ""

        product_url = f"?product_id={p['id']}"

        st.markdown(
            f"""
<div class="product-card">
  <a href="{product_url}" target="_top" class="product-img-link">
    <img src="{p['image']}" alt="{p['name']}">
    {left_badge}
    {stock_badge}
  </a>
  <a href="{product_url}" target="_top" class="product-info-link">
    <div class="product-info">
      <div class="product-name">{p['name']}</div>
      <div class="price-wrap">
        <span class="price-now">${p['price']:.2f}</span>
        {orig_html}{disc_html}
      </div>
    </div>
  </a>
</div>""",
            unsafe_allow_html=True,
        )

        st.markdown('<div class="card-btn-wrap">', unsafe_allow_html=True)
        if st.button("Add to Cart", key=f"cart_{p['id']}", use_container_width=True):
            add_to_cart(p)
            st.toast(f"✅ {p['name']} added to cart!")
        st.markdown('</div>', unsafe_allow_html=True)


# ── Wishlist page renderer ────────────────────────────────────────────────────
def render_wishlist_page():
    st.markdown('<div class="wishlist-page">', unsafe_allow_html=True)

    if st.button("← Back", key="wl_back"):
        st.session_state.view = "home"
        st.rerun()

    st.markdown(
        '<h2 class="section-title" style="margin-top:16px;text-align:left">Your Wishlist</h2>',
        unsafe_allow_html=True,
    )

    all_products = load_products()
    wishlist_products = [p for p in all_products if p["id"] in st.session_state.wishlist]

    if not wishlist_products:
        st.markdown(
            """<div class="wishlist-empty">
              <div class="wishlist-empty-icon">♡</div>
              <h3>Your wishlist is empty</h3>
              <p>Save your favourite pieces here and come back to them anytime.</p>
            </div>""",
            unsafe_allow_html=True,
        )
        if st.button("DISCOVER EARRINGS", type="primary", use_container_width=False):
            st.session_state.view = "shop"
            st.rerun()
    else:
        st.markdown(
            f'<p class="section-sub" style="text-align:left;margin-bottom:16px">{len(wishlist_products)} saved item{"s" if len(wishlist_products) != 1 else ""}</p>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="wishlist-products">', unsafe_allow_html=True)
        for _row_start in range(0, len(wishlist_products), 4):
            _wl_batch = wishlist_products[_row_start:_row_start+4]
            cols = st.columns(4)
            for i, p in enumerate(_wl_batch):
                with cols[i]:
                    discount = 0
                    if p.get("original_price", 0) > p["price"]:
                        discount = int((1 - p["price"] / p["original_price"]) * 100)

                    left_badge = ""
                    if p.get("featured") and discount == 0:
                        left_badge = '<span class="badge-new">NEW</span>'
                    elif discount:
                        left_badge = f'<span class="badge">-{discount}%</span>'

                    orig_html = (
                        f'<span class="price-was">${p["original_price"]:.2f}</span>'
                        if p.get("original_price") else ""
                    )

                    product_url = f"?product_id={p['id']}"

                    st.markdown(
                        f"""<div class="product-card">
                          <a href="{product_url}" target="_top" class="product-img-link">
                            <img src="{p['image']}" alt="{p['name']}">
                            {left_badge}
                          </a>
                          <a href="{product_url}" target="_top" class="product-info-link">
                            <div class="product-info">
                              <div class="product-name">{p['name']}</div>
                              <div class="price-wrap">
                                <span class="price-now">${p['price']:.2f}</span>
                                {orig_html}
                              </div>
                            </div>
                          </a>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                    st.markdown('<div class="card-btn-wrap">', unsafe_allow_html=True)
                    if st.button("Add to Cart", key=f"wl_cart_{p['id']}", use_container_width=True):
                        add_to_cart(p)
                        st.toast(f"✅ {p['name']} added to cart!")
                    st.markdown('</div>', unsafe_allow_html=True)

                    if st.button("Remove", key=f"wl_rm_{p['id']}", use_container_width=True):
                        st.session_state.wishlist.discard(p["id"])
                        st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)  # close wishlist-products

    st.markdown('</div>', unsafe_allow_html=True)  # close wishlist-page
    render_footer()


# ═════════════════════════════════════════════════════════════════════════════
# TOP NAVIGATION — always rendered
# ═════════════════════════════════════════════════════════════════════════════
render_promo_ticker()
render_navbar()
render_free_shipping_bar()


# ═════════════════════════════════════════════════════════════════════════════
# VIEW: HOME
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.view == "home":

    render_hero_carousel()
    render_category_tiles()
    st.markdown("<div style='margin-bottom:20px'></div>", unsafe_allow_html=True)

    st.markdown('<div class="content-pad">', unsafe_allow_html=True)

    all_products = load_products()

    # Featured section
    st.markdown('<h2 class="section-title">✦ Featured Collection</h2>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Handpicked favourites loved by thousands</p>', unsafe_allow_html=True)
    featured = [p for p in all_products if p.get("featured")]
    if featured:
        for i in range(0, len(featured), 4):
            cols = st.columns(4)
            for j, p in enumerate(featured[i:i+4]):
                render_product_card(p, cols[j])

    # More Earrings section
    non_featured = [p for p in all_products if not p.get("featured")]
    if non_featured:
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown('<h2 class="section-title">All Earrings</h2>', unsafe_allow_html=True)
        st.markdown('<p class="section-sub">Explore our full collection</p>', unsafe_allow_html=True)
        for i in range(0, len(non_featured), 4):
            cols2 = st.columns(4)
            for j, p in enumerate(non_featured[i:i+4]):
                render_product_card(p, cols2[j])

    st.markdown('</div>', unsafe_allow_html=True)

    render_trust_section()

    # Value props
    st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="content-pad">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">Why Love Earrings?</h2>', unsafe_allow_html=True)
    st.markdown('<div class="value-props-row">', unsafe_allow_html=True)
    v1, v2, v3, v4 = st.columns(4)
    for col, icon, title, desc in [
        (v1, "🚚", "Free Shipping", "On orders over $35"),
        (v2, "💎", "Premium Quality", "Hypoallergenic materials"),
        (v3, "↩️", "30-Day Returns", "Hassle-free returns"),
        (v4, "🔒", "Secure Payment", "100% safe checkout"),
    ]:
        with col:
            st.markdown(
                f"""<div style="text-align:center;padding:24px 12px;background:#f2f2f2;border-radius:8px">
                <div style="font-size:1.8em;margin-bottom:8px">{icon}</div>
                <div style="font-family:'Inter',sans-serif;font-weight:600;color:#0d0d0d;font-size:0.92em;margin-bottom:4px">{title}</div>
                <div style="color:#767676;font-size:0.76em">{desc}</div>
            </div>""",
                unsafe_allow_html=True,
            )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="cta-row">', unsafe_allow_html=True)
    _, mid, _ = st.columns([2, 1, 2])
    with mid:
        if st.button("SHOP ALL EARRINGS", use_container_width=True, type="primary"):
            st.session_state.view = "shop"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    render_brand_story()
    render_footer()


# ═════════════════════════════════════════════════════════════════════════════
# VIEW: SHOP
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.view == "shop":
    render_hero_carousel()

    st.markdown('<div class="content-pad">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title" style="margin-top:20px">All Earrings</h2>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Inline filter bar
    all_products_raw = load_products()
    categories = ["All"] + sorted({p["category"] for p in all_products_raw})
    all_colors = sorted({c for p in all_products_raw for c in p.get("colors", [])})
    color_options = ["All"] + all_colors
    sort_options = ["Featured", "Price: Low to High", "Price: High to Low", "Top Rated"]

    prices = [p["price"] for p in all_products_raw]
    price_min, price_max = float(min(prices)), float(max(prices))
    if st.session_state.filter_price is None:
        st.session_state.filter_price = (price_min, price_max)

    cat_idx = categories.index(st.session_state.filter_cat) if st.session_state.filter_cat in categories else 0
    sort_idx = sort_options.index(st.session_state.filter_sort) if st.session_state.filter_sort in sort_options else 0

    st.markdown('<div class="filter-bar-wrap">', unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1:
        selected_cat = st.selectbox("Category", categories, index=cat_idx, key="shop_cat_filter")
    with f2:
        sort_by = st.selectbox("Sort By", sort_options, index=sort_idx, key="shop_sort_filter")
    with f3:
        search = st.text_input("Search", placeholder="Search earrings...", key="shop_search")
    st.markdown('</div>', unsafe_allow_html=True)

    st.session_state.filter_cat = selected_cat
    st.session_state.filter_sort = sort_by

    all_products = all_products_raw
    if search:
        q = search.lower()
        all_products = [
            p for p in all_products
            if q in p["name"].lower()
            or q in p.get("description", "").lower()
            or any(q in t for t in p.get("tags", []))
        ]

    products = apply_filters(all_products)

    st.markdown('<div class="content-pad">', unsafe_allow_html=True)
    st.markdown(
        f'<p class="section-sub" style="text-align:left">{len(products)} earrings found</p>',
        unsafe_allow_html=True,
    )

    if not products:
        st.info("No earrings match your filters.")
    else:
        for i in range(0, len(products), 4):
            cols = st.columns(4)
            for j, p in enumerate(products[i:i+4]):
                render_product_card(p, cols[j])

    st.markdown('</div>', unsafe_allow_html=True)
    render_trust_section()
    render_footer()


# ═════════════════════════════════════════════════════════════════════════════
# VIEW: PRODUCT DETAIL
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.view == "detail":
    st.markdown('<div class="content-pad detail-page">', unsafe_allow_html=True)
    p = st.session_state.selected_product
    if not p:
        st.session_state.view = "shop"
        st.rerun()

    if st.button("← Back to Shop", key="detail_back"):
        st.session_state.view = "shop"
        st.session_state.selected_product = None
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    img_col, info_col = st.columns([1, 1])

    with img_col:
        st.image(resolve_image(p["image"]), use_container_width=True)

    with info_col:
        discount = 0
        if p.get("original_price", 0) > p["price"]:
            discount = int((1 - p["price"] / p["original_price"]) * 100)
        stars = "★" * int(p.get("rating", 0)) + "☆" * (5 - int(p.get("rating", 0)))

        stock = p.get("stock", 0)
        stock_warning = (
            f'<div style="background:#f2f2f2;border-left:3px solid #6950f3;'
            f'border-radius:4px;padding:8px 12px;margin-bottom:14px;font-size:0.80em;color:#6950f3;">'
            f'Only {stock} pieces left — order soon!</div>'
            if 0 < stock < 10 else ""
        )

        wishlisted = p["id"] in st.session_state.wishlist

        st.markdown(
            f"""
<h1 style="font-family:'Inter',sans-serif;color:#0d0d0d;font-size:1.75em;font-weight:700;margin-bottom:6px;line-height:1.15">{p['name']}</h1>
<div style="color:#ffc00a;font-size:1em;margin-bottom:12px">{stars}
  <span style="color:#767676;font-size:0.80em;margin-left:4px">({p.get('reviews',0)} reviews)</span>
</div>
<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px">
  <span style="font-size:1.75em;font-weight:700;color:#0d0d0d;font-family:'Inter',sans-serif">${p['price']:.2f}</span>
  {'<span style="text-decoration:line-through;color:#d3d3d3;font-size:1.1em">$' + f"{p['original_price']:.2f}" + '</span>' if p.get('original_price') else ''}
  {'<span style="background:#6950f3;color:#fff;padding:3px 12px;font-size:0.76em;font-weight:600;border-radius:999px">' + str(discount) + '% OFF</span>' if discount else ''}
</div>
{stock_warning}
<p style="color:#767676;line-height:1.75;font-size:0.88em;margin-bottom:16px">{p.get('description','')}</p>
<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px">
  {''.join(f'<span style="background:#f2f2f2;color:#0d0d0d;border:1px solid #e5e5e5;padding:4px 16px;font-size:0.78em;font-weight:500;border-radius:999px">{c}</span>' for c in p.get('colors',[]))}
</div>
<div style="background:#f2f2f2;padding:10px 16px;margin-bottom:20px;font-size:0.82em;color:#767676;border-radius:8px">
  Category: <strong style="color:#0d0d0d">{p.get('category','')}</strong> &nbsp;·&nbsp;
  Stock: <strong style="color:{'#6950f3' if stock > 0 else '#e53935'}">{'In Stock' if stock > 0 else 'Out of Stock'}</strong>
</div>
""",
            unsafe_allow_html=True,
        )

        qty = st.number_input("Quantity", min_value=1, max_value=min(p.get("stock", 1), 10), value=1)

        a1, a2 = st.columns([1, 1])
        with a1:
            if st.button("ADD TO CART", use_container_width=True, type="primary", key="detail_add"):
                add_to_cart(p, qty)
                st.toast(f"✅ {qty} × {p['name']} added to cart!")
        with a2:
            if st.button("BUY NOW", use_container_width=True, key="detail_buy"):
                add_to_cart(p, qty)
                st.session_state.view = "cart"
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        wl_label = "❤️ Saved to Wishlist" if wishlisted else "♡ Add to Wishlist"
        if st.button(wl_label, key=f"wl_detail_{p['id']}", use_container_width=True):
            if wishlisted:
                st.session_state.wishlist.discard(p["id"])
                st.toast("Removed from wishlist")
            else:
                st.session_state.wishlist.add(p["id"])
                st.toast("💛 Saved to wishlist!")
            st.rerun()

    st.markdown("---")
    st.markdown(
        '<h3 style="font-family:\'Inter\',sans-serif;color:#0d0d0d;font-size:1.25em;font-weight:700;margin-bottom:4px">You Might Also Like</h3>',
        unsafe_allow_html=True,
    )
    all_products_rel = load_products()
    related = [
        x for x in all_products_rel
        if x["category"] == p["category"] and x["id"] != p["id"]
    ][:4]
    if related:
        for i in range(0, len(related), 4):
            cols = st.columns(4)
            for j, rp in enumerate(related[i:i+4]):
                render_product_card(rp, cols[j])

    st.markdown('</div>', unsafe_allow_html=True)
    render_footer()


# ═════════════════════════════════════════════════════════════════════════════
# VIEW: CART (full checkout page)
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.view == "cart":
    st.markdown('<div class="content-pad cart-page">', unsafe_allow_html=True)
    st.markdown(
        '<h2 style="font-family:\'Inter\',sans-serif;color:#0d0d0d;font-size:1.65em;font-weight:700;margin:20px 0 4px;text-align:center">Your Cart</h2>',
        unsafe_allow_html=True,
    )

    if st.session_state.checkout_done:
        st.balloons()
        st.success("🎉 Order placed successfully! Thank you for shopping with Love Earrings.")
        st.session_state.checkout_done = False
        st.session_state.cart = []
        if st.button("CONTINUE SHOPPING", type="primary"):
            st.session_state.view = "shop"
            st.rerun()

    elif not st.session_state.cart:
        st.markdown(
            """<div style="text-align:center;padding:48px 20px">
              <div style="font-size:3em;margin-bottom:16px">🛒</div>
              <h3 style="font-family:'Inter',sans-serif;color:#0d0d0d;font-size:1.4em;font-weight:700;margin-bottom:8px">Your cart is empty</h3>
              <p style="color:#767676;font-size:0.84em">Add some beautiful earrings to get started.</p>
            </div>""",
            unsafe_allow_html=True,
        )
        if st.button("SHOP NOW", type="primary"):
            st.session_state.view = "shop"
            st.rerun()
    else:
        cart_col, summary_col = st.columns([3, 2])

        with cart_col:
            st.markdown(
                '<p style="font-size:0.74em;color:#767676;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:12px">Order Items</p>',
                unsafe_allow_html=True,
            )
            for idx, item in enumerate(st.session_state.cart):
                st.markdown(
                    f"""<div style="display:flex;gap:12px;padding:12px;background:#f2f2f2;margin-bottom:8px;border-left:3px solid #6950f3;align-items:center;border-radius:8px">
                      <img src="{item['image']}" style="width:56px;height:56px;object-fit:cover;flex-shrink:0;border-radius:8px">
                      <div style="flex:1;min-width:0">
                        <div style="font-weight:600;font-size:0.86em;color:#0d0d0d;margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{item['name']}</div>
                        <div style="font-size:0.74em;color:#767676">{item.get('category','')}</div>
                        <div style="font-size:0.82em;font-weight:700;color:#6950f3;margin-top:3px">${item['price']:.2f} each</div>
                      </div>
                    </div>""",
                    unsafe_allow_html=True,
                )
                qc1, qc2, qc3 = st.columns([1, 3, 1])
                with qc1:
                    new_qty = st.number_input("Qty", min_value=1, max_value=10, value=item["qty"], key=f"qty_{idx}", label_visibility="collapsed")
                    st.session_state.cart[idx]["qty"] = new_qty
                with qc2:
                    st.markdown(f"<div style='padding-top:6px;font-weight:700;font-size:0.9em'>${item['price'] * new_qty:.2f}</div>", unsafe_allow_html=True)
                with qc3:
                    if st.button("✕", key=f"del_{idx}", use_container_width=True):
                        st.session_state.cart.pop(idx)
                        st.rerun()

        with summary_col:
            subtotal = cart_total()
            shipping = 0 if subtotal >= 35 else 4.99
            total = subtotal + shipping

            st.markdown(
                f"""<div style="background:#f2f2f2;padding:24px;border-radius:12px;border-top:3px solid #6950f3">
                  <p style="font-family:'Inter',sans-serif;font-size:1.1em;font-weight:700;color:#0d0d0d;margin-bottom:18px">Order Summary</p>
                  <div style="display:flex;justify-content:space-between;margin-bottom:10px;font-size:0.86em">
                    <span style="color:#767676">Subtotal</span><strong>${subtotal:.2f}</strong>
                  </div>
                  <div style="display:flex;justify-content:space-between;margin-bottom:8px;font-size:0.86em">
                    <span style="color:#767676">Shipping</span>
                    <strong style="color:{'#6950f3' if shipping == 0 else '#0d0d0d'}">{'FREE' if shipping == 0 else f'${shipping:.2f}'}</strong>
                  </div>
                  {'<p style="color:#6950f3;font-size:0.76em;margin-bottom:10px">Add $' + f"{35 - subtotal:.2f}" + ' more for free shipping</p>' if shipping > 0 else ''}
                  <hr style="border-color:#e5e5e5;margin:12px 0">
                  <div style="display:flex;justify-content:space-between;font-size:1.1em">
                    <strong>Total</strong><strong style="color:#6950f3">${total:.2f}</strong>
                  </div>
                </div>""",
                unsafe_allow_html=True,
            )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<p style="font-size:0.74em;color:#767676;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:10px">Shipping Details</p>',
                unsafe_allow_html=True,
            )
            name = st.text_input("Full Name", placeholder="Your full name")
            email = st.text_input("Email", placeholder="your@email.com")
            address = st.text_area("Delivery Address", height=80, placeholder="Street, City, State, ZIP")

            if st.button("PLACE ORDER", use_container_width=True, type="primary"):
                if not name or not email or not address:
                    st.error("Please fill in all shipping details.")
                else:
                    save_order({
                        "customer_name": name,
                        "customer_email": email,
                        "address": address,
                        "items": [
                            {"id": i["id"], "name": i["name"], "price": i["price"], "qty": i["qty"]}
                            for i in st.session_state.cart
                        ],
                        "total": total,
                    })
                    st.session_state.checkout_done = True
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    render_footer()


# ═════════════════════════════════════════════════════════════════════════════
# VIEW: WISHLIST
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.view == "wishlist":
    render_wishlist_page()
