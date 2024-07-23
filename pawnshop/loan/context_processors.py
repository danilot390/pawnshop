from django.utils import timezone
from django.db.models import Q, F
from django.http import HttpResponse, HttpResponseRedirect

def updated_arrears(pledges, day):
    context={}
    try:
        for loan in pledges:
            rescue_date = loan.renewal_date if loan.renewal_date is not None else loan.rescue_date
            arrears = (day - rescue_date).days
            loan.arrears = arrears
            loan.save()
    except:
        context

    return context

def check_pledge(request):
    company = request.user.company
    current_day = timezone.now().date()

    pledges = company.pledges.filter(
        Q(status=True),
        Q(updated_at__lte=current_day),
        Q(rescue_date__lt=current_day) | Q(renewal_date__isnull=True) & Q(renewal_date__lt=current_day)
        )
    
    return updated_arrears(pledges,current_day)

def pledge_processor(request):
    if request.user.is_authenticated:
        check = check_pledge(request)
        return check
    else:
        return ''


    