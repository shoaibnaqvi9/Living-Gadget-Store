import re,requests,os
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.utils.text import slugify
from django.contrib import messages
from django.core.files.base import ContentFile
from django.utils.crypto import get_random_string
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.hashers import make_password
from .models import User, Category, Product
from django.conf import settings
from django.db.models import Q

def home(request):
    news_data = fetch_news()
    categories = Category.objects.all()
    records = Product.objects.all()
    context = {
        'news_data': news_data,
        'show_product': records,
        'categories': categories,
    }
    return render(request, 'home.html', context)


def dashboard(request):
    news_data = fetch_news()
    categories = Category.objects.all()
    records = Product.objects.all()
    context = {
        'news_data': news_data,
        'show_product': records,
        'categories': categories,
        'session_name': request.session.get('name', 'Guest'),
        'session_email': request.session.get('email', ''),
        'session_img': request.session.get('img', 'default_img.png'),
    }
    print(request.session.get('img', 'default_img.png'))
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
            return render(request, "signup.html")
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "signup.html")
        user = User(name=name, email=email, password=password, address=address, phone=phone)
        user.save()

        if img:
            img_name, img_extension = os.path.splitext(img.name)
            img_extension = img_extension.lower()
            if img_extension not in ['.jpg', '.jpeg', '.png']:
                messages.error(request, "Image must be in JPG or PNG format.")
                return render(request, "signup.html")
            new_img_name = f"{user.id}_{user.name}{img_extension}"
            img_content = img.read()
            user.image.save(new_img_name, ContentFile(img_content))
            user.save()
        else:
            messages.error(request, "Please upload an image.")
            return render(request, "signup.html")
        messages.success(request, "You have signed up successfully.")
        return redirect("login")
    else:
        return render(request, "signup.html")

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = User.objects.filter(email=email)
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
                return render(request, 'login.html', {'msg': msg})
    else:
        return render(request, 'login.html')

def logout(request):
    logout(request)
    return redirect('login')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)
            reset_token = get_random_string(50)
            user.reset_token = reset_token
            user.save(update_fields=['reset_token'])

            reset_link = request.build_absolute_uri(f'/applicate/reset_password/{reset_token}/')
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
                return render(request, 'forgot_password.html', {'msg': msg})

            msg = 'A password reset link has been sent to your email.'
            return render(request, 'forgot_password.html', {'msg': msg})
        except User.DoesNotExist:
            msg = 'No user found with this email address.'
            return render(request, 'forgot_password.html', {'msg': msg})

    return render(request, 'forgot_password.html')


def reset_password(request, reset_token):
    if request.method == 'POST':
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('cpassword')
        if new_password == confirm_password:
            try:
                user = User.objects.get(reset_token=reset_token)
                user.password = new_password
                user.reset_token = None
                user.save()
                msg = "Password reset successfully!"
                return redirect('login')
            except User.DoesNotExist:
                msg = "Invalid reset token."
        else:
            msg = "Passwords do not match."

        return render(request, 'reset_password.html', {'msg': msg})
    else:
        return render(request, 'reset_password.html')
    

def add_category(request):
    if request.method == 'POST':
        name = request.POST.get("name")
        category = Category(name=name)
        category.save()
        msg = "Category added successfully"
        messages.success(request,msg)
        return redirect("category")
    else:
        categories = Category.objects.all()
        return render(request, 'category.html',{'categories': categories})

def createprod(request):
    if request.method == 'POST':
        name = request.POST.get("name")
        brand = request.POST.get("brand")
        price = request.POST.get("price")
        qty = request.POST.get("qty")
        imgfile = request.FILES.get("img")
        c_id = request.POST.get("category")
        u_id = request.session.get('user_id')
        status = 'Available'
        if imgfile and not (imgfile.name.endswith('png') or imgfile.name.endswith('jpg')):
            messages.info(request, "Only png and jpg files are accepted!")
            return redirect('createprod')
        if Product.objects.filter(name=name).exists():
            messages.info(request, "Product already exists.")
            return redirect('createprod')
        try:
            user = User.objects.get(id=u_id)
        except User.DoesNotExist:
            messages.error(request, "User not logged in.")
            return redirect('login')
        try:
            category = Category.objects.get(id=c_id)
        except Category.DoesNotExist:
            messages.info(request, "Category does not exist.")
            return redirect('createprod')
        product = Product(name=name,brand=brand,price=price,qty=qty,category=category,user=user,status=status)
        if imgfile:
            fss = FileSystemStorage()
            filename = f"{slugify(product.name)}_{product.id}{os.path.splitext(imgfile.name)[1]}"
            file = fss.save(filename, imgfile)
            product.img = fss.url(file)
        else:
            product.img = "default.jpg"
        product.save()
        messages.info(request, "Product has been inserted successfully.")
        return redirect("createprod")
    else:
        categories = Category.objects.all()
        return render(request, 'createprod.html', {'categories': categories})

def editproduct(request,product_name):
    product = get_object_or_404(Product, name=product_name)
    if request.method == 'POST':
        price = request.POST.get("price")
        qty = request.POST.get("qty")
        u_id = request.session.get('user_id')
        status = request.POST.get('status')
        try:
            user = User.objects.get(id=u_id)
        except User.DoesNotExist:
            messages.error(request, "User not logged in.")
            return redirect('login')
        product.price = price
        product.qty = qty
        product.user = user
        product.status = status
        product.save()
        messages.info(request, "Product has been edited successfully.")
        return redirect("dashboard")
    else:
        return render(request, 'edit_product.html', {'product': product})

def category_related_products(request,category_name):
    categories = Category.objects.all()
    category = get_object_or_404(Category, name=category_name)
    products = Product.objects.filter(category=category)
    context = {
        'category':category,
        'products': products,
        'category_name': category_name,
        'categories': categories,
    }
    return render(request, 'category_related_products.html', context)

def fetch_news():
    api_key = 'f274f6a51cd94add837984e51a09312e'
    url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}'
    response = requests.get(url)
    news_data = response.json()
    news_data['articles'] = news_data['articles'][:5]
    return news_data

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
    return render(request, 'view_cart.html', context)

def deleteproduct(request,product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, f"Product '{product.name}' has been deleted successfully.")
        return redirect('dashboard')
    return render(request, 'confirm_delete.html', {'product': product})
def search(request):
    query = request.GET.get('q')
    if query:
        search_results = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(brand__icontains=query) | 
            Q(category__name__icontains=query)
        )
    else:
        search_results = Product.objects.none()
    
    context = {
        'query': query,
        'search_results': search_results,
        'show_product': Product.objects.all(),
        'news_data': fetch_news(),
    }
    return render(request, 'home.html', context)
