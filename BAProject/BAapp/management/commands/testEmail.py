from django.core.management.base import BaseCommand
from django.conf import settings
from BAapp.utils.email_send import email_send

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        try:
            subject = "Test"
            message = "Testeando mailing"
            # from_email = f'"Buenaventura Agronegocios" <{settings.DEFAULT_FROM_EMAIL}>'
            to_email = input("Enter email: ")
            recipient = to_email.split(',')
            email_send(subject, recipient, "", "", {})
        except Exception as e:
            print(e)