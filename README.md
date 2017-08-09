# bl-status-api - EMS Box Loading System - REST API
The purpose of this repository is the manage the code and documentation for the **RESTful API** component of the Box Loading Status (bl-status) System

## Overview
The Box Loading Status system **API** provides an interface for external apps to submit CRUD requests against the system's underlying Database (MongoDB). In addition, the API implements any applicable centralized/common business rules.  The RESTful API uses HTTP protocol to communicate with external apps.  The **C**reate, **R**ead, **U**pdate, and **Delete** opertaions (CRUD) are mapped to the corresponding http verbs (POST, GET, PUT, DELETE), respectively.  Django and the Django REST API Framework (Python based) is used to build out the API.

## Server Deployment (uWSGI, NGINX on Ubuntu Linux 16.04 LTS)

### Github source code repository clone:
```
$ git clone https://github.com/edbrad/bl-status-api.git
```
### Reference links:

https://luxagraf.net/src/how-set-django-uwsgi-systemd-debian-8

https://gist.github.com/evildmp/3094281

http://daeyunshin.com/2013/01/06/nginx-uwsgi-django-flask-deployment.html

### uWSGI configuation file: bl_status_api.ini:
```
[uwsgi]
master = true
socket = :8080
emperor = /etc/uwsgi
emperor-on-demand-directory = /etc/uwsgi
chdir = /home/netadmin/bl-status-api/bl_status_api/
wsgi-file = bl_status_api/wsgi.py
home = /home/netadmin/Env/bl-status-api/
vacuum = true

```

### Fixing uWSGI "No internal Routing Support..." error
```
$ pip uninstall uwsgi
$ sudo apt-get install libpcre3 libpcre3-dev
$ pip install uwsgi -I --no-cache-dir
```

### Global nginx configuration /etc/nginx/nginx.conf:
```
user www-data;
#user root;
worker_processes auto;
pid /run/nginx.pid;

events {
    worker_connections 768;
    # multi_accept on;
}

http {

    ##
    # Basic Settings
    ##

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    # server_tokens off;

    # server_names_hash_bucket_size 64;
    # server_name_in_redirect off;

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    ##
    # SSL Settings
    ##

    ssl_protocols TLSv1 TLSv1.1 TLSv1.2; # Dropping SSLv3, ref: POODLE
    ssl_prefer_server_ciphers on;

    ##
    # Logging Settings
    ##

    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    ##
    # Gzip Settings
    ##

    gzip on;
    gzip_disable "msie6";

    # gzip_vary on;
    # gzip_proxied any;
    # gzip_comp_level 6;
    # gzip_buffers 16 8k;
    # gzip_http_version 1.1;
    # gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    ##
    # Virtual Host Configs
    ##

    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}


#mail {
#    # See sample authentication script at:
#    # http://wiki.nginx.org/ImapAuthenticateWithApachePhpScript
# 
#    # auth_http localhost/auth.php;
#    # pop3_capabilities "TOP" "USER";
#    # imap_capabilities "IMAP4rev1" "UIDPLUS";
# 
#    server {
#        listen     localhost:110;
#        protocol   pop3;
#        proxy      on;
#    }
# 
#    server {
#        listen     localhost:143;
#        protocol   imap;
#        proxy      on;
#    }
#}

```

### project nginx config:
```
# nginx.conf
upstream django {
    # connect to this socket
    #server unix:/tmp/uwsgi.sock;    # for a file socket
    server 127.0.0.1:8080;      # for a web port socket
    }

server {
    # the port your site will be served on
    listen      80;
    # the domain name it will serve for
    server_name bl-status-api.emsmail.com;   # substitute your machine's IP address or FQDN
    #server_name 172.16.168.110;   # substitute your machine's IP address or FQDN    
    charset     utf-8;

    #Max upload size
    client_max_body_size 75M;   # adjust to taste

    # Django media
    location /media  {
                alias /home/netadmin/bl-status-api/bl_status_api/static/;  # your Django project's media files
    }

    location /static {
                alias /home/netadmin/bl-status-api/bl_status_api/static/;  # your Django project's static files
    }

    # Finally, send all non-media requests to the Django server.
    location / {
        uwsgi_pass  django;
        include     /etc/nginx/uwsgi_params; # or the uwsgi_params you installed manually
        }
    }
```

### Link project nginx config to nginx-enabled sites:
```
sudo ln nginx.conf /etc/nginx/sites-enabled/
```

### Project folder permission (works but ???):
```
sudo chmod -R 777 /home/netadmin/bl-status-api
```
