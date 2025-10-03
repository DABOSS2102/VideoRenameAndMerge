from PyQt6.QtCore import QThread, pyqtSignal
import VideoUtils
import os, ffmpeg, time

class VideoWorker(QThread):
    log = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, file_path, base_name):
        super().__init__()
        self.file_path = file_path
        self.base_name = base_name

    def run(self):
        file_path = self.file_path
        base_name = self.base_name

        self.log.emit(f"You entered: {file_path}")

        if os.path.isdir(file_path):
            self.log.emit("Files in the directory:")
            step_start = time.time()
            files = sorted([f for f in os.listdir(file_path) if f.lower().endswith('.mp4')])
            self.log.emit(f"Step 1 (Listing files) took {time.time() - step_start:.2f} seconds.")

            total_files = len(files)
            if total_files == 0:
                self.progress.emit(100)
                self.log.emit("No mp4 files found to process.")
                return

            self.progress.emit(10)

             # Create renamed_videos directory
            renamed_dir = os.path.join(file_path, "renamed_videos")
            os.makedirs(renamed_dir, exist_ok=True)

            step_start = time.time()
            pad_length = len(str(total_files))
            renamed_files = VideoUtils.rename_mp4_files(file_path, files, base_name, pad_length, self.log.emit, output_dir=renamed_dir)
            self.log.emit(f"Step 2 (Renaming files) took {time.time() - step_start:.2f} seconds.")

            self.log.emit("preprocessing videos...")
            step_start = time.time()
            preprocessed_files = []
            for idx, f in enumerate(renamed_files, start=1):
                preprocessed = VideoUtils.preprocess_single_file(f, self.log.emit)
                preprocessed_files.append(preprocessed)
                self.progress.emit(30 + int((idx / total_files) * 40))
            self.log.emit(f"Step 3 (Preprocessing videos) took {time.time() - step_start:.2f} seconds.")

            if preprocessed_files:
                self.progress.emit(70)
                youtube_dir = os.path.join(file_path, "youtube_video")
                os.makedirs(youtube_dir, exist_ok=True)
                output_path, inputs_txt_path = VideoUtils.concatenate_videos(preprocessed_files, youtube_dir, self.log.emit)
                self.progress.emit(85)
                VideoUtils.cleanup_files(preprocessed_files, inputs_txt_path, self.log.emit)
                self.progress.emit(100)
            else:
                self.progress.emit(100)
                self.log.emit("No mp4 files found to concatenate.")

        else:
            self.progress.emit(100)
            self.log.emit("The provided path is not a valid directory.")
