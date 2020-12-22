import argparse
import logging

from bdrc_ocr import (
    BATCH_PREFIX,
    IMAGES,
    IMAGES_BASE_DIR,
    OCR_BASE_DIR,
    OUTPUT,
    SERVICE,
    apply_ocr_on_folder,
    archive_on_s3,
    catalog,
    get_s3_prefix_path,
    get_volume_infos,
    get_work_local_id,
    save_images_for_vol,
)

logging.basicConfig(
    filename=f"{__file__}.log",
    format="%(asctime)s, %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
)


def process(args):
    work_local_id, _ = get_work_local_id(args.work)
    for vol_info in get_volume_infos(work_local_id, imagegroup=args.imagegroup):
        print(f"[INFO] Processing {vol_info['imagegroup']} ....")
        save_images_for_vol(
            imagelist=vol_info["imagelist"],
            work_local_id=work_local_id,
            imagegroup=vol_info["imagegroup"],
            images_base_dir=IMAGES_BASE_DIR,
        )

        apply_ocr_on_folder(
            images_base_dir=IMAGES_BASE_DIR,
            work_local_id=work_local_id,
            imagegroup=vol_info["imagegroup"],
            ocr_base_dir=OCR_BASE_DIR,
        )

        # get s3 paths to save images and ocr output
        s3_ocr_paths = get_s3_prefix_path(
            work_local_id=work_local_id,
            imagegroup=vol_info["imagegroup"],
            service=SERVICE,
            batch_prefix=BATCH_PREFIX,
            data_types=[IMAGES, OUTPUT],
        )

        # save image and ocr output at ocr.bdrc.org bucket
        archive_on_s3(
            images_base_dir=IMAGES_BASE_DIR,
            ocr_base_dir=OCR_BASE_DIR,
            work_local_id=work_local_id,
            imagegroup=vol_info["imagegroup"],
            s3_paths=s3_ocr_paths,
        )

        catalog.ocr_to_opf(OCR_BASE_DIR / work_local_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("work")
    parser.add_argument("--imagegroup", "-img", default=chr(0), help="start imagegroup")
    args = parser.parse_args()

    process(args)
