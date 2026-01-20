from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import FileExtensionValidator
import os

# --- القوائم الثابتة (الخيارات) ---
USER_TYPES = (
    ('ROOT', 'Root (Zero)'),
    ('ADMIN', 'Admin (Professor)'),
    ('STUDENT', 'Student'),
    ('GUEST', 'Guest'),
)

DEPARTMENTS = (
    ('ELEC', 'الهندسة الكهربائية'),
    ('CHEM', 'الهندسة الكيميائية'),
    ('CIVIL', 'الهندسة المدنية'),
    ('MECH', 'الهندسة الميكانيكية'),
    ('MED', 'الهندسة الطبية'),
)

SEMESTERS = [(i, f'السمستر {i}') for i in range(1, 11)]

MATERIAL_TYPES = (
    ('LECTURE', 'محاضرة'),
    ('REFERENCE', 'مرجع'),
    ('EXERCISE', 'تمارين'),
    ('EXAM', 'امتحانات'),
)

# --- 1. جدول المستخدمين المخصص ---
class User(AbstractUser):
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='STUDENT')
    student_id = models.CharField(max_length=12, blank=True, null=True, unique=True, verbose_name="الرقم الجامعي")
    full_name = models.CharField(max_length=100, verbose_name="الاسم الكامل")
    
    # للأمان والتجميد
    failed_login_attempts = models.IntegerField(default=0)
    is_frozen = models.BooleanField(default=False)
    frozen_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.full_name if self.full_name else self.username

# --- 2. جدول المواد الدراسية ---
class Course(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم المادة")
    code = models.CharField(max_length=20, verbose_name="كود المادة")
    department = models.CharField(max_length=10, choices=DEPARTMENTS, verbose_name="القسم")
    semester = models.IntegerField(choices=SEMESTERS, verbose_name="السمستر")
    professor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'user_type': 'ADMIN'}, verbose_name="أستاذ المقرر")
    description = models.TextField(blank=True, verbose_name="وصف المادة")
    last_update = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    def __str__(self):
        return f"{self.name} - {self.get_department_display()}"

# --- 3. جدول ملفات المواد (المحتوى) ---
class CourseFile(models.Model):
    course = models.ForeignKey(Course, related_name='files', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, verbose_name="عنوان الملف")
    file_type = models.CharField(max_length=20, choices=MATERIAL_TYPES, verbose_name="نوع الملف")
    file = models.FileField(
        upload_to='course_materials/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'exe', 'zip', 'ppt', 'pptx', 'docx', 'doc', 'jpg', 'png', 'jpeg'])],
        verbose_name="الملف"
    )
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# --- 4. جدول روابط الفيديو (يوتيوب) ---
class CourseVideo(models.Model):
    course = models.ForeignKey(Course, related_name='videos', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, verbose_name="عنوان الفيديو")
    url = models.URLField(verbose_name="رابط اليوتيوب")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

# --- 5. جدول المنتدى (النقاشات) ---
class ForumPost(models.Model):
    course = models.ForeignKey(Course, related_name='posts', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(verbose_name="نص الرسالة")
    image = models.ImageField(upload_to='forum_images/', blank=True, null=True, verbose_name="صورة مرفقة")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.author.full_name} in {self.course.name}"

class ForumReply(models.Model):
    post = models.ForeignKey(ForumPost, related_name='replies', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(verbose_name="الرد")
    created_at = models.DateTimeField(auto_now_add=True)

# --- 6. جدول الشعارات وإعدادات الموقع ---
class SiteSettings(models.Model):
    college_logo = models.ImageField(upload_to='logos/', default='logos/default_college.png')
    university_logo = models.ImageField(upload_to='logos/', default='logos/default_uni.png')
    
    def save(self, *args, **kwargs):
        # ضمان وجود صف واحد فقط للإعدادات
        if not self.pk and SiteSettings.objects.exists():
            return
        return super(SiteSettings, self).save(*args, **kwargs)

# --- 7. سجل المتابعة للروت (Dashboard Logs) ---
class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"
