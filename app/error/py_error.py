from typing import Optional, Dict
from pydantic import BaseModel
import json


class BaseResponse(BaseModel):
    api_response_code: int
    message: str
    version: Optional[str] = None


class PyError(Exception):
    INTERNAL_ERROR = 5000
    FORBIDDEN = 4003
    AUTHORIZATION = 4001
    BADREQUEST = 4000
    RESOURCE_NOT_FOUND = 4004

    error_response: BaseResponse

    def __init__(
        self,
        error_response: BaseResponse,
        message: str = "",
        ex: Optional[Exception] = None,
    ):
        full_message = f"{message} && {str(ex)}" if ex else message
        super().__init__(full_message)
        self.error_response = error_response

    @staticmethod
    def get_error_mapping(api_response_code: int) -> Dict:
        error_mappings = {
            PyError.INTERNAL_ERROR: {
                "status_code": 500,
                "message": "Internal Server Error",
            },
            PyError.FORBIDDEN: {"status_code": 403, "message": "Forbidden Error"},
            PyError.AUTHORIZATION: {
                "status_code": 401,
                "message": "Authorization Error",
            },
            PyError.BADREQUEST: {"status_code": 400, "message": "Bad Request"},
            PyError.RESOURCE_NOT_FOUND: {
                "status_code": 404,
                "message": "Resource Not Found",
            },
        }
        return error_mappings.get(
            api_response_code, {"status_code": 500, "message": "Unknown Error"}
        )

    def __str__(self):
        return json.dumps(self.error_response.dict())

    def to_action_result(self) -> Dict:
        error_mapping = PyError.get_error_mapping(self.error_response.api_response_code)
        return {
            "status_code": error_mapping["status_code"],
            "message": self.error_response.message,
        }
