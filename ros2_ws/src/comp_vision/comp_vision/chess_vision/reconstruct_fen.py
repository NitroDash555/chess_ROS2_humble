import logging

import chess

class FenReconstructionError(Exception):
    """Базовое исключение для ошибок восстановления FEN."""
    pass

class AmbiguousMoveError(FenReconstructionError):
    """Неоднозначный ход (например, два коня могут пойти на одну клетку)."""
    pass

class NoValidMoveError(FenReconstructionError):
    """Не найдено ни одного легального хода, объясняющего изменения."""
    pass

def reconstruct_fen(prev_fen, color_fen, default_promotion='q', logger=None):
    """
    Восстанавливает реальный FEN на основе предыдущего FEN и цветового FEN.
    Возвращает строку FEN.
    В случае неоднозначности или невозможности восстанавливает предыдущий FEN,
    но генерирует исключение с подробным сообщением.
    """
    board = chess.Board(prev_fen)
    
    # Парсим color_fen
    rows = "87654321"
    cols = "abcdefgh"
    color_board = {}
    fen_rows = color_fen.split('/')[:8]
    for i, row_str in enumerate(fen_rows):
        idx = 0
        for ch in row_str:
            if ch.isdigit():
                idx += int(ch)
            else:
                cell = cols[idx] + rows[i]
                color_board[cell] = 'white' if ch.isupper() else 'black'
                idx += 1

    # Определяем изменения
    removed = []
    added = []
    for sq in chess.SQUARE_NAMES:
        was_occupied = board.piece_at(chess.parse_square(sq)) is not None
        is_occupied = sq in color_board
        if was_occupied and not is_occupied:
            removed.append(sq)
        elif not was_occupied and is_occupied:
            added.append(sq)
    #print(removed, added)
    
    if len(removed) == 0 and len(added) == 0:
        if logger is not None:
            logger.info("Никаких изменений позиции не обнаружено. Возвращаем предыдущий FEN.")
        else:
            logging.getLogger('chess_vision').info(
                "Никаких изменений позиции не обнаружено. Возвращаем предыдущий FEN.")
        return prev_fen


    # --- Функция для поиска всех возможных ходов, объясняющих изменения ---
    possible_moves = []
    
    # 1. Обычный ход (1 removed, 1 added)
    if len(removed) == 1 and len(added) == 1:
        from_sq = chess.parse_square(removed[0])
        to_sq = chess.parse_square(added[0])
        piece = board.piece_at(from_sq)
        if piece and piece.color == board.turn:
            move = chess.Move(from_sq, to_sq)
            if move in board.legal_moves:
                possible_moves.append(move)
    
    # 2. Рокировки
    castle_variants = {
        ('e1','h1','g1','f1'): (chess.E1, chess.H1, chess.G1, chess.F1, chess.WHITE),  # короткая белые
        ('e1','a1','c1','d1'): (chess.E1, chess.A1, chess.C1, chess.D1, chess.WHITE),  # длинная белые
        ('e8','h8','g8','f8'): (chess.E8, chess.H8, chess.G8, chess.F8, chess.BLACK),
        ('e8','a8','c8','d8'): (chess.E8, chess.A8, chess.C8, chess.D8, chess.BLACK),
    }
    for (r0, r1, a0, a1), (king_sq, rook_sq, to_king, to_rook, color) in castle_variants.items():
        if sorted(removed) == sorted([r0, r1]) and sorted(added) == sorted([a0, a1]):
            # Проверяем, что король и ладья на месте
            king_ok = board.piece_at(king_sq) and board.piece_at(king_sq).piece_type == chess.KING and board.piece_at(king_sq).color == color
            rook_ok = board.piece_at(rook_sq) and board.piece_at(rook_sq).piece_type == chess.ROOK and board.piece_at(rook_sq).color == color
            if king_ok and rook_ok:
                move = chess.Move(king_sq, to_king)
                if move in board.legal_moves:
                    possible_moves.append(move)
    
    # 3. Взятие на проходе (2 removed, 1 added)
    if len(removed) == 2 and len(added) == 1:
        moving_color = board.turn
        from_sq = None
        captured_sq = None
        for sq in removed:
            piece = board.piece_at(chess.parse_square(sq))
            if piece and piece.color == moving_color and piece.piece_type == chess.PAWN:
                from_sq = chess.parse_square(sq)
            else:
                captured_sq = chess.parse_square(sq)
        to_sq = chess.parse_square(added[0])
        if from_sq and captured_sq:
            move = chess.Move(from_sq, to_sq)
            if move in board.legal_moves and board.is_en_passant(move):
                possible_moves.append(move)
    
    # 4. Превращение пешки (1 removed, 1 added, пешка достигает последней горизонтали)
    if len(removed) == 1 and len(added) == 1:
        from_sq = chess.parse_square(removed[0])
        to_sq = chess.parse_square(added[0])
        piece = board.piece_at(from_sq)
        if piece and piece.piece_type == chess.PAWN:
            if (piece.color == chess.WHITE and chess.square_rank(to_sq) == 7) or \
               (piece.color == chess.BLACK and chess.square_rank(to_sq) == 0):
                # Перебираем возможные фигуры превращения (ферзь, ладья, слон, конь)
                promotion_pieces = ['q', 'r', 'b', 'n']  # по умолчанию ферзь, но можно все
                for promo in promotion_pieces:
                    move = chess.Move(from_sq, to_sq, promotion=chess.Piece.from_symbol(promo.upper() if piece.color == chess.WHITE else promo.lower()).piece_type)
                    if move in board.legal_moves:
                        possible_moves.append(move)
                # Если есть хотя бы один, мы не различаем, какой именно – пользователь должен указать.
                # Если больше одного, это неоднозначность (хотя обычно в такой позиции только одно превращение возможно)
    
    # --- Анализ найденных возможных ходов ---
    
    elif len(possible_moves) == 0:
        raise NoValidMoveError("Не найдено ни одного легального хода, объясняющего изменения позиции.")
    elif len(possible_moves) > 1:
        # Формируем сообщение о неоднозначности
        moves_uci = [m.uci() for m in possible_moves]
        raise AmbiguousMoveError(f"Обнаружено несколько возможных ходов: {moves_uci}. Невозможно однозначно восстановить FEN.")
    else:
        # Ровно один возможный ход
        board.push(possible_moves[0])
        return board.fen()