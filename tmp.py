
import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QMessageBox
from PyQt5.QtCore import Qt


# Main window class that handles the overall game structure
class GameWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		# Game configuration variables
		self.board_size = 6  # Size of the game board
		self.number_weights = [5, 3, 2]  # Weights for numbers 1, 2, and 3
		self.bomb_weight = 2  # Weight for bombs
		# Game state variables
		self.current_score = 1
		self.revealed_cells = set()
		# UI elements
		self.central_widget = QWidget()
		self.setCentralWidget(self.central_widget)
		self.main_layout = QVBoxLayout(self.central_widget)
		self.score_label = QLabel()
		self.initUI()


	def initUI(self):
		self.setWindowTitle('Number Bomb Game')
		self.showMainMenu()


	def showMainMenu(self):
		# Clear existing layout
		for i in reversed(range(self.main_layout.count())): 
			self.main_layout.itemAt(i).widget().setParent(None)
		
		# Create main menu buttons
		start_button = QPushButton('Start Game')
		start_button.clicked.connect(self.startGame)
		quit_button = QPushButton('Quit')
		quit_button.clicked.connect(self.close)
		
		self.main_layout.addWidget(start_button)
		self.main_layout.addWidget(quit_button)


	def startGame(self):
		# Reset game state
		self.current_score = 1
		self.revealed_cells = set()
		
		# Clear existing layout
		for i in reversed(range(self.main_layout.count())): 
			widget = self.main_layout.itemAt(i).widget()
			if widget is not None:
				widget.deleteLater()
			layout = self.main_layout.itemAt(i).layout()
			if layout is not None:
				while layout.count():
					item = layout.takeAt(0)
					widget = item.widget()
					if widget is not None:
						widget.deleteLater()
				self.main_layout.removeItem(layout)
		
		# Create game board
		self.createBoard()
		
		# Add score label
		self.score_label = QLabel(f'Score: {self.current_score}')
		self.main_layout.addWidget(self.score_label)


	def createBoard(self):
		# Create game grid
		game_layout = QGridLayout()
		
		# Generate board values
		self.board = self.generateBoard()
		
		# Create buttons and add them to grid
		self.buttons = [[QPushButton() for _ in range(self.board_size)] for _ in range(self.board_size)]
		for i in range(self.board_size):
			for j in range(self.board_size):
				button = self.buttons[i][j]
				button.setFixedSize(50, 50)
				# Connect button to click event
				button.clicked.connect(lambda checked, row=i, col=j: self.onCellClick(row, col))
				game_layout.addWidget(button, i, j)

		
		# Add row sums
		for i in range(self.board_size):
			row_sum, row_bombs = self.getRowInfo(i)
			game_layout.addWidget(QLabel(f'{row_sum} ({row_bombs}B)'), i, self.board_size)
		
		# Add column sums
		for j in range(self.board_size):
			col_sum, col_bombs = self.getColumnInfo(j)
			game_layout.addWidget(QLabel(f'{col_sum} ({col_bombs}B)'), self.board_size, j)
		
		self.main_layout.addLayout(game_layout)


	def generateBoard(self):
		# Generate board values based on weights
		possibilities = [1, 2, 3, 'B']
		weights = self.number_weights + [self.bomb_weight]
		return [[random.choices(possibilities, weights=weights)[0] for _ in range(self.board_size)] for _ in range(self.board_size)]


	def getRowInfo(self, row):
		# Calculate sum and bomb count for a row
		row_values = self.board[row]
		return sum(x for x in row_values if isinstance(x, int)), row_values.count('B')


	def getColumnInfo(self, col):
		# Calculate sum and bomb count for a column
		col_values = [self.board[i][col] for i in range(self.board_size)]
		return sum(x for x in col_values if isinstance(x, int)), col_values.count('B')


	def onCellClick(self, row, col):
		# Handle cell click event
		if (row, col) in self.revealed_cells:
		return
		
		self.revealed_cells.add((row, col))
		value = self.board[row][col]
		button = self.buttons[row][col]
		
		if value == 'B':
		button.setText('B')
		self.gameOver(False)
		else:
		button.setText(str(value))
		self.current_score *= value
		self.score_label.setText(f'Score: {self.current_score}')  # Update this line
		
		if len(self.revealed_cells) == self.board_size**2 - sum(row.count('B') for row in self.board):
		    self.gameOver(True)

	def gameOver(self, won):
		# Handle game over state
		# Reveal all cells
		for i in range(self.board_size):
			for j in range(self.board_size):
				if (i, j) not in self.revealed_cells:
					value = self.board[i][j]
					self.buttons[i][j].setText('B' if value == 'B' else str(value))
		
		message = f"You {'won' if won else 'lost'}! Final score: {self.current_score}"
		reply = QMessageBox.question(self, 'Game Over', f"{message}\nPlay again?", 
					QMessageBox.Yes | QMessageBox.No)
		
		if reply == QMessageBox.Yes:
			self.startGame()
		else:
			self.showMainMenu() 


if __name__ == '__main__':
	app = QApplication(sys.argv)
	game = GameWindow()
	game.setMinimumSize(400, 400)
	game.show()
	sys.exit(app.exec_())


