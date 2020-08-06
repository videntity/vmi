# Verify My Identity (VMI)

[![OpenID Certified](https://cloud.githubusercontent.com/assets/1454075/7611268/4d19de32-f97b-11e4-895b-31b2455a7ca6.png)](https://openid.net/certification/)

Verify My Identity is a certified OpenID Connect Provider. Its supports role-based permissions by using Django groups.
VMI manages relationships between organizations, staff users, and consumer users. Other features include:


* Trusted Referee Support - According to NIST SP 800-63-3.
* FIDO U2F / FIDO 2 Support
* Text Message Multi-factor authentication support 
* Vectors of Trust Support
* Support for `document` and `address` claims as defined in the iGov Profile for OIDC.


Installation
------------

This project is based on Python 3.6 and Django 2.1.x. 

Download the project:


    git clone https://github.com/TransparentHealth/vmi.git
   

Install dev libraries 
``````````````````````

(Ubuntu/Debian)

    sudo apt-get install python3.6-dev libsasl2-dev python-dev libldap2-dev libssl-dev


(RetHat/CentOS)

Install supporting libraries. (Consider using virtualenv for your python setup).

    sudo yum install python-devel openldap-devel

    cd vmi
    pip install -r requirements.txt

Depending on your local environment you made need some supporting libraries
for the above command to run cleanly. For example you need a 
compiler and python-dev.


Add some entries to your `/etc/hosts` file.


If running this OIDC server in conjunction with `smh_app` or `sharemyhealth` (OAuth2 server)
on the same machine for development, then we recommend setting up names for each server host in `/etc/hosts`.
You might add lines like the following to `/etc/hosts` file:


     127.0.0.1       verifymyidentity
     127.0.0.1       oauth2org




Setup some local environment variables via whatever stategy you choose.
The default is using a `.env` file containing the following.
Set this variable specific toy your hostname and environment


    export EC2PARAMSTORE_4_ENVIRONMENT_VARIABLES=".ENV" 
    export AWS_ACCESS_KEY_ID="YOUR_KEY_ID"
    export AWS_SECRET_ACCESS_KEY="YOUR_SECRET"
    export OIDC_PROVIDER="http://verifymyidentity:8000"
    export OIDC_ISSUER="http://verifymyidentity:8000"
    export HOSTNAME_URL="http://verifymyidentity:8000"
    export ALLOWED_HOSTS="*"
    export DJANGO_SUPERUSER_USERNAME="youruser"
    export DJANGO_SUPERUSER_PASSWORD="yourpassword"
    export DJANGO_SUPERUSER_EMAIL="super@example.com"
    export DJANGO_SUPERUSER_FIRST_NAME="Super"
    export DJANGO_SUPERUSER_LAST_NAME="User"


    export FROM_EMAIL="no-reply@verifymyidentity.org"
    export ADMIN_EMAIL="no-reply@verifymyidentity.org"



    # If using Twilio for SMS  delivery 
    export TWILIO_ACCOUNT_SID="ACcccXXXXXXXXXXXXXXXXXXXXXX"
    export TWILIO_TOKEN="4161XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    export TWILIO_FROM_NUMBER="+12025555555"
    
    # If using Sendgrid for email delivery 
    export SENDGRID_API_KEY="SG.FyxxxXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXi0c0MuH3Af_g"
    
    # Do some basic branding. (See the settings file for more options.)
    export SUBJECT_LUHN_PREFIX = env('SUBJECT_LUHN_PREFIX', '012345')
    export ORGANIZATION_NAME = env('DJANGO_APPLICATION_TITLE', "Diamond Health")
    
    # You may also override the top left project name
    export TOP_LEFT_TITLE = env('TOP_LEFT_TITLE', 'verify my identity2')
    export PARTNER_REF = env('PARTNER_REF', 'Diamond Health')
    



This is how you can brand the project to your needs.
See the `settings.py` and for a full list.  Below are some basic variable you may want to set.

Just add the above to a `.env` and then do a `source .env`. Without valid 
AWS credentials email and SMS text functions will not work. The superuser settings
are used to create a default superuser.

Create the database:


    python manage.py migrate


Create initial Groups and Permissions, and Organizations


    python manage.py create_default_groups
    python manage.py create_sample_organizations



Create a superuser (Optional)


    python manage.py create_super_user_from_envars


In development our convention is to run `vmi` on port `8000`, `sharemyhealth` on 8001, and `smh_app` on `8002`.
To start this server on port 8001 issue the following command.


     python manage.py runserver 


This will start the server on the default port of `8000`.




Docker Installation
-------------------

Alternatively, a Docker configuration is available in:


    .development

By default the docker instance will be attached to 
port **8000** on localhost

It will also configure a postgreSQL instance on port **5432**.

If you're working with a fresh db image
the migrations have to be run.

```
docker-compose -f .development/docker-compose.yml exec web python manage.py migrate
```

If you make changes to `requirements.txt` to add libraries re-run 
`docker-compose` with the `--build` option.

After the VMI Docker container is completely setup, you execute Django 
commands like so:


`docker-compose -f .development/docker-compose.yml exec web python manage.py`


Connecting ShareMyHealth ShareMyHealth App, and VerifyMyIdentity
------------------------------------------====================---

The following link outlines some settings for getting Verify My Identity and Share My Health working in
a in a local development environment.

[Local Verify My Identity and Share My Health](https://gist.github.com/whytheplatypus/4b11eec09df978656b9007155a96c7dd)



## Associated Projects

[VerifyMyIdentity - VMI](https://github.com/TransparentHealth/vmi), 
a standards-focused OpenID Connect Identity Provider.


[ShareMyHealth](https://github.com/TransparentHealth/sharemyhealth) is designed as a 
consumer-mediated health information exchange. It is an OAuth2 Provider and FHIR Server.  
ShareMyHealth acts as a relying party to 
[vmi](https://github.com/TransparentHealth/vmi).


[ShareMyHealth App](https://github.com/TransparentHealth/sharemyhealth) is a web application
for community members and community-based organizations.  It functions as a personal health record
and allows users to selectivly share information with organizations they choose.

ShareMyHealth App is an OAuth2 client to [ShareMyHealth](https://github.com/TransparentHealth/sharemyhealth).
It gets healkth information as FHIR.  It is also a relying party to [vmi](https://github.com/TransparentHealth/vmi).


## Supporting Resources

vmi uses css resources from Bootstrap (v.3.3.x) and 
Font-Awesome (v4.4.x). 

