from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import *
from django.contrib import messages
from datetime import timedelta

def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # البحث عن المستخدم للتحقق من التجميد قبل فحص الباسورد
        try:
            user_obj = User.objects.get(username=username)
            if user_obj.is_frozen:
                # فك التجميد إذا مر يوم
                if timezone.now() > user_obj.last_failed_attempt + timedelta(days=1):
                    user_obj.is_frozen = False
                    user_obj.failed_attempts = 0
                    user_obj.save()
                else:
                    return render(request, 'login.html', {'error': 'حسابك مجمد. الرجاء التواصل مع الإدارة.'})
        except User.DoesNotExist:
            pass # سيتعامل معه authenticate

        user = authenticate(request, username=username, password=password)
        
        # تسجيل المحاولة في السجل
        ip = request.META.get('REMOTE_ADDR')
        
        if user is not None:
            # تصفير المحاولات الفاشلة
            user.failed_attempts = 0
            user.save()
            
            login(request, user)
            LoginLog.objects.create(user=user, username_attempt=username, ip_address=ip, status='Success')
            
            if user.user_type == 'guest':
                request.session.set_expiry(1800) # 30 دقيقة للضيف
            
            if user.user_type == 'root':
                return redirect('root_dashboard')
            return redirect('home')
        else:
            # منطق الفشل والتجميد
            try:
                user_obj = User.objects.get(username=username)
                user_obj.failed_attempts += 1
                user_obj.last_failed_attempt = timezone.now()
                if user_obj.failed_attempts >= 5:
                    user_obj.is_frozen = True
                user_obj.save()
            except User.DoesNotExist:
                pass
            
            LoginLog.objects.create(username_attempt=username, ip_address=ip, status='Failed')
            return render(request, 'login.html', {'error': 'بيانات غير صحيحة أو تم تجميد الحساب'})

    return render(request, 'login.html')

def guest_login(request):
    # إنشاء مستخدم ضيف مؤقت أو استخدام مستخدم ضيف عام
    guest_name = request.POST.get('guest_name', 'Guest')
    # (في التطبيق الحقيقي يفضل استخدام Sessions بدون إنشاء User في الداتابيز للضيوف لتجنب الامتلاء)
    # ولكن للتبسيط سنستخدم حساب ضيف موحد
    return redirect('home') # يتم التعامل معه في الصلاحيات
