import os
import sys
import webbrowser
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QComboBox,
    QFileDialog,
    QMessageBox,
    QLabel,
    QRadioButton,
    QProgressBar,
)
from PyQt6.QtGui import QPixmap, QIcon
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
from PyQt6.QtCore import Qt, QThread, pyqtSignal

class DownloadThread(QThread):
    progress_updated = pyqtSignal(float)
    download_finished = pyqtSignal(str)

    def __init__(self, ydl_opts, url):
        super().__init__()
        self.ydl_opts = ydl_opts
        self.url = url

    def run(self):
        try:
            with YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([self.url])
            self.download_finished.emit("success")
        except DownloadError as e:
            self.download_finished.emit(f"error: {str(e)}")
        except Exception as e:
            self.download_finished.emit(f"error: {str(e)}")

class YoutubeDownloader(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize UI components
        self.init_ui()

        # Set the path to ffmpeg
        self.set_ffmpeg_path()

        # Initialize download thread
        self.download_thread = None

    def set_ffmpeg_path(self):
        ffmpeg_path = 'ffmpeg'
        if sys.platform == "win32":
            ffmpeg_path += ".exe"
        ffmpeg_path = os.path.join(os.path.dirname(__file__), ffmpeg_path)
        os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)

    def init_ui(self):
        self.setWindowTitle("DeepTube :: Unofficial YouTube Downloader")
        self.setGeometry(300, 300, 400, 400)  # Adjusted height

        # Main widget and layout setup
        self.main_widget = QWidget(self)
        self.main_layout = QVBoxLayout(self.main_widget)
        self.setCentralWidget(self.main_widget)

        # Logo image
        self.logo_label = QLabel(self)
        logo_path = self.img_resouce_path("logo.png")
        self.logo_pixmap = QPixmap(logo_path)
        self.logo_label.setPixmap(self.logo_pixmap)
        self.logo_label.setScaledContents(True)
        self.logo_label.setFixedSize(380, 100)  # Adjust size as needed
        self.main_layout.addWidget(self.logo_label)

        # Add a small space after the logo
        self.main_layout.addSpacing(10)

        # YouTube link input field
        url_label = QLabel("YouTube URL:", self)
        self.main_layout.addWidget(url_label)
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Insert the URL of your YouTube video.")
        self.main_layout.addWidget(self.url_input)

        # Video quality selection
        quality_label = QLabel("Video Quality:", self)
        self.main_layout.addWidget(quality_label)
        self.quality_input = QComboBox(self)
        self.quality_input.addItems(
            ["360p", "480p", "720p", "1080p", "1440p", "2160p", "best", "worst"]
        )
        self.main_layout.addWidget(self.quality_input)

        # Audio format selection
        audio_label = QLabel("Audio Format:", self)
        self.main_layout.addWidget(audio_label)
        self.audio_format_input = QComboBox(self)
        self.audio_format_input.addItems(
            ["best", "aac", "flac", "mp3", "m4a", "opus", "vorbis", "wav"]
        )
        self.main_layout.addWidget(self.audio_format_input)

        # Video format selection
        video_format_label = QLabel("Video Format:", self)
        self.main_layout.addWidget(video_format_label)
        self.video_format_input = QComboBox(self)
        self.video_format_input.addItems(["mp4", "mkv", "webm"])
        self.main_layout.addWidget(self.video_format_input)

        # Video download radio button
        self.video_radio = QRadioButton("Video Download", self)
        self.video_radio.setChecked(True)
        self.video_radio.toggled.connect(self.handle_video_radio)
        self.main_layout.addWidget(self.video_radio)

        # Audio download radio button
        self.audio_radio = QRadioButton("Audio only", self)
        self.audio_radio.setChecked(False)
        self.audio_radio.toggled.connect(self.handle_audio_radio)
        self.main_layout.addWidget(self.audio_radio)

        # Progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setVisible(False)
        self.main_layout.addWidget(self.progress_bar)

        # Download button
        self.download_button = QPushButton("Download", self)
        self.download_button.clicked.connect(self.start_download)
        self.main_layout.addWidget(self.download_button)

        # GitHub icon button
        self.icon_button = QPushButton("", self)
        github_icon_path = self.img_resouce_path("github-mark.png")
        self.icon_button.setIcon(QIcon(github_icon_path))  # Replace 'icon.png' with your icon file
        self.icon_button.clicked.connect(self.handle_icon_button)
        self.icon_button.setFixedWidth(30)  # Set a fixed width
        self.icon_button.setStyleSheet(
            "QPushButton {background-color: transparent; border: none;}"
        )
        self.main_layout.addWidget(self.icon_button)

        # Add some spacing between components
        self.main_layout.addSpacing(10)

        self.show()

    def img_resouce_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.dirname(__file__)
        return os.path.join(base_path, relative_path)

    def handle_audio_radio(self, state):
        if state == Qt.CheckState.Checked:
            self.quality_input.setEnabled(False)
            self.video_format_input.setEnabled(False)
        else:
            self.quality_input.setEnabled(True)
            self.video_format_input.setEnabled(True)

    def handle_video_radio(self, state):
        if state == Qt.CheckState.Checked:
            self.quality_input.setEnabled(True)
            self.video_format_input.setEnabled(True)
        else:
            self.quality_input.setEnabled(False)
            self.video_format_input.setEnabled(False)

    def start_download(self):
        video_url = self.url_input.text().strip()
        if not video_url:
            QMessageBox.warning(self, "Warning", "Please enter a YouTube link.")
            return

        video_quality = self.quality_input.currentText()
        audio_format = self.audio_format_input.currentText()

        # Display the file save dialog
        save_file, _ = QFileDialog.getSaveFileName(
            self, "Select Download File", "", "All Files (*)"
        )
        if save_file:
            if self.audio_radio.isChecked():
                self.download_audio(video_url, audio_format, save_file)

            if self.video_radio.isChecked():
                self.download_video(video_url, video_quality, save_file)
        else:
            QMessageBox.warning(
                self, "Warning", "The path to save the file is not specified."
            )

    def download_video(self, video_url, video_quality, save_path):
        quality = (
            f"{video_quality}p"
            if video_quality != "best" and not video_quality.endswith("p")
            else video_quality
        )

        video_format = self.video_format_input.currentText()
        save_path += f".{video_format}"  # Add the extension to the save path

        ydl_opts = {
            "format": f"bestvideo[height<={quality}]+bestaudio/best",
            "outtmpl": save_path,
            "merge_output_format": video_format,
            "progress_hooks": [self.update_progress],
            "ffmpeg_location": 'ffmpeg',
        }

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.download_thread = DownloadThread(ydl_opts, video_url)
        self.download_thread.progress_updated.connect(self.update_progress)
        self.download_thread.download_finished.connect(self.handle_download_finished)
        self.download_thread.start()

    def download_audio(self, video_url, audio_format, save_path):
        save_path += f".{audio_format}"  # Add the extension to the save path

        ydl_opts = {
            "format": f"bestaudio/best[ext={audio_format}]",
            "outtmpl": save_path,
            "progress_hooks": [self.update_progress],
            "ffmpeg_location": 'ffmpeg',
        }

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.download_thread = DownloadThread(ydl_opts, video_url)
        self.download_thread.progress_updated.connect(self.update_progress)
        self.download_thread.download_finished.connect(self.handle_download_finished)
        self.download_thread.start()

    def update_progress(self, d):
        if d['status'] == 'downloading':
            percent = d['_percent_str']
            self.progress_bar.setValue(float(percent.strip('%')))

    def handle_download_finished(self, status):
        self.progress_bar.setVisible(False)
        if status == "success":
            QMessageBox.information(self, "Success", "The download is complete.")
        else:
            QMessageBox.critical(self, "Error", f"An error occurred: {status}")

    def handle_icon_button(self):
        webbrowser.open("https://github.com/59rice/Deeptube")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = YoutubeDownloader()
    sys.exit(app.exec())
