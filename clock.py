from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler

from misc.session_scheduler import delete_film_session_every_week

# sched = BlockingScheduler({'apscheduler.timezone': 'UTC'})
sched = BackgroundScheduler({'apscheduler.timezone': 'UTC'})


@sched.scheduled_job('interval', hours=24)
def clear_session_table():
    delete_film_session_every_week()


# scheduler.add_job(func=delete_film_session_every_week,
#                   trigger="interval", hours=24)
# scheduler.start()

sched.start()
