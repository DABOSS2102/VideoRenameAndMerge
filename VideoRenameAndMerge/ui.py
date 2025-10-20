from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QFileDialog, QLabel, QLineEdit, QProgressBar
from worker import VideoWorker
from UserPreferences import UserPreferences
import os

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Rename and Merge")
        self.resize(600, 400)
        layout = QVBoxLayout()

        layout_row_1 = QHBoxLayout()
        # Base Name Input
        base_name_container = QVBoxLayout()
        self.label_1 = QLabel("Base Name:")
        base_name_container.addWidget(self.label_1)
        self.txt_box_1 = QLineEdit()
        self.txt_box_1.setText(UserPreferences.load_last_base_name() or "video")
        base_name_container.addWidget(self.txt_box_1)
        layout_row_1.addLayout(base_name_container)
        # Concatenated Video Name Input
        concatenated_video_name_container = QVBoxLayout()
        self.label_2 = QLabel("Concatenated Video Name:")
        concatenated_video_name_container.addWidget(self.label_2)
        self.txt_box_2 = QLineEdit()
        self.txt_box_2.setText(UserPreferences.load_last_concatenated_name() or "merged_video")
        concatenated_video_name_container.addWidget(self.txt_box_2)
        layout_row_1.addLayout(concatenated_video_name_container)
        # Add Base Name Input and Concatenated Video Name Input to Main Layout
        layout.addLayout(layout_row_1)
        # Folder Selection Input
        select_folder_container = QVBoxLayout()
        self.label_3 = QLabel("Select the folder containing videos:")
        select_folder_container.addWidget(self.label_3)
        self.select_btn = QPushButton("Select Folder")
        self.select_btn.clicked.connect(self.select_folder)
        select_folder_container.addWidget(self.select_btn)
        # Add Folder Selection Input to Main Layout
        layout.addLayout(select_folder_container)

        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.start_process)
        self.start_btn.setEnabled(False)
        layout.addWidget(self.start_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.setLayout(layout)
        self.folder_path = ""

        self.last_folder = UserPreferences.load_last_folder() or ""

    def _find_existing_parent(self, path: str) -> str:
        """
        Walk up the path until an existing directory is found.
        Returns empty string if none found.
        """
        if not path:
            return ""
        p = os.path.abspath(path)
        while p and not os.path.isdir(p):
            parent = os.path.dirname(p)
            if parent == p:
                # reached filesystem root
                return ""
            p = parent
        return p if os.path.isdir(p) else ""

    def select_folder(self):
        start_dir = self._find_existing_parent(self.last_folder) or self.last_folder
        dialog = QFileDialog(self, "Select Video Folder", start_dir)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, False)
        dialog.setNameFilter("Video Files (*.mp4 *.mov *.mkv *.avi *.wmv *.flv);;All Files (*)")
        
        if dialog.exec():
            selected = dialog.selectedFiles()
            if selected:
                folder = selected[0]
                self.folder_path = folder
                self.label_3.setText(f"Selected: {folder}")
                self.start_btn.setEnabled(True)
                UserPreferences.save_last_folder(folder)
                self.last_folder = folder

    def start_process(self):
        self.log_output.clear()
        base_name = self.txt_box_1.text()
        concatenated_name = self.txt_box_2.text()
        UserPreferences.save_last_base_name(base_name)
        UserPreferences.save_last_concatenated_name(concatenated_name)
        UserPreferences.save_last_folder(self.folder_path)
        self.worker = VideoWorker(self.folder_path, base_name, concatenated_name)
        self.worker.log.connect(self.append_log)
        self.worker.progress.connect(self.update_progress)
        self.worker.start()
        self.start_btn.setEnabled(False)
        self.worker.finished.connect(lambda: self.start_btn.setEnabled(True))
    
    def append_log(self, text):
        self.log_output.append(text)

    def update_progress(self, value):
        self.progress_bar.setValue(value)