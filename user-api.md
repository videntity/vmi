Creating and Modify Users for Consumer Directed Exchange
========================================================

This document describes how to create and modify users in VerifyMyIdentity. VerifyMyIdentity is an open-source standards-focused certified Open ID Connect (OIDC) Identity Provider. 

The following examples create "Member" accounts for purposes of Consumer Directed Exchange (CDeX). Member is often an synonym for "Patient", "Conumser", "Client", and "Community Member".  The API calls shown here are to be used by trusted 3rd party applications.

The field names and structure of the HTTP request\response  bodies mirror and build upon Open ID Connect (OIDC) https://openid.net/specs/openid-connect-core-1_0.html and the iGov Profile for OpenID Connect https://openid.net/specs/openid-igov-openid-connect-1_0-02.html.

Authorization to the API is controlled through OAuth2.



Create a User Example #1: Minimal
==============================

The following example illustrates a bare rminimum request necessary to create a new user for purposes of Consumer Directed Exchange) 

* HTTP Method: POST 
* Request Body: application/json
* Response Body: application/json
* Endpoint:https://alpha.verifymyidentity.com/api/v1/user/
* Authorization: OAuth2 Bearer Token

Discussion
----------
The fields `gender` and `birthdate` are not strictly required to create an account but are necessary to enable patient-linking and matching to the individual's health records.   While not required a `password` parameter may also be given in this request.  If the password is not set, the user will need to set their own password through some alternative workflow.  In this example, there are no claims being made about the user's identity assurance level (IAL), therefore the resulting IAL is `1` (lowest trust).  In the next Enriched Example section we will create a more robust user from the start.


Request Body
------------

    {
    "preferred_username": "james",
    "given_name": "James",
    "family_name": "Kirk",
    "gender": "male",
    "birthdate": "1952-01-03"
    }




Successful Request Response
---------------------------

A successful response `HTTP 200` will return a similar structure to what was sent.:


    {
    "iss": "https://alpha.verifymyidentity.com",
    "subject": "123456789012345",  
    "username": "james",   
    "given_name": "James",
    "family_name": "Kirk",
    "gender": "male",
    "birthdate": "1952-01-03",
    "ial": 1,
    "id_assursance" : [],
    "document" : [],
    "address": []
    }


Create a User Example #2 - More Options
========================================

The following example illustrates an account creation with more demographic and identity infiormation.


* HTTP Method: POST 
* Request Body: application/json
* Response Body: application/json
* Endpoint:https://alpha.verifymyidentity.com/api/v1/user/
* Authorization: OAuth2 Bearer Token



Request Body
------------

    {
  	"iss": "https://alpha.verifymyidentity.com",
    "subject": "123456789012345",  
    "preferred_username": "james",
    "given_name": "James",
    "family_name": "Kirk",
    "gender": "male",
    "password": "tree garden jump fox,
    "birthdate": "1952-01-03",
    "nickname": "Jim",
    "phone_number": "+15182345678",
    "email": "jamess@example.com"
    }



Successful Request Response
---------------------------

A successful response `HTTP 200`:


    {
    "iss": "https://alpha.verifymyidentity.com",
    "subject": "123456789012345", 
    "preferred_username": "james",
    "given_name": "James",
    "family_name": "Kirk",
    "name": "James Kirk",
    "gender": "male",
    "birthdate": "1952-01-03",
    "nickname": "Jim",
    "phone_number": "+15182345678",
    "email": "jamess@example.com",
    "ial": 1,
    "id_assursance" : [],
    "document" : [],
    "address": []
    }



Modify a User's Date of Birth
------------------------------

* HTTP Method: POST or PUT
* Request Body: application/json
* Response Body: application/json
* Endpoint: https://alpha.verifymyidentity.com/api/v1/user/[sub]
* Authorization: OAuth2 Bearer Token


Request Endpoint: HTTP PUT /api/v1/user/123456789012345

Request Body:
-------------


    {
    "birthdate": "2233-03-22"
    }



Successful Response
-------------------

Response code is `200`. 


    {
    "sub": "123456789012345",
    "birthdate": "2233-03-22"
    }



Adding\Modify Identity Assurance Level Evidence
-----------------------------------------------

* HTTP Method: `POST` (tp create) amd `PUT` (to Modify)
* Request Body: application/json
* Response Body: application/json
* Endpoint:https://alpha.verifymyidentity.com/api/v1/user/[sub]
* Authorization: OAuth2 Bearer Token

Adding a record of identifity verifieaction is how the IAL is calculated.  The `sub` is provided  as the identifer for the user record. 
In most cases, the goal is to move a user's account from level `1` to level `2` for an extended period of time. The identity assurance level (IAL) claim contains:

* A description of the evidence
* A code classifiing the evidence. Codes include `ONE-SUPERIOR-OR-STRONG+`,`ONE-STRONG-TWO-FAIR`,`TWO-STRONG`,  `TRUSTED-REFEREE-VOUCH`, and `KBA`. See Nist SP 800-63-3 for details.
* The subject identifier of the person acting as a trusted agent (if applicable).
* The date of the identity verification check.


Request Endpoint: HTTP POST `/api/v1/user/123456789012345/id-assurance/`

Request Body for Create
-----------------------


    {
    "description": "NY Medicaid card.",
    "classification": "ONE-SUPERIOR-OR-STRONG+",
    "exp": "2022-01-01",
    "verifier_subject": "876545671054321",
    "note": "A paper copy of the document is on file.",
    "verification_date": "2019-03-04"
    }




Example Response for Create
---------------------------


    {
    "uid": "97fb9995-fa8b-4719-9f55-65c1c5f4fd1b",
    "description": "NY Medicaid card.",
    "classification": "ONE-SUPERIOR-OR-STRONG+",
    "verifier_subject": "876545671054321",
    "note": "A paper copy of the document is on file.",
    "verification_date": "2019-03-04",
    "user": {
            "subject": "123456789012345"
    		}
     }


Request Endpoint: HTTP PUT `/api/v1/user/123456789012345/id-assurance/97fb9995-fa8b-4719-9f55-65c1c5f4fd1b`

Request Body for Update
-----------------------

In this exaample the expiration date is updated.

    {
    "uid": "97fb9995-fa8b-4719-9f55-65c1c5f4fd1b",
    "description": "NY Medicaid card.",
    "classification": "NE-SUPERIOR-OR-STRONG+",
    "exp": "2028-12-12",
    "verifier_subject": "876545671054321",
    "note": "A paper copy of the document is on file.",
    "verification_date": "2019-03-04"
    }



Example Response for Update
---------------------------


    {
     "uid": "97fb9995-fa8b-4719-9f55-65c1c5f4fd1b",
     "description": "NY Medicaid card.",
     "classification": "NE-SUPERIOR-OR-STRONG+",
     "exp": "2028-12-12",
     "verifier_subject": "876545671054321",
     "note": "A paper copy of the document is on file.",
     "verification_date": "2019-03-04"
    		"user": {
                    "subject": 123456789012345
    			}
     }



Adding\Modifying Identifiers
----------------------------

* HTTP Method: `POST` (to create) `PUT` (to update)
* Request Body: application/json
* Response Body: application/json
* Endpoint:https://alpha.verifymyidentity.com/api/v1/user/[sub]/identifier/
* Authorization: OAuth2 Bearer Token

Identifiers are for adding master patient indexes and other types of pointers to individuals.  Examples include, a Mediciad ID number, a driver's license numbers, and a patient ID to a particular online resource (e.g. FHIR)aa record of identifity verifieaction is how the IAL is calculated.  The `sub` is provided  as the identifer for the user record. 
In most cases, the goal is to move a user's account from level `1` to level `2` for an extended period of time.



Adding a Mediciad ID number
---------------------------

Request Endpoint: HTTP POST /api/v1/user/123456789012345/identifier/

Request Body for Create Identifier
-------------------------


      {
  	  "issuer": "New York Department of Health HHS Mediciad Duke Health Systems",
      type": "MEDICIAD_ID_NY",
      "num": "9ASDFG2",
      "region": "NY"
      }




Successful Response for Create Identifer
----------------------------------------

    {
    "uid": "94474d22-0962-4a6b-89ba-cddbe3e3a8d4",
    "issuer": "New York Department of Health HHS Mediciad Duke Health Systems",
    "type": "MEDICIAD_ID_NY",
    "num": "9ASDFG2",
    "region": "NY"
    "user": {
            "subject": 123456789012345
        	}
     }


Adding FHIR Pointers as Identifiers
-----------------------------------

* HTTP Method: `POST` (to create) `PUT` (to update)
* Request Body: application/json
* Response Body: application/json
* Endpoint:https://alpha.verifymyidentity.com/api/v1/user/[sub]/identifier/
* Authorization: OAuth2 Bearer Token


In the folowing example, two patient ID's to consumer facing API's are added to the user's record.
The `software_id` field is used as the primary key to uniquely identify a given system. The `issuer` is a string describing the system.  The `type` identifies the type of the data contained in `nu,`  The `endpoint'` is the actual URL for the FHIR Resource server.  The `num` is the actual FHIR patient identier. Despit its name, it need not be a number.

Request
-------
    {"document":
    [{
    		"issuer": "Health information Exchange of NY (HIXNY)",
    		"software_id": "HIXNY-patient-api",
    		"type": "FHIR_PATIENT_ID",
    		"num": "123456789012345",
    		"endpoint": "https://hixny.oauth2.io/fhir/patient/DSTU2/"
    	},
    	{
            "uid": "d64e9b97-2a5a-4e69-b400-ad059a8c1fc8",
    		"issuer": "Duke Health Systems",
    		"software_id": "Duke-Health-Systems-Patient-API",
    		"type": "FHIR_PATIENT_ID",
    		"num": "TGifRZDexrA8rYQWTmVU0e8G0VCpxGrspxW0dZ3Ls1owB",
    		"endpoint": "https://health-apis.duke.edu/FHIR/patient/DSTU2/"
    	}]
      }

Successful Response
-------------------

    {"sub": "123456789012345",
     "document":
        [
    	{
        "uid": "94474d22-0962-4a6b-89ba-cddbe3e3a8d4",
    	"issuer": "New York Department of Health HHS Mediciad Duke Health Systems",
    	"type": "MEDICIAD_ID",
    	"num": "9ASDFG2",
        "region": "NY"
        "user": {
        "subject": "123456789012345"
    			}
    	},
    	{
        "uid": "50efab40-fd26-4f75-b124-30e4cec93620",
    	"issuer": "Health information Exchange of NY (HIXNY)",
    	"software_id": "HIXNY-patient-api",
    	"type": "FHIR_PATIENT_ID",
    	"num": "123456789012345",
    	"endpoint": "https://hixny.oauth2.io/fhir/patient/DSTU2/"
    	"user": {
                "subject": "123456789012345"
    			}
    	},
    	{
        "uid": "d64e9b97-2a5a-4e69-b400-ad059a8c1fc8",
    	"issuer": "Duke Health Systems",
    	"software_id": "Duke-Health-Systems-Patient-API",
    	"type": "FHIR_PATIENT_ID",
    	"num": "TGifRZDexrA8rYQWTmVU0e8G0VCpxGrspxW0dZ3Ls1owB",
    	"endpoint": "https://health-apis.duke.edu/FHIR/patient/DSTU2/"
    	"user": {
                "subject": "123456789012345"
    			}
    	}
        ]
    }



Adding/Modifiing Addresses
==========================

* HTTP Method: `POST` (to create) `PUT` (to update)
* Request Body: application/json
* Response Body: application/json
* Endpoint:https://alpha.verifymyidentity.com/api/v1/user/[sub]/address/
* Authorization: OAuth2 Bearer Token

Addresses are physical addresses.  This works just like the other APIs/


Request
-------


    	{
        "formatted": "837 State St.\n Schenectady, NY 12307",
    	"street_address": "837 State St.",
    	"locality": "Schenectady",
    	"region": "NY",
    	"postal_code": "12307",
    	"country": "US"
    	}



Successful Response
-------------------

A successful response returns an `HTTP 200` :

    {
    "uid": "6ef4a89a-b520-4dab-be3e-e1b9e2f4d722",
    "formatted": "837 State St.\n Schenectady, NY 12307",
    "street_address": "837 State St.",
    "locality": "Schenectady",
    "region": "NY",
    "postal_code": "12307",
    "country": "US",
    "user": {
            "subject": 123456789012345
    		}
    }
    

