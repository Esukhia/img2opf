import logging
import shutil
from pathlib import Path

from bdrc_ocr import (get_s3_bits, get_s3_image_list, get_s3_prefix_path,
                      get_volume_infos, get_work_local_id,
                      image_exists_locally, save_file)

logging.basicConfig(
    filename=f"{__file__}.log",
    format="%(asctime)s, %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
)


def save_images_for_vol(
    imagelist,
    work_local_id,
    imagegroup,
    images_base_dir,
    start=0,
    n_images=float("inf"),
):
    """
    this function gets the list of images of a volume and download all the images from s3.
    The output directory is output_base_dir/work_local_id/imagegroup
    """
    for i, image_path in enumerate(imagelist):
        if i < start:
            continue
        if i >= start + n_images:
            break
        imagegroup_output_dir = images_base_dir / work_local_id / imagegroup
        # if image_exists_locally(image_path.name, imagegroup_output_dir):
        #     continue
        filebits = get_s3_bits(image_path.as_posix())
        if filebits:
            save_file(filebits, image_path.name, imagegroup_output_dir)


def process_work(work, filters):
    work_local_id, work = get_work_local_id(work)
    for vol_info in get_volume_infos(work_local_id):
        imagegroup = vol_info["imagegroup"]
        if imagegroup > filters["till"]:
            break
        if imagegroup in filters["skip"]:
            continue
        print(f"[INFO] Processing {imagegroup} ....")
        save_images_for_vol(
            imagelist=vol_info["imagelist"],
            work_local_id=work_local_id,
            imagegroup=imagegroup,
            images_base_dir=Path("./publication"),
        )


def rename():
    for i, vol_path in enumerate(sorted(Path("./publication/W1KG13607").iterdir())):
        dest_path = vol_path.parent / f"v{i+1:03}"
        shutil.move(str(vol_path), str(dest_path))


def resize(path):
    import cv2

    def resize_by_percent(img_fn, out_fn=None, scale_percent=60):
        img = cv2.imread(str(img_fn))
        "Resize the image to given percent `scale_percent` of the image"
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
        if out_fn:
            cv2.imwrite(str(out_fn), resized)
        else:
            return resized

    path = Path(path)
    out_path = path.parent / f"{path.name}-resized"
    for vol_fn in path.iterdir():
        print(f"[INFO] Processing {vol_fn.name} ...")
        vol_out_path = out_path / vol_fn.name
        vol_out_path.mkdir(exist_ok=True, parents=True)
        for img_fn in vol_fn.iterdir():
            img_out_fn = vol_out_path / img_fn.name
            resize_by_percent(img_fn, out_fn=img_out_fn)


if __name__ == "__main__":
    work = "W22083"
    filters = {"type": "", "till": "Z", "skip": []}

    process_work(work, filters)
    # rename()
    # resize('./publication/W1KG13607')
