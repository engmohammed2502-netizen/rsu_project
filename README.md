# rsu_project
مكتبة كلية الهندسة بواسطة الباش مهندس زيرو



# تحديث مستودعات النظام
sudo apt update && sudo apt upgrade -y

# تثبيت الأدوات الأساسية (Git و Docker)
sudo apt install git docker.io docker-compose-v2 -y

# التأكد من تشغيل خدمة دوكر عند الإقلاع
sudo systemctl enable --now docker



# جلب الكود من GitHub
git clone [رابط_المستودع_الخاص_بك]

# الدخول إلى المجلد الرئيسي (الذي يحتوي على settings.py و Dockerfile)
cd rsu_project



docker compose --build -d

docker compose up -d


sudo docker compose exec web python manage.py makemigrations library




sudo docker compose exec web python manage.py migrate


#انشاء حساب الروت للتحكم الكامل بالموقع بعد تنفيذ المر 
#ادخل اسم المدير والايميل والباسوورد 

sudo docker compose exec web python manage.py createsuperuser

docker compose restart wed


#finish

