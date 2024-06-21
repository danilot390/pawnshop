from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum, Case, When, IntegerField

from box.forms import RechargeBoxForm, BoxForm
from loan.models import UserBox, CompanyBox, IndividualBox, Box, RechargePersonalBox

from datetime import timedelta


@login_required(login_url='login:logg')
def box_view(request):
    user = request.user
    personal_box = user.user_boxes.last()
    company_box = False
    if request.user.groups.filter(name='Admin').exists():
        company = user.company
        box = Box.objects.filter(company=company, type__isnull=False)
        internal_box = Box.objects.filter(company=company, type__isnull=True)
        company_box = company.company_boxes.last()

    else:
        box = Box.objects.filter(employee=request.user, type__isnull=False)
        internal_box = Box.objects.filter(employee=request.user, type__isnull=True)

    total_in = box.aggregate(total_in=Sum(Case(
        When(type='IN', then='amount'),
        default=0,
        output_field=IntegerField()
    )))['total_in']
    total_out = box.aggregate(total_out=Sum(Case(
        When(type='OUT', then='amount'),
        default=0,
        output_field=IntegerField()
    )))['total_out']

    total_box = (total_in or 0)-(total_out or 0)

        
    context = {
        'box' : box,
        'internal_box' : internal_box,
        'personal_box' : personal_box,
        'company_box' : company_box,
        'total' : total_box,
    }
    return render(request, 'box/box.html', context)

@login_required(login_url='login:logg')
def recharge_box(request):
    company = request.user.company
    employees = company.employees.all()
    context={
        'employees': employees
    }
    return render(request, 'box/recharge_box.html', context)

def create_individual_box(start_date, end_date):
    return IndividualBox.objects.create(
        start_date = start_date,
        end_date = end_date,
    )

def create_user_box(us,start_date, end_date):
    individual_box = create_individual_box(
        start_date=start_date, 
        end_date=end_date
        )
    return UserBox.objects.create(
        employee = us,
        individual_box = individual_box,
    )

def create_company_box(company,start_date, end_date):
    individual_box = create_individual_box(
        start_date, 
        end_date
        )
    return CompanyBox.objects.create(
        company = company,
        individual_box = individual_box
    )

def check_individual_box(us, box, type):
    current_day = timezone.now().date()
    start_date = current_day - timedelta(days=current_day.weekday())
    end_date = start_date + timedelta(days=6)

    if box is None or box.individual_box.start_date != start_date:
        in_global_amount = box.individual_box.in_global_amount if box else 0
        out_global_amount = box.individual_box.out_global_amount if box else 0
        global_amount = box.individual_box.global_amount if box else 0

        if type == 'us':
            box = create_user_box(us=us, start_date=start_date, end_date=end_date)
        elif type == 'company':
            box = create_company_box(company=us.company, start_date=start_date, end_date=end_date)
        
        box.individual_box.in_global_amount = in_global_amount
        box.individual_box.out_global_amount = out_global_amount
        box.individual_box.global_amount = global_amount
        box.individual_box.save()

    return box

def box_out(box, amount):
    box.out_week_amount += amount
    box.week_amount -= amount
    box.out_global_amount += amount
    box.global_amount -= amount
    box.save()

def box_in(box, amount):
    box.in_week_amount += amount
    box.week_amount += amount
    box.in_global_amount += amount
    box.global_amount += amount
    box.save()

def boxes(us, receiver, amount, transaction):
    receiver_box = receiver.user_boxes.last()
    receiver_box = check_individual_box(receiver, receiver_box, 'us')
    
    if transaction == 'move':
        us_box = us.user_boxes.last()
        us_box = check_individual_box(us, us_box, 'us')
        box_out(us_box.individual_box, amount)
    elif transaction == 'in':
        company_box = us.company.company_boxes.last()
        company_box = check_individual_box(us,company_box, 'company')
        box_in(company_box.individual_box, amount)
    
    box_in(receiver_box.individual_box, amount)
    pass

@login_required(login_url='login:logg')
@transaction.atomic
def recharge_box_post(request):
    if request.method == 'POST':
        recharge_form = RechargeBoxForm(request.POST)
        box_form = BoxForm(request.POST)
        if recharge_form.is_valid() and box_form.is_valid():
            user = request.user
            amount = box_form.cleaned_data['amount']
            new_box = box_form.save(commit=False)
            new_box.company = user.company

            if request.POST.get('new') is None:
                new_box.employee = user
                new_box.save()

                new_recharge = recharge_form.save(commit=False)
                boxes(user,new_recharge.receiver,amount,'move')
                new_recharge.box = new_box
                new_recharge.save()
                receiver = new_recharge.receiver.person.get_full_name()
            else:
                
                
                new_box.employee = recharge_form.cleaned_data['receiver']
                new_box.type = 'IN'
                new_box.save()
                receiver = new_box.employee.person.get_full_name()
                boxes(user,new_box.employee,amount,'in')

            messages.success(request, f"Recharge of {receiver}'s box was successful.")
            return redirect('box:box')
    
    
    messages.error(request, "Something went wrong. Please try again.")
    return redirect("box:recharge")
            
def expenses_box_view(request):
    context = {} 
    return render(request, 'box/expenses.html', context)

def register_expense(us, amount):
    personal_box = us.user_boxes.last()
    personal_box = check_individual_box(us, personal_box, 'us')
    company_box = us.company.company_boxes.last()
    company_box = check_individual_box(us.company, company_box, 'company')

    box_out(company_box.individual_box, amount)
    box_out(personal_box.individual_box, amount)

@login_required(login_url='login:logg')
@transaction.atomic
def expenses_box_post(request):
    if request.method == 'POST':
        box_form = BoxForm(request.POST)
        if box_form.is_valid():
            expense = box_form.save(commit=False)
            expense.company = request.user.company
            expense.employee = request.user
            expense.type = 'OUT'
            expense.save()

            register_expense(request.user, expense.amount)

            messages.success(request, f'Expenses registered successfully.')
            return redirect('box:box')
        
    messages.error(request, "Failed to register expense. Please try again.")
    return redirect("box:expenses_box")