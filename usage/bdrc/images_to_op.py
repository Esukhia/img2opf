import argparse
import json
from pathlib import Path

from openpecha.catalog import CatalogManager

from bdrc_ocr import gzip_str
from ocr.google_ocr import get_text_from_image

catalog = CatalogManager(formatter_type="ocr")


def apply_ocr_on_folder(images_dir, ocr_base_dir):
    ocr_output_dir = ocr_base_dir / images_dir.name
    ocr_output_dir.mkdir(exist_ok=True, parents=True)
    if not images_dir.is_dir():
        return
    for img_fn in images_dir.iterdir():
        result_fn = ocr_output_dir / f"{img_fn.stem}.json.gz"
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

    return ocr_output_dir


def images2opf(images_path):
    ocr_output_dir = apply_ocr_on_folder(Path(images_path), Path("./archive"))
    catalog.ocr_to_opf(ocr_output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Images to OpenPecha")
    parser.add_argument("--input", "-o", help="path to images")
    args = parser.parse_args()

    images2opf(args.input)
