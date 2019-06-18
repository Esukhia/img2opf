import argparse
import io
import glob
import os

from google.cloud import vision
from google.cloud.vision import types


vision_client = vision.ImageAnnotatorClient()

def text_annotations(fn):
    with io.open(fn, 'rb') as image_file:
        content = image_file.read()
        image = types.Image(content=content)

    response = vision_client.document_text_detection(image=image)
    texts = response.text_annotations

    try:
        return texts[0].description
    except:
        return ""


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
        vol_texts.append(text_annotations(fn))
    
    output_fn = os.path.join(output_dir, 'ocr_output.txt')
    with open(output_fn, 'w') as f:
        f.write('\n\n'.join(vol_texts))
