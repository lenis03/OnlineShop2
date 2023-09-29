from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
import pytz

from accounts.models import OtpCode


class Command(BaseCommand):
    help = 'remove all expired opt codes'

    def handle(self, *args, **options):
        expired_time = datetime.now(tz=pytz.timezone('Asia/Tehran')) - timedelta(minutes=2)
        OtpCode.objects.filter(created__lt=expired_time).delete()
        self.stdout.write('All expired otp codes removed!')
