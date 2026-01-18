from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import datetime

# توسيع نموذج المستخدم ليشمل الأنواع المختلفة
class User(AbstractUser):
    USER_TYPES = (
        ('root', 'Root (Zero)'),
        ('admin', 'Professor (Admin)'),
        ('student', 'Student'),
        ('guest', 'Guest'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='guest')
    is_frozen = models.BooleanField(default=False)
    failed_attempts = models.IntegerField(default=0)
    last_failed_attempt = models.DateTimeField(null=True, blank=True)
    department = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.username

# الأقسام والسمسترات
class Department(models.Model):
    name = models.CharField(max_length=100) # كهربائية، مدنية..
    def __str__(self): return self.name

class Semester(models.Model):
    number = models.IntegerField() # 1 to 10
    def __str__(self): return f"Semester {self.number}"

# المواد
class Course(models.Model):
    name = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    professor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'user_type': 'admin'})
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, related_name='course_updates', on_delete=models.SET_NULL, null=True)

    def __str__(self): return self.name

# الملفات (محاضرات، تمارين..)
class CourseFile(models.Model):
    FILE_TYPES = (
        ('lecture', 'محاضرة'),
        ('reference', 'مرجع'),
        ('exercise', 'تمارين'),
        ('exam', 'امتحانات'),
    )
    course = models.ForeignKey(Course, related_name='files', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='course_materials/')
    file_type = models.CharField(max_length=20, choices=FILE_TYPES)
    uploaded_at = models.DateTimeField(auto_now_add=True)

# المنتدى
class ForumPost(models.Model):
    course = models.ForeignKey(Course, related_name='posts', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='forum_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

# سجل الدخول للمتابعة (Dashboard)
class LoginLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    username_attempt = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20) # Success, Failed
