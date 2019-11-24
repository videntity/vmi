import random
from django.conf import settings
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

# Copyright Videntity Systems Inc.
__author__ = "Alan Viars"


def random_secret(y=40):
    return ''.join(random.choice('abcdefghijklmnopqrstuvwxyz'
                                 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                                 '0123456789') for x in range(y))


def send_member_verify_request_email(to_user, about_user_profile, organization):
    """Send to trust/org agents to login and verify the identity of this person."""

    plaintext = get_template('verify-new-member-email.txt')
    htmly = get_template('verify-new-member-email.html')
    context = {"APPLICATION_TITLE": settings.APPLICATION_TITLE,
               "TO_FIRST_NAME": to_user.first_name,
               "TO_LAST_NAME": to_user.last_name,
               "ABOUT_FIRST_NAME": about_user_profile.user.first_name,
               "ABOUT_LAST_NAME": about_user_profile.user.last_name,
               "ORGANIZATION_NAME": organization.name,
               "ABOUT_SUBJECT": about_user_profile.subject,
               "HOSTNAME_URL": settings.HOSTNAME_URL,
               }

    subject = """[%s]A New Member account requires your approval.""" % (
        settings.ORGANIZATION_NAME)
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [to_user.email, ]

    text_content = plaintext.render(context)
    html_content = htmly.render(context)

    msg = EmailMultiAlternatives(subject=subject, body=text_content,
                                 to=to, from_email=from_email)
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
    <p>
    Click on the link to reset your password.<br>
    <a href='%s'> %s</a>
    </p>
    <p>
    Thank you,
    </p>
    <p>
    The %s Team

    </p>
    """ % (link, link, settings.ORGANIZATION_NAME)

    text_content = """
    Click on the link to reset your password.
    %s


    Thank you,

    The %s Team

    """ % (link, settings.ORGANIZATION_NAME)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to, ])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def send_activation_key_via_email(user, signup_key):
    """Do not call this directly.  Instead use create_signup_key in utils."""
    plaintext = get_template('verify-your-email-email.txt')
    htmly = get_template('verify-your-email-email.html')

    subject = '[%s]Verify your email address' % (settings.ORGANIZATION_NAME)

    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email, ]
    activation_link = '%s%s' % (settings.HOSTNAME_URL,
                                reverse('activation_verify',
                                        args=(signup_key,)))

    context = {"APPLICATION_TITLE": settings.APPLICATION_TITLE,
               "FIRST_NAME": user.first_name,
               "LAST_NAME": user.last_name,
               "ACTIVATION_LINK": activation_link,
               }

    text_content = plaintext.render(context)
    html_content = htmly.render(context)
    msg = EmailMultiAlternatives(subject=subject, body=text_content,
                                 to=to, from_email=from_email)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def send_new_org_account_approval_email(to_user, about_user, organization):
    plaintext = get_template('approve-organization-affiliation-email.txt')
    htmly = get_template('approve-organization-affiliation-email.html')
    context = {"APPLICATION_TITLE": settings.APPLICATION_TITLE,
               "TO_FIRST_NAME": to_user.first_name,
               "TO_LAST_NAME": to_user.last_name,
               "ABOUT_FIRST_NAME": about_user.first_name,
               "ABOUT_LAST_NAME": about_user.last_name,
               "ORGANIZATION_NAME": organization.name,
               "HOSTNAME_URL": settings.HOSTNAME_URL,
               }

    subject = """[%s]A New organizational account for %s requires your approval.""" % (
        settings.ORGANIZATION_NAME, organization.name)
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [to_user.email, ]

    text_content = plaintext.render(context)
    html_content = htmly.render(context)

    msg = EmailMultiAlternatives(subject=subject, body=text_content,
                                 to=to, from_email=from_email)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def send_org_account_approved_email(to_user, organization):
    plaintext = get_template('organization-affiliation-approved-email.txt')
    htmly = get_template('organization-affiliation-approved-email.html')
    context = {"APPLICATION_TITLE": settings.APPLICATION_TITLE,
               "TO_FIRST_NAME": to_user.first_name,
               "TO_LAST_NAME": to_user.last_name,
               "HOSTNAME_URL": settings.HOSTNAME_URL,
               "ORGANIZATION_NAME": organization.name,
               "KILLER_APP_URI": settings.KILLER_APP_URI
               }

    subject = """[%s]Your account has been approved by %s's point of contact""" % (
        settings.ORGANIZATION_NAME, organization.name)
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [to_user.email, ]

    text_content = plaintext.render(context)
    html_content = htmly.render(context)

    msg = EmailMultiAlternatives(subject=subject, body=text_content,
                                 to=to, from_email=from_email)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
