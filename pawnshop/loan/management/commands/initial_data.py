from django.core.management.base import BaseCommand

from django.contrib.auth.models import Group
from loan.models import *

class Command(BaseCommand):
    help = 'Load initial data into the database'

    def handle(self, *args, **kwargs):
        #  Create Roles
        rol_admin = Group.objects.get_or_create(name='Admin')
        rol_employee = Group.objects.get_or_create(name='Employee')
        self.stdout.write(self.style.SUCCESS('Admin & Employee rols are avaible.'))
        
        # Create person
        ci = '3w45644'
        name = 'Juancito'
        last_name = 'Pinto'
        address = 'ballybough rd'
        phone_number = '45664565'
        person = Person.objects.get_or_create(
            ci = ci,
            defaults={'name' : name,
                      'last_name' : last_name,
                      'address' : address,
                      'phone_number' : phone_number,}
        )
        
        ci = '342453-fg'
        name = 'Pedrito'
        last_name = 'Infante'
        address = 'ballybough rd'
        phone_number = '6567789'
        person2 = Person.objects.get_or_create(
            ci = ci,
            defaults={'name' : name,
                      'last_name' : last_name,
                      'address' : address,
                      'phone_number' : phone_number,}
        )
        self.stdout.write(self.style.SUCCESS('Person get or created successfully'))

        # Create Company
        name = 'Smile Capital'
        slug = 'Smiles'
        slang = 'Your smile it is important.'
        company = Company.objects.get_or_create(
            name = name,
            defaults={'slug' : slug,
                      'slang' : slang,}
        )
        self.stdout.write(self.style.SUCCESS('Company get or created successfully'))

        # Create or get a superuser
        username = 'admin'  
        email = 'admin@example.com'  
        password = 'admin'  

        if not User.objects.filter(username=username).exists():
            user = User.objects.create_superuser(username, email, password)
            self.stdout.write(self.style.SUCCESS('Superuser created successfully'))
            
        else:
            user=User.objects.filter(username=username).first()
            self.stdout.write(self.style.SUCCESS('Superuser already exists'))
        user.groups.add(rol_admin[0])
        user.person = person[0]
        user.company = company[0]
        user.save()
        # Create or get a employee
        username = 'worker'  
        email = 'worker@example.com'  
        password = '1234'  

        if not User.objects.filter(username=username).exists():
            user2 = User.objects.create_superuser(username, email, password)
            self.stdout.write(self.style.SUCCESS('Superuser created successfully'))
        else:
            user2=User.objects.filter(username=username).first()
            self.stdout.write(self.style.SUCCESS('Superuser already exists'))
        user2.groups.add(rol_employee[0])
        user2.person = person2[0]
        user2.company = company[0]
        
        user2.save()


