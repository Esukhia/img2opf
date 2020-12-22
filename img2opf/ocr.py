import io
from pathlib import Path

from google.cloud import vision
from google.cloud.vision import types
from google.protobuf.json_format import MessageToJson

vision_client = vision.ImageAnnotatorClient()


def google_ocr(image):
    """
    image: file_path or image bytes
    return: google ocr response in Json
    """
    if isinstance(image, (str, Path)):
        with io.open(image, "rb") as image_file:
            content = image_file.read()
    else:
        content = image
    ocr_image = types.Image(content=content)

    response = vision_client.document_text_detection(image=ocr_image)
    response_json_str = MessageToJson(response)

    return eval(response_json_str)


if __name__ == "__main__":

    import argparse

    from tqdm import tqdm

    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--input_dir", type=str, help="directory path containing all the images"
    )
    ap.add_argument("--n", type=int, help="start page number", default=1)
    ap.add_argument(
        "--output_dir", default="./output", help="directory to store the ocr output"
    )
    ap.add_argument(
        "--combine",
        action="store_true",
        help="Combine the output of all the images in output_dir",
    )
    args = ap.parse_args()

    print("[INFO] OCR started ....")
    input_path = Path(args.input_dir)
    output_path = Path(args.output_dir)
    output_path.mkdir(exist_ok=True, parents=True)

    fns = [fn for fn in input_path.iterdir() if fn.suffix in [".png", ".jpg", ".jpeg"]]
    if args.combine:
        fns = sorted(fns)

    texts = []
    for fn in tqdm(fns[args.n - 1 :]):
        response = google_ocr(fn)
        if "textAnnotations" not in response:
            continue
        text = response["textAnnotations"][0]["description"]
        if not args.combine:
            output_fn = output_path / f"{fn.stem}.txt"
            output_fn.write_text(text)
        else:
            texts.append(text)

    if args.combine and texts:
        output_fn = output_path / f"{input_path.name}.txt"
        output_fn.write_text("\n\n\n".join(texts))
        print("[INFO] Output is saved at:", str(output_fn))
    else:
        print("INFO]  Output is saved at:", str(output_path))
