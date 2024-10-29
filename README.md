# match_product_service
MPS is a service that matches offer items with a list of products based on the API id matching criteria.
Products are matched, compared with similarities and differences counts, and returned in a JSON response.

Running with Python 3.12, FastAPI, Uvicorn, Pytest, Requests, Pydantic, and Pipenv.

### External dependencies
1. [x] Running RabbitMQ server on `localhost:5672` for producing messages.
2. [x] Running API server on `localhost:5000` for id product matching.

### Clone project and install dependencies
```bash
git clone https://github.com/VojtaMarek/match_product_service.git
pipenv install
```

### Create your config file
```bash
cp config.example.py config.py
```
Fill in the required fields in the config.py file. Or set the environment variables.

### Run the service
```bash
pipenv run python -m uvicorn api:app --reload
curl 'http://localhost:8000/run-worker'
### wait for the worker to fill your database
curl 'http://localhost:8000/product/name'
```
