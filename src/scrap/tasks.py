from datetime import timedelta
import asyncio

from src.scrap.celery import celery_app

from src.scrap.financial_parser import FinancialParser


@celery_app.on_after_finalize.connect
def init_parser(sender, **kwarg):
    scrap_task_once.delay()


@celery_app.task(is_async=True)
async def scrap_hourly_task():
    finan = FinancialParser()

    await finan.parsing(timedelta(hours=1))

    data = await finan.parsing_data()

    return {"status": "done", "scraped_at": datetime.datetime.utcnow()}
    


@celery_app.task(is_async=True)
async def scrap_task_once():
    finan = FinancialParser()

    await finan.parsing(timedelta(days=30))

    data = await finan.parsing_data()

    return {"status": "done", "scraped_at": datetime.datetime.utcnow()}
