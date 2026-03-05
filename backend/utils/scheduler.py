from apscheduler.schedulers.background import BackgroundScheduler
from database import db
from datetime import datetime

def start_scheduler(app):
    scheduler = BackgroundScheduler()

    def expire_bookings():
        now = datetime.now()
        for b in db['bookings']:
            if b['status'] == 'Active' and b['end_time'] < now:
                b['status'] = 'Expired'
                # find slot
                for s in db['slots']:
                    if s['id'] == b['slot_id']:
                        s['status'] = 'Available'
                        break

    scheduler.add_job(expire_bookings, 'interval', minutes=1)
    scheduler.start()
