import boto3
from django.db.models.signals import post_save
from django.conf import settings
from twilio.rest import Client
import logging

logger = logging.getLogger('verifymyidentity_.%s' % __name__)


def send_sms_code(sender, instance, created, **kwargs):

    number = instance.device.phone_number
    if settings.SMS_STRATEGY == "AWS-SNS":
        sns = boto3.client('sns')
        sns.publish(
            PhoneNumber=number,
            Message="Your code for %s is : %s" % (
                settings.ORGANIZATION_NAME, instance.code),
            MessageAttributes={
                'AWS.SNS.SMS.SenderID': {
                    'DataType': 'String',
                    'StringValue': 'MySenderID'
                }
            }
        )
        logger.info("Message sent to %s by AWS SNS." % (number))
    if settings.SMS_STRATEGY == "TWILIO":
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_TOKEN)
        message = client.messages.create(to=number, from_=settings.TWILIO_FROM_NUMBER,
                                         body="Your code for %s is : %s" % (settings.ORGANIZATION_NAME, instance.code))
        logger.info("Message sent to %s by Twilio. %s" % (number, message.sid))


post_save.connect(send_sms_code, sender='sms.SMSCode')
