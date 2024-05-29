# pose_landmark_utils.py
import mediapipe as mp
from icecream import ic
def create_landmark_dict(pose_landmarks, landmark_name):
    """
    #### dictionary in the format {x: x_value, y: y_value, z: z_value, name: landmark_name} for a specified mediapipe landmark_name
    
    Args:
    * pose_landmarks: results.pose_landmarks inherited from `output_values`. the list of pose landmarks detected in Mediapipe
    * landmark_name: used to specify which xyz values to return

    Returns:  
    * dict in the format {x: x_value, y: y_value, z: z_value, name: landmark_name} for a specified mediapipe landmark_name
    
    Example:
        `landmark_dict = create_landmark_dict(pose_landmarks, landmark)`
    """
    landmark_obj = pose_landmarks.landmark[landmark_name]
    return {'x': landmark_obj.x, 'y': landmark_obj.y, 'z':landmark_obj.z, 'obj_name': landmark_name}

def output_values(pose_landmarks, landmark_list, display=True):
    """
    Args:
    * pose_landmarks: (frozenset) accepts results.pose_landmarks. it is a list of pose landmarks detected in Mediapipe package
    * landark_list: (list) the list of landmarks to output xyz
    * display: (bool) to print or not

    Returns:
    * None
    * dict in format `{'Example_mark': {'name':,
                                             'x':,
                                             'y':,
                                             'z':},
                                             }`
    Example:
    * elif event == 'xyz':
    \toutput_values(results.pose_landmarks, OUTPUT_LANDMARKS)
    \twindow['left_shoulder_xyz'].update()
    """

    if not pose_landmarks:
        ic("No landmarks detected")
        return None
  
    result_landmark_dict = {}

    for landmark in landmark_list:
        ic(landmark)
        landmark_dict = create_landmark_dict(pose_landmarks, landmark)
        landmark_name = mp.solutions.pose.PoseLandmark(landmark).name
        result_landmark_dict[landmark_name] = landmark_dict
        ic(result_landmark_dict[landmark_name])
        if display:
            print(f"{landmark_name} x: {landmark_dict['x']:.2f}, y: {landmark_dict['y']:.2f}, z: {landmark_dict['z']:.2f}")

    ic(result_landmark_dict)
    return result_landmark_dict

def calc_landmark_coords(results, mp_pose, landmark_name, width, height):
    try:
        # lm = results.pose_landmarks

        x = int(results.pose_landmarks.landmark[landmark_name].x * width)
        y = int(results.pose_landmarks.landmark[landmark_name].y * height)
        return x,y  
#         # l_shldr_x = int(lm.landmark[lmPose.LEFT_SHOULDER].x * w)

    except AttributeError:
        ic("no landmarks detected, ERROR")
        # return None, None

