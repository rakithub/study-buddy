from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Room, Topic, Message, User
from .forms import RoomForm, MessageForm, UserForm, MyUserCreationForm


def login_page(request):
    if request.user.is_authenticated:
        return redirect('base:home')
    
    page = 'login'

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        # try:
        #     user = User.objects.get(username=username)
        # except:
        #     messages.error(request, "The user does not exist.")
        
        user =  authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return redirect('base:home')
        else:
            messages.error(request, "Email and password does not match.")

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logout_user(request):
    logout(request)
    return redirect('base:home')


def register_page(request):
    page = 'register'
    if request.method != 'POST':
        form = MyUserCreationForm()
    else:
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('base:home')
        else:
            messages.error(request, 'An error occurred during registration.')

    context = {'page': page, 'form': form}
    return render(request, 'base/login_register.html', context)


def home(request):
    from urllib.parse import unquote
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    if room_messages.count() > 5:
        recent_messages = room_messages[:5]
    else:
        recent_messages = room_messages

    if Topic.objects.count() > 5:
        topics = Topic.objects.all()[:5]
    else:
        topics = Topic.objects.all()

    context = {"rooms": rooms, "topics": topics, 'room_count': room_count, 'recent_messages': recent_messages}
    return render(request, "base/home.html", context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all().order_by('username')
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('base:room', room.id)

    context = {"room": room, "room_messages": room_messages, 'participants': participants}
    return render(request, "base/room.html", context)


def user_profile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    recent_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms, 
               'recent_messages': recent_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url='base:login')
def create_room(request):
    form_state = 'create'
    topics = Topic.objects.all()
    form = RoomForm()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room_name = request.POST.get('name')
        room_description = request.POST.get('description')
        if room_name and form.is_valid:
            room = Room.objects.create(
                name=room_name,
                host=request.user,
                description=room_description,
                topic=topic
            )
            return redirect('base:home')
        else:
            messages.error(request, "Please fill out room name.")
        
    context = {'form': form, 'topics': topics, 'form_state': form_state}
    return render(request, "base/room_form.html", context)


@login_required(login_url='base:login')
def update_room(request, pk):
    form_state = 'update'
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse("You're not allowed here.")
    if request.method != 'POST':
        topics = Topic.objects.all()
        form = RoomForm(instance=room)
    else:
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.topic = topic
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        if room.name:
            room.save()
            return redirect('base:home')
        else:
            messages.error(request, "Please fill out room name.")

    context = {'form': form, 'form_state': form_state, 
               'room_topic': room.topic, 'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='base:login')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse("You're not allowed here.")
    if request.method == 'POST':
        room.delete()
        return redirect('base:home')

    return render(request, 'base/delete.html', {"obj": room})


@login_required(login_url='base:login')
def delete_message(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse("You're not allowed here.")
    if request.method == 'POST':
        room = message.room
        message.delete()
        return redirect('base:room', room.id)

    return render(request, 'base/delete.html', {"obj": message})


@login_required(login_url='base:login')
def edit_message(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse("You're not allowed here.")
    
    form = MessageForm(instance=message)
    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message)
        if form.is_valid():
            room = message.room
            form.save()
            return redirect('base:room', room.id)
        
    context = {"form": form, "message": message}
    return render(request, 'base/edit_message.html', context)


def update_user(request, pk):
    form = UserForm(instance=request.user)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('base:user_profile', pk=request.user.id)
        
    return render(request, 'base/update_user.html', {'form': form})


def topics(request):
    q = request.GET.get('q') if request.GET.get('q') else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})


def activities(request):
    room_messages = Message.objects.all()
    if room_messages.count() > 5:
        recent_messages = room_messages[:5]
    else:
        recent_messages = room_messages 
    return render(request, 'base/activities.html', {'recent_messages': recent_messages})