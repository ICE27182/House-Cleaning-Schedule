

import json
from os.path import exists
from datetime import datetime

class Admins:
    LOG_PATH = "admins_log.txt"
    def __init__(self, passkeys_path:str):
        with open(passkeys_path, "r") as f:
            self.passkeys: dict[str, str] = json.load(f)
        if not exists(Admins.LOG_PATH):
            with open(Admins.LOG_PATH, "w") as f:
                f.write("")
    
    def validate_passkey(self, passkey: str) -> None | str:
        """
        Validate the passkey.
        """
        return self.passkeys[passkey] if passkey in self.passkeys else None
    
    def log(self, passkey: str, message: str) -> None:
        """"
        Log the admin operation.
        """
        if passkey not in self.passkeys:
            raise ValueError("Invalid passkey")
        admin_name = self.passkeys[passkey]
        with open(Admins.LOG_PATH, "a") as f:
            f.write(f"{datetime.now()} - {admin_name:20} - {message}\n")
