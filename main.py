# main.py

from PySimpleGUI import running_mac,running_windows
# from  gui_functions import webcam_gui
import cv2
import PySimpleGUI as sg
import mediapipe as mp
# from posture_boolean import is_standing, is_hand_raised
from pose_landmark_utils import get_landmark_coordinates
from posture_calculations import findAngle, findDistance
from icecream import ic
import warnings
# suppresses a near dated mediapipe dependency
warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf")



def main():
    # =============================CONSTANTS and INITIALIZATIONS=====================================#
    
    # in seconds, determine how long a user must have a bad posture until a notification
    POSTURE_WARNING_TIME = 2

    # accesses mediapipe pose estimation solutions 
    mp_pose = mp.solutions.pose

    # Instantiate pose estimater
    pose = mp_pose.Pose()

    # sg Windows element layout
    layout = [
        [sg.Image(filename='', key='image')],
    ]

    # TODO Sunset feature
    REQ_LANDMARKS = [mp_pose.PoseLandmark.LEFT_SHOULDER,
                        mp_pose.PoseLandmark.RIGHT_SHOULDER,
                        mp_pose.PoseLandmark.LEFT_EAR,
                        mp_pose.PoseLandmark.LEFT_HIP]

    # Initilize frame counters.
    good_frames = 0
    bad_frames = 0

    # Font type.
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Colors.
    # blue = (255, 127, 0)
    red = (50, 50, 255)
    green = (127, 255, 0)
    # dark_blue = (127, 20, 0)
    light_green = (127, 233, 100)
    yellow = (0, 255, 255)
    pink = (255, 0, 255)

    # Open the webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Unable to access the camera")
        return

    # Meta.
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_size = (width, height)
    
    # Instantiate sg window
    window = sg.Window('Webcam Window', layout, location=(width,height), resizable=True, size=(width*2,height*2))
    # ===============================================================================================#

    # Main loop
    while True:
        success, image = cap.read()
        if not success:
            ic("Error reading image")
            break

        # Get fps.
        fps = cap.get(cv2.CAP_PROP_FPS)
        # Get height and width.
        h, w = image.shape[:2]

        # Convert the image from BGR to RGB --- MEDIAPIPE REQUIREMENT!!!
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Process the image and detect poses
        results = pose.process(image)

        # Convert image back to BGR for better image visibility
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        # Draw the pose annotation on the image
        # annotated_image = image.copy()
        event, values = window.read(timeout=20)

        if event == sg.WINDOW_CLOSED:
            break

        # Use lm and lmPose as representative of the following methods.
        lm = results.pose_landmarks
        lmPose = mp_pose.PoseLandmark

        # Calculate posture
        l_shldr_x, l_shldr_y = get_landmark_coordinates(lm, lmPose.LEFT_SHOULDER, w, h)
        r_shldr_x, r_shldr_y = get_landmark_coordinates(lm, lmPose.RIGHT_SHOULDER, w, h)
        l_ear_x, l_ear_y = get_landmark_coordinates(lm, lmPose.LEFT_EAR, w, h)
        l_hip_x, l_hip_y = get_landmark_coordinates(lm, lmPose.LEFT_HIP, w, h)

        # Calculate distance between left shoulder and right shoulder points.
        offset = findDistance(l_shldr_x, l_shldr_y, r_shldr_x, r_shldr_y)

        # Assist to align the camera to point at the side view of the person.
        # Offset threshold 30 is based on results obtained from analysis over 100 samples.
        if offset < 100:
            cv2.putText(image, str(int(offset)) + ' Aligned', (w - 150, 30), font, 0.9, green, 2)
        else:
            cv2.putText(image, str(int(offset)) + '\n Not Aligned', (w - 150, 30), font, 0.9, red, 2)

        # Calculate angles.
        neck_inclination = findAngle(l_shldr_x, l_shldr_y, l_ear_x, l_ear_y)
        torso_inclination = findAngle(l_hip_x, l_hip_y, l_shldr_x, l_shldr_y)

        # Draw landmarks.
        cv2.circle(image, (l_shldr_x, l_shldr_y), 7, yellow, -1)
        cv2.circle(image, (l_ear_x, l_ear_y), 7, yellow, -1)

        # Let's take y - coordinate of P3 100px above x1,  for display elegance.
        # Although we are taking y = 0 while calculating angle between P1,P2,P3.
        cv2.circle(image, (l_shldr_x, l_shldr_y - 100), 7, yellow, -1)
        cv2.circle(image, (r_shldr_x, r_shldr_y), 7, pink, -1)
        cv2.circle(image, (l_hip_x, l_hip_y), 7, yellow, -1)

        # Similarly, here we are taking y - coordinate 100px above x1. Note that
        # you can take any value for y, not necessarily 100 or 200 pixels.
        cv2.circle(image, (l_hip_x, l_hip_y - 100), 7, yellow, -1)

        # Put text, Posture and angle inclination.
        # Text string for display.
        angle_text_string = 'Neck : ' + str(int(neck_inclination)) + '  Torso : ' + str(int(torso_inclination))

        # Determine whether good posture or bad posture.
        # The threshold angles have been set based on intuition.
        if neck_inclination < 40 and torso_inclination < 10:
            bad_frames = 0
            good_frames += 1
            
            cv2.putText(image, angle_text_string, (10, 30), font, 0.9, light_green, 2)
            cv2.putText(image, str(int(neck_inclination)), (l_shldr_x + 10, l_shldr_y), font, 0.9, light_green, 2)
            cv2.putText(image, str(int(torso_inclination)), (l_hip_x + 10, l_hip_y), font, 0.9, light_green, 2)

            # Join landmarks.
            cv2.line(image, (l_shldr_x, l_shldr_y), (l_ear_x, l_ear_y), green, 4)
            cv2.line(image, (l_shldr_x, l_shldr_y), (l_shldr_x, l_shldr_y - 100), green, 4)
            cv2.line(image, (l_hip_x, l_hip_y), (l_shldr_x, l_shldr_y), green, 4)
            cv2.line(image, (l_hip_x, l_hip_y), (l_hip_x, l_hip_y - 100), green, 4)

        else:
            good_frames = 0
            bad_frames += 1

            cv2.putText(image, angle_text_string, (10, 30), font, 0.9, red, 2)
            cv2.putText(image, str(int(neck_inclination)), (l_shldr_x + 10, l_shldr_y), font, 0.9, red, 2)
            cv2.putText(image, str(int(torso_inclination)), (l_hip_x + 10, l_hip_y), font, 0.9, red, 2)

            # Join landmarks.
            cv2.line(image, (l_shldr_x, l_shldr_y), (l_ear_x, l_ear_y), red, 4)
            cv2.line(image, (l_shldr_x, l_shldr_y), (l_shldr_x, l_shldr_y - 100), red, 4)
            cv2.line(image, (l_hip_x, l_hip_y), (l_shldr_x, l_shldr_y), red, 4)
            cv2.line(image, (l_hip_x, l_hip_y), (l_hip_x, l_hip_y - 100), red, 4)

        # Calculate the time of remaining in a particular posture.
        # time = total_frames/fps
        good_time = (1 / fps) * good_frames
        bad_time =  (1 / fps) * bad_frames

        # Pose time.
        if good_time > 0:
            time_string_good = 'Good Posture Time : ' + str(round(good_time, 1)) + 's'
            cv2.putText(image, time_string_good, (10, h - 20), font, 0.9, green, 2)
        else:
            time_string_bad = 'Bad Posture Time : ' + str(round(bad_time, 1)) + 's'
            cv2.putText(image, time_string_bad, (10, h - 20), font, 0.9, red, 2)

        # If you stay in bad posture for more than 3 minutes (180s) send an alert.
        if bad_time > POSTURE_WARNING_TIME: # TODO make value later
            # sendWarning()
            ic("BAD POSTURE Warning!")

        # Update GUI
        imgbytes = cv2.imencode('.png', image)[1].tobytes()
        window['image'].update(data=imgbytes)

    # Release the webcam and close the window
    cap.release()
    window.close()

if __name__ =="__main__":
    if running_windows or running_mac:
        main()    
    else:
        print("this OS is not supported")