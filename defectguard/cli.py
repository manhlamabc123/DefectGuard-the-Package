import argparse, json, os, getpass
from urllib.parse import urlparse
from .auto_extract.RepositoryExtractor import RepositoryExtractor
from utils.utils import commit_to_info
from .deepjit.handler import DeepJIT
from .cc2vec.handler import CC2Vec
from .simcom.handler import SimCom
from .lapredict.handler import LAPredict
from .tlel.handler import TLEL
from .jitline.handler import JITLine

__version__ = "0.1.0"

def read_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)

    parser.add_argument('-repo', type=str, default='', help='path to git repo')
    parser.add_argument('-commit_hash', type=str, default='HEAD', help='commit hash')
    available_languages = ["Python", "Java", "C++", "C", "C#", "JavaScript", "TypeScript", "Ruby", "PHP", "Go", "Swift"]
    parser.add_argument('-main_language', type=str, default='', choices=available_languages, help='Main language of repo')
    
    parser.add_argument('-commit', type=str, default='', help='commit link')
    parser.add_argument('-access_token', type=str, default='', help='user access token')
    
    # parser.add_argument('-ensemble', action='store_true', help='enable ensemble')
    available_ensemble = ['average', 'max', 'majority']
    parser.add_argument('-ensemble', nargs='+', type=str, default=[], choices=available_ensemble, help='list of deep learning models')
    parser.add_argument('-threshold', type=int, default=0.5, help='threshold')

    models = ['deepjit', 'cc2vec', 'simcom', 'codebert_cc2vec', 'lapredict', 'earl', 'tlel', 'jitline']
    parser.add_argument('-models', nargs='+', type=str, default=[], choices=models, help='list of deep learning models')
    dataset = ['gerrit', 'go', 'platform', 'jdt', 'qt', 'openstack']
    parser.add_argument('-dataset', type=str, default='openstack', choices=dataset, help='dataset')
    parser.add_argument('-cross', action='store_true', help='cross project')

    parser.add_argument('-device', type=str, default='cpu', help='Ex: cpu, cuda, cuda:1')

    parser.add_argument('-debug', action='store_true', help='allow debug print')

    return parser

def init_model(model_name, dataset, cross, device):
    match model_name:
        case 'deepjit':
            return DeepJIT(
                dataset=dataset,
                project='cross' if cross else 'within',
                device=device
            )
        case 'cc2vec':
            return CC2Vec(
                dataset=dataset,
                project='cross' if cross else 'within',
                device=device
            )
        case 'simcom':
            return SimCom(
                dataset=dataset,
                project='cross' if cross else 'within',
                device=device
            )
        case 'lapredict':
            return LAPredict(
                dataset=dataset,
                project='cross' if cross else 'within',
                device=device
            )
        case 'tlel':
            return TLEL(
                dataset=dataset,
                project='cross' if cross else 'within',
                device=device
            )
        case 'jitline':
            return JITLine(
                dataset=dataset,
                project='cross' if cross else 'within',
                device=device
            )
        case _:
            raise Exception('No such model')


def main():
    params = read_args().parse_args()

    user_input = {
        'ensemble': params.ensemble,
        'threshold': params.threshold,
        "models": params.models,
        'dataset': params.dataset,
        'cross': params.cross,
        "device": params.device
    }
    
    # User's input handling
    if params.commit == '' and params.repo == '':
        raise Exception("-commit, -repo, atleast one of these is required")

    if params.commit != '':
        parsed_url = urlparse(params.commit)
        if parsed_url.hostname == 'github.com' and '/commit/' in parsed_url.path:
            user_input['link_commit'] = params.commit
            if not os.path.exists("github_access_token.txt"):
                password = getpass.getpass("Enter your GitHub access token: ")
                file_name = "github_access_token.txt"
                with open(file_name, "w") as file:
                    file.write(password)
                print(f"GitHub access token has been saved to {file_name}")
            else:
                with open("github_access_token.txt", "r") as f:
                    user_input['access_token'] = f.read().strip()
        else:
            raise Exception(f'{params.commit} not a GitHub commit link')

    if params.repo != '':
        if params.commit_hash == '':
            raise Exception(f'Commit hash is required')
        if params.main_language == '':
            raise Exception(f"Repository's main language is required")
                
    if params.debug:
        dict_without_token = user_input.copy()
        dict_without_token.pop("access_token", None)
        dict_without_token.pop("commit_info", None)
        print("User's input: ", json.dumps(dict_without_token, indent=4))

    # Extract info from user's repo

    #-----THANH-------
    current_dir = os.getcwd()
    extractor = RepositoryExtractor(params.repo, current_dir, params.main_language)
    extractor.get_repo_commits_info(main_language_only=True)
    extractor.extract_repo_k_features()
    user_input["features"] = extractor.features[params.commit_hash]
    commit = extractor.commits[params.commit_hash]
    user_input["commit_info"] = commit_to_info(commit)
    #-----THANH-------
    
    print(json.dumps(user_input, indent=4))

    # Load Model
    model_list = {}
    for model in params.models:
        model_list[model] = init_model(model, params.dataset, params.cross, params.device)

    print(model_list.keys())

    # Inference
    outputs = {}
    for model in model_list.keys():
        outputs[model] = model_list[model].handle(user_input)

    print(json.dumps(outputs, indent=4))