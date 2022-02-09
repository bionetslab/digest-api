from application import setup as digest_setup


def setup(self):
    print("starting setup!")
    digest_setup.__main__


def check(self):
    print("checking")
    if True:
        setup(self)

def clear(self):
    pass