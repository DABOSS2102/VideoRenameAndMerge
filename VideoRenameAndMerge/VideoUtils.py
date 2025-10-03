import ffmpeg
import time
import os

def rename_single_mp4_file(file_path, filename, new_base_name, idx, pad_length, log_emit):
    old_file = os.path.join(file_path, filename)
    if os.path.isfile(old_file):
        idx_str = str(idx).zfill(pad_length)
        base_name = f"{new_base_name}_{idx_str}"
        ext = ".mp4"
        new_filename = base_name + ext
        new_file = os.path.join(file_path, new_filename)
        suffix = 1
        while os.path.exists(new_file):
            suffix_str = str(suffix).zfill(pad_length)
            new_filename = f"{base_name}_{suffix_str}{ext}"
            new_file = os.path.join(file_path, new_filename)
            suffix += 1
        os.rename(old_file, new_file)
        log_emit(f"Renamed '{filename}' to '{new_filename}'")
        return new_file
    return None

def rename_mp4_files(file_path, files, new_base_name, pad_length, log_emit):
    renamed_files = []
    pad_length = len(str(len(files)))
    for idx, filename in enumerate(files, start=1):
        new_file = rename_single_mp4_file(file_path, filename, new_base_name, idx, pad_length, log_emit)
        if new_file:
            renamed_files.append(new_file)
    return renamed_files

def preprocess_single_file(f, log_callback):
    preprocess_start = time.time()
    preprocessed = f.replace('.mp4', '_preprocessed.mp4')
    (
        ffmpeg
        .input(f)
        .output(
            preprocessed,
            vcodec='h264_nvenc',
            acodec='aac',
            r=60,
            s='1080x1920',
            ar=44100,
            pix_fmt='yuv420p',
            preset='fast',
            movflags='faststart',
            loglevel='error'
        )
        .overwrite_output()
        .run()
    )
    log_callback(
        f"Preprocessed '{os.path.basename(f)}' to '{os.path.basename(preprocessed)}' in {time.time() - preprocess_start:.2f} seconds."
    )
    return preprocessed

def preprocess_file_list(file_list, log_callback):
    log_callback("preprocessing videos...")
    step_start = time.time()
    preprocessed_files = []
    for f in file_list:
        preprocessed = preprocess_single_file(f, log_callback)
        preprocessed_files.append(preprocessed)
    log_callback(f"Step 3 (Preprocessing videos) took {time.time() - step_start:.2f} seconds.")
    return preprocessed_files

def concatenate_videos(preprocessed_files, file_path, log_emit):
    """
    Concatenates preprocessed video files into a single output video.

    Args:
        preprocessed_files (list): List of preprocessed video file paths.
        file_path (str): Directory path where output and temp files are stored.
        log_emit (callable): Function to emit log messages.
    Returns:
        str: Path to the concatenated output video.
        str: Path to the temporary inputs.txt file.
    """
    output_path = os.path.join(file_path, "10022025HammerPractice.mp4")
    log_emit("Concatenating videos using ffmpeg-python...")

    step_start = time.time()
    inputs_txt_path = os.path.join(file_path, "inputs.txt")
    with open(inputs_txt_path, "w") as f:
        for file in preprocessed_files:
            f.write(f"file '{file}'\n")

    ffmpeg.input(inputs_txt_path, format='concat', safe=0).output(
        output_path, c='copy', loglevel='error'
    ).overwrite_output().run()
    log_emit(f"Step 4 (Concatenating videos) took {time.time() - step_start:.2f} seconds.")

    log_emit(f"Created concatenated video: {output_path}")
    return output_path, inputs_txt_path

def cleanup_files(preprocessed_files, inputs_txt_path, log_emit):
    """
    Removes preprocessed video files and the temporary inputs.txt file.

    Args:
        preprocessed_files (list): List of preprocessed video file paths.
        inputs_txt_path (str): Path to the temporary inputs.txt file.
        log_emit (callable): Function to emit log messages.
    """
    step_start = time.time()
    for file in preprocessed_files:
        try:
            os.remove(file)
            log_emit(f"Removed preprocessed file: {file}")
        except Exception as e:
            log_emit(f"Could not remove {file}: {e}")

    try:
        os.remove(inputs_txt_path)
        log_emit(f"Removed temporary file: {inputs_txt_path}")
    except Exception as e:
        log_emit(f"Could not remove {inputs_txt_path}: {e}")
    log_emit(f"Step 5 (Cleanup) took {time.time() - step_start:.2f} seconds.")