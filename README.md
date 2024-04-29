# backyardbp
A boilerplate application as per our own inhouse features.

## Project Setup (How to run)
- Clone the repo
```
git clone https://github.com/BackyardCS/nca2-backend.git
```

- Create virtual environment using this command
```
python3 -m venv venv
```

- Activate the virtual environment
```
source venv/bin/activate
```
- Run the following command to install dependencies/libraries
```
pip install -r requirements.txt
```
- Run the migrations
```
python manage.py migrate
```
- Run the server using following command
```
python manage.py runserver
```

## To run testcases

- Run tests
```
pytest
pytest -vv -s
```

- Check Coverage
```
pytest --cov
coverage report -m
```