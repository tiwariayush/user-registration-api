from fastapi import HTTPException, status

class EmailAlreadyUsed(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT, 
            detail={
                "error": "EMAIL_ALREADY_USED",
                "message": "Email already registered.",
                "code": "DM_REG_001"
            }
        )

class InvalidCredentials(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail={
                "error": "INVALID_CREDENTIALS",
                "message": "Invalid email or password.",
                "code": "DM_REG_002"
            }
        )

class CodeExpired(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail={
                "error": "CODE_EXPIRED",
                "message": "Activation code expired.",
                "code": "DM_REG_003"
            }
        )

class InvalidCode(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail={
                "error": "INVALID_CODE",
                "message": "Invalid activation code.",
                "code": "DM_REG_004"
            }
        )

class AlreadyActive(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT, 
            detail={
                "error": "ALREADY_ACTIVE",
                "message": "Account already active.",
                "code": "DM_REG_005"
            }
        )
