from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

def email_send(
        subject_email : str, 
        to_email : list, 
        path_to_text : str, 
        path_to_html : str, 
        context : dict
    ):
    res = 1
    try:
        subject = subject_email
        from_email = f'"Buenaventura Agronegocios" <{settings.DEFAULT_FROM_EMAIL}>'
        to = to_email
        text_content = get_template(path_to_text).render(context)
        html_content = get_template(path_to_html).render(context)
        # borrar despues
        with open('dump.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except Exception as e:
        res = e

    return res