import os
import cv2
import numpy as np
from PIL import Image
from shapely.geometry import Polygon
from . import PiecesDetector, PerspectiveTransformer
from ...debug import is_debug

class ChessPieceMapper:

    @staticmethod
    def chess_pieces_detector(image):
        results = PiecesDetector.detect_pieces(image)
        boxes = results[0].boxes
        detections = boxes.xyxy.numpy() # type: ignore

        # Save debug image if DEBUG is true
        if is_debug():
            # Dictionary for piece names
            di = {0: 'b', 1: 'k', 2: 'n', 3: 'p', 4: 'q', 5: 'r', 6: 'B', 7: 'K', 8: 'N', 9: 'P', 10: 'Q', 11: 'R'}
            
            # Convert PIL Image to numpy array if needed
            if isinstance(image, Image.Image):
                img_array = np.array(image)
            else:
                img_array = image.copy()
            
            # Draw boxes and labels on the image
            for i, detection in enumerate(detections):
                x1, y1, x2, y2 = map(int, detection[:4])
                # Draw rectangle
                cv2.rectangle(img_array, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Get piece name and confidence
                piece_class = boxes.cls[i].item()
                confidence = float(boxes.conf[i].item()) * 100  # convert to percentage
                piece_name = f"{di[piece_class]} ({confidence:.0f}%)"
                
                # Calculate text position (center of box)
                text_x = int((x1 + x2) / 2)
                text_y = int((y1 + y2) / 2)
                
                # Get text size for centering
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.8
                thickness = 2
                (text_width, text_height), _ = cv2.getTextSize(piece_name, font, font_scale, thickness)
                
                # Draw text with background for better visibility
                cv2.putText(img_array, piece_name, 
                          (text_x - text_width//2, text_y + text_height//2),
                          font, font_scale, (0, 0, 0), thickness + 1)  # black outline
                cv2.putText(img_array, piece_name, 
                          (text_x - text_width//2, text_y + text_height//2),
                          font, font_scale, (255, 255, 255), thickness)  # white text
            
            # Save the image
            debug_image = Image.fromarray(img_array)
            debug_image.save('pipe/04_pieces.png')

        return detections, boxes

    @staticmethod
    def connect_square_to_detection(detections, square, boxes, iou_threshold=0.1, padding=30):
        di = {0: 'b', 1: 'k', 2: 'n', 3: 'p', 4: 'q', 5: 'r', 6: 'B', 7: 'K', 8: 'N', 9: 'P', 10: 'Q', 11: 'R'}
        list_of_iou = []

        for i, detection in enumerate(detections):
            # Adjust detection for padding
            box_x1, box_y1 = detection[0] - padding, detection[1] - padding
            box_x2, box_y2 = detection[2] - padding, detection[1] - padding
            box_x3, box_y3 = detection[2] - padding, detection[3] - padding
            box_x4, box_y4 = detection[0] - padding, detection[3] - padding
            
            if box_y4 - box_y1 > 60:
                box_complete = np.array([[box_x1, box_y1 + 40], [box_x2, box_y2 + 40], [box_x3, box_y3], [box_x4, box_y4]])
            else:
                box_complete = np.array([[box_x1, box_y1], [box_x2, box_y2], [box_x3, box_y3], [box_x4, box_y4]])

            if ChessPieceMapper.is_valid_polygon(box_complete) and ChessPieceMapper.is_valid_polygon(square):
                try:
                    iou = PerspectiveTransformer.calculate_iou(box_complete, square)
                    list_of_iou.append(iou)
                except Exception as e:
                    list_of_iou.append(0)
            else:
                list_of_iou.append(0)

        max_iou = max(list_of_iou)
        num = list_of_iou.index(max_iou)
        piece = boxes.cls[num].tolist()

        return di[piece] if max_iou > iou_threshold else "empty"

    @staticmethod
    def is_valid_polygon(points):
        return len(points) >= 3 and Polygon(points).is_valid

    @staticmethod
    def assign_pieces_to_squares(detections, boxes, squares, iou_threshold=0.1, padding=30):
        """
        Назначает каждую детекцию единственному квадрату (тому, где IoU максимален).
        """
        di = {0: 'b', 1: 'k', 2: 'n', 3: 'p', 4: 'q', 5: 'r',
              6: 'B', 7: 'K', 8: 'N', 9: 'P', 10: 'Q', 11: 'R'}

        best_square_for_det = {}
        used_squares = set()

        # Сортировка по уверенности
        confidences = boxes.conf.cpu().numpy() if hasattr(boxes.conf, 'cpu') else boxes.conf
        sorted_indices = np.argsort(-confidences)

        for idx in sorted_indices:
            detection = detections[idx]
            x1, y1, x2, y2 = detection[:4]

            box_x1 = x1 - padding
            box_y1 = y1 - padding
            box_x2 = x2 - padding
            box_y2 = y1 - padding
            box_x3 = x2 - padding
            box_y3 = y2 - padding
            box_x4 = x1 - padding
            box_y4 = y2 - padding

            if (box_y4 - box_y1) > 60:
                box_complete = np.array([[box_x1, box_y1 + 40],
                                         [box_x2, box_y2 + 40],
                                         [box_x3, box_y3],
                                         [box_x4, box_y4]])
            else:
                box_complete = np.array([[box_x1, box_y1],
                                         [box_x2, box_y2],
                                         [box_x3, box_y3],
                                         [box_x4, box_y4]])

            best_iou = 0
            best_square = None
            for square_name, square_vertices in squares.items():
                if square_name in used_squares:
                    continue
                if not (ChessPieceMapper.is_valid_polygon(box_complete) and ChessPieceMapper.is_valid_polygon(square_vertices)):
                    continue
                try:
                    iou = PerspectiveTransformer.calculate_iou(box_complete, square_vertices)
                    if iou > best_iou:
                        best_iou = iou
                        best_square = square_name
                except:
                    pass

            if best_square is not None and best_iou > iou_threshold:
                piece_class = int(boxes.cls[idx].item())
                piece_symbol = di.get(piece_class, 'empty')
                if piece_symbol != 'empty':
                    best_square_for_det[best_square] = piece_symbol
                    used_squares.add(best_square)

        result = {name: 'empty' for name in squares}
        for sq, piece in best_square_for_det.items():
            result[sq] = piece
        return result