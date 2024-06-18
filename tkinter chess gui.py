import tkinter as tk
from tkinter import messagebox
import chess
import chess.svg
import time

class ChessGame:
    def __init__(self, time_limit, increment):
        self.window = tk.Tk()
        self.window.title("Chess Game")
        self.window.geometry("800x800")
        self.canvas = tk.Canvas(self.window, width=1500, height=1500)
        self.canvas.pack()
        self.board = chess.Board()
        self.time_limit = time_limit
        self.increment = increment
        self.white_time = time_limit
        self.black_time = time_limit
        self.first_move = True
        self.draw_board()
        self.window.bind("<Button>", self.click)
        self.window.mainloop()

    def draw_board(self):
        self.canvas.delete("all")
        self.canvas.create_text(400, 50, text=self.board.fen(), font=("Arial", 20))
        for i in range(8):
            for j in range(8):
                color = "gray" if (i+j) % 2 == 0 else "white"
                self.canvas.create_rectangle(i*100, j*100, (i+1)*100, (j+1)*100, fill=color)
        pieces = self.board.piece_map()
        for square, piece in pieces.items():
            x = square % 8
            y = 7 - square // 8
            piece_symbol = self.get_piece_symbol(piece)
            self.canvas.create_text(x*100+50, y*100+50, text=piece_symbol, font=("Arial", 50))
        if not self.first_move:
            self.canvas.create_text(200, 50, text="White time: " + str(self.white_time), font=("Arial", 20))
            self.canvas.create_text(600, 750, text="Black time: " + str(self.black_time), font=("Arial", 20))

    def get_piece_symbol(self, piece):
        if piece.piece_type == chess.PAWN:
            return "�" if piece.color == chess.BLACK else "♙"
        elif piece.piece_type == chess.KNIGHT:
            return "♞" if piece.color == chess.BLACK else "♘"
        elif piece.piece_type == chess.BISHOP:
            return "♝" if piece.color == chess.BLACK else "♗"
        elif piece.piece_type == chess.ROOK:
            return "♜" if piece.color == chess.BLACK else "♖"
        elif piece.piece_type == chess.QUEEN:
            return "♛" if piece.color == chess.BLACK else "♕"
        elif piece.piece_type == chess.KING:
            return "♚" if piece.color == chess.BLACK else "♔"

    def click(self, event):
        x = event.x // 100
        y = 7 - event.y // 100
        square = y*8 + x
        if self.board.piece_at(square):
            self.canvas.create_rectangle(x*100, (7-y)*100, (x+1)*100, ((7-y)+1)*100, outline="red")
            self.window.bind("<Button>", lambda event, square=square: self.move(square, event))
        else:
            messagebox.showerror("Invalid move", "No piece to move")

    def move(self, start_square, event):
        x = event.x // 100
        y = 7 - event.y // 100
        end_square = y*8 + x
        try:
            move = self.board.find_move(start_square, end_square)
            self.board.push(move)
            self.draw_board()
            if self.first_move:
                self.first_move = False
                self.window.after(1000, self.update_time)
            if self.board.turn == chess.WHITE:
                self.white_time += self.increment
            else:
                self.black_time += self.increment
        except ValueError:
            messagebox.showerror("Invalid move", "Invalid move")
        self.window.bind("<Button>", self.click)

    def update_time(self):
        if self.board.turn == chess.WHITE:
            self.white_time -= 1
        else:
            self.black_time -= 1
        self.draw_board()
        if self.white_time <= 0:
            messagebox.showinfo("Game over", "Black wins")
            self.window.quit()
        elif self.black_time <= 0:
            messagebox.showinfo("Game over", "White wins")
            self.window.quit()
        self.window.after(1000, self.update_time)

if __name__ == "__main__":
    game = ChessGame(300, 5)  # 5 minutes time limit, 5 seconds increment
