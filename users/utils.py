import phonenumbers
from rest_framework.exceptions import ValidationError
from twilio.rest import Client
import decouple

def check_phone_number(number):
    try:
        phone_number = phonenumbers.parse(number)
        return phonenumbers.is_valid_number(phone_number)
    except:
        raise ValidationError({
            'message':'Enter a valid phone number'
        })

# def check_phone_number_or_username(number):
#     try:
#         phone_number = phonenumbers.parse(number)
#         return phonenumbers.is_valid_number(phone_number)
#     except:
#         return False

def send_sms_verification_code(phone_number, code):
    account_sid = decouple.config('TWILIO_ACCOUNT_SID')
    auth_token = decouple.config('TWILIO_AUTH_TOKEN')
    from_user = decouple.config('FROM_USER_PHONE_NUMBER')
    client = Client(account_sid, auth_token)
    client.messages.create(
        body=f"Your verification code: {code}",
        from_= from_user,
        to = str(phone_number)
    )