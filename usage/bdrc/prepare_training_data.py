import logging
import shutil
from pathlib import Path

from bdrc_ocr import (
    get_s3_bits,
    get_s3_image_list,
    get_s3_prefix_path,
    get_volume_infos,
    get_work_local_id,
    image_exists_locally,
    save_file,
)

logging.basicConfig(
    filename=f"{__file__}.log",
    format="%(asctime)s, %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
)


def save_images_for_vol(
    volume_prefix_url,
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
    s3prefix = get_s3_prefix_path(work_local_id, imagegroup)
    for i, imageinfo in enumerate(get_s3_image_list(volume_prefix_url)):
        if i < start:
            continue
        if i >= start + n_images:
            break
        imagegroup_output_dir = images_base_dir / work_local_id / imagegroup
        if image_exists_locally(imageinfo["filename"], imagegroup_output_dir):
            continue
        s3path = s3prefix + "/" + imageinfo["filename"]
        filebits = get_s3_bits(s3path)
        if filebits:
            save_file(filebits, imageinfo["filename"], imagegroup_output_dir)


def save_images_for_vol_incoming(
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
        if image_exists_locally(image_path.name, imagegroup_output_dir):
            continue
        filebits = get_s3_bits(str(image_path))
        if filebits:
            save_file(filebits, image_path.name, imagegroup_output_dir)


def process_work(work, filters):
    work_local_id, work = get_work_local_id(work)
    if filters["type"] == "incomming":
        work_id = work_local_id
    else:
        work_id = work
    for i, vol_info in enumerate(get_volume_infos(work_id, filters)):
        imagegroup = vol_info["imagegroup"]
        if imagegroup > filters["till"]:
            break
        if imagegroup in filters["skip"]:
            continue
        print(f"[INFO] Processing {imagegroup} ....")
        if filters["type"] == "incomming":
            save_images_for_vol_incoming(
                imagelist=vol_info["imagelist"],
                work_local_id=work_local_id,
                imagegroup=vol_info["imagegroup"],
                images_base_dir=Path("/media/tenzin/Maetok"),
            )
        else:
            save_images_for_vol(
                volume_prefix_url=vol_info["volume_prefix_url"],
                work_local_id=work_local_id,
                imagegroup=imagegroup,
                images_base_dir=Path("./publication"),
                start=11,
                n_images=25,
            )
        if i == 1:
            break


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
    work = "W2KG210295"
    filters = {"type": "incomming", "till": "Z", "skip": []}

    process_work(work, filters)
    # rename()
    # resize('./publication/W1KG13607')
