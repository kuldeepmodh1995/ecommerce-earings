import json
import os
import uuid
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")
ORDERS_FILE = os.path.join(DATA_DIR, "orders.json")


def load_products():
    if not os.path.exists(PRODUCTS_FILE):
        return []
    with open(PRODUCTS_FILE, "r") as f:
        return json.load(f)


def save_products(products):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(products, f, indent=2)


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
