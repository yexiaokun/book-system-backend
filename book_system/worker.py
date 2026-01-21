import time
from celery import Celery


celery_app = Celery(
    "tasks",
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/0"
)


@celery_app.task
def generate_pdf_and_send_email(book_title: str):
    print(f"📄 [后台] 开始为《{book_title}》生成 PDF...")
    time.sleep(5)
    print(f"📧 [后台] PDF 生成完毕，邮件已发送给用户！")
    return "Mission Complete"

@celery_app.task
def log_operation(msg: str):
    time.sleep(3)
    print(f"书《{msg}》已归还")
    return "Mission Complete"