from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .forms import RegisterForm, ProfileForm
from django.contrib.auth import views, authenticate, login, get_user_model
from django.contrib import messages
from django.urls import reverse
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core import exceptions
from django.views import generic
from channels_presence.models import Room
from webpush import send_group_notification, send_user_notification
from .models import ChatMessage
from .models import NotificationCount


class IndexView(generic.View):

    def get(self, request):
        # We want to show the last 10 messages, ordered most-recent-last
        try:
            room = Room.objects.get(channel_name='all')
            chat_queryset = ChatMessage.objects.filter(room=room).order_by("-created")[:10]
        except:
            chat_queryset = ChatMessage.objects.order_by("-created")[:10]

        chat_message_count = len(chat_queryset)
        if chat_message_count > 0:
            first_message_id = chat_queryset[len(chat_queryset)-1].id
        else:
            first_message_id = -1
        previous_id = -1
        if first_message_id != -1:
            try:
                previous_id = ChatMessage.objects.filter(
                    pk__lt=first_message_id).order_by("-pk")[:1][0].id
            except IndexError:
                previous_id = -1
        chat_messages = reversed(chat_queryset)

        if request.user.is_authenticated:
            try:
                count = (NotificationCount.objects.get(user=request.user)).count
            except:
                nc = NotificationCount.objects.create(user=request.user)
                count = nc.count
        else:
            count = 0

        return render(request, "chatdemo/chatroom.html", {
            'chat_messages': chat_messages,
            'first_message_id': previous_id,
            'notification_count' : count,
        })


class LogoutView(LoginRequiredMixin, View):

    def get(self, request):
        template_response = views.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect(reverse('chatdemo:login'))


class RegisterView(View):
    form_class = RegisterForm
    template_name = 'registration/register.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_username = form.cleaned_data['username']
            new_password = form.cleaned_data['password']
            new_email = form.cleaned_data['email']

            if get_user_model().objects.filter(username=new_username).exists():
                messages.error(
                    request, "Username not available, choose a different one")
                return render(request, self.template_name, {'form': form})
            if (new_email != '' and
                    get_user_model().objects.filter(email=new_email).exists()):
                messages.error(
                    request, "Email not available, choose a different one")
                return render(request, self.template_name, {'form': form})

            # validate password
            try:
                # validate_password(new_password)
                pass
            except exceptions.ValidationError as e:
                form.errors['password'] = list(e.messages)
                return render(request, self.template_name, {'form': form})

            user = get_user_model().objects.create_user(
                username=new_username, password=new_password, email=new_email)
            user = authenticate(username=new_username, password=new_password)

            n = NotificationCount.objects.create(user=user)

            if user is not None:
                login(request, user)
                return redirect(reverse('chatdemo:profile'))

        else:
            return render(request, self.template_name, {'form': form})


class ProfileView(LoginRequiredMixin, View):
    login_url = '/user/login/'
    form_class = ProfileForm
    template_name = 'registration/profile.html'

    def get(self, request, *args, **kwargs):
        data = {}
        if request.user.email != '':
            data['email'] = request.user.email
        form = self.form_class(initial=data)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST,
                               initial={'email': request.user.email})
        if form.is_valid():
            if form.has_changed():
                user = request.user

                for field in form.changed_data:
                    if field == 'email':
                        if form.cleaned_data[field] != '' and User.objects.filter(email=form.cleaned_data[field]).exclude(id=user.id).exists():
                            messages.error(
                                request, "Email address is already in use")
                            return redirect(reverse('chatdemo:profile'))
                    setattr(user, field, form.cleaned_data[field])
                user.save()
                messages.success(request, "Profile has been updated")
                return redirect(reverse('chatdemo:profile'))
            else:
                messages.info(request, "Data has not been changed")
                return redirect(reverse('chatdemo:profile'))
        else:
            messages.error(request, "Invalid form data")
            return redirect(reverse('chatdemo:profile'))


def push_notification(request):
    if 'notification' in request.GET:
        payload = {"head": request.user.username, "body": request.GET['notification']}
    else:
        payload = {"head": request.user.username, "body": "有東西出錯了"}

    notification_count = NotificationCount.objects.get(user=request.user)
    if int(notification_count.count) > 0:
        notification_count.count = int(notification_count.count) - 1
        notification_count.save()

        send_group_notification(group_name='all', payload=payload, ttl=1000)
        return redirect(reverse('chatdemo:home_page'))
    else:
        payload = {"head": "Error", "body": "尬廣次數不足"}
        send_user_notification(user=request.user, payload=payload, ttl=1000)
        return redirect(reverse('chatdemo:home_page'))


def buy_notification(request):
    buy_count = int(request.GET['count'])
    print('buy_count')
    print(buy_count)
    notification_count = NotificationCount.objects.get(user=request.user)
    notification_count.count = int(notification_count.count) + buy_count
    notification_count.save()

    payload = {"head": "購買成功", "body": "已購買" + str(buy_count) + "次廣播"}
    send_user_notification(user=request.user, payload=payload, ttl=1000)
    return redirect(reverse('chatdemo:home_page'))
