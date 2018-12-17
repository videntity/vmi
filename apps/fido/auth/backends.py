User = get_user_model()

class FIDO2Backend:
    def authenticate(self, request, **credentials):
        data = cbor.loads(request.get_data())[0]
        credential_id = data['credentialId']
        credentials = Credential.objects.filter(credential_id=credential_id).all()
        client_data = ClientData(data['clientDataJSON'])
        auth_data = AuthenticatorData(data['authenticatorData'])
        signature = data['signature']

        cred = server.authenticate_complete(
            request.session.pop('state'),
            credentials,
            credential_id,
            client_data,
            auth_data,
            signature
        )
        return cred.user

    def get_user(user_id):
        return User.objects.get(user_id)
