
# views.py
from django.shortcuts import render
from django.conf import settings
from .models import Video
from .utils import detect_license_plate, get_plate_number
from uuid import uuid4
import os
import cv2
import numpy as np
import pytesseract
import time

# Specify the path to the Tesseract OCR executable (update this path based on your installation)
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

def index(request):
    return render(request, 'license_plate/index.html')

def upload_video(request):
    try:
        max_frames = 100
        if request.method == 'POST':
            uploaded_file = request.FILES['file']
            video = Video(video_file=uploaded_file)
            video.save()

            video_path = os.path.join(settings.MEDIA_ROOT, video.video_file.name)

            frames_with_plate = []
            image_save_path = os.path.join(settings.MEDIA_ROOT, 'images')  
            os.makedirs(image_save_path, exist_ok=True)

            cap = cv2.VideoCapture(video_path)
            ret, previous_frame = cap.read() # Read the first frame
            height, width, _ = previous_frame.shape # Get the dimensions of the first frame

            frame_count = 0 # Add this line to initialize the frame_count variable

            while frame_count < max_frames:
                success, frame = cap.read()

                if not success:
                    break

                # Resize frame to a common size
                frame = cv2.resize(frame, (width, height))

                # Check if the dimensions match
                if frame.shape != previous_frame.shape:
                    print("Warning: Frame dimensions do not match. Skipping current frame.")
                    continue

                # Detect license plates and draw on the frame
                frame_with_plate = detect_license_plate(frame, save_path=image_save_path)

                # Highlight changes between consecutive frames
                color_frame = cv2.absdiff(frame, previous_frame)

                # Update the previous frame for the next iteration
                previous_frame = frame.copy()

                # Combine the original frame with the highlighted changes
                result_frame = cv2.addWeighted(frame, 0.7, color_frame, 0.3, 0)

                # Check if the plate number is already captured
                plate_number = get_plate_number(frame_with_plate, previous_frame=previous_frame)
                if plate_number and plate_number not in frames_with_plate:
                    frames_with_plate.append(plate_number)

                    # Generate the filename based on the plate number
                    filename = f"plate-{plate_number}.png"
                    file_path = os.path.join(image_save_path, filename)

                    # Save the frame with the generated filename
                    cv2.imwrite(file_path, result_frame)

                frame_count += 1 # Increment the frame_count variable at the end of each iteration

                # Add a delay to avoid excessive processing
                time.sleep(0.1)

            cap.release()

            # Print or log the frames_with_plate variable
            print("Frames with Unique Plate Numbers:")
            print(frames_with_plate)

            rel_video_path = os.path.relpath(video_path, settings.MEDIA_ROOT)
            rel_image_paths = [os.path.relpath(os.path.join(image_save_path, f"plate-{plate}.png"), settings.MEDIA_ROOT) for plate in frames_with_plate]

            return render(request, 'license_plate/index.html', {
                'video_path': rel_video_path,
                'frames_with_plate': rel_image_paths,
            })

    except Exception as e:
        error_message = str(e)
        print("An error occurred: {}".format(error_message))
        return render(request, 'license_plate/index.html', {'video_path': video_path, 'frames_with_plate': frames_with_plate})
    else:
        return render(request, 'license_plate/index.html')


