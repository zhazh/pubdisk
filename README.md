# Pubdisk

*Flask app - an share disk on remote server.*

## Installation

Linux.
```
$ git clone https://github.com/zhazh/pubdisk.git
$ cd pubdisk
$ python -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
$ cat 'replace your secret string' > .env
$ flask init
$ flask run # gunicorn --workers=4 --bind=0.0.0.0:5000 wsgi:app
* Running on http://0.0.0.0:5000/
```

Admin account:
* username: `admin`
* password: `admin`

## License

This project is licensed under the MIT License (see the
[LICENSE](LICENSE) file for details).
