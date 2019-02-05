# Verify My Identity

[![OpenID Certified](https://cloud.githubusercontent.com/assets/1454075/7611268/4d19de32-f97b-11e4-895b-31b2455a7ca6.png)](https://openid.net/certification/)

Verify My Identity is a certified OpenID Connect Provider. Its supports role-based permission bu using Django groups. VMI manages relationships between 
Organizations, staff users, and consumer users. Other features include:


* Trusted Referee Support - According to NIST SP 800-63-3.
* FIDO U2F / FIDO 2 Support
* Text Message multi-facotor Support 
* Vectors of Trust Support
* Support for `document` and `address` claims a defined in the iGov Profile for OIDC.


Installation
------------

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

```
docker-compose exec web .development/migrate.sh
# if any permissions errors are thrown try
# docker-compose exec web chmod +x .development/migrate.sh
# then run the migrate script again
```

If you make changes to requirements.txt to add libraries re-run 
docker-compose with the --build option.

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