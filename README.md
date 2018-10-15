# vmi

VerifyMyIdentity.com - An OpenID Connect Provider supporting 
identity assurance escelation and FIDO.

This project is based on Python 3.5 and Django 2.1.x.

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

[VerifyMyIdentity - VMI](https://github.com/TransparentHealth/vmi), 
a standards-focused OpenID Connect Identity Provider.

[ShareMyHealth](https://github.com/TransparentHealth/sharemyhealth) is designed as a 
consumer-mediated health information exchange.  
ShareMyHealth acts as a relying party to 
[vmi](https://github.com/TransparentHealth/vmi).

## Supporting Resources

vmi uses css resources from Bootstrap (v.3.3.x) and 
Font-Awesome (v4.4.x). 

More to come... 

