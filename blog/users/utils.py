import jwt
from jwt import DecodeError, ExpiredSignatureError

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode

from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


def send_email_for_verification(user_id, receiver, current_site, mail_subject, email_template):
    user = User.objects.get(id=user_id)
    token = RefreshToken.for_user(user).access_token
    message = render_to_string(email_template, {'domain': current_site, 'token': token})
    email = EmailMessage(mail_subject, message, 'serg@gmail.com', to=[receiver])
    email.content_subtype = 'html'
    email.send()


def send_email_for_reset_password(user_id, receiver, current_site, mail_subject, email_template):
    user = User.objects.get(id=user_id)
    uidb64 = urlsafe_base64_encode(smart_bytes(user.pk))
    token = PasswordResetTokenGenerator().make_token(user)
    message = render_to_string(email_template, {'domain': current_site, 'user': user, 'token': token, 'uid': uidb64})
    email = EmailMessage(mail_subject, message, 'serg@gmail.com', to=[receiver])
    email.content_subtype = 'html'
    email.send()


def activate_user(token):
    try:
        token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = token.get('user_id')
        user = User.objects.get(id=user_id)
        if not user.is_verified:
            user.is_verified = True
            user.save()
            return Response({'detail': 'Thank you for your email confirmation.'}, status=status.HTTP_200_OK)
        return Response({'detail': 'Your email is verified.'}, status=status.HTTP_400_BAD_REQUEST)
    except ExpiredSignatureError:
        return Response({'detail': 'Activation link is expired'}, status=status.HTTP_400_BAD_REQUEST)
    except DecodeError:
        return Response({'detail': 'The token is invalid'}, status=status.HTTP_400_BAD_REQUEST)
