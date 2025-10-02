import os
import ffmpeg
import time

print("Hello world!")

file_path = input("Please enter the file path of videos to be renamed and merged: ")
print(f"You entered: {file_path}")

if os.path.isdir(file_path):
    print("Files in the directory:")
    step_start = time.time()
    files = sorted([f for f in os.listdir(file_path) if f.lower().endswith('.mp4')])
    print(f"Step 1 (Listing files) took {time.time() - step_start:.2f} seconds.")

    step_start = time.time()
    renamed_files = []
    for idx, filename in enumerate(files, start=1):
        old_file = os.path.join(file_path, filename)
        if os.path.isfile(old_file):
            base_name = f"throw{idx}"
            ext = ".mp4"
            new_filename = base_name + ext
            new_file = os.path.join(file_path, new_filename)
            suffix = 1
            new_filename = f"throw{idx}.mp4"
            while os.path.exists(new_file):
                new_filename = f"{base_name}_{suffix}{ext}"
                new_file = os.path.join(file_path, new_filename)
                suffix += 1
            os.rename(old_file, new_file)
            renamed_files.append(new_file)
            print(f"Renamed '{filename}' to '{new_filename}'")
    print(f"Step 2 (Renaming files) took {time.time() - step_start:.2f} seconds.")

    print("preprocessing videos...")
    step_start = time.time()
    preprocessed_files = []
    for f in renamed_files:
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
        preprocessed_files.append(preprocessed)
        preprocess_time = time.time() - preprocess_start
        print(f"Done preprocessing: {os.path.basename(f)} -> {os.path.basename(preprocessed)} (took {preprocess_time:.2f} seconds)")
    print(f"Step 3 (Preprocessing videos) took {time.time() - step_start:.2f} seconds.")

    if preprocessed_files:
        output_path = os.path.join(file_path, "youtubeVideo.mp4")
        print("Concatenating videos using ffmpeg-python...")

        step_start = time.time()
        # Use concat demuxer for best results
        inputs_txt_path = os.path.join(file_path, "inputs.txt")
        with open(inputs_txt_path, "w") as f:
            for file in preprocessed_files:
                f.write(f"file '{file}'\n")

        ffmpeg.input(inputs_txt_path, format='concat', safe=0).output(
            output_path, c='copy', loglevel='error'
        ).overwrite_output().run()
        print(f"Step 4 (Concatenating videos) took {time.time() - step_start:.2f} seconds.")

        print(f"Created concatenated video: {output_path}")

        step_start = time.time()
        # Remove preprocessed files
        for file in preprocessed_files:
            try:
                os.remove(file)
                print(f"Removed preprocessed file: {file}")
            except Exception as e:
                print(f"Could not remove {file}: {e}")

        # Optionally remove the inputs.txt file
        try:
            os.remove(inputs_txt_path)
            print(f"Removed temporary file: {inputs_txt_path}")
        except Exception as e:
            print(f"Could not remove {inputs_txt_path}: {e}")
        print(f"Step 5 (Cleanup) took {time.time() - step_start:.2f} seconds.")

    else:
        print("No mp4 files found to concatenate.")

else:
    print("The provided path is not a valid directory.")