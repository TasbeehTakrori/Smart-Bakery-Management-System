from models.checkpoint_conditions import CheckpointCondition
from config import SessionLocal
import pandas as pd

def get_latest_checkpoint_values(default_value=1):
    session = SessionLocal()
    try:
        latest = (
            session.query(CheckpointCondition)
            .order_by(CheckpointCondition.date.desc())
            .first()
        )

        if latest is None:
            raise ValueError("No checkpoint data found")

        return {
            "cp_1": latest.cp_1,
            "cp_2": latest.cp_2,
            "cp_3": latest.cp_3,
            "cp_4": latest.cp_4,
            "cp_5": latest.cp_5,
        }
    except Exception as e:
        print(f"⚠️ لم يتمكن من جلب الحواجز: {e}")
        return {f"cp_{i}": default_value for i in range(1, 6)}
    finally:
        session.close()

from models.checkpoint_conditions import CheckpointCondition
from config import SessionLocal
from datetime import datetime, timedelta
import pandas as pd

def get_checkpoint_conditions_last_n_days(days=7):
    """
    تُرجع DataFrame فيه قيم الحواجز من اليوم الحالي إلى (اليوم - days).
    """
    session = SessionLocal()
    try:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days - 1)

        results = (
            session.query(CheckpointCondition)
            .filter(CheckpointCondition.date >= start_date)
            .filter(CheckpointCondition.date <= end_date)
            .order_by(CheckpointCondition.date)
            .all()
        )

        if not results:
            print("⚠️ لا توجد بيانات حواجز في آخر", days, "يوم.")
            return pd.DataFrame()

        df = pd.DataFrame([{
            "ds": r.date,
            "cp_1": r.cp_1,
            "cp_2": r.cp_2,
            "cp_3": r.cp_3,
            "cp_4": r.cp_4,
            "cp_5": r.cp_5
        } for r in results])
        df["ds"] = pd.to_datetime(df["ds"])
        return df

    except Exception as e:
        print(f"❌ خطأ في جلب بيانات الحواجز: {e}")
        return pd.DataFrame()
    finally:
        session.close()

def get_checkpoint_conditions_range(start_date, end_date):
    """
    تُرجع DataFrame فيه القيم اليومية للحواجز بين تاريخين.
    """
    session = SessionLocal()
    try:
        results = (
            session.query(CheckpointCondition)
            .filter(CheckpointCondition.date >= start_date)
            .filter(CheckpointCondition.date <= end_date)
            .all()
        )

        if not results:
            print("⚠️ لا توجد بيانات حواجز في الفترة المطلوبة.")
            return pd.DataFrame()

        # تحويل إلى DataFrame
        df = pd.DataFrame([{
            "ds": r.date,
            "cp_1": r.cp_1,
            "cp_2": r.cp_2,
            "cp_3": r.cp_3,
            "cp_4": r.cp_4,
            "cp_5": r.cp_5
        } for r in results])
        df["ds"] = pd.to_datetime(df["ds"])
        return df

    except Exception as e:
        print(f"❌ خطأ في جلب بيانات الحواجز: {e}")
        return pd.DataFrame()
    finally:
        session.close()