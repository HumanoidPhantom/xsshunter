#!/usr/bin/env python
import binascii
import os
from ConfigParser import SafeConfigParser

nginx_template = """
server {
    # Redirect HTTP to www
    listen 80;
    server_name fakedomain.com;
    location / {
        rewrite ^/(.*)$ https://www.fakedomain.com/$1 permanent;
    }
}

server {
    # Redirect payloads to HTTPS
    listen 80;
    server_name *.fakedomain.com;
    proxy_set_header X-Forwarded-For $remote_addr;

    return 307 https://$host$request_uri;
    client_max_body_size 500M; # In case we have an extra large payload capture 
}

server {
    # Redirect HTTPS to www
    listen 443;
    ssl on;
    ssl_certificate /etc/nginx/ssl/cert.pem; # Wildcard SSL certificate
    ssl_certificate_key /etc/nginx/ssl/privkey.pem; # Wildcard SSL certificate key

    server_name fakedomain.com;
    location / {
        rewrite ^/(.*)$ https://www.fakedomain.com/$1 permanent;
    }
}

server {
    # API proxy
    listen 443;
    ssl on;
    ssl_certificate /etc/nginx/ssl/cert.pem; # Wildcard SSL certificate
    ssl_certificate_key /etc/nginx/ssl/privkey.pem; # Wildcard SSL certificate key

    server_name *.fakedomain.com;
    access_log /var/log/nginx/fakedomain.com.vhost.access.log;
    error_log /var/log/nginx/fakedomain.com.vhost.error.log;

    client_max_body_size 500M;

    location / {
        proxy_pass  http://localhost:8888;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $remote_addr;
    }
}

server {
    # Redirect api to HTTPS
    listen 80;
    server_name api.fakedomain.com; # Subdomain for API server
    proxy_set_header X-Forwarded-For $remote_addr;

    return 307 https://api.fakedomain.com$request_uri;
    client_max_body_size 500M; # In case we have an extra large payload capture 
}

server {
   # Redirect www to HTTPS
   listen 80;
   server_name www.fakedomain.com;
   location / {
       rewrite ^/(.*)$ https://www.fakedomain.com/$1 permanent;
   }
}

server {
   # GUI proxy
   listen 443;
   server_name www.fakedomain.com;
   client_max_body_size 500M;
   ssl on;
   ssl_certificate /etc/nginx/ssl/cert.pem; # Wildcard SSL certificate
   ssl_certificate_key /etc/nginx/ssl/privkey.pem; # Wildcard SSL certificate key


   location / {
       proxy_pass  http://localhost:1234;
       proxy_set_header Host $host;
   }
}
"""

config = SafeConfigParser()
config.read('.env')

if not config.has_section('main'):
    config.add_section('main')

print """
 __   __ _____ _____   _    _             _            
 \ \ / // ____/ ____| | |  | |           | |           
  \ V /| (___| (___   | |__| |_   _ _ __ | |_ ___ _ __ 
   > <  \___ \\\\___ \  |  __  | | | | '_ \| __/ _ \ '__|
  / . \ ____) |___) | | |  | | |_| | | | | ||  __/ |   
 /_/ \_\_____/_____/  |_|  |_|\__,_|_| |_|\__\___|_|   
                                                       
                                                       
                                           Setup Utility
    """

print "What is the base domain name you will be using? "
print "(ex. localhost, www.example.com)"
hostname = raw_input( "Domain? ")
if hostname != "":
    config.set('main', 'xssh_domain', hostname)	
nginx_template = nginx_template.replace( "fakedomain.com", hostname )

print "Great! Now let's setup your Mailgun account to send XSS alerts to."
print ""
print "Enter your API key: "
print "(ex. key-8da843ff65205a61374b09b81ed0fa35)"
config.set('main', 'xssh_mailgun_api_key', raw_input( "Mailgun API key: "))
print ""
print "What is your Mailgun domain? "
print "(ex. example.com)"
config.set('main', 'xssh_mailgun_sending_domain', raw_input( "Mailgun domain: "))
print ""
print "What email address is sending the payload fire emails?: "
print "(ex. no-reply@example.com)"
config.set('main', 'xssh_email_from', raw_input( "Sending email address: "))
print ""
print "Where should abuse/contact emails go?: "
print "(ex. yourpersonal@gmail.com)"
config.set('main', 'xssh_abuse_email', raw_input( "Abuse/Contact email: "))
print ""
print ""
print "What is your postgres hostname? "
print "(default postgres)"
p_hostname = raw_input( "Postgres hostname? ")
config.set('main', 'xssh_postgres_hostname', p_hostname if p_hostname != "" else "postgres"))
print ""
print ""
print "What postgres user is this service using? "
print "(ex. xsshunter)"
config.set('main', 'xssh_postgres_username', raw_input( "Postgres username: "))
print ""
print "What is the postgres user's password? "
print "(ex. @!$%@^%UOFGJOEJG$)"
config.set('main', 'xssh_postgres_password', raw_input( "Postgres password: "))
print ""
print "What is the postgres user's DB? "
print "(ex. xsshunter)"
config.set('main', 'xssh_postgres_db', raw_input( "Postgres DB: "))
print ""
print "Generating cookie secret..."
config.set('main', 'xssh_cookie_secret', binascii.hexlify( os.urandom(50))

with open('.env', 'w') as f:
    config.write(f)

print "Minting new nginx configuration file..."
file_handler = open( "default", "w" )
file_handler.write( nginx_template )
file_handler.close()

print """
Setup complete! Please now copy the 'default' file to /etc/nginx/sites-enabled/default
This can be done by running the following:
sudo cp default /etc/nginx/sites-enabled/default

Also, please ensure your wildcard SSL certificate and key are available at the following locations:
/etc/nginx/ssl/cert.pem; # Wildcard SSL certificate
/etc/nginx/ssl/privkey.pem; # Wildcard SSL key

Good luck hunting for XSS!
"""
