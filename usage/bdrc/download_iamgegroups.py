import argparse
import logging
import sys
from pathlib import Path

from bdrc_ocr import get_volume_infos, get_work_local_id, save_images_for_vol

logging.basicConfig(
    filename=f"{__file__}.log",
    format="%(asctime)s, %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
)

"""
        bucket_name="ocr.bdrc.io",
        type_="output",
        batch_prefix="batch",
        service="vision",
        imagegroup="I1PD96845",
"""


def process(args):
    work_local_id, _ = get_work_local_id(args.work)
    for vol_info in get_volume_infos(work_local_id):
        imagegroup = vol_info["imagegroup"]
        if imagegroup > args.end:
            break
        if imagegroup < args.start:
            continue
        if imagegroup in args.skip:
            continue
        print(f"[INFO] Processing {imagegroup} ....")
        save_images_for_vol(
            imagelist=vol_info["imagelist"],
            work_local_id=work_local_id,
            imagegroup=imagegroup,
            images_base_dir=Path("archive/images/missing-imagegroups"),
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("work")
    parser.add_argument("--start", "-s", default=chr(0), help="start imagegroup")
    parser.add_argument(
        "--end", "-e", default=chr(sys.maxunicode), help="end imagegroup"
    )
    parser.add_argument(
        "--skip", "-sk", default="", help="imagegroups to be skiped (in comma seperated"
    )
    args = parser.parse_args()

    process(args)
