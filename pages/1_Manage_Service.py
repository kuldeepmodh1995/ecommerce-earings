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
)

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "images")
os.makedirs(STATIC_DIR, exist_ok=True)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def resolve_image(img_path: str) -> str:
    """Convert 'app/static/images/foo.jpg' to an absolute local path for st.image().
    Leaves external URLs unchanged.
    """
    if img_path and img_path.startswith("app/static/"):
        return os.path.join(BASE_DIR, img_path[len("app/"):])
    return img_path

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Manage Service | Love Earrings",
    page_icon="⚙️",
    layout="wide",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@300;400;600&display=swap');
  html, body, [class*="css"] { font-family: 'Lato', sans-serif; }
  .block-container { padding-top: 1rem !important; }

  .admin-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    padding: 24px 32px; border-radius: 14px; margin-bottom: 28px;
    display: flex; align-items: center; justify-content: space-between;
  }
  .admin-header h1 {
    font-family: 'Playfair Display', serif; color: #f5c6d0;
    font-size: 1.8em; margin: 0;
  }
  .admin-header p { color: #d4a5b5; margin: 4px 0 0; font-size: .9em; }
  .admin-badge {
    background: #e91e8c; color: #fff; padding: 4px 14px;
    border-radius: 20px; font-size: .78em; font-weight: 700; letter-spacing: 1px;
  }

  .stat-card {
    background: #fff; border-radius: 14px; padding: 20px 24px;
    border: 1px solid #f0e8ed; text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,.06);
  }
  .stat-number { font-size: 2.2em; font-weight: 700; color: #c2185b; }
  .stat-label { color: #888; font-size: .88em; margin-top: 4px; }

  .section-card {
    background: #fff; border-radius: 14px; padding: 24px;
    border: 1px solid #f0e8ed; margin-bottom: 24px;
    box-shadow: 0 2px 12px rgba(0,0,0,.04);
  }
  .section-title {
    font-family: 'Playfair Display', serif; color: #1a1a2e;
    font-size: 1.35em; margin-bottom: 18px; padding-bottom: 10px;
    border-bottom: 2px solid #f5c6d0;
  }

  .product-row {
    background: #fdf6f9; border-radius: 10px;
    padding: 12px 16px; margin-bottom: 8px;
    border: 1px solid #f0e4ec; display: flex; align-items: center; gap: 16px;
  }

  .status-badge {
    display: inline-block; padding: 3px 12px; border-radius: 20px;
    font-size: .78em; font-weight: 700;
  }
  .status-pending { background: #fff3cd; color: #856404; }
  .status-processing { background: #cfe2ff; color: #084298; }
  .status-shipped { background: #d1ecf1; color: #0c5460; }
  .status-delivered { background: #d4edda; color: #155724; }
  .status-cancelled { background: #f8d7da; color: #721c24; }

  [data-testid="stSidebar"] { background: #1a1a2e !important; }
  [data-testid="stSidebar"] * { color: #d4a5b5 !important; }
  [data-testid="stSidebar"] .stRadio label { color: #f5c6d0 !important; }

  .login-card {
    max-width: 400px; margin: 80px auto; background: #fff;
    border-radius: 20px; padding: 40px; box-shadow: 0 8px 40px rgba(0,0,0,.12);
    border: 1px solid #f5c6d0; text-align: center;
  }
  .login-card h2 { font-family: 'Playfair Display', serif; color: #1a1a2e; }
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
        ["📊 Dashboard", "🛍️ Products", "📦 Orders", "🖼️ Media Library"],
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

    st.markdown("<br>", unsafe_allow_html=True)

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

    # Recent orders
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

    # ── All Products tab ──
    with tab1:
        products = load_products()
        search = st.text_input("🔍 Search products...", placeholder="Name, category, color...")
        if search:
            q = search.lower()
            products = [p for p in products if q in p["name"].lower() or q in p.get("category", "").lower()]

        st.caption(f"{len(products)} products")

        for p in products:
            with st.expander(f"{'⭐ ' if p.get('featured') else ''}{p['name']} — {p['category']} — ${p['price']:.2f}"):
                col_img, col_form = st.columns([1, 2])

                with col_img:
                    st.image(resolve_image(p["image"]), use_container_width=True)

                    # Image upload
                    st.markdown("**Update Product Image**")
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
                        st.success("Image updated!")
                        st.rerun()

                    # Or URL
                    new_url = st.text_input(
                        "Or paste image URL",
                        value=p.get("image", ""),
                        key=f"url_{p['id']}",
                    )

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

                        colors_raw = st.text_input(
                            "Colors (comma-separated)", value=", ".join(p.get("colors", []))
                        )
                        tags_raw = st.text_input(
                            "Tags (comma-separated)", value=", ".join(p.get("tags", []))
                        )
                        featured = st.checkbox("Featured Product", value=p.get("featured", False))

                        sc1, sc2 = st.columns(2)
                        with sc1:
                            save_btn = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
                        with sc2:
                            del_btn = st.form_submit_button("🗑️ Delete Product", use_container_width=True)

                        if save_btn:
                            img_val = new_url if new_url != p.get("image", "") else p.get("image", "")
                            update_product(
                                p["id"],
                                {
                                    "name": name,
                                    "description": desc,
                                    "price": price,
                                    "original_price": orig_price,
                                    "category": category,
                                    "stock": stock,
                                    "colors": [c.strip() for c in colors_raw.split(",") if c.strip()],
                                    "tags": [t.strip() for t in tags_raw.split(",") if t.strip()],
                                    "featured": featured,
                                    "image": img_val,
                                },
                            )
                            st.success(f"✅ '{name}' updated successfully!")
                            st.rerun()

                        if del_btn:
                            delete_product(p["id"])
                            st.warning(f"🗑️ '{p['name']}' deleted.")
                            st.rerun()

    # ── Add New Product tab ──
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
                        "name": new_name,
                        "description": new_desc,
                        "price": new_price,
                        "original_price": new_orig,
                        "category": new_cat,
                        "stock": new_stock,
                        "colors": [c.strip() for c in new_colors.split(",") if c.strip()],
                        "tags": [t.strip() for t in new_tags.split(",") if t.strip()],
                        "featured": new_featured,
                        "image": img_path,
                        "rating": 0.0,
                        "reviews": 0,
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
            status_colors = {
                "Pending": "#856404",
                "Processing": "#084298",
                "Shipped": "#0c5460",
                "Delivered": "#155724",
                "Cancelled": "#721c24",
            }
            sc = status_colors.get(status, "#555")

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

                    total_items = sum(i["qty"] for i in o.get("items", []))
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

    # Upload new image
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

    # Gallery of uploaded images
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

    # Show all current product images
    st.markdown("---")
    st.markdown("**Current Product Image URLs:**")
    products = load_products()
    for p in products:
        st.markdown(f"- **{p['name']}**: `{p.get('image', '')}`")
