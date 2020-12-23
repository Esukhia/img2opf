# Google-OCR

### Setup with pip & virtualenv
Clone this repo and follow the steps below
```
cd img2opf
virtualenv .env
source .env/bin/activate
pip install -r requirements.txt
```
Follow this [Quick Start](https://pypi.org/project/google-cloud-vision/) guide to setup Google Vision API, which is necessary for using Google OCR service. There is also [video tutorial](https://www.youtube.com/watch?v=nMY0qDg16y4)


## Usage
Running OCR on collection of images. Note: Google OCR doesn't support `.tif` images. 
```
usage: img2opf/ocr.py [-h] [--input_dir INPUT_DIR] [--n N]
                     [--output_dir OUTPUT_DIR] [--combine_output]

optional arguments:
  -h, --help            show this help message and exit
  --input_dir INPUT_DIR
                        directory path containing all the images
  --n N                 start page number
  --output_dir OUTPUT_DIR
                        directory to store the ocr output
  --combine_output      Combine the output of all the images in output_dir
```
Output of OCR will be stored in `.txt` file with name of image file int `output_dir` individually by default.
IF you want to output of all images in single `.txt` file when give `--combine` flag.

## example:
For example you have images to be OCRed in `./my_images` like below:
```
./my_images/
    image_01.png
    image_02.jpg
    image_03.jpeg
```

1. To OCR the all images, run following command:
```
python ocr/google_ocr.py --input_dir ./my_images --output_dir output
```

Output:
```
./output/
    image_01.txt
    image_02.txt
    image_03.txt
```

2. To OCR the all images starting from 2nd image, run the following command:
```
python ocr/google_ocr.py --input_dir ./my_images -n 2 --output_dir output`
```

Output:
```
./output/
    image_02.txt
    image_03.txt
```

3. To combine output of all images, run following command:
```
python img2opf/ocr.py --input_dir ./my_images --output_dir output` --combine
```

Output:
```
./output/
    my_images.txt
```

Note: If you have any issue with using the script or any feature that you would like to suggest please feel free to create an [issue](https://github.com/Esukhia/Google-OCR/issues) on that.
