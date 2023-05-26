import lief
import pandas as pd
from flask import Flask, jsonify, request
from defender.models.attribute_extractor import PEAttributeExtractor
import zipfile
import os
from defender.train_classifier import JSONAttributeExtractor, NeedForSpeedModel
from sklearn.ensemble import RandomForestClassifier
import _pickle as cPickle
import gzip
import tempfile


def create_app(model, threshold):
    app = Flask(__name__)
    app.config['model'] = model

    # analyse a sample
    @app.route('/test', methods=['POST'])
    def post():
        # curl -XPOST --data-binary @somePEfile http://127.0.0.1:8080/ -H "Content-Type: application/octet-stream"
        if request.headers['Content-Type'] != 'application/octet-stream':
            resp = jsonify({'error': 'expecting application/octet-stream'})
            resp.status_code = 400  # Bad Request
            return resp

        bytez = request.data

        try:
            # initialize feature extractor with bytez
            pe_att_ext = PEAttributeExtractor(bytez)
            # extract PE attributes
            atts = pe_att_ext.extract()
            # transform into a dataframe
            atts = pd.DataFrame([atts])
            model = app.config['model']

            # query the model
            result = model.predict_threshold(atts, threshold)[0]
            print('LABEL = ', result)
        except (lief.bad_format, lief.read_out_of_bound) as e:
            print("Error:", e)
            result = 1

        if not isinstance(result, int) or result not in {0, 1}:
            resp = jsonify({'error': 'unexpected model result (not in [0,1])'})
            resp.status_code = 500  # Internal Server Error
            return resp

        resp = jsonify({'result': result})
        resp.status_code = 200
        return resp

    @app.route('/train', methods=['POST'])
    def train_model():
        if 'file' not in request.files:
            resp = jsonify({'error': 'No file attached'})
            resp.status_code = 400  # Bad Request
            return resp

        file = request.files['file']

        # Check if the file is a zip file
        if not file.filename.endswith('.zip'):
            resp = jsonify({'error': 'Expecting a zip file'})
            resp.status_code = 400  # Bad Request
            return resp

        # Extract the zip file to a temporary folder
        with zipfile.ZipFile(file, 'r') as zip_ref:
            temp_folder = 'temp'
            zip_ref.extractall(temp_folder)

        training_folder = os.path.join(temp_folder, 'train_files')

        try:
            # Iterate over the extracted PE files and extract features
            train_data = []
            for root, _, files in os.walk(training_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'rb') as f:
                            bytez = f.read()
                        pe_att_ext = PEAttributeExtractor(bytez)
                        print(file_path)
                        atts = pe_att_ext.extract()
                        atts['label'] = 0
                        train_data.append(atts)
                    except (lief.bad_format, lief.read_out_of_bound) as e:
                        print(f"Error processing {file_path}: {e}")

            # Train the model using the extracted PE features
            # create a NFS model
            training_data = pd.DataFrame(train_data)
            print(training_data)
            clf = NeedForSpeedModel(
                classifier=RandomForestClassifier(n_jobs=-1))
            # train it
            clf.fit(training_data)
            # save clf
            print("Saving model...", flush=True)
            # save it

            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_filename = temp_file.name
                with gzip.open(temp_filename, 'wb') as fp:
                    cPickle.dump(clf, fp)

            # save_gzip_pickle(CLF_FILE, clf)
            model_path = 'defender/models/pat.pkl'
            os.rename(temp_file.name, model_path)

            resp = jsonify({'message': 'Model trained successfully'})
            resp.status_code = 200
            return resp

        finally:
            print("Remove the temporary folder")
            # if os.path.exists(temp_folder):
            #     os.remove(temp_folder)

    # get the model info

    @app.route('/model', methods=['GET'])
    def get_model():
        # curl -XGET http://127.0.0.1:8080/model
        resp = jsonify(app.config['model'].model_info())
        resp.status_code = 200
        return resp

    return app
