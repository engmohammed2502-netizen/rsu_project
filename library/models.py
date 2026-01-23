from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    USER_TYPES = (
        ('ROOT', 'Root'),
        ('STUDENT', 'Student'),
        ('ADMIN', 'Professor/Admin'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='STUDENT')
    full_name = models.CharField(max_length=255, verbose_name="الاسم الكامل")
    
    # >>>>>>>>> بداية الإضافة الجديدة (تجميد الحساب) >>>>>>>>>
    is_frozen = models.BooleanField(default=False, verbose_name="تجميد الحساب")
    # <<<<<<<<< نهاية الإضافة الجديدة <<<<<<<<<

    def __str__(self):
        return self.username

# >>>>>>>>> بداية الإضافة الجديدة (جدول الزوار) >>>>>>>>>
class GuestLog(models.Model):
    name = models.CharField(max_length=255)
    entry_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.entry_time}"
# <<<<<<<<< نهاية الإضافة الجديدة <<<<<<<<<

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='departments/', blank=True, null=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    semester = models.IntegerField(default=1)
    professor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'user_type': 'ADMIN'})
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class CourseFile(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='files')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='course_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# >>>>>>>>> بداية الإضافة الجديدة (جدول المنتدى) >>>>>>>>>
class ForumPost(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    guest_name = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField(verbose_name="التعليق")
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
# <<<<<<<<< نهاية الإضافة الجديدة <<<<<<<<<
