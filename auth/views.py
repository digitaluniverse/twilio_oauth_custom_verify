from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import models, serializers
from .verify import verifications,verification_checks
from drf_social_oauth2.views import TokenView
from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from oauth2_provider.signals import app_authorized
import json
from oauth2_provider.models import get_access_token_model, get_application_model, get_refresh_token_model
from rest_framework.permissions import IsAuthenticated, IsAdminUser




# Create your views here.
class verifyNumber(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = serializers.UserSerializer(user, many=False)
        data = request.data
        number = data['number']

        if (not user.phone_verified and user.number != number):
            verifications(number, 'sms')
            user.number = number
            user.save()
            response = Response(
                data={str("Sending Verification code")}, status=status.HTTP_200_OK)
        elif not user.phone_verified:
            verifications(number, 'sms')
            response = Response(
                data={str("Sending Verification code")}, status=status.HTTP_200_OK)
        else:
            response = Response(data={"error": str(
                "Phone Number is already Verified")}, status=status.HTTP_400_BAD_REQUEST)
        return response


class confirmPhone(APIView):
    def get(self, request):
        data = request.data
        number = data['number']
        code = data['code']
        try:
            valid = verification_checks(number, code).valid
            print(valid)
            if not valid:
                return Response(
                    data={"error": "Not Valid Try Again"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                user = models.CustomUser.objects.get(number=number)
                user.phone_verified = valid
                user.save()
                return Response(
                    data={"verified": number}, status=status.HTTP_200_OK)
            except Exception as error:
                return Response(
                    data={"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response(
                data={"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)


class verifyEmail(APIView):
    def put(self, request):
        data = request.data
        email = data['email']
        try:
            verifications(email, 'email')
            return Response(data={str("Sending Verification code")}, status=status.HTTP_200_OK)
        except Exception as error:
            return Response(data={"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

class confirmEmail(APIView):
    def get(self, request):
        data = request.data
        email = data['email']
        code = data['code']
        try:
            valid = verification_checks(email, code).valid
            print(valid)
            if not valid:
                # verifications(email, 'email')
                return Response(
                    data={"error": "Not Valid Try Again"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                user = models.CustomUser.objects.get(email=email)
                user.email_verified = valid
                user.save()
                return Response(
                    data={"verified": email}, status=status.HTTP_200_OK)
            except Exception as error:
                return Response(
                    data={"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response(
                data={"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)



class register(APIView):
    def post(self, request):
        data = request.data
        print(data['email'])
        serializer = serializers.RegisterSerializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            user = models.CustomUser.objects.create(
                username=data['email'],
                email=data['email'],
                password=make_password(data['password'])
            )
            return Response(data={"Account Created Successfully Sending Verification code to: "+str(user.email)}, status=status.HTTP_200_OK)
        except ValidationError:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class login(TokenView):
    def post(self, request, *args, **kwargs):
        # Use the rest framework `.data` to fake the post body of the django request.
        mutable_data = request.data.copy()
        request._request.POST = request._request.POST.copy()
        for key, value in mutable_data.items():
            request._request.POST[key] = value
        url, headers, body, status = self.create_token_response(
            request._request)
        if status == 200:
            body = json.loads(body)
            access_token = body.get("access_token")
            if access_token is not None:
                token = get_access_token_model().objects.get(
                    token=access_token)
                app_authorized.send(
                    sender=self, request=request,
                    token=token)
                if not token.user.email_verified:
                    return Response({"error": "Email must be Verified before Login"},
                                    status=status.HTTP_400_BAD_REQUEST)
                user_data = serializers.UserSerializer(token.user).data
                body.update(user_data)
                body = json.dumps(body)
        response = Response(data=json.loads(body), status=status)

        for k, v in headers.items():
            response[k] = v
        return response