from multiprocessing import Pipe
from pathlib import Path
import face_recognition
import cv2
import os


#Processes an image of a person and encodes the face of the person
def encode_faces(image):
    #Returns a list of tuples of found face locations in css (top, right, bottom, left) order
    face_location = face_recognition.face_locations(image, number_of_times_to_upsample=1, model='hog')

    #Given an image, returns a list of 128-dimensional face encodings (one for each face in the image)
    face_encoding = face_recognition.face_encodings(image, known_face_locations=face_location, num_jitters=1)

    return face_encoding


# Converts images of faces into an array of values and associates them with the person's name
def allowed_people(image_file_name):

    image_file_folder = Path("/home/pi/Desktop/facelock")

    #Loads an image file into a numpy array
    allowed_person_image = face_recognition.load_image_file(image_file_folder / image_file_name)

    allowed_person_face_encoding = encode_faces(allowed_person_image)

    return allowed_person_face_encoding


def face_rec(child_connection, allowed_people_face_encodings, allowed_people_names):

    # Open the Raspberry Pi camera
    camera = cv2.VideoCapture(0)

    process_frame = True

    # Returns true if previous call to VideoCapture constructor succeeded
    while camera.isOpened():
        
        person = "This person is not allowed to access the chest."
        
        # Grabs, encodes and returns the next video frame
        # retval == false if camera has been disconnected.
        # image is the encoded frame that was grabbed
        retval, encoded_frame = camera.read()
        
        if process_frame: 
            video_face_encoding = encode_faces(encoded_frame)

            # Loop through each face in this frame of video
            for face_encoding in video_face_encoding:
                # See if the face in the camera is a match for the known face(s)
                comparison = face_recognition.compare_faces(allowed_people_face_encodings, face_encoding, tolerance=0.6)
                
                # If a match was found in allowed_people_face_encodings, assign the person's name to 'person'.
                if True in comparison:
                    comparison_index = comparison.index(True)
                    person = allowed_people_names[comparison_index]

                # Send the person's name or the default value for person (if the person does not have access) back to the main process
                child_connection.send(person)
        
        process_frame = not process_frame

        # In case we want to display the video stream on a screen
        cv2.imshow('Screen', encoded_frame)

        # hit esc to quit
        if cv2.waitKey(1) == 27:
            break

    child_connection.close()
    camera.release()
    cv2.destroyAllWindows()


def start_face_recognition_process(allowed_people_face_encodings, allowed_people_names):
    parent_connection, child_connection = Pipe()
    
    PID = os.fork()

    if PID < 0:
        print ('Creation of child process for facial recognition was unsuccessful.')
    
    # child process just performs facial recogntion
    elif PID == 0:
        print('Running child process for facial recognition.')
        face_rec(child_connection, allowed_people_face_encodings, allowed_people_names,)
        
    # main process will run keypad code and servo motor code
    else:
        # Receive the name of the person from the child process
        person = parent_connection.recv()
        print(person)
        password = input('Please enter the password: ')
        correct_password = '12345'

        while (password != correct_password):
            password = input('Please try entering the password again: ')
        
        if person in allowed_people_names:
            print('Access granted to ' + person)
            
            #PUT MOTOR CODE TO UNLOCK THE BOX HERE

        else:
            print('Access not granted.')


def main():
    
    kailyn_face_encoding = allowed_people('kailyn.jpg')[0]
    majumder_face_encoding = allowed_people('majumder.jpg')[0]
    
    allowed_people_face_encodings = [
        kailyn_face_encoding,
        majumder_face_encoding
    ]
    
    allowed_people_names = [
        'Kailyn Williams',
        'AKM Majumder'
    ]
    
    start_face_recognition_process(allowed_people_face_encodings, allowed_people_names)


if __name__ == '__main__':

    main()
