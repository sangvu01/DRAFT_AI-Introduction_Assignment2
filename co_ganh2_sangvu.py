import time
import random

# =========================
# BOARD
# =========================

def init_board():
    return [[+1, +1, +1, +1, +1],
            [+1,  0,  0,  0, +1],
            [+1,  0,  0,  0, -1],
            [-1,  0,  0,  0, -1],
            [-1, -1, -1, -1, -1]]

def copy_board(b):
    return [row[:] for row in b]

# =========================
# MOVE GENERATION
# =========================

def get_valid_moves(board, player):
    moves = []
    for r in range(5):
        for c in range(5):
            if board[r][c] != player:
                continue

            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue

                    # cấm chéo ở ô lẻ
                    if (r + c) % 2 != 0 and abs(dr) == 1 and abs(dc) == 1:
                        continue

                    nr, nc = r + dr, c + dc
                    if 0 <= nr < 5 and 0 <= nc < 5 and board[nr][nc] == 0:
                        moves.append(((r, c), (nr, nc)))
    return moves

# =========================
# GANH (FAST ONLY)
# =========================

def apply_ganh(board, r, c):
    p = board[r][c]
    if p == 0:
        return 0

    patterns = [
        ((-1,0),(1,0)),
        ((0,-1),(0,1)),
        ((-1,-1),(1,1)),
        ((1,-1),(-1,1))
    ]

    score = 0

    for d1, d2 in patterns:
        r1, c1 = r + d1[0], c + d1[1]
        r2, c2 = r + d2[0], c + d2[1]

        if not (0 <= r1 < 5 and 0 <= c1 < 5):
            continue
        if not (0 <= r2 < 5 and 0 <= c2 < 5):
            continue

        if board[r1][c1] == board[r2][c2] == -p:
            board[r1][c1] = p
            board[r2][c2] = p
            score += 1

    return score

# =========================
# APPLY MOVE
# =========================

def apply_move(board, move, player):
    b = copy_board(board)
    (r1, c1), (r2, c2) = move

    b[r1][c1] = 0
    b[r2][c2] = player

    gain = apply_ganh(b, r2, c2)

    return b, gain

# =========================
# QUICK HEURISTIC FOR SORTING
# =========================

def quick_score(board, move, player):
    _, gain = apply_move(board, move, player)
    return gain

# =========================
# EVALUATION
# =========================

def evaluate(board, player):
    my = opp = 0
    center = {(2,2),(1,2),(3,2),(2,1),(2,3)}
    pos = 0

    for r in range(5):
        for c in range(5):
            if board[r][c] == player:
                my += 1
                if (r,c) in center:
                    pos += 1
            elif board[r][c] == -player:
                opp += 1
                if (r,c) in center:
                    pos -= 1

    return 10*(my-opp) + pos

# =========================
# ALPHA BETA
# =========================

def alphabeta(board, depth, alpha, beta, player, max_player, time_limit):
    if time.time() > time_limit or depth == 0:
        return evaluate(board, max_player)

    moves = get_valid_moves(board, player)
    if not moves:
        return evaluate(board, max_player)

    # move ordering nhẹ
    moves.sort(key=lambda m: quick_score(board, m, player), reverse=True)

    if player == max_player:
        value = float('-inf')

        for m in moves:
            nb, _ = apply_move(board, m, player)
            value = max(value, alphabeta(nb, depth-1, alpha, beta, -player, max_player, time_limit))
            alpha = max(alpha, value)
            if alpha >= beta:
                break

        return value

    else:
        value = float('inf')

        for m in moves:
            nb, _ = apply_move(board, m, player)
            value = min(value, alphabeta(nb, depth-1, alpha, beta, -player, max_player, time_limit))
            beta = min(beta, value)
            if alpha >= beta:
                break

        return value

# =========================
# ITERATIVE DEEPENING MOVE
# =========================

def move(board, player, remain_time):
    moves = get_valid_moves(board, player)
    if not moves:
        return None

    best_move = moves[0]

    start = time.time()
    time_limit = start + 2.8

    for depth in range(1, 6):  # đủ cho 3s
        if time.time() > time_limit:
            break

        best_score = float('-inf')
        current_best = best_move

        for m in moves:
            nb, _ = apply_move(board, m, player)

            score = alphabeta(nb, depth-1, float('-inf'), float('inf'),
                              -player, player, time_limit)

            if score > best_score:
                best_score = score
                current_best = m

            if time.time() > time_limit:
                break

        best_move = current_best

    return best_move

# =========================
# TEST LOOP
# =========================

def print_board(b):
    m = {1:'O', -1:'X', 0:' '}
    for r in b:
        print(' '.join(m[x] for x in r))
    print()

def fight():
    b = init_board()
    turn = 1

    print_board(b)

    for _ in range(100):
        m = move(b, turn, 100)

        if not m:
            break

        b, _ = apply_move(b, m, turn)

        print(turn, m)
        print_board(b)

        turn = -turn
        time.sleep(0.05)

fight()