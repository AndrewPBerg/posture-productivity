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

def get_landmark_coordinates(landmarks, landmark_name, image_width, image_height):
    """
    Args: 
    * landmarks: () accepts results.pose_landmarks
    * landmark_name: accepts lmPose.* get the name of the desired landmark to be checked
    * image_width: width of the image
    * image_height: height of the image

    Returns: 
    * x, y : coordinates calculated from the pixel position of landmark
    * None, None: in the case of exceptions

    Example: 
    lm = results.pose_landmarks
    lmPose = mp_pose.PoseLandmark

    # Calculate posture
    l_shldr_x, l_shldr_y = get_landmark_coordinates(lm, lmPose.LEFT_SHOULDER, w, h)
    """
    try:
        x = int(landmarks.landmark[landmark_name].x * image_width)
        y = int(landmarks.landmark[landmark_name].y * image_height)
        return x, y
    except IndexError:
        # Handle the case where the landmark is not found
        return None, None
    except AttributeError:
        # Handle the case where landmarks are not properly initialized
        return None, None


