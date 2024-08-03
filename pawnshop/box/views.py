from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, Case, When, IntegerField

from box.forms import RechargeBoxForm, BoxForm
from box.utils import check_individual_box, process_boxes, box_in_delete, box_out_delete, box_out, box_in, boxes, register_expense, get_current_week
from loan.models import Box

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

@login_required(login_url='login:logg')            
def expenses_box_view(request):
    context = {} 
    return render(request, 'box/expenses.html', context)

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

@transaction.atomic
def delete_box(request, id):
    """View to delted a box."""
    box = get_object_or_404(Box, id=id)
    amount = box.amount
    user = box.employee
    start_week_box, _ = get_current_week(current_day=box.created_at)
    
    user_boxes = user.user_boxes.filter(individual_box__created_at__gte=start_week_box)
    company_boxes = user.company.company_boxes.filter(individual_box__created_at__gte=start_week_box)
    
    if box.type == 'OUT':
        process_boxes(user_boxes, amount)
        process_boxes(company_boxes, amount)

    elif box.type == 'IN':
        process_boxes(user_boxes, amount, is_out=False)
        process_boxes(company_boxes, amount, is_out=False)
    else:
        recharge=box.recharge_personal_box
        receiver=recharge.receiver
        receiver_boxes = receiver.user_boxes.filter(individual_box__created_at__gte=start_week_box)
        
        process_boxes(receiver_boxes, amount, is_out=False)
        process_boxes(user_boxes, amount)

    box.delete()

    return redirect('box:box')