import argparse
import json
from pathlib import Path

from bdrc_ocr import save_images_for_vol, archive_on_s3, get_volume_infos, gzip_str, get_s3_prefix_path


# s3 bucket directory config
SERVICE = "vision"
BATCH_PREFIX = 'batch'
IMAGES = 'images'
OUTPUT = 'output'

# local directory config
DATA_PATH = Path('./archive')
IMAGES_BASE_DIR = DATA_PATH/IMAGES
OCR_BASE_DIR = DATA_PATH/OUTPUT
CHECK_POINT_FN = DATA_PATH/'last_vol.cp'


def convert_old_result(images_base_dir, work_path, work_local_id, imagegroup, ocr_base_dir):
    images_dir = images_base_dir/work_local_id/imagegroup
    result_dir = work_path/f'V{work_local_id[1:]}_{imagegroup}'/'resources'
    ocr_output_dir = ocr_base_dir/work_local_id/imagegroup
    ocr_output_dir.mkdir(exist_ok=True, parents=True)

    imgs_and_old_results = [sorted(images_dir.iterdir()), sorted(result_dir.iterdir())]
    for img_fn, old_result_fn in zip(*imgs_and_old_results):
        result_fn = ocr_output_dir/f'{img_fn.stem}.json.gz'
        if result_fn.is_file(): continue
        try:
            result = json.dumps(json.load(old_result_fn.open()))
        except:
            continue
        gzip_result = gzip_str(result)
        result_fn.write_bytes(gzip_result)


def process_work(work_path):
    work_local_id = work_path.name
    volume_prefix_url = f'bdr:{work_local_id}'
    if CHECK_POINT_FN.is_file():
        last_vol = CHECK_POINT_FN.read_text().strip()

    for vol_info in get_volume_infos(volume_prefix_url):
        if last_vol:
            if vol_info['imagegroup'] < last_vol: continue

        print(f'\t[INFO] Volume {vol_info["imagegroup"]} processing ....')
        try:
            # save all the images for a given vol
            save_images_for_vol(
                volume_prefix_url=vol_info['volume_prefix_url'],
                work_local_id=work_local_id, 
                imagegroup=vol_info['imagegroup'],
                images_base_dir=IMAGES_BASE_DIR
            )
            print('\t\t- Saved volume images')

            convert_old_result(
                images_base_dir=IMAGES_BASE_DIR,
                work_path=work_path,
                work_local_id=work_local_id,
                imagegroup=vol_info['imagegroup'],
                ocr_base_dir=OCR_BASE_DIR
            )
            print('\t\t- Converted old results')

            # get s3 paths to save images and ocr output
            s3_ocr_paths = get_s3_prefix_path(
                work_local_id=work_local_id,
                imagegroup=vol_info['imagegroup'],
                service=SERVICE,
                batch_prefix=BATCH_PREFIX,
                data_types=[IMAGES, OUTPUT]
            )

            # save image and ocr output at ocr.bdrc.org bucket
            archive_on_s3(
                images_base_dir=IMAGES_BASE_DIR,
                ocr_base_dir=OCR_BASE_DIR,
                work_local_id=work_local_id,
                imagegroup=vol_info['imagegroup'],
                s3_paths=s3_ocr_paths
            )
            print('\t\t- Archived volume images and ocr output')
        except:
            print(f'\t[ERROR] Error occured while processing Volume {vol_info["imagegroup"]}')
            CHECK_POINT_FN.write_text(vol_info['imagegroup'])
            break


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='Process some integers.')
    # parser.add_argument('--output', '-o', help='path to workids file')
    # args = parser.parse_args()
    
    # output_path = Path(args.output)
    output_path = Path('usage/bdrc/output')

    for work_path in output_path.iterdir():
        print(f'[INFO] Work {work_path.name} processing ....')
        process_work(work_path)
        print(f'[INFO] Work {work_path.name} completed.')