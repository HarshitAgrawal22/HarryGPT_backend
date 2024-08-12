from django.contrib import admin
from .models import *
from django.contrib.auth.models import User

# admin.site.register(ChatSession)
# admin.site.register(Message)
# admin.site.register(Interaction)s
# Register your models here.


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["chat_session", "sender", "text", "timestamp"]


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "user", "created_at"]


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ["user", "user_input", "response", "timestamp"]
