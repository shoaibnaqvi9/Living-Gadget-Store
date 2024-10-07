import re,os,requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.files.base import ContentFile
from django.utils.crypto import get_random_string
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from .models import Customer
from myapp.models import Category, Product

def dashboard(request):
    news_data = fetch_news()
    context = {
        'news_data': news_data,
        'session_name': request.session.get('name', 'Guest'),
        'session_email': request.session.get('email', ''),
        'session_img': request.session.get('img', 'default_img.png'),
    }
    return render(request, 'dashboard.html', context)

def signup(request):
    if request.method == 'POST':
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        address = request.POST.get("address")
        phone = request.POST.get("phone")
        img = request.FILES.get("img")

        password_regex = re.compile(r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')

        if not password_regex.match(password):
            messages.error(request, "Password must be at least 8 characters long, include 1 uppercase letter, 1 number, and 1 special character.")
            return render(request, "customer_signup.html")
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "customer_signup.html")
        user = Customer(name=name, email=email, password=password, address=address, phone=phone)
        user.save()

        if img:
            img_name, img_extension = os.path.splitext(img.name)
            img_extension = img_extension.lower()
            if img_extension not in ['.jpg', '.jpeg', '.png']:
                messages.error(request, "Image must be in JPG or PNG format.")
                return render(request, "customer_signup.html")
            new_img_name = f"{user.id}_{user.name}{img_extension}"
            img_content = img.read()
            user.image.save(new_img_name, ContentFile(img_content))
            user.save()
        else:
            messages.error(request, "Please upload an image.")
            return render(request, "customer_signup.html")
        messages.success(request, "You have signed up successfully.")
        return redirect("customer_login")
    else:
        return render(request, "customer_signup.html")

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = Customer.objects.filter(email=email)
        if user is not None:
            user = user[0]
            if user.password == password:
                request.session['user_id'] = user.id
                request.session['name'] = user.name
                request.session['email'] = user.email
                return redirect('dashboard')
            else:
                msg = 'Invalid Credentials'
                messages.error(request, msg)
                return render(request, 'customer_login.html', {'msg': msg})
    else:
        return render(request, 'customer_login.html')

def logout(request):
    logout(request)
    return redirect('customer_login')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = Customer.objects.get(email=email)
            reset_token = get_random_string(50)
            user.reset_token = reset_token
            user.save(update_fields=['reset_token'])

            reset_link = request.build_absolute_uri(f'/customer_reset_password/{reset_token}/')
            try:
                send_mail(
                    'Password Reset Request',
                    f'Click the link to reset your password: {reset_link}',
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
            except BadHeaderError:
                msg = 'Invalid header found.'
                return render(request, 'customer_forgot_password.html', {'msg': msg})

            msg = 'A password reset link has been sent to your email.'
            return render(request, 'customer_forgot_password.html', {'msg': msg})
        except Customer.DoesNotExist:
            msg = 'No user found with this email address.'
            return render(request, 'customer_forgot_password.html', {'msg': msg})

    return render(request, 'customer_forgot_password.html')

def reset_password(request, reset_token):
    if request.method == 'POST':
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('cpassword')
        if new_password == confirm_password:
            try:
                user = Customer.objects.get(reset_token=reset_token)
                user.password = new_password
                user.reset_token = None
                user.save()
                msg = "Password reset successfully!"
                return redirect('login')
            except Customer.DoesNotExist:
                msg = "Invalid reset token."
        else:
            msg = "Passwords do not match."

        return render(request, 'customer_reset_password.html', {'msg': msg})
    else:
        return render(request, 'customer_reset_password.html')

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        cart[str(product_id)] = {
            'name': product.name,
            'price': product.price,
            'quantity': 1,
            'img_url': product.img.url,
        }
    request.session['cart'] = cart
    cart_count = sum(item['quantity'] for item in cart.values())
    request.session['cart_count'] = cart_count
    request.session['last_viewed_category'] = product.category.name
    messages.success(request, f"{product.name} added to cart.")
    return redirect('category_related_products', category_name=product.category.name)

def view_cart(request):
    categories = Category.objects.all()
    cart = request.session.get('cart', {})
    last_viewed_category_name = request.session.get('last_viewed_category', None)
    if last_viewed_category_name:
        last_viewed_category = get_object_or_404(Category, name=last_viewed_category_name)
    else:
        last_viewed_category = None
    if request.method == 'POST':
        print(request.POST)
        item_id = request.POST.get('item_id')
        if item_id in cart:
            del cart[item_id]
            request.session['cart'] = cart
            messages.success(request, "Item removed from cart.")
        else:
            messages.error(request, "Item not found in cart.")
    total_price = sum(item['price'] * item['quantity'] for item in cart.values())
    context = {
        'cart': cart,
        'total_price': total_price,
        'categories': categories,
        'category': last_viewed_category,
    }
    return render(request, 'customer_view_cart.html', context)

def deleteproduct(request,product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, f"Product '{product.name}' has been deleted successfully.")
        return redirect('dashboard')
    return render(request, 'confirm_delete.html', {'product': product})

def fetch_news():
    api_key = 'f274f6a51cd94add837984e51a09312e'
    url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}'
    response = requests.get(url)
    news_data = response.json()
    news_data['articles'] = news_data['articles'][:5]
    return news_data