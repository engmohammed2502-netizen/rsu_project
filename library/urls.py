from django.urls import path
from . import views

urlpatterns = [
    # 1. صفحة تسجيل الدخول (الصفحة الرئيسية للموقع)
    path('', views.login_view, name='login'),
    
    # 2. صفحة الخروج وتدمير الجلسة
    path('logout/', views.logout_view, name='logout'),
    
    # 3. نظام دخول الضيوف (تسجيل الاسم والبدء)
    path('guest_login/', views.guest_login, name='guest_login'),

    # 4. واجهة المكتبة الرئيسية (Home)
    path('home/', views.home, name='home'),
    
    # 5. لوحة تحكم الروت (Zero) للمراقبة والإحصائيات
    path('dashboard/', views.root_dashboard, name='root_dashboard'),

    # 6. روابط الأقسام (كهرباء، مدنية، ميكانيكا، كيمياء، طبية)
    path('department/<str:dept_code>/', views.department_view, name='department'),
    
    # 7. روابط السمسترات داخل كل قسم
    path('department/<str:dept_code>/semester/<int:sem_id>/', views.semester_view, name='semester'),
    
    # 8. صفحة المادة العلمية (الملفات ومنتدى النقاش المطور)
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),

    # 9. رابط إضافة تعليق أو رد (جديد - لتفعيل المنتدى)
    # هذا الرابط هو المسؤول عن استقبال التعليقات الجديدة والردود على تعليقات سابقة
    path('course/<int:course_id>/add_comment/', views.add_comment, name='add_comment'),

    # 10. روابط العمليات (تحميل الملفات وحذفها)
    path('download/<int:file_id>/', views.download_file, name='download_file'),
    path('delete_file/<int:file_id>/', views.delete_file, name='delete_file'),
    
    # 11. إضافة مستخدم جديد (لصلاحيات الروت فقط)
    path('add-user/', views.add_user_view, name='add_user'),
]
