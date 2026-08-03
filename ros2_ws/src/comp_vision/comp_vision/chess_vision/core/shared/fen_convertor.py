import numpy as np
import cv2

class FENConverter:
    @staticmethod
    def generate_fen(ptsT, ptsL, detections, boxes, warped):
        """
        Генерирует цветовой FEN: белые фигуры -> 'P', чёрные -> 'p'.
        
        Аргументы:
            ptsT, ptsL: координаты сетки (как раньше)
            detections: массив (N,4) xyxy координат боксов
            boxes: объект YOLO boxes (не используется, оставлен для совместимости)
            warped: выпрямленное изображение (numpy array BGR)
        """
        rows = "87654321"
        cols = "abcdefgh"
        
        # Порог яркости: выше этого значения – белая фигура, иначе чёрная
        # При необходимости подберите вручную, например 120
        THRESHOLD = 100
        
        # Создаём пустую доску
        board = [['.' for _ in range(8)] for _ in range(8)]
        
        for box in detections:
            x1, y1, x2, y2 = map(int, box[:4])
            cx = (x1 + x2) / 2.0
            cy = (y1 + y2) / 2.0
            
            # Определяем клетку по центру
            cell = None
            for col_idx, (x_start, x_end) in enumerate(zip(ptsT[:-1], ptsT[1:])):
                if x_start[0] <= cx <= x_end[0]:
                    for row_idx, (y_start, y_end) in enumerate(zip(ptsL[:-1], ptsL[1:])):
                        if y_start[1] <= cy <= y_end[1]:
                            cell = f"{cols[col_idx]}{rows[row_idx]}"
                            break
                    if cell:
                        break
            if cell is None:
                continue
            
            col_letter = cell[0]
            row_digit = cell[1]
            i = rows.index(row_digit)   # строка 0..7 (8-я -> 0)
            j = cols.index(col_letter)   # столбец 0..7 (a -> 0)
            
            # Вырезаем область фигуры и определяем цвет
            roi = warped[y1:y2, x1:x2]
            if roi.size == 0:
                continue
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            mean_val = np.mean(gray)
            piece = 'P' if mean_val > THRESHOLD else 'p'
            board[i][j] = piece
        
        # Преобразуем доску в FEN
        fen_rows = []
        for row in board:
            row_str = ''
            empty = 0
            for cell in row:
                if cell == '.':
                    empty += 1
                else:
                    if empty:
                        row_str += str(empty)
                        empty = 0
                    row_str += cell
            if empty:
                row_str += str(empty)
            fen_rows.append(row_str)
        fen = '/'.join(fen_rows)
        #fen += ' w KQkq - 0 1'
        return fen