import csv
from io import BytesIO
import json
from pathlib import Path
import requests

from ocr.google_ocr import get_text_from_image

def get_image(img_url):
    response = requests.get(img_url)
    img = response.content
    # img = BytesIO(response.content)
    return img


def get_image_url(path):
    with path.open() as tsv_file:
        reader = csv.reader(tsv_file, delimiter='\t')
        for row in reader:
            yield row


if __name__ == "__main__":
    input_path = Path('usage/bdrc/tsv')
    output_path = Path('usage/bdrc/output')
    output_path.mkdir(exist_ok=True)

    for tsv_path in input_path.iterdir():
        # create work directory
        work_dir = output_path/f'{tsv_path.stem}'
        work_dir.mkdir(exist_ok=True)

        # get vol_id, img_seq and img_url
        prev_vol_id = ''
        for vol_id, img_seq, img_url in get_image_url(tsv_path):
            if 'http' not in img_url: continue
            
            # create vol directory
            vol_dir = work_dir/vol_id
            if vol_id != prev_vol_id: 
                vol_dir.mkdir(exist_ok=True)
                prev_vol_id = vol_id

            # get OCR json response
            img = get_image(img_url)
            response_json = get_text_from_image(img)
            response_dict = eval(response_json)
            
            # save response in json and output text
            page_path_json = vol_dir/f'{img_seq}.json'
            page_path_txt = vol_dir/f'{img_seq}.txt'
            json.dump(response_dict, page_path_json.open('w'))
            page_path_txt.write_text(response_dict['textAnnotations'][0]['description'])