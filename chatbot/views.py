from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from chatbot.services.chat_service import ChatService
from .models import ChatMessage


class ChatAPIView(APIView):
    """API endpoint for handling chatbot queries."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Handle user query and return chatbot response."""
        query = request.data.get("query")

        if not query:
            return Response({"error": "Query is required"}, status = 400)

        chat_service = ChatService()
        response = chat_service.handle_query(request.user, query)

        # Save chat history
        ChatMessage.objects.create(
            user=request.user,
            query=query,
            response=response
        )

        return Response({
            "query": query,
            "response": response
        })
    
@login_required(login_url='/login/')
def chat_ui(request):
    """Render chatbot UI page."""
    return render(request, "chat.html")

@login_required
def chat_history(request):
    """Render user's chat history."""
    chats = ChatMessage.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "history.html", {"chats": chats})