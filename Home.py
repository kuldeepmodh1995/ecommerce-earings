import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from utils.data_manager import load_products, save_order

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Love Earrings",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
  /* ── Global ── */
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Lato:wght@300;400;600&display=swap');

  html, body, [class*="css"] { font-family: 'Lato', sans-serif; }
  .block-container { padding-top: 0 !important; }

  /* ── Hero ── */
  .hero {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    padding: 70px 40px;
    text-align: center;
    border-radius: 0 0 24px 24px;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
  }
  .hero::before {
    content: "💎 ✨ 💗 ✨ 💎";
    position: absolute; top: 12px; left: 50%; transform: translateX(-50%);
    font-size: 22px; opacity: 0.35; letter-spacing: 8px;
  }
  .hero h1 {
    font-family: 'Playfair Display', serif;
    color: #f5c6d0;
    font-size: 3.6em;
    margin: 0 0 10px;
    letter-spacing: 3px;
  }
  .hero p {
    color: #d4a5b5;
    font-size: 1.15em;
    margin: 0 0 28px;
    font-weight: 300;
    letter-spacing: 1px;
  }
  .hero-cta {
    display: inline-block;
    background: linear-gradient(135deg, #e91e8c, #c2185b);
    color: #fff !important;
    padding: 13px 38px;
    border-radius: 50px;
    font-size: 1em;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-decoration: none;
    transition: all .3s;
    box-shadow: 0 6px 24px rgba(233,30,140,.35);
  }
  .hero-cta:hover { transform: translateY(-2px); box-shadow: 0 10px 32px rgba(233,30,140,.5); }

  /* ── Product card ── */
  .product-card {
    background: #fff;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 2px 16px rgba(0,0,0,.07);
    transition: transform .25s, box-shadow .25s;
    margin-bottom: 20px;
    border: 1px solid #f0e8ed;
  }
  .product-card:hover { transform: translateY(-5px); box-shadow: 0 12px 36px rgba(0,0,0,.13); }

  .product-img-wrap { position: relative; overflow: hidden; }
  .product-img-wrap img { width: 100%; height: 220px; object-fit: cover; transition: transform .4s; }
  .product-card:hover .product-img-wrap img { transform: scale(1.06); }

  .badge {
    position: absolute; top: 10px; left: 10px;
    background: #e91e8c; color: #fff;
    padding: 3px 10px; border-radius: 20px;
    font-size: .75em; font-weight: 700;
  }
  .badge-featured {
    position: absolute; top: 10px; right: 10px;
    background: #0f3460; color: #f5c6d0;
    padding: 3px 10px; border-radius: 20px;
    font-size: .72em; font-weight: 600;
  }

  .product-info { padding: 14px 16px 18px; }
  .product-name {
    font-family: 'Playfair Display', serif;
    font-size: 1.02em; font-weight: 600;
    color: #1a1a2e; margin: 0 0 6px;
    line-height: 1.35;
  }
  .stars { color: #f4a423; font-size: .85em; margin-bottom: 6px; }
  .price-wrap { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
  .price-now { font-size: 1.15em; font-weight: 700; color: #c2185b; }
  .price-was { font-size: .88em; color: #aaa; text-decoration: line-through; }
  .discount { font-size: .8em; color: #e91e8c; font-weight: 600; }

  /* ── Buttons ── */
  .btn-cart {
    background: linear-gradient(135deg, #e91e8c, #c2185b);
    color: #fff !important; border: none;
    width: 100%; padding: 9px 0; border-radius: 8px;
    font-size: .9em; font-weight: 600; cursor: pointer;
    letter-spacing: .5px; margin-bottom: 6px;
  }
  .btn-outline {
    background: transparent; color: #c2185b !important;
    border: 1.5px solid #c2185b; width: 100%; padding: 7px 0;
    border-radius: 8px; font-size: .9em; font-weight: 600; cursor: pointer;
  }

  /* ── Section headers ── */
  .section-title {
    font-family: 'Playfair Display', serif;
    font-size: 2em; color: #1a1a2e; text-align: center;
    margin-bottom: 6px;
  }
  .section-sub {
    text-align: center; color: #888; margin-bottom: 30px;
    font-size: .95em; letter-spacing: .5px;
  }
  .divider { border: none; border-top: 2px solid #f5c6d0; margin: 30px auto; width: 80px; }

  /* ── Category pills ── */
  .cat-strip { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 24px; justify-content: center; }
  .cat-pill {
    background: #f9f0f4; color: #c2185b; border: 1.5px solid #f5c6d0;
    border-radius: 50px; padding: 6px 20px; font-size: .88em;
    font-weight: 600; cursor: pointer; transition: all .2s;
  }
  .cat-pill:hover, .cat-pill.active { background: #c2185b; color: #fff; border-color: #c2185b; }

  /* ── Cart sidebar ── */
  .cart-item {
    background: #fdf6f9; border-radius: 10px;
    padding: 10px 12px; margin-bottom: 8px;
    border: 1px solid #f0e4ec;
  }
  .cart-item-name { font-weight: 600; font-size: .92em; color: #1a1a2e; }
  .cart-item-price { color: #c2185b; font-weight: 700; }

  /* ── Footer ── */
  .footer {
    background: #1a1a2e; color: #d4a5b5;
    text-align: center; padding: 32px 20px;
    margin-top: 50px; border-radius: 16px 16px 0 0;
  }
  .footer h3 { font-family: 'Playfair Display', serif; color: #f5c6d0; margin-bottom: 8px; }
  .footer a { color: #f5c6d0; text-decoration: none; margin: 0 12px; }
  .footer a:hover { text-decoration: underline; }

  /* ── Toast ── */
  .stAlert { border-radius: 12px !important; }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] { background: #fdf6f9 !important; }
  [data-testid="stSidebar"] .stMarkdown h2 {
    font-family: 'Playfair Display', serif; color: #c2185b;
  }
</style>
""",
    unsafe_allow_html=True,
)

# ── Session state ─────────────────────────────────────────────────────────────
if "cart" not in st.session_state:
    st.session_state.cart = []
if "view" not in st.session_state:
    st.session_state.view = "shop"
if "selected_product" not in st.session_state:
    st.session_state.selected_product = None
if "checkout_done" not in st.session_state:
    st.session_state.checkout_done = False


def add_to_cart(product):
    for item in st.session_state.cart:
        if item["id"] == product["id"]:
            item["qty"] += 1
            return
    st.session_state.cart.append({**product, "qty": 1})


def cart_count():
    return sum(i["qty"] for i in st.session_state.cart)


def cart_total():
    return sum(i["price"] * i["qty"] for i in st.session_state.cart)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💎 Love Earrings")
    st.markdown("---")

    # Navigation
    st.markdown("### Navigation")
    nav = st.radio(
        "",
        ["🏠 Home", "🛍️ Shop All", "🛒 Cart"],
        index=0,
        label_visibility="collapsed",
    )
    if nav == "🏠 Home":
        st.session_state.view = "home"
    elif nav == "🛍️ Shop All":
        st.session_state.view = "shop"
    elif nav == "🛒 Cart":
        st.session_state.view = "cart"

    st.markdown("---")

    # Filters (visible on shop view)
    st.markdown("### Filter Products")

    all_products = load_products()
    categories = ["All"] + sorted({p["category"] for p in all_products})
    selected_cat = st.selectbox("Category", categories)

    all_colors = sorted({c for p in all_products for c in p.get("colors", [])})
    selected_color = st.selectbox("Color", ["All"] + all_colors)

    prices = [p["price"] for p in all_products]
    price_range = st.slider(
        "Price Range ($)",
        min_value=float(min(prices)),
        max_value=float(max(prices)),
        value=(float(min(prices)), float(max(prices))),
        step=1.0,
    )

    sort_by = st.selectbox(
        "Sort By", ["Featured", "Price: Low to High", "Price: High to Low", "Top Rated"]
    )

    st.markdown("---")
    st.markdown(f"### 🛒 Cart ({cart_count()} items)")
    if st.session_state.cart:
        for item in st.session_state.cart:
            st.markdown(
                f"""<div class="cart-item">
                <div class="cart-item-name">{item['name']}</div>
                <div class="cart-item-price">${item['price']:.2f} × {item['qty']}</div>
            </div>""",
                unsafe_allow_html=True,
            )
        st.markdown(f"**Total: ${cart_total():.2f}**")
        if st.button("🛒 Checkout", use_container_width=True):
            st.session_state.view = "cart"
    else:
        st.caption("Your cart is empty")


# ── Filter & sort helper ──────────────────────────────────────────────────────
def apply_filters(products):
    filtered = products
    if selected_cat != "All":
        filtered = [p for p in filtered if p["category"] == selected_cat]
    if selected_color != "All":
        filtered = [p for p in filtered if selected_color in p.get("colors", [])]
    filtered = [
        p for p in filtered if price_range[0] <= p["price"] <= price_range[1]
    ]
    if sort_by == "Price: Low to High":
        filtered.sort(key=lambda x: x["price"])
    elif sort_by == "Price: High to Low":
        filtered.sort(key=lambda x: x["price"], reverse=True)
    elif sort_by == "Top Rated":
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
            '<span class="badge-featured">✦ Featured</span>'
            if p.get("featured")
            else ""
        )
        orig_html = (
            f'<span class="price-was">${p["original_price"]:.2f}</span>'
            if p.get("original_price")
            else ""
        )
        disc_html = (
            f'<span class="discount">{discount}% OFF</span>' if discount else ""
        )

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
                st.success(f"Added to cart!", icon="✅")
        with c2:
            if st.button("👁️ View", key=f"view_{p['id']}", use_container_width=True):
                st.session_state.selected_product = p
                st.session_state.view = "detail"
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# VIEW: HOME
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.view == "home":
    # Hero
    st.markdown(
        """
<div class="hero">
  <h1>Love Earrings</h1>
  <p>Discover handcrafted earrings made for every moment of your life</p>
</div>""",
        unsafe_allow_html=True,
    )

    # Categories strip
    st.markdown(
        """
<div class="cat-strip">
  <span class="cat-pill">💛 Studs</span>
  <span class="cat-pill">⭕ Hoops</span>
  <span class="cat-pill">🌊 Drops</span>
  <span class="cat-pill">✨ Chandeliers</span>
  <span class="cat-pill">🌀 Dangles</span>
</div>""",
        unsafe_allow_html=True,
    )

    # Featured products
    st.markdown('<h2 class="section-title">✦ Featured Collection</h2>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Handpicked favourites loved by thousands</p>', unsafe_allow_html=True)

    all_products = load_products()
    featured = [p for p in all_products if p.get("featured")][:6]

    cols = st.columns(3)
    for i, p in enumerate(featured):
        render_product_card(p, cols[i % 3])

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Value props
    st.markdown('<h2 class="section-title">Why Love Earrings?</h2>', unsafe_allow_html=True)
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
                <div style="font-family:'Playfair Display',serif;font-weight:600;color:#1a1a2e;margin:8px 0 4px">{title}</div>
                <div style="color:#888;font-size:.88em">{desc}</div>
            </div>""",
                unsafe_allow_html=True,
            )

    # Shop now button
    st.markdown("<br>", unsafe_allow_html=True)
    _, mid, _ = st.columns([2, 1, 2])
    with mid:
        if st.button("🛍️ Shop All Earrings", use_container_width=True):
            st.session_state.view = "shop"
            st.rerun()

    # Footer
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
    st.markdown('<h2 class="section-title">🛍️ All Earrings</h2>', unsafe_allow_html=True)

    # Search bar
    search = st.text_input("🔍 Search earrings...", placeholder="e.g. gold hoop, pearl stud...")
    all_products = load_products()

    if search:
        q = search.lower()
        all_products = [
            p
            for p in all_products
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


# ─────────────────────────────────────────────────────────────────────────────
# VIEW: PRODUCT DETAIL
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.view == "detail":
    p = st.session_state.selected_product
    if not p:
        st.session_state.view = "shop"
        st.rerun()

    if st.button("← Back to Shop"):
        st.session_state.view = "shop"
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    img_col, info_col = st.columns([1, 1])

    with img_col:
        st.image(p["image"], use_container_width=True)

    with info_col:
        discount = 0
        if p.get("original_price", 0) > p["price"]:
            discount = int((1 - p["price"] / p["original_price"]) * 100)
        stars = "★" * int(p.get("rating", 0)) + "☆" * (5 - int(p.get("rating", 0)))

        st.markdown(
            f"""
<h1 style="font-family:'Playfair Display',serif;color:#1a1a2e;font-size:2em">{p['name']}</h1>
<div style="color:#f4a423;font-size:1.1em">{stars}
  <span style="color:#999;font-size:.85em">({p.get('reviews',0)} reviews)</span>
</div>
<br>
<div style="display:flex;align-items:center;gap:14px">
  <span style="font-size:2em;font-weight:700;color:#c2185b">${p['price']:.2f}</span>
  {'<span style="text-decoration:line-through;color:#aaa;font-size:1.2em">$' + f"{p['original_price']:.2f}" + '</span>' if p.get('original_price') else ''}
  {'<span style="background:#e91e8c;color:#fff;padding:3px 12px;border-radius:20px;font-size:.85em;font-weight:700">' + str(discount) + '% OFF</span>' if discount else ''}
</div>
<br>
<p style="color:#555;line-height:1.7">{p.get('description','')}</p>
<br>
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

        qty = st.number_input("Quantity", min_value=1, max_value=min(p.get("stock", 1), 10), value=1)

        a1, a2 = st.columns(2)
        with a1:
            if st.button("🛒 Add to Cart", use_container_width=True, type="primary"):
                for _ in range(qty):
                    add_to_cart(p)
                st.success(f"Added {qty} × {p['name']} to cart!")
        with a2:
            if st.button("💗 Buy Now", use_container_width=True):
                for _ in range(qty):
                    add_to_cart(p)
                st.session_state.view = "cart"
                st.rerun()

    st.markdown("---")
    st.markdown("### You Might Also Like")
    all_products = load_products()
    related = [
        x
        for x in all_products
        if x["category"] == p["category"] and x["id"] != p["id"]
    ][:3]
    if related:
        cols = st.columns(3)
        for i, rp in enumerate(related):
            render_product_card(rp, cols[i])


# ─────────────────────────────────────────────────────────────────────────────
# VIEW: CART
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.view == "cart":
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
                        st.image(item["image"], width=80)
                    with nc:
                        st.markdown(f"**{item['name']}**")
                        st.caption(f"Category: {item.get('category','')}")
                    with pc:
                        new_qty = st.number_input(
                            "Qty", min_value=1, max_value=10,
                            value=item["qty"], key=f"qty_{idx}"
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
  <h3 style="font-family:'Playfair Display',serif;color:#1a1a2e;margin-bottom:18px">Order Summary</h3>
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
                            {"id": i["id"], "name": i["name"], "price": i["price"], "qty": i["qty"]}
                            for i in st.session_state.cart
                        ],
                        "total": total,
                    })
                    st.session_state.checkout_done = True
                    st.rerun()
