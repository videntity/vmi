from django.conf import settings
import boto3


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
    if settings.SMS_STRATEGY == "MS-AZURE":
        # To DO : Add code to send text message SNS
        pass
