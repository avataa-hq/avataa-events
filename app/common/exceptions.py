class CommonException(Exception):
    def __init__(self, detail, status_code=None):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class NotAvailableInstanceType(CommonException):
    pass


class TokenIsNotValid(CommonException):
    pass
