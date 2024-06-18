import random
import tkinter as tk

word_list_file = "C:/Users/Jack/Desktop/DATest/Wordle/Wordlist2.txt"

with open(word_list_file, "r") as file:
    word_list = file.read().splitlines()

class WordGuessGame:
    def __init__(self):
        self.word_to_guess = random.choice(word_list)
        self.game_mode = None
        self.guessed_letters = [["_"] * len(self.word_to_guess) for _ in range(5)]
        self.current_guess = 0
        self.required_chars = set()
        self.required_positions = {}
        self.keyboard_colors = {}

        self.root = tk.Tk()
        self.root.title("Word Guessing Game")
        self.root.geometry("800x800")
        self.root.configure(bg="#333")

        self.mode_label = tk.Label(self.root, text="Select a game mode:", font=("Arial", 24), bg="#333", fg="#fff")
        self.mode_label.pack(pady=20)

        self.easy_button = tk.Button(self.root, text="Easy", command=lambda: self.start_game("easy"), font=("Arial", 24), bg="#444", fg="#fff")
        self.hard_button = tk.Button(self.root, text="Hard", command=lambda: self.start_game("hard"), font=("Arial", 24), bg="#444", fg="#fff")
        self.easy_button.pack()
        self.hard_button.pack()

        self.guess_frame = tk.Frame(self.root, bg="#333")
        self.guess_labels = []
        for i in range(5):
            row = []
            for j in range(5):
                label = tk.Label(self.guess_frame, text="", font=("Arial", 36), width=2, borderwidth=1, relief="solid", bg="#333", fg="#fff")
                label.grid(row=i, column=j)
                row.append(label)
            self.guess_labels.append(row)

        self.error_label = tk.Label(self.root, text="", font=("Arial", 24), bg="#333", fg="#f00")
        self.guess_entry = tk.Entry(self.root, font=("Arial", 24), bg="#444", fg="#fff")
        self.guess_button = tk.Button(self.root, text="Guess", command=self.make_guess, font=("Arial", 24), bg="#444", fg="#fff")

        self.keyboard_frame = tk.Frame(self.root, bg="#333")
        self.keyboard_labels = {}
        row1 = ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"]
        row2 = ["A", "S", "D", "F", "G", "H", "J", "K", "L"]
        row3 = ["Z", "X", "C", "V", "B", "N", "M"]
        for i, row in enumerate([row1, row2, row3]):
            for j, letter in enumerate(row):
                label = tk.Label(self.keyboard_frame, text=letter, font=("Arial", 24), width=2, bg="#333", fg="#fff")
                label.grid(row=i, column=j)
                self.keyboard_labels[letter] = label

    def start_game(self, game_mode):
        self.game_mode = game_mode
        self.mode_label.pack_forget()
        self.easy_button.pack_forget()
        self.hard_button.pack_forget()
        self.guess_frame.pack(pady=50)
        self.error_label.pack()
        self.guess_entry.pack()
        self.guess_button.pack()
        self.keyboard_frame.pack(pady=20)

    def make_guess(self):
        guess = self.guess_entry.get()
        self.guess_entry.delete(0, tk.END)

        if self.game_mode == "easy" and (not guess.isalpha() or len(guess) != 5):
            self.error_label.config(text="Invalid input! Please enter a 5-letter word.")
            return
        elif self.game_mode == "hard":
            if len(guess) > 5:
                self.error_label.config(text="Invalid input! Please enter a word with 5 characters or less.")
                return
            valid_guess = True
            for pos, char in self.required_positions.items():
                if guess[pos] != char:
                    valid_guess = False
                    break
            for char in self.required_chars:
                if char not in guess:
                    valid_guess = False
                    break
            if not valid_guess:
                self.error_label.config(text="Try again! You have to use the highlighted letters.")
                return

        remaining_word = list(self.word_to_guess.lower())

        for j in range(len(self.word_to_guess)):
            if j < len(guess) and guess[j].lower() == self.word_to_guess[j].lower():
                self.guessed_letters[self.current_guess][j] = guess[j]
                remaining_word[j] = "_"  # mark as used
                if self.game_mode == "hard":
                    self.required_positions[j] = guess[j].lower()
            elif j < len(guess) and guess[j].lower() in remaining_word:
                index = remaining_word.index(guess[j].lower())
                remaining_word[index] = "_"  # mark as used
                self.guessed_letters[self.current_guess][j] = guess[j]
                if self.game_mode == "hard":
                    self.required_chars.add(guess[j].lower())
            elif j < len(guess):
                self.guessed_letters[self.current_guess][j] = guess[j]

        for i in range(5):
            for j in range(5):
                if self.guessed_letters[i][j].lower() == self.word_to_guess[j].lower():
                    self.guess_labels[i][j].config(text=self.guessed_letters[i][j], bg="#0f0")  # bright green
                elif self.guessed_letters[i][j].lower() in self.word_to_guess.lower():
                    self.guess_labels[i][j].config(text=self.guessed_letters[i][j], bg="#ff0")  # warm yellow
                else:
                    self.guess_labels[i][j].config(text=self.guessed_letters[i][j])

        for letter in self.keyboard_labels:
            if letter.lower() in [char.lower() for char in self.guessed_letters[self.current_guess]]:
                if letter.lower() in self.word_to_guess.lower():
                    self.keyboard_colors[letter] = "#0f0"  # bright green
                else:
                    self.keyboard_colors[letter] = "#f00"  # red

        for letter, color in self.keyboard_colors.items():
            self.keyboard_labels[letter].config(bg=color)

        if self.word_to_guess.lower() == "".join(guess).lower():
            self.error_label.config(text="Congratulations, you won!", fg="#0f0")
            self.guess_button.pack_forget()
            self.restart_button = tk.Button(self.root, text="Restart", command=self.restart, font=("Arial", 24), bg="#444", fg="#fff")
            self.quit_button = tk.Button(self.root, text="Quit", command=self.root.destroy, font=("Arial", 24), bg="#444", fg="#fff")
            self.restart_button.pack()
            self.quit_button.pack()
        else:
            self.current_guess += 1
            if self.current_guess >= 5:
                self.error_label.config(text="Sorry, you lost! The word was " + self.word_to_guess, fg="#f00")
                self.guess_button.pack_forget()
                self.restart_button = tk.Button(self.root, text="Restart", command=self.restart, font=("Arial", 24), bg="#444", fg="#fff")
                self.quit_button = tk.Button(self.root, text="Quit", command=self.root.destroy, font=("Arial", 24), bg="#444", fg="#fff")
                self.restart_button.pack()
                self.quit_button.pack()

    def restart(self):
        self.root.destroy()
        game = WordGuessGame()
        game.run()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = WordGuessGame()
    game.run()
