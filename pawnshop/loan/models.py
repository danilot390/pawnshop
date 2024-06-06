from django.db import models
from django.contrib.auth.models import AbstractUser

class Company(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField( max_length=100)
    slug = models.CharField( max_length=10)
    slang = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Person(models.Model):
    id = models.AutoField(primary_key=True)
    ci = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=150)
    address = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)

    def get_full_name(self):
        return self.name + ' ' + self.last_name

class User(AbstractUser):
    person = models.ForeignKey("Person", on_delete=models.PROTECT, related_name='user', null=True)
    company = models.ForeignKey("Company", on_delete=models.CASCADE, related_name='employees', null=True)
    password = models.CharField( max_length=250)
    last_login = models.CharField( max_length=150)
    is_superuser = models.BooleanField(default=False)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ['person', 'email', 'password']

class Pledge(models.Model):
    id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='pledges'
    )
    client = models.ForeignKey(
        'Person',
        on_delete=models.CASCADE,
        related_name='pledges'
    )
    company = models.ForeignKey("Company", on_delete=models.CASCADE, related_name='pledges')
    article = models.CharField(max_length=50)
    type = models.CharField(max_length=30)
    description = models.TextField()
    loan_date = models.DateField()
    rescue_date = models.DateField()
    renewal_date = models.DateField(null=True, blank=True)
    loan = models.PositiveIntegerField()
    interest = models.PositiveIntegerField()
    arrears = models.PositiveIntegerField(default=0)
    estimated_value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class OtherContract(models.Model):
    id = models.AutoField(primary_key=True)
    BUY_SELL = 'BS'
    DEBT_RECOGNITION = 'DR'
    TYPE_OF_CONTRACT_CHOICES = [
        (BUY_SELL, 'Buy and sell'),
        (DEBT_RECOGNITION, 'Debt recognition')
    ]
    pledge = models.ForeignKey(
        'Pledge',
        on_delete=models.CASCADE,
        related_name='contracts'
    )
    contract_type = models.CharField(max_length=2, choices=TYPE_OF_CONTRACT_CHOICES)
    currency = models.CharField(default='$US', max_length=10)
    initial_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Box(models.Model):
    id = models.AutoField(primary_key=True)
    INPUT = 'IN'
    OUTPUT = 'OUT'
    TYPE_TRANSACTION_CHOICES = [
        (INPUT, 'Input'),
        (OUTPUT, 'Output'),
    ]

    company = models.ForeignKey("Company", on_delete=models.CASCADE, related_name='box')
    employee = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='transactions'
    )
    amount = models.PositiveIntegerField()
    type = models.CharField(max_length=3, choices=TYPE_TRANSACTION_CHOICES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Paid(Box):
    RESCUE = 'RS'
    RENEWAL = 'RN'
    PURCHASE = 'PC'
    TYPE_OF_PAID = [
        (RESCUE, 'Rescue'),
        (RENEWAL, 'Renewal'),
        (PURCHASE, 'Purchase')
    ]
    pledge = models.ForeignKey(
        'Pledge',
        on_delete=models.CASCADE,
        related_name='paids'
    )
    type_paid = models.CharField(max_length=2, choices=TYPE_OF_PAID)

class RechargePersonalBox(Box):
    receiver = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='Recharges'
    )

class PersonalBox(models.Model):
    id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='personal_boxes'
    )
    in_week_amount = models.PositiveIntegerField(default=0)
    out_week_amount = models.PositiveIntegerField(default=0)
    week_amount = models.PositiveIntegerField(default=0)
    in_global_amount = models.PositiveIntegerField(default=0)
    out_global_amount = models.PositiveIntegerField(default=0)
    global_amount = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class BlackList(models.Model):
    id = models.AutoField(primary_key=True)
    client = models.ForeignKey(
        'Person',
        on_delete=models.CASCADE,
        related_name='blacklists'
    )
    company = models.ForeignKey("Company", on_delete=models.CASCADE, related_name='black_list')
    reason = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class VehicleInspection(models.Model):
    id = models.AutoField(primary_key=True)
    pledge = models.ForeignKey(
        'Pledge',
        on_delete=models.CASCADE,
        related_name='inspections'
    )
    plate = models.CharField(max_length=50)
    chassis = models.CharField(max_length=50)
    motor = models.CharField(max_length=50)
    motor_status = models.TextField()
    bodywork_status = models.TextField()
    taxes = models.DecimalField(max_digits=15, decimal_places=2)
    infractions = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
