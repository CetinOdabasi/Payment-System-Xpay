import datetime

from django.contrib import messages
from django.contrib.auth import (authenticate, get_user_model, login,)
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import (get_list_or_404,
                              get_object_or_404,
                              redirect,
                              render)
from django.utils import timezone
from django.views import generic

from .forms import (CurrentAccountForm,
                    LoginForm,
                    MoneyDepositingForm,
                    SendMoneyForm,
                    SignUpForm,
                    XpayAccountForm,
                    EditProfileForm)
from .models import AccountTransaction, Country_files, XpayAccount
from django.contrib.auth.decorators import login_required

MyUser = get_user_model()






def signup_page(request):
    form = SignUpForm(request.POST or None)
    if form.is_valid():
        data = form.cleaned_data
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        phone_number = data.get('phone_number')
        country = data.get('country')
        new_user = MyUser.objects.create_user(
            email, password, first_name, last_name, phone_number, country)
        new_user.save()
        login(request, new_user)
        messages.info(request, "Registration Successful")
        return redirect('login_page')

    context = {
        "form": form
    }
    return render(request, "xpay/signup.html", context)


def login_page(request):
    form = LoginForm(request.POST or None)
    context = {
        'form': form
    }

    if form.is_valid():
        data = form.cleaned_data
        email = data.get('email')
        password = data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile_page')
        else:
            messages.warning(request, 'Email address or password is incorrect!')

    return render(request, "xpay/login.html", context)



def home_page(request):
    return render(request,'xpay/homepage.html')


def profile_page(request):
    return render(request,'xpay/profile.html')


def my_xpay_account_page(request):
    ibanNo=XpayAccount.objects.filter(email=request.user, account_status='open')
    context={
        'ibanNo':ibanNo,
    }
    return render(request,'xpay/my_account.html',context)




def detail(request, account_number):
    iban_detail_page=get_object_or_404(XpayAccount, pk=account_number)
    open_iban_list=XpayAccount.objects.filter(email_id=request.user,  account_status='open')
    account_transaction=AccountTransaction.objects.filter(xpay_iban_no=iban_detail_page.iban_no)
    account_transaction_last=AccountTransaction.objects.filter(xpay_iban_no=iban_detail_page.iban_no).last()


    context={
        'open_iban_list' : open_iban_list,
        'iban_detail_page' : iban_detail_page,
        'account_transaction':account_transaction,        
        'account_transaction_last':account_transaction_last,
    }
    return render (request,'xpay/detail.html', context)
    





def user_profile_page(request):
    if request.method == 'POST'and "update" in request.POST:
        editform = EditProfileForm(request.POST, instance=request.user)
        if editform.is_valid():
            editform.save(commit=True)
            return redirect("user_profile")
        else:
            return redirect("user_profile")
    if request.method == 'POST'and "passform" in request.POST:
        passform = PasswordChangeForm(user=request.user,data=request.POST)
        if passform.is_valid():
            passform.save()
            update_session_auth_hash(request, passform.user)
            messages.success(request, 'Your password was successfully updated!') 
            return redirect('user_profile')
        else:
            messages.error(request, 'Please correct the error below.')
            return redirect('user_profile')
    
    else:
        editform=EditProfileForm(instance=request.user)
        passform = PasswordChangeForm(request.user)
    return render(request, 'xpay/user_profile.html',{"editform":editform, "passform":passform})





def open_and_close_account_page(request):
    if request.method == "POST" and 'form1' in request.POST:
        form1 = XpayAccountForm(request.POST)
        if form1.is_valid():
            post = form1.save(commit=False)
            post.email = request.user
            post.save()



    if request.method == "POST" and 'form2' in request.POST:
        form2= CurrentAccountForm(request.user, request.POST)
        if form2.is_valid():
            form2.iban_no = request.user
            form2.iban_no = form2.cleaned_data['current_accounts']
            account_status_query=XpayAccount.objects.filter(email=request.user, iban_no=form2.iban_no).update(account_status='close')
            return redirect( 'open_and_close_account_page')

    else:
        form1 = XpayAccountForm()
        form2 = CurrentAccountForm(request.user)
    return render(request, 'xpay/open_and_close_account.html', {'form1': form1, 'form2':form2})





def money_depositing_page(request):
    if request.method == "POST": 
        form = MoneyDepositingForm(request.user, request.POST)
        if form.is_valid():
            print('a')
            return render(request,'xpay/money_depositing_confirmation.html',{'form': form})
            print('b')
    else:
        form = MoneyDepositingForm(request.user)
    return render(request, 'xpay/money_depositing.html', {'form': form})



def money_depositing_confirmation_page(request):
    if request.method == "POST":
        form = MoneyDepositingForm(request.user, request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.xpayaccount=XpayAccount.objects.get(account_number=request.user.id)
            form.xpay_iban_no=form.receiver_iban_no
            form.receiver_full_name=request.user.get_full_name()
            form.save()
            return redirect('money_depositing_page')

    else:
        form = MoneyDepositingForm(request.user)
    return render(request, 'xpay/money_depositing.html', {'form': form})





def send_money_page(request):
    if request.method == "POST":
        form = SendMoneyForm(request.user, request.POST or None)
        if form.is_valid():
            return render(request,'xpay/send_money_confirmation.html',{'form': form})

    else:
        form = SendMoneyForm(request.user)
    return render(request, 'xpay/send_money.html', {'form': form})

def send_money_confirmation_page(request):
    if request.method == "POST":
        form = SendMoneyForm(request.user, request.POST or None)
        if form.is_valid():
            form = form.save(commit=False)
            form.xpayaccount=XpayAccount.objects.get(account_number=request.user.id)
            form.sender_full_name=request.user.get_full_name()
            form.xpay_iban_no=form.sender_iban_no
            form.amount=form.amount*-1
            form.save()
            return redirect('send_money_page')
        
    else:
        form = SendMoneyForm(request.user)
    return render(request, 'xpay/send_money.html', {'form': form})




