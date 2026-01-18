import firebase_admin
from firebase_admin import credentials, messaging

_firebase_app = None

def init_firebase():
    global _firebase_app
    if not _firebase_app:
        cred = credentials.Certificate("secrets/firebase-admin.json")
        _firebase_app = firebase_admin.initialize_app(cred)

def send_fcm(token: str, title: str, body: str):
    init_firebase()

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,
    )

    response = messaging.send(message)
    return response
