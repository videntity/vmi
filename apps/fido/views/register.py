
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def begin(request):
    registration_data, state = server.register_begin({
        'id': b'user_id',
        'name': 'a_user',
        'displayName': 'A. User',
        'icon': 'https://example.com/image.png'
    }, credentials)
    request.session['state'] = state
    return Response(cbor.dump_dict(registration_data))

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def complete(request):
    data = cbor.loads(request.get_data())[0]
    client_data = ClientData(data['clientDataJSON'])
    att_obj = AttestationObject(data['attestationObject'])

    auth_data = server.register_complete(
        request.session['state'],
        client_data,
        att_obj
    )

    Credential.objects.create(auth_data.credential_data)
    return Response({'status': 'OK'})
