from django.core.management.base import BaseCommand
from BAapp.utils.email_send import email_send

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        subject = "Test"
        to_email = input("Enter email(s): ")
        recipient = list(to_email.split(','))
        email_send(subject, recipient, "", "", {})