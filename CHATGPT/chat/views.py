from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
import json
import logging
from .models import Interaction, ChatSession, Message
import google.generativeai as genai
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .renderers import UserRenderer
from icecream import ic
from rest_framework_simplejwt.tokens import RefreshToken

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Google Generative AI
genai.configure(api_key="AIzaSyDb1VLrY9x-DaO9kZAN6pky3pJz7Jxd26k")
g_model = genai.GenerativeModel("gemini-1.5-pro-exp-0801")
Chat = g_model.start_chat(history=[])


def get_gemini_response(user_input, context):
    try:
        full_query = f"{user_input} {context}" if context else user_input
        response = g_model.generate_content(full_query)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"


def chatPage(request):
    return render(request, "chat.html")


class ChatView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        chatPage()

    def post(self, request):
        try:
            data = json.loads(request.body)
            ic(data)
            # TODO in the below line i need to fetch the id of user
            user_id = request.user.id
            print(user_id)
            user_input = data.get("input", "")
            session_id = data.get("chat_session_id", None)
            print(session_id)
            if not user_input:
                return JsonResponse({"error": "No input provided"}, status=400)

            if session_id:
                ic(session_id)
                chat_session = ChatSession.objects.get(id=session_id, user_id=user_id)
                print(chat_session)
            else:
                return JsonResponse({"error": "No session ID provided"}, status=400)

            previous_messages = Message.objects.filter(
                chat_session=chat_session
            ).order_by("timestamp")
            history = [
                {"role": "user" if msg.sender == "user" else "model", "text": msg.text}
                for msg in previous_messages
            ]

            response = Chat.send_message(user_input, stream=True)
            print("response has been taken")
            logger.info("resolving response...")
            response.resolve()
            logger.info("Response resolved.")
            response_text = response.text

            Message.objects.create(
                chat_session=chat_session, sender="user", text=user_input
            )
            Message.objects.create(
                chat_session=chat_session, sender="bot", text=response_text
            )

            Interaction.objects.create(
                user_id=user_id, user_input=user_input, response=response_text
            )
            ic(response_text)
            return JsonResponse({"response": response_text})
        except Exception as e:
            logger.error(f"Error in chat view: {str(e)}")

            return JsonResponse({"error": str(e)}, status=500)


def welcome(request):
    return render(request, "welcome.html")


class ChatSessionsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):  # done
        data = json.loads(request.body)
        ic(data)
        session_name = data.get("session_name")
        chat_session = ChatSession.objects.create(name=session_name, user=request.user)
        return JsonResponse({"chat_session_id": chat_session.id}, status=201)

    def delete(self, request):  # done
        data = json.loads(request.body)
        session_id = data.get("session_id")
        ic(session_id)
        ChatSession.objects.filter(id=session_id).delete()
        return JsonResponse({"status": "deleted"})

    def get(self, request):  # not done
        sessions = ChatSession.objects.all().values("id", "name", "user")
        return JsonResponse({"sessions": list(sessions)})


class personalChatSessions(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):  # done
        print(request.user.id)
        sessions = ChatSession.objects.filter(user_id=request.user.id).values(
            "id", "name", "user"
        )

        # sessions = ChatSession.objects.all().values("id", "name", "user")
        return JsonResponse({"sessions": list(sessions)})


# def create_chat_session(request):
#     if request.method == "POST":


def get_chat_messages(request, session_id):
    try:
        messages = Message.objects.filter(chat_session=session_id).values(
            "sender", "text"
        )
        return JsonResponse(list(messages), safe=False)
    except Exception as e:
        logger.error(f"Error in get_chat_messages view: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def save_message(request, chat_session_id):
    chat_session = get_object_or_404(ChatSession, id=chat_session_id, user=request.user)
    if request.method == "POST":
        data = json.loads(request.body)
        sender = data["sender"]
        text = data["text"]
        Message.objects.create(chat_session=chat_session, sender=sender, text=text)
        return JsonResponse({"status": "Message saved"})
    return JsonResponse({"error": "Invalid request method"}, status=405)


# @csrf_exempt
# def delete_chat_session(request, session_id):

#     if request.method == "DELETE":


def get_tokens(
    user,
) -> dict:  # this is the method for getting  tokens for a user to autherize
    refresh = RefreshToken.for_user(
        user
    )  # this built in will provide us both access and refresh token
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }  # got both the tokens


class UserRegistrationView(APIView):  # done
    def get(self, request):
        return Response({"user": User.objects.get(pk=request.data.get("id")).username})

    # this code will be executed when we hit the url with the get request
    # and it will provide us the id in the body of the request
    # if the user with that id is found then it will return the username else it will raise a exception
    # it can be done by just checking if the user is none

    def post(self, request):
        serializer = UserRegistrationSerializers(data=request.data)
        print(serializer)
        if serializer.is_valid():
            # checking if the serializer is valid or not
            # it is being checked by the validate method in the serializer we are using
            user = (
                serializer.save()
            )  # it will save and return the user created by the serialized data
            return Response(
                {
                    "msg": "regestrationsucessfull",
                    "data": serializer.data,  # here we are getting the data from the serializer which it is holding
                    "tokens": get_tokens(user),
                    # here we are using the method we created at the top for getting  the access and refresh token for the user
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {"msg": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )  # if any exception occurs it will show the exception to us by the this but in json format so it doesnt break the flow of the code

    # this post reuest will be hit when we hit the api with a post request
    # this is used while registering a new user


class UserLoginView(APIView):  # done
    renderer_classes = [UserRenderer]
    # these render  classes provide us the format to show the exception in the json of the api

    def post(self, request):  # this is login post reuest api
        serializer = UserLoginSerializer(data=request.data)
        # using the custom defined serializer by sending it the data(body and headers) of the request
        if serializer.is_valid():
            # checking if the data provided by the request is valid or not by the validate method defined in the serializers
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]

            # these are the data we are getting after validating it
            user = authenticate(username=username, password=password)
            # normally authenticating the user by the authenticate method
            if user is not None:
                return Response(
                    {"message": "Login Successfull", "tokens": get_tokens(user)},
                    status=status.HTTP_200_OK,
                )
            # if the user is not none then we are gettings its token and adding it to our response
            else:
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # here this will be used when there is a credential fault
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # return Response({"msg":"either the password or username is incorrect","errorss":""},status=status.HTTP_404_NOT_FOUND)
