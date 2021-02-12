from django.urls import path
from . import views
from django.conf.urls import url


urlpatterns = [

    path('', views.home_page, name='home_page'),
    path('login_page/', views.login_page, name='login_page'),
    path('signup_page/', views.signup_page, name='signup_page'),
    path('profile_page/', views.profile_page, name='profile_page'),
    path('my_xpay_account_page/', views.my_xpay_account_page, name='my_xpay_account_page'),
    path('open_and_close_account_page/', views.open_and_close_account_page, name='open_and_close_account_page'),
    path('money_depositing_page/', views.money_depositing_page, name='money_depositing_page'),
    path('money_depositing_confirmation_page/', views.money_depositing_confirmation_page, name='money_depositing_confirmation_page'),
    path('send_money_page/', views.send_money_page, name='send_money_page'),
    path('send_money_confirmation_page/', views.send_money_confirmation_page, name='send_money_confirmation_page'),
    path('my_xpay_account_page/<int:account_number>', views.detail, name='detail'),
    path('user_profile_page', views.user_profile_page, name='user_profile_page'),


]