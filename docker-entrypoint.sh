. /venv/bin/activate
cd /narratave

export SECRET_KEY="django-insecure-=%d_9dgzc8nk4=5j$6ra_ry8m*00s0_qr%ws%pe9i7z^n)8uy"
export DB_NAME=zsamiqgk
export DB_USER=zsamiqgk
export DB_PASSWORD=or9pjOpcDYfPHsCE4fhiTC4h28qFPR3e
export DB_HOST=rosie.db.elephantsql.com
export DB_PORT=5432

exec uvicorn Narratave.asgi:application --host 0.0.0.0 --port 8000