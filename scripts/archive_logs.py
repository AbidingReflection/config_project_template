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
    if not files_to_archive:
        print("No logs to archive.")
        return

    # Get the earliest and latest timestamps based on file creation times
    earliest_ts = datetime.fromtimestamp(os.path.getctime(files_to_archive[0])).strftime('%Y%m%d_%H%M%S')
    latest_ts = datetime.fromtimestamp(os.path.getctime(files_to_archive[-1])).strftime('%Y%m%d_%H%M%S')
    
    archive_name = f"logs_{earliest_ts}_to_{latest_ts}.zip"
    archive_path = os.path.join(archive_dir, archive_name)

    with zipfile.ZipFile(archive_path, 'w') as archive_zip:
        for file in files_to_archive:
            archive_zip.write(file, os.path.basename(file))
            os.remove(file)
            print(f"Zipped and removed: {file}")
    print(f"Archive created: {archive_path}")

def archive_old_logs(logs_dir):
    """Archive all but the last 5 .log files."""
    archive_dir = os.path.join(logs_dir, 'archive')
    os.makedirs(archive_dir, exist_ok=True)

    log_files = get_log_files(logs_dir)
    files_to_archive = log_files[:-5]  # Archive all but the last 5 files

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
