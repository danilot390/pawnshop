from django.db import models
from django.contrib.auth.models import AbstractUser

class Company(models.Model):
    owner = models.OneToOneField(
        'Person',
        on_delete=models.CASCADE,
        related_name='owner'
    )
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
    def __str__(self):
        return self.ci +'-'+self.name + ' ' + self.last_name

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
    image = models.ImageField( upload_to=None, height_field=None, width_field=None, max_length=None, null=True, blank=True)
    company = models.ForeignKey("Company", on_delete=models.CASCADE, related_name='pledges')
    article = models.CharField(max_length=50)
    type = models.CharField(max_length=30)
    description = models.TextField()
    loan_date = models.DateField()
    rescue_date = models.DateField()
    renewal_date = models.DateField(null=True, blank=True)
    loan = models.PositiveIntegerField()
    interest = models.PositiveIntegerField()
    balance = models.IntegerField(default=0)
    arrears = models.PositiveIntegerField(default=0)
    estimated_value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def loan_to_interest_ratio(self):
        if self.interest != 0:
            return round(self.balance / self.interest, 0)
        return None 
    
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

    company = models.ForeignKey("Company", on_delete=models.CASCADE, related_name='transactions')
    employee = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='transactions'
    )
    amount = models.PositiveIntegerField()
    type = models.CharField(max_length=3, choices=TYPE_TRANSACTION_CHOICES, null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Paid(models.Model):
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
    box = models.OneToOneField("Box", on_delete=models.CASCADE, related_name='paid_box')
    type_paid = models.CharField(max_length=2, choices=TYPE_OF_PAID)

class RechargePersonalBox(models.Model):
    box = models.OneToOneField("Box", on_delete=models.CASCADE, related_name='recharge_personal_box')
    receiver = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='recharges'
    )

class IndividualBox(models.Model):
    in_week_amount = models.IntegerField(default=0)
    out_week_amount = models.IntegerField(default=0)
    week_amount = models.IntegerField(default=0)
    in_global_amount = models.IntegerField(default=0)
    out_global_amount = models.IntegerField(default=0)
    global_amount = models.IntegerField(default=0)
    start_date = models.DateField( auto_now=False, auto_now_add=False, blank=True, null=True)
    end_date = models.DateField( auto_now=False, auto_now_add=False, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"IndividualBox {self.start_date}"
    
class UserBox(models.Model):
    employee = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='user_boxes',
    )
    individual_box = models.OneToOneField("IndividualBox", 
                                        on_delete=models.PROTECT,
                                        related_name='user_box',
                                        )
    
    def __str__(self):
        return f"UserBox {self.employee.person.get_full_name()} for {self.individual_box}"
    
class CompanyBox(models.Model):
    company = models.ForeignKey("Company", 
                                on_delete=models.CASCADE,
                                related_name='company_boxes',
                                )
    individual_box = models.OneToOneField("IndividualBox", 
                                          on_delete=models.CASCADE,
                                          related_name='company_box',
                                          )
    

class BlackList(models.Model):
    id = models.AutoField(primary_key=True)
    client = models.ForeignKey(
        'Person',
        on_delete=models.CASCADE,
        related_name='blacklist'
    )
    company = models.ForeignKey("Company", on_delete=models.CASCADE, related_name='black_list')
    reason = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class VehicleInspection(models.Model):
    id = models.AutoField(primary_key=True)
    pledge = models.OneToOneField(
        'Pledge',
        on_delete=models.CASCADE,
        related_name='inspection'
    )
    clase = models.CharField(max_length=80)
    color = models.CharField( max_length=50)
    model = models.CharField(max_length=50)
    marca = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    plate = models.CharField(max_length=50)
    chassis = models.CharField(max_length=50)
    motor = models.CharField(max_length=50)
    crpva = models.CharField(max_length=30)
    motor_status = models.TextField()
    bodywork_status = models.TextField()
    taxes = models.DecimalField(max_digits=15, decimal_places=2)
    infractions = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
