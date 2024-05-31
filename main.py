from PySimpleGUI import running_mac, running_windows
import cv2
import PySimpleGUI as sg
import mediapipe as mp
from pose_utils import process_frame, calculate_posture_metrics
from gui_functions import draw_posture_indicators, toggle_button_images
from icecream import ic
import warnings

# Suppresses a near-dated mediapipe dependency
warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf")

def main():
    # APP posture limits
    POSTURE_WARNING_TIME = 2

    FONT = cv2.FONT_HERSHEY_SIMPLEX

    # Colors
    RED = (50, 50, 255)
    GREEN = (127, 255, 0)
    LIGHT_GREEN = (127, 233, 100)

    # used for of-off buttons
    # get the base64 strings for the button images
    toggle_btn_off, toggle_btn_on = toggle_button_images() 

    # Initialize pose
    pose = mp.solutions.pose.Pose()

    # check if webcam opens
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Unable to access the camera")
        return

    # Get image metadata
    cap.set(cv2.CAP_PROP_FPS, 30.0)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # initialize window
    layout = [[sg.Image(filename='', key='image')],
              [sg.Button(button_text='Click for Snapshot',tooltip='Click for Data Snapshot', key='snapshot_button'), sg.Text(text='',key='snapshot_text')],
              [sg.Text('Display annotations (On/Off):'),sg.Button('', image_data=toggle_btn_on, key='-TOGGLE-GRAPHIC-', button_color=(sg.theme_background_color(), sg.theme_background_color()), border_width=0)]]
    
    window = sg.Window('Webcam Window', layout, location=(0,0), resizable=True, size=(width*2, height*2))


    good_frames = 0
    bad_frames = 0
    display_annotations = True

    # Used to adjust the posture conditionals
    difficulty = 0

    # default values set for offset and inclination conditions
    nrml_offset = 300
    nrml_neck_inclination = 40
    nrml_torso_inclination = 10

    while True:
        
        success, image = cap.read()

        if not success:
            ic("Error reading image") # TODO write "no webcam found" in window, not terminal
            break

        results, image = process_frame(image, pose)

        event, values = window.read(timeout=20)

        if event == sg.WINDOW_CLOSED:
            break
        elif event == '-TOGGLE-GRAPHIC-':
            # flips graphic toggle
            display_annotations = not display_annotations
            window['-TOGGLE-GRAPHIC-'].update(image_data=toggle_btn_on if display_annotations else toggle_btn_off)

        if results.pose_landmarks:
            try:
                metrics = calculate_posture_metrics(pose, image)
                if metrics:
                    l_shldr_x, l_shldr_y = metrics['l_shldr_x'], metrics['l_shldr_y']
                    r_shldr_x, r_shldr_y= metrics['r_shldr_x'], metrics['r_shldr_y']
                    l_ear_x, l_ear_y = metrics['l_ear_x'], metrics['l_ear_y']
                    l_hip_x, l_hip_y = metrics['l_hip_x'], metrics['l_hip_y']
                    offset = metrics['offset']
                    neck_inclination = metrics['neck_inclination']
                    torso_inclination = metrics['torso_inclination']

                    if event == 'snapshot_button':
                        nrml_offset = (offset + difficulty)
                        nrml_neck_inclination = (neck_inclination + difficulty)
                        nrml_torso_inclination = (torso_inclination + difficulty)

                        window['snapshot_text'].update((f"offset: {int(offset)} \
                              \nneck: {int(neck_inclination)} \
                              \ntorso: {int(torso_inclination)}"))
                        

            
                    if offset < nrml_offset:
                        cv2.putText(image, f'{int(offset)} Aligned', (10, height - 200), FONT, 0.9, GREEN, 2)
                    else:
                        cv2.putText(image, f'{int(offset)}\n Not Aligned', (10, height - 200), FONT, 0.9, RED, 2)

                    if display_annotations:
                        color = LIGHT_GREEN if neck_inclination < nrml_neck_inclination and torso_inclination < nrml_torso_inclination else RED
                        draw_posture_indicators(image, l_shldr_x, l_shldr_y, r_shldr_x, r_shldr_y, l_ear_x, l_ear_y, l_hip_x, l_hip_y, color)

                    good_time = (1 / fps) * good_frames
                    bad_time = (1 / fps) * bad_frames
                    
                    angle_text_string = f'Neck: {int(neck_inclination)}  Torso: {int(torso_inclination)}'
                    if neck_inclination < nrml_neck_inclination and torso_inclination < nrml_torso_inclination:
                        color = LIGHT_GREEN
                        posture_status = 'Good'
                    else:
                        color = RED
                        posture_status = 'Bad'
                    
                    cv2.putText(image, angle_text_string, (10, 30), FONT, 0.9, color, 2)
                    cv2.putText(image, f'Good Posture Time: {round(good_time, 1)}s' if good_time > 0 else f'Bad Posture Time: {round(bad_time, 1)}s', (10, height - 20), FONT, 0.9, color, 2)

                    if posture_status == 'Good' and offset < nrml_offset:
                        bad_frames = 0
                        good_frames += 1
                    else:
                        good_frames = 0
                        bad_frames += 1

                    if bad_time > POSTURE_WARNING_TIME:
                        ic("BAD POSTURE Warning!")
            except TypeError as e0:
                ic(f"TYPE ERROR CAUGHT: {e0}")
            except UnboundLocalError as e1:
                ic(f"UnboundLocalError caught: {e1}")

        imgbytes = cv2.imencode('.png', image)[1].tobytes()
        window['image'].update(data=imgbytes)

    cap.release()
    window.close()

if __name__ == "__main__":
    if running_windows or running_mac:
        main()
    else:
        print("This OS is not supported")
