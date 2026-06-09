from apscheduler.schedulers.background import BackgroundScheduler
from services.pay_func import close_expired_payments
from database import SessionLocal
from utils.logger import get_logger

logger = get_logger("scheduler")


def close_expired_payments_task():
    """定时任务：关闭过期支付记录"""
    db = SessionLocal()
    try:
        result = close_expired_payments(db)
        logger.info(f"定时任务执行结果: {result}")
    except Exception as e:
        logger.error(f"定时任务执行失败: {str(e)}")
    finally:
        db.close()


def init_scheduler():
    """初始化定时任务调度器"""
    scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
    
    # 添加定时任务：每5分钟执行一次
    scheduler.add_job(
        close_expired_payments_task,
        "interval",
        minutes=5,
        id="close_expired_payments",
        replace_existing=True
    )
    
    # 启动调度器
    scheduler.start()
    logger.info("定时任务调度器已启动，每5分钟检查并关闭过期支付记录")
    
    return scheduler