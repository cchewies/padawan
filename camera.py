import cv2
import numpy as np

# ---------- Global config ----------
BRIGHTNESS_FACTOR = 1.0
COL_THRESHOLD = 70
THRESHOLD = 100

cap = None
mode = "bright"   # bright, red, green, blue

def init():
    global cap

    # Open camera
    cap = cv2.VideoCapture(1)

    # Create windows
    cv2.namedWindow("Green", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Green", 1900, 1000)

    # Camera settings
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.0)  # manual
    cap.set(cv2.CAP_PROP_EXPOSURE, -6)
    cap.set(cv2.CAP_PROP_GAIN, 16)

    # Print camera properties
    for prop in [
        cv2.CAP_PROP_AUTO_EXPOSURE,
        cv2.CAP_PROP_EXPOSURE,
        cv2.CAP_PROP_GAIN,
        cv2.CAP_PROP_BRIGHTNESS
    ]:
        print(prop, cap.get(prop))


def loop():
    global mode

    ret, frame = cap.read()
    if not ret:
        return None

    b, g, r = cv2.split(frame)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    dark = np.clip(gray * BRIGHTNESS_FACTOR, 0, 255).astype(np.uint8)

    # --- Select hitbox mode ---
    if mode == "bright":
        hitbox = dark >= THRESHOLD
        label = "Bright Pixel"
    elif mode == "red":
        hitbox = (r > COL_THRESHOLD) & (r > g) & (r > b)
        label = "Red"
    elif mode == "green":
        hitbox = (g > COL_THRESHOLD) & (g > r) & (g > b)
        label = "Green"
    elif mode == "blue":
        hitbox = (b > COL_THRESHOLD) & (b > g) & (b > r)
        label = "Blue"

    # --- Visual overlay ---
    overlay = frame.copy()
    overlay[hitbox] = [0, 0, 255]
    output = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)

    cv2.putText(
        output,
        f"Mode: {label}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.imshow("View", output)

    # --- Input handling ---
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        return None
    elif key == ord('w'):
        mode = "bright"
    elif key == ord('r'):
        mode = "red"
    elif key == ord('g'):
        mode = "green"
    elif key == ord('b'):
        mode = "blue"

    return hitbox


# ---------- Main ----------
init()
while loop():
    pass

cap.release()
cv2.destroyAllWindows()
