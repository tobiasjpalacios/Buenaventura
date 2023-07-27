from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
import requests

# NOTE: comentado 
# def email_send(
#         subject_email : str, 
#         to_email : list, 
#         path_to_text : str, 
#         path_to_html : str, 
#         context : dict
#     ):
#     res = 1
#     try:
#         subject = subject_email
#         from_email = f'"Buenaventura Agronegocios" <{settings.DEFAULT_FROM_EMAIL}>'
#         to = to_email
#         text_content = get_template(path_to_text).render(context)
#         html_content = get_template(path_to_html).render(context)
#         msg = EmailMultiAlternatives(subject, text_content, from_email, to)
#         msg.attach_alternative(html_content, "text/html")
#         msg.send()
#     except Exception as e:
#         res = e

#     return res

def email_send(
        subject_email : str, 
        to_email : list, 
        path_to_text : str, 
        path_to_html : str, 
        context : dict
    ):
    try:
        subject = subject_email
        to = ', '.join(to_email)
        html_content = get_template(path_to_html).render(context) if path_to_html else "<h1>TESTING BVAGRO MAILING</h1>"

        payload = {
            'service_id': settings.EMAILJS_SERVICE_ID,
            'template_id': settings.EMAILJS_TEMPLATE_ID,
            'user_id': settings.EMAILJS_USER_ID,
            'accessToken': settings.EMAILJS_API_KEY,
            'template_params': {
                'subject': subject,
                'email': to,
                'html_content': html_content
            }
        }

        response = requests.post('https://api.emailjs.com/api/v1.0/email/send', json=payload)
        response.raise_for_status()
        print('Email sent successfully')
    except requests.exceptions.RequestException as e:
        print('Failed to send email:', str(e))
