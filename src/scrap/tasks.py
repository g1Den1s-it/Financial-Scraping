from datetime import timedelta, datetime
import asyncio
import logging
import logging.config

from src.scrap.celery import celery_app
from src.log_conf import CELERY_LOGGING_CONFIG

from src.scrap.financial_parser import FinancialParser
from src.database import get_db_session
from src.scrap.services import create_post

logging.config.dictConfig(CELERY_LOGGING_CONFIG)

logger = logging.getLogger('celery_app')


@celery_app.on_after_finalize.connect
def init_parser(sender, **kwarg):
    try:
        asyncio.run(scrap_task_once())

    except RuntimeError as e:
        logger.error(f"Failed to trigger scrap_task_once in on_after_finalize: {e}")
    except Exception as e:
        logger.error(f"Unexpected error when triggering scrap_task_once: {e}")


@celery_app.task(is_async=True)
async def scrap_hourly_task():
    logger.info("Starting fetch data by one hour.")

    finan = FinancialParser()

    logger.log("Scraping...")

    await finan.parsing(timedelta(hours=1))

    data = await finan.pars_post_data()

    logger.info(f"DONE! Fetched: {len(data)} post")

    logger.info("Starting save data in database...")

    async for session in get_db_session():
        for post in data:
            await create_post(post, session)


    return {"status": "done", "scraped_at": datetime.utcnow()}
    


@celery_app.task(is_async=True)
async def scrap_task_once():
    logger.info("Starting scraping month financial time posts.")

    finan = FinancialParser()
    
    logger.info("Scraping...")
    
    await finan.parsing(timedelta(days=1))
    
    logger.info("fetch data from post")
    
    data = await finan.pars_post_data()
    
    logger.info(f"DONE! Fetched: {len(data)} post")

    logger.info("Starting save data in database...")


    async for session in get_db_session():
        for post in data:
            await create_post(post, session)

    return {"status": "done", "scraped_at": datetime.utcnow()}
