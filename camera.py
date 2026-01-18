import cv2
import numpy as np

cap = None

# Brightness + threshold tuning
BRIGHTNESS_FACTOR = 1.0   # <1 = darker
COL_THRESHOLD = 70           # 0–255
THRESHOLD = 100           # 0–255

def init():
    global cap
    # Open camera
    cap = cv2.VideoCapture(0)

    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.0)  # manual
    cap.set(cv2.CAP_PROP_EXPOSURE, -6)        # brighter
    cap.set(cv2.CAP_PROP_GAIN, 16)            # reduce noise

    for prop in [
        cv2.CAP_PROP_AUTO_EXPOSURE,
        cv2.CAP_PROP_EXPOSURE,
        cv2.CAP_PROP_GAIN,
        cv2.CAP_PROP_BRIGHTNESS
    ]:
        print(prop, cap.get(prop))

def get_hitbox():
    ret, frame = cap.read()
    if not ret:
        return None
    b, g, r = cv2.split(frame)

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Reduce brightness
    dark = np.clip(gray * BRIGHTNESS_FACTOR, 0, 255).astype(np.uint8)

    # Bright-pixel hitbox (boolean array)
    # hitbox   = (r > COL_THRESHOLD) & (r > g) & (r > b)
    # hitbox = (g > COL_THRESHOLD) & (g > r) & (g > b)
    # hitbox  = (b > THRESHOLD) & (b > g) & (b > r)
    hitbox = dark >= THRESHOLD

    # Quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        return None
    
    return hitbox, frame

def clean():
    cap.release()   
    cv2.destroyAllWindows()
