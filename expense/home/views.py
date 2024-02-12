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
from .forms import CreateUserForm, LoginForm

from django.contrib.auth.decorators import login_required

# - Authentication models & functions
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate, login, logout

@login_required(login_url="login")
def home(request):
    profile = Profile.objects.filter(user=request.user).first()
    expenses = Expense.objects.filter(user=request.user)

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

        return redirect('/')

    context = {'profile': profile, 'expenses': expenses}
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

def user_logout(request):

    auth.logout(request)

    return redirect("login")