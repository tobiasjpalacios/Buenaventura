from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        try:
            subject = "Test"
            message = "Testeando mailing"
            from_email = f'"Buenaventura Agronegocios" <{settings.DEFAULT_FROM_EMAIL}>'
            to_email = input("Email: ")
            recipient = [to_email]
            send_mail(subject, message, from_email, recipient)
        except Exception as e:
            print(e)