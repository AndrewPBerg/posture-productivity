import mediapipe as mp
from icecream import ic
import math as m
import cv2

def process_frame(image, pose):
    """
    ### Process the frame to detect pose and calculate metrics.

    Args:
    * image(Any cv2 image object)
    * pose([mediapipe] mp.solutions.pose.Pose() object)

    Returns:
    * results: returns mp.pose processed image data 
    * image: returns the same frame

    Example: 
    `results, image = process_frame(image, pose)` 
    """
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)
    return results, cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

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
    ### Calculate a given landmarks x and y values relative to frames resolution 

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

    l_shldr_x, l_shldr_y = get_landmark_coordinates(lm, lmPose.LEFT_SHOULDER, w, h)
    """
    try:
        x = int(landmarks.landmark[landmark_name].x * image_width)
        y = int(landmarks.landmark[landmark_name].y * image_height)
        return x, y
    except IndexError:
        # Handle case where the landmark is not found
        return None, None
    except AttributeError:
        # Handle case where landmarks are not properly initialized
        return None, None
    
def calculate_posture_metrics(pose, image):
    """
    ### Capture a snapshot of the user's posture and return key metrics in a dictionary format.
    
    Args: 
    * pose: (mediapipe pose object from: mp.solutions.pose.Pose())
    * image: (Any cv2 image)
    
    Returns:
    * metrics: a dictionary containing landmark coordinates, and calculated offsets, torso/neck inclinations

    Example:
    `metrics = snapshot(pose, image)`
    """
    h, w = image.shape[:2]

    results, image = process_frame(image, pose)

    lm = results.pose_landmarks
    if lm is None:
        return None

    mp_landmarks = mp.solutions.pose.PoseLandmark

    # Calculate posture coordinates
    l_shldr_x, l_shldr_y = get_landmark_coordinates(lm, mp_landmarks.LEFT_SHOULDER, w, h)
    r_shldr_x, r_shldr_y = get_landmark_coordinates(lm, mp_landmarks.RIGHT_SHOULDER, w, h)
    l_ear_x, l_ear_y = get_landmark_coordinates(lm, mp_landmarks.LEFT_EAR, w, h)
    l_hip_x, l_hip_y = get_landmark_coordinates(lm, mp_landmarks.LEFT_HIP, w, h)

    # Calculate distance between left shoulder and right shoulder points
    offset = findDistance(l_shldr_x, l_shldr_y, r_shldr_x, r_shldr_y)

    # Calculate angles
    neck_inclination = findAngle(l_shldr_x, l_shldr_y, l_ear_x, l_ear_y)
    torso_inclination = findAngle(l_hip_x, l_hip_y, l_shldr_x, l_shldr_y)

    return {
        'l_shldr_x': l_shldr_x,
        'l_shldr_y': l_shldr_y,
        'r_shldr_x': r_shldr_x,
        'r_shldr_y': r_shldr_y,
        'l_ear_x': l_ear_x,
        'l_ear_y': l_ear_y,
        'l_hip_x': l_hip_x,
        'l_hip_y': l_hip_y,
        'offset': offset,
        'neck_inclination': neck_inclination,
        'torso_inclination': torso_inclination
    }



def findDistance(x1, y1, x2, y2):
    dist = m.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return dist

def findAngle(x1, y1, x2, y2):
    theta = m.acos((y2 - y1) * (-y1) / (m.sqrt(
        (x2 - x1) ** 2 + (y2 - y1) ** 2) * y1))
    degree = int(180 / m.pi) * theta
    return degree
