import mediapipe as mp
from icecream import ic

mp_pose = mp.solutions.pose

def is_hand_raised(pose_landmarks):
    """
    Returns bool for if hand is raised

    Args:
    * pose_landmarks: (frozenset) accepts results.pose_landmarks. it is a list of pose landmarks detected in Mediapipe package

    Returns: 
    * True
    * False

    Example:
    * `hand_raised = is_hand_raised(results.pose_landmarks)`
    """
    if not pose_landmarks:
        return False

    left_wrist = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
    left_elbow = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW]
    left_shoulder = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]

    right_wrist = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
    right_elbow = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW]
    right_shoulder = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]

    left_hand_raised = (left_wrist.y < left_elbow.y < left_shoulder.y)
    right_hand_raised = (right_wrist.y < right_elbow.y < right_shoulder.y)

    return left_hand_raised or right_hand_raised

def is_standing(pose_landmarks, standing_threshold=0.08):
    """
    Returns True for if person is standing

    Args:
    * pose_landmarks: (frozenset) accepts results.pose_landmarks. it is a list of pose landmarks detected in Mediapipe package
    * standing_threshold: (float) decimal number to determine what is standing. Default = 0.08

    Returns: 
    * True
    * False

    Example:
    * `standing = is_standing(results.pose_landmarks)`
    """
    standing = True
    if not pose_landmarks:
        return standing
    # Extract the y-coordinates of the relevant landmarks
    try:
        # left_hip_y = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].y
        # right_hip_y = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP].y
        # left_knee_y = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE].y
        # right_knee_y = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE].y
        # average_hip_y = (left_hip_y + right_hip_y) / 2
        # average_knee_y = (left_knee_y + right_knee_y) / 2

        left_shoulder_y = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y
        right_shoulder_y = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].y
        left_eye_y = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_EYE].y
        right_eye_y = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_EYE].y

        # Calculate the average y-coordinates for shoulders and eyes
        average_shoulder_y = (left_shoulder_y + right_shoulder_y) / 2
        average_eye_y = (left_eye_y + right_eye_y) / 2


        # ic(f"avg_shoulder_y {average_shoulder_y}  - eye_y {average_eye_y} = {average_shoulder_y-average_eye_y}")
        # ic(f"x > standing_threshold {standing_threshold} = {average_shoulder_y - average_eye_y > standing_threshold}")
        # ic(average_hip_y,average_knee_y,(average_hip_y-average_knee_y))
        if average_eye_y < 0.002:
            standing = True

        if average_shoulder_y - average_eye_y > standing_threshold:
            standing = False
        else:
            standing = True
        
        return standing
    except TypeError:
        return True