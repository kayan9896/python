
import sys
import json
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit

class NFLPlayerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.players = self.load_players()

    def initUI(self):
        self.setWindowTitle('NFL Player Information')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        search_button = QPushButton('Search')
        search_button.clicked.connect(self.search_player)
        search_layout.addWidget(QLabel('Player Name:'))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)

        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)

        layout.addLayout(search_layout)
        layout.addWidget(self.result_display)

        self.setLayout(layout)

    def load_players(self):
        # Load players from file (assuming you've already fetched and saved the data)
        try:
            with open('nfl_players.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Players file not found. Fetching data...")
            return self.fetch_players()

    def fetch_players(self):
        url = "https://tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com/getNFLPlayerList"
        headers = {
            "X-RapidAPI-Host": "tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com",
            "X-RapidAPI-Key": "2e2983aa24mshf223e0da45b080fp15eec8jsnd05e86a3029a"
        }
        response = requests.get(url, headers=headers)
        data = response.json()
        
        # Save the full JSON response to a file
        with open('nfl_players.json', 'w') as f:
            json.dump(data, f)
        
        return data

    def search_player(self):
        name = self.search_input.text().lower()
        for player in self.players['body']:
            if name in player['longName'].lower():
                self.display_player_info(player)
                return
        self.result_display.setText("Player not found.")

    def display_player_info(self, player):
        info = json.dumps(player, indent=2)
        self.result_display.setText(info)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = NFLPlayerApp()
    ex.show()
    sys.exit(app.exec_())

