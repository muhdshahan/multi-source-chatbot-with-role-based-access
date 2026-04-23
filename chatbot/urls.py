from django.urls import path
from .views import ChatAPIView, chat_ui, chat_history

urlpatterns = [
    path("chat/", ChatAPIView.as_view(), name="chat-api"),
    path("ui/", chat_ui, name="chat-ui"),
    path("history/", chat_history, name="chat-history"),
]