import copy

NEIGHBOURHOOD = [[(1, 0), (0, 1)],
 [(1, 1), (0, 0), (0, 2)],
 [(1, 2), (0, 1), (0, 3)],
 [(1, 3), (0, 2), (0, 4)],
 [(1, 4), (0, 3)],
 [(0, 0), (2, 0), (1, 1)],
 [(0, 1), (2, 1), (1, 0), (1, 2)],
 [(0, 2), (2, 2), (1, 1), (1, 3)],
 [(0, 3), (2, 3), (1, 2), (1, 4)],
 [(0, 4), (2, 4), (1, 3)],
 [(1, 0), (3, 0), (2, 1)],
 [(1, 1), (3, 1), (2, 0), (2, 2)],
 [(1, 2), (3, 2), (2, 1), (2, 3)],
 [(1, 3), (3, 3), (2, 2), (2, 4)],
 [(1, 4), (3, 4), (2, 3)],
 [(2, 0), (4, 0), (3, 1)],
 [(2, 1), (4, 1), (3, 0), (3, 2)],
 [(2, 2), (4, 2), (3, 1), (3, 3)],
 [(2, 3), (4, 3), (3, 2), (3, 4)],
 [(2, 4), (4, 4), (3, 3)],
 [(3, 0), (4, 1)],
 [(3, 1), (4, 0), (4, 2)],
 [(3, 2), (4, 1), (4, 3)],
 [(3, 3), (4, 2), (4, 4)],
 [(3, 4), (4, 3)]]


def read_boards(file):
    previous_board = []
    current_board = []
    for _ in range(5):
        row = file.readline()
        previous_board.append([int(row[0]),int(row[1]),int(row[2]),int(row[3]),int(row[4])])
    for _ in range(5):
        row = file.readline()
        current_board.append([int(row[0]),int(row[1]),int(row[2]),int(row[3]),int(row[4])])
    return previous_board, current_board

def read_file_and_create_input(file_name = 'input.txt'):
    with open(file_name) as file:
        piece_type = int(file.readline())
        previous_board, current_board = read_boards(file)
        return previous_board, current_board, piece_type
    
def write_output_file(best_move, file_name = 'output.txt'):
    with open(file_name, 'w') as file:
        if best_move[0] == -1 and best_move[1] == -1:
            file.write("PASS")
        else:
            file.write(f"{best_move[0]},{best_move[1]}")

class Board():
    def __init__(self,board):
        self.board = board
        self.board_size = len(board)
        self.liberty = [[-1 for j in range(self.board_size)] for i in range(self.board_size)]
        self.total_pieces = -1
    
    
    def copy_board(self):
        new_board= [[],[],[],[],[]]
        for i in range(self.board_size):
            for j in range(self.board_size):
                new_board[i].append(self.board[i][j])
        return Board(new_board)

    def get_ally_neighbors_and_vacancy(self, i, j):
        neighbors = NEIGHBOURHOOD[i*5 + j]
        allies = []
        vacancy = []
        ally_piece = self.board[i][j]
        for piece in neighbors:
            current_piece = self.board[piece[0]][piece[1]]
            if  current_piece == ally_piece:
                allies.append(piece)
            elif current_piece == 0 :
                vacancy.append(piece)
        return allies, vacancy
    
    def get_all_allies_and_surrounding_vacancies(self,i, j):
        queue = [(i, j)]
        all_allies = set()
        all_vacancies = set()
        all_allies.add((i, j))
        while  queue:
            i,j = queue.pop(0)
            allies,vacancies = self.get_ally_neighbors_and_vacancy(i,j)
            for ally in allies:
                if ally not in all_allies:
                    queue.append(ally)
                    all_allies.add(ally)
            for vacancy in vacancies:
                all_vacancies.add(vacancy)
        return all_allies, all_vacancies

    def get_liberty(self,i,j):
        if self.liberty[i][j] <0:
            allies, vacancies = self.get_all_allies_and_surrounding_vacancies(i,j)
            liberty = len(vacancies)
            for x,y in allies:
                self.liberty[x][y] = liberty
        return self.liberty[i][j]
    
    def get_dead_pieces(self, piece_type):
        dead_pieces = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i][j] == piece_type and self.get_liberty(i, j)==0:
                    dead_pieces.append((i,j))
        return dead_pieces
    
    def clean_board_pieces(self, piece_type):
        dead_pieces = self.get_dead_pieces(piece_type)
        if not dead_pieces: 
            return self
        else:
            new_board = self.copy_board()
            for i,j in dead_pieces:
                new_board.board[i][j] = 0
            return new_board
    
    def create_new_board_with_move(self,piece_type,i,j):
        new_board = self.copy_board()
        new_board.board[i][j] = piece_type
        return new_board
        
    def get_board_pieces(self):
        if self.total_pieces < 0:
            total_pieces = 0
            for i in range(self.board_size):
                for j in range(self.board_size):
                    if self.board[i][j]>0:
                        total_pieces +=1
            self.total_pieces = total_pieces
        return self.total_pieces
    
    def is_board_full(self):
        return self.get_board_pieces()>=24
    
    
    @staticmethod
    def check_boards(board1, board2):
        for i in range(board1.board_size):
            for j in range(board1.board_size):
                if board1.board[i][j] != board2.board[i][j]:
                    return False
        return True

class BoardStates():
    
    def __init__(self, previous_board, current_board, piece_type):
        self.piece_type = piece_type
        self.opponent_piece_type = 2 if piece_type == 1 else 1
        self.previous_board = previous_board
        self.current_board = current_board
        self.board_size = current_board.board_size
        self.opponent_pass = Board.check_boards(self.previous_board, self.current_board)
        
    def check_game_over(self,board):
        return (self.opponent_pass and Board.check_boards(self.current_board, board)) or (board.is_board_full()) #Scope for improvement double checking
    
    def find_next_valid_moves(self):
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.current_board.board[i][j] == 0:
                    new_board = self.current_board.create_new_board_with_move(self.piece_type, i,j)
                    cleaned_new_board = new_board.clean_board_pieces(self.opponent_piece_type)
                    if cleaned_new_board.get_liberty(i,j)>0 and not Board.check_boards(self.previous_board, cleaned_new_board):
                        yield (i, j), BoardStates(self.current_board, cleaned_new_board, self.opponent_piece_type)
        
        if self.current_board.get_board_pieces()>15:         
            yield (-1, -1), BoardStates(self.current_board,self.current_board, self.opponent_piece_type)


class MiniMax():
    def __init__(self, input_board_state):
        self.input_board_state = input_board_state 
    
    def get_best_move(self, depth):
        
        value = float('inf') if self.input_board_state.piece_type == 1 else -float('inf')
        next_valid_move = False
        beta = float('inf')
        alpha = -beta
        best_move = ()

        for move, new_board_state in self.input_board_state.find_next_valid_moves():
            next_valid_move = True
            
            if self.input_board_state.check_game_over(new_board_state.current_board):
                new_value = self.evaluation(new_board_state)
            else:
                new_value = self.minimax(new_board_state, depth - 1, alpha, beta)
            
            if self.input_board_state.piece_type == 1:
                if new_value < value:
                    value = new_value
                    best_move = move
                    beta = min(beta, new_value)
            else:
                if new_value > value:
                    value = new_value
                    best_move = move
                    alpha = max(alpha, new_value)
            
            if beta<=alpha:
                break
        
        if not next_valid_move:
            return self.evaluation(self.input_board_state)
        
        return best_move,value

    def minimax(self, board_state, depth, alpha, beta):
        
        value = float('inf') if board_state.piece_type == 1 else -float('inf')
        next_valid_move = False
        
        if depth == 0:
            tmp = self.evaluation(board_state)
            return tmp

        for _, new_board_state in board_state.find_next_valid_moves():
                next_valid_move = True
                
                if board_state.check_game_over(new_board_state.current_board):
                    new_value = self.evaluation(new_board_state)
                else:
                    new_value = self.minimax(new_board_state, depth - 1, alpha, beta)
                
                if board_state.piece_type == 1:
                    value = min(new_value,value)
                    beta = min(beta, new_value)
                else:
                    value = max(new_value,value)
                    alpha = max(alpha, new_value)
                    
                if beta<=alpha:
                    break

        if not next_valid_move:
            return self.evaluation(board_state)

        return value
    
    def evaluation(self, board_state):
        result = 0

        capture_reward = 0
        board_pieces = board_state.current_board.get_board_pieces()
        
        liberty_penality = 0
        liberty_difference =  0
        piece_difference = 0
        piece_value_difference = 0
        for i in range(board_state.board_size):
            for j in range(board_state.board_size):
                if board_state.current_board.board[i][j] == 1:
                    value = board_state.current_board.get_liberty(i,j)
                    liberty_difference = liberty_difference - value
                    if value == 1:
                        liberty_penality = liberty_penality + 50
                    if i==0 or j==0 or i==4 or j==4:
                        piece_value_difference = piece_value_difference - 2
                    elif i==2 and j==2:
                        piece_value_difference = piece_value_difference - 8
                    else:
                        piece_value_difference = piece_value_difference - 4
                    piece_difference = piece_difference - 1
                elif board_state.current_board.board[i][j] == 2:
                    value = board_state.current_board.get_liberty(i,j)
                    liberty_difference = liberty_difference + value
                    if value == 1:
                        liberty_penality = liberty_penality - 50
                    if i==0 or j==0 or i==4 or j==4:
                        piece_value_difference = piece_value_difference + 2
                    elif i==2 and j==2:
                        piece_value_difference = piece_value_difference + 8
                    else:
                        piece_value_difference = piece_value_difference + 4
                    piece_difference = piece_difference + 1
        
        piece_difference_result = (piece_difference*10)**3
        piece_value_difference_result = piece_value_difference*(1-board_pieces/25)
        liberty_difference_result = (liberty_difference)*(1-board_pieces/25)**2
        liberty_penality_result  = (liberty_penality)*(1-board_pieces/25)
        result = piece_difference_result + piece_value_difference_result +  liberty_difference_result + liberty_penality_result
        return result


def main():
    depth_chart = []
    for i in range(25):
        if i<15:
            depth_chart.append(4)
        elif i<16:
            depth_chart.append(3)
        else:
            depth_chart.append(2)
    previous_board, current_board, piece_type = read_file_and_create_input()
    board_states = BoardStates(Board(previous_board), Board(current_board), piece_type)
    board_pieces = board_states.current_board.get_board_pieces()
    move, value = MiniMax(board_states).get_best_move(depth=depth_chart[board_pieces])
    write_output_file(move, file_name = 'output.txt')


if __name__ == '__main__':
    main()