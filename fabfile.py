from fabric.api import *

def production():
	"""Production environment settings"""
	env.settings = 'production'
	env.user = 'adi'
	env.password = 'adi!@#'
	env.hosts = ['128.199.193.7']
	env.base_path = '/home/adi/apps/py'
	env.path = env.base_path + '/lannister'
	env.git = 'https://github.com/daimagine/lannister.git'
	env.branch = 'master'
	env.dependencies = [
		{
			'name': 'stark',
			'git': 'https://github.com/daimagine/stark.git',
			'branch': 'master'
		}
	]

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

def clone_dependencies():
	"""Do initial clone of the git repo dependencies"""
	with cd('%(base_path)s' % env):
		for repo in env.dependencies:
			run('git clone %(git)s %(name)s' % repo)

def clone_repo():
	"""Do initial clone of the git repo"""
	clone_dependencies()
	with cd('%(base_path)s' % env):
		run('git clone %(git)s' % env)

def checkout_dependencies():
	"""Pull dependencies repo project"""
	with cd('%(base_path)s' % env):
		for repo in env.dependencies:
			with cd('%(name)s' % repo):
				run("git checkout %(branch)s" % repo)
				run("git pull --rebase")

def checkout_latest():
	"""Pull the latest code into the git repo"""
	checkout_dependencies()
	with cd('%(path)s' % env):
		run("git checkout %(branch)s" % env)
		run("git pull --rebase")

def install_requirements():
	"""Install the required packages using pip"""
	sudo("apt-get install python-pip")
	sudo("pip install virtualenv")
	sudo("pip install virtualenvwrapper")
	run("pip install supervisor")
	sudo("mkdir -p /var/log/supervisord")
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
		with prefix('WORKON_HOME=$HOME/.virtualenvs'):
		    with prefix('source /usr/local/bin/virtualenvwrapper.sh'):
		        with cd('%(path)s' % env), prefix('workon jualio'):
		        	with prefix('add2virtualenv %(base_path)s' % env):
			        	sudo('kill -9 `cat /var/run/supervisord.pid`')
			        	sudo('rm /tmp/supervisor.sock')
			        	sudo('rm /var/run/supervisor.sock')
			        	sudo('rm /var/run/supervisord.pid')
			        	sudo('supervisord -c %(path)s/supervisor/production.conf' % env)
			        	sudo('cp %(path)s/supervisor/ng_lannister.conf /etc/nginx/conf.d/ng_lannister.conf' % env)
			        	sudo('service nginx restart')


