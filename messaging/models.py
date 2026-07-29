from django.db import models
from accounts.models import User

class Conversation(models.Model):
    participants = models.ManyToManyField(
        User, related_name='conversation'
    )
created_at = models.DateTimeField(auto_now_add=True)
uploaded_at = models.DateTimeField(auto_now=True)

class Meta:
    ordering = ['-uploaded_at']

def __str__(self):
        names = ', '.join(
            p.get_full_name() or p.username
            for p in self.participants.all()
        )
        return f'گفتگو: {names}'

def get_other_user(self, user):
        """نفر مقابل در گفتگو"""
        return self.participants.exclude(pk=user.pk).first()

def last_message(self):
        return self.messages.last()

def unread_count(self, user):
    return self.messages.filter(
        is_read=False
    ).exclude(sender=user).count()

class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE,
        related_name='messages'
    )
    sender    = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content   = models.TextField(max_length=1000)
    is_read   = models.BooleanField(default=False)
    created_at= models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def str(self):
        return f"{self.sender.username}: {self.content[:30]}"








