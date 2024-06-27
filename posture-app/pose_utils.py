import mediapipe as mp
import math as m
import cv2


def calculate_posture_metrics(pose:mp.solutions.pose.Pose,
                              image:cv2.Mat) -> dict[str,float]:
    """
    ### Capture a snapshot of the user's posture and return key metrics in a dictionary format.

    Args:
    * pose: (mediapipe pose object: mp.solutions.pose.Pose())
    * image: (cv2 image object, see :func:`process_frame`)

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
    l_shldr_x, l_shldr_y, l_shldr_z = _get_landmark_coordinates(
        lm, mp_landmarks.LEFT_SHOULDER, w, h, calc_z=True
    )
    r_shldr_x, r_shldr_y, r_shldr_z = _get_landmark_coordinates(
        lm, mp_landmarks.RIGHT_SHOULDER, w, h, calc_z=True
    )
    l_ear_x, l_ear_y, l_ear_z = _get_landmark_coordinates(
        lm, mp_landmarks.LEFT_EAR, w, h, calc_z=True
    )
    l_hip_x, l_hip_y = _get_landmark_coordinates(lm, mp_landmarks.LEFT_HIP, w, h)

    # Calculate distance between left shoulder and right shoulder points
    shldr_distance = _findDistance(l_shldr_x, l_shldr_y, r_shldr_x, r_shldr_y)

    # Calculate angles
    neck_inclination = _findAngle(l_shldr_x, l_shldr_y, l_ear_x, l_ear_y)
    torso_inclination = _findAngle(l_hip_x, l_hip_y, l_shldr_x, l_shldr_y)

    return {
        "l_shldr_x": l_shldr_x,
        "l_shldr_y": l_shldr_y,
        # "l_shldr_z": l_shldr_z,
        "r_shldr_x": r_shldr_x,
        "r_shldr_y": r_shldr_y,
        # "r_shldr_z": r_shldr_z,
        "l_ear_x": l_ear_x,
        "l_ear_y": l_ear_y,
        # "l_ear_z": l_ear_z,
        "l_hip_x": l_hip_x,
        "l_hip_y": l_hip_y,
        "shldr_distance": shldr_distance,
        "neck_inclination": neck_inclination,
        "torso_inclination": torso_inclination,
        "closeness": abs(
            (l_shldr_z + r_shldr_z + l_ear_z) / 3
        ),  # arithmetic mean of shldr + ear z's
        "shldr_level": abs(l_shldr_y - r_shldr_y),
    }

def process_frame(image:cv2.Mat, pose:mp.solutions.pose.Pose)-> tuple[mp.solutions.pose.PoseLandmark, cv2.Mat]:
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


def _get_landmark_coordinates(
    landmarks:any, landmark_name:any, image_width:int, image_height:int, calc_z=False
):
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
        if calc_z:
            z = int(landmarks.landmark[landmark_name].z * image_width)
            return x, y, z
        return x, y
    except IndexError:
        # Handle case where the landmark is not found
        return None, None
    except AttributeError:
        # Handle case where landmarks are not properly initialized
        return None, None




def _findDistance(x1, y1, x2, y2) -> float:
    dist = m.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return dist


def _findAngle(x1, y1, x2, y2) -> float:
    theta = m.acos((y2 - y1) * (-y1) / (m.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) * y1))
    degree = int(180 / m.pi) * theta
    return degree
