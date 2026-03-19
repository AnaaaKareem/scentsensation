from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from .models import *
from .forms import *
import pymysql
import stripe
import random

def home(request):
    return render(request, 'store/homepage.html')

def signup(request):
    # Check If the user submitted signup form
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)

        # Convert form data into a list
        if form.is_valid() and form.cleaned_data.get('password1') == form.cleaned_data.get('password2'):
            data = form.cleaned_data

            # Establish a Database connection
            connection = pymysql.connect(
                host=settings.HOST,
                port=settings.PORT,
                user=settings.USER,
                password=settings.PASSWORD,
                db=settings.DB,
                charset=settings.CHARSET,
                cursorclass=pymysql.cursors.DictCursor
            )

            try:
                with connection.cursor() as cursor:
                    # Insert into customer table
                    sql = """
                            INSERT INTO customer (
                                first_name, middle_name, last_name, DOB, email_address, password, gender
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """
                    cursor.execute(sql, (
                        data['first_name'], data.get('middle_name'), data['last_name'], data.get('DOB'),
                        data['email_address'], make_password(data['password1']), data.get('gender')
                    ))
                    # Get customer_id
                    customer_id = cursor.lastrowid
                    # Get phone_numbers table
                    phone_number = data.get('phone_numbers')
                    if phone_number:
                        phone_sql = "INSERT INTO phone_numbers (customer_id, phone_number) VALUES (%s, %s)"
                        cursor.execute(phone_sql, (customer_id, phone_number))

                        # Insert address
                        house = data.get('house')
                        street_name = data.get('street_name')
                        town_city = data.get('town_city')
                        county = data.get('county')
                        postcode = data.get('postcode')
                        country = data.get('country')

                        if house and street_name and town_city and county and postcode and country:
                            address_sql = """
                                INSERT INTO addresses (
                                    customer_id, house, street_name, town_city, county, postcode, country
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """
                            cursor.execute(address_sql, (
                                customer_id, house, street_name, town_city, county, postcode, country
                            ))

                        # Assign Membership
                        member = data.get('membership')
                        if member:
                            member_sql = """
                                INSERT INTO membership (
                                    customer_id, member_type, end_ren_date
                                ) VALUES (%s, %s, %s)
                            """
                            cursor.execute(member_sql, (
                                customer_id, member, timezone.now() + timedelta(days=30)
                            ))

                    # Confirm Queries
                    connection.commit()
                    # Output a message
                    messages.success(request, "User registered successfully!")
                    # Redirect to home
                    return redirect(home)
            # Rollback connection if error with a message
            except pymysql.MySQLError as e:
                connection.rollback()
                messages.error(request, f"Database error: {e}")
                # Refresh page
                return redirect('signupAccount')
            finally:
                # Close connection
                connection.close()
    else:
        form = UserRegistrationForm()

    # Pass form in context to be used in html template
    return render(request, 'store/signup.html', {'form': form})

def signin(request):
    # Check If the user submitted login credentials
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')

        # Establish a Database connection
        connection = pymysql.connect(
            host=settings.HOST,
            port=settings.PORT,
            user=settings.USER,
            password=settings.PASSWORD,
            db=settings.DB,
            charset=settings.CHARSET,
            cursorclass=pymysql.cursors.DictCursor
        )

        try:
            with connection.cursor() as cursor:
                # Fetch customer data
                cursor.execute("""
                    SELECT customer_id, password
                    FROM customer WHERE email_address=%s;
                """, (email,))
                customer = cursor.fetchone()

                if customer and check_password(password, customer['password']):

                    # Generate a 6-digit code
                    verification_code = random.randint(100000, 999999)
                    print(verification_code)

                    # Save code and expiry in session
                    request.session['2fa_code'] = str(verification_code)
                    request.session['2fa_expires'] = (datetime.now() + timedelta(minutes=5)).isoformat()
                    request.session['2fa_email'] = email

                    # Send the email
                    send_mail(
                        'Your 2FA Code',
                        f'Your verification code is: {verification_code}',
                        'no-reply@yourdomain.com',
                        [email],
                        fail_silently=False,
                    )
                    # Redirect to homepage upon successful session
                    return redirect('verify_2fa')
                else:
                    messages.error(request, 'Invalid email or password')
        except pymysql.MySQLError:
            # Rollback connection if error with a message
            connection.rollback()
            messages.error(request, 'Something went wrong during login')
        finally:
            # Close connection
            connection.close()

    return render(request, 'store/signin.html')

def verify_2fa(request):
    if request.method == 'POST':

        # Establish a Database connection
        connection = pymysql.connect(
            host=settings.HOST,
            port=settings.PORT,
            user=settings.USER,
            password=settings.PASSWORD,
            db=settings.DB,
            charset=settings.CHARSET,
            cursorclass=pymysql.cursors.DictCursor
        )

        code = request.POST.get('code')
        session_code = request.session.get('2fa_code')
        expires_at = request.session.get('2fa_expires')
        email = request.session.get('2fa_email')

        if session_code and datetime.fromisoformat(expires_at) > datetime.now():
            if code == session_code:
                try:
                    with connection.cursor() as cursor:
                        # Fetch customer data
                        cursor.execute("""
                            SELECT customer_id, first_name, middle_name, last_name, gender, DOB, password
                            FROM customer WHERE email_address=%s;
                        """, (email,))
                        # Store customer data using cursor
                        customer = cursor.fetchone()
                        # Save session using customer information
                        request.session['customer_id'] = customer['customer_id']
                        request.session['first_name'] = customer['first_name']
                        request.session['middle_name'] = customer['middle_name']
                        request.session['last_name'] = customer['last_name']
                        request.session['email_address'] = email
                        request.session['gender'] = customer['gender']
                        if customer['DOB']:
                            request.session['DOB'] = customer['DOB'].isoformat()

                        # Fetch address data
                        cursor.execute("""
                            SELECT house, street_name, town_city, county, postcode, country
                            FROM addresses WHERE customer_id=%s LIMIT 1;
                        """, (customer['customer_id'],))
                        # Store address data using cursor
                        address = cursor.fetchone()
                        if address:
                            # Save session using address information
                            request.session['house'] = address['house']
                            request.session['street_name'] = address['street_name']
                            request.session['town_city'] = address['town_city']
                            request.session['county'] = address['county']
                            request.session['postcode'] = address['postcode']
                            request.session['country'] = address['country']

                        # Fetch Phone Numbers data
                        cursor.execute("""
                            SELECT phone_number FROM phone_numbers WHERE customer_id=%s;
                        """, (customer['customer_id'],))
                        # Store phone numbers using cursor
                        phone_numbers = cursor.fetchall()
                        # Save session using phone numbers
                        request.session['phone_numbers'] = [phone['phone_number'] for phone in
                                                            phone_numbers] if phone_numbers else []

                        # Fetch membership data
                        cursor.execute("""
                            SELECT member_id, member_type, end_ren_date FROM membership WHERE customer_id=%s;
                        """, (customer['customer_id'],))
                        # Store membership data using cursor
                        membership = cursor.fetchone()
                        if membership:
                            # Save session using membership
                            request.session['membership'] = {
                                'member_id': membership['member_id'],
                                'member_type': membership['member_type'],
                                'end_ren_date': membership['end_ren_date'].isoformat() if membership['end_ren_date'] else None
                            }

                        # Clean up
                        request.session.pop('2fa_code', None)
                        request.session.pop('2fa_expires', None)
                        request.session.pop('pending_customer', None)

                        # Redirect to homepage upon successful session
                        return redirect('homepage')
                finally:
                    connection.close()
            else:
                messages.error(request, 'Invalid 2FA code')
                return render(request, 'store/verify_2fa.html')
        else:
            messages.error(request, '2FA code expired. Please login again.')
            return redirect('signin')
    return render(request, 'store/verify_2fa.html')

def signout(request):
    # Flush all session data store
    request.session.flush()
    # Redirect to signin page
    return redirect('signinAccount')

def account(request):
    connection = None

    # Fetch data from database to view account information
    if request.method == 'GET':
        # Store customer_id from session
        customer_id = request.session.get('customer_id')

        try:
            # Establish a Database connection
            connection = pymysql.connect(
                host=settings.HOST,
                port=settings.PORT,
                user=settings.USER,
                password=settings.PASSWORD,
                db=settings.DB,
                charset=settings.CHARSET,
                cursorclass=pymysql.cursors.DictCursor
            )

            with connection.cursor() as cursor:
                # Query customer information
                cursor.execute("SELECT * FROM customer WHERE customer_id = %s", (customer_id,))
                # Use cursor to store customer information
                customer = cursor.fetchone()
                # Load queried customer information
                if customer:
                    request.session['first_name'] = customer['first_name']
                    request.session['middle_name'] = customer['middle_name']
                    request.session['last_name'] = customer['last_name']
                    request.session['email_address'] = customer['email_address']
                    request.session['DOB'] = str(customer['DOB'])
                    request.session['gender'] = customer['gender']

                # Query address information
                cursor.execute("SELECT * FROM addresses WHERE customer_id = %s", (customer_id,))
                # Use cursor to store customer information
                address = cursor.fetchone()
                # Load queried customer information
                if address:
                    request.session['house'] = address['house']
                    request.session['street_name'] = address['street_name']
                    request.session['town_city'] = address['town_city']
                    request.session['county'] = address['county']
                    request.session['postcode'] = address['postcode']
                    request.session['country'] = address['country']

                # Query address information
                cursor.execute("SELECT member_type FROM membership WHERE customer_id = %s", (customer_id,))
                # Use cursor to store membership information
                membership = cursor.fetchone()
                # Load queried membership information
                if membership:
                    request.session['membership'] = membership['member_type']

        except pymysql.MySQLError as e:
            # Rollback changes on error
            connection.rollback()
            # Display error message
            messages.error(request, f"Database error: {e}")
        finally:
            # Close database connection
            connection.close()

    # Check if the user will be updating or deleting account
    if request.method == 'POST':
        # Retrieve customer_id from session
        customer_id = request.session.get('customer_id')
        # Check if the request is for updating account information
        if 'update' in request.POST:
            # Initialize form with POST data
            form = UserUpdateForm(request.POST)
            # Validate form data
            if form.is_valid():
                # Extract cleaned form data
                data = form.cleaned_data
                try:

                    # Establish a Database connection
                    connection = pymysql.connect(
                        host=settings.HOST,
                        port=settings.PORT,
                        user=settings.USER,
                        password=settings.PASSWORD,
                        db=settings.DB,
                        charset=settings.CHARSET,
                        cursorclass=pymysql.cursors.DictCursor
                    )

                    with connection.cursor() as cursor:
                        # --- Customer fields ---
                        # Update first name if provided
                        if data.get('first_name'):
                            cursor.execute("UPDATE customer SET first_name = %s WHERE customer_id = %s",
                                           (data['first_name'], customer_id))

                        # Update middle name if provided
                        if data.get('middle_name'):
                            cursor.execute("UPDATE customer SET middle_name = %s WHERE customer_id = %s",
                                           (data['middle_name'], customer_id))

                        # Update last name if provided
                        if data.get('last_name'):
                            cursor.execute("UPDATE customer SET last_name = %s WHERE customer_id = %s",
                                           (data['last_name'], customer_id))

                        # Update date of birth if provided
                        if data.get('DOB'):
                            cursor.execute("UPDATE customer SET DOB = %s WHERE customer_id = %s",
                                           (data['DOB'], customer_id))

                        # Update email address if provided
                        if data.get('email_address'):
                            cursor.execute("UPDATE customer SET email_address = %s WHERE customer_id = %s",
                                           (data['email_address'], customer_id))

                        # Update password if provided (hashed)
                        if data.get('password'):
                            cursor.execute("UPDATE customer SET password = %s WHERE customer_id = %s",
                                           (make_password(data['password']), customer_id))

                        # Update gender if provided
                        if data.get('gender'):
                            cursor.execute("UPDATE customer SET gender = %s WHERE customer_id = %s",
                                           (data['gender'], customer_id))

                        # --- Phone number ---
                        # Insert or update phone number if provided
                        if data.get('phone_numbers'):
                            cursor.execute("""
                                INSERT INTO phone_numbers (customer_id, phone_number)
                                VALUES (%s, %s)
                                ON DUPLICATE KEY UPDATE phone_number = VALUES(phone_number)
                            """, (customer_id, data['phone_numbers']))

                        # --- Address fields ---
                        # Update house if provided
                        if data.get('house'):
                            cursor.execute("UPDATE addresses SET house = %s WHERE customer_id = %s",
                                           (data['house'], customer_id))

                        # Update street name if provided
                        if data.get('street_name'):
                            cursor.execute("UPDATE addresses SET street_name = %s WHERE customer_id = %s",
                                           (data['street_name'], customer_id))

                        # Update town/city if provided
                        if data.get('town_city'):
                            cursor.execute("UPDATE addresses SET town_city = %s WHERE customer_id = %s",
                                           (data['town_city'], customer_id))

                        # Update county if provided
                        if data.get('county'):
                            cursor.execute("UPDATE addresses SET county = %s WHERE customer_id = %s",
                                           (data['county'], customer_id))

                        # Update postcode if provided
                        if data.get('postcode'):
                            cursor.execute("UPDATE addresses SET postcode = %s WHERE customer_id = %s",
                                           (data['postcode'], customer_id))

                        # Update country if provided
                        if data.get('country'):
                            cursor.execute("UPDATE addresses SET country = %s WHERE customer_id = %s",
                                           (data['country'], customer_id))

                        # --- Membership ---
                        # Update membership type and renewal date if provided
                        if data.get('membership'):
                            cursor.execute("""
                                UPDATE membership 
                                SET member_type = %s, end_ren_date = %s
                                WHERE customer_id = %s
                            """, (data['membership'], timezone.now() + timedelta(days=30), customer_id))

                        # Commit all database changes
                        connection.commit()
                        # Display success message
                        messages.success(request, "Your account information has been updated.")
                        # Redirect to account page
                        return redirect('account')

                # Handle database errors
                except pymysql.MySQLError as e:
                    # Rollback changes on error
                    connection.rollback()
                    # Display error message
                    messages.error(request, f"Database error: {e}")
                finally:
                    # Close database connection
                    connection.close()

        # Check if the request is for deleting the account
        elif 'delete' in request.POST:
            # Retrieve customer_id from session
            customer_id = request.session.get('customer_id')
            try:

                # Establish a Database connection
                connection = pymysql.connect(
                    host=settings.HOST,
                    port=settings.PORT,
                    user=settings.USER,
                    password=settings.PASSWORD,
                    db=settings.DB,
                    charset=settings.CHARSET,
                    cursorclass=pymysql.cursors.DictCursor
                )

                with connection.cursor() as cursor:
                    # Delete address records for the customer
                    cursor.execute("DELETE FROM addresses WHERE customer_id = %s", (customer_id,))
                    # Delete phone number records for the customer
                    cursor.execute("DELETE FROM phone_numbers WHERE customer_id = %s", (customer_id,))
                    # Delete membership records for the customer
                    cursor.execute("DELETE FROM membership WHERE customer_id = %s", (customer_id,))
                    # Delete places records for the customer
                    cursor.execute("DELETE FROM places WHERE customer_id = %s", (customer_id,))
                    # Delete customer record
                    cursor.execute("DELETE FROM customer WHERE customer_id = %s", (customer_id,))
                    # Commit all database changes
                    connection.commit()
            # Handle database errors
            except pymysql.MySQLError:
                # Rollback changes on error
                connection.rollback()
            finally:
                # Close database connection
                connection.close()
                # Clear all session data
                request.session.flush()
                # Redirect to homepage
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
    # Fetch all products data
    all_products = Products.objects.all()
    # Fetch all product images data
    images = ProductImages.objects.all()

    # Retrieve all filters from category tag
    category_filter = request.GET.getlist('category')
    # Apply category filter if categories are selected
    if category_filter:
        # Use Q objects for filtering
        q_objects = Q()
        # Add personal fragrances to the Q object
        if 'Personal Fragrances' in category_filter:
            q_objects |= Q(personal_fragrance__isnull=False)
        # Add home fragrances to the Q object
        if 'Home Fragrances' in category_filter:
            q_objects |= Q(home_fragrance__isnull=False)
        # Store all filtered products
        all_products = all_products.filter(q_objects)

    # Retrieve all filters from gender tag
    gender_filter = request.GET.getlist('gender')
    # Apply gender filter if genders are selected
    if gender_filter:
        # Filter gender found in personal fragrance if found
        all_products = all_products.filter(personal_fragrance__gender__in=gender_filter)

    # Get minimum price from tag
    min_price = request.GET.get('min_price')
    # Get maximum price from tag
    max_price = request.GET.get('max_price')
    # Apply minimum price filter if provided
    if min_price:
        all_products = all_products.filter(price__gte=min_price)
    # Apply maximum price filter if provided
    if max_price:
        all_products = all_products.filter(price__lte=max_price)


    # Initialize paginator with 6 products per page
    paginator = Paginator(all_products, 6)
    # Get current page number (default to 1)
    page_number = request.GET.get('page', 1)
    # Retrieve the page object for the current page
    page_obj = paginator.get_page(page_number)


    # Check is user is adding a product to basket
    if request.method == "POST" and "add_basket" in request.POST:
        # Fetch product ID
        product_id = request.POST.get("product_id")
        # Fetch Quantity
        quantity = int(request.POST.get("quantity", 1))
        # Fetch Customer from current session
        customer_id = request.session['customer_id']

        # Create or update basket item for the customer and product
        basket_item, created = Basket.objects.get_or_create(
            customer_id=customer_id,
            product_id=product_id,
            defaults={'quantity': quantity}
        )

        # If basket item already exists, increment quantity
        if not created:
            basket_item.quantity += quantity
            basket_item.save()

        # Redirect to store page after adding to basket
        return redirect('store')

    context = {
        'products': page_obj,
        'images': images,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages()
    }

    return render(request, 'store/storepage.html', context)

def basket(request):
    # Retrieve customer ID from session
    customer_id = request.session.get('customer_id')
    # Redirect to sign-in page if customer is not logged in
    if not customer_id:
        return redirect('signin')

    # Establish a Database connection
    connection = pymysql.connect(
        host=settings.HOST,
        port=settings.PORT,
        user=settings.USER,
        password=settings.PASSWORD,
        db=settings.DB,
        charset=settings.CHARSET,
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            # Fetch basket items with product details
            sql = """
                SELECT b.*, p.product_name, p.price, p.brand
                FROM basket b
                JOIN products p ON b.product_id = p.product_id
                WHERE b.customer_id = %s;
            """
            cursor.execute(sql, (customer_id,))
            # Store all basket items
            basket_items = cursor.fetchall()

            # Initialize list to store basket items
            items = []
            # Initialize subtotal for basket
            subtotal = 0

            # Process each basket item
            for item in basket_items:
                # Fetch first image for the product
                sql = "SELECT image FROM product_images WHERE product_id = %s LIMIT 1;"
                cursor.execute(sql, (item['product_id'],))
                # Store product image
                image = cursor.fetchone()

                # Check if product is a personal fragrance
                sql = "SELECT * FROM personal_fragrances WHERE product_id = %s;"
                cursor.execute(sql, (item['product_id'],))
                # Store personal fragrance details
                personal = cursor.fetchone()

                # Check if product is a home fragrance
                sql = "SELECT * FROM home_fragrances WHERE product_id = %s;"
                cursor.execute(sql, (item['product_id'],))
                # Store home fragrance details
                home_fragrances = cursor.fetchone()

                # Calculate total price for the item
                total_price = item['price'] * item['quantity']
                # Add item total to subtotal
                subtotal += total_price

                # Add item details to the items list
                items.append({
                    'product': {
                        'product_id': item['product_id'],
                        'brand': item['brand'],
                        'product_name': item['product_name'],
                        'price': item['price']
                    },
                    'quantity': item['quantity'],
                    'image': image,
                    'personal': personal,
                    'home': home_fragrances,
                })

            # Fetch membership and discount rate
            sql = """
                SELECT d.discount_rate 
                FROM membership m
                JOIN discount_rate d ON m.member_type = d.member_type
                WHERE m.customer_id = %s;
            """
            cursor.execute(sql, (customer_id,))
            # Store discount rate
            row = cursor.fetchone()
            # Set discount rate
            discount_rate = row['discount_rate']

            # Calculate discount based on subtotal and discount rate
            discount = subtotal * (discount_rate / 100)
            # Calculate final total after discount
            total = subtotal - discount

            context = {
                'items': items,
                'subtotal': round(subtotal, 2),
                'discount': round(discount, 2),
                'total': round(total, 2),
                'discount_rate': discount_rate
            }

    except pymysql.MySQLError:
        # Rollback changes on error
        connection.rollback()

    finally:
        # Close database connection
        connection.close()

    return render(request, 'store/basket.html', context)

def delete_from_basket(request, product_id):
    # Retrieve customer ID from session
    customer_id = request.session.get('customer_id')
    # Redirect to sign-in page if customer is not logged in
    if not customer_id:
        return redirect('signin')

    # Establish a Database connection
    connection = pymysql.connect(
        host=settings.HOST,
        port=settings.PORT,
        user=settings.USER,
        password=settings.PASSWORD,
        db=settings.DB,
        charset=settings.CHARSET,
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            # Query the product item to be removed
            sql = """
                DELETE FROM basket WHERE customer_id = %s AND product_id = %s
            """
            # Remove the product from basket
            cursor.execute(sql, (customer_id, product_id))
            connection.commit()

    except pymysql.MySQLError:
        # Rollback changes on error
        connection.rollback()

    finally:
        # Close database connection
        connection.close()

    return redirect('basket')

def add_quantity(request, product_id):
    customer_id = request.session.get('customer_id')
    if request.method == 'POST' and customer_id:

        # Establish a Database connection
        connection = pymysql.connect(
            host=settings.HOST,
            port=settings.PORT,
            user=settings.USER,
            password=settings.PASSWORD,
            db=settings.DB,
            charset=settings.CHARSET,
            cursorclass=pymysql.cursors.DictCursor
        )

        try:
            with connection.cursor() as cursor:
                # Check if item already exists in basket
                cursor.execute("""
                    SELECT quantity FROM basket
                    WHERE customer_id = %s AND product_id = %s
                """, (customer_id, product_id))
                item = cursor.fetchone()

                if item:
                    # Increment quantity
                    cursor.execute("""
                        UPDATE basket
                        SET quantity = quantity + 1
                        WHERE customer_id = %s AND product_id = %s
                    """, (customer_id, product_id))
                else:
                    # Insert new row with quantity = 1
                    cursor.execute("""
                        INSERT INTO basket (customer_id, product_id, quantity)
                        VALUES (%s, %s, 1)
                    """, (customer_id, product_id))

                connection.commit()
        finally:
            connection.close()
    return redirect('basket')

def remove_quantity(request, product_id):
    customer_id = request.session.get('customer_id')
    if request.method == 'POST' and customer_id:

        # Establish a Database connection
        connection = pymysql.connect(
            host=settings.HOST,
            port=settings.PORT,
            user=settings.USER,
            password=settings.PASSWORD,
            db=settings.DB,
            charset=settings.CHARSET,
            cursorclass=pymysql.cursors.DictCursor
        )

        try:
            with connection.cursor() as cursor:
                # Check if item already exists in basket
                cursor.execute("""
                    SELECT quantity FROM basket
                    WHERE customer_id = %s AND product_id = %s
                """, (customer_id, product_id))
                item = cursor.fetchone()

                if item:
                    # Increment quantity
                    cursor.execute("""
                        UPDATE basket
                        SET quantity = quantity - 1
                        WHERE customer_id = %s AND product_id = %s
                    """, (customer_id, product_id))

                connection.commit()
        finally:
            connection.close()
    return redirect('basket')

def checkout(request):
    customer_id = request.session.get('customer_id')

    if not customer_id:
        return redirect('homepage')

    # Establish a Database connection
    connection = pymysql.connect(
        host=settings.HOST,
        port=settings.PORT,
        user=settings.USER,
        password=settings.PASSWORD,
        db=settings.DB,
        charset=settings.CHARSET,
        cursorclass=pymysql.cursors.DictCursor
    )

    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        with connection.cursor() as cursor:
            # Get basket items
            sql = """
                SELECT b.product_id, b.quantity, p.product_name, p.price, p.brand
                FROM basket b
                JOIN products p ON b.product_id = p.product_id
                WHERE b.customer_id = %s;
            """
            cursor.execute(sql, (customer_id,))
            basketItems = cursor.fetchall()

            if not basketItems:
                return redirect('basket')

            # Fetch discount rate
            sql = """
                SELECT d.discount_rate FROM membership as m
                JOIN discount_rate as d ON m.member_type = d.member_type
                WHERE customer_id = %s;
            """
            cursor.execute(sql, (customer_id,))
            row = cursor.fetchone()
            discount_rate = row['discount_rate'] if row else 0

            # Calculate subtotal
            subtotal = sum(item['price'] * item['quantity'] for item in basketItems)

            connection.commit()

    except pymysql.MySQLError as e:
        connection.rollback()
        print(f"MySQL Error: {e}")
        return redirect('basket')

    finally:
        connection.close()

    line_items = []

    for item in basketItems:
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'unit_amount': int(item['price'] * 100),
                'product_data': {
                    'name': item['brand'] + " - " + item['product_name'],
                },
            },
            'quantity': item['quantity'],
        })

    # Calculate discount and total
    discount = round(subtotal * (discount_rate / 100), 2)
    total = round(subtotal - discount, 2)

    coupon = stripe.Coupon.create(
        percent_off=discount_rate,
        duration="once",
    )

    # Create Stripe Checkout Session
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        discounts=[{"coupon": coupon}],
        success_url=request.build_absolute_uri('/payment_success/') + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri('/basket/'),
        metadata={
            'customer_id': customer_id,
            'subtotal': subtotal,
            'discount': discount,
            'total': total,
        }
    )

    # Store session_id in the session to use later on success
    request.session['pending_checkout'] = {
        'customer_id': customer_id,
        'subtotal': subtotal,
        'discount': discount,
        'total': total,
    }

    return redirect(session.url, code=303)

@csrf_exempt
def payment_success(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    session_id = request.GET.get('session_id')

    if not session_id:
        return redirect('homepage')

    # Retrieve the session details from Stripe
    session = stripe.checkout.Session.retrieve(session_id)
    customer_id = session.metadata.get('customer_id')

    if not customer_id:
        return redirect('homepage')

    # Establish a Database connection
    connection = pymysql.connect(
        host=settings.HOST,
        port=settings.PORT,
        user=settings.USER,
        password=settings.PASSWORD,
        db=settings.DB,
        charset=settings.CHARSET,
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT b.product_id, b.quantity, p.product_name, p.brand, p.price
                FROM basket b
                JOIN products p ON b.product_id = p.product_id
                WHERE b.customer_id = %s;
            """, (customer_id,))
            basketItems = cursor.fetchall()

            if not basketItems:
                return redirect('basket')

            # Create new order
            cursor.execute("""
                INSERT INTO orders (order_date, order_time, order_type, payment_method) 
                VALUES (%s, %s, %s, %s);
            """, (
                timezone.now(),
                timezone.now(),
                request.session.get('fulfilment', 'Pickup'),
                'Card'
            ))
            order_id = cursor.lastrowid

            # Insert order items
            for item in basketItems:
                cursor.execute("""
                    INSERT INTO order_items (order_id, product_id, quantity) 
                    VALUES (%s, %s, %s);
                """, (order_id, item['product_id'], item['quantity']))

            # Track in places
            for item in basketItems:
                cursor.execute("""
                    INSERT INTO places (order_id, product_id, customer_id) 
                    VALUES (%s, %s, %s);
                """, (order_id, item['product_id'], customer_id))

            # Clear basket
            cursor.execute("DELETE FROM basket WHERE customer_id = %s;", (customer_id,))

            # Get discount rate
            cursor.execute("""
                SELECT d.discount_rate FROM membership m
                JOIN discount_rate d ON m.member_type = d.member_type
                WHERE m.customer_id = %s;
            """, (customer_id,))
            row = cursor.fetchone()
            discount_rate = row['discount_rate'] if row else 0

            # Calculate totals
            subtotal = sum(item['price'] * item['quantity'] for item in basketItems)
            discount = round(subtotal * (discount_rate / 100), 2)
            total = round(subtotal - discount, 2)

            connection.commit()

    except pymysql.MySQLError:
        connection.rollback()
        return redirect('basket')

    finally:
        connection.close()

    # Create email content
    subject = f"Order #{order_id}"
    html_message = render_to_string('store/receipt.html', {
        'customer_email': request.session.get('email_address'),
        'order_id': order_id,
        'items': basketItems,
        'subtotal': round(subtotal, 2),
        'discount_rate': discount_rate,
        'discount': round(discount, 2),
        'total': round(total, 2),
    })

    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [request.session.get('email_address')]

    # Send the email
    send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)

    return render(request, 'store/checkout.html', {
        'order_id': order_id,
        'items': basketItems,
        'subtotal': round(subtotal, 2),
        'discount_rate': discount_rate ,
        'discount': round(discount, 2),
        'total': round(total, 2)
    })

def admin_dashboard(request):

    # Establish a Database connection
    connection = pymysql.connect(
        host=settings.HOST,
        port=settings.PORT,
        user=settings.USER,
        password=settings.PASSWORD,
        db=settings.DB,
        charset=settings.CHARSET,
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            # Total orders
            cursor.execute("SELECT COUNT(*) AS total_orders FROM orders;")
            total_orders = cursor.fetchone()['total_orders']

            # Total products
            cursor.execute("SELECT COUNT(*) AS total_products FROM products;")
            total_products = cursor.fetchone()['total_products']

            # Total customers
            cursor.execute("SELECT COUNT(*) AS total_customers FROM customer;")
            total_customers = cursor.fetchone()['total_customers']

            # Total revenue
            cursor.execute("""
                SELECT SUM(oi.quantity * p.price) AS total_revenue
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id;
            """)
            total_revenue = cursor.fetchone()['total_revenue'] or 0

            # Top-selling product
            cursor.execute("""
                SELECT p.product_name, SUM(oi.quantity) AS total_sold
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                GROUP BY oi.product_id
                ORDER BY total_sold DESC
                LIMIT 1;
            """)
            top_product = cursor.fetchone()

            # Membership breakdown (optional)
            cursor.execute("""
                SELECT member_type, COUNT(*) as count
                FROM membership
                GROUP BY member_type;
            """)
            membership_data = cursor.fetchall()

            context = {
                'total_orders': total_orders,
                'total_products': total_products,
                'total_customers': total_customers,
                'total_revenue': round(total_revenue, 2),
                'top_product': top_product,
                'membership_data': membership_data
            }

    finally:
        connection.close()

    return render(request, 'store/admin_dashboard.html', context)