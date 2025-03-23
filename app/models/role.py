from enum import Enum


class Role(Enum):
    UNKNOWN = "Unknown"
    ADMIN = "Admin"
    USER = "User"

    def __str__(self):
        return self.value
