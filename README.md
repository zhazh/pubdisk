# Pubdisk

*An share disk on remote server.*

## Installation

clone:
```
$ git clone https://github.com/zhazh/pubdisk.git
$ cd pubdisk
```
create & activate virtual env then install dependency:

with venv/virtualenv + pip:
```
$ python -m venv env  # use `virtualenv env` for Python2, use `python3 ...` for Python3 on Linux & macOS
$ source env/bin/activate  # use `env\Scripts\activate` on Windows
$ pip install -r requirements.txt
```
generate administrator account then run on development environment:
```
$ flask init
$ flask run
* Running on http://0.0.0.0:5000/
```
generate administrator account then run on production environment:
```
$ vi .flaskenv  # set FLASK_ENV=production
$ flask init
$ gunicorn --workers=4 --bind=0.0.0.0:5000 wsgi:app
* Running on http://0.0.0.0:5000/
```
Admin account:

* username: `admin`
* password: `admin`

## License

This project is licensed under the MIT License (see the
[LICENSE](LICENSE) file for details).
