import json
import streamlit as st
import streamlit.components.v1 as components
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from utils.data_manager import (
    load_products,
    save_order,
    load_nav_categories,
    load_hero_banners,
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

# ── CSS — Palmonas-inspired premium design ────────────────────────────────────
st.markdown(
    """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; box-sizing: border-box; }
  *, *::before, *::after { box-sizing: inherit; }
  body { background: #fff; }

  .block-container {
    padding-top: 0 !important; padding-left: 0 !important;
    padding-right: 0 !important; padding-bottom: 2rem !important;
    max-width: 100% !important;
  }
  section[data-testid="stMain"] > div { padding-left: 0 !important; padding-right: 0 !important; }
  header[data-testid="stHeader"] { display: none !important; }

  /* ── Hide sidebar completely ── */
  [data-testid="collapsedControl"] { display: none !important; }
  [data-testid="stSidebar"] { display: none !important; }

  /* ══════════════════════════════════════════════
     PROMO TICKER
     ══════════════════════════════════════════════ */
  .promo-ticker {
    background: #1A1A1A; color: #D4C4A0;
    padding: 8px 0; overflow: hidden; white-space: nowrap;
    font-size: 0.68em; font-weight: 500; letter-spacing: 0.6px;
  }
  .promo-ticker-inner { display: inline-block; animation: ticker-scroll 32s linear infinite; }
  .promo-ticker-inner span { margin: 0 28px; opacity: 0.88; }
  .promo-ticker-inner span::before { content: '✦'; margin-right: 12px; color: #C9A84C; }
  @keyframes ticker-scroll { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }

  /* ══════════════════════════════════════════════
     NAVBAR
     ══════════════════════════════════════════════ */
  .navbar-wrap {
    background: #fff; border-bottom: 1px solid #E8E4DE;
    padding: 0 14px; height: 54px;
    display: flex; align-items: center; justify-content: space-between;
    position: sticky; top: 0; z-index: 999;
  }
  .navbar-left { display: flex; align-items: center; }
  .navbar-brand {
    font-family: 'Cormorant Garamond', serif; color: #1A1A1A;
    font-size: 1.22em; font-weight: 600; letter-spacing: 1.5px; white-space: nowrap;
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
    display: block; height: 1.5px; background: #1A1A1A;
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
    background: #fff; z-index: 9999;
    transform: translateX(-100%);
    transition: transform 0.32s cubic-bezier(0.4, 0, 0.2, 1);
    display: flex; flex-direction: column;
    box-shadow: 4px 0 32px rgba(0,0,0,0.14);
    overflow-y: auto;
  }
  .nav-overlay.open { transform: translateX(0); }

  .nav-overlay-header {
    display: flex; justify-content: space-between; align-items: center;
    padding: 16px 20px; border-bottom: 1px solid #E8E4DE; flex-shrink: 0;
  }
  .nav-overlay-brand {
    font-family: 'Cormorant Garamond', serif; font-size: 1.15em; font-weight: 600;
    color: #1A1A1A; letter-spacing: 1.5px;
  }
  .nav-close-btn {
    background: none; border: none; cursor: pointer; font-size: 1.4em;
    color: #1A1A1A; padding: 0 4px; line-height: 1; font-weight: 300;
  }
  .nav-overlay-links { padding: 4px 0; flex-shrink: 0; }
  .nav-overlay-links a {
    display: block; padding: 15px 24px;
    font-size: 0.88em; font-weight: 600; color: #1A1A1A;
    text-decoration: none; border-bottom: 1px solid #F5F2ED;
    letter-spacing: 1px; text-transform: uppercase;
    transition: color 0.2s, background 0.2s;
  }
  .nav-overlay-links a:hover { background: #F9F7F4; color: #C9A84C; }

  .nav-overlay-section { padding: 18px 24px; border-top: 1px solid #E8E4DE; flex-shrink: 0; }
  .nav-overlay-section h4 {
    font-size: 0.64em; font-weight: 700; color: #aaa;
    letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 12px;
  }
  .nav-overlay-section a {
    display: block; padding: 10px 0;
    font-size: 0.84em; color: #555; text-decoration: none;
    border-bottom: 1px solid #F0EDE8;
    letter-spacing: 0.3px; transition: color 0.2s;
  }
  .nav-overlay-section a:last-child { border-bottom: none; }
  .nav-overlay-section a:hover { color: #C9A84C; }

  /* Cart icon fixed top-right */
  .navbar-cart-btn {
    position: fixed; top: 9px; right: 14px; z-index: 1001;
  }
  .navbar-cart-btn .stButton > button {
    background: none !important; border: none !important; box-shadow: none !important;
    font-size: 1.1em !important; color: #1A1A1A !important;
    padding: 6px 2px !important; min-height: 0 !important;
    line-height: 1 !important; font-weight: 400 !important;
  }
  .navbar-cart-btn .stButton > button:hover { color: #C9A84C !important; background: none !important; }

  /* Wishlist icon fixed top-right */
  .navbar-wishlist-btn {
    position: fixed; top: 9px; right: 54px; z-index: 1001;
  }
  .navbar-wishlist-btn .stButton > button {
    background: none !important; border: none !important; box-shadow: none !important;
    font-size: 1.1em !important; color: #1A1A1A !important;
    padding: 6px 2px !important; min-height: 0 !important;
    line-height: 1 !important; font-weight: 400 !important;
  }
  .navbar-wishlist-btn .stButton > button:hover { color: #C9A84C !important; background: none !important; }

  /* ══════════════════════════════════════════════
     FREE SHIPPING BAR
     ══════════════════════════════════════════════ */
  .free-shipping-bar {
    background: #F9F7F4; color: #666; text-align: center; padding: 8px 12px;
    font-size: 0.68em; font-weight: 500; letter-spacing: 0.5px;
    border-bottom: 1px solid #EDEAE4;
  }

  /* ══════════════════════════════════════════════
     CATEGORY NAV
     ══════════════════════════════════════════════ */
  .cat-nav-container {
    background: white; padding: 0 8px;
    overflow-x: auto; -webkit-overflow-scrolling: touch;
    border-bottom: 1px solid #F0EDE8;
  }
  .cat-nav-container div[data-testid="stHorizontalBlock"] {
    gap: 0 !important; flex-wrap: nowrap !important; overflow-x: auto !important;
  }
  .cat-nav-container .stButton > button {
    background: none !important; border: none !important; box-shadow: none !important;
    border-bottom: 2px solid transparent !important; border-radius: 0 !important;
    color: #888 !important; font-weight: 500 !important;
    font-size: 0.66em !important; padding: 11px 9px !important;
    white-space: nowrap !important; letter-spacing: 0.8px !important;
    text-transform: uppercase !important;
  }
  .cat-nav-container .stButton > button:hover {
    color: #1A1A1A !important; border-bottom: 2px solid #1A1A1A !important;
    background: none !important;
  }

  /* ══════════════════════════════════════════════
     CONTENT PADDING
     ══════════════════════════════════════════════ */
  .content-pad { padding: 0 8px; }

  /* ══════════════════════════════════════════════
     PRODUCT GRID — 2 cols mobile, 4 cols tablet+
     ══════════════════════════════════════════════ */
  .content-pad div[data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
  .content-pad div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
    min-width: 50% !important; flex: 0 0 50% !important; width: 50% !important;
    padding-left: 4px !important; padding-right: 4px !important;
  }

  /* ══════════════════════════════════════════════
     PRODUCT CARD
     ══════════════════════════════════════════════ */
  .product-card { background: #fff; overflow: hidden; margin-bottom: 10px; }
  .product-img-link { display: block; overflow: hidden; position: relative; }
  .product-img-link img {
    width: 100%; aspect-ratio: 3/4; object-fit: cover; display: block;
    transition: transform 0.5s ease;
  }
  .product-img-link:hover img { transform: scale(1.04); }
  .product-info-link { text-decoration: none; display: block; }

  /* Badges */
  .badge {
    position: absolute; top: 8px; left: 8px;
    background: #1A1A1A; color: #fff;
    padding: 2px 7px; font-size: .56em; font-weight: 700;
    letter-spacing: 0.6px; text-transform: uppercase;
  }
  .badge-new {
    position: absolute; top: 8px; left: 8px;
    background: #C9A84C; color: #fff;
    padding: 2px 7px; font-size: .56em; font-weight: 700; letter-spacing: 0.6px;
  }
  .badge-featured { display: none; }
  .badge-stock {
    position: absolute; bottom: 8px; left: 8px;
    background: rgba(255,255,255,0.92); color: #1A1A1A;
    padding: 2px 7px; font-size: .56em; font-weight: 600;
  }

  .product-info { padding: 8px 2px 4px; }
  .product-name {
    font-family: 'Inter', sans-serif; font-size: 0.70em; font-weight: 400;
    color: #1A1A1A; margin: 0 0 4px; line-height: 1.4;
  }
  .stars { display: none; }
  .price-wrap { display: flex; align-items: center; gap: 5px; margin-bottom: 7px; flex-wrap: wrap; }
  .price-now { font-size: 0.78em; font-weight: 600; color: #1A1A1A; }
  .price-was { font-size: .70em; color: #bbb; text-decoration: line-through; }
  .discount { font-size: .66em; color: #C9A84C; font-weight: 600; }

  /* Add-to-cart button on card */
  .card-btn-wrap { padding: 0 2px 10px; }
  .card-btn-wrap .stButton > button {
    background: #1A1A1A !important; color: #fff !important;
    border: none !important; border-radius: 1px !important;
    font-size: 0.62em !important; font-weight: 600 !important;
    padding: 9px 4px !important; letter-spacing: 0.8px !important;
    width: 100% !important; text-transform: uppercase !important;
    font-family: 'Inter', sans-serif !important;
    min-height: 0 !important; line-height: 1.2 !important;
    transition: background 0.2s !important;
  }
  .card-btn-wrap .stButton > button:hover { background: #333 !important; }

  /* ══════════════════════════════════════════════
     CART / DETAIL PAGE
     ══════════════════════════════════════════════ */
  .cart-page div[data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
  .cart-page div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
    min-width: 100% !important; flex: 0 0 100% !important; width: 100% !important;
  }
  .detail-page div[data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
  .detail-page div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
    min-width: 100% !important; flex: 0 0 100% !important; width: 100% !important;
  }
  .value-props-row div[data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
  .value-props-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
    min-width: 50% !important; flex: 0 0 50% !important; width: 50% !important;
    margin-bottom: 8px !important;
  }
  .cta-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(1),
  .cta-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(3) {
    display: none !important;
  }
  .cta-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) {
    min-width: 100% !important; flex: 0 0 100% !important; width: 100% !important;
  }

  /* Filter bar */
  .filter-bar-wrap {
    padding: 10px 8px; background: #F9F7F4;
    border-bottom: 1px solid #E8E4DE; margin-bottom: 14px;
  }
  .filter-bar-wrap div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
    min-width: 33% !important; flex: 0 0 33% !important; width: 33% !important;
    padding-left: 3px !important; padding-right: 3px !important;
  }
  .filter-bar-wrap .stSelectbox label {
    font-size: 0.64em !important; color: #999 !important;
    text-transform: uppercase !important; letter-spacing: 0.6px !important;
  }
  .filter-bar-wrap .stSelectbox > div > div {
    border: 1px solid #E0DDD8 !important; border-radius: 1px !important;
    background: #fff !important; font-size: 0.78em !important;
    min-height: 34px !important;
  }

  /* ══════════════════════════════════════════════
     SECTION HEADINGS
     ══════════════════════════════════════════════ */
  .section-title {
    font-family: 'Cormorant Garamond', serif; font-size: 1.45em; color: #1A1A1A;
    text-align: center; margin-bottom: 4px; padding: 0 8px;
    font-weight: 600; letter-spacing: 0.5px;
  }
  .section-sub {
    text-align: center; color: #aaa; margin-bottom: 16px; font-size: .70em;
    letter-spacing: 0.5px; text-transform: uppercase;
  }
  .divider { border: none; border-top: 1px solid #E8E4DE; margin: 24px auto; width: 40px; }

  /* ══════════════════════════════════════════════
     CATEGORY TILES
     ══════════════════════════════════════════════ */
  .cat-tiles-section { padding: 20px 10px 12px; background: #fff; }
  .cat-tiles-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 10px; }
  .cat-tile {
    background: #F9F7F4; padding: 14px 4px 10px; text-align: center;
    cursor: pointer; transition: background 0.2s;
    text-decoration: none; display: block;
  }
  .cat-tile:hover { background: #F0EDE8; }
  .cat-tile-emoji { font-size: 1.5em; display: block; margin-bottom: 5px; }
  .cat-tile-label {
    font-family: 'Inter', sans-serif; font-size: 0.60em;
    font-weight: 600; color: #1A1A1A; display: block;
    text-transform: uppercase; letter-spacing: 0.7px;
  }

  /* ══════════════════════════════════════════════
     TRUST SECTION
     ══════════════════════════════════════════════ */
  .trust-section { background: #F9F7F4; padding: 28px 10px 24px; margin: 16px 0 0; }
  .trust-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 14px; }
  .trust-card { background: #fff; padding: 16px 8px; text-align: center; }
  .trust-card-icon { font-size: 1.4em; margin-bottom: 8px; display: block; }
  .trust-card-title {
    font-family: 'Inter', sans-serif; font-size: 0.64em; font-weight: 700;
    color: #1A1A1A; margin-bottom: 4px; text-transform: uppercase;
    letter-spacing: 0.6px; display: block;
  }
  .trust-card-desc { font-size: 0.60em; color: #999; line-height: 1.5; }

  /* ══════════════════════════════════════════════
     BRAND STORY
     ══════════════════════════════════════════════ */
  .brand-story { background: #1A1A1A; color: #fff; padding: 44px 16px; text-align: center; }
  .brand-story h2 {
    font-family: 'Cormorant Garamond', serif; font-size: 1.35em; font-weight: 600;
    color: #C9A84C; margin-bottom: 14px; letter-spacing: 1.5px; text-transform: uppercase;
  }
  .brand-story p {
    font-size: 0.80em; line-height: 1.9; color: rgba(255,255,255,0.65);
    max-width: 460px; margin: 0 auto;
  }
  .brand-story-stats {
    display: flex; justify-content: center; gap: 32px; margin-top: 28px; flex-wrap: wrap;
  }
  .stat-item { text-align: center; }
  .stat-num {
    font-family: 'Cormorant Garamond', serif; font-size: 1.7em; font-weight: 600;
    color: #C9A84C; display: block;
  }
  .stat-label { font-size: 0.58em; color: rgba(255,255,255,0.45); letter-spacing: 1px; text-transform: uppercase; }

  /* ══════════════════════════════════════════════
     FOOTER
     ══════════════════════════════════════════════ */
  .footer-enhanced { background: #111; padding: 36px 16px 18px; }
  .footer-brand { text-align: center; margin-bottom: 28px; }
  .footer-brand h3 {
    font-family: 'Cormorant Garamond', serif; color: #C9A84C;
    font-size: 1.35em; font-weight: 600; margin-bottom: 6px; letter-spacing: 1.5px;
  }
  .footer-brand p { color: #666; font-size: 0.70em; }
  .footer-links-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px 16px; margin-bottom: 24px; }
  .footer-col h4 {
    color: #fff; font-size: 0.66em; font-weight: 700; margin-bottom: 10px;
    text-transform: uppercase; letter-spacing: 1.2px;
  }
  .footer-col a {
    display: block; color: #666; text-decoration: none;
    font-size: 0.68em; margin-bottom: 7px; transition: color 0.2s;
  }
  .footer-col a:hover { color: #C9A84C; }
  .footer-social { text-align: center; margin-bottom: 20px; }
  .footer-social h4 {
    color: #fff; font-size: 0.66em; font-weight: 700; margin-bottom: 12px;
    text-transform: uppercase; letter-spacing: 1.2px;
  }
  .social-icons { display: flex; justify-content: center; gap: 10px; }
  .social-icon {
    width: 34px; height: 34px; border-radius: 50%;
    background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.11);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.95em; text-decoration: none; color: #aaa; transition: all 0.2s;
  }
  .social-icon:hover { background: rgba(201,168,76,0.18); color: #C9A84C; }
  .footer-payment {
    text-align: center; margin-bottom: 16px; padding-top: 16px;
    border-top: 1px solid rgba(255,255,255,0.07);
  }
  .footer-payment p {
    color: #555; font-size: 0.62em; margin-bottom: 8px;
    letter-spacing: 0.6px; text-transform: uppercase;
  }
  .payment-icons { display: flex; justify-content: center; gap: 8px; flex-wrap: wrap; }
  .payment-icon {
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.09);
    padding: 4px 10px; font-size: 0.60em; color: #888; font-weight: 600; letter-spacing: 0.3px;
  }
  .footer-bottom {
    text-align: center; padding-top: 14px;
    border-top: 1px solid rgba(255,255,255,0.05); color: #444; font-size: 0.62em;
  }

  /* ══════════════════════════════════════════════
     CART DIALOG
     ══════════════════════════════════════════════ */
  .cart-dialog-item {
    background: #F9F7F4; padding: 12px 14px; margin-bottom: 8px;
    border-left: 3px solid #C9A84C;
  }

  /* ══════════════════════════════════════════════
     WISHLIST PAGE
     ══════════════════════════════════════════════ */
  .wishlist-page { padding: 20px 10px 32px; }
  .wishlist-empty {
    text-align: center; padding: 48px 20px;
  }
  .wishlist-empty-icon { font-size: 3em; margin-bottom: 16px; }
  .wishlist-empty h3 {
    font-family: 'Cormorant Garamond', serif; color: #1A1A1A;
    font-size: 1.5em; font-weight: 600; margin-bottom: 8px;
  }
  .wishlist-empty p { color: #999; font-size: 0.82em; }

  /* Wishlist product columns — same as content-pad grid */
  .wishlist-products div[data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
  .wishlist-products div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
    min-width: 50% !important; flex: 0 0 50% !important; width: 50% !important;
    padding-left: 4px !important; padding-right: 4px !important;
  }
  @media (min-width: 600px) {
    .wishlist-products div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
      min-width: 25% !important; flex: 0 0 25% !important; width: 25% !important;
    }
  }
  .wishlist-card-name { font-size: 0.76em; color: #1A1A1A; font-weight: 500; margin-bottom: 4px; }
  .wishlist-card-price { font-size: 0.76em; color: #C9A84C; font-weight: 700; }

  /* ══════════════════════════════════════════════
     GLOBAL BUTTON RESETS
     ══════════════════════════════════════════════ */
  div[data-testid="stMainBlockContainer"] .stButton > button[kind="primary"],
  div[data-testid="stMainBlockContainer"] [data-testid="stBaseButton-primary"] {
    background: #1A1A1A !important; color: #fff !important;
    border: none !important; border-radius: 1px !important;
    font-weight: 600 !important; letter-spacing: 0.5px !important;
  }
  .stTextInput > div > div > input {
    border: 1px solid #E8E4DE !important; border-radius: 1px !important;
    font-size: 0.84em !important;
  }

  /* ══════════════════════════════════════════════
     TABLET — min-width: 600px
     ══════════════════════════════════════════════ */
  @media (min-width: 600px) {
    .navbar-wrap { padding: 0 24px; height: 60px; }
    .navbar-brand { font-size: 1.4em; }
    .content-pad { padding: 0 14px; }
    .content-pad div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
      min-width: 25% !important; flex: 0 0 25% !important; width: 25% !important;
    }
    .cat-tiles-grid { grid-template-columns: repeat(6, 1fr); }
    .product-name { font-size: 0.74em; }
    .section-title { font-size: 1.75em; }
    .footer-links-grid { grid-template-columns: repeat(4, 1fr); }
    .trust-section { padding: 28px 14px 24px; }
    .cat-tiles-section { padding: 22px 14px 12px; }
    .filter-bar-wrap { padding: 10px 14px; }
    .navbar-cart-btn { right: 24px; }
    .navbar-wishlist-btn { right: 64px; }
    .wishlist-grid { grid-template-columns: repeat(3, 1fr); }
  }

  /* ══════════════════════════════════════════════
     LARGE TABLET — min-width: 768px
     ══════════════════════════════════════════════ */
  @media (min-width: 768px) {
    .navbar-brand { font-size: 1.52em; }
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
    .navbar-brand { font-size: 1.6em; }
    .content-pad { padding: 0 44px; }
    .content-pad div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
      min-width: unset !important; flex: 1 1 0 !important; width: auto !important;
    }
    .value-props-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
      min-width: unset !important; flex: 1 1 0 !important; width: auto !important;
    }
    .cart-page div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
      min-width: 0 !important; width: auto !important; flex: revert !important;
    }
    .detail-page div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
      min-width: 0 !important; width: auto !important; flex: revert !important;
    }
    .cta-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(1),
    .cta-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(3) {
      display: block !important; min-width: unset !important; flex: 1 1 0 !important;
    }
    .cta-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) {
      min-width: unset !important; flex: 1 1 0 !important; width: auto !important;
    }
    .product-name { font-size: 0.82em; }
    .section-title { font-size: 2.1em; }
    .cat-tiles-section { padding: 28px 44px 14px; }
    .trust-section { padding: 38px 44px 32px; }
    .brand-story { padding: 56px 44px; }
    .brand-story h2 { font-size: 1.75em; }
    .footer-enhanced { padding: 48px 44px 20px; }
    .navbar-cart-btn { right: 44px; top: 14px; }
    .navbar-wishlist-btn { right: 88px; top: 14px; }
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
    st.query_params.clear()
    _all_p = load_products()
    _match = next((p for p in _all_p if str(p["id"]) == str(_product_id)), None)
    if _match:
        st.session_state.selected_product = _match
        st.session_state.view = "detail"
    st.rerun()

_nav_redirect = st.query_params.get("nav_redirect", "")
if _nav_redirect:
    st.query_params.clear()
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
    elif _nav_redirect == "manage":
        st.switch_page("pages/1_Manage_Service.py")
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
              <h3 style='font-family:"Cormorant Garamond",serif;color:#1A1A1A;font-size:1.4em;font-weight:600;margin-bottom:6px'>Your cart is empty</h3>
              <p style='color:#999;font-size:0.82em;letter-spacing:0.3px'>Discover our premium earring collection</p>
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
              <div style="font-weight:600;color:#1A1A1A;font-size:0.88em;margin-bottom:3px">{item['name']}</div>
              <div style="color:#C9A84C;font-size:0.80em;font-weight:600">${item['price']:.2f}</div>
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
                f"<div style='text-align:right;font-weight:700;color:#1A1A1A;padding-top:7px;font-size:0.92em'>"
                f"${item['price'] * item['qty']:.2f}</div>",
                unsafe_allow_html=True,
            )
        with col_del:
            if st.button("✕", key=f"rm_{idx}", use_container_width=True):
                st.session_state.cart.pop(idx)
                st.rerun()

    st.markdown("<hr style='border-color:#E8E4DE;margin:16px 0 12px'>", unsafe_allow_html=True)

    subtotal = cart_total()
    shipping = 0.0 if subtotal >= 35 else 4.99
    total = subtotal + shipping

    st.markdown(
        f"""<div style="background:#F9F7F4;padding:16px;border-left:3px solid #C9A84C">
          <div style="display:flex;justify-content:space-between;margin-bottom:8px;font-size:0.85em">
            <span style="color:#777">Subtotal</span>
            <strong>${subtotal:.2f}</strong>
          </div>
          <div style="display:flex;justify-content:space-between;margin-bottom:6px;font-size:0.85em">
            <span style="color:#777">Shipping</span>
            <strong style="color:{'#C9A84C' if shipping == 0 else '#1A1A1A'}">{'FREE' if shipping == 0 else f'${shipping:.2f}'}</strong>
          </div>
          {'<p style="color:#C9A84C;font-size:0.74em;margin:4px 0 0">Add $' + f"{35 - subtotal:.2f}" + ' more for free shipping</p>' if shipping > 0 else ''}
          <hr style="border-color:#E8E4DE;margin:10px 0">
          <div style="display:flex;justify-content:space-between;font-size:1.05em">
            <strong>Total</strong>
            <strong style="color:#C9A84C">${total:.2f}</strong>
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
body {{ font-family: 'Inter', sans-serif; overflow: hidden; background: #1A1A1A; }}

.carousel-container {{
  position: relative; width: 100%; height: 260px;
  overflow: hidden; background: #1A1A1A;
}}
.slide {{
  position: absolute; inset: 0; opacity: 0;
  transition: opacity 0.8s ease-in-out; cursor: pointer;
}}
.slide.active {{ opacity: 1; }}
.slide-bg {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
.slide-overlay {{
  position: absolute; inset: 0;
  background: linear-gradient(0deg, rgba(0,0,0,0.80) 0%, rgba(0,0,0,0.40) 55%, transparent 100%);
  display: flex; align-items: flex-end; padding: 0 18px 28px;
}}
.slide-content {{ max-width: 100%; color: white; text-align: center; width: 100%; }}
.slide-content h2 {{
  font-size: 0.68em; font-weight: 400; opacity: 0.75;
  margin-bottom: 5px; letter-spacing: 1px; text-transform: uppercase;
  font-family: 'Inter', sans-serif;
}}
.slide-content h1 {{
  font-size: 1.55em; font-weight: 600; line-height: 1.15;
  margin-bottom: 14px; color: #fff;
  font-family: 'Cormorant Garamond', Georgia, serif; letter-spacing: 0.5px;
}}
.shop-btn {{
  background: #fff; color: #1A1A1A; border: none;
  padding: 9px 26px; font-size: 0.72em;
  font-weight: 700; cursor: pointer; letter-spacing: 1px;
  transition: all 0.2s; font-family: 'Inter', sans-serif;
  text-transform: uppercase;
}}
.shop-btn:hover {{ background: #C9A84C; color: #fff; }}
.nav-btn {{
  position: absolute; top: 50%; transform: translateY(-50%);
  background: rgba(255,255,255,0.12); backdrop-filter: blur(4px);
  border: 1px solid rgba(255,255,255,0.25); color: white;
  font-size: 1.2em; width: 32px; height: 32px;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  z-index: 10; transition: background 0.2s; line-height: 1;
}}
.nav-btn:hover {{ background: rgba(255,255,255,0.25); }}
.nav-btn.prev {{ left: 10px; }}
.nav-btn.next {{ right: 10px; }}

@media (min-width: 380px) {{
  .carousel-container {{ height: 290px; }}
  .slide-content h1 {{ font-size: 1.75em; }}
}}
@media (min-width: 480px) {{
  .carousel-container {{ height: 340px; }}
  .slide-content h1 {{ font-size: 2.0em; }}
  .shop-btn {{ padding: 10px 30px; }}
}}
@media (min-width: 768px) {{
  .carousel-container {{ height: 420px; }}
  .slide-overlay {{
    background: linear-gradient(90deg, rgba(0,0,0,0.75) 0%, rgba(0,0,0,0.45) 50%, transparent 80%);
    align-items: center; padding: 0 48px;
  }}
  .slide-content {{ max-width: 55%; text-align: left; width: auto; }}
  .slide-content h1 {{ font-size: 2.4em; margin-bottom: 16px; }}
  .slide-content h2 {{ font-size: 0.88em; }}
  .shop-btn {{ padding: 11px 32px; font-size: 0.76em; }}
  .nav-btn {{ width: 42px; height: 42px; font-size: 1.5em; }}
}}
@media (min-width: 960px) {{
  .carousel-container {{ height: 500px; }}
  .slide-overlay {{ padding: 0 68px; }}
  .slide-content {{ max-width: 48%; }}
  .slide-content h1 {{ font-size: 2.9em; margin-bottom: 20px; }}
  .slide-content h2 {{ font-size: 0.96em; }}
  .shop-btn {{ padding: 13px 38px; font-size: 0.80em; }}
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
  background: rgba(255,255,255,0.35); border: none; cursor: pointer;
  transition: all 0.3s; padding: 0;
}}
.dot.active {{ background: white; width: 22px; border-radius: 3px; }}
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
  window.parent.postMessage({{type: 'streamlit:setFrameHeight', height: h + 10}}, '*');
}}
reportHeight();
window.addEventListener('resize', reportHeight);
</script>
</body>
</html>
"""
    components.html(html, height=520, scrolling=False)


# ── Category nav bar renderer ─────────────────────────────────────────────────
def render_category_nav():
    cats = load_nav_categories()
    active = sorted(
        [c for c in cats if c.get("enabled", True)],
        key=lambda x: x.get("sequence", 999),
    )
    if not active:
        return

    st.markdown('<div class="cat-nav-container">', unsafe_allow_html=True)
    cols = st.columns(len(active))
    for i, c in enumerate(active):
        emoji = c.get("emoji", "")
        label = c["label"]
        redirect = c.get("redirect_to", "shop")

        with cols[i]:
            if st.button(f"{emoji} {label}" if emoji else label, key=f"navcat_{c['id']}", use_container_width=True):
                if redirect == "shop":
                    st.session_state.view = "shop"
                    st.session_state.filter_cat = "All"
                elif redirect.startswith("category:"):
                    st.session_state.view = "shop"
                    st.session_state.filter_cat = redirect[len("category:"):]
                elif redirect == "home":
                    st.session_state.view = "home"
                st.session_state.selected_product = None
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


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
    cart_icon = f"🛒 {cart_n}" if cart_n > 0 else "🛒"
    wl_icon = f"♡ {wl_n}" if wl_n > 0 else "♡"

    st.markdown(
        f"""
<div class="navbar-wrap" id="main-navbar">
  <div class="navbar-left">
    <button class="hamburger-btn" onclick="openNavMenu()" aria-label="Open menu">
      <span></span>
      <span></span>
      <span></span>
    </button>
  </div>
  <a href="?nav_redirect=home" class="navbar-brand">💎 Love Earrings</a>
  <div class="navbar-right" style="width:72px"></div>
</div>

<!-- Backdrop -->
<div class="nav-overlay-bg" id="navBg" onclick="closeNavMenu()"></div>

<!-- Slide-in menu -->
<div class="nav-overlay" id="navOverlay">
  <div class="nav-overlay-header">
    <span class="nav-overlay-brand">💎 Love Earrings</span>
    <button class="nav-close-btn" onclick="closeNavMenu()">✕</button>
  </div>
  <div class="nav-overlay-links">
    <a href="?nav_redirect=home" onclick="closeNavMenu()">Home</a>
    <a href="?nav_redirect=shop" onclick="closeNavMenu()">Shop All</a>
    <a href="?nav_redirect=wishlist" onclick="closeNavMenu()">Wishlist</a>
    <a href="?nav_redirect=manage" onclick="closeNavMenu()">Manage</a>
  </div>
  <div class="nav-overlay-section">
    <h4>Shop by Category</h4>
    <a href="?nav_redirect=category:Studs" onclick="closeNavMenu()">Studs</a>
    <a href="?nav_redirect=category:Hoops" onclick="closeNavMenu()">Hoops</a>
    <a href="?nav_redirect=category:Drops" onclick="closeNavMenu()">Drops</a>
    <a href="?nav_redirect=category:Chandeliers" onclick="closeNavMenu()">Chandeliers</a>
    <a href="?nav_redirect=category:Dangles" onclick="closeNavMenu()">Dangles</a>
  </div>
</div>

<script>
function openNavMenu() {{
  document.getElementById('navOverlay').classList.add('open');
  document.getElementById('navBg').classList.add('open');
  document.body.style.overflow = 'hidden';
}}
function closeNavMenu() {{
  document.getElementById('navOverlay').classList.remove('open');
  document.getElementById('navBg').classList.remove('open');
  document.body.style.overflow = '';
}}
document.addEventListener('keydown', function(e) {{
  if (e.key === 'Escape') closeNavMenu();
}});
</script>
""",
        unsafe_allow_html=True,
    )

    # Cart button — fixed top-right
    st.markdown('<div class="navbar-cart-btn">', unsafe_allow_html=True)
    if st.button(cart_icon, key="nav_cart", use_container_width=False):
        cart_popup()
    st.markdown('</div>', unsafe_allow_html=True)

    # Wishlist button — fixed top-right (next to cart)
    st.markdown('<div class="navbar-wishlist-btn">', unsafe_allow_html=True)
    if st.button(wl_icon, key="nav_wishlist_btn", use_container_width=False):
        st.session_state.view = "wishlist"
        st.session_state.selected_product = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ── Section renderers ─────────────────────────────────────────────────────────
def render_category_tiles():
    tiles = [
        ("💛", "Studs", "category:Studs"),
        ("⭕", "Hoops", "category:Hoops"),
        ("🌊", "Drops", "category:Drops"),
        ("✨", "Chandeliers", "category:Chandeliers"),
        ("🌀", "Dangles", "category:Dangles"),
        ("🎁", "Gifting", "shop"),
    ]
    tiles_html = "".join(
        f'<a href="?nav_redirect={redirect}" class="cat-tile">'
        f'<span class="cat-tile-emoji">{emoji}</span>'
        f'<span class="cat-tile-label">{label}</span>'
        f'</a>'
        for emoji, label, redirect in tiles
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
              <a href="?nav_redirect=shop">All Earrings</a>
              <a href="?nav_redirect=category:Studs">Studs</a>
              <a href="?nav_redirect=category:Hoops">Hoops</a>
              <a href="?nav_redirect=category:Drops">Drops</a>
              <a href="?nav_redirect=category:Chandeliers">Chandeliers</a>
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
  <a href="{product_url}" class="product-img-link">
    <img src="{p['image']}" alt="{p['name']}">
    {left_badge}
    {stock_badge}
  </a>
  <a href="{product_url}" class="product-info-link">
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
        cols = st.columns(4)
        for i, p in enumerate(wishlist_products):
            with cols[i % 4]:
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
                      <a href="{product_url}" class="product-img-link">
                        <img src="{p['image']}" alt="{p['name']}">
                        {left_badge}
                      </a>
                      <a href="{product_url}" class="product-info-link">
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
render_category_nav()
st.markdown("<div style='margin-bottom:4px'></div>", unsafe_allow_html=True)


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
        cols = st.columns(4)
        for i, p in enumerate(featured):
            render_product_card(p, cols[i % 4])

    # More Earrings section
    non_featured = [p for p in all_products if not p.get("featured")]
    if non_featured:
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown('<h2 class="section-title">All Earrings</h2>', unsafe_allow_html=True)
        st.markdown('<p class="section-sub">Explore our full collection</p>', unsafe_allow_html=True)
        cols2 = st.columns(4)
        for i, p in enumerate(non_featured):
            render_product_card(p, cols2[i % 4])

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
                f"""<div style="text-align:center;padding:20px 12px;background:#F9F7F4">
                <div style="font-size:1.8em;margin-bottom:8px">{icon}</div>
                <div style="font-family:'Cormorant Garamond',serif;font-weight:600;color:#1A1A1A;font-size:0.92em;margin-bottom:4px;letter-spacing:0.3px">{title}</div>
                <div style="color:#aaa;font-size:0.76em">{desc}</div>
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
        search = st.text_input("Search", placeholder="Search earrings...", key="shop_search", label_visibility="collapsed")
        st.markdown('<div style="font-size:0.64em;color:#aaa;text-transform:uppercase;letter-spacing:0.6px;margin-top:2px">Search</div>', unsafe_allow_html=True)
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
        cols = st.columns(4)
        for i, p in enumerate(products):
            render_product_card(p, cols[i % 4])

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
            f'<div style="background:#FFF8EE;border-left:3px solid #C9A84C;'
            f'padding:8px 12px;margin-bottom:14px;font-size:0.80em;color:#8B6914;">'
            f'Only {stock} pieces left — order soon!</div>'
            if 0 < stock < 10 else ""
        )

        wishlisted = p["id"] in st.session_state.wishlist

        st.markdown(
            f"""
<h1 style="font-family:'Cormorant Garamond',serif;color:#1A1A1A;font-size:1.85em;font-weight:600;margin-bottom:6px;line-height:1.2">{p['name']}</h1>
<div style="color:#C9A84C;font-size:1em;margin-bottom:12px">{stars}
  <span style="color:#bbb;font-size:0.80em;margin-left:4px">({p.get('reviews',0)} reviews)</span>
</div>
<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px">
  <span style="font-size:1.85em;font-weight:700;color:#1A1A1A;font-family:'Cormorant Garamond',serif">${p['price']:.2f}</span>
  {'<span style="text-decoration:line-through;color:#bbb;font-size:1.1em">$' + f"{p['original_price']:.2f}" + '</span>' if p.get('original_price') else ''}
  {'<span style="background:#C9A84C;color:#fff;padding:2px 10px;font-size:0.76em;font-weight:700;letter-spacing:0.5px">' + str(discount) + '% OFF</span>' if discount else ''}
</div>
{stock_warning}
<p style="color:#555;line-height:1.75;font-size:0.88em;margin-bottom:16px">{p.get('description','')}</p>
<div style="display:flex;gap:7px;flex-wrap:wrap;margin-bottom:16px">
  {''.join(f'<span style="background:#F9F7F4;color:#1A1A1A;border:1px solid #E8E4DE;padding:4px 14px;font-size:0.78em;font-weight:500;letter-spacing:0.3px">{c}</span>' for c in p.get('colors',[]))}
</div>
<div style="background:#F9F7F4;padding:10px 14px;margin-bottom:20px;font-size:0.82em;color:#666">
  Category: <strong style="color:#1A1A1A">{p.get('category','')}</strong> &nbsp;·&nbsp;
  Stock: <strong style="color:{'#C9A84C' if stock > 0 else '#e53935'}">{'In Stock' if stock > 0 else 'Out of Stock'}</strong>
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
        '<h3 style="font-family:\'Cormorant Garamond\',serif;color:#1A1A1A;font-size:1.35em;font-weight:600;margin-bottom:4px">You Might Also Like</h3>',
        unsafe_allow_html=True,
    )
    all_products_rel = load_products()
    related = [
        x for x in all_products_rel
        if x["category"] == p["category"] and x["id"] != p["id"]
    ][:4]
    if related:
        cols = st.columns(4)
        for i, rp in enumerate(related):
            render_product_card(rp, cols[i % 4])

    st.markdown('</div>', unsafe_allow_html=True)
    render_footer()


# ═════════════════════════════════════════════════════════════════════════════
# VIEW: CART (full checkout page)
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.view == "cart":
    st.markdown('<div class="content-pad cart-page">', unsafe_allow_html=True)
    st.markdown(
        '<h2 style="font-family:\'Cormorant Garamond\',serif;color:#1A1A1A;font-size:1.75em;font-weight:600;margin:20px 0 4px;text-align:center">Your Cart</h2>',
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
              <h3 style="font-family:'Cormorant Garamond',serif;color:#1A1A1A;font-size:1.5em;font-weight:600;margin-bottom:8px">Your cart is empty</h3>
              <p style="color:#999;font-size:0.84em">Add some beautiful earrings to get started.</p>
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
                '<p style="font-size:0.74em;color:#aaa;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:12px">Order Items</p>',
                unsafe_allow_html=True,
            )
            for idx, item in enumerate(st.session_state.cart):
                st.markdown(
                    f"""<div style="display:flex;gap:14px;padding:14px;background:#F9F7F4;margin-bottom:8px;border-left:3px solid #C9A84C">
                      <div style="flex:1">
                        <div style="font-weight:600;font-size:0.88em;color:#1A1A1A;margin-bottom:3px">{item['name']}</div>
                        <div style="font-size:0.76em;color:#aaa">{item.get('category','')}</div>
                        <div style="font-size:0.84em;font-weight:700;color:#C9A84C;margin-top:4px">${item['price']:.2f} each</div>
                      </div>
                    </div>""",
                    unsafe_allow_html=True,
                )
                qc1, qc2, qc3, qc4 = st.columns([1, 2, 2, 1])
                with qc1:
                    new_qty = st.number_input("Qty", min_value=1, max_value=10, value=item["qty"], key=f"qty_{idx}", label_visibility="collapsed")
                    st.session_state.cart[idx]["qty"] = new_qty
                with qc2:
                    st.markdown(f"<div style='padding-top:6px;font-weight:700;font-size:0.9em'>${item['price'] * new_qty:.2f}</div>", unsafe_allow_html=True)
                with qc4:
                    if st.button("✕", key=f"del_{idx}", use_container_width=True):
                        st.session_state.cart.pop(idx)
                        st.rerun()

        with summary_col:
            subtotal = cart_total()
            shipping = 0 if subtotal >= 35 else 4.99
            total = subtotal + shipping

            st.markdown(
                f"""<div style="background:#F9F7F4;padding:24px;border-top:3px solid #C9A84C">
                  <p style="font-family:'Cormorant Garamond',serif;font-size:1.2em;font-weight:600;color:#1A1A1A;margin-bottom:18px">Order Summary</p>
                  <div style="display:flex;justify-content:space-between;margin-bottom:10px;font-size:0.86em">
                    <span style="color:#777">Subtotal</span><strong>${subtotal:.2f}</strong>
                  </div>
                  <div style="display:flex;justify-content:space-between;margin-bottom:8px;font-size:0.86em">
                    <span style="color:#777">Shipping</span>
                    <strong style="color:{'#C9A84C' if shipping == 0 else '#1A1A1A'}">{'FREE' if shipping == 0 else f'${shipping:.2f}'}</strong>
                  </div>
                  {'<p style="color:#C9A84C;font-size:0.76em;margin-bottom:10px">Add $' + f"{35 - subtotal:.2f}" + ' more for free shipping</p>' if shipping > 0 else ''}
                  <hr style="border-color:#E8E4DE;margin:12px 0">
                  <div style="display:flex;justify-content:space-between;font-size:1.1em">
                    <strong>Total</strong><strong style="color:#C9A84C">${total:.2f}</strong>
                  </div>
                </div>""",
                unsafe_allow_html=True,
            )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<p style="font-size:0.74em;color:#aaa;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:10px">Shipping Details</p>',
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
