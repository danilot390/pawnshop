from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import Group
from login.forms import UserProfileForm, UserForm, NewUserForm
from loan.models import Person, User
from login.utils import admin_required



def login_view(request):
    if request.user.is_authenticated:
        return redirect('loan:loan_index')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back {username}.')
                return redirect('loan:loan_index')
    else:
        form = AuthenticationForm()

    return render(request, 'login/login.html', {'form': form})   

def log_out(request):
    logout(request)
    return redirect('login:logg')

@login_required(login_url='login:logg')
def user_view(request, id):
    user = get_object_or_404(User, id=id)
    person = user.person

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=person)
        user_form = UserForm(request.POST, instance=user)

        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()

            if user_form.cleaned_data['password']:
                user.set_password(user_form.cleaned_data['password'])
                user.save()
                update_session_auth_hash(request, user)
            
            if request.user.groups.filter(name='Admin').exists():
                user.is_active = request.POST.get('is_active') is not None
                user.save()
                
                rol_admin = Group.objects.get(name='Admin')
                rol_employee = Group.objects.get(name='Employee')
                
                if request.POST.get('is_admin'):
                    user.groups.add(rol_admin)
                else:
                    user.groups.remove(rol_admin)
                
                if request.POST.get('is_employee'):
                    user.groups.add(rol_employee)
                else:
                    user.groups.remove(rol_employee)

            messages.success(request, 'Profile updated successfully')
            return redirect('loan:loan_index')
    else:
        profile_form = UserProfileForm(instance=person)
        user_form = UserForm(instance=user)

    context = {
        'edit_us' : {
            'ci' : person.ci,
            'name' : person.name,
            'last_name' : person.last_name,
            'address' : person.address,
            'phone_number' : person.phone_number,
            'username' : user.username,
            'is_active' : user.is_active,
            'is_admin' : user.groups.filter(name='Admin').exists(),
            'is_employee' : user.groups.filter(name='Employee').exists(),
        },
    }
 
    return render(request, 'login/profile.html', context)

@admin_required
@login_required(login_url='login:logg')
def create_new_user_view(request):
    if request.method == 'POST':
        ci = request.POST.get('ci')
        
        try :
            person = Person.objects.get(ci=ci)
            profile_form = NewUserForm(request.POST, instance=person)
        except:
            profile_form = UserProfileForm(request.POST)
            
        user_form = NewUserForm(request.POST)

        if profile_form.is_valid() and user_form.is_valid():
            person = profile_form.save()

            user = user_form.save(commit=False)
            user.person = person
            user.company = request.user.company
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            
            if request.POST.get('type') == 'admin':
                user.groups.add(1)
            elif request.POST.get('type') == 'employee':
                user.groups.add(2)
            else:
                messages.error(request, 'There was an error adding the role.')

            messages.success(request, "New user created successfully!")
            return redirect('login:create_new_user')
        else:
            messages.error(request, "There was an error creating the user. Please check the form and try again.")
    context = {}
    return render(request, 'login/new_user.html', context)

@admin_required
@login_required(login_url='login:logg')
def list_user_view(request):
    company = request.user.company
    employees = company.employees.all().order_by('is_active')
    context = {
        'employees' : employees,
    }
    return render(request, 'login/list_user.html', context)
