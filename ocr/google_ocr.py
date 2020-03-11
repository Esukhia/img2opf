import argparse
import base64
import io
import glob
import os

from google.cloud import vision
from google.cloud.vision import types
from google.protobuf.json_format import MessageToJson


vision_client = vision.ImageAnnotatorClient()

def get_text_from_image(image):
    '''
    image: file_path or image bytes
    return: google ocr response in Json
    '''
    if isinstance(image, str):
        with io.open(image, 'rb') as image_file:
            content = base64.b64encode(image_file.read())
    else:
        content = base64.b64encode(image)
    image = types.Image(content=content)

    response = vision_client.document_text_detection(image=image)
    response_json = MessageToJson(response)

    return response_json


if __name__ == "__main__":

    from tqdm import tqdm

    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--input_dir", type=str, help="directory path containing all the images")
    ap.add_argument("--n", type=int, help="start page number", default=1)
    ap.add_argument("--output_dir")

    args = ap.parse_args()

    fns = sorted([o for o in glob.glob(args.input_dir + '/*') if o.endswith('.png')])

    output_dir = os.path.join("output", args.output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    vol_texts = []
    for fn in tqdm(fns[args.n-1:]):
        text = get_text_from_image(fn)
        vol_texts.append(text[0].description)
    
    output_fn = os.path.join(output_dir, 'ocr_output.txt')
    with open(output_fn, 'w') as f:
        f.write('\n\n'.join(vol_texts))