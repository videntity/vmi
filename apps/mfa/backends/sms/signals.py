import boto3
from django.db.models.signals import post_save
from django.conf import settings

def send_sms_code(sender, instance, created, **kwargs):
    sns = boto3.client('sns')
    number = instance.device.phone_number
    sns.publish(
        PhoneNumber=number,
        Message="Your code for %s is : %s" % (settings.ORGANIZATION_NAME, instance.code),
        MessageAttributes={
            'AWS.SNS.SMS.SenderID': {
                'DataType': 'String',
                'StringValue': 'MySenderID'
            }
        }
    )


post_save.connect(send_sms_code, sender='sms.SMSCode')
