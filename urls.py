from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # رابط لوحة تحكم الإدارة التي دخلت عليها سابقاً
    path('admin/', admin.site.urls),
    
    # هذا السطر هو الذي يربط مشروعك بمجلد المكتبة (library)
    path('', include('library.urls')),
]

# السماح للسيرفر بعرض ملفات الـ PDF والصور التي يرفعها الدكاترة
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
