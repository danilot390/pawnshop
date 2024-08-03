from datetime import timedelta
from django.utils import timezone
from loan.models import UserBox, CompanyBox, IndividualBox
from django.db.transaction import atomic

def get_current_week(current_day = timezone.now().date()):
    start_date = current_day - timedelta(days=current_day.weekday())
    end_date = start_date + timedelta(days=6)

    return start_date, end_date

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

    start_date, end_date = get_current_week()

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

def update_box_amounts(box, amount):
    box.global_amount += amount
    box.week_amount += amount

@atomic
def box_out(box, amount):
    update_box_amounts(box, -amount)
    box.out_week_amount += amount
    box.out_global_amount += amount
    box.save()

def box_in(box, amount):
    update_box_amounts(box, amount)
    box.in_week_amount += amount
    box.in_global_amount += amount
    box.save()

@atomic
def box_out_delete(box, amount):
    update_box_amounts(box, amount)
    box.out_week_amount -= amount
    box.out_global_amount -= amount
    box.save()

@atomic
def box_in_delete(box, amount):
    update_box_amounts(box, -amount)
    box.in_week_amount -= amount
    box.in_global_amount -= amount
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

def register_expense(us, amount):
    personal_box = us.user_boxes.last()
    personal_box = check_individual_box(us, personal_box, 'us')
    company_box = us.company.company_boxes.last()
    company_box = check_individual_box(us.company, company_box, 'company')

    box_out(company_box.individual_box, amount)
    box_out(personal_box.individual_box, amount)

@atomic
def process_boxes(boxes, amount, is_out=True, is_delete=True):
    for i, box in enumerate(boxes):
        current_box = box.individual_box
        if i==0:
            if is_delete:
                if is_out:
                    box_out_delete(current_box, amount)
                else:
                    box_in_delete(current_box,amount)
            else:
                update_box_amounts(current_box, amount if is_out else -amount)
        else:
            update_box_amounts(current_box, amount if is_out else -amount)
        current_box.save()
        
