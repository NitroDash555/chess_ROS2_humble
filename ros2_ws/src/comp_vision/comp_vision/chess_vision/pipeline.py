import os

import cv2
import numpy as np
from dotenv import load_dotenv

from .core.constants import error_messages
from .core.shared import (
    CornerDetector,
    PerspectiveTransformer,
    GridCalculator,
    ChessPieceMapper,
    FENConverter,
)
from .debug import is_debug
from .reconstruct_fen import reconstruct_fen, AmbiguousMoveError, NoValidMoveError

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def pipeline(image_path, prev_fen=None, logger=None):
    def log(message):
        if logger is not None:
            logger.info(message)
        else:
            print(message)

    if not prev_fen:
        prev_fen = START_FEN

    real_fen = prev_fen
    load_dotenv()
    step = 0
    if not os.path.exists("pipe"):
        os.makedirs("pipe")

    try:
        step = 1
        original_image = cv2.imread(image_path)
        if original_image is None:
            raise FileNotFoundError(f"Image not found at path: {image_path}")

        def preprocess_for_chess(img):
            def gray_world_balance(img):
                b, g, r = cv2.split(img)
                mean_b = np.mean(b)
                mean_g = np.mean(g)
                mean_r = np.mean(r)
                avg_gray = (mean_b + mean_g + mean_r) / 3
                scale_b = avg_gray / mean_b if mean_b != 0 else 1
                scale_g = avg_gray / mean_g if mean_g != 0 else 1
                scale_r = avg_gray / mean_r if mean_r != 0 else 1
                b = np.clip(b * scale_b, 0, 255).astype(np.uint8)
                g = np.clip(g * scale_g, 0, 255).astype(np.uint8)
                r = np.clip(r * scale_r, 0, 255).astype(np.uint8)
                return cv2.merge((b, g, r))

            img = gray_world_balance(img)
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.2, 0, 255).astype(np.uint8)
            img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            lab = cv2.merge((l, a, b))
            img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            return img

        log("1/8 Image Successfully Read")

        step = 2
        corners = CornerDetector.detect_corners(original_image)
        debug_img = original_image.copy()
        for corner in corners:
            cv2.circle(debug_img, tuple(corner.astype(int)), 10, (0, 0, 255), -1)
        if is_debug():
            cv2.imwrite("pipe/0_corners.jpg", debug_img)
        log("2/8 Corners Detected")

        step = 3
        transformed_image = PerspectiveTransformer.four_point_transform(
            image_path, corners)
        if is_debug():
            cv2.imwrite("pipe/1_warped.jpg", transformed_image)
        log("3/8 Perspective Transformation Completed")

        step = 4
        ptsT, ptsL = GridCalculator.plot_grid_on_transformed_image(
            transformed_image)
        log("4/8 Grid Points Calculated")

        step = 5
        original_image = preprocess_for_chess(original_image)
        detections, boxes = ChessPieceMapper.chess_pieces_detector(
            transformed_image)
        log("5/8 Chess Piece Detections")

        step = 6
        GridCalculator.grid_drawer(ptsT, ptsL, detections, boxes)
        log("6/8 Grid and Pieces Mapped Successfully")

        step = 7
        if hasattr(transformed_image, 'size'):
            transformed_image = np.array(transformed_image)
        predicted_fen = FENConverter.generate_fen(
            ptsT, ptsL, detections, boxes, transformed_image)
        log("7/8 Generated FEN")

        step = 8
        try:
            real_fen = reconstruct_fen(prev_fen, predicted_fen)
            log(f"Real FEN: {real_fen}")
        except AmbiguousMoveError as e:
            log(f"Ambiguous move: {e}, keeping previous FEN")
        except NoValidMoveError as e:
            log(f"Cannot reconstruct: {e}, keeping previous FEN")
        log("8/8 FEN Formatted")
        log(f"FEN: {real_fen}")
        return real_fen

    except Exception as e:
        log(f"{error_messages.get(step, 'An unknown error occurred')} "
            f"Details: {e}")
        return real_fen
