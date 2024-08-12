from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.welcome, name="welcome"),  #
    #
    #
    #
    #
    #
    path("chat/", views.ChatView.as_view(), name="chat"),
    #
    #
    #
    #
    #
    # path('chat_history/', views.chat_history, name='chat_history'),
    path("login/", views.UserLoginView.as_view(), name="login"),
    #
    #
    #
    #
    #
    path("register/", views.UserRegistrationView.as_view(), name="register"),
    #
    #
    #
    #
    #
    path(
        "chat_session/",
        views.ChatSessionsView.as_view(),
        name="create_chat_session",
    ),
    #
    #
    #
    #
    #
    path(
        "get_chat_messages/<int:session_id>/",
        views.get_chat_messages,
        name="get_chat_messages",
    ),
    #
    #
    #
    #
    #
    path(
        "save_message/<int:chat_session_id>/", views.save_message, name="save_message"
    ),
    #
    #
    #
    #
    #
    # path(
    #     "delete_chat_session/<int:session_id>/",
    #     views.delete_chat_session,
    #     name="delete_chat_session",
    # ),
    path("list_personal_chats/", views.personalChatSessions.as_view()),
]
