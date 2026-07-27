from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            # Ruxsat berilgan barcha URL nomlari (Parolni tiklash sahifalari qo'shildi)
            allowed_names = [
                'login', 
                'register', 
                'signup',
                'password_reset',          # Email kiritish sahifasi
                'password_reset_done',     # Email jo'natildi xabari
                'password_reset_complete'  # Parol o'zgardi xabari
            ]
            
            allowed_urls = []
            for name in allowed_names:
                try:
                    allowed_urls.append(reverse(name))
                except NoReverseMatch:
                    pass

            # Diqqat: Parolni tiklash havolasi (token) dinamik bo'lgani uchun uni startswith orqali tekshiramiz
            # Bu foydalanuvchi pochtasiga boradigan '/password-reset-confirm/uid/token/' linkini bloklab qo'ymaslik uchun kerak
            is_reset_confirm = request.path.startswith('/password-reset-confirm/')

            # Agar foydalanuvchi ruxsat berilmagan sahifaga kirsa, loginga yuboriladi
            if (request.path not in allowed_urls 
                    and not is_reset_confirm 
                    and not request.path.startswith('/static/') 
                    and not request.path.startswith('/media/')):
                return redirect('login')

        response = self.get_response(request)
        return response