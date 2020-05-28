==============COLORSCHEME===========
LIGHTEST 	e6e3e3
LIGHT    	c9c9c9
MEDIUM	 	7B797C 
DARK 		444243
DARKEST	 	0E0D0B
ERR			c75061
LOGIN BACKGROUNDIMG CREDIT "Photo by Muradi on Unsplash" (https://unsplash.com/photos/0b8NaL2CMaQ)

==============NETWORKING============
Original godaddy=>
ns17.domaincontrol.com
ns18.domaincontrol.com

==============PYTHON================
python -m pip install --upgrade pip
pip install virtualenv
pip install virtualenvwrapper-win
mkvirtualenv <projectname> or virtualenv <projectname>
workon <projectname> OR source /home/ubuntu/inven3s/api/inven3s/bin/activate
rmvirtualenv <projectname>
	
pip install flask
pip install mysql-connector-python
pip install simplejson
pip install requests
pip install bs4
pip install pyjwt
pip install py3-validate-email
pip install flask-cors
pip install waitress

==============UBUNTU/SCREEN=========
Home => /home/ubuntu/inven3s
WEBAPP 	ssh -i inven3s.pem ubuntu@13.229.67.229
API 	ssh -i inven3s.pem ubuntu@13.229.135.211

create new screen: screen -S <screenname>
remove screen: screen -XS <screennumber> quit

==============NPM===================
PACKAGE DEPENDENCY
npm i semantic-ui-calendar-react
npm i semantic-ui-react
npm i react
npm i react-favicon
npx create-react-app my-app
npm i react-device-detect

If we need NPM web server only running on HTTPS:
export HTTPS=true

==============NGINX=================
RUNS ON WEBAPP
sudo apt-get install nginx
sudo nano /etc/nginx/nginx.conf

server {
   listen         80 default_server;
   listen         [::]:80 default_server;
   server_name    localhost;
   root           /usr/share/nginx/html;
   location / {
       proxy_pass http://127.0.0.1:3000;
       proxy_http_version 1.1;
       proxy_set_header Upgrade $http_upgrade;
       proxy_set_header Connection 'upgrade';
       proxy_set_header Host $host;
       proxy_cache_bypass $http_upgrade;
   }
}

sudo nano /etc/nginx/sites-enabled/default and change the default port 80 to something else. this file uses the default port 80 which needs to be changed. 
sudo service nginx restart
systemctl status nginx.service 

==============SSL/HTTPS================
sudo service nginx stop
pip install certbot-nginx
sudo apt-get install python3-certbot-nginx
sudo certbot --nginx -d inven3s.com -d www.inven3s.com
sudo certbot --nginx -d 13.229.135.211
sudo service nginx restart
(https://medium.com/@poudel.01anuj/deploying-reactjs-project-on-the-linux-server-with-ssl-certificate-https-aa14bf2737aa)

 Congratulations! Your certificate and chain have been saved at:
   /etc/letsencrypt/live/inven3s.com/fullchain.pem
   Your key file has been saved at:
   /etc/letsencrypt/live/inven3s.com/privkey.pem
   Your cert will expire on 2020-08-26. To obtain a new or tweaked
   version of this certificate in the future, simply run certbot again
   with the "certonly" option. To non-interactively renew *all* of
   your certificates, run "certbot renew"
 - Your account credentials have been saved in your Certbot
   configuration directory at /etc/letsencrypt. You should make a
   secure backup of this folder now. This configuration directory will
   also contain certificates and private keys obtained by Certbot so
   making regular backups of this folder is ideal.