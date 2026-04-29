import streamlit as st
import sys
import os
import base64
import shutil
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.data_manager import (
    load_products,
    save_products,
    add_product,
    update_product,
    delete_product,
    load_orders,
    update_order_status,
    get_stats,
    load_hero_banners,
    save_hero_banners,
    add_hero_banner,
    update_hero_banner,
    delete_hero_banner,
)

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "images")
os.makedirs(STATIC_DIR, exist_ok=True)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def resolve_image(img_path: str) -> str:
    if img_path and img_path.startswith("app/static/"):
        return os.path.join(BASE_DIR, img_path[len("app/"):])
    return img_path


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Manage Service | Love Earrings",
    page_icon="⚙️",
    layout="wide",
)

# ── Viewport meta ─────────────────────────────────────────────────────────────
st.markdown(
    '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
    unsafe_allow_html=True,
)

# ── CSS — MOBILE FIRST ────────────────────────────────────────────────────────
st.markdown(
    """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@300;400;600&display=swap');
  html, body, [class*="css"] { font-family: 'Lato', sans-serif; box-sizing: border-box; }
  *, *::before, *::after { box-sizing: inherit; }

  /* ══════════════════════════════════════════════
     BASE = mobile 360px
     ══════════════════════════════════════════════ */
  .block-container { padding: 0.4rem 0.4rem 2rem !important; max-width: 100% !important; }

  .admin-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    padding: 14px 14px; border-radius: 10px; margin-bottom: 14px;
    display: flex; flex-direction: column; align-items: flex-start; gap: 8px;
  }
  .admin-header h1 {
    font-family: 'Playfair Display', serif; color: #f5c6d0; font-size: 1.15em; margin: 0;
  }
  .admin-header p { color: #d4a5b5; margin: 0; font-size: .80em; }
  .admin-badge {
    background: #e91e8c; color: #fff; padding: 3px 11px;
    border-radius: 20px; font-size: .72em; font-weight: 700; letter-spacing: 1px;
  }

  .stat-card {
    background: #fff; border-radius: 12px; padding: 14px 12px;
    border: 1px solid #f0e8ed; text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,.06);
  }
  .stat-number { font-size: 1.7em; font-weight: 700; color: #c2185b; }
  .stat-label { color: #888; font-size: .78em; margin-top: 3px; }

  /* Stat cards: 2×2 on mobile */
  .stat-cards-row div[data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
  .stat-cards-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
    min-width: 48% !important; flex: 0 0 48% !important;
  }

  /* Dashboard panels: stacked on mobile */
  .dash-cols-row div[data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
  .dash-cols-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
    min-width: 100% !important; flex: 0 0 100% !important;
  }

  .section-card {
    background: #fff; border-radius: 12px; padding: 14px 12px;
    border: 1px solid #f0e8ed; margin-bottom: 14px;
    box-shadow: 0 2px 10px rgba(0,0,0,.04);
  }
  .section-title {
    font-family: 'Playfair Display', serif; color: #1a1a2e;
    font-size: 1.05em; margin-bottom: 12px; padding-bottom: 8px;
    border-bottom: 2px solid #f5c6d0;
  }

  .product-row {
    background: #fdf6f9; border-radius: 10px; flex-wrap: wrap;
    padding: 10px 12px; margin-bottom: 8px;
    border: 1px solid #f0e4ec; display: flex; align-items: center; gap: 10px;
  }

  .status-badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: .74em; font-weight: 700; }
  .status-pending { background: #fff3cd; color: #856404; }
  .status-processing { background: #cfe2ff; color: #084298; }
  .status-shipped { background: #d1ecf1; color: #0c5460; }
  .status-delivered { background: #d4edda; color: #155724; }
  .status-cancelled { background: #f8d7da; color: #721c24; }

  [data-testid="stSidebar"] { background: #1a1a2e !important; }
  [data-testid="stSidebar"] * { color: #d4a5b5 !important; }
  [data-testid="stSidebar"] .stRadio label { color: #f5c6d0 !important; }

  .login-card {
    max-width: 100%; margin: 20px auto; background: #fff;
    border-radius: 16px; padding: 24px 16px; box-shadow: 0 6px 30px rgba(0,0,0,.10);
    border: 1px solid #f5c6d0; text-align: center;
  }
  .login-card h2 { font-family: 'Playfair Display', serif; color: #1a1a2e; font-size: 1.3em; }

  .banner-card {
    background: #fdf6f9; border-radius: 12px; padding: 12px;
    border: 1px solid #f0e4ec; margin-bottom: 10px;
  }

  /* ══════════════════════════════════════════════
     TABLET — min-width: 600px
     ══════════════════════════════════════════════ */
  @media (min-width: 600px) {
    .block-container { padding: 0.6rem 0.75rem 2rem !important; }
    .admin-header { padding: 18px 22px; flex-direction: row; align-items: center; margin-bottom: 20px; }
    .admin-header h1 { font-size: 1.4em; }
    .stat-card { padding: 16px 16px; }
    .stat-number { font-size: 1.9em; }
    .stat-label { font-size: .82em; }
    .section-card { padding: 18px 16px; margin-bottom: 18px; }
    .section-title { font-size: 1.2em; }
    .login-card { max-width: 420px; margin: 40px auto; padding: 32px 24px; }
  }

  /* ══════════════════════════════════════════════
     DESKTOP — min-width: 960px
     ══════════════════════════════════════════════ */
  @media (min-width: 960px) {
    .block-container { padding: 1rem 1rem 2rem !important; }
    .admin-header { padding: 24px 32px; border-radius: 14px; margin-bottom: 28px; }
    .admin-header h1 { font-size: 1.8em; }
    .admin-header p { font-size: .9em; }

    /* Stat cards: 4 columns on desktop */
    .stat-cards-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
      min-width: unset !important; flex: 1 1 0 !important;
    }

    /* Dashboard panels: side-by-side on desktop */
    .dash-cols-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
      min-width: unset !important; flex: 1 1 0 !important;
    }

    .stat-card { padding: 20px 24px; border-radius: 14px; }
    .stat-number { font-size: 2.2em; }
    .stat-label { font-size: .88em; }
    .section-card { padding: 24px; border-radius: 14px; margin-bottom: 24px; }
    .section-title { font-size: 1.35em; margin-bottom: 18px; padding-bottom: 10px; }
    .product-row { padding: 12px 16px; gap: 16px; }
    .login-card { max-width: 400px; margin: 80px auto; padding: 40px; border-radius: 20px; }
    .status-badge { padding: 3px 12px; font-size: .78em; }
  }
</style>
""",
    unsafe_allow_html=True,
)

# ── Auth ──────────────────────────────────────────────────────────────────────
ADMIN_PASSWORD = "loveearrings2026"

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    st.markdown(
        """
<div class="login-card">
  <div style="font-size:3em">⚙️</div>
  <h2>Manage Service</h2>
  <p style="color:#888;margin-bottom:24px">Love Earrings Internal Tool</p>
</div>""",
        unsafe_allow_html=True,
    )
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown("### Admin Login")
        password = st.text_input("Password", type="password", placeholder="Enter admin password")
        if st.button("Login", use_container_width=True, type="primary"):
            if password == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Incorrect password. Please try again.")
        st.caption("💡 Default password: `loveearrings2026`")
    st.stop()

# ── Admin UI ──────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="admin-header">
  <div>
    <h1>⚙️ Manage Service</h1>
    <p>Love Earrings — Internal Management Tool</p>
  </div>
  <div>
    <span class="admin-badge">ADMIN PANEL</span>
  </div>
</div>""",
    unsafe_allow_html=True,
)

# Sidebar navigation
with st.sidebar:
    st.markdown(
        '<div style="text-align:center;padding:16px 0"><span style="font-size:1.8em">⚙️</span><br>'
        '<strong style="font-size:1.1em;color:#f5c6d0">Manage Service</strong></div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")
    section = st.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "🛍️ Products",
            "📦 Orders",
            "🖼️ Media Library",
            "🎠 Hero Banners",
        ],
        label_visibility="collapsed",
    )
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.admin_logged_in = False
        st.rerun()
    st.markdown(
        '<p style="font-size:.78em;text-align:center;margin-top:16px;color:#8a6070 !important">'
        'Love Earrings v1.0</p>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
if section == "📊 Dashboard":
    stats = get_stats()

    st.markdown('<div class="stat-cards-row">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    for col, icon, number, label in [
        (c1, "🛍️", stats["total_products"], "Total Products"),
        (c2, "📦", stats["total_orders"], "Total Orders"),
        (c3, "⏳", stats["pending_orders"], "Pending Orders"),
        (c4, "💰", f"${stats['total_revenue']:.2f}", "Total Revenue"),
    ]:
        with col:
            st.markdown(
                f"""<div class="stat-card">
                <div style="font-size:2em">{icon}</div>
                <div class="stat-number">{number}</div>
                <div class="stat-label">{label}</div>
            </div>""",
                unsafe_allow_html=True,
            )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="dash-cols-row">', unsafe_allow_html=True)
    dash_left, dash_right = st.columns([1, 1])

    with dash_left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 Product Categories</div>', unsafe_allow_html=True)
        products = load_products()
        from collections import Counter
        cats = Counter(p["category"] for p in products)
        for cat, cnt in cats.most_common():
            pct = int(cnt / len(products) * 100)
            st.markdown(
                f"""<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
                <span style="font-weight:600">{cat}</span>
                <span style="color:#888">{cnt} products</span>
            </div>
            <div style="background:#f0e8ed;border-radius:20px;height:8px;margin-bottom:14px">
                <div style="background:linear-gradient(90deg,#e91e8c,#c2185b);width:{pct}%;height:8px;border-radius:20px"></div>
            </div>""",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with dash_right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">⚠️ Low Stock Alerts</div>', unsafe_allow_html=True)
        low = stats["low_stock"]
        if low:
            for p in low:
                color = "#dc3545" if p["stock"] < 5 else "#fd7e14"
                st.markdown(
                    f"""<div style="display:flex;justify-content:space-between;align-items:center;
                    background:#fdf6f9;padding:10px 14px;border-radius:10px;margin-bottom:8px;
                    border-left:4px solid {color}">
                        <span style="font-weight:600">{p['name']}</span>
                        <span style="color:{color};font-weight:700">{p['stock']} left</span>
                    </div>""",
                    unsafe_allow_html=True,
                )
        else:
            st.success("All products are well stocked!")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # close dash-cols-row

    orders = load_orders()
    if orders:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📦 Recent Orders</div>', unsafe_allow_html=True)
        recent = sorted(orders, key=lambda x: x.get("created_at", ""), reverse=True)[:5]
        for o in recent:
            status_class = f"status-{o.get('status', 'pending').lower()}"
            st.markdown(
                f"""<div class="product-row" style="justify-content:space-between">
                <div><strong>{o['id']}</strong><br>
                  <span style="color:#888;font-size:.85em">{o.get('customer_name','N/A')} — {o.get('customer_email','')}</span>
                </div>
                <div style="text-align:right">
                  <strong style="color:#c2185b">${o.get('total',0):.2f}</strong><br>
                  <span class="status-badge {status_class}">{o.get('status','Pending')}</span>
                </div>
            </div>""",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PRODUCTS
# ─────────────────────────────────────────────────────────────────────────────
elif section == "🛍️ Products":
    tab1, tab2 = st.tabs(["📋 All Products", "➕ Add New Product"])

    with tab1:
        all_products = load_products()
        search = st.text_input("🔍 Search products...", placeholder="Name, category, color...")
        if search:
            q = search.lower()
            all_products = [p for p in all_products if q in p["name"].lower() or q in p.get("category", "").lower()]

        st.caption(f"{len(all_products)} products total")

        featured_products = [p for p in all_products if p.get("featured")]
        more_products = [p for p in all_products if not p.get("featured")]

        if featured_products:
            st.markdown(
                '<div class="section-title" style="margin-top:8px">⭐ Featured Collection</div>',
                unsafe_allow_html=True,
            )
            st.caption(f"{len(featured_products)} featured products")

        for p in featured_products:
            with st.expander(f"⭐ {p['name']} — {p['category']} — ${p['price']:.2f}"):
                col_img, col_form = st.columns([1, 2])

                with col_img:
                    st.image(resolve_image(p["image"]), use_container_width=True)
                    st.markdown("**Upload New Image**")
                    uploaded = st.file_uploader(
                        "Upload new image",
                        type=["jpg", "jpeg", "png", "webp"],
                        key=f"upload_{p['id']}",
                        label_visibility="collapsed",
                    )
                    if uploaded:
                        ext = uploaded.name.split(".")[-1]
                        filename = f"{p['id']}.{ext}"
                        filepath = os.path.join(STATIC_DIR, filename)
                        with open(filepath, "wb") as f:
                            f.write(uploaded.read())
                        update_product(p["id"], {"image": f"app/static/images/{filename}"})
                        st.success("✅ Image saved!")
                        st.rerun()

                with col_form:
                    with st.form(key=f"edit_{p['id']}"):
                        name = st.text_input("Product Name", value=p["name"])
                        desc = st.text_area("Description", value=p.get("description", ""), height=100)

                        fc1, fc2 = st.columns(2)
                        with fc1:
                            price = st.number_input("Price ($)", value=float(p["price"]), step=0.01)
                            stock = st.number_input("Stock", value=int(p.get("stock", 0)), step=1)
                        with fc2:
                            orig_price = st.number_input(
                                "Original Price ($)", value=float(p.get("original_price", p["price"])), step=0.01
                            )
                            category = st.selectbox(
                                "Category",
                                ["Studs", "Hoops", "Drops", "Chandeliers", "Dangles"],
                                index=["Studs", "Hoops", "Drops", "Chandeliers", "Dangles"].index(p.get("category", "Studs"))
                                if p.get("category") in ["Studs", "Hoops", "Drops", "Chandeliers", "Dangles"]
                                else 0,
                            )

                        colors_raw = st.text_input("Colors (comma-separated)", value=", ".join(p.get("colors", [])))
                        tags_raw = st.text_input("Tags (comma-separated)", value=", ".join(p.get("tags", [])))
                        featured = st.checkbox("Featured Product", value=p.get("featured", False))
                        new_url = st.text_input("🔗 Image URL (paste to change)", value=p.get("image", ""))

                        sc1, sc2 = st.columns(2)
                        with sc1:
                            save_btn = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
                        with sc2:
                            del_btn = st.form_submit_button("🗑️ Delete Product", use_container_width=True)

                        if save_btn:
                            update_product(p["id"], {
                                "name": name, "description": desc, "price": price,
                                "original_price": orig_price, "category": category, "stock": stock,
                                "colors": [c.strip() for c in colors_raw.split(",") if c.strip()],
                                "tags": [t.strip() for t in tags_raw.split(",") if t.strip()],
                                "featured": featured, "image": new_url,
                            })
                            st.success(f"✅ '{name}' updated successfully!")

                        if del_btn:
                            delete_product(p["id"])
                            st.warning(f"🗑️ '{p['name']}' deleted.")
                            st.rerun()

        if more_products:
            st.markdown("<hr style='border-color:#f5c6d0;margin:20px 0'>", unsafe_allow_html=True)
            st.markdown('<div class="section-title">🛍️ More Earrings</div>', unsafe_allow_html=True)
            st.caption(f"{len(more_products)} non-featured products")

        for p in more_products:
            with st.expander(f"{p['name']} — {p['category']} — ${p['price']:.2f}"):
                col_img, col_form = st.columns([1, 2])

                with col_img:
                    st.image(resolve_image(p["image"]), use_container_width=True)
                    st.markdown("**Upload New Image**")
                    uploaded = st.file_uploader(
                        "Upload new image",
                        type=["jpg", "jpeg", "png", "webp"],
                        key=f"upload_{p['id']}",
                        label_visibility="collapsed",
                    )
                    if uploaded:
                        ext = uploaded.name.split(".")[-1]
                        filename = f"{p['id']}.{ext}"
                        filepath = os.path.join(STATIC_DIR, filename)
                        with open(filepath, "wb") as f:
                            f.write(uploaded.read())
                        update_product(p["id"], {"image": f"app/static/images/{filename}"})
                        st.success("✅ Image saved!")
                        st.rerun()

                with col_form:
                    with st.form(key=f"edit_{p['id']}"):
                        name = st.text_input("Product Name", value=p["name"])
                        desc = st.text_area("Description", value=p.get("description", ""), height=100)

                        fc1, fc2 = st.columns(2)
                        with fc1:
                            price = st.number_input("Price ($)", value=float(p["price"]), step=0.01)
                            stock = st.number_input("Stock", value=int(p.get("stock", 0)), step=1)
                        with fc2:
                            orig_price = st.number_input(
                                "Original Price ($)", value=float(p.get("original_price", p["price"])), step=0.01
                            )
                            category = st.selectbox(
                                "Category",
                                ["Studs", "Hoops", "Drops", "Chandeliers", "Dangles"],
                                index=["Studs", "Hoops", "Drops", "Chandeliers", "Dangles"].index(p.get("category", "Studs"))
                                if p.get("category") in ["Studs", "Hoops", "Drops", "Chandeliers", "Dangles"]
                                else 0,
                            )

                        colors_raw = st.text_input("Colors (comma-separated)", value=", ".join(p.get("colors", [])))
                        tags_raw = st.text_input("Tags (comma-separated)", value=", ".join(p.get("tags", [])))
                        featured = st.checkbox("Featured Product", value=p.get("featured", False))
                        new_url = st.text_input("🔗 Image URL (paste to change)", value=p.get("image", ""))

                        sc1, sc2 = st.columns(2)
                        with sc1:
                            save_btn = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
                        with sc2:
                            del_btn = st.form_submit_button("🗑️ Delete Product", use_container_width=True)

                        if save_btn:
                            update_product(p["id"], {
                                "name": name, "description": desc, "price": price,
                                "original_price": orig_price, "category": category, "stock": stock,
                                "colors": [c.strip() for c in colors_raw.split(",") if c.strip()],
                                "tags": [t.strip() for t in tags_raw.split(",") if t.strip()],
                                "featured": featured, "image": new_url,
                            })
                            st.success(f"✅ '{name}' updated successfully!")

                        if del_btn:
                            delete_product(p["id"])
                            st.warning(f"🗑️ '{p['name']}' deleted.")
                            st.rerun()

    with tab2:
        st.markdown("### Add New Earring Product")
        with st.form("add_product_form"):
            nc1, nc2 = st.columns(2)
            with nc1:
                new_name = st.text_input("Product Name *")
                new_price = st.number_input("Price ($) *", min_value=0.01, step=0.01, value=19.99)
                new_orig = st.number_input("Original Price ($)", min_value=0.0, step=0.01, value=29.99)
                new_stock = st.number_input("Stock *", min_value=0, step=1, value=50)
            with nc2:
                new_cat = st.selectbox("Category *", ["Studs", "Hoops", "Drops", "Chandeliers", "Dangles"])
                new_colors = st.text_input("Colors (comma-separated)", placeholder="Gold, Silver")
                new_tags = st.text_input("Tags (comma-separated)", placeholder="daily wear, gold")
                new_featured = st.checkbox("Mark as Featured")

            new_desc = st.text_area("Description *", height=100)
            new_img_url = st.text_input("Image URL", placeholder="https://...")
            new_img_file = st.file_uploader("Or upload image", type=["jpg", "jpeg", "png", "webp"])

            submitted = st.form_submit_button("➕ Add Product", use_container_width=True, type="primary")

            if submitted:
                if not new_name or not new_desc:
                    st.error("Product name and description are required.")
                else:
                    img_path = new_img_url or "https://images.unsplash.com/photo-1630018548696-e6f716289c97?w=400&h=400&fit=crop"
                    prod_id = add_product({
                        "name": new_name, "description": new_desc,
                        "price": new_price, "original_price": new_orig,
                        "category": new_cat, "stock": new_stock,
                        "colors": [c.strip() for c in new_colors.split(",") if c.strip()],
                        "tags": [t.strip() for t in new_tags.split(",") if t.strip()],
                        "featured": new_featured, "image": img_path,
                        "rating": 0.0, "reviews": 0,
                    })

                    if new_img_file:
                        ext = new_img_file.name.split(".")[-1]
                        filename = f"{prod_id}.{ext}"
                        filepath = os.path.join(STATIC_DIR, filename)
                        with open(filepath, "wb") as f:
                            f.write(new_img_file.read())
                        update_product(prod_id, {"image": f"app/static/images/{filename}"})

                    st.success(f"✅ '{new_name}' added with ID: {prod_id}")
                    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# ORDERS
# ─────────────────────────────────────────────────────────────────────────────
elif section == "📦 Orders":
    orders = load_orders()

    st.markdown(f"### 📦 Orders ({len(orders)} total)")

    if not orders:
        st.info("No orders yet. Orders placed on the storefront will appear here.")
    else:
        status_options = ["All", "Pending", "Processing", "Shipped", "Delivered", "Cancelled"]
        filter_status = st.selectbox("Filter by Status", status_options)

        display_orders = orders if filter_status == "All" else [o for o in orders if o.get("status") == filter_status]
        display_orders = sorted(display_orders, key=lambda x: x.get("created_at", ""), reverse=True)

        for o in display_orders:
            status = o.get("status", "Pending")
            with st.expander(f"🧾 {o['id']} — {o.get('customer_name','N/A')} — ${o.get('total',0):.2f} — {status}"):
                oc1, oc2 = st.columns([2, 1])
                with oc1:
                    st.markdown(f"""
**Customer:** {o.get('customer_name', 'N/A')}
**Email:** {o.get('customer_email', '')}
**Address:** {o.get('address', '')}
**Ordered:** {o.get('created_at', '')[:16].replace('T', ' ')}
""")
                    st.markdown("**Items:**")
                    for item in o.get("items", []):
                        st.markdown(f"- {item['name']} × {item['qty']} — ${item['price'] * item['qty']:.2f}")

                    subtotal = sum(i["price"] * i["qty"] for i in o.get("items", []))
                    st.markdown(f"**Subtotal:** ${subtotal:.2f} | **Total:** ${o.get('total', 0):.2f}")

                with oc2:
                    st.markdown(f"**Current Status:** :{'green' if status == 'Delivered' else 'orange' if status == 'Pending' else 'blue'}[{status}]")
                    new_status = st.selectbox(
                        "Update Status",
                        ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"],
                        index=["Pending", "Processing", "Shipped", "Delivered", "Cancelled"].index(status),
                        key=f"status_{o['id']}",
                    )
                    if st.button("Update", key=f"upd_{o['id']}", type="primary"):
                        update_order_status(o["id"], new_status)
                        st.success(f"Order {o['id']} updated to {new_status}")
                        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# MEDIA LIBRARY
# ─────────────────────────────────────────────────────────────────────────────
elif section == "🖼️ Media Library":
    st.markdown("### 🖼️ Media Library")
    st.caption("Manage product images stored on the server")

    with st.expander("📤 Upload New Image", expanded=True):
        up_file = st.file_uploader(
            "Choose image file",
            type=["jpg", "jpeg", "png", "webp", "gif"],
            key="media_upload",
        )
        custom_name = st.text_input("Custom filename (optional)", placeholder="e.g. gold-hoop-01")
        if st.button("Upload to Library", type="primary") and up_file:
            ext = up_file.name.split(".")[-1]
            fname = (custom_name.strip().replace(" ", "-") or up_file.name.split(".")[0]) + f".{ext}"
            fpath = os.path.join(STATIC_DIR, fname)
            with open(fpath, "wb") as f:
                f.write(up_file.read())
            st.success(f"✅ Uploaded: `app/static/images/{fname}`")
            st.rerun()

    st.markdown("---")
    st.markdown("**Uploaded Images:**")

    images = [
        f for f in os.listdir(STATIC_DIR)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif"))
    ] if os.path.exists(STATIC_DIR) else []

    if not images:
        st.info("No images uploaded yet. Upload images above to see them here.")
    else:
        st.caption(f"{len(images)} images in library")
        cols = st.columns(4)
        for i, fname in enumerate(sorted(images)):
            with cols[i % 4]:
                fpath = os.path.join(STATIC_DIR, fname)
                st.image(fpath, caption=fname, use_container_width=True)
                st.code(f"app/static/images/{fname}", language=None)
                if st.button("🗑️ Delete", key=f"del_img_{fname}"):
                    os.remove(fpath)
                    st.success(f"Deleted {fname}")
                    st.rerun()

    st.markdown("---")
    st.markdown("**Current Product Image URLs:**")
    products = load_products()
    for p in products:
        st.markdown(f"- **{p['name']}**: `{p.get('image', '')}`")


# ─────────────────────────────────────────────────────────────────────────────
# HERO BANNERS
# ─────────────────────────────────────────────────────────────────────────────
elif section == "🎠 Hero Banners":
    st.markdown("### 🎠 Hero Banners")
    st.caption(
        "Auto-rotating carousel banners shown at the top of the homepage. "
        "Clicking a banner redirects shoppers to the configured destination."
    )

    st.info(
        "**Redirect values:** `shop` → all products · `category:Hoops` → filter by category · `https://...` → external link"
    )

    tab_banners, tab_add_banner = st.tabs(["📋 Manage Banners", "➕ Add New Banner"])

    with tab_banners:
        banners = load_hero_banners()
        banners_sorted = sorted(banners, key=lambda x: x.get("sequence", 999))

        if not banners_sorted:
            st.info("No hero banners yet. Add one using the tab above.")
        else:
            st.caption(f"{len(banners_sorted)} banners · Reorder by changing the Sequence number and saving")

            for b in banners_sorted:
                enabled_icon = "🟢" if b.get("enabled", True) else "🔴"
                with st.expander(
                    f"{enabled_icon} {b.get('sequence','?')}. {b.get('title','Untitled')} → {b.get('redirect_to','')}",
                    expanded=False,
                ):
                    img_col, form_col = st.columns([1, 2])

                    with img_col:
                        img_src = b.get("image", "")
                        if img_src:
                            if img_src.startswith("app/static/"):
                                local = resolve_image(img_src)
                                if os.path.exists(local):
                                    st.image(local, use_container_width=True)
                                else:
                                    st.markdown(f"`{img_src}`")
                            else:
                                st.image(img_src, use_container_width=True)
                        else:
                            st.markdown("_No image set_")

                        st.markdown("**Upload Banner Image**")
                        banner_upload = st.file_uploader(
                            "Upload banner image",
                            type=["jpg", "jpeg", "png", "webp"],
                            key=f"banner_up_{b['id']}",
                            label_visibility="collapsed",
                        )
                        if banner_upload:
                            ext = banner_upload.name.split(".")[-1]
                            filename = f"banner_{b['id']}.{ext}"
                            filepath = os.path.join(STATIC_DIR, filename)
                            with open(filepath, "wb") as f:
                                f.write(banner_upload.read())
                            update_hero_banner(b["id"], {"image": f"app/static/images/{filename}"})
                            st.success("✅ Banner image saved!")
                            st.rerun()

                    with form_col:
                        with st.form(key=f"banner_edit_{b['id']}"):
                            hb_title = st.text_input("Title *", value=b.get("title", ""))
                            hb_subtitle = st.text_input("Subtitle", value=b.get("subtitle", ""))
                            hb_btn_text = st.text_input("Button Text", value=b.get("button_text", "Shop Now"))
                            hb_img_url = st.text_input(
                                "🔗 Image URL (or upload left)",
                                value=b.get("image", ""),
                                placeholder="https://...",
                            )
                            hb_redirect = st.text_input(
                                "Redirect To *",
                                value=b.get("redirect_to", "shop"),
                                help="shop · category:Hoops · https://...",
                            )

                            seq_col, en_col = st.columns([1, 1])
                            with seq_col:
                                hb_seq = st.number_input("Sequence", value=int(b.get("sequence", 1)),
                                                         min_value=1, step=1)
                            with en_col:
                                hb_enabled = st.checkbox("Show on homepage", value=b.get("enabled", True))

                            sb1, sb2 = st.columns(2)
                            with sb1:
                                hb_save = st.form_submit_button("💾 Save", use_container_width=True, type="primary")
                            with sb2:
                                hb_del = st.form_submit_button("🗑️ Delete", use_container_width=True)

                            if hb_save:
                                if not hb_title or not hb_redirect:
                                    st.error("Title and Redirect To are required.")
                                else:
                                    update_hero_banner(b["id"], {
                                        "title": hb_title,
                                        "subtitle": hb_subtitle,
                                        "button_text": hb_btn_text,
                                        "image": hb_img_url,
                                        "redirect_to": hb_redirect,
                                        "sequence": hb_seq,
                                        "enabled": hb_enabled,
                                    })
                                    st.success(f"✅ Banner '{hb_title}' saved!")
                                    st.rerun()

                            if hb_del:
                                delete_hero_banner(b["id"])
                                st.warning("🗑️ Banner deleted.")
                                st.rerun()

    with tab_add_banner:
        st.markdown("### Add New Hero Banner")
        with st.form("add_banner_form"):
            ab_title = st.text_input("Title *", placeholder="e.g. New Arrivals")
            ab_subtitle = st.text_input("Subtitle", placeholder="e.g. Fresh styles — just landed")
            ab_btn = st.text_input("Button Text", value="Shop Now")

            img_url_col, img_up_col = st.columns([1, 1])
            with img_url_col:
                ab_img_url = st.text_input("Image URL", placeholder="https://...")
            with img_up_col:
                ab_img_file = st.file_uploader("Or upload image", type=["jpg", "jpeg", "png", "webp"], key="add_banner_img")

            ab_redirect = st.text_input(
                "Redirect To *",
                placeholder="shop  or  category:Hoops  or  https://...",
            )

            existing_banners = load_hero_banners()
            ab_seq = st.number_input(
                "Sequence",
                value=max((b.get("sequence", 0) for b in existing_banners), default=0) + 1,
                min_value=1, step=1,
            )
            ab_enabled = st.checkbox("Show on homepage immediately", value=True)

            ab_submit = st.form_submit_button("➕ Add Banner", use_container_width=True, type="primary")

            if ab_submit:
                if not ab_title or not ab_redirect:
                    st.error("Title and Redirect To are required.")
                else:
                    img_path = ab_img_url or "https://images.unsplash.com/photo-1630018548696-e6f716289c97?w=1400&h=600&fit=crop"
                    new_id = add_hero_banner({
                        "title": ab_title,
                        "subtitle": ab_subtitle,
                        "button_text": ab_btn,
                        "image": img_path,
                        "redirect_to": ab_redirect,
                        "sequence": ab_seq,
                        "enabled": ab_enabled,
                    })

                    if ab_img_file:
                        ext = ab_img_file.name.split(".")[-1]
                        filename = f"banner_{new_id}.{ext}"
                        filepath = os.path.join(STATIC_DIR, filename)
                        with open(filepath, "wb") as f:
                            f.write(ab_img_file.read())
                        update_hero_banner(new_id, {"image": f"app/static/images/{filename}"})

                    st.success(f"✅ Banner '{ab_title}' added!")
                    st.rerun()
