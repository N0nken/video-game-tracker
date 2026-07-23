import requests
import time


def sign_up():
    x = requests.post("http://127.0.0.1:5000/auth/sign_up", json={"email": "test@email.tld", "username": "test_user", "password": "test_pass"})

    print(x.text)


def login():
    x = requests.post("http://127.0.0.1:5000/auth/login", json={"email": "test@email.tld", "password": "test_pass"})

    print(x.text)


def track():
    pass


if __name__ == "__main__":
    login()