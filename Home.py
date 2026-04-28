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
    """Return a URL-safe path for use in HTML img src."""
    if img_path and img_path.startswith("app/static/"):
        return "/" + img_path
    return img_path


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Love Earrings",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Viewport meta (critical for mobile scaling) ───────────────────────────────
st.markdown(
    '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">',
    unsafe_allow_html=True,
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Lato:wght@300;400;600&display=swap');

  html, body, [class*="css"] { font-family: 'Lato', sans-serif; }

  /* ── Full screen layout ── */
  .block-container {
    padding-top: 0 !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
    padding-bottom: 2rem !important;
    max-width: 100% !important;
  }
  section[data-testid="stMain"] > div { padding-left: 0 !important; padding-right: 0 !important; }
  header[data-testid="stHeader"] { display: none !important; }

  /* ── Sidebar expand button always visible ── */
  [data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    background: #1e0a3c !important;
    color: #f5c6d0 !important;
    border-radius: 0 8px 8px 0 !important;
  }
  [data-testid="collapsedControl"] svg { fill: #f5c6d0 !important; }

  /* ── Top Navbar ── */
  .navbar-wrap {
    background: linear-gradient(135deg, #1e0a3c 0%, #0f0520 100%);
    padding: 12px 28px;
    border-radius: 0;
    margin-bottom: 0;
    display: flex;
    align-items: center;
  }
  .navbar-brand {
    font-family: 'Playfair Display', serif;
    color: #f5c6d0;
    font-size: 1.55em;
    font-weight: 700;
    letter-spacing: 1px;
    white-space: nowrap;
  }

  /* ── Product card ── */
  .product-card {
    background: #fff; border-radius: 16px; overflow: hidden;
    box-shadow: 0 2px 16px rgba(0,0,0,.07);
    transition: transform .25s, box-shadow .25s;
    margin-bottom: 4px; border: 1px solid #f0e8ed;
    cursor: pointer;
  }
  .product-card:hover { transform: translateY(-5px); box-shadow: 0 12px 36px rgba(0,0,0,.13); }

  .product-img-wrap { position: relative; overflow: hidden; }
  .product-img-wrap img { width: 100%; height: 220px; object-fit: cover; transition: transform .4s; }
  .product-card:hover .product-img-wrap img { transform: scale(1.06); }

  .badge {
    position: absolute; top: 10px; left: 10px;
    background: #e91e8c; color: #fff;
    padding: 3px 10px; border-radius: 20px; font-size: .75em; font-weight: 700;
  }
  .badge-featured {
    position: absolute; top: 10px; right: 10px;
    background: #3d0c78; color: #f5c6d0;
    padding: 3px 10px; border-radius: 20px; font-size: .72em; font-weight: 600;
  }

  .product-info { padding: 14px 16px 18px; }
  .product-name {
    font-family: 'Playfair Display', serif;
    font-size: 1.02em; font-weight: 600; color: #1e0a3c;
    margin: 0 0 6px; line-height: 1.35;
  }
  .stars { color: #f4a423; font-size: .85em; margin-bottom: 6px; }
  .price-wrap { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
  .price-now { font-size: 1.15em; font-weight: 700; color: #c2185b; }
  .price-was { font-size: .88em; color: #aaa; text-decoration: line-through; }
  .discount { font-size: .8em; color: #e91e8c; font-weight: 600; }

  /* ── Section headers ── */
  .section-title {
    font-family: 'Playfair Display', serif;
    font-size: 2em; color: #1e0a3c; text-align: center; margin-bottom: 6px;
    padding: 0 1rem;
  }
  .section-sub {
    text-align: center; color: #888; margin-bottom: 30px;
    font-size: .95em; letter-spacing: .5px;
  }
  .divider { border: none; border-top: 2px solid #f5c6d0; margin: 30px auto; width: 80px; }

  /* ── Footer ── */
  .footer {
    background: #1e0a3c; color: #d4a5b5;
    text-align: center; padding: 32px 20px; margin-top: 50px; border-radius: 0;
  }
  .footer h3 { font-family: 'Playfair Display', serif; color: #f5c6d0; margin-bottom: 8px; }
  .footer a { color: #f5c6d0; text-decoration: none; margin: 0 12px; }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] { background: #fdf6f9 !important; }
  [data-testid="stSidebar"] h2 { font-family: 'Playfair Display', serif; color: #c2185b; }

  /* ── Category nav native buttons ── */
  .cat-nav-container {
    border-bottom: 1.5px solid #f0e8ed;
    background: white;
    padding: 2px 0;
    margin-bottom: 4px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  .cat-nav-container div[data-testid="stHorizontalBlock"] { gap: 0 !important; flex-wrap: nowrap; overflow-x: auto; -webkit-overflow-scrolling: touch; }
  .cat-nav-container .stButton > button {
    background: none !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    color: #1e0a3c !important;
    font-weight: 600 !important;
    font-size: 0.83em !important;
    padding: 8px 10px !important;
    white-space: nowrap !important;
    box-shadow: none !important;
    letter-spacing: 0.3px !important;
  }
  .cat-nav-container .stButton > button:hover {
    color: #e91e8c !important;
    border-bottom: 2px solid #e91e8c !important;
    background: none !important;
  }

  /* ── Content padding wrapper ── */
  .content-pad { padding: 0 1.5rem; }

  /* ── Cart dialog ── */
  .cart-dialog-item {
    background: #fdf6f9; border-radius: 10px;
    padding: 12px 14px; margin-bottom: 10px; border: 1px solid #f0e4ec;
  }

  /* ─────────────────────────────────────────────────────────
     MOBILE RESPONSIVE STYLES
     ───────────────────────────────────────────────────────── */

  /* Tablet: ≤ 900px */
  @media (max-width: 900px) {
    .navbar-brand { font-size: 1.3em; }
    .navbar-wrap { padding: 10px 16px; }
    .section-title { font-size: 1.6em; }
    .content-pad { padding: 0 1rem; }
    .product-img-wrap img { height: 190px; }
  }

  /* Mobile: ≤ 640px */
  @media (max-width: 640px) {

    /* Navbar compact */
    .navbar-wrap { padding: 8px 12px; }
    .navbar-brand { font-size: 1.1em; letter-spacing: 0.5px; }

    /* Nav button bar: compact, scrollable */
    .nav-btn-bar {
      overflow-x: auto !important;
      -webkit-overflow-scrolling: touch !important;
      padding: 2px 8px !important;
    }
    .nav-btn-bar div[data-testid="stHorizontalBlock"] {
      flex-wrap: nowrap !important;
      gap: 2px !important;
      overflow-x: auto !important;
    }
    .nav-btn-bar .stButton > button {
      font-size: 0.78em !important;
      padding: 6px 8px !important;
      white-space: nowrap !important;
    }

    /* Category nav: smaller text, touch-scroll */
    .cat-nav-container .stButton > button {
      font-size: 0.74em !important;
      padding: 6px 8px !important;
    }

    /* Product grid: 2 columns on mobile */
    .content-pad div[data-testid="stHorizontalBlock"] {
      flex-wrap: wrap !important;
    }
    .content-pad div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
      min-width: 48% !important;
      flex: 0 0 48% !important;
      width: 48% !important;
    }

    /* Product card adjustments */
    .product-img-wrap img { height: 150px; }
    .product-info { padding: 10px 10px 12px; }
    .product-name { font-size: 0.88em; }
    .price-now { font-size: 1em; }
    .price-was { font-size: .78em; }
    .discount { font-size: .72em; }
    .stars { font-size: .75em; }
    .badge { font-size: .65em; padding: 2px 7px; top: 6px; left: 6px; }
    .badge-featured { font-size: .62em; padding: 2px 7px; top: 6px; right: 6px; }

    /* Smaller Add to Cart / View Details buttons inside cards */
    .content-pad .stButton > button {
      font-size: 0.75em !important;
      padding: 6px 4px !important;
    }

    /* Section titles */
    .section-title { font-size: 1.35em; padding: 0 0.5rem; }
    .section-sub { font-size: .85em; margin-bottom: 18px; }

    /* Content padding */
    .content-pad { padding: 0 0.5rem; }

    /* Value props: 2×2 grid */
    .value-props-row div[data-testid="stHorizontalBlock"] {
      flex-wrap: wrap !important;
    }
    .value-props-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
      min-width: 48% !important;
      flex: 0 0 48% !important;
      width: 48% !important;
      margin-bottom: 8px !important;
    }

    /* Footer */
    .footer { padding: 24px 12px; margin-top: 30px; }
    .footer a { margin: 0 6px; font-size: .85em; }

    /* Cart page: stack columns */
    .cart-page div[data-testid="stHorizontalBlock"] {
      flex-wrap: wrap !important;
    }
    .cart-page div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
      min-width: 100% !important;
      flex: 0 0 100% !important;
      width: 100% !important;
    }

    /* Detail page: stack image + info */
    .detail-page div[data-testid="stHorizontalBlock"] {
      flex-wrap: wrap !important;
    }
    .detail-page div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
      min-width: 100% !important;
      flex: 0 0 100% !important;
      width: 100% !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] { min-width: 260px !important; max-width: 80vw !important; }
  }

  /* Small phones: ≤ 400px */
  @media (max-width: 400px) {
    .navbar-brand { font-size: 0.95em; }
    .product-img-wrap img { height: 130px; }
    .product-name { font-size: 0.80em; }
    .section-title { font-size: 1.15em; }
    .content-pad { padding: 0 0.3rem; }
  }
</style>
""",
    unsafe_allow_html=True,
)

# ── Session state ─────────────────────────────────────────────────────────────
if "cart" not in st.session_state:
    st.session_state.cart = []
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

# ── Query-param redirect handler (hero banners + nav categories) ───────────────
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
@st.dialog("🛒 Your Cart")
def cart_popup():
    if not st.session_state.cart:
        st.markdown(
            "<div style='text-align:center;padding:20px 0'>"
            "<div style='font-size:3em'>🛒</div>"
            "<h3 style='color:#1e0a3c'>Your cart is empty</h3>"
            "<p style='color:#888'>Add some earrings to get started!</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        if st.button("🛍️ Continue Shopping", use_container_width=True, type="primary"):
            st.rerun()
        return

    for idx, item in enumerate(st.session_state.cart):
        st.markdown(
            f"""<div class="cart-dialog-item">
              <div style="font-weight:600;color:#1e0a3c;margin-bottom:4px">{item['name']}</div>
              <div style="color:#c2185b;font-size:.9em">${item['price']:.2f} each</div>
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
                f"<div style='text-align:center;font-weight:700;font-size:1.1em;padding-top:6px'>"
                f"{item['qty']}</div>",
                unsafe_allow_html=True,
            )
        with col_plus:
            if st.button("+", key=f"plus_{idx}", use_container_width=True):
                st.session_state.cart[idx]["qty"] += 1
                st.rerun()
        with col_sub:
            st.markdown(
                f"<div style='text-align:right;font-weight:600;color:#c2185b;padding-top:6px'>"
                f"${item['price'] * item['qty']:.2f}</div>",
                unsafe_allow_html=True,
            )
        with col_del:
            if st.button("🗑️", key=f"rm_{idx}", use_container_width=True):
                st.session_state.cart.pop(idx)
                st.rerun()

    st.markdown("<hr style='border-color:#f5c6d0;margin:16px 0 12px'>", unsafe_allow_html=True)

    subtotal = cart_total()
    shipping = 0.0 if subtotal >= 35 else 4.99
    total = subtotal + shipping

    st.markdown(
        f"""<div style="background:#fff;border-radius:12px;padding:16px;border:1px solid #f5c6d0">
          <div style="display:flex;justify-content:space-between;margin-bottom:8px">
            <span style="color:#555">Subtotal</span>
            <strong>${subtotal:.2f}</strong>
          </div>
          <div style="display:flex;justify-content:space-between;margin-bottom:4px">
            <span style="color:#555">Shipping</span>
            <strong>{'FREE 🎉' if shipping == 0 else f'${shipping:.2f}'}</strong>
          </div>
          {'<p style="color:#e91e8c;font-size:.82em;margin:4px 0 0">Add $' + f"{35 - subtotal:.2f}" + ' more for free shipping!</p>' if shipping > 0 else ''}
          <hr style="border-color:#f5c6d0;margin:10px 0">
          <div style="display:flex;justify-content:space-between;font-size:1.15em">
            <strong>Total</strong>
            <strong style="color:#c2185b">${total:.2f}</strong>
          </div>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✅ Proceed to Checkout", use_container_width=True, type="primary"):
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
body {{ font-family: 'Lato', sans-serif; overflow: hidden; background: #1e0a3c; }}

.carousel-container {{
  position: relative;
  width: 100%;
  height: 470px;
  border-radius: 0;
  overflow: hidden;
  background: #1e0a3c;
}}

@media (max-width: 640px) {{
  .carousel-container {{ height: 300px; }}
  .slide-overlay {{ padding: 0 20px; background: linear-gradient(0deg, rgba(30,10,60,0.92) 0%, rgba(30,10,60,0.5) 60%, transparent 100%); align-items: flex-end; padding-bottom: 36px; }}
  .slide-content {{ max-width: 100%; text-align: center; }}
  .slide-content h1 {{ font-size: 1.7em; margin-bottom: 12px; }}
  .slide-content h2 {{ font-size: 0.82em; }}
  .shop-btn {{ padding: 10px 28px; font-size: 0.82em; }}
  .nav-btn {{ width: 36px; height: 36px; font-size: 1.3em; }}
}}

@media (max-width: 400px) {{
  .carousel-container {{ height: 240px; }}
  .slide-content h1 {{ font-size: 1.35em; }}
}}

.slide {{
  position: absolute;
  inset: 0;
  opacity: 0;
  transition: opacity 0.7s ease-in-out;
  cursor: pointer;
}}
.slide.active {{ opacity: 1; }}

.slide-bg {{
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}}

.slide-overlay {{
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, rgba(30,10,60,0.88) 0%, rgba(30,10,60,0.55) 50%, transparent 80%);
  display: flex;
  align-items: center;
  padding: 0 64px;
}}

.slide-content {{
  max-width: 52%;
  color: white;
}}

.slide-content h2 {{
  font-size: 1.05em;
  font-weight: 400;
  opacity: 0.85;
  margin-bottom: 6px;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  font-family: 'Lato', sans-serif;
}}

.slide-content h1 {{
  font-size: 2.8em;
  font-weight: 700;
  line-height: 1.1;
  margin-bottom: 18px;
  color: #f5c6d0;
  font-family: Georgia, serif;
  letter-spacing: 1px;
}}

.shop-btn {{
  background: white;
  color: #1e0a3c;
  border: none;
  padding: 13px 38px;
  border-radius: 40px;
  font-size: 0.92em;
  font-weight: 700;
  cursor: pointer;
  letter-spacing: 0.5px;
  transition: all 0.2s;
  font-family: 'Lato', sans-serif;
}}
.shop-btn:hover {{
  background: #f5c6d0;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.2);
}}

.nav-btn {{
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255,255,255,0.3);
  color: white;
  font-size: 1.8em;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  transition: background 0.2s;
  line-height: 1;
}}
.nav-btn:hover {{ background: rgba(255,255,255,0.3); }}
.nav-btn.prev {{ left: 16px; }}
.nav-btn.next {{ right: 16px; }}

.dots {{
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
  z-index: 10;
}}

.dot {{
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255,255,255,0.4);
  border: none;
  cursor: pointer;
  transition: all 0.3s;
  padding: 0;
}}
.dot.active {{
  background: white;
  width: 26px;
  border-radius: 4px;
}}
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
  e.stopPropagation();
  goTo(current - 1);
  resetTimer();
}});

document.getElementById('nextBtn').addEventListener('click', (e) => {{
  e.stopPropagation();
  goTo(current + 1);
  resetTimer();
}});

document.querySelectorAll('.dot').forEach((dot, i) => {{
  dot.addEventListener('click', (e) => {{
    e.stopPropagation();
    goTo(i);
    resetTimer();
  }});
}});

function handleClick(e, idx) {{
  e.stopPropagation();
  navigateTo(redirects[idx]);
}}

function dotClick(e, idx) {{
  e.stopPropagation();
  goTo(idx);
  resetTimer();
}}

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
</script>
</body>
</html>
"""
    components.html(html, height=490, scrolling=False)


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
        badge = c.get("badge", "")
        display = f"{emoji} {label}" + (f" [{badge}]" if badge else "")
        redirect = c.get("redirect_to", "shop")

        with cols[i]:
            if st.button(display, key=f"navcat_{c['id']}", use_container_width=True):
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


# ── Top Navigation Bar ────────────────────────────────────────────────────────
st.markdown(
    '<div class="navbar-wrap"><span class="navbar-brand">💎 Love Earrings</span></div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="nav-btn-bar" style="padding: 4px 1rem 0;">', unsafe_allow_html=True)
nb1, nb2, nb3, nb4, nb_space, nb_cart = st.columns([1.2, 1, 1, 1.2, 4, 1.8])

with nb1:
    if st.button("🏠 Home", use_container_width=True, key="nav_home"):
        st.session_state.view = "home"
        st.session_state.selected_product = None
        st.session_state.filter_cat = "All"
        st.rerun()
with nb2:
    if st.button("🛍️ Shop", use_container_width=True, key="nav_shop"):
        st.session_state.view = "shop"
        st.session_state.selected_product = None
        st.session_state.filter_cat = "All"
        st.rerun()
with nb3:
    if st.button("⚙️ Manage", use_container_width=True, key="nav_manage"):
        st.switch_page("pages/1_Manage_Service.py")
with nb_cart:
    cart_n = cart_count()
    cart_label = f"🛒 Cart  {'·  ' + str(cart_n) if cart_n > 0 else ''}"
    if st.button(cart_label, use_container_width=True, key="nav_cart",
                 type="primary" if cart_n > 0 else "secondary"):
        cart_popup()
st.markdown('</div>', unsafe_allow_html=True)

# ── Category nav bar (dynamic, always visible) ────────────────────────────────
render_category_nav()

st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)


# ── Sidebar — filters ONLY ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 Filter Products")
    st.markdown("---")

    _all = load_products()

    if not _all:
        st.info("No products are currently available.")
    else:
        categories = ["All"] + sorted({p["category"] for p in _all})
        prices = [p["price"] for p in _all]
        price_min, price_max = float(min(prices)), float(max(prices))

        # Initialise price range once products are known
        if st.session_state.filter_price is None:
            st.session_state.filter_price = (price_min, price_max)

        # Clamp stored price to current product range
        stored_price = (
            max(price_min, st.session_state.filter_price[0]),
            min(price_max, st.session_state.filter_price[1]),
        )

        all_colors = sorted({c for p in _all for c in p.get("colors", [])})
        color_options = ["All"] + all_colors

        cat_idx = categories.index(st.session_state.filter_cat) if st.session_state.filter_cat in categories else 0
        color_idx = color_options.index(st.session_state.filter_color) if st.session_state.filter_color in color_options else 0
        sort_options = ["Featured", "Price: Low to High", "Price: High to Low", "Top Rated"]
        sort_idx = sort_options.index(st.session_state.filter_sort) if st.session_state.filter_sort in sort_options else 0

        selected_cat = st.selectbox("Category", categories, index=cat_idx)
        selected_color = st.selectbox("Color", color_options, index=color_idx)
        price_range = st.slider(
            "Price Range ($)",
            min_value=price_min,
            max_value=price_max,
            value=stored_price,
            step=1.0,
        )
        sort_by = st.selectbox("Sort By", sort_options, index=sort_idx)

        # Detect any filter change vs. last run
        filters_changed = (
            selected_cat != st.session_state.filter_cat
            or selected_color != st.session_state.filter_color
            or price_range != st.session_state.filter_price
            or sort_by != st.session_state.filter_sort
        )

        # Persist filter selections
        st.session_state.filter_cat = selected_cat
        st.session_state.filter_color = selected_color
        st.session_state.filter_price = price_range
        st.session_state.filter_sort = sort_by

        # Active-filter badge + clear button
        active_count = sum([
            selected_cat != "All",
            selected_color != "All",
            price_range != (price_min, price_max),
            sort_by != "Featured",
        ])
        if active_count:
            st.markdown(
                f"<div style='background:#fce4ec;border-radius:8px;padding:6px 10px;"
                f"color:#c2185b;font-size:.85em;margin-bottom:6px'>"
                f"<b>{active_count} filter{'s' if active_count > 1 else ''} active</b></div>",
                unsafe_allow_html=True,
            )
            if st.button("✖ Clear All Filters", use_container_width=True):
                st.session_state.filter_cat = "All"
                st.session_state.filter_color = "All"
                st.session_state.filter_price = (price_min, price_max)
                st.session_state.filter_sort = "Featured"
                st.toast("Filters cleared!")
                st.rerun()

        # Auto-navigate to shop when a filter changes
        if filters_changed and st.session_state.view != "shop":
            st.session_state.view = "shop"
            st.session_state.selected_product = None
            st.rerun()


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
        stars = "★" * int(p.get("rating", 0)) + "☆" * (5 - int(p.get("rating", 0)))
        badge_html = f'<span class="badge">-{discount}%</span>' if discount else ""
        featured_html = (
            '<span class="badge-featured">✦ Featured</span>' if p.get("featured") else ""
        )
        orig_html = (
            f'<span class="price-was">${p["original_price"]:.2f}</span>'
            if p.get("original_price")
            else ""
        )
        disc_html = f'<span class="discount">{discount}% OFF</span>' if discount else ""

        st.markdown(
            f"""
<div class="product-card">
  <div class="product-img-wrap">
    <img src="{p['image']}" alt="{p['name']}">
    {badge_html}{featured_html}
  </div>
  <div class="product-info">
    <div class="product-name">{p['name']}</div>
    <div class="stars">{stars} <span style="color:#999;font-size:.8em">({p.get('reviews',0)})</span></div>
    <div class="price-wrap">
      <span class="price-now">${p['price']:.2f}</span>
      {orig_html}{disc_html}
    </div>
  </div>
</div>""",
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🛒 Add to Cart", key=f"cart_{p['id']}", use_container_width=True):
                add_to_cart(p)
                st.toast(f"✅ {p['name']} added to cart!")
        with c2:
            if st.button("👁️ View Details", key=f"view_{p['id']}", use_container_width=True):
                st.session_state.selected_product = p
                st.session_state.view = "detail"
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# VIEW: HOME
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.view == "home":

    # Hero carousel
    render_hero_carousel()
    st.markdown("<div style='margin-bottom:28px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="content-pad">', unsafe_allow_html=True)

    all_products = load_products()

    # Featured section
    st.markdown('<h2 class="section-title">✦ Featured Collection</h2>', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-sub">Handpicked favourites loved by thousands</p>',
        unsafe_allow_html=True,
    )
    featured = [p for p in all_products if p.get("featured")]
    cols = st.columns(3)
    for i, p in enumerate(featured):
        render_product_card(p, cols[i % 3])

    # More Earrings section
    non_featured = [p for p in all_products if not p.get("featured")]
    if non_featured:
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown('<h2 class="section-title">🛍️ More Earrings</h2>', unsafe_allow_html=True)
        st.markdown(
            '<p class="section-sub">Explore our full collection</p>', unsafe_allow_html=True
        )
        cols2 = st.columns(3)
        for i, p in enumerate(non_featured):
            render_product_card(p, cols2[i % 3])

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Value props
    st.markdown('<h2 class="section-title">Why Love Earrings?</h2>', unsafe_allow_html=True)
    st.markdown('<div class="value-props-row">', unsafe_allow_html=True)
    v1, v2, v3, v4 = st.columns(4)
    for col, icon, title, desc in [
        (v1, "🚚", "Free Shipping", "On all orders over $35"),
        (v2, "💎", "Premium Quality", "Hypoallergenic materials"),
        (v3, "↩️", "30-Day Returns", "Hassle-free returns"),
        (v4, "🔒", "Secure Payment", "100% safe checkout"),
    ]:
        with col:
            st.markdown(
                f"""<div style="text-align:center;padding:20px;background:#fdf6f9;border-radius:14px;border:1px solid #f5c6d0">
                <div style="font-size:2em">{icon}</div>
                <div style="font-family:'Playfair Display',serif;font-weight:600;color:#1e0a3c;margin:8px 0 4px">{title}</div>
                <div style="color:#888;font-size:.88em">{desc}</div>
            </div>""",
                unsafe_allow_html=True,
            )

    st.markdown('</div>', unsafe_allow_html=True)  # close value-props-row
    st.markdown("<br>", unsafe_allow_html=True)
    _, mid, _ = st.columns([2, 1, 2])
    with mid:
        if st.button("🛍️ Shop All Earrings", use_container_width=True):
            st.session_state.view = "shop"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)  # close content-pad

    st.markdown(
        """
<div class="footer">
  <h3>💎 Love Earrings</h3>
  <p>Crafted with love, worn with pride.</p>
  <p style="margin-top:14px">
    <a href="#">Privacy Policy</a>
    <a href="#">Terms of Service</a>
    <a href="#">Contact Us</a>
    <a href="#">FAQ</a>
  </p>
  <p style="margin-top:18px;font-size:.82em;color:#8a6070">© 2026 Love Earrings. All rights reserved.</p>
</div>""",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# VIEW: SHOP
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.view == "shop":
    render_hero_carousel()
    st.markdown('<div class="content-pad">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">🛍️ All Earrings</h2>', unsafe_allow_html=True)

    search = st.text_input("🔍 Search earrings...", placeholder="e.g. gold hoop, pearl stud...")
    all_products = load_products()

    if search:
        q = search.lower()
        all_products = [
            p for p in all_products
            if q in p["name"].lower()
            or q in p.get("description", "").lower()
            or any(q in t for t in p.get("tags", []))
        ]

    products = apply_filters(all_products)

    st.markdown(
        f'<p class="section-sub">{len(products)} earrings found</p>',
        unsafe_allow_html=True,
    )

    if not products:
        st.info("No earrings match your filters. Try adjusting the sidebar filters.")
    else:
        cols = st.columns(3)
        for i, p in enumerate(products):
            render_product_card(p, cols[i % 3])
    st.markdown('</div>', unsafe_allow_html=True)  # close content-pad


# ─────────────────────────────────────────────────────────────────────────────
# VIEW: PRODUCT DETAIL
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.view == "detail":
    st.markdown('<div class="content-pad detail-page">', unsafe_allow_html=True)
    p = st.session_state.selected_product
    if not p:
        st.session_state.view = "shop"
        st.rerun()

    if st.button("← Back to Shop"):
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

        st.markdown(
            f"""
<h1 style="font-family:'Playfair Display',serif;color:#1e0a3c;font-size:2em">{p['name']}</h1>
<div style="color:#f4a423;font-size:1.1em">{stars}
  <span style="color:#999;font-size:.85em">({p.get('reviews',0)} reviews)</span>
</div><br>
<div style="display:flex;align-items:center;gap:14px">
  <span style="font-size:2em;font-weight:700;color:#c2185b">${p['price']:.2f}</span>
  {'<span style="text-decoration:line-through;color:#aaa;font-size:1.2em">$' + f"{p['original_price']:.2f}" + '</span>' if p.get('original_price') else ''}
  {'<span style="background:#e91e8c;color:#fff;padding:3px 12px;border-radius:20px;font-size:.85em;font-weight:700">' + str(discount) + '% OFF</span>' if discount else ''}
</div><br>
<p style="color:#555;line-height:1.7">{p.get('description','')}</p><br>
<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px">
  {''.join(f'<span style="background:#f9f0f4;color:#c2185b;border:1px solid #f5c6d0;border-radius:20px;padding:4px 14px;font-size:.82em;font-weight:600">{c}</span>' for c in p.get('colors',[]))}
</div>
<div style="background:#f9f0f4;border-radius:10px;padding:10px 16px;margin-bottom:18px;font-size:.9em;color:#555">
  📦 Category: <strong>{p.get('category','')}</strong> &nbsp;|&nbsp;
  🏷️ Stock: <strong>{'In Stock' if p.get('stock',0) > 0 else 'Out of Stock'}</strong>
  {(' &nbsp;|&nbsp; 🔥 Only ' + str(p['stock']) + ' left!') if 0 < p.get('stock',0) < 10 else ''}
</div>
""",
            unsafe_allow_html=True,
        )

        qty = st.number_input(
            "Quantity", min_value=1, max_value=min(p.get("stock", 1), 10), value=1
        )

        a1, a2 = st.columns(2)
        with a1:
            if st.button("🛒 Add to Cart", use_container_width=True, type="primary"):
                add_to_cart(p, qty)
                st.toast(f"✅ {qty} × {p['name']} added to cart!")
        with a2:
            if st.button("💗 Buy Now", use_container_width=True):
                add_to_cart(p, qty)
                st.session_state.view = "cart"
                st.rerun()

    st.markdown("---")
    st.markdown("### You Might Also Like")
    all_products = load_products()
    related = [
        x for x in all_products
        if x["category"] == p["category"] and x["id"] != p["id"]
    ][:3]
    if related:
        cols = st.columns(3)
        for i, rp in enumerate(related):
            render_product_card(rp, cols[i])
    st.markdown('</div>', unsafe_allow_html=True)  # close content-pad


# ─────────────────────────────────────────────────────────────────────────────
# VIEW: CART  (full checkout page)
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.view == "cart":
    st.markdown('<div class="content-pad cart-page">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">🛒 Your Cart</h2>', unsafe_allow_html=True)

    if st.session_state.checkout_done:
        st.balloons()
        st.success("🎉 Order placed successfully! Thank you for shopping with Love Earrings.")
        st.session_state.checkout_done = False
        st.session_state.cart = []
        if st.button("Continue Shopping"):
            st.session_state.view = "shop"
            st.rerun()

    elif not st.session_state.cart:
        st.info("Your cart is empty. Start shopping!")
        if st.button("🛍️ Shop Now"):
            st.session_state.view = "shop"
            st.rerun()
    else:
        cart_col, summary_col = st.columns([2, 1])

        with cart_col:
            for idx, item in enumerate(st.session_state.cart):
                with st.container():
                    ic, nc, pc, rc = st.columns([1, 3, 2, 1])
                    with ic:
                        st.image(resolve_image(item["image"]), width=80)
                    with nc:
                        st.markdown(f"**{item['name']}**")
                        st.caption(f"Category: {item.get('category','')}")
                    with pc:
                        new_qty = st.number_input(
                            "Qty", min_value=1, max_value=10,
                            value=item["qty"], key=f"qty_{idx}",
                        )
                        st.session_state.cart[idx]["qty"] = new_qty
                        st.markdown(f"**${item['price'] * new_qty:.2f}**")
                    with rc:
                        if st.button("🗑️", key=f"del_{idx}"):
                            st.session_state.cart.pop(idx)
                            st.rerun()
                    st.divider()

        with summary_col:
            subtotal = cart_total()
            shipping = 0 if subtotal >= 35 else 4.99
            total = subtotal + shipping

            st.markdown(
                f"""
<div style="background:#fdf6f9;border-radius:16px;padding:24px;border:1px solid #f5c6d0">
  <h3 style="font-family:'Playfair Display',serif;color:#1e0a3c;margin-bottom:18px">Order Summary</h3>
  <div style="display:flex;justify-content:space-between;margin-bottom:10px">
    <span>Subtotal</span><strong>${subtotal:.2f}</strong>
  </div>
  <div style="display:flex;justify-content:space-between;margin-bottom:10px">
    <span>Shipping</span><strong>{'FREE 🎉' if shipping == 0 else f'${shipping:.2f}'}</strong>
  </div>
  {'<p style="color:#888;font-size:.82em;margin-bottom:10px">Add $' + f"{35 - subtotal:.2f}" + ' more for free shipping!</p>' if shipping > 0 else ''}
  <hr style="border-color:#f5c6d0">
  <div style="display:flex;justify-content:space-between;font-size:1.2em">
    <strong>Total</strong><strong style="color:#c2185b">${total:.2f}</strong>
  </div>
</div>""",
                unsafe_allow_html=True,
            )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**Shipping Details**")
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            address = st.text_area("Address", height=80)

            if st.button("✅ Place Order", use_container_width=True, type="primary"):
                if not name or not email or not address:
                    st.error("Please fill in all shipping details.")
                else:
                    save_order({
                        "customer_name": name,
                        "customer_email": email,
                        "address": address,
                        "items": [
                            {"id": i["id"], "name": i["name"],
                             "price": i["price"], "qty": i["qty"]}
                            for i in st.session_state.cart
                        ],
                        "total": total,
                    })
                    st.session_state.checkout_done = True
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)  # close content-pad
