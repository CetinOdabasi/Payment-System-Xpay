from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.utils import timezone
import numpy as np
import pandas as pd 
import uuid
from django.dispatch import receiver    
from django.db.models.signals import post_save, pre_save
from django.db.models import Sum
from django.db.models import F

MyUser = settings.AUTH_USER_MODEL


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, first_name=None, last_name=None, phone_number=None, country=None, is_active=True, is_staff=False, is_admin=False):
        if not email:
            raise ValueError('Users must have an email address')
        if not password:
            raise ValueError('Users must have a password')

        user_obj = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            country=country,
        )
        user_obj.active = is_active
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.set_password(password)
        user_obj.save(using=self._db)
        return user_obj

    def create_staff_user(self, email, password=None):
        user_obj = self.create_user(
            email,
            password=password,
            is_staff=True
        )
        return user_obj

    def create_superuser(self, email, password=None):
        user_obj = self.create_user(
            email,
            password=password,
            is_staff=True,
            is_admin=True,
        )
        return user_obj


class MyUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(null=False, blank=False,unique=True, max_length=80, verbose_name='Email')
    first_name = models.CharField(null=True, blank=False, max_length=80, verbose_name='First Name')
    last_name = models.CharField(null=True, blank=False, max_length=80, verbose_name='Last Name')
    phone_number = models.IntegerField(blank=False, null=True, verbose_name='Phone Number')
    country = models.CharField(max_length=255, blank=False, null=True, verbose_name='Country')
    date_joined = models.DateTimeField(verbose_name='Date Joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='Last Login', auto_now_add=True)
    active = models.BooleanField(default=True, verbose_name='Is Active')
    admin = models.BooleanField(default=False, verbose_name='Is Admin')
    staff = models.BooleanField(default=False, verbose_name='Is Staff')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_short_name(self):
        if self.first_name:
            return self.first_name
        return self.email

    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email


    @property
    def is_active(self):
        return self.active

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_superuser(self):
        return self.admin




class Currency_files(models.Model):
    currency_name=models.CharField(max_length=100)
    currency_code=models.CharField(max_length=100)





df_currency_file=pd.read_csv("C:\\Users\\ekrem\\anaconda3\envs\\djangoenv\\pandas cvs dosyaları\\currenciees.csv", encoding = "ISO-8859-1", header=0, skip_blank_lines=True)
df_currency_file = df_currency_file.sort_values('Currency_name')
df_currency_file=df_currency_file.set_index("Currency_name")

idx = ['Turkish lira','European euro','United States Dollar'] + [i for i in df_currency_file.index if i not in ['Turkish lira','European euro','United States Dollar']]
df_currency_file = df_currency_file.reindex(idx)
df_currency_file.reset_index(drop=False,inplace=True)

crrncy = []
for i in range(len(df_currency_file)):
    crrncy=Currency_files.objects.get_or_create(                             #csv dosya okuma
    currency_name=df_currency_file.iloc[i][0],
    currency_code=df_currency_file.iloc[i][1],
)



class Country_files(models.Model):
    country_code=models.CharField(max_length=100)
    country_name=models.CharField(max_length=100)




df_iso_country=pd.read_csv("C:\\Users\\ekrem\\anaconda3\envs\\djangoenv\\pandas cvs dosyaları\\iso_2digit_alpha_country_codes.csv", encoding = "ISO-8859-1", header=0, skip_blank_lines=True)
df_iso_country = df_iso_country.sort_values('Country_name')

cntry = []
for i in range(len(df_iso_country)):
    cntry=Country_files.objects.get_or_create(
        country_code=df_iso_country.iloc[i][0],
        country_name=df_iso_country.iloc[i][1],
    )

class XpayAccount(models.Model):
    email = models.ForeignKey(MyUser,on_delete=models.CASCADE)
    currency = models.CharField(max_length=100)
    date_opened = models.DateTimeField(auto_now_add=True)
    iban_no=models.CharField(max_length=100)
    account_number=models.AutoField(primary_key=True)
    account_number2=models.CharField(max_length=50)
    account_status=models.CharField(max_length=10, default='open')





    def save(self,*args, **kwargs):
        self.iban_no =self.email.country + self.currency + self.account_number2
        super(XpayAccount, self).save(*args, **kwargs)




@receiver(post_save, sender=XpayAccount)
def account_number_digit(sender,created, instance, **kwargs):
    if created:
        instance.account_number2 = "%016d" % instance.pk
        instance.save()

    




class AccountTransaction(models.Model):
    xpayaccount = models.ForeignKey(XpayAccount , on_delete=models.CASCADE)
    sender_iban_no=models.CharField(max_length=80)
    sender_full_name=models.CharField(max_length=80)
    receiver_iban_no=models.CharField(max_length=80)
    xpay_iban_no=models.CharField(max_length=80)
    date_of_transaction = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    receiver_full_name=models.CharField(max_length=80)
    receiver_bank_name=models.CharField(max_length=80)
    sender_bank_name=models.CharField(max_length=80)
    account_balance=models.IntegerField(default=0)
    amount=models.IntegerField()




    def save(self,*args, **kwargs):
        account_balance_last = AccountTransaction.objects.filter(xpay_iban_no=self.xpay_iban_no).aggregate(sum=Sum('amount'))['sum'] or 0
        if  (account_balance_last < -self.amount) and (self.xpay_iban_no==self.sender_iban_no):
            return account_balance_last
        else:
            self.account_balance = self.amount + account_balance_last
        super(AccountTransaction, self).save(*args, **kwargs)





