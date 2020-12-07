Dynamic Client Registration Protocol and analogous Django Management Command
============================================================================


Dynamic Client Registration Protocol
------------------------------------

To use Dynamic Client Registration Protocol (DCRP) you must have a valid username and password.
You must also be added to the `DynamicClientRegistrationProtocol` group by a systems administrator.
Currently this feature only registers `confidential` clients with the `authorization-code` grant type.


Below is a curl example for DCRP

The file `dr.json` contains the bofy of the HTTP request. For example:


    {
    "client_name": "foo",
    "client_id": "bar",
    "redirect_uris": ["https://foo.com", "https://bar.com"]
    }
    
The command to issue will look like:


    curl -X POST -d @dr.json http://verifymyidentity:8000/dcrp/register --user your-username:your-password

A successful HTTP result will contain the client key in its body as JSON....


    {
    "client_name": "bar",
    "client_id": "foo",
    "redirect_uris": ["https://foo.com", "https://bar.com"],
    "client_secret": "bnyCgI6HXZg1GaEOwzEJtyItW0MUclobAcrzwiKOICdVaD.....",
    "grant_types": ["authorization-code", "refresh_token"]
    }
    
    
Please also check out the tests for more examples.

Django Management Command: register_oauth2_client
------------------------------------------------


This command will create or modify applications (e.g.  replying parties)
on the command line. At least one entry is needed for redirect_uris.
The examples illustrate two.


Use the `register_oauth2_client` command like so:


    python manage.py  register_oauth2_client CLIENT_ID CLIENT_NAME --redirect_uris https://example.com/callback1 https://foo.example.com/callback2


If you want to specify the skip authorization option, issue the command like so:


    python manage.py  register_oauth2_client CLIENT_ID CLIENT_NAME --redirect_uris https://example.com/callback1 https://foo.example.com/callback2 --skip_authorization 1


    python manage.py  register_oauth2_client CLIENT_ID CLIENT_NAME --redirect_uris https://example.com/callback1 https://foo.example.com/callback2
    
    
You may also use this command to delete an application.


    python manage.py register_oauth2_client CLIENT_ID --delete