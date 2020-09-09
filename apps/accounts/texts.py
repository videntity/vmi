from django.conf import settings
import boto3
import logging
from twilio.rest import Client

logger = logging.getLogger('verifymyidentity_.%s' % __name__)


def send_text(message, number):
    if settings.SMS_STRATEGY == "AWS-SNS":
        sns = boto3.client('sns', region_name='us-east-1')
        number = "%s" % (number)
        sns.publish(
            PhoneNumber=number,
            Message=message,
            MessageAttributes={
                'AWS.SNS.SMS.SenderID': {
                    'DataType': 'String',
                    'StringValue': 'MySenderID'
                }
            }
        )

    elif settings.SMS_STRATEGY == "TWILIO":

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_TOKEN)
        tmsg = client.messages.create(to=str(number), from_=settings.TWILIO_FROM_NUMBER, body=message)
        logger.info("Message sent to %s by Twilio. %s" % (number, tmsg.sid))

    else:
        logger.error("Text Message not sent. No SMS_STRATEGY defined.")
