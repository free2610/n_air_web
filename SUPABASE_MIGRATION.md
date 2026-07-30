# SQLite dan Supabase PostgreSQL ga ko'chirish

> Bu jarayon yangi yoki ma'lumotlari o'chirilishi mumkin bo'lgan Supabase
> database uchun mo'ljallangan. Production saytda yozuvlar kelishini vaqtincha
> to'xtating, aks holda dump olinganidan keyingi yozuvlar ko'chmay qoladi.

## 1. SQLite dan backup oling

PowerShell terminalida loyiha root katalogida quyidagilarni bajaring. Ushbu
bosqichda `.env` ichida `DATABASE_URL` bo'lmasligi kerak, chunki settings
fallback sifatida `db.sqlite3` ni tanlaydi.

```powershell
Copy-Item .env.example .env
# .env dan DATABASE_URL qatorini vaqtincha o'chiring yoki izohga oling.
.\.venv\Scripts\python.exe manage.py dumpdata --natural-foreign --natural-primary --exclude contenttypes --exclude auth.permission --indent 2 -o sqlite-data.json
Compress-Archive -Path media\* -DestinationPath media-backup.zip -Force
```

`sqlite-data.json` foydalanuvchilar, guruhlar, mahsulotlar, savat, buyurtma va
boshqa Django ma'lumotlarini saqlaydi. `contenttypes` va `auth.permission`
ko'chirilmaydi: ular PostgreSQL da `migrate` tomonidan qayta yaratiladi.

## 2. Supabase ga ulang

Supabase Dashboard -> **Connect** dan URI oling va `.env` dagi `DATABASE_URL`
qiymatini to'ldiring. Render/serverless uchun Transaction pooler URI ishlating
va `?sslmode=require` parametrini qoldiring. Parolda `@`, `:`, `/`, `#` bo'lsa,
ular URL-encoded bo'lishi shart.

```env
DATABASE_URL=postgresql://postgres.PROJECT_REF:URL_ENCODED_PASSWORD@aws-0-REGION.pooler.supabase.com:6543/postgres?sslmode=require
```

Avval schema va xizmat ma'lumotlarini yarating, keyin fixture ni yuklang:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py loaddata sqlite-data.json
.\.venv\Scripts\python.exe manage.py check --deploy
```

Tekshirish uchun:

```powershell
.\.venv\Scripts\python.exe manage.py shell -c "from first_n_air.models import Category, Sneakers, Buy; print(Category.objects.count(), Sneakers.objects.count(), Buy.objects.count())"
```

Kerak bo'lganda ketma-ketlik (sequence)larni PostgreSQL avtomatik sozlaydi.
Qo'lda SQL import yoki `--fake-initial` ishlatmang.

## Media va static fayllar

`ImageField` qiymatlari database fixture ichida faqat fayl yo'li sifatida
saqlanadi; rasmlarning o'zi `sqlite-data.json` ichiga kirmaydi. Shuning uchun
`media-backup.zip` ni saqlang. Developmentda uni `media/` papkasiga qaytarish
mumkin:

```powershell
Expand-Archive -Path media-backup.zip -DestinationPath media -Force
```

Productionda Render diskiga `media/` saqlash ishonchli emas. Rasmlarni Supabase
Storage yoki S3-compatible object storage ga yuklab, Django storage backendini
unga ulash kerak. `STATIC_ROOT` va WhiteNoise allaqachon static fayllar uchun
sozlangan; deploy build qadamida mavjud `build.sh` `collectstatic` va `migrate`
ni bajaradi.
