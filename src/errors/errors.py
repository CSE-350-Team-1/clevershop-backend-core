class InitError(Exception):
    """Exception raised in case of server initialization failure"""

    def __init__(self, message="Server initialization failed"):
        super().__init__(message)



class ShutDownError(Exception):
    """Exception raised in case of server shutdown error"""

    def __init__(self, message = "Server shutdown error"):
        super().__init__(message)



class AuthorizationError(Exception):
    """Exception raised in case of authorization middleware failure"""
    def __init__(self, message = "Authorization middleware failed"):
        super().__init__(message)



class DBError(Exception):
    """Exception raised in case of database failure"""
    def __init__(self, message = "Database query failed"):
        super().__init__(message)