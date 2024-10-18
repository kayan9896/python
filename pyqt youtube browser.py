
import sys
import csv
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QMenuBar, QAction, QToolBar, QFileDialog,
                             QListWidget, QSplitter)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QObject, pyqtSlot
from pytube import YouTube

class WebEnginePage(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.channel = QWebChannel()
        self.setPage(QWebEngineView(self).page())
        self.page().setWebChannel(self.channel)

class SimpleBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple YouTube Browser")
        self.setGeometry(100, 100, 1200, 800)

        self.playlist = []
        self.current_video_index = -1

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create menu bar
        self.create_menu()

        # Create address bar
        address_widget = QWidget()
        address_layout = QHBoxLayout(address_widget)
        self.address_bar = QLineEdit()
        go_button = QPushButton("Go")
        go_button.clicked.connect(self.navigate)
        address_layout.addWidget(self.address_bar)
        address_layout.addWidget(go_button)

        # Create splitter for web view and playlist
        splitter = QSplitter(Qt.Horizontal)
        
        # Create web view
        self.web_view = WebEnginePage()

        # Create playlist widget
        self.playlist_widget = QListWidget()
        self.playlist_widget.itemDoubleClicked.connect(self.play_selected_video)

        # Add web view and playlist to splitter
        splitter.addWidget(self.web_view)
        splitter.addWidget(self.playlist_widget)
        splitter.setSizes([800, 400])  # Set initial sizes

        # Create button bar
        button_bar = QToolBar()
        self.back_button = QPushButton("Previous")
        self.back_button.clicked.connect(self.previous_video)
        self.pause_button = QPushButton("Pause/Play")
        self.pause_button.clicked.connect(self.toggle_pause)
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_video)
        button_bar.addWidget(self.back_button)
        button_bar.addWidget(self.pause_button)
        button_bar.addWidget(self.next_button)

        # Add widgets to main layout
        layout.addWidget(address_widget)
        layout.addWidget(splitter)
        layout.addWidget(button_bar)

        # JavaScript handler
        self.js_handler = JavaScriptHandler()
        self.web_view.channel.registerObject("jsHandler", self.js_handler)

    def create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        
        load_playlist_action = QAction("Load Playlist", self)
        load_playlist_action.triggered.connect(self.load_playlist)
        file_menu.addAction(load_playlist_action)

        close_action = QAction("Close", self)
        close_action.triggered.connect(self.close)
        file_menu.addAction(close_action)

    def navigate(self):
        url = self.address_bar.text()
        self.load_video(url)

    def load_video(self, url):
        if "youtube.com/watch" in url:
            self.web_view.setUrl(QUrl(url))
        else:
            self.web_view.setUrl(QUrl(url))

    def toggle_pause(self):
        self.web_view.page().runJavaScript("""
            var video = document.querySelector('video');
            if (video) {
                if (video.paused) {
                    video.play();
                } else {
                    video.pause();
                }
            }
        """)

    def load_playlist(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Playlist", "", "CSV Files (*.csv)")
        if file_name:
            self.playlist = []
            self.playlist_widget.clear()
            with open(file_name, 'r') as csvfile:
                csv_reader = csv.reader(csvfile)
                for row in csv_reader:
                    if len(row) >= 2:
                        self.playlist.append({'name': row[0], 'url': row[1]})
                        self.playlist_widget.addItem(row[0])
            
            if self.playlist:
                self.current_video_index = 0
                self.load_current_video()

    def load_current_video(self):
        if 0 <= self.current_video_index < len(self.playlist):
            video = self.playlist[self.current_video_index]
            self.address_bar.setText(video['url'])
            self.load_video(video['url'])
            self.playlist_widget.setCurrentRow(self.current_video_index)

    def next_video(self):
        if self.playlist and self.current_video_index < len(self.playlist) - 1:
            self.current_video_index += 1
            self.load_current_video()

    def previous_video(self):
        if self.playlist and self.current_video_index > 0:
            self.current_video_index -= 1
            self.load_current_video()

    def play_selected_video(self, item):
        self.current_video_index = self.playlist_widget.row(item)
        self.load_current_video()

class JavaScriptHandler(QObject):
    @pyqtSlot(str)
    def log(self, message):
        print(message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = SimpleBrowser()
    browser.show()
    sys.exit(app.exec_())


'''
bug 1
import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QAction, QMenuBar, QStatusBar)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QObject, pyqtSlot
from pytube import YouTube

class WebEnginePage(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.channel = QWebChannel()
        self.setPage(WebEnginePage(self))
        self.page().setWebChannel(self.channel)

    def createWindow(self, _):
        new_webview = WebEnginePage(self)
        self.window = new_webview
        return new_webview

class JavaScriptHandler(QObject):
    @pyqtSlot()
    def togglePlayPause(self):
        page = self.parent().web_view.page()
        page.runJavaScript("var video = document.querySelector('video'); if(video){video.paused ? video.play() : video.pause();}")

    @pyqtSlot()
    def skipAhead(self):
        page = self.parent().web_view.page()
        page.runJavaScript("var video = document.querySelector('video'); if(video){video.currentTime += 10;}")

class SimpleBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple YouTube Browser")
        self.setGeometry(100, 100, 1024, 768)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create menu bar
        self.create_menu()

        # Create address bar
        address_widget = QWidget()
        address_layout = QHBoxLayout(address_widget)
        self.address_bar = QLineEdit()
        go_button = QPushButton("Go")
        go_button.clicked.connect(self.navigate)
        address_layout.addWidget(self.address_bar)
        address_layout.addWidget(go_button)

        # Create web view
        self.web_view = WebEnginePage()

        # Create button bar
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        back_button = QPushButton("Back")
        pause_button = QPushButton("Pause/Play")
        next_button = QPushButton("Next")
        button_layout.addWidget(back_button)
        button_layout.addWidget(pause_button)
        button_layout.addWidget(next_button)

        # Connect button actions
        back_button.clicked.connect(self.web_view.back)
        pause_button.clicked.connect(self.toggle_play_pause)
        next_button.clicked.connect(self.skip_ahead)

        # Add widgets to main layout
        layout.addWidget(address_widget)
        layout.addWidget(self.web_view)
        layout.addWidget(button_widget)

        # Set up JavaScript handler
        self.js_handler = JavaScriptHandler(self)
        self.web_view.channel.registerObject("handler", self.js_handler)

        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

    def create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        
        close_action = QAction('Close', self)
        close_action.triggered.connect(self.close)
        file_menu.addAction(close_action)

    def navigate(self):
        url = self.address_bar.text()
        if "youtube.com/watch" in url:
            try:
                yt = YouTube(url)
                stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                video_url = stream.url
                self.web_view.setUrl(QUrl(video_url))
            except Exception as e:
                print(f"Error: {e}")
        else:
            self.web_view.setUrl(QUrl(url))

    def toggle_play_pause(self):
        self.js_handler.togglePlayPause()

    def skip_ahead(self):
        self.js_handler.skipAhead()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = SimpleBrowser()
    browser.show()
    sys.exit(app.exec_())


'''
'''
bug 2

import sys
import csv
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QMenuBar, QAction, QToolBar, QFileDialog)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QObject, pyqtSlot
from pytube import YouTube

class WebEnginePage(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.channel = QWebChannel()
        self.setPage(QWebEngineView(self).page())
        self.page().setWebChannel(self.channel)

class SimpleBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple YouTube Browser")
        self.setGeometry(100, 100, 1024, 768)

        self.playlist = []
        self.current_video_index = -1

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create menu bar
        self.create_menu()

        # Create address bar
        address_widget = QWidget()
        address_layout = QHBoxLayout(address_widget)
        self.address_bar = QLineEdit()
        go_button = QPushButton("Go")
        go_button.clicked.connect(self.navigate)
        address_layout.addWidget(self.address_bar)
        address_layout.addWidget(go_button)

        # Create web view
        self.web_view = WebEnginePage()

        # Create button bar
        button_bar = QToolBar()
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.previous_video)
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.toggle_pause)
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_video)
        button_bar.addWidget(self.back_button)
        button_bar.addWidget(self.pause_button)
        button_bar.addWidget(self.next_button)

        # Add widgets to main layout
        layout.addWidget(address_widget)
        layout.addWidget(self.web_view)
        layout.addWidget(button_bar)

        # JavaScript handler
        self.js_handler = JavaScriptHandler()
        self.web_view.channel.registerObject("jsHandler", self.js_handler)

    def create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        
        load_playlist_action = QAction("Load Playlist", self)
        load_playlist_action.triggered.connect(self.load_playlist)
        file_menu.addAction(load_playlist_action)

        close_action = QAction("Close", self)
        close_action.triggered.connect(self.close)
        file_menu.addAction(close_action)

    def navigate(self):
        url = self.address_bar.text()
        self.load_video(url)

    def load_video(self, url):
        if "youtube.com/watch" in url:
            try:
                yt = YouTube(url)
                stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                video_url = stream.url
                self.web_view.setUrl(QUrl(video_url))
            except Exception as e:
                print(f"Error: {e}")
        else:
            self.web_view.setUrl(QUrl(url))

    def toggle_pause(self):
        self.web_view.page().runJavaScript("""
            var video = document.querySelector('video');
            if (video) {
                if (video.paused) {
                    video.play();
                } else {
                    video.pause();
                }
            }
        """)

    def load_playlist(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Playlist", "", "CSV Files (*.csv)")
        if file_name:
            self.playlist = []
            with open(file_name, 'r') as csvfile:
                csv_reader = csv.reader(csvfile)
                for row in csv_reader:
                    if len(row) >= 2:
                        self.playlist.append({'name': row[0], 'url': row[1]})
            
            if self.playlist:
                self.current_video_index = 0
                self.load_current_video()

    def load_current_video(self):
        if 0 <= self.current_video_index < len(self.playlist):
            video = self.playlist[self.current_video_index]
            self.address_bar.setText(video['url'])
            self.load_video(video['url'])

    def next_video(self):
        if self.playlist and self.current_video_index < len(self.playlist) - 1:
            self.current_video_index += 1
            self.load_current_video()

    def previous_video(self):
        if self.playlist and self.current_video_index > 0:
            self.current_video_index -= 1
            self.load_current_video()

class JavaScriptHandler(QObject):
    @pyqtSlot(str)
    def log(self, message):
        print(message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = SimpleBrowser()
    browser.show()
    sys.exit(app.exec_())

'''
