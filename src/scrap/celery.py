from celery import Celery
from celery.schedules import crontab


celery_app = Celery('app', broker="redis://redis:6379/0", backend="redis://redis:6379/1")


celery_app.conf.timezone = 'Europe/Kyiv'


celery_app.conf.beat_schedule = {
   'run-hourly-article-update': {
        'task': 'tasks.scrap_hourly_task',
        'schedule': crontab(hour=1),
        'options': {'queue': 'hourly_crawls'},
    },   
}

celery_app.autodiscover_tasks(['src.scrap.tasks'], force=True)
