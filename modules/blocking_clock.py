import logging
from data import db_session
from apscheduler.schedulers.blocking import BlockingScheduler
from misc.session_scheduler import delete_film_session_every_week

sched = BlockingScheduler({'apscheduler.timezone': 'UTC'})

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')


# @sched.scheduled_job('interval', hours=24)
@sched.scheduled_job('cron', day_of_week='tue,fri', hour='15')
def clear_session_table_blocking():
    logging.info('Log before connect to database')
    if db_session.__factory is None:
        db_session.global_init('connect_to_db_in_db_session_file')
    delete_film_session_every_week()


sched.start()
