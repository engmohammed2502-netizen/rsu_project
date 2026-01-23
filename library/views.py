from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404
from .models import User, Course, Department, CourseFile, ForumPost, GuestLog
import os

# --- الصفحة الرئيسية ---
def home(request):
    departments = Department.objects.all()
    # التحقق من جلسة الزائر أو تسجيل الدخول
    if not request.user.is_authenticated and 'guest_name' not in request.session:
        return redirect('login')
    return render(request, 'library/home.html', {'departments': departments})

# --- تسجيل دخول الأعضاء ---
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_frozen:
                messages.error(request, 'عذراً، حسابك مجمد. يرجى مراجعة إدارة الكلية.')
                return redirect('login')
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')
    return render(request, 'library/login.html')

# --- تسجيل دخول الزوار ---
def guest_login(request):
    if request.method == 'POST':
        name = request.POST.get('guest_name')
        if name:
            GuestLog.objects.create(name=name)
            request.session['guest_name'] = name
            return redirect('home')
    return render(request, 'library/guest_login.html')

# --- عرض المواد حسب القسم والسمستر ---
def department_view(request, dept_id):
    dept = get_object_or_404(Department, id=dept_id)
    semester = request.GET.get('semester')
    courses = Course.objects.filter(department=dept, semester=semester) if semester else []
    return render(request, 'library/department.html', {'dept': dept, 'courses': courses, 'semester': semester})

# --- تفاصيل المادة والمنتدى والتحميل ---
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if not request.user.is_authenticated and 'guest_name' not in request.session:
        return redirect('login')
        
    context = {
        'course': course,
        'user_name': request.user.full_name if request.user.is_authenticated else request.session.get('guest_name')
    }
    return render(request, 'library/course_detail.html', context)

# --- دالة إضافة تعليق للمنتدى ---
def add_comment(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id)
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        
        parent_obj = ForumPost.objects.get(id=parent_id) if parent_id else None
        
        # تحديد اسم الكاتب (عضو أو زائر)
        user = request.user if request.user.is_authenticated else None
        guest_name = request.session.get('guest_name') if not request.user.is_authenticated else None

        if content:
            ForumPost.objects.create(
                course=course,
                user=user,
                guest_name=guest_name,
                content=content,
                parent=parent_obj
            )
    return redirect('course_detail', course_id=course_id)

# --- دالة تحميل الملفات (لحل مشكلة التنزيل) ---
def download_file(request, file_id):
    course_file = get_object_or_404(CourseFile, id=file_id)
    file_path = course_file.file.path
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    else:
        raise Http404("الملف غير موجود")

# --- لوحة تحكم الروت ---
@login_required
def root_dashboard(request):
    if request.user.user_type != 'ROOT':
        return redirect('home')
    return render(request, 'library/dashboard.html')

# --- إضافة مستخدم جديد ---
@login_required
def add_user_view(request):
    if request.user.user_type != 'ROOT':
        return redirect('home')
        
    if request.method == 'POST':
        try:
            full_name = request.POST.get('full_name')
            username = request.POST.get('username')
            password = request.POST.get('password')
            user_type = request.POST.get('user_type')
            
            user = User.objects.create_user(username=username, password=password, full_name=full_name, user_type=user_type)
            messages.success(request, f'تم إضافة {full_name} بنجاح')
            return redirect('root_dashboard')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {e}')
            
    return render(request, 'library/add_user.html')
