from mnemonic import Mnemonic


def generate_password_recovery_phrase():
    m = Mnemonic('english')
    mywords = m.generate(256)
    return "%s" % (mywords)
