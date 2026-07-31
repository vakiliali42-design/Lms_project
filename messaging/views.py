from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Conversation, Message
from .forms import MessageForm
from accounts.models import User
from notifications.utils import send_notification


@login_required
def conversation_list(request):
    convs = request.user.conversations.prefetch_related(
        'participants',
        'messages'
    ).order_by('-uploaded_at')

    for conv in convs:
        conv.other_user = conv.get_other_user(request.user)
        conv.unread = conv.unread_count(request.user)

    return render(request, 'messaging/list.html', {
        'conversations': convs,
    })

@login_required
def conversation_detail(request, pk):
    """مشاهده و ارسال پیام در یه گفتگو"""
    conv = get_object_or_404(
        Conversation, pk=pk,
        participants=request.user
    )

    # علامت خوانده‌شده
    conv.messages.filter(
        is_read=False
    ).exclude(sender=request.user).update(is_read=True)

    form = MessageForm(request.POST or None)
    if form.is_valid():
        msg         = form.save(commit=False)
        msg.conversation = conv
        msg.sender       = request.user
        msg.save()

        # آپدیت زمان گفتگو
        conv.save()

        # اعلان به طرف مقابل
        other = conv.get_other_user(request.user)
        send_notification(
            recipient  = other,
            notif_type = 'submission',
            title      = f'پیام جدید از {request.user.get_full_name() or request.user.username}',
            message    = msg.content[:100],
            link       = f'/messages/{conv.pk}/',
        )

        return redirect('conversation_detail', pk=conv.pk)

    return render(request, 'messaging/detail.html', {
        'conversation': conv,
        'messages_list': conv.messages.all(),
        'form':         form,
        'other_user':   conv.get_other_user(request.user),
    })


@login_required
def start_conversation(request, user_pk):
    """شروع گفتگو با یه کاربر"""
    other = get_object_or_404(User, pk=user_pk)

    # نمی‌تونی با خودت گفتگو کنی
    if other == request.user:
        messages.error(request, 'نمی‌توانید با خودتان گفتگو کنید.')
        return redirect('conversation_list')

    # بررسی گفتگوی موجود
    existing = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=other
    ).first()

    if existing:
        return redirect('conversation_detail', pk=existing.pk)

    # گفتگوی جدید
    conv = Conversation.objects.create()
    conv.participants.add(request.user, other)
    conv.save()

    return redirect('conversation_detail', pk=conv.pk)


@login_required
def delete_message(request, pk):
    """حذف پیام — فقط فرستنده"""
    msg = get_object_or_404(Message, pk=pk, sender=request.user)
    conv_pk = msg.conversation.pk
    msg.delete()
    messages.success(request, 'پیام حذف شد.')
    return redirect('conversation_detail', pk=conv_pk)