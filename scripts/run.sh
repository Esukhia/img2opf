# run OCR
rm -rf output/
python3 Google-OCR/usage/bdrc/bdrc_ocr.py

# cmd
# ( nohup sh run.sh 2>&1 | ts '[%Y-%m-%d %H:%M:%S]' ) >> nohup.log &
