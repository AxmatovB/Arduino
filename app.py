import os
import time
import glob
import cv2
import mediapipe as mp
import serial

# ===== SETTINGS =====
CAMERA_INDEX = 0
SER_BAUD = 115200

STABLE_FRAMES_REQUIRED = 6
SEND_COOLDOWN_SEC = 0.12
# ====================

def find_arduino_port():
    ports = glob.glob("/dev/ttyACM*") + glob.glob("/dev/ttyUSB*")
    return ports[0] if ports else None

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

def count_fingers(hand_landmarks, handedness_label):
    lm = hand_landmarks.landmark
    fingers = 0

    # thumb
    if handedness_label == "Right":
        if lm[4].x < lm[3].x:
            fingers += 1
    else:
        if lm[4].x > lm[3].x:
            fingers += 1

    # other fingers
    if lm[8].y  < lm[6].y:  fingers += 1
    if lm[12].y < lm[10].y: fingers += 1
    if lm[16].y < lm[14].y: fingers += 1
    if lm[20].y < lm[18].y: fingers += 1

    return max(0, min(5, fingers))

def draw_indicators(frame, active):
    h, w = frame.shape[:2]
    y = 55
    r = 22
    gap = 70
    start_x = w // 2 - gap * 2

    for i in range(1, 6):
        x = start_x + (i - 1) * gap
        color = (0, 0, 255) if i == active else (0, 200, 0)
        cv2.circle(frame, (x, y), r, color, -1)
        cv2.circle(frame, (x, y), r, (255, 255, 255), 2)
        cv2.putText(frame, str(i), (x - 6, y + 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (10, 10, 10), 2)

    cv2.putText(frame, f"FINGERS: {active}", (20, h - 18),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (230, 230, 230), 2)

def main():
    # Serial connect
    ser = None
    port = find_arduino_port()
    if not port:
        print("❌ Arduino topilmadi (/dev/ttyACM* yoki /dev/ttyUSB*). Chiqyapman.")
        return

    try:
        ser = serial.Serial(port, SER_BAUD, timeout=0.1)
        time.sleep(1.2)  # Arduino reset bo'lishi mumkin
        print("✅ Arduino port:", port)
    except Exception as e:
        print("❌ Arduino ochilmadi:", e)
        return

    # Camera
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("❌ Kamera ochilmadi. CAMERA_INDEX 0/1/2 qilib ko'ring.")
        ser.close()
        return

    last_raw = -1
    stable_count = 0
    active = 0

    last_sent = 999
    last_send_ts = 0.0

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6
    ) as hands:

        while True:
            # Arduino uzilib qolsa -> ilovani yopamiz
            if port and (not os.path.exists(port)):
                print("🔌 Arduino uzildi. Ilova yopildi.")
                break

            ok, frame = cap.read()
            if not ok:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = hands.process(rgb)

            raw = 0
            if res.multi_hand_landmarks and res.multi_handedness:
                hand_lm = res.multi_hand_landmarks[0]
                handed = res.multi_handedness[0].classification[0].label
                raw = count_fingers(hand_lm, handed)
                mp_draw.draw_landmarks(frame, hand_lm, mp_hands.HAND_CONNECTIONS)

            # stabilize
            if raw == last_raw:
                stable_count += 1
            else:
                last_raw = raw
                stable_count = 1

            if stable_count >= STABLE_FRAMES_REQUIRED:
                active = raw

            # PC indikator
            indicator = active if active in (1,2,3,4,5) else 0
            draw_indicators(frame, indicator)

            # Arduino'ga yuborish: 1..5 yoki 0
            target = indicator
            now = time.time()
            changed = (target != last_sent)
            cooldown_ok = (now - last_send_ts) > SEND_COOLDOWN_SEC

            if changed and cooldown_ok:
                try:
                    ser.write(f"{target}\n".encode())
                    last_sent = target
                    last_send_ts = now
                except Exception as e:
                    print("🔌 Serial uzildi:", e)
                    break

            cv2.imshow("Hand Panel (press Q to quit)", frame)
            k = cv2.waitKey(1) & 0xFF
            if k in (ord('q'), ord('Q')):
                break

    cap.release()
    cv2.destroyAllWindows()
    try:
        ser.close()
    except Exception:
        pass

if __name__ == "__main__":
    main()
