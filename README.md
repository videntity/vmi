# Verify My Identity (VMI)

[![OpenID Certified](https://cloud.githubusercontent.com/assets/1454075/7611268/4d19de32-f97b-11e4-895b-31b2455a7ca6.png)](https://openid.net/certification/)

Verify My Identity is a certified OpenID Connect Provider. Its supports role-based permission by using Django groups. VMI manages relationships between organizations, staff users, and consumer users. Other features include:


* Trusted Referee Support - According to NIST SP 800-63-3.
* FIDO U2F / FIDO 2 Support
* Text Message multi-facotor authentication support 
* Vectors of Trust Support
* Support for `document` and `address` claims as defined in the iGov Profile for OIDC.


Installation
------------

This project is based on Python 3.6 and Django 2.1.x. 

Dowload the project:

    git clone https://github.com/TransparentHealth/vmi.git
   

Install supporting libraries. (Consider using virtualenv for your pythoin setup.

    cd vmi
    pip install -r requirements.txt

Depending on your local environment you made need some supporting libraries
for the above com,mand to run cleanly. For example you need a 
compiler and python-dev.

Setup some local enviroment variables. 


    export AWS_ACCESS_KEY_ID="YOUR_KEY_ID"
    export AWS_SECRET_ACCESS_KEY="YOUR_SECRET"
    export OIDC_PROVIDER="http://localhost:8000"
    export OIDC_ISSUER="http://localhost:8000"
    export ALLOWED_HOSTS="*"
    export ROOT_USER=superman
    export ROOT_PASSWORD=manofst33l

Just add the above to a `.env` and then do a 'source .env'. Without valid 
AWS credentials email and SMS text functions will not work. The root username and password 
are used to create a default superuser.

Create the database:

    python manage.py migrate

As mentioned above, this step also creates a superuser.

Run the development server like so:


     python manage.py runserver




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

After the VMI Docer container is comepltely setup, you execute Django 
commands like so:


`docker-compose -f .development/docker-compose.yml exec web python manage.py`




Connecting ShareMyHealth and VerifyMyIdentity
---------------------------------------------

The following link outlines some settings for getting Verify My Identity and Share My Health working in
a in a local development environment.

[Local Verify My Identity and Share My Health](https://gist.github.com/whytheplatypus/4b11eec09df978656b9007155a96c7dd)



## Associated Projects

[VerifyMyIdentity - VMI](https://github.com/TransparentHealth/vmi), 
a standards-focused OpenID Connect Identity Provider.

[ShareMyHealth](https://github.com/TransparentHealth/sharemyhealth) is designed as a 
consumer-mediated health information exchange.  
ShareMyHealth acts as a relying party to 
[vmi](https://github.com/TransparentHealth/vmi).

## Supporting Resources

vmi uses css resources from Bootstrap (v.3.3.x) and 
Font-Awesome (v4.4.x). 


=======
identity assurance escelation and FIDO.

This project is based on Python 3.6 and Django 2.1.x.

Install supporting libraries with

    pip install -r requirements.txt
    

Alternatively, a Docker configuration is available in:

    .development

By default the docker instance will be attached to 
port **8000** on localhost

It will also configure a postgreSQL instance on port **5432**.

If you're working with a fresh db image
the migrations have to be run.

If you make changes to requirements.txt to add libraries re-run 
docker-compose with the --build option.

## Associated Projects

[ShareMyHealth](https://github.com/TransparentHealth/sharemyhealth) is designed as a 
consumer-mediated health information exchange.  
ShareMyHealth acts as a relying party to 
[vmi](https://github.com/TransparentHealth/vmi).

## Supporting Resources

vmi uses css resources from Bootstrap (v.3.3.x) and 
Font-Awesome (v4.4.x). 
