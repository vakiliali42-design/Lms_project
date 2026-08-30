# courses/forms.py
from .models import Course, Lesson, CourseContent, Review
from django import forms
from .models import Course, Lesson, CourseContent

class CourseForm(forms.ModelForm):
    start_date = forms.DateField(
        required=False,
        label="start_date",
        widget=forms.DateInput(attrs={
            "type": "date",
            'class': 'form_control'
        })
    )

    end_date = forms.DateField(
        required=False,
        label="end_date",
        widget=forms.DateInput(attrs={
            "type": "date",
            'class': 'form_control'
        })
    )

    class Meta:
        model  = Course
        fields = ['title', 'description', 'category', 'thumbnail', 'level', 'price', 'is_published', 'start_date', 'end_date']

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end   = cleaned_data.get('end_date')

        if start and end and start > end:
            raise forms.ValidationError(
                'تاریخ پایان باید بعد از تاریخ شروع باشد.'
            )
        return cleaned_data

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