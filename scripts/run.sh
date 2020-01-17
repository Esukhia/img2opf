# set up the env
sudo apt update
sudo apt install python3-pip
git clone https://github.com/Esukhia/Google-OCR.git
pip3 install -r Google-OCR/requirements.txt
pip3 install -e Google-OCR/

# run OCR
python3 Google-OCR/usage/bdrc/bdrc_ocr.py