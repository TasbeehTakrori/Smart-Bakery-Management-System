from config import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from models.order import Order

def calculate_avg_daily_sales(product_id, days_window=7):
    session: Session = SessionLocal()
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=days_window)

    total_qty = session.query(func.sum(Order.quantity))\
        .filter(Order.product_id == product_id)\
        .filter(Order.order_date >= start_date)\
        .scalar() or 0

    avg_sales = total_qty / days_window
    session.close()
    return avg_sales



def get_latest_order_date(product_id):
    session = SessionLocal()
    latest = session.query(Order).filter(Order.product_id == product_id).order_by(Order.order_date.desc()).first()
    session.close()
    return latest.order_date if latest else None