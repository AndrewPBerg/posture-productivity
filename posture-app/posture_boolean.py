import mediapipe as mp

mp_pose = mp.solutions.pose


def is_standing(pose_landmarks, standing_threshold=0.08) -> bool:
    """
    Returns True if user is standing or out of frame

    Args:
    * pose_landmarks: (frozenset) accepts results.pose_landmarks. it is a list of pose landmarks detected in Mediapipe package
    * standing_threshold: (float) decimal number to determine what is standing. Default = 0.08

    Returns:
    * Bool

    Example:
    * `standing = is_standing(results.pose_landmarks)`
    """
    standing = True
    if not pose_landmarks:
        return standing
    try:
        # Extract the y-coordinates of the relevant landmarks
        left_shoulder_y = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y
        right_shoulder_y = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].y
        left_eye_y = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_EYE].y
        right_eye_y = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_EYE].y

        # Calculate the average y-coordinates for shoulders and eyes
        average_shoulder_y = (left_shoulder_y + right_shoulder_y) / 2
        average_eye_y = (left_eye_y + right_eye_y) / 2

        if average_eye_y < 0.002:
            standing = True

        if average_shoulder_y - average_eye_y > standing_threshold:
            standing = False
        else:
            standing = True

        return standing
    except TypeError:
        return True
