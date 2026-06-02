"""
Views for the ScentSensation store app.
All database interactions use Django ORM instead of raw SQL.
"""

from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.db.models import Q, Count, Sum, F
from django.db import transaction
from .models import *
from .forms import *
import stripe
import random

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


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
                    member_type = data.get('membership')
                    if member_type and member_type != 'None':
                        discount = DiscountRate.objects.get(member_type=member_type)
                        Membership.objects.create(
                            customer=customer,
                            member_type=discount,
                            end_ren_date=timezone.now() + timedelta(days=30)
                        )
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
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        try:
            customer = Customer.objects.get(email_address=email)
            if check_password(password, customer.password):
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
    return render(request, 'store/signin.html')


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
                    if membership:
                        request.session['membership'] = {
                            'member_id': membership.member_id,
                            'member_type': membership.member_type.member_type,
                            'end_ren_date': membership.end_ren_date.isoformat() if membership.end_ren_date else None
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
            if membership:
                request.session['membership'] = membership.member_type.member_type

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

                        # Membership
                        member = data.get('membership')
                        if member and member != 'None':
                            discount = DiscountRate.objects.get(member_type=member)
                            Membership.objects.update_or_create(
                                customer=customer,
                                defaults={'member_type': discount, 'end_ren_date': timezone.now() + timedelta(days=30)}
                            )
                        # Note: if membership set to 'None', we could delete existing? Original didn't delete, just updated if provided. We'll keep but not delete.

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
        'membership': request.session.get('membership')
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
        'is_paginated': page_obj.has_other_pages()
    }
    return render(request, 'store/storepage.html', context)


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
        discount_rate = membership.member_type.discount_rate if membership else 0
        discount = subtotal * (discount_rate / 100)
        total = subtotal - discount

        context = {
            'items': items,
            'subtotal': round(subtotal, 2),
            'discount': round(discount, 2),
            'total': round(total, 2),
            'discount_rate': discount_rate
        }
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
    return redirect('basket')


def checkout(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('homepage')

    # Get fulfilment and payment method from POST if available
    if request.method == 'POST':
        fulfilment = request.POST.get('fulfilment', 'Pickup')
        payment_method = request.POST.get('payment_method', 'Card')
    else:
        fulfilment = request.session.get('fulfilment', 'Pickup')
        payment_method = 'Card'

    try:
        customer = Customer.objects.get(customer_id=customer_id)
        basket_items = list(Basket.objects.filter(customer=customer).select_related('product'))
        if not basket_items:
            messages.error(request, "Your basket is empty.")
            return redirect('basket')

        membership = getattr(customer, 'membership', None)
        discount_rate = membership.member_type.discount_rate if membership else 0

        subtotal = sum(item.product.price * item.quantity for item in basket_items)
        discount = round(subtotal * (discount_rate / 100), 2)
        total = round(subtotal - discount, 2)

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

        if request.method == 'POST':
            # Build Stripe line items
            line_items = []
            for item in basket_items:
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(item.product.price * 100),
                        'product_data': {
                            'name': f"{item.product.brand} - {item.product.product_name}",
                        },
                    },
                    'quantity': item.quantity,
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
                    'total': str(total),
                    'fulfilment': fulfilment,
                    'payment_method': payment_method,
                }
            )

            request.session['pending_checkout'] = {
                'customer_id': customer_id,
                'subtotal': subtotal,
                'discount': discount,
                'total': total,
                'fulfilment': fulfilment,
                'payment_method': payment_method,
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

            # Clear basket
            Basket.objects.filter(customer=customer).delete()

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
    membership_data = Membership.objects.values('member_type__member_type').annotate(count=Count('member_id'))

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
