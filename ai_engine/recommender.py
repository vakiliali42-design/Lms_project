import numpy as np
from sklearn.neighbors import NearestNeighbors


def get_course_recommendations(student, n_recommendations=5):
    """
    توصیه دوره با KNN.

    ساختار ماتریس:
    هر سطر = یه دانشجو
    هر ستون = یه دوره
    مقدار ۱ = ثبت‌نام کرده، ۰ = نکرده

         پایتون  Django  Docker  Linux
    احمد    1       1       0       0
    علی     1       1       1       0
    رضا     0       0       1       1
    """
    from accounts.models import User
    from courses.models import Course, Enrollment

    # همه دانشجوها و دوره‌ها
    all_students = list(User.objects.filter(role='student'))
    all_courses  = list(Course.objects.filter(is_published=True))

    if len(all_students) < 2 or len(all_courses) < 2:
        # داده کافی نیست
        return Course.objects.none()

    # ساخت ماتریس دانشجو-دوره
    student_idx = {s.pk: i for i, s in enumerate(all_students)}
    course_idx  = {c.pk: i for i, c in enumerate(all_courses)}

    # ماتریس صفر
    matrix = np.zeros((len(all_students), len(all_courses)))

    # پر کردن ماتریس
    for e in Enrollment.objects.select_related('student', 'course').all():
        si = student_idx.get(e.student_id)
        ci = course_idx.get(e.course_id)
        if si is not None and ci is not None:
            matrix[si][ci] = 1

    # اگه این دانشجو در ماتریس نیست
    if student.pk not in student_idx:
        # برگردون محبوب‌ترین دوره‌ها
        return Course.objects.filter(
            is_published=True
        ).order_by('-students')[:n_recommendations]

    # مدل KNN
    # metric='cosine' یعنی شباهت رو با زاویه بین بردارها حساب کن
    # n_neighbors=5 یعنی ۵ دانشجوی شبیه پیدا کن
    n_neighbors = min(6, len(all_students))
    model = NearestNeighbors(
        n_neighbors = n_neighbors,
        metric      = 'cosine',
        algorithm   = 'brute'
    )
    model.fit(matrix)

    # برداری که نشون میده این دانشجو چه دوره‌هایی داره
    student_vector = matrix[student_idx[student.pk]].reshape(1, -1)

    # پیدا کن شبیه‌ترین دانشجوها
    distances, indices = model.kneighbors(student_vector)

    # دوره‌هایی که این دانشجو الان داره
    my_courses = set(
        Enrollment.objects.filter(
            student=student
        ).values_list('course_id', flat=True)
    )

    # جمع‌آوری دوره‌های پیشنهادی
    recommended_pks = {}
    for i, idx in enumerate(indices[0][1:]):  # اول خودش رو skip کن
        similar_student = all_students[idx]
        their_courses = Enrollment.objects.filter(
            student=similar_student
        ).values_list('course_id', flat=True)

        for course_pk in their_courses:
            if course_pk not in my_courses:
                # هرچی شبیه‌تر، امتیاز بیشتر
                similarity = 1 - distances[0][i+1]
                recommended_pks[course_pk] = (
                    recommended_pks.get(course_pk, 0) + similarity
                )

    if not recommended_pks:
        return Course.objects.none()

    # مرتب‌سازی بر اساس امتیاز
    sorted_pks = sorted(
        recommended_pks,
        key=lambda x: recommended_pks[x],
        reverse=True
    )[:n_recommendations]

    return Course.objects.filter(pk__in=sorted_pks, is_published=True)