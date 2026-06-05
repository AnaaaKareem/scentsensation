"""
Views for the ScentSensation store app.
All database interactions use Django ORM instead of raw SQL.
"""

from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.db.models import Q, Count, Sum, F, Sum as _Sum
from django.db import transaction
from .models import *
from .forms import *
import stripe
import random
import paypalrestsdk

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Initialize PayPal
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET,
})


def home(request):
    return render(request, 'store/homepage.html')


def signup(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                with transaction.atomic():
                    # Create customer
                    customer = Customer.objects.create(
                        first_name=data['first_name'],
                        middle_name=data.get('middle_name', ''),
                        last_name=data['last_name'],
                        DOB=data['DOB'],
                        gender=data['gender'],
                        email_address=data['email_address'],
                        password=make_password(data['password1'])
                    )
                    # Phone number
                    phone = data.get('phone_numbers')
                    if phone:
                        PhoneNumbers.objects.create(customer=customer, phone_number=phone)
                    # Address
                    if all(k in data for k in ['house', 'street_name', 'town_city', 'county', 'postcode', 'country']):
                        Addresses.objects.create(
                            customer=customer,
                            house=data['house'],
                            street_name=data['street_name'],
                            town_city=data['town_city'],
                            county=data['county'],
                            postcode=data['postcode'],
                            country=data['country']
                        )
                    # Membership
                    member = data.get('membership')
                    if member and member != 'None':
                        try:
                            tier = MembershipTier.objects.get(slug=member, is_active=True)
                            from django.utils import timezone
                            Membership.objects.create(
                                customer=customer,
                                tier=tier,
                                is_active=True,
                                end_date=timezone.now() + timedelta(days=30)
                            )
                        except MembershipTier.DoesNotExist:
                            pass
                messages.success(request, "User registered successfully!")
                return redirect('homepage')
            except Exception as e:
                messages.error(request, f"Error during registration: {e}")
                return redirect('signupAccount')
    else:
        form = UserRegistrationForm()
    return render(request, 'store/signup.html', {
        'form': form,
        'countries': get_country_choices(),
        'us_states': get_us_state_choices(),
    })


def signin(request):
    remember_checked = False
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember') == 'on'
        remember_checked = remember
        try:
            customer = Customer.objects.get(email_address=email)
            if check_password(password, customer.password):
                # If "remember me" is checked, extend session to 30 days
                if remember:
                    request.session.set_expiry(2592000)  # 30 days in seconds
                else:
                    request.session.set_expiry(0)  # expire when browser closes
                verification_code = random.randint(100000, 999999)
                print(verification_code)
                request.session['2fa_code'] = str(verification_code)
                request.session['2fa_expires'] = (datetime.now() + timedelta(minutes=5)).isoformat()
                request.session['2fa_email'] = email
                # Render HTML email template
                html_message = render_to_string('store/2fa_email.html', {
                    'verification_code': verification_code,
                    'email': email,
                })
                plain_message = strip_tags(html_message)
                send_mail(
                    'Your 2FA Code',
                    plain_message,
                    settings.EMAIL_HOST_USER,
                    [email],
                    html_message=html_message,
                    fail_silently=False,
                )
                return redirect('verify_2fa')
            else:
                messages.error(request, 'Invalid email or password')
        except Customer.DoesNotExist:
            messages.error(request, 'Invalid email or password')
    return render(request, 'store/signin.html', {'remember_checked': remember_checked})


def verify_2fa(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        session_code = request.session.get('2fa_code')
        expires_at = request.session.get('2fa_expires')
        email = request.session.get('2fa_email')
        if session_code and datetime.fromisoformat(expires_at) > datetime.now():
            if code == session_code:
                try:
                    customer = Customer.objects.get(email_address=email)
                    request.session['customer_id'] = customer.customer_id
                    request.session['first_name'] = customer.first_name
                    request.session['middle_name'] = customer.middle_name or ''
                    request.session['last_name'] = customer.last_name
                    request.session['email_address'] = email
                    request.session['gender'] = customer.gender
                    if customer.DOB:
                        request.session['DOB'] = customer.DOB.isoformat()

                    # Address (first one)
                    address = customer.addresses.first()
                    if address:
                        request.session['house'] = address.house
                        request.session['street_name'] = address.street_name
                        request.session['town_city'] = address.town_city
                        request.session['county'] = address.county
                        request.session['postcode'] = address.postcode
                        request.session['country'] = address.country

                    # Phone numbers
                    phone_numbers = list(customer.phonenumbers.values_list('phone_number', flat=True))
                    request.session['phone_numbers'] = phone_numbers

                    # Membership
                    membership = getattr(customer, 'membership', None)
                    if membership and membership.tier:
                        request.session['membership'] = {
                            'member_id': membership.member_id,
                            'tier_name': membership.tier.name,
                            'tier_slug': membership.tier.slug,
                            'discount_rate': membership.tier.discount_rate,
                            'end_date': membership.end_date.isoformat() if membership.end_date else None,
                            'is_active': membership.is_active,
                        }

                    # Clean up 2FA session data
                    request.session.pop('2fa_code', None)
                    request.session.pop('2fa_expires', None)
                    request.session.pop('pending_customer', None)

                    return redirect('homepage')
                except Customer.DoesNotExist:
                    messages.error(request, 'Customer not found')
                    return redirect('signinAccount')
            else:
                messages.error(request, 'Invalid 2FA code')
                return render(request, 'store/verify_2fa.html')
        else:
            messages.error(request, '2FA code expired. Please login again.')
            return redirect('signinAccount')
    return render(request, 'store/verify_2fa.html')


def resend_2fa(request):
    if request.method == 'POST':
        email = request.session.get('2fa_email')
        if email:
            verification_code = random.randint(100000, 999999)
            request.session['2fa_code'] = str(verification_code)
            request.session['2fa_expires'] = (datetime.now() + timedelta(minutes=5)).isoformat()
            html_message = render_to_string('store/2fa_email.html', {
                'verification_code': verification_code,
                'email': email,
            })
            plain_message = strip_tags(html_message)
            send_mail(
                'Your 2FA Code',
                plain_message,
                settings.EMAIL_HOST_USER,
                [email],
                html_message=html_message,
                fail_silently=False,
            )
    return redirect(reverse('verify_2fa') + '?resent=1')


def signout(request):
    request.session.flush()
    return redirect('signinAccount')


def account(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('signinAccount')

    if request.method == 'GET':
        try:
            customer = Customer.objects.get(customer_id=customer_id)
            # Update session
            request.session['first_name'] = customer.first_name
            request.session['middle_name'] = customer.middle_name or ''
            request.session['last_name'] = customer.last_name
            request.session['email_address'] = customer.email_address
            request.session['DOB'] = customer.DOB.isoformat() if customer.DOB else ''
            request.session['gender'] = customer.gender

            address = customer.addresses.first()
            if address:
                request.session['house'] = address.house
                request.session['street_name'] = address.street_name
                request.session['town_city'] = address.town_city
                request.session['county'] = address.county
                request.session['postcode'] = address.postcode
                request.session['country'] = address.country

            membership = getattr(customer, 'membership', None)
            if membership and membership.tier:
                request.session['membership'] = membership.tier.name
            else:
                request.session.pop('membership', None)

        except Customer.DoesNotExist:
            messages.error(request, "Customer not found")
            return redirect('signinAccount')

    if request.method == 'POST':
        if 'update' in request.POST:
            form = UserUpdateForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                try:
                    with transaction.atomic():
                        customer = Customer.objects.get(customer_id=customer_id)
                        # Update customer fields
                        if data.get('first_name'):
                            customer.first_name = data['first_name']
                        if data.get('middle_name') is not None:
                            customer.middle_name = data['middle_name']
                        if data.get('last_name'):
                            customer.last_name = data['last_name']
                        if data.get('email_address'):
                            customer.email_address = data['email_address']
                        if data.get('DOB'):
                            customer.DOB = data['DOB']
                        if data.get('gender'):
                            customer.gender = data['gender']
                        if data.get('password'):
                            customer.password = make_password(data['password'])
                        customer.save()

                        # Phone number (single, update or create)
                        phone = data.get('phone_numbers')
                        if phone is not None:
                            PhoneNumbers.objects.update_or_create(customer=customer, defaults={'phone_number': phone})

                        # Address (first record) – only if required fields provided and non-empty
                        if all(k in data and data[k] for k in ['house', 'street_name', 'town_city', 'country']):
                            address, created = Addresses.objects.get_or_create(customer=customer)
                            for field in ['house', 'street_name', 'town_city', 'county', 'postcode', 'country']:
                                if data.get(field):
                                    setattr(address, field, data[field])
                            address.save()

                        # Membership -- remove old dropdown, direct users to /membership/ page
                        # Membership is now managed via the dedicated membership page with Stripe

                    messages.success(request, "Your account information has been updated.")
                    return redirect('account')
                except Exception as e:
                    messages.error(request, f"Error updating account: {e}")
                    return redirect('account')

        elif 'delete' in request.POST:
            try:
                with transaction.atomic():
                    customer = Customer.objects.get(customer_id=customer_id)
                    # Deleting customer cascades to related records due to DB constraints
                    customer.delete()
                request.session.flush()
                return redirect('homepage')
            except Exception as e:
                messages.error(request, f"Error deleting account: {e}")
                request.session.flush()
                return redirect('homepage')

    current_membership = None
    if customer_id:
        try:
            customer = Customer.objects.get(customer_id=customer_id)
            current_membership = getattr(customer, 'membership', None)
        except Customer.DoesNotExist:
            pass

    context = {
        'first_name': request.session.get('first_name'),
        'middle_name': request.session.get('middle_name', ''),
        'last_name': request.session.get('last_name'),
        'email_address': request.session.get('email_address'),
        'DOB': request.session.get('DOB'),
        'gender': request.session.get('gender'),
        'house': request.session.get('house'),
        'street_name': request.session.get('street_name'),
        'town_city': request.session.get('town_city'),
        'county': request.session.get('county'),
        'postcode': request.session.get('postcode'),
        'country': request.session.get('country'),
        'current_membership': current_membership,
        'membership': current_membership.tier.name if (current_membership and current_membership.is_active and current_membership.tier) else None
    }
    return render(request, 'store/accountInfo.html', context)


def store(request):
    all_products = Products.objects.all()
    images = ProductImages.objects.all()  # not used? template uses reverse relation

    category_filter = request.GET.getlist('category')
    if category_filter:
        q_objects = Q()
        if 'Personal Fragrances' in category_filter:
            q_objects |= Q(personal_fragrance__isnull=False)
        if 'Home Fragrances' in category_filter:
            q_objects |= Q(home_fragrance__isnull=False)
        all_products = all_products.filter(q_objects)

    gender_filter = request.GET.getlist('gender')
    if gender_filter:
        all_products = all_products.filter(personal_fragrance__gender__in=gender_filter)

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        all_products = all_products.filter(price__gte=min_price)
    if max_price:
        all_products = all_products.filter(price__lte=max_price)

    sort_map = {
        'featured': None,
        'price_low': 'price',
        'price_high': '-price',
        'newest': '-product_id',
        'name_az': 'product_name',
    }
    sort_param = request.GET.get('sort', 'featured')
    order_field = sort_map.get(sort_param)
    if order_field:
        all_products = all_products.order_by(order_field)

    paginator = Paginator(all_products, 6)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    if request.method == "POST" and "add_basket" in request.POST:
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity", 1))
        customer_id = request.session.get('customer_id')
        if not customer_id:
            return redirect('signinAccount')
        basket_item, created = Basket.objects.get_or_create(
            customer_id=customer_id,
            product_id=product_id,
            defaults={'quantity': quantity}
        )
        if not created:
            basket_item.quantity += quantity
            basket_item.save()
        return redirect('store')

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'sort': sort_param,
    }
    return render(request, 'store/storepage.html', context)


def product_detail(request, product_id):
    product = get_object_or_404(Products, product_id=product_id)
    images = ProductImages.objects.filter(product=product)
    personal = PersonalFragrances.objects.filter(product=product).first()
    home = HomeFragrances.objects.filter(product=product).first()
    context = {
        'product': product,
        'images': images,
        'personal': personal,
        'home': home,
    }
    return render(request, 'store/product_detail.html', context)


def basket(request):
    import sys
    from django.contrib.sessions.models import Session
    print("BASKET VIEW - COOKIES:", request.COOKIES, file=sys.stderr)
    print("BASKET VIEW - SESSION KEY:", request.session.session_key, file=sys.stderr)
    print("BASKET VIEW - SESSION DATA before access:", dict(request.session), file=sys.stderr)
    # Check DB
    if request.session.session_key:
        try:
            s = Session.objects.get(session_key=request.session.session_key)
            print("BASKET VIEW - DB session_data:", s.session_data, file=sys.stderr)
        except Session.DoesNotExist:
            print("BASKET VIEW - DB: No session found for key", request.session.session_key, file=sys.stderr)
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('signinAccount')

    try:
        customer = Customer.objects.get(customer_id=customer_id)
        basket_items = Basket.objects.filter(customer=customer).select_related('product')
        items = []
        subtotal = 0

        for item in basket_items:
            product = item.product
            image = ProductImages.objects.filter(product=product).first()
            personal = PersonalFragrances.objects.filter(product=product).first()
            home = HomeFragrances.objects.filter(product=product).first()
            total_price = product.price * item.quantity
            subtotal += total_price
            items.append({
                'product': {
                    'product_id': product.product_id,
                    'brand': product.brand,
                    'product_name': product.product_name,
                    'price': product.price
                },
                'quantity': item.quantity,
                'image': image,
                'personal': personal,
                'home': home,
            })

        membership = getattr(customer, 'membership', None)
        discount_rate = membership.tier.discount_rate if membership and membership.tier else 0
        discount = subtotal * (discount_rate / 100)
        total = subtotal - discount

        context = {
            'items': items,
            'subtotal': round(subtotal, 2),
            'discount': round(discount, 2),
            'total': round(total, 2),
            'discount_rate': discount_rate,
            'basket_count': sum(item['quantity'] for item in items),
        }
        request.session['basket_count'] = context['basket_count']
    except Customer.DoesNotExist:
        messages.error(request, "Customer not found")
        return redirect('signinAccount')
    except Exception as e:
        messages.error(request, f"Error: {e}")
        return redirect('signinAccount')

    return render(request, 'store/basket.html', context)


def delete_from_basket(request, product_id):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('signinAccount')
    Basket.objects.filter(customer_id=customer_id, product_id=product_id).delete()
    # Recalculate basket count
    request.session['basket_count'] = Basket.objects.filter(customer_id=customer_id).aggregate(
        total=models.Sum('quantity'))['total'] or 0
    return redirect('basket')


def add_quantity(request, product_id):
    customer_id = request.session.get('customer_id')
    if request.method == 'POST' and customer_id:
        try:
            basket_item, created = Basket.objects.get_or_create(
                customer_id=customer_id,
                product_id=product_id,
                defaults={'quantity': 1}
            )
            if not created:
                basket_item.quantity = F('quantity') + 1
                basket_item.save()
        except Exception as e:
            messages.error(request, f"Error: {e}")
    # Recalculate basket count
    request.session['basket_count'] = Basket.objects.filter(customer_id=customer_id).aggregate(
        total=models.Sum('quantity'))['total'] or 0
    return redirect('basket')


def remove_quantity(request, product_id):
    customer_id = request.session.get('customer_id')
    if request.method == 'POST' and customer_id:
        try:
            basket_item = Basket.objects.get(customer_id=customer_id, product_id=product_id)
            if basket_item.quantity > 1:
                basket_item.quantity = F('quantity') - 1
                basket_item.save()
            else:
                basket_item.delete()
        except Basket.DoesNotExist:
            pass
        except Exception as e:
            messages.error(request, f"Error: {e}")
    # Recalculate basket count
    request.session['basket_count'] = Basket.objects.filter(customer_id=customer_id).aggregate(
        total=models.Sum('quantity'))['total'] or 0
    return redirect('basket')


def checkout(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('homepage')

    # Get fulfilment, payment method, shipping, gift from POST if available
    if request.method == 'POST':
        fulfilment = request.POST.get('fulfilment', 'Delivery')
        payment_method = request.POST.get('payment_method', 'Card')
        selected_store_id = request.POST.get('selected_store_id', '')
        shipping_cost = float(request.POST.get('shipping_cost', 0))
        gift_wrap_cost = float(request.POST.get('gift_wrap_cost', 0))
        promo_code_str = request.POST.get('promo_code', '').strip()
    else:
        fulfilment = request.session.get('fulfilment', 'Delivery')
        payment_method = 'Card'
        selected_store_id = ''
        shipping_cost = 0
        gift_wrap_cost = 0
        promo_code_str = request.GET.get('promo_code', '').strip()

    try:
        customer = Customer.objects.get(customer_id=customer_id)
        basket_items = list(Basket.objects.filter(customer=customer).select_related('product'))
        if not basket_items:
            messages.error(request, "Your basket is empty.")
            return redirect('basket')

        membership = getattr(customer, 'membership', None)
        discount_rate = membership.tier.discount_rate if membership and membership.tier else 0

        subtotal = sum(item.product.price * item.quantity for item in basket_items)
        discount = round(subtotal * (discount_rate / 100), 2)
        total = round(subtotal - discount + shipping_cost + gift_wrap_cost, 2)

        # Promo code handling
        promo_code_obj = None
        promo_discount = 0
        if promo_code_str:
            try:
                promo_code_obj = PromoCode.objects.get(code=promo_code_str)
                if promo_code_obj.redeemed:
                    messages.warning(request, f"Promo code {promo_code_str} has already been redeemed.")
                    promo_code_obj = None
                    promo_code_str = ''
                else:
                    promo_discount = float(promo_code_obj.amount)
                    total = round(total - promo_discount, 2)
                    if total < 0:
                        total = 0
            except PromoCode.DoesNotExist:
                messages.warning(request, f"Promo code {promo_code_str} is not valid.")
                promo_code_str = ''

        # Build items for template display
        items_data = []
        for item in basket_items:
            image = ProductImages.objects.filter(product=item.product).first()
            items_data.append({
                'product': {
                    'product_id': item.product.product_id,
                    'brand': item.product.brand,
                    'product_name': item.product.product_name,
                    'price': item.product.price,
                },
                'quantity': item.quantity,
                'image': image,
            })

        # Get all stores for the map
        stores = Store.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)

        if request.method == 'POST':
            # Store selection validation for pickup
            selected_store = None
            if fulfilment == 'Pickup':
                if selected_store_id:
                    try:
                        selected_store = Store.objects.get(store_id=selected_store_id)
                    except Store.DoesNotExist:
                        messages.error(request, "Selected store not found. Please try again.")
                        return redirect('checkout')
                else:
                    messages.error(request, "Please select a store for pickup.")
                    return redirect('checkout')

            # --- PayPal payment flow ---
            if payment_method == 'PayPal':
                # Build PayPal payment
                item_list = []
                for item in basket_items:
                    item_list.append({
                        "name": f"{item.product.brand} - {item.product.product_name}",
                        "sku": str(item.product.product_id),
                        "price": f"{item.product.price:.2f}",
                        "currency": "GBP",
                        "quantity": item.quantity,
                    })

                payment = paypalrestsdk.Payment({
                    "intent": "sale",
                    "payer": {"payment_method": "paypal"},
                    "redirect_urls": {
                        "return_url": request.build_absolute_uri('/paypal/success/'),
                        "cancel_url": request.build_absolute_uri('/paypal/cancel/'),
                    },
                    "transactions": [{
                        "item_list": {"items": item_list},
                        "amount": {
                            "total": f"{total:.2f}",
                            "currency": "GBP",
                            "details": {
                                "subtotal": f"{subtotal:.2f}",
                                "discount": f"{discount:.2f}",
                                "shipping": f"{shipping_cost:.2f}",
                            },
                        },
                        "description": f"Scent Sensation Order — {fulfilment}",
                    }],
                })

                if payment.create():
                    # Save pending order data in session
                    request.session['pending_checkout'] = {
                        'customer_id': customer_id,
                        'subtotal': str(subtotal),
                        'discount': str(discount),
                        'shipping_cost': str(shipping_cost),
                        'gift_wrap_cost': str(gift_wrap_cost),
                        'total': str(total),
                        'fulfilment': fulfilment,
                        'payment_method': payment_method,
                        'selected_store_id': selected_store_id,
                        'paypal_payment_id': payment.id,
                        'promo_code': promo_code_str,
                        'promo_discount': str(promo_discount),
                    }
                    # Redirect to PayPal approval URL
                    for link in payment.links:
                        if link.rel == "approval_url":
                            return redirect(link.href)
                else:
                    messages.error(request, f"PayPal error: {payment.error}")
                    return redirect('checkout')

            # --- Cash payment flow ---
            elif payment_method == 'Cash':
                with transaction.atomic():
                    order = Orders.objects.create(
                        gift_card=None,
                        order_date=timezone.now(),
                        order_status='Paid',
                        order_type=fulfilment,
                        payment_method='Cash',
                        installment=False,
                        total_payment=total
                    )
                    for item in basket_items:
                        OrderItems.objects.create(
                            order=order,
                            product=item.product,
                            quantity=item.quantity,
                            price=item.product.price
                        )
                        Places.objects.create(
                            customer=customer,
                            product=item.product,
                            order=order
                        )
                    # Clear basket
                    Basket.objects.filter(customer=customer).delete()
                    # Redeem promo code
                    if promo_code_obj:
                        promo_code_obj.redeemed = True
                        promo_code_obj.redeemed_at = timezone.now()
                        promo_code_obj.save()

                request.session['last_order_id'] = order.order_id
                return redirect('payment_success')

            # --- Stripe / Card payment flow ---
            else:
                line_items = []
                for item in basket_items:
                    line_items.append({
                        'price_data': {
                            'currency': 'gbp',
                            'unit_amount': int(item.product.price * 100),
                            'product_data': {
                                'name': f"{item.product.brand} - {item.product.product_name}",
                            },
                        },
                        'quantity': item.quantity,
                    })

                # Add shipping as a line item if applicable
                if shipping_cost > 0:
                    shipping_label = "Express Delivery" if shipping_cost < 9 else "Next Day Delivery"
                    line_items.append({
                        'price_data': {
                            'currency': 'gbp',
                            'unit_amount': int(shipping_cost * 100),
                            'product_data': {
                                'name': shipping_label,
                            },
                        },
                        'quantity': 1,
                    })

                # Add gift wrap as a line item if applicable
                if gift_wrap_cost > 0:
                    line_items.append({
                        'price_data': {
                            'currency': 'gbp',
                            'unit_amount': int(gift_wrap_cost * 100),
                            'product_data': {
                                'name': "Gift Wrapping",
                            },
                        },
                        'quantity': 1,
                    })

                # Discount handling
                if discount_rate > 0:
                    coupon = stripe.Coupon.create(percent_off=int(discount_rate), duration="once")
                    discounts = [{"coupon": coupon}]
                else:
                    discounts = []

                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=line_items,
                    mode='payment',
                    discounts=discounts,
                    success_url=request.build_absolute_uri('/payment_success/') + '?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url=request.build_absolute_uri('/basket/'),
                    metadata={
                        'customer_id': customer_id,
                        'subtotal': str(subtotal),
                        'discount': str(discount),
                        'shipping_cost': str(shipping_cost),
                        'gift_wrap_cost': str(gift_wrap_cost),
                        'total': str(total),
                        'fulfilment': fulfilment,
                        'payment_method': payment_method,
                        'selected_store_id': selected_store_id,
                        'promo_code': promo_code_str,
                        'promo_discount': str(promo_discount),
                    }
                )

                request.session['pending_checkout'] = {
                    'customer_id': customer_id,
                    'subtotal': subtotal,
                    'discount': discount,
                    'shipping_cost': shipping_cost,
                    'gift_wrap_cost': gift_wrap_cost,
                    'total': total,
                    'fulfilment': fulfilment,
                    'payment_method': payment_method,
                    'selected_store_id': selected_store_id,
                    'promo_code': promo_code_str,
                    'promo_discount': str(promo_discount),
                }

                return redirect(session.url, code=303)

        # GET: render checkout page
        context = {
            'items': items_data,
            'subtotal': round(subtotal, 2),
            'discount': round(discount, 2),
            'total': round(total, 2),
            'discount_rate': discount_rate,
            'fulfilment': fulfilment,
            'payment_method': payment_method,
            'stores': stores,
            'selected_store_id': selected_store_id,
            'promo_code': promo_code_str,
            'promo_discount': promo_discount,
        }
        return render(request, 'store/checkout.html', context)

    except Exception as e:
        messages.error(request, f"Checkout error: {e}")
        return redirect('basket')


@csrf_exempt
def payment_success(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        return redirect('homepage')

    try:
        session = stripe.checkout.Session.retrieve(session_id)

        # Verify payment was completed
        if session.payment_status != 'paid':
            messages.error(request, "Payment was not completed. Please try again.")
            return redirect('basket')

        # Ensure session has valid metadata and convert to plain dict
        if not session.metadata:
            messages.error(request, "Invalid payment session metadata")
            return redirect('basket')
        # StripeObject has a to_dict() method for safe conversion
        metadata = session.metadata.to_dict()

        customer_id = metadata.get('customer_id')
        if not customer_id:
            return redirect('homepage')

        with transaction.atomic():
            customer = Customer.objects.get(customer_id=customer_id)
            basket_items = list(Basket.objects.filter(customer=customer).select_related('product'))
            if not basket_items:
                messages.error(request, "Your basket is empty.")
                return redirect('basket')

            # Create order
            order = Orders.objects.create(
                gift_card=None,
                order_date=timezone.now(),
                order_status='Paid',
                order_type=metadata.get('fulfilment', 'Pickup'),
                payment_method=metadata.get('payment_method', 'Card'),
                installment=False,
                total_payment=float(metadata.get('total', 0))
            )

            # Create order items and places
            for item in basket_items:
                OrderItems.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
                Places.objects.create(
                    customer=customer,
                    product=item.product,
                    order=order
                )

            # If pickup, store the selected store in session for receipt
            selected_store_id = metadata.get('selected_store_id', '')
            if selected_store_id:
                try:
                    request.session['pickup_store'] = Store.objects.get(store_id=selected_store_id).name
                except Store.DoesNotExist:
                    pass

            # Clear basket
            Basket.objects.filter(customer=customer).delete()

            # Redeem promo code if one was used
            promo_code_str = metadata.get('promo_code', '')
            if promo_code_str:
                try:
                    promo = PromoCode.objects.get(code=promo_code_str)
                    promo.redeemed = True
                    promo.redeemed_at = timezone.now()
                    promo.save()
                except PromoCode.DoesNotExist:
                    pass

            # Extract totals for email/receipt
            subtotal = float(metadata.get('subtotal', 0))
            discount = float(metadata.get('discount', 0))
            total = float(metadata.get('total', 0))
            discount_rate = int((discount / subtotal * 100) if subtotal else 0)
    except Exception as e:
        import traceback
        import sys
        tb = traceback.format_exc()
        # Print full error details to console for debugging
        print("=" * 80, file=sys.stderr)
        print(f"PAYMENT ERROR - Type: {type(e).__name__}", file=sys.stderr)
        print(f"PAYMENT ERROR - Message: {str(e)}", file=sys.stderr)
        print(f"PAYMENT ERROR - Args: {e.args}", file=sys.stderr)
        print(f"PAYMENT ERROR - Metadata: {metadata if 'metadata' in locals() else 'N/A'}", file=sys.stderr)
        print(f"PAYMENT ERROR - Customer ID: {customer_id if 'customer_id' in locals() else 'N/A'}", file=sys.stderr)
        print(f"PAYMENT ERROR - Subtotal: {subtotal if 'subtotal' in locals() else 'N/A'}", file=sys.stderr)
        print(f"PAYMENT ERROR - Full traceback:\n{tb}", file=sys.stderr)
        print("=" * 80, file=sys.stderr)
        messages.error(request, f"Payment processing error: {e}")
        return redirect('basket')

    # Send confirmation email
    # Prepare items data for templates (flat structure)
    items_data = []
    for item in basket_items:
        image = ProductImages.objects.filter(product=item.product).first()
        items_data.append({
            'brand': item.product.brand,
            'product_name': item.product.product_name,
            'price': item.product.price,
            'quantity': item.quantity,
            'image': image,
        })

    subject = f"Order #{order.order_id}"
    html_message = render_to_string('store/receipt.html', {
        'customer_email': request.session.get('email_address'),
        'order_id': order.order_id,
        'items': items_data,
        'subtotal': round(subtotal, 2),
        'discount_rate': discount_rate,
        'discount': round(discount, 2),
        'total': round(total, 2),
    })
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [request.session.get('email_address')]
    send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)

    return render(request, 'store/payment_success.html', {
        'order_id': order.order_id,
        'items': items_data,
        'subtotal': round(subtotal, 2),
        'discount_rate': discount_rate,
        'discount': round(discount, 2),
        'total': round(total, 2)
    })


def admin_dashboard(request):
    total_orders = Orders.objects.count()
    total_products = Products.objects.count()
    total_customers = Customer.objects.count()
    total_revenue = OrderItems.objects.aggregate(total=Sum(F('quantity') * F('price')))['total'] or 0
    top_product = OrderItems.objects.values('product__product_name').annotate(total_sold=Sum('quantity')).order_by('-total_sold').first()
    membership_data = Membership.objects.filter(is_active=True, tier__isnull=False).values('tier__name').annotate(count=Count('member_id')).order_by('tier__name')
    membership_tiers = MembershipTier.objects.filter(is_active=True).order_by('monthly_price')
    total_members = Membership.objects.filter(is_active=True).count()

    # Recent orders with customer info
    recent_orders = Orders.objects.select_related().prefetch_related('items').order_by('-order_date')[:10]

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
        'total_revenue': round(total_revenue, 2),
        'top_product': top_product,
        'membership_data': membership_data,
        'recent_orders': recent_orders,
        'top_products': top_products,
    }
    return render(request, 'store/admin_dashboard.html', context)


def about(request):
    return render(request, 'store/about.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')

        try:
            from django.core.mail import send_mail as django_send_mail
            from django.conf import settings
            full_subject = f"[Scent Sensation Contact] {subject}"
            full_message = f"From: {name} <{email}>\n\n{message}"
            django_send_mail(
                full_subject,
                full_message,
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_HOST_USER],
                fail_silently=True,
            )
            from django.contrib import messages as django_messages
            django_messages.success(request, "Thank you! Your message has been sent. We'll get back to you soon.")
        except Exception:
            from django.contrib import messages as django_messages
            django_messages.error(request, "Sorry, there was an error sending your message. Please try again later.")

        return redirect('contact')

    return render(request, 'store/contact.html')


def membership_page(request):
    """Display all active membership tiers for subscription."""
    tiers = MembershipTier.objects.filter(is_active=True).annotate(
        subscriber_count=Count('subscriptions', filter=Q(subscriptions__is_active=True))
    ).order_by('monthly_price')
    customer_id = request.session.get('customer_id')
    current_membership = None
    if customer_id:
        try:
            customer = Customer.objects.get(customer_id=customer_id)
            current_membership = getattr(customer, 'membership', None)
        except Customer.DoesNotExist:
            pass

    # Determine the most popular tier based on active subscriptions count
    most_popular_tier = None
    if tiers.exists():
        max_subscribers = max(t.subscriber_count for t in tiers)
        if max_subscribers > 0:
            most_popular_tier = next(t for t in tiers if t.subscriber_count == max_subscribers)
        else:
            # Fallback to the 'elite' slug tier if no subscriptions exist
            most_popular_tier = next((t for t in tiers if t.slug == 'elite'), None)

    context = {
        'tiers': tiers,
        'current_membership': current_membership,
        'most_popular_tier': most_popular_tier,
    }
    return render(request, 'store/membership.html', context)


def membership_checkout(request):
    """Process membership subscription via Stripe Checkout."""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('signinAccount')

    if request.method != 'POST':
        return redirect('membership')

    tier_slug = request.POST.get('tier_slug')
    billing = request.POST.get('billing', 'monthly')

    try:
        tier = MembershipTier.objects.get(slug=tier_slug, is_active=True)
    except MembershipTier.DoesNotExist:
        from django.contrib import messages as django_messages
        django_messages.error(request, "Selected membership tier is not available.")
        return redirect('membership')

    customer = Customer.objects.get(customer_id=customer_id)

    # Determine which price ID to use
    if billing == 'yearly':
        price_id = tier.stripe_yearly_price_id
    else:
        price_id = tier.stripe_monthly_price_id

    # Auto-create Stripe price if not set
    if not price_id:
        try:
            product = stripe.Product.create(
                name=f"Scent Sensation — {tier.name} Membership",
                description=f"{tier.name} plan — {tier.discount_rate}% off all products",
                metadata={'tier_slug': tier.slug, 'tier_id': str(tier.tier_id)},
            )
            if billing == 'yearly':
                price = stripe.Price.create(
                    product=product.id,
                    unit_amount=int(float(tier.yearly_price) * 100),
                    currency='gbp',
                    nickname=f"{tier.name} Yearly",
                )
                price_id = price.id
                # Save for next time
                tier.stripe_yearly_price_id = price_id
                tier.save(update_fields=['stripe_yearly_price_id'])
            else:
                price = stripe.Price.create(
                    product=product.id,
                    unit_amount=int(float(tier.monthly_price) * 100),
                    currency='gbp',
                    recurring={'interval': 'month', 'interval_count': 1},
                    nickname=f"{tier.name} Monthly",
                )
                price_id = price.id
                # Save for next time
                tier.stripe_monthly_price_id = price_id
                tier.save(update_fields=['stripe_monthly_price_id'])
        except Exception as e:
            from django.contrib import messages as django_messages
            django_messages.error(request, f"Error setting up payment: {e}")
            return redirect('membership')

    try:
        is_recurring = billing == 'monthly'
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='subscription' if is_recurring else 'payment',
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            success_url=request.build_absolute_uri('/membership/success/') + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri('/membership/failure/'),
            metadata={
                'customer_id': customer_id,
                'tier_id': tier.tier_id,
                'tier_slug': tier.slug,
                'billing': billing,
            }
        )
        return redirect(session.url, code=303)
    except Exception as e:
        from django.contrib import messages as django_messages
        django_messages.error(request, f"Error creating checkout session: {e}")
        return redirect('membership')


def membership_success(request):
    """Handle successful membership payment."""
    session_id = request.GET.get('session_id')
    if not session_id:
        return redirect('homepage')

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        # For payment mode: payment_status == 'paid'; for subscription mode: status == 'complete'
        if session.payment_status == 'paid' or session.status == 'complete':
            metadata = session.metadata
            customer_id = metadata['customer_id']
            tier_id = metadata['tier_id']
            billing = metadata['billing'] if 'billing' in metadata else 'monthly'

            if customer_id and tier_id:
                customer = Customer.objects.get(customer_id=customer_id)
                tier = MembershipTier.objects.get(tier_id=tier_id)

                # Calculate end date based on billing period
                from django.utils import timezone
                if billing == 'yearly':
                    end_date = timezone.now() + timezone.timedelta(days=365)
                else:
                    end_date = timezone.now() + timezone.timedelta(days=30)

                # Update or create membership
                Membership.objects.update_or_create(
                    customer=customer,
                    defaults={
                        'tier': tier,
                        'is_active': True,
                        'end_date': end_date.date(),
                        'start_date': timezone.now().date(),
                    }
                )

                # Update session
                request.session['membership'] = tier.name

                # Calculate next payment date
                if billing == 'yearly':
                    next_payment_date = end_date.date()
                else:
                    from django.utils import timezone as tz
                    next_payment_date = (tz.now() + tz.timedelta(days=30)).date()

                return render(request, 'store/membership_success.html', {
                    'tier': tier,
                    'billing': billing,
                    'start_date': timezone.now().date(),
                    'end_date': end_date.date(),
                    'next_payment_date': next_payment_date,
                })
    except Exception as e:
        from django.contrib import messages as django_messages
        django_messages.error(request, f"Error activating membership: {e}")

    return redirect('membership')


def membership_failure(request):
    """Handle failed membership payment (user clicked cancel on Stripe)."""
    return render(request, 'store/membership_failure.html')


def membership_cancel(request):
    """Cancel current membership."""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('signinAccount')

    if request.method == 'POST':
        try:
            customer = Customer.objects.get(customer_id=customer_id)
            membership = getattr(customer, 'membership', None)
            if membership:
                membership.is_active = False
                membership.auto_renew = False
                membership.save()
                request.session.pop('membership', None)
                from django.contrib import messages as django_messages
                django_messages.success(request, "Your membership has been cancelled.")
        except Exception:
            pass

    return redirect('membership')


def paypal_success(request):
    """Handle PayPal return after user approves payment."""
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    if not payment_id or not payer_id:
        messages.error(request, "PayPal payment was not completed.")
        return redirect('basket')

    pending = request.session.get('pending_checkout')
    if not pending or pending.get('paypal_payment_id') != payment_id:
        messages.error(request, "Invalid PayPal session. Please try again.")
        return redirect('basket')

    try:
        payment = paypalrestsdk.Payment.find(payment_id)

        if payment.execute({"payer_id": payer_id}):
            # Payment executed successfully — create the order
            customer_id = pending['customer_id']
            customer = Customer.objects.get(customer_id=customer_id)
            basket_items = list(Basket.objects.filter(customer=customer).select_related('product'))

            subtotal = float(pending['subtotal'])
            discount = float(pending['discount'])
            total = float(pending['total'])
            fulfilment = pending['fulfilment']
            selected_store_id = pending.get('selected_store_id', '')

            with transaction.atomic():
                order = Orders.objects.create(
                    gift_card=None,
                    order_date=timezone.now(),
                    order_status='Paid',
                    order_type=fulfilment,
                    payment_method='PayPal',
                    installment=False,
                    total_payment=total,
                )

                for item in basket_items:
                    OrderItems.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price,
                    )
                    Places.objects.create(
                        customer=customer,
                        product=item.product,
                        order=order,
                    )

                # If pickup, store the selected store name for receipt
                if selected_store_id:
                    try:
                        request.session['pickup_store'] = Store.objects.get(store_id=selected_store_id).name
                    except Store.DoesNotExist:
                        pass

                # Clear basket
                Basket.objects.filter(customer=customer).delete()

                # Redeem promo code if one was used
                promo_code_used = pending.get('promo_code', '')
                if promo_code_used:
                    try:
                        promo = PromoCode.objects.get(code=promo_code_used)
                        promo.redeemed = True
                        promo.redeemed_at = timezone.now()
                        promo.save()
                    except PromoCode.DoesNotExist:
                        pass

            # Clear pending checkout
            request.session.pop('pending_checkout', None)

            # Send confirmation email
            items_data = []
            for item in basket_items:
                image = ProductImages.objects.filter(product=item.product).first()
                items_data.append({
                    'brand': item.product.brand,
                    'product_name': item.product.product_name,
                    'price': item.product.price,
                    'quantity': item.quantity,
                    'image': image,
                })

            discount_rate = int((discount / subtotal * 100) if subtotal else 0)

            subject = f"Order #{order.order_id}"
            html_message = render_to_string('store/receipt.html', {
                'customer_email': request.session.get('email_address'),
                'order_id': order.order_id,
                'items': items_data,
                'subtotal': round(subtotal, 2),
                'discount_rate': discount_rate,
                'discount': round(discount, 2),
                'total': round(total, 2),
            })
            plain_message = strip_tags(html_message)
            send_mail(subject, plain_message, settings.EMAIL_HOST_USER,
                      [request.session.get('email_address')], html_message=html_message)

            return render(request, 'store/payment_success.html', {
                'order_id': order.order_id,
                'items': items_data,
                'subtotal': round(subtotal, 2),
                'discount_rate': discount_rate,
                'discount': round(discount, 2),
                'total': round(total, 2),
            })
        else:
            messages.error(request, f"PayPal execution error: {payment.error}")
            return redirect('basket')

    except Exception as e:
        messages.error(request, f"PayPal processing error: {e}")
        return redirect('basket')


def paypal_cancel(request):
    """Handle PayPal cancellation."""
    request.session.pop('pending_checkout', None)
    messages.warning(request, "PayPal payment was cancelled.")
    return redirect('checkout')


# ===== Promo Code Management =====

def promo_generate(request):
    """Generate a new promo code with a specified cash amount."""
    if request.method == 'POST':
        amount_str = request.POST.get('amount', '').strip()
        try:
            amount = float(amount_str)
            if amount <= 0:
                messages.error(request, "Amount must be greater than zero.")
                return redirect('promo_generate')
        except (ValueError, TypeError):
            messages.error(request, "Please enter a valid number.")
            return redirect('promo_generate')

        # Generate a unique 8-char alphanumeric code
        import string
        chars = string.ascii_uppercase + string.digits
        while True:
            code = 'PROMO-' + ''.join(random.choices(chars, k=8))
            if not PromoCode.objects.filter(code=code).exists():
                break

        promo = PromoCode.objects.create(code=code, amount=amount)
        messages.success(request, f"Promo code {promo.code} created for £{promo.amount:.2f}")
        return redirect('promo_generate')

    # GET — show the form + recently generated codes
    recent_codes = PromoCode.objects.order_by('-created_at')[:10]
    return render(request, 'store/promo_generate.html', {'recent_codes': recent_codes})


def promo_list(request):
    """List all promo codes with their status."""
    all_codes = PromoCode.objects.order_by('-created_at')
    return render(request, 'store/promo_list.html', {'promo_codes': all_codes})
