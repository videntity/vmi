
class AuthenticationRequired(Exception):
    def __init__(self, n):
        self.next = n
