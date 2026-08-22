from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re


def clean_text(text):
    """
    متن رو تمیز می‌کنه:
    - حروف کوچک میکنه
    - کاراکترهای خاص حذف میکنه
    - فاصله‌های اضافه حذف میکنه
    """
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def check_plagiarism(assignment, threshold=0.7):
    """
    تکالیف یه assignment رو با هم مقایسه میکنه.

    threshold = 0.7 یعنی:
    اگه شباهت بیشتر از ۷۰٪ بود → تقلب احتمالی

    برمیگردونه لیستی از جفت‌هایی که مشکوکن:
    [
        {
            'student1': 'احمد',
            'student2': 'علی',
            'similarity': 0.85,
            'level': 'HIGH'
        }
    ]

    TF-IDF چیه؟
    Term Frequency-Inverse Document Frequency
    به هر کلمه یه وزن میده:
    - کلماتی که در یه متن زیاد هستن ولی در بقیه کم → وزن بالا
    - کلماتی که در همه متن‌ها زیادن (مثل "و" "که") → وزن پایین
    """
    from assignments.models import Submission

    submissions = list(
        Submission.objects.filter(
            assignment=assignment
        ).select_related('student')
    )

    if len(submissions) < 2:
        return []

    # متن‌ها رو استخراج کن
    texts   = [clean_text(s.note or '') for s in submissions]
    valid   = [(i, t) for i, t in enumerate(texts) if len(t) > 10]

    if len(valid) < 2:
        return []

    indices, clean_texts = zip(*valid)

    # TF-IDF Vectorizer
    # هر متن رو به یه بردار عددی تبدیل میکنه
    vectorizer = TfidfVectorizer(
        analyzer         = 'char_wb',  # کاراکتر به کاراکتر (برای فارسی بهتره)
        ngram_range      = (2, 4),     # ۲ تا ۴ کاراکتر پشت هم
        min_df           = 1,
        max_features     = 1000
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(clean_texts)
    except Exception:
        return []

    # محاسبه شباهت بین همه جفت‌ها
    similarity_matrix = cosine_similarity(tfidf_matrix)

    results = []
    for i in range(len(indices)):
        for j in range(i + 1, len(indices)):
            sim = float(similarity_matrix[i][j])
            if sim >= threshold:
                # تعیین سطح خطر
                if sim >= 0.9:
                    level = 'VERY HIGH'
                    level_fa = 'خیلی زیاد'
                elif sim >= 0.8:
                    level = 'HIGH'
                    level_fa = 'زیاد'
                else:
                    level = 'MEDIUM'
                    level_fa = 'متوسط'

                s1 = submissions[indices[i]]
                s2 = submissions[indices[j]]

                results.append({
                    'student1':    s1.student,
                    'student2':    s2.student,
                    'submission1': s1,
                    'submission2': s2,
                    'similarity':  round(sim * 100, 1),
                    'level':       level,
                    'level_fa':    level_fa,
                })

    # مرتب‌سازی از بیشترین به کمترین شباهت
    results.sort(key=lambda x: x['similarity'], reverse=True)
    return results