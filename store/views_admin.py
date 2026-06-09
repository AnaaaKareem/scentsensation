from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum, Count, F, Q
from functools import wraps
import json
import base64
from datetime import datetime, timedelta

from .models import (
    Customer, Products, PersonalFragrances, HomeFragrances, ProductImages,
    Orders, OrderItems, MembershipTier, Membership, DiscountRate, Store, Inventory
)
from .supabase_client import get_supabase_client

# Decorator to restrict access to authenticated admin users
def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('admin_user_id'):
            messages.warning(request, "Please log in to access the Admin Portal.")
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def admin_login(request):
    """Sign in admin user using Supabase Auth."""
    if request.session.get('admin_user_id'):
        return redirect('admin_dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not email or not password:
            messages.error(request, "Please enter both email and password.")
            return render(request, 'store/admin/admin_login.html')

        supabase = get_supabase_client()
        try:
            # Authenticate via Supabase SDK
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            
            # Check user role / metadata if applicable
            user_data = response.user
            is_admin = user_data.user_metadata.get('is_admin', False) if user_data.user_metadata else False
            
            # Allow login if email starts with 'admin' (for mock/demo safety) or metadata matches
            if is_admin or email.lower().startswith('admin'):
                request.session['admin_user_id'] = user_data.id
                request.session['admin_email'] = user_data.email
                messages.success(request, f"Welcome back, {email}!")
                return redirect('admin_dashboard')
            else:
                messages.error(request, "Access denied. You do not have admin privileges.")
                supabase.auth.sign_out()
        except Exception as e:
            messages.error(request, f"Authentication failed: {str(e)}")

    return render(request, 'store/admin/admin_login.html')


def admin_logout(request):
    """Log out admin user and clear session."""
    supabase = get_supabase_client()
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    request.session.pop('admin_user_id', None)
    request.session.pop('admin_email', None)
    messages.success(request, "You have been logged out.")
    return redirect('admin_login')


@admin_required
def admin_dashboard(request):
    """Render dashboard KPI metrics, memberships, and recent sales."""
    total_orders = Orders.objects.count()
    total_products = Products.objects.count()
    total_customers = Customer.objects.count()
    total_revenue = OrderItems.objects.aggregate(total=Sum(F('quantity') * F('price')))['total'] or 0
    top_product = OrderItems.objects.values('product__product_name').annotate(total_sold=Sum('quantity')).order_by('-total_sold').first()
    membership_data = Membership.objects.filter(is_active=True, tier__isnull=False).values('tier__name').annotate(count=Count('member_id')).order_by('tier__name')
    membership_tiers = MembershipTier.objects.all().order_by('monthly_price')
    total_members = Membership.objects.filter(is_active=True).count()

    # Recent orders with customer info
    recent_orders = Orders.objects.all().order_by('-order_date')[:10]

    # Top products by sales
    top_products = OrderItems.objects.values(
        'product__product_name', 'product__brand'
    ).annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]

    context = {
        'total_orders': total_orders,
        'total_products': total_products,
        'total_customers': total_customers,
        'total_revenue': round(float(total_revenue), 2),
        'top_product': top_product,
        'membership_data': membership_data,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'membership_tiers': membership_tiers,
        'total_members': total_members,
    }
    return render(request, 'store/admin/admin_dashboard.html', context)


@admin_required
def tier_save(request):
    """Save (Add or Edit) a membership tier."""
    if request.method == 'POST':
        tier_id = request.POST.get('tier_id')
        name = request.POST.get('name', '').strip()
        monthly_price = request.POST.get('monthly_price')
        yearly_price = request.POST.get('yearly_price')
        discount_rate = request.POST.get('discount_rate')
        description = request.POST.get('description', '').strip()
        is_active = request.POST.get('is_active') == 'on' or request.POST.get('is_active') == 'true'

        try:
            with transaction.atomic():
                # Ensure discount rate exists in DISCOUNT_RATE
                DiscountRate.objects.get_or_create(
                    member_type=name,
                    defaults={'discount_rate': float(discount_rate)}
                )

                if tier_id:
                    tier = get_object_or_404(MembershipTier, tier_id=tier_id)
                    tier.name = name
                    tier.monthly_price = float(monthly_price)
                    tier.yearly_price = float(yearly_price)
                    tier.discount_rate = float(discount_rate)
                    tier.description = description
                    tier.is_active = is_active
                    tier.save()
                    messages.success(request, f"Membership tier '{name}' updated successfully.")
                else:
                    slug = name.lower().replace(' ', '-')
                    # Avoid slug collision
                    original_slug = slug
                    counter = 1
                    while MembershipTier.objects.filter(slug=slug).exists():
                        slug = f"{original_slug}-{counter}"
                        counter += 1
                    
                    MembershipTier.objects.create(
                        name=name,
                        slug=slug,
                        monthly_price=float(monthly_price),
                        yearly_price=float(yearly_price),
                        discount_rate=float(discount_rate),
                        description=description,
                        is_active=is_active
                    )
                    messages.success(request, f"Membership tier '{name}' created successfully.")
        except Exception as e:
            messages.error(request, f"Error saving tier: {str(e)}")

    return redirect('admin_dashboard')


@admin_required
def tier_toggle(request, tier_id):
    """Enable or disable a membership tier."""
    tier = get_object_or_404(MembershipTier, tier_id=tier_id)
    tier.is_active = not tier.is_active
    tier.save()
    status = "enabled" if tier.is_active else "disabled"
    messages.success(request, f"Membership tier '{tier.name}' has been {status}.")
    return redirect('admin_dashboard')


@admin_required
def add_product(request):
    """Custom page for creating a new product."""
    if request.method == 'POST':
        brand = request.POST.get('brand', '').strip()
        product_name = request.POST.get('product_name', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price')
        region = request.POST.get('region', 'US')
        gift = request.POST.get('gift') == 'on'
        
        category = request.POST.get('category')  # 'Personal' or 'Home'
        image_file = request.FILES.get('image')

        try:
            with transaction.atomic():
                # 1. Create main product
                product = Products.objects.create(
                    brand=brand,
                    product_name=product_name,
                    description=description,
                    price=float(price),
                    gift=gift,
                    region=region
                )

                # 2. Add Base64 Image if uploaded
                if image_file:
                    image_data = image_file.read()
                    base64_str = base64.b64encode(image_data).decode('utf-8')
                    ProductImages.objects.create(
                        product=product,
                        image=base64_str
                    )

                # 3. Create specific sub-type details
                if category == 'Personal':
                    size = request.POST.get('personal_size', '100ml').strip()
                    fragrance_family = request.POST.get('personal_family', 'Floral')
                    gender = request.POST.get('personal_gender', 'Female')
                    strength = request.POST.get('personal_strength', 'Eau de Parfum')
                    
                    PersonalFragrances.objects.create(
                        product=product,
                        size=size,
                        fragrance_family=fragrance_family,
                        gender=gender,
                        strength=strength
                    )
                elif category == 'Home':
                    product_type = request.POST.get('home_type', 'Scented Candles')
                    bundle = request.POST.get('home_bundle') == 'on'

                    HomeFragrances.objects.create(
                        product=product,
                        product_type=product_type,
                        bundle=bundle
                    )

                messages.success(request, f"Product '{product_name}' added successfully!")
                return redirect('admin_dashboard')
        except Exception as e:
            messages.error(request, f"Failed to add product: {str(e)}")

    context = {
        'families': ['Floral', 'Oriental', 'Woody', 'Fresh', 'Citrus', 'Chypre'],
        'strengths': ['Eau de Parfum', 'Eau de Toilette', 'Parfum'],
        'genders': ['Male', 'Female', 'Unisex'],
        'home_types': ['Scent Diffuser', 'Air Freshener', 'Scented Candles', 'Room Sprays', 'Reed Diffusers']
    }
    return render(request, 'store/admin/add_product.html', context)


@admin_required
def manage_inventory(request):
    """View and update store product inventory."""
    stores = Store.objects.all()
    selected_store_id = request.GET.get('store_id') or (stores.first().store_id if stores.exists() else None)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update':
            inventory_id = request.POST.get('inventory_id')
            quantity = request.POST.get('quantity')
            threshold = request.POST.get('threshold')
            
            item = get_object_or_404(Inventory, inventory_id=inventory_id)
            item.quantity = int(quantity)
            item.restocking_threshold = int(threshold)
            item.last_restocking_date = timezone.now().date()
            item.save()
            messages.success(request, f"Inventory updated for {item.product.product_name}.")
        
        elif action == 'add':
            store_id = request.POST.get('store_id')
            product_id = request.POST.get('product_id')
            quantity = request.POST.get('quantity', 0)
            threshold = request.POST.get('threshold', 10)
            
            store = get_object_or_404(Store, store_id=store_id)
            product = get_object_or_404(Products, product_id=product_id)
            
            Inventory.objects.get_or_create(
                store=store,
                product=product,
                defaults={
                    'quantity': int(quantity),
                    'restocking_threshold': int(threshold),
                    'last_restocking_date': timezone.now().date()
                }
            )
            messages.success(request, f"Added {product.product_name} to store inventory.")
            
        return redirect(f"/admin-portal/inventory/?store_id={selected_store_id}")

    inventory_items = []
    available_products = Products.objects.all()
    
    if selected_store_id:
        inventory_items = Inventory.objects.filter(store_id=selected_store_id).select_related('product')
        # Exclude products already in inventory for this store
        existing_product_ids = inventory_items.values_list('product_id', flat=True)
        available_products = available_products.exclude(product_id__in=existing_product_ids)

    context = {
        'stores': stores,
        'selected_store_id': int(selected_store_id) if selected_store_id else None,
        'inventory_items': inventory_items,
        'available_products': available_products
    }
    return render(request, 'store/admin/manage_inventory.html', context)


@admin_required
def view_customers(request):
    """Search and filter customer list with membership info."""
    query = request.GET.get('q', '').strip()
    tier_filter = request.GET.get('tier', '').strip()
    
    customers = Customer.objects.all().prefetch_related('membership__tier')
    
    if query:
        customers = customers.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email_address__icontains=query)
        )
        
    if tier_filter:
        if tier_filter == 'None':
            customers = customers.filter(membership__isnull=True)
        else:
            customers = customers.filter(membership__tier__name=tier_filter, membership__is_active=True)

    tiers = MembershipTier.objects.values_list('name', flat=True)
    
    context = {
        'customers': customers,
        'tiers': tiers,
        'selected_tier': tier_filter,
        'search_query': query
    }
    return render(request, 'store/admin/view_customers.html', context)


@admin_required
def export_reports(request):
    """Overview of business stats and printable reports."""
    # Compute sales over time (last 30 days)
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    orders = Orders.objects.filter(order_date__gte=thirty_days_ago)
    
    daily_sales = {}
    for o in orders:
        day_str = o.order_date.strftime('%Y-%m-%d')
        daily_sales[day_str] = daily_sales.get(day_str, 0) + o.total_payment

    # Order status breakdown
    status_data = Orders.objects.values('order_status').annotate(count=Count('order_id'))
    
    # Payment method breakdown
    payment_data = Orders.objects.values('payment_method').annotate(count=Count('order_id'))
    
    # Check if printing HTML or PDF (by passing a flag)
    print_mode = request.GET.get('print') == 'true'
    
    context = {
        'daily_sales': sorted(daily_sales.items()),
        'status_data': status_data,
        'payment_data': payment_data,
        'report_date': today.strftime('%d %B %Y'),
        'total_revenue': round(float(OrderItems.objects.aggregate(total=Sum(F('quantity') * F('price')))['total'] or 0), 2),
        'total_orders': Orders.objects.count(),
        'total_members': Membership.objects.filter(is_active=True).count(),
        'total_customers': Customer.objects.count()
    }
    
    if print_mode:
        return render(request, 'store/admin/print_report.html', context)
        
    return render(request, 'store/admin/export_reports.html', context)
