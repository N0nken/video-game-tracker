import jwt
import time


class TokenManager:
    def __init__(self, secret_key: str, algorithm: str, token_type: str):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_type = token_type


    def issue_token(self, expiration: int, user_id: str, scope: int) -> str:
        header = {
            "alg": self.algorithm,
            "typ": self.token_type
        }

        payload = {
            "user_scope": scope,
            "user_id": user_id,
            "exp": time.time() + expiration
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm, headers=header)

        return token
    

    def verify_token(self, token: str) -> dict:
        try:
            decoded = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return {"OK": True, "token": decoded}
        except jwt.ExpiredSignatureError:
            return {"OK": False, "content": "Token expired"}
        except jwt.InvalidTokenError:
            return {"OK": False, "content": "Invalid token"}
    

    def get_user_id(self, token: dict) -> str:
        return token["user_id"]