echo "BUILD started...."

pipenv install --system --deploy
pipenv shell
python manage.py collectstatic