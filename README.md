==============COLORSCHEME===========
LIGHTEST 	dcdfe3
LIGHT    	b9bec7
MEDIUM	 	848b96
DARK 		374152 (NEW)
DARKEST	 	111721
ERR			c75061

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
ssh -i inven3s.pem ubuntu@13.229.67.229

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

==============NGINX=================
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

sudo nano /etc/nginx/sites-enabled and change the default port 80 to something else
sudo service nginx restart
systemctl status nginx.service 