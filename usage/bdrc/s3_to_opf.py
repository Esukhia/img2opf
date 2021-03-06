from bdrc_ocr import (
    BATCH_PREFIX,
    DEBUG,
    IMAGES_BASE_DIR,
    OCR_BASE_DIR,
    OUTPUT,
    SERVICE,
    catalog,
    get_s3_bits,
    get_s3_image_list,
    get_s3_prefix_path,
    get_volume_infos,
    get_work_local_id,
    ocr_output_bucket,
    save_images_for_vol,
)

DEBUG["status"] = True


def save_json_output(bits, fn, output_dir):
    output_dir.mkdir(exist_ok=True, parents=True)
    output_fn = output_dir / fn
    output_fn.write_bytes(bits.getvalue())


def download_ocr_output_for_vol(
    volume_prefix_url, work_local_id, imagegroup, ocr_base_dir
):
    s3prefix = get_s3_prefix_path(
        work_local_id,
        imagegroup,
        service=SERVICE,
        batch_prefix=BATCH_PREFIX,
        data_types=[OUTPUT],
    )

    for imageinfo in get_s3_image_list(volume_prefix_url):
        ocr_output_dir = ocr_base_dir / work_local_id / imagegroup
        ocr_json_fn = f"{imageinfo['filename'].split('.')[0]}.json.gz"
        if (ocr_output_dir / ocr_json_fn).is_file():
            continue
        s3path = s3prefix[OUTPUT] + "/" + ocr_json_fn
        if DEBUG["status"]:
            print(f"\t- downloading {ocr_json_fn}")
        filebits = get_s3_bits(s3path, ocr_output_bucket)
        if filebits:
            save_json_output(filebits, ocr_json_fn, ocr_output_dir)


def process_work(work, vols=None):
    work_local_id, work = get_work_local_id(work)

    is_work_empty = True
    for vol_info in get_volume_infos(work):
        is_work_empty = False
        print(f'[INFO] {vol_info["imagegroup"]} processing ....')

        if vols and vol_info["imagegroup"] not in vols:
            continue

        save_images_for_vol(
            volume_prefix_url=vol_info["volume_prefix_url"],
            work_local_id=work_local_id,
            imagegroup=vol_info["imagegroup"],
            images_base_dir=IMAGES_BASE_DIR,
        )

        download_ocr_output_for_vol(
            volume_prefix_url=vol_info["volume_prefix_url"],
            work_local_id=work_local_id,
            imagegroup=vol_info["imagegroup"],
            ocr_base_dir=OCR_BASE_DIR,
        )

    # if not is_work_empty:
    #    catalog.ocr_to_opf(OCR_BASE_DIR / work_local_id)


if __name__ == "__main__":
    # process_work('W1PD95844')
    process_work("W1PD96682", ["I1PD96857"])
