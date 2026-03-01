import cv2
import mediapipe as mp
import numpy as np
import os
import time
from datetime import datetime

# -------------------------------
# Helper functions
# -------------------------------

def fingers_up(hand_landmarks, h, w):
    lm = hand_landmarks.landmark
    points = [(int(p.x * w), int(p.y * h)) for p in lm]

    fingers = []

    # Thumb check for mirrored image
    if points[4][0] < points[3][0]:
        fingers.append(1)
    else:
        fingers.append(0)

    tip_ids = [8, 12, 16, 20]
    pip_ids = [6, 10, 14, 18]

    for tip, pip in zip(tip_ids, pip_ids):
        if points[tip][1] < points[pip][1]:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers, points

def count_fingers(fingers):
    return sum(fingers)

def save_canvas(canvas, save_dir="saved_drawings"):
    os.makedirs(save_dir, exist_ok=True)
    filename = datetime.now().strftime("drawing_%Y%m%d_%H%M%S.png")
    path = os.path.join(save_dir, filename)

    if np.any(canvas != 255):
        cv2.imwrite(path, canvas)
        return path
    return None

def draw_button(frame, rect, text, fill_color, selected=False, text_color=(85, 85, 85)):
    x1, y1, x2, y2 = rect
    cv2.rectangle(frame, (x1, y1), (x2, y2), fill_color, -1)
    border_color = (255, 255, 255) if selected else (225, 225, 225)
    border_thickness = 3 if selected else 2
    cv2.rectangle(frame, (x1, y1), (x2, y2), border_color, border_thickness)
    cv2.putText(frame, text, (x1 + 10, y1 + 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, text_color, 2)

def get_clicked_button(x, y, buttons):
    for name, (x1, y1, x2, y2), _ in buttons:
        if x1 <= x <= x2 and y1 <= y <= y2:
            return name
    return None

def get_size_value(size_name):
    if size_name == "S":
        return 4
    elif size_name == "M":
        return 8
    elif size_name == "L":
        return 14
    return 8

def draw_toolbar(frame, selected_color_name, brush_size_name):
    color_buttons = [
        ("PINK",   (20, 15, 110, 55),  (214, 209, 255)),
        ("MINT",   (120, 15, 210, 55), (214, 248, 224)),
        ("BLUE",   (220, 15, 310, 55), (255, 236, 219)),
        ("LAV",    (320, 15, 410, 55), (239, 222, 245)),
        ("PEACH",  (420, 15, 530, 55), (203, 232, 255)),
        ("ERASER", (540, 15, 660, 55), (230, 230, 230)),
    ]

    size_buttons = [
        ("S", (680, 15, 730, 55), (248, 248, 248)),
        ("M", (740, 15, 790, 55), (248, 248, 248)),
        ("L", (800, 15, 850, 55), (248, 248, 248)),
    ]

    action_buttons = [
        ("UNDO",  (20, 70, 120, 110),  (246, 241, 235)),
        ("SAVE",  (130, 70, 230, 110), (236, 246, 238)),
        ("CLEAR", (240, 70, 360, 110), (246, 236, 236)),
    ]

    for name, rect, color in color_buttons:
        draw_button(frame, rect, name, color, selected=(name == selected_color_name))

    for name, rect, color in size_buttons:
        draw_button(frame, rect, name, color, selected=(name == brush_size_name))

    for name, rect, color in action_buttons:
        draw_button(frame, rect, name, color, selected=False)

    return color_buttons, size_buttons, action_buttons

def rebuild_canvas(canvas_shape, stroke_history, background_color=255):
    canvas = np.ones(canvas_shape, dtype=np.uint8) * background_color
    for stroke in stroke_history:
        for p1, p2, color, thickness in stroke:
            cv2.line(canvas, p1, p2, color, thickness)
    return canvas

# -------------------------------
# Pretty intro screen
# -------------------------------

def draw_rounded_panel(img, top_left, bottom_right, color, radius=25):
    x1, y1 = top_left
    x2, y2 = bottom_right

    overlay = img.copy()
    cv2.rectangle(overlay, (x1 + radius, y1), (x2 - radius, y2), color, -1)
    cv2.rectangle(overlay, (x1, y1 + radius), (x2, y2 - radius), color, -1)
    cv2.circle(overlay, (x1 + radius, y1 + radius), radius, color, -1)
    cv2.circle(overlay, (x2 - radius, y1 + radius), radius, color, -1)
    cv2.circle(overlay, (x1 + radius, y2 - radius), radius, color, -1)
    cv2.circle(overlay, (x2 - radius, y2 - radius), radius, color, -1)
    return overlay

def show_intro_screen():
    window_name = "AirDraw Pastel Edition v3"
    h, w = 720, 1280

    start = time.time()
    duration = 2.0

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    while True:
        elapsed = time.time() - start
        if elapsed >= duration:
            break

        progress = elapsed / duration

        intro = np.ones((h, w, 3), dtype=np.uint8) * 248

        # Soft pastel gradient-ish bands
        cv2.rectangle(intro, (0, 0), (w, 110), (239, 222, 245), -1)
        cv2.rectangle(intro, (0, 610), (w, h), (214, 248, 224), -1)

        # Floating pastel circles
        circles = [
            ((170, 150), 70, (214, 209, 255)),
            ((1080, 150), 75, (203, 232, 255)),
            ((210, 560), 55, (255, 236, 219)),
            ((1060, 555), 60, (239, 222, 245)),
            ((640, 120), 35, (236, 246, 238)),
        ]
        for (cx, cy), r, color in circles:
            cv2.circle(intro, (cx, cy), r, color, -1)

        # Center panel
        intro = draw_rounded_panel(intro, (220, 180), (1060, 520), (252, 252, 252), radius=30)

        # Tiny fade/slide effect
        title_y = int(280 + (1 - progress) * 20)
        sub_y = int(350 + (1 - progress) * 15)
        line_y = int(425 + (1 - progress) * 10)

        # Title
        cv2.putText(
            intro,
            "Computer Vision Project",
            (300, title_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.6,
            (92, 92, 92),
            4
        )

        # Name
        cv2.putText(
            intro,
            "by Navyatha G",
            (470, sub_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.1,
            (120, 120, 120),
            3
        )

        # App name
        cv2.putText(
            intro,
            "Launching AirDraw Pastel Edition...",
            (355, line_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (145, 145, 145),
            2
        )

        # Decorative mini text
        cv2.putText(
            intro,
            "Hand Tracking / Gesture Drawing / OpenCV + MediaPipe",
            (340, 485),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.72,
            (160, 160, 160),
            2
        )

        cv2.imshow(window_name, intro)
        key = cv2.waitKey(30) & 0xFF
        if key == 13 or key == ord('q') or key == 27:
            break

# -------------------------------
# Main app
# -------------------------------

def main():
    show_intro_screen()

    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils

    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    # Change to 0 / 1 / 2 depending on your Mac camera
    cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    canvas = None
    prev_x, prev_y = 0, 0
    smooth_x, smooth_y = 0, 0
    smoothing = 0.35

    selected_color_name = "PINK"
    brush_size_name = "M"
    status_message = "Ready"
    status_timer = 0

    color_map = {
        "PINK":   (214, 209, 255),
        "MINT":   (214, 248, 224),
        "BLUE":   (255, 236, 219),
        "LAV":    (239, 222, 245),
        "PEACH":  (203, 232, 255),
        "ERASER": (255, 255, 255),
    }

    stroke_history = []
    current_stroke_points = []

    save_hold_start = None
    clear_hold_start = None
    HOLD_TIME = 0.8

    print("Controls:")
    print("- Index finger only: Draw")
    print("- Index + middle: Select toolbar buttons")
    print("- Hold all 5 fingers up: Clear")
    print("- Hold thumb + index up: Save")
    print("- Keyboard: u=undo, c=clear, s=save, q=quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        if canvas is None:
            canvas = np.ones_like(frame) * 255

        soft_bg = cv2.GaussianBlur(frame, (21, 21), 0)
        soft_bg = cv2.addWeighted(frame, 0.35, soft_bg, 0.65, 0)

        toolbar_frame = soft_bg.copy()
        color_buttons, size_buttons, action_buttons = draw_toolbar(
            toolbar_frame, selected_color_name, brush_size_name
        )

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        mode_text = "No Hand"
        finger_count_text = "Fingers: 0"

        if status_timer > 0:
            status_timer -= 1

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]

            mp_drawing.draw_landmarks(
                toolbar_frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            fingers, points = fingers_up(hand_landmarks, h, w)
            finger_count = count_fingers(fingers)
            finger_count_text = f"Fingers: {finger_count}"

            index_tip = points[8]
            cv2.circle(toolbar_frame, index_tip, 8, (255, 255, 255), cv2.FILLED)

            if fingers == [0, 1, 0, 0, 0]:
                mode_text = "DRAW"
                save_hold_start = None
                clear_hold_start = None

                x, y = index_tip

                if prev_x == 0 and prev_y == 0:
                    prev_x, prev_y = x, y
                    current_stroke_points = []

                smooth_x = int(prev_x * (1 - smoothing) + x * smoothing) if prev_x != 0 else x
                smooth_y = int(prev_y * (1 - smoothing) + y * smoothing) if prev_y != 0 else y

                selected_color = color_map[selected_color_name]
                thickness = 28 if selected_color_name == "ERASER" else get_size_value(brush_size_name)

                cv2.line(canvas, (prev_x, prev_y), (smooth_x, smooth_y), selected_color, thickness)
                current_stroke_points.append(((prev_x, prev_y), (smooth_x, smooth_y), selected_color, thickness))

                prev_x, prev_y = smooth_x, smooth_y

            elif fingers == [0, 1, 1, 0, 0]:
                mode_text = "SELECT"
                save_hold_start = None
                clear_hold_start = None

                if current_stroke_points:
                    stroke_history.append(current_stroke_points)
                    current_stroke_points = []

                prev_x, prev_y = 0, 0
                smooth_x, smooth_y = 0, 0

                x, y = index_tip
                cv2.rectangle(toolbar_frame, (x - 14, y - 14), (x + 14, y + 14), (255, 255, 255), 2)

                selected_tool = get_clicked_button(x, y, color_buttons)
                if selected_tool:
                    selected_color_name = selected_tool
                    status_message = f"Selected: {selected_tool}"
                    status_timer = 20

                selected_size = get_clicked_button(x, y, size_buttons)
                if selected_size:
                    brush_size_name = selected_size
                    status_message = f"Brush size: {selected_size}"
                    status_timer = 20

                selected_action = get_clicked_button(x, y, action_buttons)
                if selected_action == "UNDO":
                    if stroke_history:
                        stroke_history.pop()
                        canvas = rebuild_canvas(canvas.shape, stroke_history)
                        status_message = "Undo"
                        status_timer = 20

                elif selected_action == "SAVE":
                    saved_path = save_canvas(canvas)
                    if saved_path:
                        status_message = f"Saved: {os.path.basename(saved_path)}"
                    else:
                        status_message = "Nothing to save"
                    status_timer = 20

                elif selected_action == "CLEAR":
                    canvas = np.ones_like(frame) * 255
                    stroke_history = []
                    current_stroke_points = []
                    status_message = "Canvas cleared"
                    status_timer = 20

            elif fingers == [1, 1, 1, 1, 1]:
                mode_text = "HOLD CLEAR"
                save_hold_start = None

                if current_stroke_points:
                    stroke_history.append(current_stroke_points)
                    current_stroke_points = []

                prev_x, prev_y = 0, 0
                smooth_x, smooth_y = 0, 0

                if clear_hold_start is None:
                    clear_hold_start = time.time()

                held = time.time() - clear_hold_start
                status_message = f"Hold clear: {held:.1f}s"

                if held >= HOLD_TIME:
                    canvas = np.ones_like(frame) * 255
                    stroke_history = []
                    current_stroke_points = []
                    status_message = "Canvas cleared"
                    status_timer = 20
                    clear_hold_start = None

            elif fingers == [1, 1, 0, 0, 0]:
                mode_text = "HOLD SAVE"
                clear_hold_start = None

                if current_stroke_points:
                    stroke_history.append(current_stroke_points)
                    current_stroke_points = []

                prev_x, prev_y = 0, 0
                smooth_x, smooth_y = 0, 0

                if save_hold_start is None:
                    save_hold_start = time.time()

                held = time.time() - save_hold_start
                status_message = f"Hold save: {held:.1f}s"

                if held >= HOLD_TIME:
                    saved_path = save_canvas(canvas)
                    if saved_path:
                        status_message = f"Saved: {os.path.basename(saved_path)}"
                    else:
                        status_message = "Nothing to save"
                    status_timer = 20
                    save_hold_start = None

            else:
                mode_text = "IDLE"
                save_hold_start = None
                clear_hold_start = None

                if current_stroke_points:
                    stroke_history.append(current_stroke_points)
                    current_stroke_points = []

                prev_x, prev_y = 0, 0
                smooth_x, smooth_y = 0, 0

        else:
            save_hold_start = None
            clear_hold_start = None

            if current_stroke_points:
                stroke_history.append(current_stroke_points)
                current_stroke_points = []

            prev_x, prev_y = 0, 0
            smooth_x, smooth_y = 0, 0

        canvas_gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        _, ink_mask = cv2.threshold(canvas_gray, 250, 255, cv2.THRESH_BINARY_INV)

        drawing_only = cv2.bitwise_and(canvas, canvas, mask=ink_mask)
        ink_mask_3 = cv2.cvtColor(ink_mask, cv2.COLOR_GRAY2BGR)

        output = toolbar_frame.copy()
        output = np.where(ink_mask_3 > 0, drawing_only, output)

        cv2.rectangle(output, (380, 70), (550, 110), (249, 249, 249), -1)
        cv2.putText(output, f"Mode: {mode_text}", (390, 97),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.62, (95, 95, 95), 2)

        cv2.rectangle(output, (560, 70), (740, 110), (249, 249, 249), -1)
        cv2.putText(output, finger_count_text, (570, 97),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.62, (95, 95, 95), 2)

        cv2.rectangle(output, (750, 70), (1180, 110), (249, 249, 249), -1)
        cv2.putText(output, status_message, (760, 97),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.58, (95, 95, 95), 2)

        cv2.imshow("AirDraw Pastel Edition v3", output)

        key = cv2.waitKey(1) & 0xFF
        if key == 13 or key == ord('q') or key == 27:
            break
        elif key == ord('u'):
            if current_stroke_points:
                current_stroke_points = []
            elif stroke_history:
                stroke_history.pop()

            canvas = rebuild_canvas(canvas.shape, stroke_history)
            status_message = "Undo"
            status_timer = 20

        elif key == ord('c'):
            canvas = np.ones_like(frame) * 255
            stroke_history = []
            current_stroke_points = []
            status_message = "Canvas cleared"
            status_timer = 20

        elif key == ord('s'):
            saved_path = save_canvas(canvas)
            if saved_path:
                status_message = f"Saved: {os.path.basename(saved_path)}"
            else:
                status_message = "Nothing to save"
            status_timer = 20

    cap.release()
    cv2.destroyAllWindows()
    hands.close()

if __name__ == "__main__":
    main()