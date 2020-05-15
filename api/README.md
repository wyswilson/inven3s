=====DEPENDENCIES============
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

ssh -i inven3s.pem ubuntu@13.229.67.229

create new screen: screen -S <screenname>
remove screen: screen -XS <screennumber> quit
==============================