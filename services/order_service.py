from models.order import Order
from models.product import Product
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload


def get_actual_orders_per_day(product_id: int, start_date, end_date):
    session = SessionLocal()
    orders = (
        session.query(
            Order.order_date.label("ds"),
            func.sum(Order.quantity).label("actual")
        )
        .filter(Order.product_id == product_id)
        .filter(Order.order_date >= start_date)
        .filter(Order.order_date <= end_date)
        .group_by(Order.order_date)
        .all()
    )
    session.close()

    df = pd.DataFrame(orders, columns=["ds", "actual"])
    df["ds"] = pd.to_datetime(df["ds"])
    return df

def get_recent_orders(days=None, limit=None):
    session = SessionLocal()

    query = session.query(Order).options(
        joinedload(Order.product),  # تحميل علاقة المنتج
        joinedload(Order.customer)  # تحميل علاقة الزبون
    )

    if days is not None:
        cutoff = datetime.now() - timedelta(days=days)
        query = query.filter(Order.order_date >= cutoff)

    query = query.order_by(Order.order_date.desc())

    if limit is not None:
        query = query.limit(limit)

    orders = query.all()

    results = []
    for o in orders:
        results.append({
            "id": o.id,
            "product_id": o.product_id,
            "product_name": o.product.name if o.product else "غير معروف",
            "quantity": o.quantity,
            "customer_name": o.customer.name if o.customer else "غير معروف",
            "order_date": o.order_date
        })

    session.close()
    return results

def get_order_counts_by_product():
    session = SessionLocal()

    results = (
        session.query(
            Product.id.label("product_id"),
            Product.name.label("product_name"),
            func.count(Order.id).label("order_count")
        )
        .join(Order, Product.id == Order.product_id)
        .group_by(Product.id)
        .all()
    )

    session.close()

    return [
        {
            "product_id": row.product_id,
            "name": row.product_name,
            "orders": row.order_count
        }
        for row in results
    ]


from models.order import Order
from models.customer import Customer
from config import SessionLocal
from sqlalchemy import func

def get_repeat_customers(min_orders=2):
    session = SessionLocal()

    results = (
        session.query(
            Customer.name,
            func.count(Order.id).label("orders")
        )
        .join(Order, Customer.id == Order.customer_id)
        .group_by(Customer.id)
        .having(func.count(Order.id) >= min_orders)
        .all()
    )

    session.close()

    return [{"name": r.name, "orders": r.orders} for r in results]

def add_order(order_data):
    session = SessionLocal()
    try:
        customer_id = order_data.get("customer_id")
        if not customer_id:
            unknown = session.query(Customer).filter(Customer.name == "زبون غير معروف").first()
            customer_id = unknown.id if unknown else None

        new_order = Order(
            product_id=order_data["product_id"],
            quantity=order_data["quantity"],
            customer_id=customer_id,
            order_date=order_data.get("order_date", datetime.utcnow())
        )
        session.add(new_order)
        session.commit()
    finally:
        session.close()

from models.order import Order
from config import SessionLocal
from sqlalchemy import func

def get_latest_order_date(product_id: int):
    session = SessionLocal()

    latest_date = (
        session.query(func.max(Order.order_date))
        .filter(Order.product_id == product_id)
        .scalar()
    )

    session.close()
    return latest_date


def get_total_quantity_by_product():
    session = SessionLocal()
    results = (
        session.query(Order.product_id, func.sum(Order.quantity).label("total_quantity"))
        .group_by(Order.product_id)
        .all()
    )
    session.close()
    return [{"product_id": r.product_id, "total_quantity": r.total_quantity} for r in results]

def get_order_counts_per_day(last_days=7):
    session = SessionLocal()
    since_date = datetime.now() - timedelta(days=last_days)
    results = (
        session.query(func.date(Order.order_date).label("day"), func.count(Order.id))
        .filter(Order.order_date >= since_date)
        .group_by(func.date(Order.order_date))
        .order_by(func.date(Order.order_date))
        .all()
    )
    session.close()

    return [{"day": r[0].strftime("%Y-%m-%d"), "count": r[1]} for r in results]
