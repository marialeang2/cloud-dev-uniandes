class APIException(Exception):
    """Base exception for API errors"""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.detail)


class ValidationException(APIException):
    """Exception for validation errors"""
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)


class NotFoundException(APIException):
    """Exception for resource not found"""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)


class DuplicateException(APIException):
    """Exception for duplicate resources"""
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)


class UnauthorizedException(APIException):
    """Exception for unauthorized access"""
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=401, detail=detail)


class ForbiddenException(APIException):
    """Exception for forbidden access"""
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=403, detail=detail)

