class SomOfficeUserError(Exception):
    def __init__(self, ref, msg):
        super(SomOfficeUserError, self).__init__("""
            Error {} the SomOffice user of Partner Ref {}.
            Error message: {}
            """.format(self.action, ref, msg)
        )


class SomOfficeUserCreationError(SomOfficeUserError):
    action = "creating"


class SomOfficeUserChangeEmailError(SomOfficeUserError):
    action = "changing email"
