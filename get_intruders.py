import sqlite3
import cv2
import os
import numpy as np  # Import numpy as np

def get_intruders():
    # Connect to the SQLite database
    conn = sqlite3.connect('intruder_log.db')
    cursor = conn.cursor()

    # Query to select data from the database
    cursor.execute('SELECT id, track_id, timestamp, image FROM intruders ORDER BY timestamp')

    # Fetch all records
    records = cursor.fetchall()

    # Ensure the images directory exists
    if not os.path.exists('retrieved_images'):
        os.makedirs('retrieved_images')

    # Process each record
    for record in records:
        intruder_id, track_id, timestamp, image_blob = record

        # Convert the image blob back to an image
        nparr = np.frombuffer(image_blob, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Save the image with a unique name
        image_path = os.path.join('retrieved_images', f'intruder_{intruder_id}_{timestamp}.jpg')
        cv2.imwrite(image_path, img)

        print(f"Saved image for intruder {intruder_id} at {timestamp}")

    conn.close()

if __name__ == "__main__":
    get_intruders()
