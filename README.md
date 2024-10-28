# match_product_service
MPS is a service that matches an offer item with a list of products based on the api id matching criteria.
Products are matched and compared with similarities and differences couts and returned in a json response.

Running with Python 3.12, FastAPI, Uvicorn, Pytest, Requests, Pydantic, and Pipenv.

### External dependencies
1. [x] Running RabbitMQ server on `localhost:5672` for producing messages.
2. [x] Running API server on `localhost:5000` for id product matching.

### Clone project and install dependencies
```bash
git clone <repo-url>
pipenv install
```

### create config file
```bash
cp config.example.py config.py
```
Fill in the required fields in the config.py file. Or set the environment variables.

### Run the service
```bash
pipenv run python -m unicorn api:app --reload
curl --request GET 'http://localhost:8000/run-worker'
### wait for the worker to fill your database
curl --request GET 'http://localhost:8000/product/name'
```

### Run the tests
```bash
pipenv run pytest
```
