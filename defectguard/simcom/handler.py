from defectguard.BaseHandler import BaseHandler
import pickle, json, torch
from defectguard.simcom.model import DeepJITModel
from defectguard.utils.utils import download_folder, SRC_PATH

class SimCom(BaseHandler):
    def __init__(self, version='platform_within', dictionary='platform', device="cpu"):
        self.model_name = 'simcom'
        self.version = version
        self.dictionary = dictionary
        self.initialized = False
        self.com = None
        self.sim = None
        self.device = device
        download_folder(self.model_name, self.version, self.dictionary)
        
    def initialize(self):
        # Create machine learning model
        with open(f"{SRC_PATH}/models/{self.model_name}/sim_{self.version}", "rb") as f:
            self.sim = pickle.load(f)
            
        # Load dictionary
        dictionary = pickle.load(open(f"{SRC_PATH}/models/{self.model_name}/{self.dictionary}_dictionary", 'rb'))
        dict_msg, dict_code = dictionary

        # Load parameters
        with open(f"{SRC_PATH}/models/{self.model_name}/hyperparameters", 'r') as file:
            params = json.load(file)

        # Set up param
        params["filter_sizes"] = [int(k) for k in params["filter_sizes"].split(',')]
        params["vocab_msg"], params["vocab_code"] = len(dict_msg), len(dict_code)
        params["class_num"] = 1

        # Create model and Load pretrain
        self.com = DeepJITModel(params).to(device=self.device)
        self.com.load_state_dict(torch.load(f"{SRC_PATH}/models/{self.model_name}/com_{self.version}", map_location=self.device))

        # Set initialized to True
        self.initialized = True

    def preprocess(self, data):
        if not self.initialized:
            self.initialize()
        print("Preprocessing...")

    def inference(self, model_input):
        if not self.initialized:
            self.initialize()
        print("Inferencing...")

    def postprocess(self, inference_output):
        if not self.initialized:
            self.initialize()
        print("Postprocessing...")

    def handle(self, data):
        if not self.initialized:
            self.initialize()
        print("Handling...")
        preprocessed_data = self.preprocess(data)
        model_output = self.inference(preprocessed_data)
        final_prediction = self.postprocess(model_output)