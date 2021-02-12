from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth import authenticate
from xpay.models import XpayAccount, Currency_files, Country_files, AccountTransaction
import re
from django.db.models import Sum
from django.contrib.auth.forms import UserChangeForm
from django.db.models import F

MyUser = get_user_model()


class UserAdminCreationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = MyUser
        fields = ('email',)

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = MyUser
        fields = ('email', 'password', 'active', 'admin')

    def clean_password(self):

        return self.initial["password"]

class SignUpForm(forms.ModelForm):
    password = forms.CharField(min_length=8, widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)
    k=Country_files.objects.all().values_list('country_code', flat=True)
    v=Country_files.objects.all().values_list('country_name', flat=True)
    country_choices =list(zip(k,v))
    country = forms.ChoiceField(choices=country_choices, widget=forms.Select())

    class Meta:
        model = MyUser
        fields = ('email', 'first_name', 'last_name',
                  'phone_number', 'country')
    


    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2


    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_active = False
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email:')
    password = forms.CharField(label="Password:", widget=forms.PasswordInput)

    class META:
        model = MyUser
        fields = ('email', 'password')





class EditProfileForm(UserChangeForm):
    k=Country_files.objects.all().values_list('country_code', flat=True)
    v=Country_files.objects.all().values_list('country_name', flat=True)
    country_choices =list(zip(k,v))
    country = forms.ChoiceField(choices=country_choices, widget=forms.Select())


    class Meta:
        model = MyUser
        fields = ('email', 'first_name', 'last_name','phone_number','country')






class XpayAccountForm(forms.ModelForm):
    k=Currency_files.objects.all().values_list('currency_code', flat=True)
    v=Currency_files.objects.all().values_list('currency_name', flat=True)
    currency_choices =list(zip(k,v))
    currency = forms.ChoiceField(choices=currency_choices, widget=forms.Select())


    class Meta:
        model=XpayAccount
        fields=('currency',)

class CurrentAccountForm(forms.ModelForm):
    current_accounts = forms.ModelChoiceField(queryset=None, to_field_name='iban_no')


    class Meta:
        model=XpayAccount
        fields=('current_accounts',)

    def __init__(self, email, *args, **kwargs):
        super(CurrentAccountForm, self).__init__(*args,**kwargs)
        self.fields['current_accounts'].queryset = XpayAccount.objects.filter(email=email, account_status='open').values_list('iban_no', flat=True).distinct().order_by('account_number2')






class MoneyDepositingForm(forms.ModelForm):
    receiver_iban_no = forms.ModelChoiceField(queryset=None, to_field_name='iban_no')
    amount=forms.IntegerField(min_value=0)

    class Meta:
        model=AccountTransaction
        fields=('receiver_iban_no','sender_full_name','sender_iban_no','sender_bank_name','amount',)

    def __init__(self, email,*args, **kwargs):
        super(MoneyDepositingForm, self).__init__(*args,**kwargs)
        self.fields['receiver_iban_no'].queryset = XpayAccount.objects.filter(email=email, account_status='open').values_list('iban_no', flat=True).distinct().order_by('account_number2')



class SendMoneyForm(forms.ModelForm):
    sender_iban_no = forms.ModelChoiceField(queryset=None, to_field_name='iban_no')
    amount=forms.IntegerField(min_value=0)


    
    class Meta:
        model=AccountTransaction
        fields=('sender_iban_no','receiver_iban_no','receiver_full_name','receiver_bank_name','amount',)



    def __init__(self, email,*args, **kwargs):
        super(SendMoneyForm, self).__init__(*args,**kwargs)
        self.fields['sender_iban_no'].queryset = XpayAccount.objects.filter(email=email, account_status='open').values_list('iban_no', flat=True).distinct().order_by('account_number2')
        
        
    def clean(self):
        cleaned_data = super().clean()
        amount=cleaned_data.get("amount")
        sender_iban_no=cleaned_data.get("sender_iban_no")
        account_balance_total=AccountTransaction.objects.filter(xpay_iban_no=sender_iban_no).aggregate(sum=Sum('amount'))['sum'] or 0
        if account_balance_total < amount:
            raise forms.ValidationError('Insufficient account balance !')
        else:
            pass
        
        
