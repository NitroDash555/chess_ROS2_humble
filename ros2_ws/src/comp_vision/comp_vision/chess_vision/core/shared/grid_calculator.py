from . import PerspectiveTransformer
from ...debug import is_debug
from chess_common import repo_paths
import os
import numpy as np
import cv2


class GridCalculator:

    def __init__(self):
        pass

    @staticmethod
    def plot_grid_on_transformed_image(image, padding=30):
        corners = np.array([[padding, padding],
                            [image.size[0] - padding, padding],
                            [padding, image.size[1] - padding],
                            [image.size[0] - padding, image.size[1] - padding]])

        corners = PerspectiveTransformer.order_points(corners)
        TL, TR, BL, BR = corners[0], corners[1], corners[3], corners[2]

        def interpolate(xy0, xy1):
            x0, y0 = xy0
            x1, y1 = xy1
            dx, dy = (x1 - x0) / 8, (y1 - y0) / 8
            return [(x0 + i * dx, y0 + i * dy) for i in range(9)]

        ptsT = interpolate(TL, TR)
        ptsL = interpolate(TL, BL)

        if is_debug():
            debug_img = np.asarray(image).copy()
            for a, b in zip(ptsL, interpolate(TR, BR)):
                cv2.line(debug_img, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), (0, 0, 255), 2)
            for a, b in zip(ptsT, interpolate(BL, BR)):
                cv2.line(debug_img, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), (0, 0, 255), 2)
            cv2.imwrite(os.path.join(repo_paths.pipe_dir(), '03_grid.png'), cv2.cvtColor(debug_img, cv2.COLOR_RGB2BGR))

        return ptsT, ptsL
    

    @staticmethod
    def grid_drawer(ptsT, ptsL, detections, boxes):
        if not is_debug():
            return
        import matplotlib.pyplot as plt
        height = int(ptsL[-1][1] - ptsL[0][1] + 100)  # Add padding
        width = int(ptsT[-1][0] - ptsT[0][0] + 100)   # Add padding
        img_copy = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Adjust points to account for padding
        padding = 50
        ptsT = [(x[0], x[1] + padding) for x in ptsT]
        ptsL = [(x[0] + padding, x[1]) for x in ptsL]
        
        # Draw vertical lines (using ptsT)
        for pt in ptsT:
            start_point = (int(pt[0]), int(ptsL[0][1]))  # Top point
            end_point = (int(pt[0]), int(ptsL[-1][1]))   # Bottom point
            cv2.line(img_copy, start_point, end_point, (255, 255, 255), 2)

        # Draw horizontal lines (using ptsL)
        for pt in ptsL:
            start_point = (int(ptsT[0][0]), int(pt[1]))  # Left point
            end_point = (int(ptsT[-1][0]), int(pt[1]))   # Right point
            cv2.line(img_copy, start_point, end_point, (255, 255, 255), 2)

        # Dictionary for piece names
        di = {0: 'b', 1: 'k', 2: 'n', 3: 'p', 4: 'q', 5: 'r', 
            6: 'B', 7: 'K', 8: 'N', 9: 'P', 10: 'Q', 11: 'R'}

        # Draw detected pieces
        for i, detection in enumerate(detections):
            x1, y1, x2, y2 = map(int, detection[:4])
            
            # Get piece name
            piece_class = boxes.cls[i].item()
            piece_name = f"{di[piece_class]}"
            
            # Calculate text position (center of box)
            text_x = int((x1 + x2) / 2) + padding
            text_y = int((y1 + y2) / 2) + padding
            
            # Add text label with better visibility
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1.2
            thickness = 2
            
            # Get text size for centering
            (text_width, text_height), _ = cv2.getTextSize(piece_name, font, font_scale, thickness)
            text_x -= text_width // 2
            text_y += text_height // 2

            # Draw text
            cv2.putText(img_copy, piece_name, 
                    (text_x, text_y),
                    font, font_scale, (0, 255, 0), thickness)
            
        plt.figure(figsize=(12, 12))

        plt.imshow(img_copy)
        plt.axis('off')
        plt.savefig(os.path.join(repo_paths.pipe_dir(), '05_grid_with_pieces.png'), bbox_inches='tight', pad_inches=0)
        plt.close()

           



