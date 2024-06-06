from django.contrib.auth.decorators import user_passes_test

def user_is_admin(user):
    return user.groups.filter(name='Admin').exists()
def user_is_employee(user):
    return user.groups.filter(name='Employee').exists()

def admin_required(view_func):
    decorated_view_func = user_passes_test(user_is_admin)(view_func)
    return decorated_view_func
def employee_required(view_func):
    decoreted_view_func = user_passes_test(user_is_employee)(view_func)
    return decoreted_view_func