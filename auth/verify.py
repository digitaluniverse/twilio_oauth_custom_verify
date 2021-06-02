from twilio.rest import Client
from django.conf import settings

client = Client(settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN)


def verifications(user_destination, via):


    return client.verify \
        .services(settings.TWILIO_VERIFICATION_SID) \
        .verifications \
        .create(
            to=user_destination,
            channel=via,
            channel_configuration={
                'channel': via,
                'substitutions': {
                    'email': user_destination
                }
            }
        )


def verification_checks(user_destination, token):
    return client.verify \
        .services(settings.TWILIO_VERIFICATION_SID) \
        .verification_checks \
        .create(to=user_destination, code=token)