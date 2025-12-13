git clone [REPO_URL] leafcoin-demo
cd leafcoin-demo
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
./demo/run.sh
# In a second terminal:
./demo/test_transfer.sh
