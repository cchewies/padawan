import camera as c
import time
import random
import cv2
import numpy as np

# -------- Game config --------
GAME_W, GAME_H = 1920, 1080      # window size
HITBOX_W, HITBOX_H = 240, 135    # downsized hitbox for collision
SPAWN_INTERVAL = 0.7              # seconds between bolts
BOLT_BASE_RADIUS = 0.15
BOLT_SPEED = 500                # pixels per second toward player
FLASH_DURATION = 0.2
MARGIN = int((HITBOX_H - 5) / 2)
CLAMP_MARGIN = 20
VX = 200
VY = 130
GROWTH_COEFF = 7

# -------- Game state --------
bolts = []
last_spawn_time = 0
flash_time = 0

# Create game window
cv2.namedWindow("Game", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Game", GAME_W, GAME_H)

c.init()

class Bolt:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z          # distance from player
        self.hit = False
        self.spawn_time = time.time()
        self.z_initial = z  # store initial distance

        # Random small drift per second
        self.vx = random.uniform(-VX, VX)  # pixels/sec horizontal
        self.vy = random.uniform(-VY, VY)  # pixels/sec vertical

    def update(self, dt):
        # Move bolt
        self.z -= BOLT_SPEED * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Clamp to window bounds
        self.x = np.clip(self.x, CLAMP_MARGIN, GAME_W-1-CLAMP_MARGIN)
        self.y = np.clip(self.y, CLAMP_MARGIN, GAME_H-1-CLAMP_MARGIN)

    def get_radius(self):
        fraction_traveled = 1 - self.z / self.z_initial
        scale = np.exp(GROWTH_COEFF * fraction_traveled)
        return max(5, int(BOLT_BASE_RADIUS * scale))

# Main loop
prev_time = time.time()

while True:
    now = time.time()
    dt = now - prev_time
    prev_time = now

    result = c.get_hitbox()
    if result is None:
        break
    hitbox, _ = result

    # Downsize hitbox for fast collision
    small_hitbox = cv2.resize(hitbox.astype(np.uint8), (HITBOX_W, HITBOX_H)) > 0

    # -------- SINGLE FRAME BUFFER --------
    frame = np.zeros((GAME_H, GAME_W, 3), dtype=np.uint8)  # black background
    # now everything (bolts, hitbox, flash) will draw onto this single buffer

    # Spawn new bolts
    if now - last_spawn_time >= SPAWN_INTERVAL:
        x_spawn = random.randint(MARGIN, GAME_W-MARGIN)
        y_spawn = random.randint(MARGIN, GAME_H-MARGIN)
        z_spawn = 1000  # far away
        bolts.append(Bolt(x_spawn, y_spawn, z_spawn))
        last_spawn_time = now

    # ---- Draw bolts ----
    for bolt in bolts[:]:
        bolt.update(dt)
        radius = bolt.get_radius()

        # Check if bolt reaches player (screen plane)
        if bolt.z <= 0:
            hx = int(bolt.x * HITBOX_W / GAME_W)
            hy = int(bolt.y * HITBOX_H / GAME_H)
            collision_radius = int(radius * HITBOX_W / GAME_W)

            x0 = max(hx - collision_radius, 0)
            x1 = min(hx + collision_radius, HITBOX_W)
            y0 = max(hy - collision_radius, 0)
            y1 = min(hy + collision_radius, HITBOX_H)

            if y1 > y0 and x1 > x0:
                sub_hitbox = small_hitbox[y0:y1, x0:x1]
                if sub_hitbox.any():
                    h_sub, w_sub = y1 - y0, x1 - x0
                    yy, xx = np.ogrid[0:h_sub, 0:w_sub]
                    mask = (xx - (hx - x0))**2 + (yy - (hy - y0))**2 <= collision_radius**2
                    if np.any(sub_hitbox & mask):
                        bolt.hit = True

            bolts.remove(bolt)
            if not bolt.hit:
                flash_time = now
            continue

        # Draw bolt in flight
        cv2.circle(frame, (int(bolt.x), int(bolt.y)), radius, (255, 0, 0), -1)

    # ---- Overlay hitbox on top (directly on frame) ----
    hit_overlay = cv2.resize(small_hitbox.astype(np.uint8)*255, (GAME_W, GAME_H))
    frame[:, :, 1] = np.maximum(frame[:, :, 1], hit_overlay)  # green channel
    alpha_hit = 0.5
    frame = cv2.addWeighted(frame, 1, frame, alpha_hit, 0)

    # ---- Red flash if active (draw on same buffer) ----
    if now - flash_time < FLASH_DURATION:
        overlay = np.full_like(frame, (0, 0, 255))
        alpha = 0.4
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

    # Display the single frame buffer
    cv2.imshow("Game", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

c.clean()
cv2.destroyAllWindows()
