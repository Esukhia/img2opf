import argparse
import json
import logging
from pathlib import Path

from ocr.google_ocr import get_text_from_image
from openpecha.catalog import CatalogManager

from bdrc_ocr import gzip_str

catalog = CatalogManager(formatter_type="ocr")

logging.basicConfig(
    filename=f"{__file__}.log",
    format="%(asctime)s, %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
)


def apply_ocr_on_vol(vol_dir, out_dir):
    out_vol_dir = out_dir / vol_dir.name
    out_vol_dir.mkdir(exist_ok=True, parents=True)
    if not vol_dir.is_dir():
        return
    for img_fn in vol_dir.iterdir():
        result_fn = out_vol_dir / f"{img_fn.stem}.json.gz"
        if result_fn.is_file():
            continue
        try:
            result = get_text_from_image(str(img_fn))
        except:
            logging.error(f"Google OCR issue: {result_fn}")
            continue
        result = json.dumps(result)
        gzip_result = gzip_str(result)
        result_fn.write_bytes(gzip_result)


def apply_ocr_on_work(path):
    path = Path(path)
    out_dir = Path("./archive") / path.name
    for vol_path in path.iterdir():
        apply_ocr_on_vol(vol_path, out_dir)
    return out_dir


def images2opf(work_path):
    ocr_output_dir = apply_ocr_on_work(work_path)
    catalog.ocr_to_opf(ocr_output_dir)
    catalog.update_catalog()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Images to OpenPecha")
    parser.add_argument("--input", "-i", help="path to images"),
    args = parser.parse_args()

    images2opf(args.input)
