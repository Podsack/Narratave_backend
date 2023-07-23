# Narratave
## Get Started
1. Activate pipenv shell (If you do not have poetry then install it with: `pip install poetry`)
 ```
 poetry shell
 ```
 2. Install dependencies
 ```
 poetry install
 ```
 4. Migrate the database
  ```
  python manage.py migrate
  ```
 5. Compile static files
 ```
 python manage.py collectstatic
 ```
 6. Starting the server
 ```
 python manage.py runserver 8000
 ```
