import cv2
import numpy as np
import os

def remove_background(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None: return
    
    if img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        
    gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
    _, thresh = cv2.threshold(gray, 20, 255, cv2.THRESH_BINARY)
    
    h, w = thresh.shape
    im_in = thresh.copy()
    mask_ff = np.zeros((h+2, w+2), np.uint8)
    
    # Floodfill from corners
    cv2.floodFill(im_in, mask_ff, (0,0), 255)
    cv2.floodFill(im_in, mask_ff, (0,h-1), 255)
    cv2.floodFill(im_in, mask_ff, (w-1,0), 255)
    cv2.floodFill(im_in, mask_ff, (w-1,h-1), 255)
    
    im_floodfill_inv = cv2.bitwise_not(im_in)
    im_out = thresh | im_floodfill_inv
    
    # Smooth edges
    im_out = cv2.GaussianBlur(im_out, (3, 3), 0)
    _, im_out = cv2.threshold(im_out, 127, 255, cv2.THRESH_BINARY)

    img[:, :, 3] = im_out
    cv2.imwrite(image_path, img)
    print("Processed", image_path)

images = ['boss_commando.png', 'boss_blue_vest.png', 'boss_techno.png', 'boss_yolk_king.png', 'boss.png']
base_path = 'd:/gamebanga2d/chicken_shooting_game/assets/images/'
for img_name in images:
    path = os.path.join(base_path, img_name)
    if os.path.exists(path):
        remove_background(path)
