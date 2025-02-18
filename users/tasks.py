import logging
from celery import shared_task
from celery.exceptions import Retry
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 5})
def send_verification_email(email, code, action):
    subject = '脑洞制造邮箱验证'
    html_message = render_to_string('email/verification_email.html', {
        'code': code,
        'email': email,
        'action': action,
    })
    plain_message = strip_tags(html_message)
    from_email = '1549971272@qq.com'
    recipient_list = [email]
    try:
        send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)
        logger.info(f"Verification email successfully sent to {email} with code {code}（{action}）.")
        return True
    except Exception as e:
        # 记录日志或进行其他处理
        logger.error(f"Failed to send verification email to {email}: {str(e)}")
        raise Retry(exc=e)
