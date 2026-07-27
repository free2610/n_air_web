import random
import numpy as np
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Avg, Q
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import requests
from .models import Category, Advertising, Cart, CartItem, Sneakers, Buy, Review
from .forms import ContactForm, ChoicesForm, ProfileUpdateForm
# 8974045404:AAHoWSVIwZqKaBf6th5qttttA5hlIE7m89U

# 1. DOIMIY ISHLAYDIGAN PROFIL (XARIDLAR TARIXI VA KATEGORIYALAR BILAN)
@login_required
def profile(request):
    ctg = Category.objects.all() # base.html menyusi buzilmasligi uchun
    
    # Buyurtmalarni foydalanuvchining ismi va emaili bo'yicha kafolatlangan qidiruv
    user_email = request.user.email if request.user.email else f"{request.user.username}@mail.com"
    my_orders = Buy.objects.filter(
        Q(name=request.user.username) | Q(email=user_email)
    ).order_by('-id')
    
    ctx = {
        'ctg': ctg,
        'my_orders': my_orders
    }
    return render(request, 'blog/profile.html', ctx)


# 2. XAVFSIZ BUYURTMA BERISH FUNKSIYASI
@login_required
def checkout_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    
    if not cart_items.exists():
        return redirect('view_cart')
        
    if request.method == 'POST':
        name = request.POST.get('name', request.user.username)
        phone = request.POST.get('phone')
        size = request.POST.get('size', '42')
        map_location = request.POST.get('map', 'Kiritilmagan')
        user_email = request.user.email if request.user.email else f"{request.user.username}@mail.com"
        
        # Bot xabari uchun mahsulotlar ro'yxatini yig'amiz
        products_text = ""
        
        for item in cart_items:
            quantity_str = str(item.quantity)
            if quantity_str not in ["1", "2", "3", "4", "5"]:
                quantity_str = "1"
                
            Buy.objects.create(
                name=name,
                phone=phone,
                product=item.product,
                size=size,
                how=quantity_str,
                map=map_location,
                email=user_email
            )
            
            # Har bir mahsulotni xabarga qo'shish
            products_text += f"👟 {item.product.name} | o'lcham: {size} | {quantity_str} dona\n"
        
        # --- TELEGRAMGA XABAR YUBORISH QISMI ---
        try:
            BOT_TOKEN = "8974045404:AAHoWSVIwZqKaBf6th5qttttA5hlIE7m89U"
            CHAT_ID = "8029403026"
            
            # Google Maps havolasini yasash
            map_link = f"https://www.google.com/maps?q={map_location}" if "," in map_location else "Kiritilmagan"
            
            telegram_msg = (
                f"🔥 *YANGI BUYURTMA KELDI!*\n\n"
                f"👤 *Mijoz:* {name}\n"
                f"📞 *Telefon:* {phone}\n"
                f"📧 *Email:* {user_email}\n\n"
                f"🛒 *Mahsulotlar:*\n{products_text}\n"
                f"📍 *Manzil (Google Map):* [Xaritani ochish]({map_link})"
            )
            
            # Telegram API ga so'rov yuborish
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            requests.post(url, data={"chat_id": CHAT_ID, "text": telegram_msg, "parse_mode": "Markdown"})
        except Exception as e:
            print("Telegram xabar yuborishda xato:", e)
        # ----------------------------------------
        
        cart_items.delete()
        return render(request, 'blog/checkout_success.html')
        
    return render(request, 'blog/checkout_form.html', {'cart': cart})


# 3. KROSSOVKA SAHIFASI (REYTING VA SHARHLAR BILAN)
def single(request, pk=None):
    ctg = Category.objects.all()
    sneakers = Sneakers.objects.all()
    
    try:
        random_s = np.random.choice(sneakers, size=3, replace=False)
    except ValueError:
        random_s = sneakers
        
    product_pk = get_object_or_404(Sneakers, pk=pk)
    
    if request.method == 'POST' and 'submit_review' in request.POST:
        rating = request.POST.get('rating', 5)
        comment = request.POST.get('comment', '')
        
        Review.objects.create(
            product=product_pk,
            user=request.user,
            rating=int(rating),
            comment=comment
        )
        return redirect('single', pk=pk)
        
    reviews = Review.objects.filter(product=product_pk).select_related('user').order_by('-created_at')
    
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    if average_rating is None:
        average_rating = 5.0
    else:
        average_rating = round(average_rating, 1)

    ctx = {
        'ctg': ctg,
        'product_pk': product_pk,
        'random_s': random_s,
        'sneakers': sneakers,
        'reviews': reviews,
        'average_rating': average_rating,
    }
    return render(request, 'blog/single.html', ctx)


# 4. SAVAT BILAN ISHLASH FUNKSIYALARI
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Sneakers, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
        
    return redirect('view_cart')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('view_cart')

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'blog/cart.html', {'cart': cart})


# 5. FOYDALANUVCHI PROFILINI TAHRIRLASH
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profilingiz muvaffaqiyatli yangilandi!")
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'blog/edit_profile.html', {'form': form})


# 6. TIZIMGA KIRISH VA CHIQISH
def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
    return render(request, 'blog/login.html')

def logout_user(request):
    logout(request)
    return redirect('home')


# 7. BOSH SAHIFA (QIDIRUV INTEGRATSIYASI BILAN)
def home(requests):
    ctg = Category.objects.all()
    advertising = Advertising.objects.all()
    
    # Qidiruv so'rovini olish
    query = requests.GET.get('search')
    if query:
        # Qidiruvni kengaytiramiz: Nomi, Ikkinchi nomi yoki Tavsifida shu so'z bo'lsa topadi
        sneaker = Sneakers.objects.filter(
            Q(name__icontains=query) | 
            Q(last_name__icontains=query) | 
            Q(character__icontains=query)
        ).distinct() # Takroriy nusxalar chiqmasligi uchun distinct() qo'shdik
    else:
        # So'rov bo'lmasa, barcha mahsulotlarni ko'rsatamiz
        sneaker = Sneakers.objects.all()
        
    random_sneak = random.choice(advertising) if advertising.exists() else None
    
    ctx = {
        'ctg': ctg,
        'sneaker': sneaker,
        'random_sneak': random_sneak,
        'query': query, # Qidirilgan so'zni input ichida qoldirish uchun
    }
    return render(requests, 'blog/index.html', ctx)

# 8. ALOQA SAHIFASI
def contact(requests):
    ctg = Category.objects.all()
    if requests.method == 'POST':
        forms = ContactForm(requests.POST)
        if forms.is_valid():
            forms.save()
            return redirect('home')
    ctx = {'ctg': ctg}
    return render(requests, 'blog/contact.html', ctx)


# 9. RO'YXATDAN O'TISH
def register(request):
    ctg = Category.objects.all()
    if request.method == 'POST':
        username = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('home')
    return render(request, 'blog/register.html', {'ctg': ctg})


# 10. MAHSULOTLAR KATEGORIYASI
def products(requests, slug=None):
    ctg = Category.objects.all()
    category = Category.objects.get(slug=slug)
    sneaker = Sneakers.objects.all().filter(type_id=category.id)
    ctx = {
        'ctg': ctg,
        'category': category,
        'sneaker': sneaker,
    }
    return render(requests, 'blog/products.html', ctx)