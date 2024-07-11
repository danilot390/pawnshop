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
        Pledge.objects.filter().delete()
        
        self.stdout.write(self.style.SUCCESS('The UserBox table it was clean successfull.'))
        self.stdout.write(self.style.SUCCESS('The CompanyBox table it was clean successfull.'))
        self.stdout.write(self.style.SUCCESS('The Box table it was clean successfull.'))
        self.stdout.write(self.style.SUCCESS('The IndividualBox table it was clean successfull.'))
        self.stdout.write(self.style.SUCCESS('The RechargePersonalBox table it was clean successfull.'))
        self.stdout.write(self.style.SUCCESS('The Pledge table it was clean successfull.'))
      