from main.views import check_deadman_switch
from apscheduler.schedulers.blocking import BlockingScheduler
from main.logic import check_modules_release
sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=1440)
def run_deadman():
    check_deadman_switch()
    check_modules_release()

sched.start()