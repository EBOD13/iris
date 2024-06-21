# import threading
# import cv2
# import face_recognition
# import os
# 
# # Initialize the camera
# cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# 
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
# 
# counter = 0
# face_match = False
# 
# # Directory containing reference images
# reference_dir = "C:/Users/oleka/OneDrive/Desktop/iris/data/images/faces"
# 
# # Verify that the directory exists
# if not os.path.exists(reference_dir):
#     print(f"Directory {reference_dir} does not exist.")
#     exit()
# 
# # Load all reference images and encode faces
# reference_encodings = []
# for img_name in os.listdir(reference_dir):
#     if img_name.endswith(('.png', '.jpg', '.jpeg')):
#         img_path = os.path.join(reference_dir, img_name)
#         image = face_recognition.load_image_file(img_path)
#         encoding = face_recognition.face_encodings(image)
#         if encoding:
#             reference_encodings.append(encoding[0])
# 
# if not reference_encodings:
#     print("No reference images with identifiable faces found in the directory.")
#     exit()
# 
# def check_face(frame, reference_encodings):
#     global face_match
#     try:
#         # Find face encodings in the current frame
#         face_encodings = face_recognition.face_encodings(frame)
# 
#         # Check each face found in the frame against the reference encodings
#         face_match = any(face_recognition.compare_faces(reference_encodings, face_encoding) for face_encoding in face_encodings)
#     except Exception as e:
#         face_match = False
#         print(f"Error in face recognition: {e}")
# 
# while True:
#     ret, frame = cap.read()
# 
#     if ret:
#         if counter % 30 == 0:
#             try:
#                 threading.Thread(target=check_face, args=(frame.copy(), reference_encodings)).start()
#             except ValueError:
#                 pass
#         counter += 1
# 
#         if face_match:
#             cv2.putText(frame, "MATCH", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
#         else:
#             cv2.putText(frame, "NO MATCH", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
# 
#         cv2.imshow("Face Check", frame)
# 
#     key = cv2.waitKey(1)
#     if key == ord("q"):
#         break
# 
# cv2.destroyAllWindows()
# cap.release()

import face_recognition
import cv2
import numpy as np

# This is a demo of running face recognition on live video from your webcam. It's a little more complicated than the
# other example, but it includes some basic performance tweaks to make things run a lot faster:
#   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
#   2. Only detect faces in every other frame of video.

# PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
# OpenCV is *not* required to use the face_recognition library. It's only required if you want to run this
# specific demo. If you have trouble installing it, try any of the other demos that don't require it instead.

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

# Load a sample picture and learn how to recognize it.
daniel_image = face_recognition.load_image_file("C:/Users/oleka/OneDrive/Desktop/iris/data/images/faces/Me.png")
daniel_face_encoding = face_recognition.face_encodings(daniel_image)[0]

# Create arrays of known face encodings and their names
known_face_encodings = [
    daniel_face_encoding,
]
known_face_names = [
    "Daniel",
]

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Only process every other frame of video to save time
    if process_this_frame:
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            face_names.append(name)

    process_this_frame = not process_this_frame


    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()