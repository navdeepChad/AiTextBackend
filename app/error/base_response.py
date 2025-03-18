class BaseResponse:
    def __init__(self, api_response_code: int, message: str):
        self.api_response_code = api_response_code
        self.message = message
