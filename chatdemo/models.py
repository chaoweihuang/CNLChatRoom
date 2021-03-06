from django.db import models
from django.contrib.auth.models import User
from channels_presence.models import Room
from django.utils import timezone
from django.urls import reverse


class ChatMessage(models.Model):
    """
    Model to represent user submitted changed to a resource guide
    """

    # Fields
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    message = models.TextField(max_length=3000)
    message_html = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        String to represent the message
        """

        return self.message


class NotificationCount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    count = models.IntegerField(default=5)


class BlackList(models.Model):
    """
    Model to represent black list
    """

    user = models.TextField(max_length=300)
    blacked_user = models.TextField(max_length=300)
