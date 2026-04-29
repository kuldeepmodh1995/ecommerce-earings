import json
import os
import uuid
from datetime import datetime

import streamlit as st

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")
ORDERS_FILE = os.path.join(DATA_DIR, "orders.json")
NAV_CATEGORIES_FILE = os.path.join(DATA_DIR, "nav_categories.json")
HERO_BANNERS_FILE = os.path.join(DATA_DIR, "hero_banners.json")
SHOP_CATEGORIES_FILE = os.path.join(DATA_DIR, "shop_categories.json")

_DEFAULT_NAV_CATEGORIES = [
    {"id": "nc1", "label": "New Arrivals", "emoji": "✨", "badge": "", "redirect_to": "shop", "sequence": 1, "enabled": True},
    {"id": "nc2", "label": "Best Sellers", "emoji": "🏆", "badge": "", "redirect_to": "shop", "sequence": 2, "enabled": True},
    {"id": "nc3", "label": "Studs", "emoji": "💛", "badge": "", "redirect_to": "category:Studs", "sequence": 3, "enabled": True},
    {"id": "nc4", "label": "Hoops", "emoji": "⭕", "badge": "", "redirect_to": "category:Hoops", "sequence": 4, "enabled": True},
    {"id": "nc5", "label": "Drops", "emoji": "🌊", "badge": "", "redirect_to": "category:Drops", "sequence": 5, "enabled": True},
    {"id": "nc6", "label": "Chandeliers", "emoji": "✨", "badge": "New", "redirect_to": "category:Chandeliers", "sequence": 6, "enabled": True},
    {"id": "nc7", "label": "Dangles", "emoji": "🌀", "badge": "", "redirect_to": "category:Dangles", "sequence": 7, "enabled": True},
    {"id": "nc8", "label": "Gifting", "emoji": "🎁", "badge": "", "redirect_to": "shop", "sequence": 8, "enabled": True},
    {"id": "nc9", "label": "About Us", "emoji": "💎", "badge": "", "redirect_to": "home", "sequence": 9, "enabled": True},
]

_DEFAULT_SHOP_CATEGORIES = [
    {"id": "sc1", "name": "Studs",       "emoji": "💛", "image": "", "redirect_to": "category:Studs",       "sequence": 1, "enabled": True},
    {"id": "sc2", "name": "Hoops",       "emoji": "⭕", "image": "", "redirect_to": "category:Hoops",       "sequence": 2, "enabled": True},
    {"id": "sc3", "name": "Drops",       "emoji": "🌊", "image": "", "redirect_to": "category:Drops",       "sequence": 3, "enabled": True},
    {"id": "sc4", "name": "Chandeliers", "emoji": "✨", "image": "", "redirect_to": "category:Chandeliers", "sequence": 4, "enabled": True},
    {"id": "sc5", "name": "Dangles",     "emoji": "🌀", "image": "", "redirect_to": "category:Dangles",     "sequence": 5, "enabled": True},
    {"id": "sc6", "name": "Gifting",     "emoji": "🎁", "image": "", "redirect_to": "shop",                 "sequence": 6, "enabled": True},
]

_DEFAULT_HERO_BANNERS = [
    {
        "id": "hb1",
        "title": "Discover Handcrafted Earrings",
        "subtitle": "Made for every moment of your life",
        "button_text": "Shop Now",
        "image": "https://images.unsplash.com/photo-1630018548696-e6f716289c97?w=1400&h=600&fit=crop",
        "redirect_to": "shop",
        "sequence": 1,
        "enabled": True,
    },
    {
        "id": "hb2",
        "title": "Featured Collection",
        "subtitle": "Handpicked favourites loved by thousands",
        "button_text": "Explore Now",
        "image": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=1400&h=600&fit=crop",
        "redirect_to": "category:Hoops",
        "sequence": 2,
        "enabled": True,
    },
    {
        "id": "hb3",
        "title": "New Season Arrivals",
        "subtitle": "Fresh styles — just landed",
        "button_text": "Shop New",
        "image": "https://images.unsplash.com/photo-1596944924616-7b38e7cfac36?w=1400&h=600&fit=crop",
        "redirect_to": "category:Studs",
        "sequence": 3,
        "enabled": True,
    },
]


# ── Products ──────────────────────────────────────────────────────────────────

@st.cache_data(ttl=2)
def load_products():
    if not os.path.exists(PRODUCTS_FILE):
        return []
    with open(PRODUCTS_FILE, "r") as f:
        return json.load(f)


def save_products(products):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(products, f, indent=2)
    load_products.clear()


def get_product_by_id(product_id):
    products = load_products()
    return next((p for p in products if p["id"] == product_id), None)


def add_product(product_data):
    products = load_products()
    product_data["id"] = str(uuid.uuid4())[:6].upper()
    product_data["rating"] = product_data.get("rating", 0.0)
    product_data["reviews"] = product_data.get("reviews", 0)
    products.append(product_data)
    save_products(products)
    return product_data["id"]


def update_product(product_id, updated_data):
    products = load_products()
    for i, p in enumerate(products):
        if p["id"] == product_id:
            products[i].update(updated_data)
            save_products(products)
            return True
    return False


def delete_product(product_id):
    products = load_products()
    products = [p for p in products if p["id"] != product_id]
    save_products(products)


# ── Orders ────────────────────────────────────────────────────────────────────

def load_orders():
    if not os.path.exists(ORDERS_FILE):
        return []
    with open(ORDERS_FILE, "r") as f:
        return json.load(f)


def save_order(order_data):
    orders = load_orders()
    order_data["id"] = "ORD-" + str(uuid.uuid4())[:8].upper()
    order_data["created_at"] = datetime.now().isoformat()
    order_data["status"] = "Pending"
    orders.append(order_data)
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)
    return order_data["id"]


def update_order_status(order_id, status):
    orders = load_orders()
    for o in orders:
        if o["id"] == order_id:
            o["status"] = status
            break
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)


def get_stats():
    products = load_products()
    orders = load_orders()
    total_revenue = sum(
        sum(item["price"] * item["qty"] for item in o.get("items", []))
        for o in orders
        if o.get("status") != "Cancelled"
    )
    return {
        "total_products": len(products),
        "total_orders": len(orders),
        "pending_orders": sum(1 for o in orders if o.get("status") == "Pending"),
        "total_revenue": total_revenue,
        "low_stock": [p for p in products if p.get("stock", 0) < 10],
    }


# ── Nav Categories ────────────────────────────────────────────────────────────

def load_nav_categories():
    if not os.path.exists(NAV_CATEGORIES_FILE):
        save_nav_categories(_DEFAULT_NAV_CATEGORIES)
        return list(_DEFAULT_NAV_CATEGORIES)
    with open(NAV_CATEGORIES_FILE, "r") as f:
        return json.load(f)


def save_nav_categories(categories):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(NAV_CATEGORIES_FILE, "w") as f:
        json.dump(categories, f, indent=2)


def add_nav_category(cat_data):
    cats = load_nav_categories()
    cat_data["id"] = "nc" + str(uuid.uuid4())[:6]
    cats.append(cat_data)
    save_nav_categories(cats)
    return cat_data["id"]


def update_nav_category(cat_id, updated):
    cats = load_nav_categories()
    for i, c in enumerate(cats):
        if c["id"] == cat_id:
            cats[i].update(updated)
            save_nav_categories(cats)
            return True
    return False


def delete_nav_category(cat_id):
    cats = load_nav_categories()
    cats = [c for c in cats if c["id"] != cat_id]
    save_nav_categories(cats)


# ── Hero Banners ──────────────────────────────────────────────────────────────

def load_hero_banners():
    if not os.path.exists(HERO_BANNERS_FILE):
        save_hero_banners(_DEFAULT_HERO_BANNERS)
        return list(_DEFAULT_HERO_BANNERS)
    with open(HERO_BANNERS_FILE, "r") as f:
        return json.load(f)


def save_hero_banners(banners):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(HERO_BANNERS_FILE, "w") as f:
        json.dump(banners, f, indent=2)


def add_hero_banner(banner_data):
    banners = load_hero_banners()
    banner_data["id"] = "hb" + str(uuid.uuid4())[:6]
    banners.append(banner_data)
    save_hero_banners(banners)
    return banner_data["id"]


def update_hero_banner(banner_id, updated):
    banners = load_hero_banners()
    for i, b in enumerate(banners):
        if b["id"] == banner_id:
            banners[i].update(updated)
            save_hero_banners(banners)
            return True
    return False


def delete_hero_banner(banner_id):
    banners = load_hero_banners()
    banners = [b for b in banners if b["id"] != banner_id]
    save_hero_banners(banners)


# ── Shop Categories (Homepage "Shop by Category" tiles) ───────────────────────

@st.cache_data(ttl=2)
def load_shop_categories():
    if not os.path.exists(SHOP_CATEGORIES_FILE):
        save_shop_categories(_DEFAULT_SHOP_CATEGORIES)
        return list(_DEFAULT_SHOP_CATEGORIES)
    with open(SHOP_CATEGORIES_FILE, "r") as f:
        return json.load(f)


def save_shop_categories(categories):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SHOP_CATEGORIES_FILE, "w") as f:
        json.dump(categories, f, indent=2)
    load_shop_categories.clear()


def add_shop_category(cat_data):
    cats = load_shop_categories()
    cat_data["id"] = "sc" + str(uuid.uuid4())[:6]
    cats.append(cat_data)
    save_shop_categories(cats)
    return cat_data["id"]


def update_shop_category(cat_id, updated):
    cats = load_shop_categories()
    for i, c in enumerate(cats):
        if c["id"] == cat_id:
            cats[i].update(updated)
            save_shop_categories(cats)
            return True
    return False


def delete_shop_category(cat_id):
    cats = load_shop_categories()
    cats = [c for c in cats if c["id"] != cat_id]
    save_shop_categories(cats)
