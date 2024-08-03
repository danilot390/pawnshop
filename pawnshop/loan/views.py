from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone

from loan.forms import BlackListForm, PledgeForm, PersonForm, PersonFormWithLoan, OtherContractForm, VehicleInspectionForm
from loan.models import Person, Box, OtherContract, Pledge, BlackList
from box.views import check_individual_box, box_out, box_in

from datetime import timedelta

@login_required(login_url='login:logg')
def index_loan(request):
    """View to display the index page of the loan module."""
    message = f'Welcome back dear {request.user.person.name}.'
    context = {'message' : message,}
    return render(request, 'loan/index.html', context)

@login_required(login_url='login:logg')
def loan_view(request):
    """View to display the loan check person is register."""
    return render(request, 'loan/check_person.html')

def loan_reg_view(request, person):
    """View to register a loan for a person."""
    pledge_form = PledgeForm()
    person_form = PersonForm(instance = person)
    black_list = person.blacklist.filter(is_active=True).last() or False
    context = {
        'id_person' : person.id,
        'pledge_form' : pledge_form,
        'person_form' : person_form,
        'black_list' : black_list, 
    }
    return render(request, 'loan/loan.html', context)


@login_required(login_url='login:logg')
def person_view(request, ci):
    """View to display the person form with loan details."""
    person_form = PersonFormWithLoan()
    context = {
        'person_form' : person_form,
    }
    return render(request, 'loan/person.html', context)


@transaction.atomic
def create_person(request):
    """View to process loan posting."""
    if request.method == 'POST':
        person_form = PersonFormWithLoan(request.POST)
        
        if person_form.is_valid():
            person = person_form.save()
            messages.success(request, 'Successfully registered a new person.')
            if person_form.clean_go_loan():
                return loan_reg_view(request, person)
            else:
                return redirect('loan:loan_index')

    messages.error(request, 'There was an error with the form submission.')
    return redirect('loan:loan')


@transaction.atomic
def loan_post(request, id_person):
    """Vew to process loan posting"""
    if request.method == 'POST':
        person = get_object_or_404(Person, id=id_person)
        pledge_form = PledgeForm(request.POST)
        person_form = PersonForm(request.POST, instance=person)
        user = request.user
        company = user.company

        if pledge_form.is_valid() and person_form.is_valid():

            person = person_form.save()
            
            new_pledge = pledge_form.save(commit=False)
            new_pledge.client = person
            new_pledge.employee = user
            new_pledge.company = company
            new_pledge.balance = new_pledge.loan
            
            amount_out = new_pledge.balance*((100 - new_pledge.interest)/100)
            user_box = check_individual_box(user, user.user_boxes.last(), 'us')
            company_box = check_individual_box(user, company.company_boxes.last(), 'company')
            box_out(user_box.individual_box, amount_out)
            box_out(company_box.individual_box, amount_out)

            box = Box.objects.create(
                company = company,
                employee = user,
                amount = amount_out,
                type = 'OUT',
                description = f'Loan for {new_pledge.loan} - {new_pledge.client.get_full_name()}',
            )

            new_pledge.box = box
            new_pledge.save()

            return other_contracts(request, new_pledge)
            
        messages.error(request, 'There was an error with the form submission.')
    return redirect('loan:loan')

def other_contracts(request, pledge):
    """View to handle other contracts related to a pledge."""
    debt_rec = create_other_contracts(pledge, 'DR')
    vehicle_contract =create_other_contracts(pledge, 'BS') if pledge.type == 'vehicles' else False
    debt_rec_form = OtherContractForm(instance=debt_rec)
    vehicle_contract_form = OtherContractForm(instance=vehicle_contract) if vehicle_contract else False
    vehicle_inspection_form = VehicleInspectionForm() if vehicle_contract else False

    context ={
        'id': pledge.id,
        'debt_rec_form': debt_rec_form,
        'vehicle_contract_form': vehicle_contract_form,
        'vehicle_inspection_form': vehicle_inspection_form,
    }

    messages.success(request, "Successfully registered a new loan.")
    return render(request, 'loan/other_contracts.html', context)

@transaction.atomic
def save_contracts(request, id):
    """View to save contracts realted to a pledge."""
    if request.method == 'POST':
        pledge = get_object_or_404(Pledge, id=id)
        debt_rec = pledge.contracts.get(contract_type='DR')
        vehicle_contract = pledge.contracts.get(contract_type='BS') if pledge.type == 'vehicles' else False
        debt_rec_form = OtherContractForm(request.POST, instance=debt_rec)
        vehicle_contract_form = OtherContractForm(request.POST, instance=vehicle_contract)if vehicle_contract else True
        vehicle_inspection_form = VehicleInspectionForm(request.POST)if vehicle_contract else True
        
        if vehicle_contract is not False:
            if debt_rec_form.is_valid() and vehicle_inspection_form.is_valid() and vehicle_contract_form.is_valid():
                debt_rec_form.save()
                vehicle_contract_form.save()
                inspection = vehicle_inspection_form.save(commit=False)
                inspection.pledge = pledge
                inspection.save()
                
        elif debt_rec_form.is_valid():
            debt_rec_form.save()
        messages.success(request,'Contracts save successfully.')
        return redirect('loan:loan_detail', id=id)
    else:
        messages.error(request, 'There was an error saving the contracts.')
        return redirect('loan:loan')


def create_other_contracts(pledge, type):
    """Helper function to create other contracts related to a pledge."""
    ini_date = pledge.loan_date - timedelta(days=31)
    return OtherContract.objects.create(
        pledge = pledge,
        contract_type = type,
        initial_date = ini_date,
        end_date = pledge.rescue_date,
    )


def check_person_post(request):
    """View to handle peron checking post request"""
    if request.method == 'POST':
        ci = request.POST.get('ci')
        person = Person.objects.filter(ci=ci).first()
        if person is not None:
            return loan_reg_view(request, person)
        return redirect('loan:person', ci=ci)

@login_required(login_url='login:logg')
def list_loans(request):
    """View to list all active loans."""
    company = request.user.company
    list_loans = company.pledges.filter(balance__gt= 0, status=True).order_by('arrears', 'rescue_date')
    context = {
        'list_loans': list_loans,
    }
    return render(request, 'loan/list_loans.html', context)

@login_required(login_url='login:logg')
def loan_detail(request, id):
    """View to display the details of loan."""
    loan = get_object_or_404(Pledge, id=id)
    context ={
        'loan': loan,
    }
    return render(request, 'loan/loan_detail.html', context)

@transaction.atomic
def loan_paid(request, id):
    """View to mark a loan as paid."""
    user = request.user
    company = user.company
    loan = get_object_or_404(Pledge, id=id)
    user_box = check_individual_box(user, user.user_boxes.last(), 'us')
    company_box = check_individual_box(user, company.company_boxes.last(), 'company')
    box_in(user_box.individual_box, loan.balance)
    box_in(company_box.individual_box, loan.balance)

    Box.objects.create(
        company = company,
        employee = user,
        amount = loan.balance,
        type = 'IN',
        description = f"{loan.client.get_full_name()}'s loan for {loan.article} successfully settled.",
    )

    loan.balance = 0
    loan.status = False
    loan.save()
    messages.success(request,'Loan successfully settled.')
    return redirect('loan:list_loans')

@transaction.atomic
def loan_renewal(request, id):
    """View to renew a loan."""
    user = request.user
    company = user.company
    loan = get_object_or_404(Pledge, id=id)
    user_box = check_individual_box(user, user.user_boxes.last(), 'us')
    company_box = check_individual_box(user, company.company_boxes.last(), 'company')
    loan_to_interst = loan.loan_to_interest_ratio()
    box_in(user_box.individual_box, loan_to_interst)
    box_in(company_box.individual_box, loan_to_interst)

    Box.objects.create(
        company = company,
        employee = user,
        amount = loan.loan_to_interest_ratio(),
        type = 'IN',
        description = f"{loan.client.get_full_name()}'s loan for {loan.article} successfully renewal.",
    )

    loan.renewal_date = timezone.now().date() + timedelta(days=31)
    loan.arrears = 0
    loan.save()
    messages.success(request,'Loan successfully renewed.')
    return redirect('loan:list_loans')

@login_required(login_url='login:logg')
def list_havings(request):
    """View lo list all articles in arrears."""
    company = request.user.company
    articles = company.pledges.filter(arrears__gt=0, status=True)
    context = {
        'articles' : articles,
    }
    return render(request, 'loan/list_havings.html', context)

@transaction.atomic
def article_sell(request, id):
    """View to mark an article as sold."""
    if request.method == 'POST':
        balance = int(float(request.POST.get('purchase')))
        loan = get_object_or_404(Pledge, id=id)
        loan.status=False
        loan.balance=0

        user = request.user
        user_box = check_individual_box(user, user.user_boxes.last(), 'us')
        company_box = check_individual_box(user.company, user.company.company_boxes.last(), 'company')
        box_in(user_box.individual_box, balance)
        box_in(company_box.individual_box, balance)

        Box.objects.create(
            company = user.company,
            employee = user,
            amount = balance,
            type = 'IN',
            description = f"{loan.article} was sold successfully.",
        )

        loan.save()
        messages.success(request, 'Purchase register successfully.')
    
    return redirect('loan:list_havings')

@login_required(login_url='login:logg')
def black_list(request):
    """View to display the active black list accros the program."""
    black_list = BlackList.objects.filter(is_active=True)
    context = {
        'black_list': black_list,
    }
    return render(request, 'loan/black_list.html', context)

@login_required(login_url='login:logg')
def add_black_list(request):
    """View to add a person to the blask list."""
    people = Person.objects.all()
    if request.method == 'POST':
        black_list_form = BlackListForm(request.POST, people_queryset=people)
        if black_list_form.is_valid():
            add_black_list = black_list_form.save(commit=False)
            add_black_list.company = request.user.company
            add_black_list.save()
            messages.success(request, 'Successfully added to the black list.')
            return redirect('loan:black_list')
        messages.error(request, 'There was an error with the form submission.')
    
    
    black_list_form = BlackListForm(people_queryset=people)
    context = {
        'black_list_form': black_list_form,
    }
    return render(request, 'loan/add_black_list.html', context)


def delete_black_list(request, id):
    """View to mark a person as no longer blacklisted."""
    try:
        black = get_object_or_404(BlackList, id=id)
        black.is_active = False
        black.save()
        messages.success(request, 'Successfully removed from the black list.')
    except BlackList.DoesNotExist:
        messages.error(request,'There was an error removing from the black list.')
    
    return redirect('loan:black_list')
