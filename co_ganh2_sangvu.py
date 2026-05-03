import random
import time

def init_board():
    return [[+1, +1, +1, +1, +1],
            [+1,  0,  0,  0, +1],
            [+1,  0,  0,  0, -1],
            [-1,  0,  0,  0, -1],
            [-1, -1, -1, -1, -1]]

def copy_board(board):
    return [row[:] for row in board]

def get_valid_moves(board, player):
    moves = []
    for r in range(5):
        for c in range(5):
            if board[r][c] == player:
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue

                        if (r + c) % 2 != 0 and abs(dr) == 1 and abs(dc) == 1:
                            continue

                        nr, nc = r + dr, c + dc
                        if 0 <= nr < 5 and 0 <= nc < 5 and board[nr][nc] == 0:
                            moves.append(((r, c), (nr, nc)))
    return moves


def apply_ganh(board, i, j):
    player = board[i][j]
    if not player:
        return 0

    ganhs = [
        ((-1, 0), (1, 0)),
        ((0, -1), (0, 1)),
        ((-1, -1), (1, 1)),
        ((1, -1), (-1, 1)),
    ]

    score = 0

    for d1, d2 in ganhs:
        l1 = (i + d1[0], j + d1[1])
        l2 = (i + d2[0], j + d2[1])

        if not (0 <= l1[0] < 5 and 0 <= l1[1] < 5 and 0 <= l2[0] < 5 and 0 <= l2[1] < 5):
            continue

        if board[l1[0]][l1[1]] == board[l2[0]][l2[1]] == -player:
            board[l1[0]][l1[1]] = player
            board[l2[0]][l2[1]] = player
            score += 1

    return score


def is_surrounded(board, player, r, c, visited=None):
    if visited is None:
        visited = set()

    if board[r][c] != player:
        return False

    if (r, c) in visited:
        return True

    visited.add((r, c))

    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue

            if (r + c) % 2 != 0 and abs(dr) == 1 and abs(dc) == 1:
                continue

            nr, nc = r + dr, c + dc

            if 0 <= nr < 5 and 0 <= nc < 5:
                if board[nr][nc] == 0:
                    return False
                if board[nr][nc] == player:
                    if not is_surrounded(board, player, nr, nc, visited):
                        return False

    return True


def apply_chet(board, player, r, c):
    score = 0
    for i in range(5):
        for j in range(5):
            if board[i][j] == -player and is_surrounded(board, -player, i, j):
                board[i][j] = player
                score += 1
    return score


def apply_move(board, move, player):
    new_board = copy_board(board)
    start, end = move

    new_board[start[0]][start[1]] = 0
    new_board[end[0]][end[1]] = player

    apply_ganh(new_board, end[0], end[1])
    apply_chet(new_board, player, end[0], end[1])

    return new_board


def get_forced_moves(board, player):
    moves = get_valid_moves(board, player)
    ganh_moves = []

    for move in moves:
        start, end = move

        temp = copy_board(board)
        temp[start[0]][start[1]] = 0
        temp[end[0]][end[1]] = player

        if apply_ganh(temp, end[0], end[1]) > 0:
            ganh_moves.append(move)

    return ganh_moves if ganh_moves else moves


def evaluate_board(board, player):
    w_material = 10
    w_mobility = 3
    w_position = 1

    my = opp = 0
    pos = [(2,2),(1,2),(3,2),(2,1),(2,3)]
    pos_score = 0

    for r in range(5):
        for c in range(5):
            if board[r][c] == player:
                my += 1
                if (r,c) in pos:
                    pos_score += 1
            elif board[r][c] == -player:
                opp += 1
                if (r,c) in pos:
                    pos_score -= 1

    my_moves = len(get_forced_moves(board, player))
    opp_moves = len(get_forced_moves(board, -player))

    return (w_material * (my - opp)) + \
           (w_mobility * (my_moves - opp_moves)) + \
           (w_position * pos_score)


# ================= MINIMAX FIX =================

def minimax(board, depth, alpha, beta, maximizing, player_id, time_mark):

    if time.time() - time_mark > 2.85:
        return evaluate_board(board, player_id)

    if depth == 0:
        return evaluate_board(board, player_id)

    current = player_id if maximizing else -player_id
    moves = get_forced_moves(board, current)

    if not moves:
        return evaluate_board(board, player_id)

    if maximizing:
        best = float('-inf')

        for m in moves:
            nb = apply_move(board, m, current)
            val = minimax(nb, depth-1, alpha, beta, False, player_id, time_mark)

            best = max(best, val)
            alpha = max(alpha, val)

            if beta <= alpha:
                break

        return best

    else:
        best = float('inf')

        for m in moves:
            nb = apply_move(board, m, current)
            val = minimax(nb, depth-1, alpha, beta, True, player_id, time_mark)

            best = min(best, val)
            beta = min(beta, val)

            if beta <= alpha:
                break

        return best


# ================= MOVE FIX =================

def move(board, player, remain_time):
    moves = get_forced_moves(board, player)
    if not moves:
        return None

    best_move = moves[0]
    best_score = float('-inf')

    time_mark = time.time()

    # iterative deepening đúng cách
    for depth in range(1, 6):

        if time.time() - time_mark > 2.7:
            break

        current_best = best_move
        current_score = best_score

        for m in moves:
            nb = apply_move(board, m, player)

            val = minimax(nb, depth-1, float('-inf'), float('inf'), False, player, time_mark)

            if val > current_score:
                current_score = val
                current_best = m

            if time.time() - time_mark > 2.85:
                break

        best_move = current_best
        best_score = current_score

    return best_move


# ================= GIỮ NGUYÊN =================

def greedy_find(board, player, valid_moves):
    best_move = valid_moves[0]
    best_score = evaluate_board(apply_move(board, best_move, player), player)

    for m in valid_moves[1:]:
        score = evaluate_board(apply_move(board, m, player), player)
        if score > best_score:
            best_score = score
            best_move = m

    return best_move, best_score


def random_move(board, player, remain_time):
    moves = get_valid_moves(board, player)
    return random.choice(moves) if moves else None


def print_board(board):
    char = {1:'O', -1:'X', 0:' '}
    for r in board:
        print(" ".join(char[x] for x in r))
    print()


def fight():
    board = init_board()
    print_board(board)

    turn = 1

    for i in range(100):
        best_move = move(board, turn, 100) if turn == 1 else random_move(board, turn, 100)

        if not best_move:
            break

        board = apply_move(board, best_move, turn)

        print(f"TURN {i+1}: {'YOU' if turn==1 else 'ENEMY'}")
        print(best_move)
        print_board(board)

        time.sleep(0.1)
        turn *= -1


fight()