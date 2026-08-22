from django.core.management.base import BaseCommand
from accounts.models import User
from courses.models import Course, Enrollment, Category
from assignments.models import Assignment, Submission
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'ایجاد داده تست برای AI'

    def handle(self, *args, **kwargs):

        # ── دسته‌بندی ────────────────────────────────────
        cat, _ = Category.objects.get_or_create(
            slug='programming',
            defaults={'name': 'برنامه‌نویسی'}
        )

        # ── دوره‌ها ──────────────────────────────────────
        courses_data = [
            ('دوره پایتون مقدماتی',   'python-basic'),
            ('دوره Django',            'django-course'),
            ('دوره Docker',            'docker-course'),
            ('دوره Linux',             'linux-course'),
            ('دوره Git و GitHub',      'git-course'),
        ]

        courses = []
        # پیدا کن یه استاد
        teacher = User.objects.filter(role='teacher').first()
        if not teacher:
            teacher = User.objects.create_user(
                username  = 'teacher_test',
                password  = 'test1234',
                role      = 'teacher',
                first_name= 'استاد',
                last_name = 'تست',
                email     = 'teacher@test.com',
            )
            self.stdout.write(f'✅ استاد تست ساخته شد')

        for title, slug in courses_data:
            course, created = Course.objects.get_or_create(
                slug=slug,
                defaults={
                    'title':        title,
                    'description':  f'توضیحات {title}',
                    'teacher':      teacher,
                    'category':     cat,
                    'level':        'beginner',
                    'price':        0,
                    'is_published': True,
                }
            )
            courses.append(course)
            if created:
                self.stdout.write(f'✅ دوره ساخته شد: {title}')

        # ── دانشجوها ─────────────────────────────────────
        students_data = [
            ('student1', 'علی', 'رضایی',  'ali@test.com'),
            ('student2', 'رضا', 'محمدی',  'reza@test.com'),
            ('student3', 'مریم','احمدی',  'maryam@test.com'),
            ('student4', 'سارا','حسینی',  'sara@test.com'),
            ('student5', 'امیر','کریمی',  'amir@test.com'),
            ('student6', 'نیلو','صادقی',  'nilo@test.com'),
        ]

        students = []
        for username, first, last, email in students_data:
            student, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'password':   'test1234',
                    'role':       'student',
                    'first_name': first,
                    'last_name':  last,
                    'email':      email,
                }
            )
            if created:
                student.set_password('test1234')
                student.save()
                self.stdout.write(f'✅ دانشجو ساخته شد: {first} {last}')
            students.append(student)

        # ── ثبت‌نام‌ها ───────────────────────────────────
        # الگوی ثبت‌نام — هر دانشجو در چه دوره‌هایی
        # اینطوری KNN می‌تونه الگو پیدا کنه
        enrollments_pattern = {
            'student1': [0, 1, 2],      # پایتون، Django، Docker
            'student2': [0, 1, 2, 3],   # + Linux
            'student3': [0, 1],         # پایتون، Django
            'student4': [2, 3, 4],      # Docker، Linux، Git
            'student5': [2, 3],         # Docker، Linux
            'student6': [0, 4],         # پایتون، Git
        }

        for student in students:
            pattern = enrollments_pattern.get(student.username, [0])
            for idx in pattern:
                Enrollment.objects.get_or_create(
                    student=students[students.index(student)],
                    course=courses[idx]
                )
                self.stdout.write('✅ ثبت‌نام‌ها ایجاد شد')

        # ── تکلیف تست ───────────────────────────────────
        assignment, created = Assignment.objects.get_or_create(
            title   = 'تکلیف تست AI',
            course  = courses[0],
            defaults={
                'teacher':     teacher,
                'description': 'این یه تکلیف تست برای بررسی تقلب هست',
                'due_date':    timezone.now() + timedelta(days=7),
                'max_score':   100,
            }
        )

        if created:
            self.stdout.write('✅ تکلیف تست ساخته شد')

        # ── ارسال تکلیف با متن‌های مشابه ────────────────
        # این متن‌ها شبیه همن تا تشخیص تقلب تست بشه
        similar_texts = [
            "حل مسئله با استفاده از حلقه for در پایتون و پیاده سازی الگوریتم مرتب سازی",
            "پیاده سازی الگوریتم مرتب سازی با استفاده از حلقه for در زبان پایتون",
            "کاملاً متفاوت: کار با دیکشنری در پایتون و متدهای آن مثل get و update",
        ]

        for i, student in enumerate(students[:3]):
            if Enrollment.objects.filter(
                student=student, course=courses[0]
            ).exists():
                sub, created = Submission.objects.get_or_create(
                    assignment=assignment,
                    student=student,
                    defaults={
                        'note':   similar_texts[i],
                        'status': 'submitted',
                        'file':   'submissions/test.txt',
                    }
                )
                if created:
                    self.stdout.write(
                        f'✅ ارسال تکلیف برای {student.username}'
                    )

        self.stdout.write(
            self.style.SUCCESS(
                '\n🎉 همه داده‌های تست ساخته شدن!\n'
                'یوزر: student1 تا student6\n'
                'رمز همه: test1234\n'
                f'تکلیف تست در دوره: {courses[0].title}'
            )
        )