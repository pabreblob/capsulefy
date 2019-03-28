from django.core.management.base import BaseCommand, CommandError
from main.views import check_deadman_switch

from apscheduler.schedulers.blocking import BlockingScheduler
from main.logic import check_modules_release
import requests
from capsulefyweb import  settings
sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=10)
def run_deadman():
    url=settings.BASEURL
    requests.get(url+'rundeadman/')
    check_modules_release()

sched.start()