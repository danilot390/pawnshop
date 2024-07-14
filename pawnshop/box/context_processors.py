from box.utils import create_company_box, create_user_box, get_current_week

def box_information(request):
    """
    Retrieve information about the user's box and the company's box if the user is an admin.

    Retrieves details about 

    Returns:
        Dictionary: General details about the user's box and company's box.
    """
    if request.user.is_authenticated:
        user = request.user
        company = user.company

        user_box = user.user_boxes.last() 
        company_box = company.company_boxes.last() 
        
        start_date, end_date = get_current_week()
        user_box = user_box if user_box is not None else create_user_box(user, start_date, end_date)
        company_box = company_box if company_box is not None else create_company_box(company, start_date, end_date)

        company_box = company_box.individual_box if request.user.groups.filter(name='Admin').exists() else None

        context = {
            'us_box_': user_box.individual_box,
            'company_box_': company_box,
        }
    else:
        context = {
            'us_box_': False,
            'company_box_': False,
        }
    
    return context