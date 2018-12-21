
class VerificationRequired(Exception):
    def __init__(self, n):
        self.next = n
