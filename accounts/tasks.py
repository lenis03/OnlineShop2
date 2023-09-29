from celery import shared_task
from datetime import datetime, timedelta
import pytz

from accounts.models import OtpCode


@shared_task
def remove_expired_otps_task():
    expired_time = datetime.now(tz=pytz.timezone('Asia/Tehran')) - timedelta(minutes=2)
    OtpCode.objects.filter(created__lt=expired_time).delete()
