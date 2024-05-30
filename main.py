
from PySimpleGUI import running_mac,running_windows
import cv2
import PySimpleGUI as sg
import mediapipe as mp
from pose_landmark_utils import get_landmark_coordinates, findAngle, findDistance
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

    layout = [
        [sg.Image(filename='', key='image')],
    ]

    # Initilize frame counters.
    good_frames = 0
    bad_frames = 0

    font = cv2.FONT_HERSHEY_SIMPLEX

    # blue = (255, 127, 0)
    red = (50, 50, 255)
    green = (127, 255, 0)
    # dark_blue = (127, 20, 0)
    light_green = (127, 233, 100)
    yellow = (0, 255, 255)
    pink = (255, 0, 255)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Unable to access the camera")
        return

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_size = (width, height)
    
    window = sg.Window('Webcam Window', layout, location=frame_size, resizable=True, size=(width*2,height*2))
    # ===============================================================================================#

    while True:
        success, image = cap.read()
        if not success:
            ic("Error reading image")
            break

        fps = cap.get(cv2.CAP_PROP_FPS)
        h, w = image.shape[:2]

        # Convert the image from BGR to RGB --- MEDIAPIPE REQUIREMENT!!!
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Process the image and detect poses
        results = pose.process(image)

        # Convert image back to BGR for better image visibility
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        event, values = window.read(timeout=20)

        if event == sg.WINDOW_CLOSED:
            break

        lm = results.pose_landmarks
        lmPose = mp_pose.PoseLandmark

        # Calculate posture coordinates
        l_shldr_x, l_shldr_y = get_landmark_coordinates(lm, lmPose.LEFT_SHOULDER, w, h)
        r_shldr_x, r_shldr_y = get_landmark_coordinates(lm, lmPose.RIGHT_SHOULDER, w, h)
        l_ear_x, l_ear_y = get_landmark_coordinates(lm, lmPose.LEFT_EAR, w, h)
        l_hip_x, l_hip_y = get_landmark_coordinates(lm, lmPose.LEFT_HIP, w, h)

        try:
        # Calculate distance between left shoulder and right shoulder points.
            offset = findDistance(l_shldr_x, l_shldr_y, r_shldr_x, r_shldr_y)

            if offset < 100:
                cv2.putText(image, str(int(offset)) + ' Aligned', (10, h-200), font, 0.9, green, 2)
            else:
                cv2.putText(image, str(int(offset)) + '\n Not Aligned', (10, h-200), font, 0.9, red, 2)

            # Calculate angles.
            neck_inclination = findAngle(l_shldr_x, l_shldr_y, l_ear_x, l_ear_y)
            torso_inclination = findAngle(l_hip_x, l_hip_y, l_shldr_x, l_shldr_y)

            # Draw landmarks as circles
            cv2.circle(image, (l_shldr_x, l_shldr_y), 7, yellow, -1)
            cv2.circle(image, (l_ear_x, l_ear_y), 7, yellow, -1)
            cv2.circle(image, (l_shldr_x, l_shldr_y - 100), 7, yellow, -1)
            cv2.circle(image, (r_shldr_x, r_shldr_y), 7, pink, -1)
            cv2.circle(image, (l_hip_x, l_hip_y), 7, yellow, -1)
            cv2.circle(image, (l_hip_x, l_hip_y - 100), 7, yellow, -1)

            angle_text_string = 'Neck : ' + str(int(neck_inclination)) + '  Torso : ' + str(int(torso_inclination))

            # Determine whether good posture or bad posture.
            if neck_inclination < 40 and torso_inclination < 10:
                bad_frames = 0
                good_frames += 1
                
                cv2.putText(image, angle_text_string, (10, 30), font, 0.9, light_green, 2)
                cv2.putText(image, str(int(neck_inclination)), (l_shldr_x + 10, l_shldr_y), font, 0.9, light_green, 2)
                cv2.putText(image, str(int(torso_inclination)), (l_hip_x + 10, l_hip_y), font, 0.9, light_green, 2)

                # Join landmarks with lines
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
                cv2.line(image, (l_shldr_x, l_shldr_y), (l_ear_x, l_ear_y), red, 4)
                cv2.line(image, (l_shldr_x, l_shldr_y), (l_shldr_x, l_shldr_y - 100), red, 4)
                cv2.line(image, (l_hip_x, l_hip_y), (l_shldr_x, l_shldr_y), red, 4)
                cv2.line(image, (l_hip_x, l_hip_y), (l_hip_x, l_hip_y - 100), red, 4)

            # time = total_frames/fps
            good_time = (1 / fps) * good_frames
            bad_time =  (1 / fps) * bad_frames


            if good_time > 0:
                time_string_good = 'Good Posture Time : ' + str(round(good_time, 1)) + 's'
                cv2.putText(image, time_string_good, (10, h - 20), font, 0.9, green, 2)
            else:
                time_string_bad = 'Bad Posture Time : ' + str(round(bad_time, 1)) + 's'
                cv2.putText(image, time_string_bad, (10, h - 20), font, 0.9, red, 2)

            if bad_time > POSTURE_WARNING_TIME:
                # sendWarning()
                ic("BAD POSTURE Warning!")
        except TypeError:
            ic("Couldn't find landmarks")
        except UnboundLocalError:
            ic("variable not declared yet")


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