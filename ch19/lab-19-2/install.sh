# install python3 virtual environment so you don't break your local python environment.
sudo apt install python3-venv

# create a virtual environment for python labs
python3 -m venv lab-19 && source ./lab-19/bin/activate

pip install wheel
pip install shodan

echo "Modify the SHODAN_API_KEY with your key before running scripts"
