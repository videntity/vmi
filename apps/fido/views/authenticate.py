
@api_view(['POST'])
def begin(request):
    auth_data, state = server.authenticate_begin(credentials)
    request.session['state'] = state
    return Response(cbor.dump_dict(auth_data))

@api_view(['POST'])
def complete(request):
    # requires fido authentication backend
    user = authenticate(request)
    if user is not None:
        login(request, user)
    raise PermissionDenied
