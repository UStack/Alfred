from apscheduler.schedulers.background import BackgroundScheduler


_scheduler = BackgroundScheduler()


def add_job(*args, **kwargs):
    _scheduler.add_job(*args, **kwargs)

_scheduler.start()
