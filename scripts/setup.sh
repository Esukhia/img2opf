# set up the env
sudo apt update
sudo add-apt-repository ppa:git-core/ppa -y
sudo apt-get install git -y
sudo apt install python3-pip
git clone https://github.com/Esukhia/Google-OCR.git
pip3 install -r Google-OCR/requirements.txt
pip3 install -e Google-OCR/