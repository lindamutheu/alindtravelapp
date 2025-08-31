import requests
from django.conf import settings

def initiate_chapa_payment(payment, callback_url):
    url = f"{settings.CHAPA_BASE_URL}/transaction/initialize"
    headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}

    payload = {
        "amount": str(payment.amount),
        "currency": payment.currency,
        "email": payment.user.email,
        "first_name": payment.user.first_name,
        "last_name": payment.user.last_name,
        "tx_ref": payment.chapa_tx_ref,
        "callback_url": callback_url,
        "return_url": f"https://yourdomain.com/payment/success/{payment.id}/",
        "customization": {
            "title": "Booking Payment",
            "description": f"Payment for booking {payment.booking.id}"
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()


def verify_chapa_payment(tx_ref):
    url = f"{settings.CHAPA_BASE_URL}/transaction/verify/{tx_ref}"
    headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}

    response = requests.get(url, headers=headers)
    return response.json()
