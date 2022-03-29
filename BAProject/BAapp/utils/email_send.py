from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from smtplib import SMTPException
from django.http import HttpResponse

def email_send(subject_email, to_email, path_to_text, path_to_html, context):
    res = None
    try:
        subject = subject_email
        from_email = f'"Buenaventura Agronegocios" <{settings.DEFAULT_FROM_EMAIL}>'
        to = to_email
        text_content = get_template(path_to_text).render(context)
        html_content = get_template(path_to_html).render(context)
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except Exception as e:
        res = e

    res = 1

    return res