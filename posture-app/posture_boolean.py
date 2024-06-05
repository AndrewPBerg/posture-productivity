import mediapipe as mp

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

def is_standing(pose_landmarks):
    """
    Returns bool for if person is standing

    Args:
    * pose_landmarks: (frozenset) accepts results.pose_landmarks. it is a list of pose landmarks detected in Mediapipe package

    Returns: 
    * True
    * False

    Example:
    * `standing = is_standing(results.pose_landmarks)`
    """
    if not pose_landmarks:
        return False

    left_hip = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
    left_knee = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE]
    left_ankle = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE]

    right_hip = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
    right_knee = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE]
    right_ankle = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE]

    # Check if the knees are below the hips and the ankles are below the knees
    left_leg_straight = left_ankle.y > left_knee.y > left_hip.y
    right_leg_straight = right_ankle.y > right_knee.y > right_hip.y

    return left_leg_straight and right_leg_straight