import sys
import warnings
warnings.filterwarnings('ignore')

sys.path.append('./musicnn')
from musicnn.tagger import top_tags


def inference(output_file):
    results = top_tags(output_file, model='MTT_musicnn', topN=10)
    return results