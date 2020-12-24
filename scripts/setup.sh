# set up the env
sudo apt -y update
sudo apt -y install python3-pip
sudo apt -y install moreutils

# install Google-OCR
if [ -d ~/ocr/img2opf ]; then
  cd ~/ocr/img2opf;
  git pull;
  cd ..;
else
  git clone https://github.com/Esukhia/Google-OCR.git;
fi

pip3 install -r Google-OCR/requirements.txt
pip3 install -e Google-OCR/

# git setup
pip3 uninstall gitdb2
pip3 install gitdb
git config --global user.email "ten13zin@gmail.com"
git config --global user.name "tenzin"
