from django.core.management.base import BaseCommand

from django.contrib.auth.models import Group
from loan.models import *

class Command(BaseCommand):
    help = 'Clean data into the database'

    def handle(self, *args, **kwargs):        
        UserBox.objects.filter().delete()
        CompanyBox.objects.filter().delete()
        Box.objects.filter().delete()
        IndividualBox.objects.filter().delete()
        RechargePersonalBox.objects.filter().delete()
      