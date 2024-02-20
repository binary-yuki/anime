import logging
import os
import time
from utils.operator import async_task_get_list_list
from celery import Celery

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


@celery.task(name="create_query_task")  # name defines the task name
def create_query_task(ids: list):
    """
    :param ids: Video id list
    """
    try:
        logging.info("Task started")
        logging.debug(f"ids: {ids}")
        logging.info(f"type(ids): {type(ids)}")
        if type(ids) is str:
            ls = [ids]
        else:
            ls = ids
        results = async_task_get_list_list(ls)
        return results
    except Exception as e:
        # log the exception
        logging.error("Error occurred:", exc_info=True)
        print("Error occurred:", e)
        # re-raise the exception
        raise


@celery.task(name="create_task")  # name defines the task name
def create_task(task_type: int):
    """
    :param task_type: Task type
    """
    time.sleep(5)
    return {"task_type": task_type, "status": "completed"}

