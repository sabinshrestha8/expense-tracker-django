from pyexpat.errors import messages
from django.shortcuts import redirect, render, get_object_or_404
from .models import *
from .forms import CodeForm, CreateUserForm, CustomUserChangeForm, LoginForm
from django.contrib import messages
from .utils import send_email

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
            # text = request.POST.get('text')
            # amount = request.POST.get('amount')
            # expense_type = request.POST.get('expense_type')

            # expense = Expense(name=text, amount=amount, expense_type=expense_type, user=request.user)
            # expense.save()

            # if expense_type == 'Positive':
            #     profile.balance += float(amount)
            # else:
            #     profile.expenses += float(amount)
            #     profile.balance -= float(amount)

            # profile.save()

            text = request.POST.get('text')
            amount_str = request.POST.get('amount')  # Get the amount as string
            amount = float(amount_str)  # Convert the string to float
            expense_type = request.POST.get('expense_type')

            # Check if balance is greater than or equal to the amount
            if expense_type == 'Positive' or profile.balance >= amount:
                expense = Expense(name=text, amount=amount, expense_type=expense_type, user=request.user)
                expense.save()

                if expense_type == 'Positive':
                    profile.balance += float(amount)
                else:
                    profile.expenses += float(amount)
                    profile.balance -= float(amount)

                profile.save()
            else:
                # Handle case where balance is insufficient
                messages.error(request, "Insufficient balance to make this expense.")
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

            messages.success(request, "User registered successfully.")

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
                # auth.login(request, user)
  
                # return redirect("/")

                request.session['pk'] = user.pk
                return redirect('verify_otp');
    
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

def verify_otp(request):
    form = CodeForm(request.POST or None)
    pk = request.session.get('pk')

    if pk:
        user = CustomUser.objects.get(pk=pk)
        code = user.code
        # code_user = f"{user.username}: {code}"

        if not request.POST :
            # print(code_user)
            #send sms
            # send_sms(code_user, user.phone_number)

            #send email
            send_email(code, 'bodemagazine@gmail.com')
        if form.is_valid():
            num = form.cleaned_data.get('number')

            if str(code) == num:
                code.save()
                auth.login(request, user)
                return redirect("/")
            else:
                return redirect('login')
    return render(request, 'two_factor_auth.html', {'form': form})
