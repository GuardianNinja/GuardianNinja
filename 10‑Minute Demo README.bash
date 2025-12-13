git clone [REPO_URL] leafcoin-demo
cd leafcoin-demo
docker build -t leafcoin-demo:latest .
docker run --rm -it leafcoin-demo:latest /bin/bash -c "./demo/run.sh"
# In a second terminal inside the container or another shell:
./demo/test_transfer.sh
