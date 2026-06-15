from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from order.models import Order
from users.forms import RegisterUserForm, LoginUserForm, EditUserForm


# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)

            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = RegisterUserForm(
            initial={'phone': 'RU'}
        )

    return render(request, 'users/register.html', {'form': form})


def my_login(request):
    if request.method == 'POST':
        form = LoginUserForm(request.POST)

        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )

            if user is not None:
                login(request, user)

                next = request.GET.get('next')
                if next:
                    return redirect(next)

                return redirect('models')
    else:
        form = LoginUserForm()

    return render(request, 'users/login.html', {'form': form})


@login_required
def profile(request):
    context = {'user': request.user, 'orders': Order.objects.filter(user=request.user).order_by('created_at')[:3]}
    return render(request, 'users/profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save(commit=True)
            return redirect('profile')
    else:
        form = EditUserForm(instance=request.user)

    return render(request, 'users/profile_edit.html', {'form': form})


@login_required
def my_logout(request):
    logout(request)
    return redirect('login')


@login_required
def balance_replenishment(request):
    if request.method == 'POST':
        amount_str = request.POST.get('amount')

        if amount_str:
            try:
                amount = Decimal(amount_str)

                if amount <= 0:
                    messages.error(request, 'Сумма пополнения должна быть положительной.')

                user = request.user
                user.balance += amount
                user.save(update_fields=['balance'])
                messages.success(request, f'Ваш баланс успешно пополнен на {amount} PC!')

            except InvalidOperation:
                messages.error(request, 'Пожалуйста, введите корректную сумму.')
        else:
            messages.error(request, 'Вы не указали сумму для пополнения.')

    return redirect('profile')
