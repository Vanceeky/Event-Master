from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse, HttpResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import random
import string

# Create your views here.
''''
@login_required
def chat_view(request, chatroom_name = 'public-chat'):
    chat_group = get_object_or_404(ChatGroup, group_name = chatroom_name)





    chat_messages = chat_group.chat_messages.all()[:30]

    other_user = None

    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            raise Http404
        
        for member in chat_group.members.all():
            if member != request.user:
                other_user = member
                break


    if request.htmx:
        message = request.POST['message']
        message_ = GroupMessage.objects.create(group=chat_group, author=request.user, body=message)
        message_.save()

        context = {
            'message': message_,
            'user': request.user
        }
        return render(request, 'chat/chat_partials.html', context)
    


    context = {
    'chat_group': chat_group, 
    'chat_messages': chat_messages,
    'other_user': other_user,
    'chatroom_name': chatroom_name,
    }
    return render(request, 'chat/chat.html', context)

'''


@login_required
def inbox(request):
    user = request.user
    chat_groups = ChatGroup.objects.filter(is_private=True, members=user)

    groups_info = []
    for group in chat_groups:
        last_message = group.chat_messages.first()
        other_members = group.members.exclude(id=user.id)

        # Prepare to collect member info
        other_members_info = []
        for member in other_members:
            # Access the avatar safely and set default if necessary
            avatar_url = '/static/images/default-avatar.png'  # Default avatar
            if hasattr(member, 'customer') and member.customer.avatar:
                avatar_url = member.customer.avatar.url
            
            other_members_info.append({
                'username': member.username,
                'avatar': avatar_url,
                'first_name': member.first_name,
                'last_name': member.last_name,
            })

        # Prepare last message information
        if last_message:
            is_seen = last_message.is_seen
            
            if last_message.file:
                last_message_text = "You: Sent a file" if last_message.author == user else f"Sent a file"
            else:
                last_message_text = (
                    f"You: {last_message.body[:25]}..." if last_message.author == user 
                    else f"{last_message.body[:25]}..."
                ) if len(last_message.body) > 25 else last_message.body
            
            if not is_seen:
                last_message_text += " (New)"
        else:
            last_message_text = "No messages yet"

        groups_info.append({
            'group': group,
            'other_members': other_members_info,  # Member info including avatars
            'last_message': last_message_text,
            'last_message_is_seen': is_seen,
        })

    context = {
        'groups_info': groups_info,
    }
    return render(request, 'chat/inbox.html', context)


def get_chat_messages(request, group_id):
    group = get_object_or_404(ChatGroup, id=group_id)
    
 
    if request.user not in group.members.all():
        return JsonResponse({'error': 'You are not a member of this group.'}, status=403)
    

    messages = group.chat_messages.select_related('author').order_by('created_at')
    

    other_user = group.members.exclude(id=request.user.id).first()
    
    messages_data = []
    for message in messages:
        messages_data.append({
            'body': message.body,
            'author': message.author.username,
            'is_author': message.author == request.user,
            'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
    
    return JsonResponse({
        'messages': messages_data,
        'other_user': {
            'first_name': other_user.first_name,
            'last_name': other_user.last_name
        } if other_user else None
    })


@login_required
def chat_view(request, chatroom_name='public-chat'):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    chat_messages = chat_group.chat_messages.all()[:30]
    user = request.user
    other_user = None

    private_chat_groups = ChatGroup.objects.filter(is_private=True, members=request.user)
    groups_info = []

    for group in private_chat_groups:
        last_message = group.chat_messages.first() 

        is_last_message_seen = last_message.is_seen if last_message else True  

        other_members_info = []
        other_members = group.members.exclude(id=user.id)

        for member in other_members:
            avatar_url = '/static/images/default-avatar.png'  # Default avatar
            if hasattr(member, 'customer') and member.customer.avatar:
                avatar_url = member.customer.avatar.url
            
            other_members_info.append({
                'username': member.username,
                'first_name': member.first_name,
                'last_name': member.last_name,
                'avatar': avatar_url,
            })

        if last_message:
            if last_message.file:
                last_message_text = "You: Sent a file" if last_message.author == user else f"Sent a file"
            else:
                last_message_text = (
                    f"You: {last_message.body[:25]}..." if last_message.author == user 
                    else f"{last_message.body[:25]}..."
                ) if len(last_message.body) > 25 else last_message.body

            if not is_last_message_seen:
                last_message_text += " (New)"
        else:
            last_message_text = "No messages yet"

        groups_info.append({
            'group': group,
            'other_members': other_members_info,  # Updated to include member info
            'last_message': last_message_text,
            'last_message_is_seen': is_last_message_seen, 
        })

    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            raise Http404
        
        for member in chat_group.members.all():
            if member != request.user:
                other_user = member
                break

    if request.htmx:
        message = request.POST['message']
        message_ = GroupMessage.objects.create(group=chat_group, author=request.user, body=message)
        message_.save()

        context = {
            'message': message_,
            'user': request.user
        }
        return render(request, 'chat/chat_partials.html', context)
    
    context = {
        'chat_group': chat_group, 
        'chat_messages': chat_messages,
        'other_user': other_user,
        'chatroom_name': chatroom_name,
        'groups_info': groups_info,  # Include groups_info in context
    }
    return render(request, 'chat/chat.html', context)



def generate_random_chars(length=8):
    characters = string.ascii_letters + string.digits  # Exclude special characters
    return ''.join(random.choice(characters) for _ in range(length))



@login_required
def get_or_create_chatroom(request, username):
    if request.user.username == username:
        return redirect('chat')

    other_user = get_object_or_404(User, username=username)
    
    chatroom = ChatGroup.objects.filter(
        members=request.user
    ).filter(
        members=other_user,
        is_private=True
    ).first()

    if chatroom:
     
        return redirect('chatroom', chatroom.group_name)
    else:
       
        group_name = generate_random_chars() 
        chatroom = ChatGroup.objects.create(
            is_private=True,
            group_name=group_name
        )
        chatroom.members.add(other_user, request.user)
        chatroom.save()

        return redirect('chatroom', chatroom.group_name)




@login_required
def user_chat_groups(request):
    chat_groups = ChatGroup.objects.filter(members=request.user)
    data = []

    for group in chat_groups:
        # Get members excluding the current user
        members = group.members.exclude(id=request.user.id).values('first_name', 'last_name')
        members_list = [f"{member['first_name']} {member['last_name']}" for member in members]

        # Get the last message in the group
        last_message = group.chat_messages.last()
        if last_message:
            last_message_body = last_message.body
            if last_message.author == request.user:
                last_message_body = f"You: {last_message_body}"
        else:
            last_message_body = "No messages yet"

        data.append({
            "id": group.id,
            "group_name": group.group_name, 
            "members": members_list,
            "last_message": last_message_body,
        })

    return JsonResponse(data, safe=False)


@login_required
def fetch_group_messages(request, group_id):
    chat_group = get_object_or_404(ChatGroup, id=group_id)
    chat_messages = chat_group.chat_messages.all().order_by('created_at')
    
    messages_data = [
        {
            'author': message.author.username,
            'body': message.body,
            'created_at': message.created_at.isoformat(), 
        } for message in chat_messages
    ]
    
    return JsonResponse(messages_data, safe=False)


def chat_file_upload(request, chatroom_name):

    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)

    if request.htmx and request.FILES:
        file = request.FILES['file']

        message = GroupMessage.objects.create(
            file = file,
            author = request.user,
            group = chat_group
        )

        channel_layer = get_channel_layer()

        event = {
            'type': 'message_handler',
            'message_id': message.id,
        }

        async_to_sync(channel_layer.group_send)(
            chatroom_name, event

        )

    return HttpResponse()



