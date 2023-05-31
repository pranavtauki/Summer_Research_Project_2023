import requests
import os
import zipfile
import gzip
import json
import pickle
import numpy as np
import pandas as pd
from train_classifier import JSONAttributeExtractor, NeedForSpeedModel
from sklearn.ensemble import RandomForestClassifier
import _pickle as cPickle
# Set the URL of the Flask app endpoint

THRESHOLD = 0.75
CLF_FILE = "Pranav_Model.pkl"


def save_gzip_pickle(filename, obj):
    fp = gzip.open(filename, 'wb')
    cPickle.dump(obj, fp)
    fp.close()


while True:
    user_input = input(
        "1. Test model\n2. Train Model\n3. Choose Model\n\nEnter your choice: ")

    if user_input == "1":
        app_url = 'http://127.0.0.1:8080/test'
        # Prompt the user to enter the file path
        file_path = input("Enter the file path to the PE file: ")

        # Read the file data
        with open(file_path, 'rb') as file:
            file_data = file.read()

        # Set the headers and content type
        headers = {'Content-Type': 'application/octet-stream'}

        # Send the file data as part of the POST request
        response = requests.post(app_url, data=file_data, headers=headers)

        # Print the response from the Flask app
        print(response.json())
        break

    elif user_input == "2":
        print("Training model...")

        url = 'http://127.0.0.1:8080/train'

        # Path to the zip file containing the training data
        # file_path = r'C:\Users\prana\Documents\Research_Project\Malware_Samples\Malware_Samples.zip'

        folder_path = input("Enter the folder path: ")

        if not os.path.exists(folder_path):
            print(f"The folder path '{folder_path}' does not exist.")
            exit()

        # Get the folder name
        folder_name = os.path.basename(folder_path)

        # Create a zip file name
        zip_filename = folder_name + ".zip"
        zip_path = os.path.join(folder_path, zip_filename)

        # Create a zip file
        try:
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                # Iterate over all files and subdirectories in the folder path
                for root, _, files in os.walk(folder_path):
                    for file in files:
                        # Get the full path of the file
                        file_path = os.path.join(root, file)
                        # Create the path inside the zip by removing the common prefix
                        zip_path_inside = os.path.relpath(
                            file_path, folder_path)
                        # Add the file to the zip with the corresponding path inside the zip
                        zipf.write(file_path, arcname=zip_path_inside)
        except Exception as e:
            print(f"An error occurred while zipping files: {str(e)}")
        else:
            print(
                f"Files zipped successfully. Zip file created at '{zip_path}'.")

        # Create a dictionary to hold the file data
        files = {'file': open(zip_path, 'rb')}

        # Send the POST request
        response = requests.post(url, files=files)

        if response.status_code == 200:
            print('Model trained successfully')
        else:
            print('An error occurred:', response.json()['error'])

        ## working code##
        # folder_path = input("Enter the folder path: ")

        # if not os.path.exists(folder_path):
        #     print(f"The folder path '{folder_path}' does not exist.")
        #     break

        # # Get the folder name
        # folder_name = os.path.basename(folder_path)

        # # Create a zip file name
        # zip_filename = folder_name + ".zip"
        # zip_path = os.path.join(folder_path, zip_filename)
        # extract_path = os.path.join(folder_path, "extracted_files")

        # # Create a zip file
        # try:
        #     with zipfile.ZipFile(zip_path, 'w') as zipf:
        #         # Iterate over all files and subdirectories in the folder path
        #         for root, _, files in os.walk(folder_path):
        #             for file in files:
        #                 # Get the full path of the file
        #                 file_path = os.path.join(root, file)
        #                 # Create the path inside the zip by removing the common prefix
        #                 zip_path_inside = os.path.relpath(
        #                     file_path, folder_path)
        #                 # Add the file to the zip with the corresponding path inside the zip
        #                 zipf.write(file_path, arcname=zip_path_inside)
        #     print(
        #         f"Files zipped successfully. Zip file created at '{zip_path}'.")
        # except Exception as e:
        #     print(f"An error occurred while zipping files: {str(e)}")

        # try:
        #     with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        #         zip_ref.extractall(extract_path)
        #     print(f"Files extracted successfully to '{extract_path}'.")
        # except Exception as e:
        #     print(f"An error occurred while extracting files: {str(e)}")

        ################# lets check this later: ##############################

        # train_attributes = []
        # gw_data = []
        # mw_data = []
        # train_files = os.path.join(extract_path, "benign_files")
        # # walk in train features
        # for root, _, files in os.walk(train_files):
        #     for file in files:
        #         # Get the full path of the file
        #         file_path = os.path.join(root, file)
        #         with open(file_path, 'r', encoding='latin-1') as file_object:
        #             # Read the lines from the file
        #             sws = file_object.readlines()
        #         # walk in each sw
        #         for sw in sws:
        #             # initialize extractor
        #             at_extractor = JSONAttributeExtractor(sw)
        #             # get train_attributes
        #             atts = at_extractor.extract()
        #             # save attribute
        #             train_attributes.append(atts)

        #         # close file
        #         file.close()
        # # transform into pandas dataframe
        # train_data = pd.DataFrame(train_attributes)
        # # create a NFS model
        # clf = NeedForSpeedModel(classifier=RandomForestClassifier(n_jobs=-1))
        # # train it
        # clf.fit(train_data)
        # # save clf
        # print("Saving model...", flush=True)
        # # save it
        # save_gzip_pickle(CLF_FILE, clf)

        break

    elif user_input == "3":
        print("Choosing model...")
        break

    else:
        print("Invalid input. Please enter a valid choice.")
