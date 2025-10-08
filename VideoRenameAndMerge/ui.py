from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QFileDialog, QLabel, QLineEdit, QProgressBar
from worker import VideoWorker

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
        base_name_container.addWidget(self.txt_box_1)
        layout_row_1.addLayout(base_name_container)
        # Concatenated Video Name Input
        concatenated_video_name_container = QVBoxLayout()
        self.label_2 = QLabel("Concatenated Video Name:")
        concatenated_video_name_container.addWidget(self.label_2)
        self.txt_box_2 = QLineEdit()
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

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Video Folder")
        if folder:
            self.folder_path = folder
            self.label_3.setText(f"Selected: {folder}")
            self.start_btn.setEnabled(True)

    def start_process(self):
        self.log_output.clear()
        base_name = self.txt_box_1.text()
        concatenated_name = self.txt_box_2.text()
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