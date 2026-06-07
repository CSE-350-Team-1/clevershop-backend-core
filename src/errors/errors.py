class InitError(Exception):
    """Exception raised in case of server initialization failure"""

    def __init__(self, message="Server initialization failed"):
        super().__init__(message)
