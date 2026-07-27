from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
# from .models import Sneakers


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}ning savatchasi"

    @property
    def get_total_price(self):
        return sum(item.get_cost for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    # Loyihangizdagi mahsulot modeli 'Card' bo'lgani uchun shu yerga ulaymiz
    product = models.ForeignKey('Sneakers', on_delete=models.CASCADE) 
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} dona"

    @property
    def get_cost(self):
        return self.product.price * self.quantity
# Create your models here.
class Category(models.Model):
    name= models.CharField(max_length=255)
    slug = models.SlugField(unique=True,blank=True)
    image = models.ImageField()

    def save(self, *args,**kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Category, self).save(*args,**kwargs)
    def __str__(self):
        return self.name

class Sneakers(models.Model):
    name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    type = models.ForeignKey(Category, on_delete=models.CASCADE)
    character = models.TextField()
    UZ = "so'm"
    RU = "₽"
    ENG = "$"
    the_price = (
        (UZ, "so'm"),
        (RU, "₽"),
        (ENG, "$"),
    )
    def __str__(self):
        return self.name

    price_type = models.CharField(max_length=10,
                                  choices=the_price,
                                  default="so'm")
    price = models.IntegerField()
    image =  models.ImageField()
    def __str__(self):
        return self.name
    

class Review(models.Model):
    product = models.ForeignKey(Sneakers, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(max_length=500)
    rating = models.IntegerField(default=5) # 1 dan 5 gacha bo'lgan raqam
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}★)"




class Buy(models.Model):
    name = models.CharField(max_length=156)
    phone = models.CharField(max_length=30)
    product = models.ForeignKey(Sneakers, on_delete=models.CASCADE, null=True)
    ALL_SIZES=(
        ("36","36"),
        ("37","37"),
        ("38","38"),
        ("39","39"),
        ("40","40"),
        ("41","41"),
        ("42","42"),
        ("43","43"),
        ("44","44"),
    )
    size= models.CharField(max_length=100, choices=ALL_SIZES)
    ALL_VALUES = (
        ("1","1"),
        ("2","2"),
        ("3","3"),
        ("4","4"),
        ("5","5"),
    )
    how = models.CharField(max_length=100,choices=ALL_VALUES)
    map = models.TextField()
    email = models.EmailField(blank=True)
    STATUS_CHOICES = (
        ('received', 'Buyurtma qabul qilindi 📥'),
        ('assembled', 'Buyurtma yig\'ildi 📦'),
        ('shipping', 'Yo\'lda 🚚'),
        ('delivered', 'Yetkazib berildi ✅'),
        ('canceled', 'Bekor qilindi ❌'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received')
    def __str__(self):
        return self.name

class Advertising(models.Model):
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100)
    image = models.ImageField()
    def __str__(self):
        return self.title



class Register(models.Model):
    name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    email = models.EmailField(blank=True)
    password = models.CharField(max_length=32)
    phone = models.CharField(max_length=32)
    message = models.TextField()

    def __str__(self):
        return self.name