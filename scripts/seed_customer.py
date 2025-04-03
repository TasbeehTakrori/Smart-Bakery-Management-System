# scripts/seed_customers.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from config import SessionLocal
from models.customer import Customer

def ensure_unknown_customer_exists(session: Session):
    existing = session.query(Customer).filter(Customer.name == "زبون غير معروف").first()
    if not existing:
        unknown = Customer(name="زبون غير معروف", email=None, phone=None)
        session.add(unknown)
        session.commit()
        print("✅ تمت إضافة الزبون غير المعروف.")
    else:
        print("ℹ️ الزبون غير المعروف موجود مسبقًا.")

def seed_customers():
    session: Session = SessionLocal()
    try:
        ensure_unknown_customer_exists(session)

        demo_customers = [
            {"name": "سارة أحمد", "email": "sara@example.com", "phone": "0599999991"},
            {"name": "محمد خالد", "email": "mohammad@example.com", "phone": "0599999992"},
            {"name": "ليلى عماد", "email": "laila@example.com", "phone": "0599999993"},
        ]

        for data in demo_customers:
            exists = session.query(Customer).filter(Customer.name == data["name"]).first()
            if not exists:
                customer = Customer(**data)
                session.add(customer)

        session.commit()
        print("✅ تمت إضافة الزبائن بنجاح.")
    finally:
        session.close()

if __name__ == "__main__":
    seed_customers()