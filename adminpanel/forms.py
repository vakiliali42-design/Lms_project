# adminpanel/forms.py

from django import forms
from accounts.models import User
from courses.models import Course

class AdminUserForm(forms.ModelForm):
    password = forms.CharField(
        label='رمز عبور',
        required=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'خالی = بدون تغییر'}),
        help_text='فقط در صورت تغییر رمز پر کنید.'
    )

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name',
                  'email', 'role', 'is_active', 'password']
        labels = {
            'username':   'نام کاربری',
            'first_name': 'نام',
            'last_name':  'نام خانوادگی',
            'email':      'ایمیل',
            'role':       'نقش',
            'is_active':  'فعال',
        }


class AdminCourseForm(forms.ModelForm):
    class Meta:
        model  = Course
        fields = ['title', 'description', 'teacher',
                  'category', 'level', 'price', 'is_published']
        labels = {
            'title':        'عنوان',
            'description':  'توضیحات',
            'teacher':      'استاد',
            'category':     'دسته‌بندی',
            'level':        'سطح',
            'price':        'قیمت',
            'is_published': 'منتشر شده',
        }

    def init(self, *args, **kwargs):
        super().init(*args, **kwargs)
        # فقط استادها در لیست نشون داده بشن
        self.fields['teacher'].queryset = User.objects.filter(role='teacher')