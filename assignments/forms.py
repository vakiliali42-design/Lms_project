# assignments/forms.py

from django import forms
from .models import Assignment, Submission

class AssignmentForm(forms.ModelForm):
    class Meta:
        model  = Assignment
        fields = ['title', 'description', 'file', 'due_date', 'max_score']
        widgets = {'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})}

class SubmissionForm(forms.ModelForm):
    class Meta:
        model  = Submission
        fields = ['file', 'note']

class GradeForm(forms.ModelForm):
    class Meta:
        model  = Submission
        fields = ['score', 'feedback']