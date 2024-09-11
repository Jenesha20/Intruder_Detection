# from detection import PersonDetection
# from notifications import Notification
# import os
# from dotenv import load_dotenv
# import argparse

# def main(capture_index):
#     # Load environment variables from .env file
#     load_dotenv()

#     # Retrieve environment variables
#     password = os.environ.get("INTRUSALERTS_PASSWORD")
#     from_email = os.environ.get("INTRUSALERTS_FROM_EMAIL")
#     to_email = os.environ.get("INTRUSALERTS_TO_EMAIL")

#     # Validate environment variables
#     if not password or not from_email or not to_email:
#         raise ValueError("Missing required environment variables. Check your .env file.")

#     # Instantiate Notification and PersonDetection classes
#     email_notification = Notification(from_email, to_email, password)
#     detector = PersonDetection(capture_index=capture_index, email_notification=email_notification)

#     # Start detection
#     detector()

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Run the person detection system.")
#     parser.add_argument('--capture_index', type=int, default=0, help='The index or IP address of the camera to be used for capture.')
#     args = parser.parse_args()

#     main(args.capture_index)

from detection import PersonDetection
from notifications import Notification
import os
from dotenv import load_dotenv
import argparse

def main(capture_index):
    load_dotenv()

    password = os.environ.get("INTRUSALERTS_PASSWORD")
    from_email = os.environ.get("INTRUSALERTS_FROM_EMAIL")
    to_email = os.environ.get("INTRUSALERTS_TO_EMAIL")

    if not password or not from_email or not to_email:
        raise ValueError("Missing required environment variables. Check your .env file.")

    email_notification = Notification(from_email, to_email, password)
    detector = PersonDetection(capture_index=capture_index, email_notification=email_notification)
    detector()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the person detection system.")
    parser.add_argument('--capture_index', type=int, default=0, help='The index or IP address of the camera to be used for capture.')
    args = parser.parse_args()

    main(args.capture_index)

