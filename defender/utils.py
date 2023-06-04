import os
import zipfile


def create_zip(folder_path):
    folder_name = os.path.basename(folder_path)
    zip_filename = folder_name + ".zip"
    zip_path = os.path.join(folder_path, zip_filename)
    try:
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zip_path_inside = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname=zip_path_inside)
    except Exception as e:
        print(f"An error occurred while zipping files: {str(e)}")
        return None
    return zip_path
