import random
from django.conf import settings
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
# Copyright Videntity Systems Inc.


def random_secret(y=40):
    return ''.join(random.choice('abcdefghijklmnopqrstuvwxyz'
                                 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                                 '0123456789') for x in range(y))


def mfa_via_email(user, code):

    subject = '[%s] Your code for access to' % (settings.APPLICATION_TITLE)
    from_email = settings.DEFAULT_FROM_EMAIL
    to = user.email

    html_content = """'
    <P>
    Provide this code on the authentication screen in your browser:<br>
     %s
    </p>
    <p>
    Thank you,
    </p>
    <p>
    The Team

    </P>
    """ % (code)

    text_content = """
    Provide this code on the authentication screen in your browser:
    %s

    Thank you,

    The Team

    """ % (code)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to, ])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def send_password_reset_url_via_email(user, reset_key):
    subject = '[%s]Your password ' \
              'reset request' % (settings.ORGANIZATION_NAME)
    from_email = settings.DEFAULT_FROM_EMAIL
    to = user.email
    link = '%s%s' % (settings.HOSTNAME_URL,
                     reverse('password_reset_email_verified',
                             args=(reset_key,)))
    html_content = """'
    <P>
    Click on the link to reset your password.<br>
    <a href='%s'> %s</a>
    </p>
    <p>
    Thank you,
    </p>
    <p>
    The Team

    </P>
    """ % (link, link)

    text_content = """
    Click on the link to reset your password.
    %s


    Thank you,

    The Team

    """ % (link)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to, ])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
    print("SENT")


def send_activation_key_via_email(user, signup_key):
    """Do not call this directly.  Instead use create_signup_key in utils."""
    subject = '[%s]Verify your email.' % (settings.ORGANIZATION_NAME)
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email, ]
    activation_link = '%s%s' % (settings.HOSTNAME_URL,
                                reverse('activation_verify',
                                        args=(signup_key,)))

    html_content = """
       <p>
       Hello %s. Please click the link to activate your account.<br>
       <a href=%s a> %s</a><br>

       Thank you,<br>

       The Team
       </p>
       """ % (user.first_name, activation_link, activation_link)

    text_content = """
       Hello %s. Please click the link to activate your account.

        %s

       Thank you,

       The Team

       """ % (user.first_name, activation_link)

    msg = EmailMultiAlternatives(subject=subject, body=text_content,
                                 to=to, from_email=from_email)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def send_new_org_account_approval_email(to_user, about_user):
    plaintext = get_template('approve-organization-affiliation-email.txt')
    htmly = get_template('approve-organization-affiliation-email.txt')
    context = {"APPLICATION_TITLE": settings.APPLICATION_TITLE,
               "TO_FIRST_NAME": to_user.first_name,
               "TO_LAST_NAME": to_user.last_name,
               "FROM_FIRST_NAME": about_user.first_name,
               "FROM_LAST_NAME": about_user.last_name
               }

    subject = """[%s]A New user account has been created for your organization that requires your approval.""" % (
        settings.ORGANIZATION_NAME)
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [to_user.email, ]

    text_content = plaintext.render(context)
    html_content = htmly.render(context)

    msg = EmailMultiAlternatives(subject=subject, body=text_content,
                                 to=to, from_email=from_email)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def send_org_account_approved_email(to_user):
    plaintext = get_template('organization-affiliation-approved-email.txt')
    htmly = get_template('organization-affiliation-approved-email.txt')
    context = {"APPLICATION_TITLE": settings.APPLICATION_TITLE,
               "TO_FIRST_NAME": to_user.first_name,
               "TO_LAST_NAME": to_user.last_name,
               }

    subject = """[%s]Your account has been approved by your organization's point of contact""" % (
        settings.ORGANIZATION_NAME)
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [to_user.email, ]

    text_content = plaintext.render(context)
    html_content = htmly.render(context)

    msg = EmailMultiAlternatives(subject=subject, body=text_content,
                                 to=to, from_email=from_email)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
