from django.core.mail import send_mail
from django.conf import settings
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
import re

def send_simple_email(user_email, code):
    subject = 'Tasdiqlash kodingiz!'
    message = f'Tasdiqlash kodingiz: {code}'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email,]
    
    send_mail(subject, message, from_email, recipient_list)
    return True

email_regex = re.compile(r'^[\w\.-]+@([\w-]+\.)+[\w-]{2,4}$')

def check_email(email):
    if re.fullmatch(email_regex, email):
        return email
    else:
        raise ValidationError('Email xato kiritildi')
    