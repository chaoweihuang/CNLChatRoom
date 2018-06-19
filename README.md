# Django Chat

This is a simple chat room built using Django Channels.

Setup instructions on Ubuntu 16.04:

Follow this [guide](https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-16-04) for the initial server setup.

Update package index :

```
sudo apt-get update
```

Install dependencies :

```
sudo apt-get install python3-pip python3-dev
```

Setup Django project :

```
git clone https://github.com/whsunset/CNLChatRoom.git

sudo apt install python3-venv

cd CNLChatRoom

mkdir venv

python3 -m venv venv/djangochat

source venv/djangochat/bin/activate

pip install -r requirements.txt

pip install --upgrade pip
```

Source the env variables :

```
deactivate

source venv/djangochat/bin/activate
```

Perform database migration : 

```
python manage.py migrate
```

Install redis by following this [guide](https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-redis-on-ubuntu-16-04).

Create Django superuser :

```
python manage.py createsuperuser
```

Start the development server :

```
python manage.py runserver
```

Start celery :

```
celery -A chatdemo worker -B -l info
```

Visit the local development server at `127.0.0.1:8000` to test the site.
