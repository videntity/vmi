from django.core.management.base import BaseCommand
import sys
import json
from collections import OrderedDict
from signal import signal, SIGINT
from ...models import IDCardConfirmation, random_number, Organization
from ...texts import send_text
import pyttsx3
from django.conf import settings


def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    sys.exit(0)


def parse_realid(binary_input):
    """Accepts a binary string containing the DL that begins with b'ANSI' """
    response = OrderedDict()
    split_items = binary_input.split(b'\x1b')
    for s in split_items:
        s = s.lstrip(b'[B')
        # Document Discr
        if s.startswith(b'DCF'):
            response['document_discriminator'] = s.split(b'DCF')[
                1].decode('ascii')
        # Inventory_control
        if s.startswith(b'DCK'):
            response['inventory_control_number'] = s.split(b'DCK')[
                1].decode('ascii')

        # date_issued DBD
        if s.startswith(b'DBD'):
            response['date_issued'] = s.split(b'DBD')[1].decode('ascii')
            response['date_issued_standardized'] = "%s-%s-%s" % (response['date_issued'][4:8],
                                                                 response[
                                                                     'date_issued'][0:2],
                                                                 response['date_issued'][2:4])

        # date_expires DBA
        if s.startswith(b'DBA'):
            response['date_expires'] = s.split(b'DBA')[1].decode('ascii')
            response['date_expires_standardized'] = "%s-%s-%s" % (response['date_expires'][4:8],
                                                                  response[
                                                                      'date_expires'][0:2],
                                                                  response['date_expires'][2:4])
        # Compliance Type
        if s.startswith(b'DDA'):
            response['compliance_type'] = s.split(b'DDA')[1].decode('ascii')

        # Name
        if s.startswith(b'DAC'):
            response['first_name'] = s.split(b'DAC')[1].decode('ascii')
        if s.startswith(b'DCT'):
            response['first_and_middle'] = s.split(b'DCT')[1].decode('ascii')
        if s.startswith(b'DAD'):
            response['middle_name'] = s.split(b'DAD')[1].decode('ascii')
        if s.startswith(b'DCS'):
            response['last_name'] = s.split(b'DCS')[1].decode('ascii')

        # DoB
        if s.startswith(b'DBB'):
            response['birthdate'] = s.split(b'DBB')[1].decode('ascii')
            response['birthdate_standardized'] = "%s-%s-%s" % (response['birthdate'][4:8],
                                                               response[
                                                                   'birthdate'][0:2],
                                                               response['birthdate'][2:4])

        # Sex
        if s.startswith(b'DBC'):
            response['sex'] = s.split(b'DBC')[1].decode('ascii')
            if response['sex'] == '1':
                response['sex_standardized'] = "male"
            elif response['sex'] == '2':
                response['sex_standardized'] = "female"
            else:
                response['sex_standardized'] = "undefined"

        # Address DAG

        if s.startswith(b'DAG'):
            response['address'] = s.split(b'DAG')[1].decode('ascii')
        # City DAI
        if s.startswith(b'DAI'):
            response['city'] = s.split(b'DAI')[1].decode('ascii')
        # State or region DAJ
        if s.startswith(b'DAJ'):
            response['state'] = s.split(b'DAJ')[1].decode('ascii')

        # Postal code DAK
        if s.startswith(b'DAK'):
            response['postal_code'] = s.split(b'DAK')[1].decode('ascii')

    #shimcode to return first name, when non-RealID.
    if 'first_name' not in response.keys() and 'first_and_middle' in response.keys():
        response['first_name'] = response['first_and_middle'].split(' ')[0]

    return response


class Command(BaseCommand):
   
    help = 'Register a Us with a RealID or similar AAMVA ID PDF417 barcode.'
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('organization_slug', nargs='?', default="acme-health")
        parser.add_argument('username', nargs='?', default="alan")


    def handle(self, *args, **options):
        
        # Load the talking lib.
        engine = pyttsx3.init();

        # This responds to control-c gracefully
        signal(SIGINT, handler)
        try:
            org = Organization.objects.get(slug=options['organization_slug'])
        except Organization.DoesNotExist:
            print('The organization specified does not exist.')
            pyttsx3.speak("The organization specified does not exist.")
            sys.exit(1)
        msg = 'Running RealID enrollment for the organization %s. The agent controlling this kiosk has the username %s.' % (org.name,options['username'])
        print(msg)
        pyttsx3.speak(msg)
        
        
        msg = 'The kiosk is now accepting keypad input from user or from the agent on behalf of the user.'
        print(msg)
        pyttsx3.speak(msg)
        
        print('Press CTRL-C to exit.')

        confirmation_code_confirm = False
        phone_number_valid = False
        while not phone_number_valid:
            
            msg = "Enter user's mobile number: "
            pyttsx3.speak(msg)
            mobile_number = input(msg)
            
            if len(mobile_number) != 10:
                msg = 'The phone number was invalid. Pleas enter a valid 10 digits US phone number. Do not preface with a "one"'
                print(msg)
                pyttsx3.speak(msg)
                
            else:
                # standardize the phone number with a "+1" in front
                mobile_number = "+1%s" % (mobile_number)
                phone_number_valid = True
                

                

                while confirmation_code_confirm is False:
                    
                    # Send and confirm code.
                    confirmation_code = str(random_number(4))
                    msg = "Your confirmation code is: %s" % (confirmation_code)
                    send_text(msg, mobile_number)
                    
                    
                    msg = ("""Thank you. A confirmation code is being sent to %s.
                           Please enter this code on the keypad or provide it to the attendant.""" % (mobile_number))
                    
                    print(msg)
                    pyttsx3.speak(msg)
                    

                    
                    msg = "Please enter the confirmation code received:"
                    pyttsx3.speak(msg)
                    confirm_code_from_user = input(msg)
                    if confirm_code_from_user == confirmation_code:
                        confirmation_code_confirm = True
                        phone_number_valid = True
                        msg = "Thank you. Your mobile phone number was verified."
                        print(msg)
                        pyttsx3.speak(msg)
                        
                    else:
                        phone_number_valid = False
                        msg = "The confirmation code was incorrect. Please re-enter your phone number for a new code."
                        print(msg)
                        pyttsx3.speak(msg)

        msg = """Reading information from the back of your license saves time and prevents errors.
                 Information including name, date of birth, and address will be collected."""
        print(msg)
        pyttsx3.speak(msg)

           
        msg = "Please present the barcode on the back of your state-issued driver's license or ID."
        print(msg)
        pyttsx3.speak(msg)
        
        
        for chunk in sys.stdin.buffer:
            if chunk.startswith(b'@^[[B^[[20~'):
                print("Barcode detected......................")

            elif chunk.startswith(b'END') or chunk.startswith(b'end'):
                print("Goodbye!")
                break

            elif chunk.startswith(b'ANSI'):
                
                print("Possible Real ID detected. Scanning....")
                response = parse_realid(chunk)
                idc = IDCardConfirmation.objects.create(details=json.dumps(response),
                                                        mobile_phone_number=mobile_number,
                                                        mobile_phone_number_verified=True,
                                                        org_slug=options['organization_slug'])
                print("Sending link to user to complete signup.")
                msg = """Thank you %s for enrolling in %s. You should shortly get a text
                         message with a link to complete your account signup.
                         You can complete this now or later.
                         The account login you create will allow you to access
                         your health information including your test results.""" % (response['first_name'], settings.APPLICATION_TITLE)
                pyttsx3.speak(msg)
                
                msg = """Hello %s %s. Welcome to %s. To complete your account signup please complete the online form at %s""" % (response['first_name'].title(),
                                                                                                                  response['last_name'].title(),
                                                                                                                  settings.APPLICATION_TITLE,
                                                                                                                  idc.url)
                send_text(msg, mobile_number)
                print("User's link to complete account is: %s " % idc.url)

