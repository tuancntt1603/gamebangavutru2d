import cv2
import pygame
import os
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class HandTracker:
    def __init__(self):
        self.use_fallback = True
        self.cap = None
        self.detector = None
        self.last_x = 0.5
        self.num_hands = 0
        
        # Model path
        model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'hand_landmarker.task')
        
        try:
            base_options = python.BaseOptions(model_asset_path=model_path)
            options = vision.HandLandmarkerOptions(
                base_options=base_options,
                num_hands=2, # Now supporting 2 hands for Slow Motion
                min_hand_detection_confidence=0.5,
                min_hand_presence_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.detector = vision.HandLandmarker.create_from_options(options)
            
            self.cap = cv2.VideoCapture(0)
            if self.cap.isOpened():
                self.use_fallback = False
                print("Status: Advanced Hand Tracking Initialized (Multi-Hand).")
            else:
                print("Status: Camera not accessible. Falling back to Mouse.")
        except Exception as e:
            print(f"Status: Hand tracking init failed ({e}). Falling back to Mouse.")

    def get_gestures(self):
        # Default: X, Y position, Shooting, FiveFingers, Fist, Num Hands, Camera Frame, Fingers
        gest = {"x": self.last_x, "y": 0.5, "shoot": False, "five_fingers": False, "fist": False, "hands": 0, "cam": None, "fingers": 1}
        
        if self.use_fallback:
            mouse_pos = pygame.mouse.get_pos()
            gest["x"] = mouse_pos[0] / 1200 
            gest["y"] = mouse_pos[1] / 800
            gest["shoot"] = pygame.mouse.get_pressed()[0]
            # Key fallbacks for skills
            keys = pygame.key.get_pressed()
            gest["five_fingers"] = keys[pygame.K_u] # U for Ultimate/Rocket
            gest["fist"] = keys[pygame.K_b] # B for Bomb
            gest["hands"] = 2 if keys[pygame.K_s] else 1 # S for Slowmo
            return gest

        try:
            success, frame = self.cap.read()
            if not success: return gest

            rgb_frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            results = self.detector.detect(mp_image)

            gest["hands"] = len(results.hand_landmarks) if results.hand_landmarks else 0
            
            if results.hand_landmarks:
                landmarks = results.hand_landmarks[0]
                # Index finger tip is landmark 8
                finger_tip = landmarks[8]
                gest["x"] = finger_tip.x
                gest["y"] = finger_tip.y
                self.last_x = finger_tip.x
                
                # 1. Pinch (Shoot) - Thumb fingertip (4) to Index fingertip (8)
                thumb_tip = landmarks[4]
                d_pinch = ((thumb_tip.x - finger_tip.x)**2 + (thumb_tip.y - finger_tip.y)**2)**0.5
                if d_pinch < 0.08: 
                    gest["shoot"] = True
                else:
                    gest["shoot"] = False
                
                # Draw Visual Feedback on frame
                h, w, _ = rgb_frame.shape
                # Index (Aim) - CYAN
                cv2.circle(rgb_frame, (int(landmarks[8].x * w), int(landmarks[8].y * h)), 8, (0, 255, 255), -1)
                # Thumb - MAGENTA
                cv2.circle(rgb_frame, (int(landmarks[4].x * w), int(landmarks[4].y * h)), 8, (255, 0, 255), -1)
                
                # Count extended fingers (Tips: 8, 12, 16, 20. MCPs: 5, 9, 13, 17)
                extended = []
                for tip, mcp in [(8, 5), (12, 9), (16, 13), (20, 17)]:
                    dist = ((landmarks[tip].x-landmarks[mcp].x)**2 + (landmarks[tip].y-landmarks[mcp].y)**2)**0.5
                    if dist > 0.1: extended.append(tip)
                
                # Check thumb (Tip: 4, MCP: 2)
                dist_thumb = ((landmarks[4].x-landmarks[2].x)**2 + (landmarks[4].y-landmarks[2].y)**2)**0.5
                if dist_thumb > 0.08: extended.append(4)
                
                gest["fingers"] = len(extended)

                # 2. Fist (All fingers curled near MCPs)
                is_fist = len(extended) == 0
                gest["fist"] = is_fist
                
                # 3. 5 ngón
                is_five = len(extended) == 5
                gest["five_fingers"] = is_five

            # Convert RGB Frame to Pygame Surface (Picture-in-Picture)
            debug_frame = cv2.resize(rgb_frame, (160, 120))
            gest["cam"] = pygame.image.frombuffer(debug_frame.tobytes(), debug_frame.shape[1::-1], "RGB")
            
            return gest
        except Exception:
            return gest

    def __del__(self):
        if self.cap: self.cap.release()
        if self.detector: self.detector.close()
