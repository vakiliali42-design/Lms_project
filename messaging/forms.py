# messaging/forms.py

from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        model   = Message
        fields  = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows':        3,
                'placeholder': 'پیام خود را بنویسید...',
                'class':       'form-control',
            })
        }
        labels = {'content': ''}