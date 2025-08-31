from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_payment_confirmation_email(user_email, booking_id):
    send_mail(
        "Booking Payment Confirmation",
        f"Your payment for booking {booking_id} was successful!",
        "lindamutheu5@gmail.com",
        [user_email],
        fail_silently=False,
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,  # must be set in settings.py
        [user_email],
        fail_silently=False,
    )
    return f"Booking confirmation email sent to {user_email}"
