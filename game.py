import pygame
import cv2
import numpy as np
from pygame import surfarray


# Open camera
cap = cv2.VideoCapture(1)
cv2.resizeWindow("Green", 1900, 1000)


# Brightness + threshold tuning
BRIGHTNESS_FACTOR = 1.0   # <1 = darker
COL_THRESHOLD = 70           # 0–255
THRESHOLD = 100           # 0–255

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

def hitbox():
    ret, frame = cap.read()
    #if not ret:
    #    break
    b, g, r = cv2.split(frame)
    
    r_img = cv2.merge([np.zeros_like(r), np.zeros_like(r), r])
    g_img = cv2.merge([np.zeros_like(g), g, np.zeros_like(g)])
    b_img = cv2.merge([b, np.zeros_like(b), np.zeros_like(b)])

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Reduce brightness
    dark = np.clip(gray * BRIGHTNESS_FACTOR, 0, 255).astype(np.uint8)

    # Bright-pixel hitbox (boolean array)
    red_mask   = (r > COL_THRESHOLD) & (r > g) & (r > b)
    green_mask = (g > COL_THRESHOLD) & (g > r) & (g > b)
    blue_mask  = (b > THRESHOLD) & (b > g) & (b > r)
    hitbox = dark >= THRESHOLD

    # Convert hitbox to visible image
    r_hitbox = (red_mask * 255).astype(np.uint8)
    g_hitbox = (green_mask * 255).astype(np.uint8)
    b_hitbox = (blue_mask * 255).astype(np.uint8)
    hitbox_img = (hitbox * 255).astype(np.uint8)

    # Show results
    return hitbox_img
    # Quit
    #if cv2.waitKey(1) & 0xFF == ord('q'):
    #    break


# activate the pygame library .
pygame.init()
X = 1900
Y = 1000

# create the display surface object
# of specific dimension..e(X, Y).
scrn = pygame.display.set_mode((X, Y))

# set the pygame window name
pygame.display.set_caption('image')

# create a surface object, image is drawn on it.
imp = pygame.image.load("desert_bg.jpg").convert()
DEFAULT_IMAGE_SIZE = (X, Y)
imp = pygame.transform.scale(imp, DEFAULT_IMAGE_SIZE)


while True:
    saber = hitbox()
    saber = surfarray.make_surface(saber)
    pygame.display.update()

# deactivates the pygame library
pygame.quit()
