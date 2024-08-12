from rest_framework import serializers
from django.contrib.auth.models import User


class UserRegistrationSerializers(serializers.ModelSerializer):
    # we are writing this code because we need to confirm trhe password field in our regestration request
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    # these are the fields need while registering the user
    class Meta:
        model = User
        # defining the model for the serializer
        fields = [
            "username",
            "password",
        ]
        # these are the fields which will be displayed in the serialized data

        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        # if attrs.get("password")!=attrs.get("password1"):
        #     raise serializers.ValidationError('both the paswords doesnt match')

        return attrs
        # this validate function is used of checkin a condition needed while creating a new user
        # the condition  can be like the age of the user must be more than 0

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data.get("username"),
            # email=validated_data.get("email")
        )
        user.set_password(validated_data.get("password"))
        user.save()
        return user

    # this method is used when we are creating the new user


class UserLoginSerializer(serializers.ModelSerializer):

    # def validate(self,attrs):
    #     return attrs
    username = serializers.CharField()  # defines incoming data will be string
    password = serializers.CharField(style={"input_type": "password"})

    # these fields(username and password) are the fields which must be in the request body
    class Meta:
        model = User
        # defining the model for the serializer
        fields = ["username", "password"]
        # fields to display
