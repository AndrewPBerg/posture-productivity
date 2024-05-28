# gui_functions.py
import cv2
import PySimpleGUI as sg
import mediapipe as mp
from posture_boolean import is_standing, is_hand_raised
from pose_landmark_utils import output_values
# import numpy as np

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# print(mp_pose.POSE_CONNECTIONS)

def webcam_gui():
    # Define the layout of the window
    layout = [
        [sg.Image(filename='', key='image')],
        [sg.Text("Hand Raised: "), sg.Text("", key='hand_raised_text')],
        [sg.Text("Is Standing: "), sg.Text("", key='is_standing_text')],
        [sg.Button("shoulders x,y,z", key='xyz')],
        [sg.Text("Left shoulder"), sg.Text("", key='left_shoulder_xyz')],
        [sg.Text("Right shoulder"), sg.Text("", key='right_shoulder_xyz')]
    ]

    # Create the window
    window = sg.Window('Webcam Window', layout, location=(800, 400))

    # Open the webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Unable to access the camera")
        return

    OUTPUT_LANDMARKS = [mp_pose.PoseLandmark.LEFT_SHOULDER,
                        mp_pose.PoseLandmark.RIGHT_SHOULDER,
                        mp_pose.PoseLandmark.MOUTH_RIGHT,
                        mp_pose.PoseLandmark.MOUTH_LEFT]

    # Main loop
    while True:
        ret, frame = cap.read()
        # Convert the image to RGB
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the image and detect poses
        results = pose.process(image_rgb)

        # Draw the pose annotation on the image
        annotated_image = frame.copy()
        event, values = window.read(timeout=20)
        if event == sg.WINDOW_CLOSED:
            break
        elif event == 'xyz':
            output_values(results.pose_landmarks, OUTPUT_LANDMARKS)
            window['left_shoulder_xyz'].update()
        if not ret:
            print("Error: Failed to capture image")
            break

        if results.pose_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(
                annotated_image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # Check if hand is raised
        hand_raised = is_hand_raised(results.pose_landmarks)

        # Check if the person is standing
        standing = is_standing(results.pose_landmarks)

        

        # Update GUI
        imgbytes = cv2.imencode('.png', annotated_image)[1].tobytes()
        window['image'].update(data=imgbytes)
        window['hand_raised_text'].update("Yes" if hand_raised else "No")
        window['is_standing_text'].update("Yes" if standing else "No")

    # Release the webcam and close the window
    cap.release()
    window.close()


def main():
    webcam_gui()
# Run the function
if __name__ == "__main__":
    main()