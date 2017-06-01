import keras
import h5py
import numpy as np

class NNListener:
    def cognition_completed(self, results):
        pass


class NNLoader:

    def __init__(self):
        pass

    def load_and_run(self, arch: str, weights: str, data: str, listener: NNListener):
        print('Loading kernel architecture...')
        with open(arch, "r") as json_file:
            json_model = json_file.read()
        model = keras.models.model_from_json(json_model)

        print('Loading kernel weights...')
        model.load_weights(weights)
        h5f = h5py.File(data, 'r')
        # FIX: Magic number for dataset name inside HDF5 file!
        h5ds = h5f['dataset']
        dataset = np.ndarray(shape=h5ds.shape)
        h5ds.read_direct(dest=dataset)

        print('Cogniting...')
        out = model.predict(dataset)
        print('Cognition completed successfully:')
        print(out)
        listener.cognition_completed(out)
