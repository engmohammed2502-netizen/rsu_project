from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# >>>>>>>>> بداية الإضافة الجديدة (استيراد دالة التحميل) >>>>>>>>>
from django.http import FileResponse, Http404
# <<<<<<<<< نهاية الإضافة الجديدة <<<<<<<<<
from .models import User, Course, Department, CourseFile, ForumPost, GuestLog
import os

def home(request):
    # >>>>>>>>> بداية الإضافة الجديدة المدمجة >>>>>>>>>

    # 1. التحقق من الهوية (الأمان): منع الدخول إلا للأعضاء أو الزوار الذين سجلوا أسماءهم
    if not request.user.is_authenticated and 'guest_name' not in request.session:
        return redirect('login')

    # 2. جلب البيانات: نستخدم قاعدة البيانات لجلب الأقسام بدلاً من القائمة الثابتة DEPARTMENTS
    # هذا يتيح لك إضافة أقسام جديدة من لوحة التحكم مباشرة
    departments = Department.objects.all()

    # 3. تحديد اسم المستخدم للترحيب:
    # - إذا كان مسجل دخول: يأخذ اسمه الكامل (full_name)
    # - إذا كان زائراً: يأخذ الاسم من الجلسة (guest_name)
    # - إذا فشل الاثنان: يظهر كلمة "زائر" كخيار احتياطي
    if request.user.is_authenticated:
        name_to_display = request.user.full_name
    else:
        name_to_display = request.session.get('guest_name', "زائر")

    # 4. بناء السياق (Context) كما في كودك الأصلي تماماً
    context = {
        'departments': departments,
        'user_name': name_to_display,
    }
    
    # <<<<<<<<< نهاية الإضافة الجديدة المدمجة <<<<<<<<<

    return render(request, 'library/home.html', context)



def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # >>>>>>>>> بداية الإضافة الجديدة (منع الحساب المجمد) >>>>>>>>>
            if user.is_frozen:
                messages.error(request, 'عذراً، حسابك مجمد. يرجى مراجعة إدارة الكلية.')
                return redirect('login')
            # <<<<<<<<< نهاية الإضافة الجديدة <<<<<<<<<
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')
    return render(request, 'library/login.html')



def guest_login(request):
    if request.method == 'POST':
        name = request.POST.get('guest_name')
        if name:
            # >>>>>>>>> بداية الإضافة المدمجة (Best of Both Worlds) >>>>>>>>>
            
            # 1. تسجيل الزائر في قاعدة البيانات (مطلب المشروع الأساسي للتوثيق)
            GuestLog.objects.create(name=name)
            
            # 2. إعدادات الجلسة (من كودك القديم لضمان التوافق)
            request.session['is_guest'] = True
            request.session['guest_name'] = name
            
            # 3. تحديد مدة البقاء (30 دقيقة = 1800 ثانية) كما كانت عندك
            request.session.set_expiry(1800) 
            
            return redirect('home')
            # <<<<<<<<< نهاية الإضافة المدمجة <<<<<<<<<
            
    return render(request, 'library/guest_login.html')



def department_view(request, dept_id):
    dept = get_object_or_404(Department, id=dept_id)
    semester = request.GET.get('semester')
    courses = Course.objects.filter(department=dept, semester=semester) if semester else []
    return render(request, 'library/department.html', {'dept': dept, 'courses': courses, 'semester': semester})

def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    # >>>>>>>>> بداية الإضافة الجديدة (تمرير اسم الزائر أو العضو) >>>>>>>>>
    if not request.user.is_authenticated and 'guest_name' not in request.session:
        return redirect('login')
    context = {
        'course': course,
        'user_name': request.user.full_name if request.user.is_authenticated else request.session.get('guest_name')
    }
    # <<<<<<<<< نهاية الإضافة الجديدة <<<<<<<<<
    return render(request, 'library/course_detail.html', context)

# >>>>>>>>> بداية الإضافة الجديدة (دالة المنتدى ودالة التحميل) >>>>>>>>>
def add_comment(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id)
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        parent_obj = ForumPost.objects.get(id=parent_id) if parent_id else None
        
        user = request.user if request.user.is_authenticated else None
        guest_name = request.session.get('guest_name') if not request.user.is_authenticated else None

        if content:
            ForumPost.objects.create(course=course, user=user, guest_name=guest_name, content=content, parent=parent_obj)
    return redirect('course_detail', course_id=course_id)

def download_file(request, file_id):
    course_file = get_object_or_404(CourseFile, id=file_id)
    file_path = course_file.file.path
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    else:
        raise Http404("الملف غير موجود")
# <<<<<<<<< نهاية الإضافة الجديدة <<<<<<<<<

@login_required
def root_dashboard(request):
    if request.user.user_type != 'ROOT':
        return redirect('home')
    return render(request, 'library/dashboard.html')

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
            User.objects.create_user(username=username, password=password, full_name=full_name, user_type=user_type)
            messages.success(request, f'تم إضافة {full_name} بنجاح')
            return redirect('root_dashboard')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {e}')
    return render(request, 'library/add_user.html')
