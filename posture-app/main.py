from PySimpleGUI import running_mac, running_windows
import cv2
import PySimpleGUI as sg
import mediapipe as mp
from pose_utils import process_frame, calculate_posture_metrics
from gui_functions import draw_posture_indicators, toggle_button_images, alert_user, Timer
from posture_boolean import is_standing
from icecream import ic
import warnings

# Suppresses a near-dated mediapipe dependency
warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf")

def main():
    # APP posture limits

    total_time = 0
    total_frames = 0
    POSTURE_WARNING_TIME = 5

    FONT = cv2.FONT_HERSHEY_SIMPLEX

    # Colors
    RED = (50, 50, 255)
    LIGHT_GREEN = (127, 233, 100)
    color = (247, 245, 245)
    neck_color = (247, 245, 245)
    closeness_color = (247, 245, 245)
    shldr_level_color = (247, 245, 245)

    # used for of-off buttons
    # get the base64 strings for the button images
    toggle_btn_off, toggle_btn_on = toggle_button_images() 

    # Initialize pose
    pose = mp.solutions.pose.Pose(static_image_mode=False, model_complexity=0)

    # default values set for offset and inclination conditions
    nrml_offset = 260
    nrml_neck_inclination = 30
    nrml_torso_inclination = 4
    my_closeness = 420
    my_shldr_distance = 270
    my_shldr_level = 10

    # Used to adjust the posture conditionals
    easiness = 5

    # check if webcam opens
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        print("Error: Unable to access the camera")
        return

    # Get image metadata
    cap.set(cv2.CAP_PROP_FPS, 10.0)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    # width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Initialize Tabgroups
    tab1_layout = [
        [sg.Text("Set Timer (minutes):"), sg.Combo(values=["20","25","30","35"], key="-TIMER-",  default_value="25")], 
        [sg.Text("Short Break (minutes):"), sg.Combo(["1","3","5"], key="-SHORTBREAK-",  default_value="3")],
        [sg.Text("Long Break (minutes):"), sg.Combo(["15","20","25","30"], key="-LONGBREAK-", default_value="35")],
        [sg.Text("Countdown Timer:", size=(15, 1)), sg.Text("", size=(8, 1), key="-DISPLAYTIMER-")],
        [sg.Button("Start"), sg.Button("(Un)Pause"), sg.Button("Reset"), sg.Button("Next")],
        [sg.Text("Auto Next from Standing (On/Off):"),sg.Button("", image_data=toggle_btn_off, key="-TOGGLE-NEXT-", button_color=(sg.theme_background_color(), sg.theme_background_color()), border_width=0)],
        [sg.Text("", key=("-AUTO-STANDING-TEXT"))],
        [sg.Text("", key=("-DONE-KEY-"))],
    ]
    tab2_layout = [[sg.Button(button_text="Change The Baseline Posture To Current Frame",tooltip="Click to change default good posture values to your current posture", key="-BASELINE-BUTTON")],
                   [sg.Text("'Laxness:"),sg.Slider(default_value=5, orientation="h",enable_events=True, key="-SLIDER-")],
                   [sg.Text("Display main video (on/off)"),sg.Button("", image_data=toggle_btn_on, key="-TOGGLE-VIDEO-", button_color=(sg.theme_background_color(), sg.theme_background_color()), border_width=0)]]
    tab3_layout = [[sg.Text("Debug Settings:")],
                   [sg.Text("Display annotations (On/Off):"),sg.Button("", image_data=toggle_btn_on, key="-TOGGLE-ANNOTATIONS-", button_color=(sg.theme_background_color(), sg.theme_background_color()), border_width=0)],
                   [sg.Text("Display Posture Data (On/Off):"),sg.Button("", image_data=toggle_btn_on, key="-TOGGLE-DATA-", button_color=(sg.theme_background_color(), sg.theme_background_color()), border_width=0)],
                   [sg.Text("Baseline posture data: ")], [sg.Text(f"offset: {int(nrml_offset)} \
                              \nneck: {int(nrml_neck_inclination)} \
                              \ntorso: {int(nrml_torso_inclination)}\
                              \nEasiness {easiness}\
                              \nCloseness {int(my_closeness)}\
                              \nShldr level {int(my_shldr_level)}\
                              \nshldr distance {int(my_shldr_distance)}",
                              key="-DEBUG-POSTURE-TEXT-")],
                   [sg.Text("Standing/Sitting:"), sg.Text("", key="-STANDING-SITTING-DEBUG-")],
                   [sg.Button(button_text="Change The Baseline Posture To Current Frame",tooltip="Click to change default good posture values to your current posture", key="-BASELINE-BUTTON2")]]
    tab4_layout = [[sg.Text("Notification Settings:")],
                   [sg.Text("Audio Notifications (On/Off):")],[sg.Button("", image_data=toggle_btn_on, key="-TOGGLE-AUDIO-", button_color=(sg.theme_background_color(), sg.theme_background_color()), border_width=0)]]
    # Initialize column layouts``
    column1_layout = [[sg.Image(filename="", key="image")]]
    column2_layout = [[sg.Frame("Settings" ,layout=[[sg.TabGroup([[sg.Tab("Timer", tab1_layout)], [sg.Tab("Posture Setup", tab2_layout)], [(sg.Tab("Debug", tab3_layout))], [(sg.Tab("Notifications", tab4_layout))]])]])]]
    
    # Initialize Window layout
    layout = [
        [sg.Column(scrollable=False, layout=column1_layout), sg.Column(scrollable=False, layout=column2_layout)],

    ]
    
    # initialize window
    window = sg.Window("Webcam Window", layout, location=(0,0), resizable=True, size=(1000,700))

    good_frames = 0
    bad_frames = 0
    display_annotations = True
    display_data = True
    play_audio = True
    automatic_standing_timer = False
    display_cv2_video = True

    alert_interval = 5  # Minimum interval between alerts in seconds
    last_alert_time = 0  # Tracks the last time the alert was played

    timer = Timer(window)

    while True:
        
        success, image = cap.read()

        if not success:
            sg.popup("Error reading image, plugin your camera and restart app")
            break

        results, image = process_frame(image, pose)

        event, values = window.read(timeout=20)

        if event is not None and values is not None:
            
            timer.check_buttons(values, event)
            timer.update_timer()

        # if timer is running calculate and update time

        if event == sg.WINDOW_CLOSED:
            break
        elif event == "-TOGGLE-ANNOTATIONS-":
            # flips graphic toggle
            display_annotations = not display_annotations
            window["-TOGGLE-ANNOTATIONS-"].update(image_data=toggle_btn_on if display_annotations else toggle_btn_off)
        elif event == "-TOGGLE-DATA-":
            display_data = not display_data
            window["-TOGGLE-DATA-"].update(image_data=toggle_btn_on if display_data else toggle_btn_off)
        elif event == "-TOGGLE-AUDIO-":
            play_audio  = not play_audio
            window["-TOGGLE-AUDIO-"].update(image_data=toggle_btn_on if play_audio else toggle_btn_off)
        elif event == "-TOGGLE-NEXT-":
            automatic_standing_timer  = not automatic_standing_timer
            window["-TOGGLE-NEXT-"].update(image_data=toggle_btn_on if automatic_standing_timer else toggle_btn_off)
            if not automatic_standing_timer:
                window["-AUTO-STANDING-TEXT"].update("")
        elif event == "-TOGGLE-VIDEO-":
            display_cv2_video  = not display_cv2_video
            window["-TOGGLE-VIDEO-"].update(image_data=toggle_btn_on if display_cv2_video else toggle_btn_off)
        elif event == "-SLIDER-":
            # get slider value and invert it for usable posture Easiness
            easiness = (int(values["-SLIDER-"]) % 11)

        if is_standing(results.pose_landmarks) and automatic_standing_timer:
            window["-STANDING-SITTING-DEBUG-"].update("Standing")
            window["-AUTO-STANDING-TEXT"].update("Standing")
            timer.check_buttons(values,event,auto_next=True)
        elif not is_standing(results.pose_landmarks) and automatic_standing_timer:
            window["-STANDING-SITTING-DEBUG-"].update("Sitting")
            window["-AUTO-STANDING-TEXT"].update("Sitting")
            timer.check_buttons(values,event,auto_start=True)

        if results.pose_landmarks:
            try:
                metrics = calculate_posture_metrics(pose, image)
                if metrics:
                    l_shldr_x, l_shldr_y = metrics["l_shldr_x"], metrics["l_shldr_y"]
                    r_shldr_x, r_shldr_y = metrics["r_shldr_x"], metrics["r_shldr_y"]
                    l_ear_x, l_ear_y = metrics["l_ear_x"], metrics["l_ear_y"]
                    l_hip_x, l_hip_y = metrics["l_hip_x"], metrics["l_hip_y"]
                    shldr_distance = metrics["shldr_distance"]
                    neck_inclination = metrics["neck_inclination"]
                    torso_inclination = metrics["torso_inclination"]
                    closeness = metrics["closeness"]
                    shldr_level = metrics["shldr_level"]

                    if event == "-BASELINE-BUTTON" or event == "-BASELINE-BUTTON2":
                        nrml_neck_inclination = neck_inclination
                        nrml_torso_inclination = torso_inclination
                        my_shldr_distance = shldr_distance
                        my_closeness = closeness
                        my_shldr_level = shldr_level

                        window["-DEBUG-POSTURE-TEXT-"].update(f"offset: {int(nrml_offset)} \
                              \nneck: {int(nrml_neck_inclination)} \
                              \ntorso: {int(nrml_torso_inclination)} \
                              \nEasiness {int(easiness)} \
                              \nCloseness {int(my_closeness)} \
                              \nShldr level {int(my_shldr_level)} \
                              \nshldr distance {int(my_shldr_distance)}")
                        
                    good_time = good_frames/fps
                    bad_time = bad_frames/fps

                    good_closeness = True
                    good_shldr = True
                    good_neck = True
                    

                    if closeness + (easiness * 20) > my_closeness > closeness - (easiness * 50):
                        closeness_color = LIGHT_GREEN
                    else:
                        closeness_color = RED
                        good_closeness = False

                    if neck_inclination + easiness + 5 > nrml_neck_inclination > neck_inclination - easiness + 5:
                        neck_color = LIGHT_GREEN
                    else:
                        neck_color = RED
                        good_neck = False
                        # good_neck = True

                    if shldr_level + easiness * 5 > my_shldr_level > shldr_level - easiness * 5:
                        color = LIGHT_GREEN
                        shldr_level_color = LIGHT_GREEN
                    else:
                        shldr_level_color = RED
                        good_neck = False

                    if good_closeness and good_shldr and good_neck:
                        color = LIGHT_GREEN
                        bad_frames = 0
                        good_frames += 1
                    else:
                        color = RED
                        good_frames = 0
                        bad_frames += 1

                    total_frames += 1


                    if display_annotations:
                        draw_posture_indicators(image, l_shldr_x, l_shldr_y, r_shldr_x, r_shldr_y, l_ear_x, l_ear_y, l_hip_x, l_hip_y, color)

                    if display_data:
                        cv2.putText(image, f"Neck: {int(neck_inclination)}", (10, 30), FONT, 0.9, neck_color, 2)
                        cv2.putText(image, f"shldr_level: {shldr_level}", (10, 60), FONT, 0.9, shldr_level_color, 2)
                        cv2.putText(image, f"Closeness: {int(closeness)}", (10, 90), FONT, 0.9, closeness_color, 2)
                        cv2.putText(image, f"Good Posture Time: {round(good_time, 1)}s" if good_time > 0 else f"Bad Posture Time: {round(bad_time, 1)}s", (10, height - 20), FONT, 0.9, color, 2)

                    if bad_time > POSTURE_WARNING_TIME:
                        total_time = total_frames/fps
                        if total_time - last_alert_time > alert_interval:
                            last_alert_time = total_time
                            if play_audio:
                                alert_user()
                                # try:
                                    # alert_user("buzz-notif.mp3")
                                # except:
                                #     alert_user("posture-app/buss-notif.mp3")

            except TypeError as e0:
                ic(f"TYPE ERROR CAUGHT: {e0}")
            except UnboundLocalError as e1:
                ic(f"UnboundLocalError caught: {e1}")
        
        if display_cv2_video:
            imgbytes = cv2.imencode(".png", image)[1].tobytes()
            window["image"].update(data=imgbytes)
        else:
            window["image"].update(data=None)

    cap.release()
    window.close()

if __name__ == "__main__": 
    if running_windows or running_mac:
        # cProfile.run('main()')
        main()
    else:
        print("This OS is not supported")
