from mysql.connector.pooling import MySQLConnectionPool
import bcrypt
from cryptography import fernet


class Database:
    def __init__(self, host: str, user: str, password: str, database: str, encryption_key: str):
        self.pool = MySQLConnectionPool(
            pool_name="mypool",
            pool_size=10,
            host=host,
            user=user,
            password=password,
            database=database,
            autocommit=True
        )
        self.fernet: fernet.Fernet = fernet.Fernet(encryption_key.encode())
    

    def get_connection(self):
        return self.pool.get_connection()


    def login(self, email: str, password: str) -> bool:
        query = """
            SELECT users.password
            FROM users
            WHERE users.email = %s
        """
        conn = self.get_connection()

        cursor = conn.cursor()
        cursor.execute(query, [email])
        result = cursor.fetchone()
        cursor.close()

        conn.close()

        encoded_password = password.encode("utf-8")
        retreived_password = result[0].encode("utf-8")

        if bcrypt.checkpw(encoded_password, retreived_password):
            return True
        
        return False
    

    def sign_up(self, email: str, username: str, password: str) -> dict:
        query = """
            INSERT INTO users (email, username, password)
            VALUES (%s, %s, %s)
        """

        encoded_password = password.encode("utf-8")

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(encoded_password, salt)

        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute(query, [email, username, hashed_password])
                cursor.close()
                conn.close()
                return {"OK": True}
            
            except:
                cursor.close()
                conn.close()
                return {"OK": False, "ERROR": "Email or username in use"}
        
        except:
            conn.close()
            return {"OK": False, "ERROR": "Connection error"}
    

    def track(self, email: str, game_id: int, status: str, score: int, favourite: bool, comment: str) -> dict:
        query = """
            INSERT INTO tracked_games (game_id, user_email, status, score, favourite, comment)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            try:
                cursor.execute(query, [email, game_id, status, score, favourite, comment])
                cursor.close()
                conn.close()
                return {"OK": True}
            
            except:
                cursor.close()
                conn.close()
                return {"OK": False, "error": "Invalid email or game id"}
        
        except:
            try:
                conn.close()
                cursor.close()
            except:
                return {"OK": False, "error": "Error establishing connection."}

            return {"OK": False, "error": "Error establishing connection."}
    

