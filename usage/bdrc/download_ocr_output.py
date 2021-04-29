import argparse
import logging
import sys
from pathlib import Path
from typing import Mapping

from bdrc_ocr import (
    BATCH_PREFIX,
    IMAGES,
    OUTPUT,
    SERVICE,
    get_s3_bits,
    get_s3_image_list,
    get_s3_prefix_path,
    get_volume_infos,
    get_work_local_id,
    ocr_output_bucket,
    save_file,
)

logging.basicConfig(
    filename=f"{__file__}.log",
    format="%(asctime)s, %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
)


def get_json_fn(fn):
    return f"{fn.split('.')[0]}.json.gz"


def get_s3_key(s3prefix, fn):
    return s3prefix + "/" + fn


def save_file(bits, fn, imagegroup_output_dir):
    imagegroup_output_dir.mkdir(exist_ok=True, parents=True)
    output_fn = imagegroup_output_dir / fn
    output_fn.write_bytes(bits.getvalue())


def download_ocr_result_for_vol(
    volume_prefix_url, work_local_id, imagegroup, output_base_dir, s3_ocr_paths
):
    imagegroup_s3prefix = s3_ocr_paths[OUTPUT]
    for imageinfo in get_s3_image_list(volume_prefix_url):
        imagegroup_output_dir = output_base_dir / work_local_id / imagegroup
        ocr_result_fn = get_json_fn(imageinfo["filename"])
        if (imagegroup_output_dir / ocr_result_fn).is_file():
            continue
        s3_key = get_s3_key(imagegroup_s3prefix, ocr_result_fn)
        filebits = get_s3_bits(s3_key, ocr_output_bucket)
        if filebits:
            save_file(filebits, ocr_result_fn, imagegroup_output_dir)


def process(args):
    work_local_id, work = get_work_local_id(args.work)
    for vol_info in get_volume_infos(work):
        imagegroup = vol_info["imagegroup"]
        if imagegroup > args.end:
            break
        if imagegroup < args.start:
            continue
        if imagegroup in args.skip:
            continue
        print(f"[INFO] Processing {vol_info['imagegroup']} ....")

        s3_ocr_paths = get_s3_prefix_path(
            work_local_id=work_local_id,
            imagegroup=vol_info["imagegroup"],
            service=SERVICE,
            batch_prefix=BATCH_PREFIX,
            data_types=[IMAGES, OUTPUT],
        )

        download_ocr_result_for_vol(
            volume_prefix_url=vol_info["volume_prefix_url"],
            work_local_id=work_local_id,
            imagegroup=vol_info["imagegroup"],
            output_base_dir=Path(args.output_dir),
            s3_ocr_paths=s3_ocr_paths,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("work")
    parser.add_argument(
        "--output_dir", "-o", default="./archive/output", help="start imagegroup"
    )
    parser.add_argument("--start", "-s", default=chr(0), help="start imagegroup")
    parser.add_argument(
        "--end", "-e", default=chr(sys.maxunicode), help="end imagegroup"
    )
    parser.add_argument(
        "--skip", "-sk", default="", help="imagegroups to be skiped (in comma seperated"
    )
    args = parser.parse_args()
    process(args)
