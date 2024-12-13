import random
from enum import Enum

class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium" 
    HARD = "hard"

class TicTacToeEngine:
    def __init__(self, difficulty=Difficulty.MEDIUM):
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.winner = None
        self.game_over = False
        self.difficulty = difficulty
        self.computer = 'O'
        self.human = 'X'

    def make_move(self, row: int, col: int) -> bool:
        """Make a human move followed by computer move"""
        if not self._make_single_move(row, col):
            return False
            
        if not self.game_over:
            self._computer_move()
            
        return True

    def _make_single_move(self, row: int, col: int) -> bool:
        """Make a single move on the board"""
        if self.game_over:
            return False
            
        if 0 <= row < 3 and 0 <= col < 3 and self.board[row][col] == ' ':
            self.board[row][col] = self.current_player
            
            if self._check_winner():
                self.winner = self.current_player
                self.game_over = True
            elif self._is_board_full():
                self.game_over = True
            else:
                self.current_player = 'O' if self.current_player == 'X' else 'X'
            return True
            
        return False

    def _computer_move(self):
        """Make computer move based on difficulty"""
        if self.difficulty == Difficulty.EASY:
            self._make_random_move()
        elif self.difficulty == Difficulty.MEDIUM:
            if random.random() < 0.5:
                self._make_smart_move()
            else:
                self._make_random_move()
        else:  
            self._make_smart_move()

    def _make_random_move(self):
        """Make a random move"""
        empty_cells = [(i, j) for i in range(3) for j in range(3) 
                      if self.board[i][j] == ' ']
        if empty_cells:
            row, col = random.choice(empty_cells)
            self._make_single_move(row, col)

    def _make_smart_move(self):
        """Make the best possible move"""
        best_score = float('-inf')
        best_move = None

        for i in range(3):
            for j in range(3):
                if self.board[i][j] == ' ':
                    self.board[i][j] = self.computer
                    score = self._minimax(0, False)
                    self.board[i][j] = ' '
                    
                    if score > best_score:
                        best_score = score
                        best_move = (i, j)

        if best_move:
            self._make_single_move(best_move[0], best_move[1])

    def _minimax(self, depth: int, is_maximizing: bool) -> int:
        """Minimax algorithm for finding best move"""
        if self._check_winner_for(self.computer):
            return 1
        if self._check_winner_for(self.human):
            return -1
        if self._is_board_full():
            return 0

        if is_maximizing:
            best_score = float('-inf')
            for i in range(3):
                for j in range(3):
                    if self.board[i][j] == ' ':
                        self.board[i][j] = self.computer
                        score = self._minimax(depth + 1, False)
                        self.board[i][j] = ' '
                        best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for i in range(3):
                for j in range(3):
                    if self.board[i][j] == ' ':
                        self.board[i][j] = self.human
                        score = self._minimax(depth + 1, True)
                        self.board[i][j] = ' '
                        best_score = min(score, best_score)
            return best_score

    def _check_winner(self) -> bool:
        """Check if current player has won"""
        return self._check_winner_for(self.current_player)

    def _check_winner_for(self, player: str) -> bool:
        """Check if specified player has won"""
        for row in self.board:
            if row.count(player) == 3:
                return True 
            
        for col in range(3):
            if all(self.board[row][col] == player for row in range(3)):
                return True
            
        if all(self.board[i][i] == player for i in range(3)):
            return True
        if all(self.board[i][2-i] == player for i in range(3)):
            return True

        return False

    def _is_board_full(self) -> bool:
        """Check if the board is full"""
        return all(cell != ' ' for row in self.board for cell in row)

    def get_board_state(self) -> list:
        """Return current board state"""
        return self.board

    def get_current_player(self) -> str:
        """Return current player"""
        return self.current_player

    def get_winner(self) -> str:
        """Return winner if game is over, None otherwise"""
        return self.winner

    def is_game_over(self) -> bool:
        """Return True if game is over"""
        return self.game_over

    def print_board(self):
        """Print current board state"""
        for row in self.board:
            print('|'.join(row))
            print('-' * 5)

    def set_difficulty(self, difficulty: Difficulty):
        """Set game difficulty"""
        self.difficulty = difficulty
