from django.conf.urls import handler404
from django.shortcuts import render
from django.urls import path
from . import views, views_admin

def custom_404(request, exception):
    return render(request, 'store/404.html', status=404)

urlpatterns = [
    path('', views.home, name='homepage'),
    path('signup/', views.signup, name='signupAccount'),
    path('signin/', views.signin, name='signinAccount'),
    path('signout/', views.signout, name='signout'),
    path('account/', views.account, name='account'),
    path('brands/', views.brand_list, name='brand_list'),
    path('brands/<slug:slug>/', views.brand_detail, name='brand_detail'),
    path('store/', views.store, name='store'),
    path('store/product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('basket/', views.basket, name='basket'),
    path('basket/delete/<int:product_id>/', views.delete_from_basket, name='delete_from_basket'),
    path('basket/add/<int:product_id>/', views.add_quantity, name='add_quantity'),
    path('basket/remove/<int:product_id>/', views.remove_quantity, name='remove_quantity'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment_success/', views.payment_success, name='payment_success'),
    
    # Admin Portal prefixed with /admin-portal/
    path('admin-portal/', views_admin.admin_login, name='admin_portal'),
    path('admin-portal/login/', views_admin.admin_login, name='admin_login'),
    path('admin-portal/logout/', views_admin.admin_logout, name='admin_logout'),
    path('admin-portal/dashboard/', views_admin.admin_dashboard, name='admin_dashboard'),
    path('admin-portal/tier/save/', views_admin.tier_save, name='tier_save'),
    path('admin-portal/tier/toggle/<int:tier_id>/', views_admin.tier_toggle, name='tier_toggle'),
    path('admin-portal/product/add/', views_admin.add_product, name='add_product'),
    path('admin-portal/inventory/', views_admin.manage_inventory, name='manage_inventory'),
    path('admin-portal/customers/', views_admin.view_customers, name='view_customers'),
    path('admin-portal/reports/', views_admin.export_reports, name='export_reports'),

    path('verify_2fa/', views.verify_2fa, name='verify_2fa'),
    path('resend_2fa/', views.resend_2fa, name='resend_2fa'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('membership/', views.membership_page, name='membership'),
    path('membership/checkout/', views.membership_checkout, name='membership_checkout'),
    path('membership/success/', views.membership_success, name='membership_success'),
    path('membership/failure/', views.membership_failure, name='membership_failure'),
    path('membership/cancel/', views.membership_cancel, name='membership_cancel'),
    path('paypal/success/', views.paypal_success, name='paypal_success'),
    path('paypal/cancel/', views.paypal_cancel, name='paypal_cancel'),
    path('promo/', views.promo_generate, name='promo_generate'),
    path('promo/list/', views.promo_list, name='promo_list'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.wishlist_add, name='wishlist_add'),
    path('wishlist/remove/<int:product_id>/', views.wishlist_remove, name='wishlist_remove'),
    path('wishlist/check/<int:product_id>/', views.wishlist_check, name='wishlist_check'),
]
