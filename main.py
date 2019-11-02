# -*- coding:UTF-8 -*-

import os

import cv2
import face_recognition
import numpy as np
from pymongo import MongoClient
from uuid import uuid1

client = MongoClient('mongodb://*****:******@**.**.**.**:*****/*****')
db = client.face
face_encodings = db.face_encodings
login_log = db.login_log


def make_1080p(cap):
    cap.set(3, 1920)
    cap.set(4, 1080)


def make_720p(cap):
    cap.set(3, 1280)
    cap.set(4, 720)


def make_480p(cap):
    cap.set(3, 640)
    cap.set(4, 480)


def start_monitor(universal_confirmation_time, universal_process_frequency, resolution, known_face_key_ids, known_face_labels,
                  known_face_encodings, known_face_grade, register=False, register_pack=None):
    register_bar = [universal_confirmation_time, universal_confirmation_time]
    user_confirmation_time = dict()
    for index, name in enumerate(known_face_labels):
        user_confirmation_time[name] = [universal_confirmation_time, universal_confirmation_time]
        if not register:
            for log in login_log.find({'parent_key_id': known_face_key_ids[index]}):
                pass

    video_capture = cv2.VideoCapture(0)
    resolution(video_capture)
    process_times = universal_process_frequency
    face_locations, face_names, face_grade = [], [], []
    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every universal_process_frequency frame of video to save time
        if process_times == 0:
            face_locations, face_names, face_grade = process_face(frame, rgb_small_frame, known_face_labels,
                                                                  known_face_encodings, known_face_grade)
            process_times = universal_process_frequency
        else:
            process_times -= 1

        if not display_results(frame, face_locations, face_names, face_grade, user_confirmation_time, register, register_bar,
                        register_pack, universal_confirmation_time):
            break

        # Display the resulting image
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()


def process_face(frame, rgb_small_frame, known_face_labels, known_face_encodings, known_face_grade):
    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(rgb_small_frame)
    onscreen_face_data = face_recognition.face_encodings(rgb_small_frame, face_locations)

    face_names = []
    face_grade = []
    if len(known_face_grade) != 0:
        for face in onscreen_face_data:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face, tolerance=0.4)
            name = "Unknown, Please run register"
            grade = str()

            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(known_face_encodings, face)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_labels[best_match_index]
                grade = known_face_grade[best_match_index]
            face_names.append(name)
            face_grade.append(grade)
    else:
        face_names = ["Unknown, Please run register"]*len(face_locations)
        face_grade = [0]*len(face_locations)
    return face_locations, face_names, face_grade


def display_results(frame, face_locations, face_names, face_grade, confirmation_bar, register, register_bar,
                    register_pack, universal_confirmation_time):
    # Display the results
    for (top, right, bottom, left), name, grade in zip(face_locations, face_names, face_grade):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        # Draw a label with a name below the face
        change = (right - left) / 248
        font = cv2.FONT_HERSHEY_DUPLEX
        if register:
            if 'register' in name:
                cv2.rectangle(frame, (left, bottom - int(35 * change)), (
                    int(left + (right - left) * register_bar[0] / register_bar[1]), bottom),
                              (0, 0, 255), cv2.FILLED)
                if len(face_locations) > 1:
                    cv2.putText(frame, 'Please Make Sure Only One Person is in the Frame',
                                (left + int(6 * change), bottom - int(6 * change)), font, change, (255, 255, 255), 1)
                else:
                    cv2.putText(frame, 'Creating User', (left + int(6 * change), bottom - int(6 * change)), font, change,
                                (255, 255, 255), 1)
                    register_bar[0] -= 1
                    if register_bar[0] == 0:
                        cv2.imwrite('./temp.jpg', frame)
                        register_to_db(register_pack[0], register_pack[1], './temp.jpg')
                        os.remove('./temp.jpg')
                        return False, None
            else:
                cv2.rectangle(frame, (left, bottom - int(35 * change)), (right, bottom), (0, 0, 255), cv2.FILLED)
                cv2.putText(frame, 'User Exists: ' + name, (left + int(6 * change), bottom - int(6 * change)), font,
                            change, (255, 255, 255), 1)
        else:
            cv2.rectangle(frame, (left, bottom - int(35 * change)), (right, bottom), (0, 0, 255), cv2.FILLED)
            cv2.putText(frame, name, (left + int(6 * change), bottom - int(6 * change)), font, change, (255, 255, 255),
                        1)
            if 'register' not in name:
                cv2.rectangle(frame, (left, bottom), (right, bottom + int(35 * change)), (0, 0, 255), cv2.FILLED)
                cv2.putText(frame, grade, (left + int(6 * change), bottom + int(29 * change)), font, change,
                            (255, 255, 255), 1)
                cv2.rectangle(frame, (left, bottom + int(35 * change)), (right, bottom + int(70 * change)), (0, 0, 255),
                              2)
                if confirmation_bar[name][0] != 0:
                    cv2.rectangle(frame, (left, bottom + int(35 * change)),
                                  (int(left + (right - left) * confirmation_bar[name][0] / confirmation_bar[name][1]),
                                   bottom + int(70 * change)),
                                  (0, 0, 255), cv2.FILLED)
                    cv2.putText(frame, 'Authenticating', (left + int(6 * change), bottom + int(64 * change)), font, change,
                                (255, 255, 255), 1)
                    confirmation_bar[name][0] -= 1
                else:
                    cv2.putText(frame, 'Authenticated', (left + int(6 * change), bottom + int(64 * change)), font,
                                change / 1.5, (255, 255, 255), 1)
                    confirmation_bar[name][0] = universal_confirmation_time
                    return False, name
    return True, None


def get_data_from_db(face_encodings):
    known_face_key_ids = []
    known_face_encodings = []
    known_face_labels = []
    known_face_grade = []
    for i in face_encodings:
        known_face_encodings.append(i['encoding'])
        known_face_labels.append(i['name'])
        known_face_grade.append(i['grade'])
        known_face_key_ids.append(i['key_id'])
    return known_face_key_ids, known_face_labels, known_face_encodings, known_face_grade


def register_to_db(name, grade, image_path):
    # converting face to face encoding
    img = face_recognition.load_image_file(image_path)
    faces = face_recognition.face_encodings(img)
    if len(faces) != 1:
        return 'Cannot Perform Action, Multiple Faces Detected'
    face_encoding = list(faces[0])
    # uploading data to database
    key_id = str(uuid1())
    print(key_id, name, grade, face_encodings)
    face_encodings.insert_one({'key_id': key_id, 'name': name, 'grade': grade, 'encoding': face_encoding})


# def register_interface():

# def welcome_interface():

if __name__ == "__main__":
    # begin interface
    confirmation_time = 50
    process_frequency = 2
    known_face_key_ids, known_face_labels, known_face_encodings, known_face_grade = get_data_from_db(face_encodings.find())
    start_monitor(confirmation_time, process_frequency, make_480p, known_face_key_ids, known_face_labels,
                  known_face_encodings, known_face_grade, True, register_pack=['X', 'Freshmen'])
