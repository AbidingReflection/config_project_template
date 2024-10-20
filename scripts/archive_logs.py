import os
import zipfile
from datetime import datetime

def get_log_files(logs_dir):
    """Return a list of log files in the logs directory, sorted by creation time."""
    log_files = [f for f in os.listdir(logs_dir) if f.endswith('.log')]
    log_files = [os.path.join(logs_dir, f) for f in log_files]
    return sorted(log_files, key=os.path.getctime)

def zip_and_remove_files(files_to_archive, archive_dir):
    """Zip the provided files into the archive directory and remove the originals."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archive_path = os.path.join(archive_dir, f"logs_archive_{timestamp}.zip")

    with zipfile.ZipFile(archive_path, 'w') as archive_zip:
        for file in files_to_archive:
            archive_zip.write(file, os.path.basename(file))
            os.remove(file)
            print(f"Zipped and removed: {file}")

def archive_old_logs(logs_dir):
    """Archive all but the last 5 .log files."""
    archive_dir = os.path.join(logs_dir, 'archive')
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)

    log_files = get_log_files(logs_dir)
    files_to_archive = log_files[:-5]  # All but the last 5 files

    if files_to_archive:
        zip_and_remove_files(files_to_archive, archive_dir)
    else:
        print("No logs to archive.")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(os.path.abspath(os.path.join(current_dir, os.pardir)), 'logs')

    if os.path.exists(logs_dir):
        archive_old_logs(logs_dir)
    else:
        print(f"Logs directory '{logs_dir}' does not exist.")
