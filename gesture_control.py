import cv2
import mediapipe as mp
import pyautogui

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

last_hand_center = None
hoverboard_active = False

def calculate_hand_center(hand_landmarks):
    x_coords = [landmark.x for landmark in hand_landmarks.landmark]
    y_coords = [landmark.y for landmark in hand_landmarks.landmark]
    return sum(x_coords) / len(x_coords), sum(y_coords) / len(y_coords)

def recognize_hand_movement(hand_landmarks, image_width, image_height):
    global last_hand_center

    hand_center_x, hand_center_y = calculate_hand_center(hand_landmarks)

    if last_hand_center is None:
        last_hand_center = (hand_center_x, hand_center_y)
        return None

    dx = hand_center_x - last_hand_center[0]
    dy = hand_center_y - last_hand_center[1]

    last_hand_center = (hand_center_x, hand_center_y)

    threshold_x = 0.03
    threshold_y = 0.03

    if abs(dx) > threshold_x or abs(dy) > threshold_y:
        if dx > threshold_x:
            return "right"
        elif dx < -threshold_x:
            return "left"
        elif dy < -threshold_y:
            return "up"
        elif dy > threshold_y:
            return "down"
    else:
        return None

def recognize_hoverboard_toggle(hand_landmarks):
    landmarks = hand_landmarks.landmark
    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
    index_finger_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_finger_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_finger_tip = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = landmarks[mp_hands.HandLandmark.PINKY_TIP]

    if (
        thumb_tip.y < index_finger_tip.y
        and index_finger_tip.y < middle_finger_tip.y
        and middle_finger_tip.y < ring_finger_tip.y
        and ring_finger_tip.y < pinky_tip.y
    ):
        return True
    else:
        return False

def recognize_enter_key(hand_landmarks):
    landmarks = hand_landmarks.landmark
    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
    index_finger_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_finger_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_finger_tip = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = landmarks[mp_hands.HandLandmark.PINKY_TIP]

    if (
        thumb_tip.y > index_finger_tip.y
        and index_finger_tip.y > middle_finger_tip.y
        and middle_finger_tip.y > ring_finger_tip.y
        and ring_finger_tip.y > pinky_tip.y
    ):
        return True
    else:
        return False

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks,
                                      mp_hands.HAND_CONNECTIONS)
            movement = recognize_hand_movement(hand_landmarks, frame.shape[1],
                                               frame.shape[0])

            if movement:
                print(f"Movement: {movement}")
                if movement == "left":
                    pyautogui.press("left")
                elif movement == "right":
                    pyautogui.press("right")
                elif movement == "up":
                    pyautogui.press("up")
                elif movement == "down":
                    pyautogui.press("down")

            if recognize_hoverboard_toggle(hand_landmarks):
                if not hoverboard_active:
                    hoverboard_active = True
                    print("Hoverboard Activated/Deactivated")
                    pyautogui.press("h")
            else:
                hoverboard_active = False

            if recognize_enter_key(hand_landmarks):
                print("Enter key pressed")
                pyautogui.press("enter")

    cv2.imshow("Hand Tracking", image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()