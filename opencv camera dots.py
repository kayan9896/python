import cv2
import numpy as np

# Initialize the video capture (0 for the default camera, or try 1, 2... for external devices)
# If using HDMI/USB capture cards, you may need to specify the appropriate index
cap = cv2.VideoCapture(0)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open video stream or file")
    exit()

while True:
    # Capture frame-by-frame from the external device
    ret, frame = cap.read()
    
    # If the frame is not captured correctly, break the loop
    if not ret:
        print("Failed to grab frame")
        break

    # Convert the frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply a threshold to create a binary image
    _, thresh = cv2.threshold(gray_frame, 0, 55, cv2.THRESH_BINARY)

    # Optionally, apply a GaussianBlur to reduce noise
    blurred = cv2.GaussianBlur(thresh, (5, 5), 0)

    # Find contours (simple approximation method)
    contours, _ = cv2.findContours(blurred, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # List to store the coordinates of the spots
    spot_coordinates = []

    # Loop through contours
    for contour in contours:
        # Calculate the moments to find the centroid of the spot
        M = cv2.moments(contour)
        
        if M['m00'] != 0:
            # Centroid coordinates
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            spot_coordinates.append((cx, cy))
        
            # Draw a circle at the centroid for visualization
            cv2.circle(frame, (cx, cy), 5, (0, 55, 0), -1)

    # Display the resulting frame with detected spots marked
    cv2.imshow('Detected Spots', frame)
    print(spot_coordinates)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close windows
cap.release()
cv2.destroyAllWindows()
