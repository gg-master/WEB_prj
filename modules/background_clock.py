from apscheduler.schedulers.background import BackgroundScheduler
from misc.session_scheduler import delete_film_session_every_week


sched = BackgroundScheduler({'apscheduler.timezone': 'UTC'})


# @sched.scheduled_job('interval', hours=24)

@sched.scheduled_job('cron', day_of_week='tue,fri', hour='15')
def clear_session_table_background():
    delete_film_session_every_week()


sched.start()
