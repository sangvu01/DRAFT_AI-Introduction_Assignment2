import random
import time

def init_board():
    return [[+1, +1, +1, +1, +1],
             [+1,  0,  0,  0, +1],
             [+1,  0,  0,  0, -1],
             [-1,  0,  0,  0, -1],
             [-1, -1, -1, -1, -1]]

def copy_board(board):
    new_board = [row[:] for row in board]
    return new_board

def get_valid_moves(board, player):
    moves = []
    for r in range(5):
        for c in range(5):
            if board[r][c] == player:
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue

                        # Ràng buộc đi chéo theo luật bàn cờ
                        if (r + c) % 2 != 0 and abs(dr) == 1 and abs(dc) == 1:
                            continue

                        nr, nc = r + dr, c + dc
                        if 0 <= nr < 5 and 0 <= nc < 5 and board[nr][nc] == 0:
                            moves.append(((r, c), (nr, nc)))
    return moves

def apply_ganh(board, i, j) -> int:
    player = board[i][j]

    if not player:
        return 0

    ganhs = [
        ((-1 ,0), (1, 0)),
        ((0 , -1), (0, 1)),
        ((-1 , -1), (1, 1)),
        ((1 , -1), (-1, 1)),
    ]

    score = 0

    for d1, d2 in ganhs:
        l1 = (i + d1[0], j + d1[1])
        l2 = (i + d2[0], j + d2[1])

        if l1[0] < 0 or l1[0] >= 5 or l1[1] < 0 or l1[1] >= 5:
            continue

        if l2[0] < 0 or l2[0] >= 5 or l2[1] < 0 or l2[1] >= 5:
            continue

        if board[l1[0]][l1[1]] == board[l2[0]][l2[1]] == -player:
            board[l1[0]][l1[1]] = player
            board[l2[0]][l2[1]] = player
            score += 1

    return score

def is_surrounded(board, player, r, c, visited = None, depth = 0) -> bool:
    if visited is None:
        visited = {}
    if player != board[r][c]:
        raise Exception("Cell has the wrong player")

    if (r, c) in visited:
        return True

    visited[(r, c)] = True

    visit_next = []

    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue

            if (r + c) % 2 != 0 and abs(dr) == 1 and abs(dc) == 1:
                continue

            nr = r + dr
            nc = c + dc

            if 0 <= nr < 5 and 0 <= nc < 5:
                if board[nr][nc] == 0:
                    return False

                if board[nr][nc] == player and (nr, nc) not in visited:
                    visit_next.append((nr, nc))

    for (nr, nc) in visit_next:
        if not is_surrounded(board, player, nr, nc, visited, depth+1):
            return False

    return True

def apply_chet(board, player, r, c) -> int:
    score = 0

    for i in range(5):
        for j in range(5):
            if board[i][j] == -player and is_surrounded(board, -player, i, j, {}, 0):
                board[i][j] = player
                score += 1

    return score

def apply_move(board, move, player):
    new_board = copy_board(board)
    start, end = move

    new_board[start[0]][start[1]] = 0
    new_board[end[0]][end[1]] = player

    score = 0

    score += apply_ganh(new_board, end[0], end[1])
    score += apply_chet(new_board, player, end[0], end[1])

    return new_board, score

def get_forced_moves(board, player):
    moves = get_valid_moves(board, player)
    ganh_moves = []

    for move in moves:
        temp_board = copy_board(board)
        start, end = move

        # thực hiện move nhưng CHƯA apply chẹt
        temp_board[start[0]][start[1]] = 0
        temp_board[end[0]][end[1]] = player

        # check có gánh không
        ganh_score = apply_ganh(temp_board, end[0], end[1])

        if ganh_score > 0:
            ganh_moves.append(move)

    if ganh_moves:
        return ganh_moves

    return moves

def evaluate_board(board, player):
    """
    Heuristic nâng cao:
    - Material (Số lượng quân): Quan trọng nhất.
    - Mobility (Số nước đi hợp lệ): Giúp AI không bị "bí".
    - Control (Kiểm soát tâm): Quân ở giữa có xu hướng linh hoạt hơn.
    """
    # Trọng số
    w_material = 10
    w_mobility = 3
    w_position = 1

    my_pieces = 0
    opp_pieces = 0
    
    # Tính số quân và kiểm soát vị trí
    center_cells = [(2, 2), (1, 2), (3, 2), (2, 1), (2, 3)]
    position_score = 0

    for r in range(5):
        for c in range(5):
            if board[r][c] == player:
                my_pieces += 1
                if (r, c) in center_cells:
                    position_score += 1
            elif board[r][c] == -player:
                opp_pieces += 1
                if (r, c) in center_cells:
                    position_score -= 1

    # Tính Mobility
    my_moves = len(get_forced_moves(board, player))
    opp_moves = len(get_forced_moves(board, -player))

    # Tổng hợp score
    score = (w_material * (my_pieces - opp_pieces)) + \
            (w_mobility * (my_moves - opp_moves)) + \
            (w_position * position_score)
            
    return score

def minimax(board, depth, alpha, beta, maximizing_player, player_id, time_mark):
    if depth == 0:
        return evaluate_board(board, player_id)

    current_player = player_id if maximizing_player else -player_id

    valid_moves = get_forced_moves(board, current_player)
    valid_moves.sort(key=lambda m: apply_move(board, m, current_player)[1], reverse=True)
    if not valid_moves:
        return evaluate_board(board, player_id)

    if maximizing_player:
        max_eval = float('-inf')
        for move in valid_moves:
            if time.time() >= time_mark + 2.9:
                print("deadline reached")
                return evaluate_board(board, player_id)

            new_board, s = apply_move(board, move, current_player)
            eval_score = minimax(new_board, depth - 1, alpha, beta, False, player_id, time_mark)
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in valid_moves:
            if time.time() >= time_mark + 2.9:
                print("deadline reached")
                return evaluate_board(board, player_id)

            new_board, s = apply_move(board, move, current_player)
            eval_score = minimax(new_board, depth - 1, alpha, beta, True, player_id, time_mark) + s*10
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval

def move(board, player, remain_time):
    """
    Hàm tính toán và trả về nước đi tiếp theo.
    - Thời gian tính toán tối đa: 3 giây.
    """
    valid_moves = get_forced_moves(board, player)

    # random.shuffle(valid_moves)

    if not valid_moves:
        return None
    valid_moves.sort(key=lambda m: apply_move(board, m, player)[1], reverse=True)
    if len(valid_moves) == 1:
        return valid_moves[0]

    best_move = valid_moves[0]
    best_score = float('-inf')

    greedy_best_move, greedy_best_score = greedy_find(board, player, valid_moves)
    if greedy_best_score > best_score:
        best_score = greedy_best_score
        best_move = greedy_best_move

    # max_depth = 5

    time_mark = time.time()
    for depth in range(1, 10):
        for move in valid_moves:
            new_board, s = apply_move(board, move, player)
            score = minimax(new_board, depth - 1, float('-inf'), float('inf'), False, player, time_mark)
            
            if score > best_score:
                best_score = score
                best_move = move

            if time.time() >= time_mark + 2.9:
                return best_move
    # for current_move in valid_moves:
    #     new_board, s = apply_move(board, current_move, player)

    #     score = minimax(new_board, max_depth - 1, float('-inf'), float('inf'), False, player, time_mark)

    #     if score > best_score:
    #         best_score = score
    #         best_move = current_move #dd

    #     if time.time() >= time_mark + 2.9:
    #         print("deadline reached")
    #         break

    return best_move

def greedy_find(board, player, valid_moves):
    new_board, best_score = apply_move(board, valid_moves[0], player)
    best_score = evaluate_board(new_board, player)
    best_move = valid_moves[0]

    for m in valid_moves[1:]:
        new_board, _ = apply_move(board, m, player)
        score = evaluate_board(new_board, player)

        if score > best_score:
            best_score = score
            best_move = m

    return best_move, best_score

def random_move(board, player, remain_time):
    valid_moves = get_valid_moves(board, player)

    if not valid_moves:
        return None

    random.shuffle(valid_moves)

    return valid_moves[0]

def print_board(board):
    char = {1: 'O', -1: 'X', 0: ' '}

    for row in board:
        for p in row:
            print(char[p], end=' ')
        print()
    print()

def fight():
    board = init_board()

    print_board(board)
    turn = 1

    for i in range(100):
        best_move = move(board, turn, 100) if turn == 1 else random_move(board, turn, 100)

        if best_move is None:
           break

        board, s = apply_move(board, best_move, turn)

        print(f"TURN {i+1}: {'YOU' if turn == 1 else 'ENEMY'}")
        print(best_move)
        print_board(board)
        # input()
        time.sleep(0.1)

        turn = -turn

fight()
