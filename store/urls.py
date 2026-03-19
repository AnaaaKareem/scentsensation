from django.conf.urls import handler404
from django.shortcuts import render
from django.urls import path
from . import views

def custom_404(request, exception):
    return render(request, '404.html', status=404)

urlpatterns = [
    path('', views.home, name='homepage'),
    path('signup/', views.signup, name='signupAccount'),
    path('signin/', views.signin, name='signinAccount'),
    path('signout/', views.signout, name='signout'),
    path('account/', views.account, name='account'),
    path('store/', views.store, name='store'),
    path('basket/', views.basket, name='basket'),
    path('basket/delete/<int:product_id>/', views.delete_from_basket, name='delete_from_basket'),
    path('basket/add/<int:product_id>/', views.add_quantity, name='add_quantity'),
    path('basket/remove/<int:product_id>/', views.remove_quantity, name='remove_quantity'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('verify_2fa/', views.verify_2fa, name='verify_2fa')
]