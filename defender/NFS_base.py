import sys
import requests
import os
from utils import create_zip


class NFS_base:
    def __init__(self):
        self.threshold = 0.75

    def test_model(self, file_path):
        app_url = 'http://127.0.0.1:8080/test'
        with open(file_path, 'rb') as file:
            file_data = file.read()
        headers = {'Content-Type': 'application/octet-stream'}
        response = requests.post(app_url, data=file_data, headers=headers)
        print(response.json())

    def train_model(self, folder_path):
        print("Training model...")
        url = 'http://127.0.0.1:8080/train'
        if not os.path.exists(folder_path):
            print(f"The folder path '{folder_path}' does not exist.")
            return

        zip_path = create_zip(folder_path)
        if zip_path is None:
            return

        try:
            files = {'file': open(zip_path, 'rb')}
            response = requests.post(url, files=files)
            if response.status_code == 200:
                print('Model trained successfully')
            else:
                print('An error occurred:', response.json()['error'])
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def choose_model(self):
        print("Choosing model...")

    def run(self):
        if len(sys.argv) < 2:
            print("Please provide an argument.")
            return

        argument = sys.argv[1]

        if argument == "test":
            if len(sys.argv) < 3:
                print("Please provide a file path.")
                return
            file_path = sys.argv[2]
            self.test_model(file_path)
        elif argument == "train":
            if len(sys.argv) < 3:
                print("Please provide a folder path.")
                return
            folder_path = sys.argv[2]
            self.train_model(folder_path)
        elif argument == "choose":
            self.choose_model()
        else:
            print("Invalid argument. Please choose 'test', 'train', or 'choose'.")


if __name__ == "__main__":
    nfs = NFS_base()
    nfs.run()
