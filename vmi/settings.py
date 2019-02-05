"""
Django settings for vmi project.

Generated by 'django-admin startproject' using Django 2.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import dj_database_url
from django.contrib.messages import constants as messages
from getenv import env

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@+ttixefm9-bu1eknb4k^5dj(f1z0^97b$zan9akdr^4s8cc54'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrapform',
    'phonenumber_field',
    'oauth2_provider',
    'rest_framework',
    'apps.oidc',
    'apps.home',
    'apps.accounts',
    'apps.ial',
    'apps.fido',
    'apps.mfa.backends.sms',

    # 'django_extensions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.mfa.middleware.DeviceVerificationMiddleware',
    'apps.mfa.middleware.AssertDeviceVerificationMiddleware',

    'apps.oidc.error_handlers.AuthenticationRequiredExceptionMiddleware',
    'apps.oidc.error_handlers.OIDCNoPromptMiddleware',
]

VERIFICATION_BACKENDS = [
    'apps.fido.auth.backends.FIDO2Backend',
    'apps.mfa.backends.sms.backend.SMSBackend',
]

SMS_CODE_CHARSET = "1234567890"

ROOT_URLCONF = 'vmi.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_settings_export.settings_export',
            ],
        },
    },
]

WSGI_APPLICATION = 'vmi.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
        default=env('DATABASES_CUSTOM',
                    'sqlite:///{}/db.sqlite3'.format(BASE_DIR))),
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = 'sitestatic'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static-assets"),
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
    ),
}

# OAUTH SETTINGS
OAUTH2_PROVIDER = {
    'SCOPES': {'openid': 'open id connect access'},
    'DEFAULT_SCOPES': ['openid'],
    'OAUTH2_VALIDATOR_CLASS': 'apps.oidc.request_validator.RequestValidator',
    'OAUTH2_SERVER_CLASS': 'apps.oidc.server.Server',
    'REQUEST_APPROVAL_PROMPT': 'auto',
}
OAUTH2_PROVIDER_GRANT_MODEL = 'oidc.Grant'
OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL = 'oauth2_provider.AccessToken'
OAUTH2_PROVIDER_APPLICATION_MODEL = 'oauth2_provider.Application'
OAUTH2_PROVIDER_REFRESH_TOKEN_MODEL = 'oauth2_provider.RefreshToken'
OIDC_PROVIDER = {
    # 'OIDC_ISSUER': 'http://localhost:8000',
    'OIDC_BASE_CLAIM_PROVIDER_CLASS': 'apps.oidc.claims.ClaimProvider',
    'OIDC_CLAIM_PROVIDERS': [
        # Mandatory
        'apps.oidc.claims.UserClaimProvider',
        'apps.accounts.claims.SubjectClaimProvider',
        # Optional
        # This claim provider currently gets all claims fetch-able via the
        # UserProfile.
        'apps.accounts.claims.UserProfileClaimProvider',
        'apps.accounts.claims.AddressClaimProvider',
        'apps.accounts.claims.IdentifierClaimProvider',
        # 'apps.accounts.claims.EmailVerifiedClaimProvider',
        # 'apps.accounts.claims.PhoneNumberClaimProvider',
        # 'apps.accounts.claims.IdentityAssuranceLevelClaimProvider',
        # 'apps.accounts.claims.AuthenticatorAssuranceLevelClaimProvider',
        # 'apps.accounts.claims.VectorsOfTrustClaimProvider',
        'apps.fido.claims.AuthenticatorAssuranceProvider',
        'apps.mfa.backends.sms.claims.AuthenticatorAssuranceProvider',
    ],
}


# Add a prefix to the lugh checkdigit calculation.
# This can help identify genuine subject ids and indicate provenance.
SUBJECT_LUHN_PREFIX = env('SUBJECT_LUHN_PREFIX', '')
APPLICATION_TITLE = env('DJANGO_APPLICATION_TITLE',
                        'Verify My Identity')
ORGANIZATION_TITLE = env(
    'DJANGO_ORGANIZATION_TITLE',
    'Alliance for Better Health')
ORGANIZATION_URI = env('DJANGO_ORGANIZATION_URI', 'https://abhealth.us')
POLICY_URI = env(
    'DJANGO_POLICY_URI',
    'https://abhealth.us')
POLICY_TITLE = env('DJANGO_POLICY_TITLE', 'Privacy Policy')
TOS_URI = env('DJANGO_TOS_URI', 'https://abhealth.us')
TOS_TITLE = env('DJANGO_TOS_TITLE', 'Terms of Service')
TAG_LINE_1 = env('DJANGO_TAG_LINE_1', 'Share your health data')
TAG_LINE_2 = env('DJANGO_TAG_LINE_2',
                 'with applications, organizations, and people you trust.')
EXPLAINATION_LINE = ('This service allows Medicare beneficiaries'
                     'to connect their health data to applications'
                     'of their choosing.')
EXPLAINATION_LINE = env('DJANGO_EXPLAINATION_LINE ', EXPLAINATION_LINE)
USER_DOCS_URI = "https://abhealth.us"
USER_DOCS_TITLE = "User Documentation"
USER_DOCS = "User Docs"
# LINKS TO DOCS
DEVELOPER_DOCS_URI = "https:/abhealth.us"
DEVELOPER_DOCS_TITLE = "Developer Documentation"
DEVELOPER_DOCS = "Developer Docs"
DEFAULT_DISCLOSURE_TEXT = """
    Unauthorized or improper use of this
    system or its data may result in disciplinary action, as well as civil
    and criminal penalties. This system may be monitored, recorded and
    subject to audit.
    """

DISCLOSURE_TEXT = env('DJANGO_PRIVACY_POLICY_URI', DEFAULT_DISCLOSURE_TEXT)

HOSTNAME_URL = env('HOSTNAME_URL', 'http://localhost:8000')


SETTINGS_EXPORT = [
    'DEBUG',
    'ALLOWED_HOSTS',
    'APPLICATION_TITLE',
    'STATIC_URL',
    'STATIC_ROOT',
    'DEVELOPER_DOCS_URI',
    'DEVELOPER_DOCS_TITLE',
    'ORGANIZATION_TITLE',
    'POLICY_URI',
    'POLICY_TITLE',
    'DISCLOSURE_TEXT',
    'TOS_URI',
    'TOS_TITLE',
    'TAG_LINE_1',
    'TAG_LINE_2',
    'EXPLAINATION_LINE',
    'USER_DOCS_URI',
    'USER_DOCS',
    'DEVELOPER_DOCS',
    'USER_DOCS_TITLE',
    'HOSTNAME_URL',
]

# Emails
DEFAULT_FROM_EMAIL = env('DJANGO_FROM_EMAIL', 'no-reply@verifymyidentity.com')
DEFAULT_ADMIN_EMAIL = env('DJANGO_ADMIN_EMAIL',
                          'no-reply@verifymyidentity.com')

# The console.EmailBackend backend prints to the console.
# Redefine this for SES or other email delivery mechanism
EMAIL_BACKEND_DEFAULT = 'django_ses.SESBackend'
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', EMAIL_BACKEND_DEFAULT)

# Un-comment the next line to print emails to the console instead of using SES.
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MFA = True

SIGNUP_TIMEOUT_DAYS = 3
ORGANIZATION_NAME = "Verify My Identity"


INDIVIDUAL_ID_TYPE_CHOICES = (
    ('PATIENT_ID_FHIR', 'Patient ID FHIR'),
    ('MPI', 'Master Patient Index (Not FHIR Patient id)'),
    ('SSN', 'Social Security Number'),
    ('MEDICIAD_ID', 'Medicaid ID Number'),
    ('MEDICICARE_HICN', 'Medicare HICN (Legacy)'),
    ('MEDICIARE_ID', 'Medicare ID Number'),
    ('INDURANCE_ID', 'Insurance ID Number'),
    ('IHE_ID', 'Health Information Exchange ID'),
    ('UHI', 'Universal Health Identifier'),
)

ORGANIZATION_ID_TYPE_CHOICES = (
    ('FEIN', 'Federal Employer ID Number (Tax ID)'),
    ('NPI', 'National Provider Identifier'),
    ('OEID', 'Other Entity Identifier'),
    ('PECOS', 'PECOS Medicare ID')
)

PHONENUMBER_DEFAULT_REGION = 'US'
