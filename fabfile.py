from fabric.api import *

def production():
	"""Production environment settings"""
	env.settings = 'production'
	env.user = 'adi'
	env.hosts = ['128.199.193.7']
	env.base_path = '/home/adi/apps/py'
	env.path = env.base_path + '/lannister'
	env.git = 'https://github.com/daimagine/lannister.git'l
	env.branch = 'master'

def setup():
	"""
	Setup a fresh virtualenv and install everything we need so it's ready to deploy to
	"""
	run('mkdir -p %(base_path)s;' % env)
	clone_repo()
	checkout_latest()
	install_requirements()

def deploy():
	"""Deploy the latest version of the site to the server and restart nginx"""
	checkout_latest()
	restart_server()

def clone_repo():
	"""Do initial clone of the git repo"""
	with cd('%(base_path)s' % env):
		run('git clone %(git)s' % env)

def checkout_latest():
	"""Pull the latest code into the git repo and copy to a timestamped release directory"""
	with cd('%(path)s' % env):
		run("git checkout %(branch)s" % env)
		run("git pull --rebase")

def install_requirements():
	"""Install the required packages using pip"""
	sudo("apt-get install python-pip")
	sudo("pip install virtualenv")
	sudo("pip install virtualenvwrapper")
	with cd('$HOME'):
		run("virtualenv --no-site-packages .virtualenvs")
	with prefix('WORKON_HOME=$HOME/.virtualenvs'):
	    with prefix('source /usr/local/bin/virtualenvwrapper.sh'):
	    	run("mkvirtualenv jualio")
	        with cd('%(path)s' % env), prefix('workon jualio'):
		        run('pip install -r requirements.txt') # Works in virtualenv

def restart_server():
	"""Restart the web server"""
	with settings(warn_only=True):
		sudo('kill -9 `cat /tmp/project-master_helpmamme.pid`')
		sudo('rm /tmp/project-master_helpmamme.pid /tmp/uwsgi_helpmamme.sock')
		run('cd %(path)s/releases/current; %(path)s/bin/uwsgi --ini %(path)s/releases/current/uwsgi.ini' % env)
		sudo('/etc/init.d/nginx restart')
