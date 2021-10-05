from django.urls import path, include
from . import views

#app_name = 'accounts'

urlpatterns = [
    path('login/', views.registration_view, name='registration_view'),
    path('login_view/',views.login_view,name='login_view'),
    path('logout/', views.logout_view, name='logout'),
    path('myaccount/', views.my_account, name='myaccount'),
    path('user/feedback/',views.FeedbackCreateView.as_view(),name='user_feedback'),
    path('help/',views.HelpCreateView.as_view(),name='help'),
    path('account/add_bio/',views.user_add_bio,name='add_bio'),
    path('account/extend/', views.account_extend, name='account_extend'),
    path('account/step/', views.account_step, name='account_step'),
    path('account/activate/<uidb64>/<token>/',views.activate, name='activate'),
    path('account/<int:pk>/<str:name>/<str:username>/<slug:slug>/',views.account_detail,name='account_detail'),
    path('account/verify/message/',views.account_verify_message,name='account_verify_message'),
    path('account/not_verified/message/',views.account_notverified_message,name='account_notverified_message'),
    path('validate/name/username/',views.validate_name_username,name='validate_name_username'),
    path('validate/email/phone/',views.validate_email_phone,name='validate_email_phone'),



]