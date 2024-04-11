# from django.shortcuts import redirect, render
# from .models import *

# # Create your views here.
# def home(request):
#     profile = Profile.objects.filter(user = request.user).first()
#     expenses = Expense.objects.filter(user = request.user)

#     if request.method == 'POST':
#         text = request.POST.get('text')
#         amount = request.POST.get('amount')
#         expense_type = request.POST.get('expense_type')

#         expense = Expense(name=text, amount=amount, expense_type=expense_type, user=request.user)
#         expense.save()

#         if expense_type == 'Positive':
#             profile.balance += float(amount)
#         else:
#             profile.expenses += float(amount)
#             profile.balance -= float(amount)

#         profile.save()
#         return redirect('/')

#     context = {'profile': profile, 'expenses': expenses}

#     return render(request, 'home.html', context)


from django.shortcuts import redirect, render, get_object_or_404
from .models import *
from .forms import CreateUserForm, CustomUserChangeForm, LoginForm

from django.contrib.auth.decorators import login_required

# - Authentication models & functions
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate, login, logout

@login_required(login_url="login")
def home(request):
    profile = Profile.objects.filter(user=request.user).first()
    expenses = Expense.objects.filter(user=request.user)
    expense_id = None
    expense = None

    if request.method == 'POST':
        if 'add' in request.POST:
            text = request.POST.get('text')
            amount = request.POST.get('amount')
            expense_type = request.POST.get('expense_type')

            expense = Expense(name=text, amount=amount, expense_type=expense_type, user=request.user)
            expense.save()

            if expense_type == 'Positive':
                profile.balance += float(amount)
            else:
                profile.expenses += float(amount)
                profile.balance -= float(amount)

            profile.save()
        elif 'edit' in request.POST:
            expense_id = request.POST.get('expense_id')
            expense = get_object_or_404(Expense, id=expense_id, user=request.user)

            context = {'profile': profile, 'expenses': expenses, 'expense': expense}
            return render(request, 'home.html', context)
        elif 'delete' in request.POST:
            expense_id = request.POST.get('expense_id')
            expense = get_object_or_404(Expense, id=expense_id, user=request.user)

            if expense.expense_type == 'Positive':
                profile.balance -= expense.amount
            else:
                profile.expenses -= expense.amount
                profile.balance += expense.amount

            profile.save()
            expense.delete()
        elif 'update' in request.POST:
            expense_id = request.POST.get('expense_id')
            text = request.POST.get('text')
            amount = request.POST.get('amount')
            expense_type = request.POST.get('expense_type')

            expense = get_object_or_404(Expense, id=expense_id, user=request.user)

            # Adjust profile balance based on the previous amount
            if expense.expense_type == 'Positive':
                profile.balance -= expense.amount
            else:
                profile.expenses -= expense.amount
                profile.balance += expense.amount

            # Adjust profile balance based on the updated amount
            if expense_type == 'Positive':
                profile.balance += float(amount)
            else:
                profile.expenses += float(amount)
                profile.balance -= float(amount)

            # Update the expense
            expense.name = text
            expense.amount = amount
            expense.expense_type = expense_type
            expense.save()

            profile.save()

        return redirect('/')

    context = {'profile': profile, 'expenses': expenses, 'expense': expense}
    return render(request, 'home.html', context)

def user_register(request):

    form = CreateUserForm()

    if request.method == "POST": 
        form = CreateUserForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect("login")
        
    context = {'registerform': form}

    return render(request, 'register.html', context=context)

def user_login(request):

    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth.login(request, user)
                
                return redirect("/")
    
    context = {'loginform':form}

    return render(request, 'login.html', context=context)

@login_required(login_url="login")
def user_logout(request):

    auth.logout(request)

    return redirect("login")

@login_required(login_url="login")
def update_profile(request):
    user = request.user
    form = CustomUserChangeForm(instance=user)

    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('/')  # Redirect to the profile page after successful update

    context = {'form': form}
    return render(request, 'profile.html', context)

@login_required(login_url="login")
def budget_profile(request):
    profile = Profile.objects.filter(user=request.user).first()

    context = {'profile': profile}

    return render(request, 'budget.html', context)

@login_required(login_url="login")
def update_budget_profile(request):
    if request.method == 'POST':
        profile = Profile.objects.filter(user=request.user).first()

        profile.income = request.POST.get('income')
        profile.expenses = request.POST.get('expenses')
        profile.balance = request.POST.get('balance')
        profile.save()

        return redirect('/')

# @login_required(login_url="login")
# def update_budget_profile(request):
#     if request.method == 'POST':
#         profile, created = Profile.objects.get_or_create(user=request.user)

#         profile.income = request.POST.get('income')
#         profile.expenses = request.POST.get('expenses')
#         profile.balance = request.POST.get('balance')
#         profile.save()

#         return redirect('/')
#     else:
#         return render(request, 'budget.html')

# @login_required(login_url="login")
# def update_budget_profile(request):
#     if request.method == 'POST':
#         profile, created = Profile.objects.get_or_create(user=request.user, income=0, expenses=0, balance=0)

#         # Ensure income, expenses, and balance are provided before saving
#         income = request.POST.get('income')
#         expenses = request.POST.get('expenses')
#         balance = request.POST.get('balance')

#         if income is not None and expenses is not None and balance is not None:
#             profile.income = income
#             profile.expenses = expenses
#             profile.balance = balance
#             profile.save()

#         return redirect('/')
#     else:
#         return render(request, 'budget.html')