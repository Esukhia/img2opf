# set up the env
sudo apt update
sudo apt install python3-pip
git clone https://github.com/Esukhia/Google-OCR.git
pip3 install -r Google-OCR/requirements.txt
pip3 install -e Google-OCR/

# git setup
pip3 uninstall gitdb2
pip3 install gitdb
git config --global user.email "ten13zin@gmail.com"
git config --global user.name "tenzin"