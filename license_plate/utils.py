# utils.py
import cv2
import numpy as np
import pytesseract
import os

def detect_license_plate(frame, save_path):
    # Load Haar cascade for license plate detection
    plate_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_russian_plate_number.xml')

    # Convert the frame to grayscale for Haar cascade
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect license plates in the frame
    plates = plate_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(25, 25))

    # Create a mask for highlighting changes in consecutive frames
    mask = np.zeros_like(gray_frame)

    # Iterate through detected plates
    for (x, y, w, h) in plates:
        # Extract the region of interest (ROI) containing the license plate
        plate_roi = frame[y:y+h, x:x+w]

        # Save the plate ROI as an image
        plate_filename = os.path.join(save_path, 'plate_{}_{}.png'.format(x, y))
        cv2.imwrite(plate_filename, plate_roi)

        # Use Tesseract OCR to extract text from the license plate
        text = pytesseract.image_to_string(plate_roi, config='--psm 8')

        # Draw a rectangle around the detected license plate
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # Add text annotation to the frame
        cv2.putText(frame, "Plate: {}".format(text), (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Highlight changes in the mask for the region of detected plate
        mask[y:y+h, x:x+w] = 255

    # Create a color frame by adding the highlighted changes to the original frame
    color_frame = cv2.addWeighted(frame, 1, cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR), 0.5, 0)

    return color_frame

def get_plate_number(frame_with_plate, previous_frame=None):
    if previous_frame is None:
        # Handle the case where the previous_frame is not provided
        return None

    # Convert the frame to grayscale
    prev = cv2.cvtColor(prvs, cv2.COLOR_BGR2GRAY)

    # Calculate optical flow between consecutive frames using Farneback method
    flow = cv2.calcOpticalFlowFarneback(prev, next, previous_frame, 0.5, 3, 15, 3, 5, 1.2, 0)

    # Compute the magnitude and angle of the 2D vectors
    mag, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])

    # Normalize the magnitude to fit into the range [0, 255]
    mag = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)

    # Convert the magnitude to uint8 type
    mag = np.uint8(mag)

    # Threshold the magnitude to get binary motion mask
    _, motion_mask = cv2.threshold(mag, 10, 255, cv2.THRESH_BINARY)

    # Convert the motion mask to three channels
    motion_mask_rgb = cv2.cvtColor(motion_mask, cv2.COLOR_GRAY2BGR)

    # Combine the original frame with the motion mask
    result_frame = cv2.addWeighted(frame_with_plate, 0.7, motion_mask_rgb, 0.3, 0)

    return result_frame

