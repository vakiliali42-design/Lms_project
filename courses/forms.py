# courses/forms.py
from .models import Course, Lesson, CourseContent, Review
from django import forms
from .models import Course, Lesson, CourseContent

class CourseForm(forms.ModelForm):
    class Meta:
        model  = Course
        fields = ['title', 'description', 'category', 'thumbnail', 'level', 'price', 'is_published']

class LessonForm(forms.ModelForm):
    class Meta:
        model  = Lesson
        fields = ['title', 'content', 'video_url', 'file', 'order']

class CourseContentForm(forms.ModelForm):
    class Meta:
        model  = CourseContent
        fields = ['title', 'file', 'description']


class ReviewForm(forms.ModelForm):
    score = forms.ChoiceField(
        choices=Review.SCORE_CHOICES,
        label='امتیاز',
        widget=forms.RadioSelect(attrs={'class': 'star-radio'})
    )

    class Meta:
        model   = Review
        fields  = ['score', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'نظر خود را بنویسید...',
                'class': 'form-control'
            })
        }
        labels = {'comment': 'نظر'}