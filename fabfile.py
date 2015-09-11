from fabric.api import *

def staging():
	"""Development server staging environment settings"""
	env.settings = 'staging'
	env.user = 'adi'
	env.hosts = ['128.199.193.7']
	env.base_path = '/home/adi/apps/py'
	env.path = env.base_path + '/lannister'
	env.git = 'https://github.com/daimagine/lannister.git'
	env.branch = 'develop'
	env.log_env = 'debug'
	env.dependencies = [
		{
			'name': 'stark',
			'git': 'https://github.com/daimagine/stark.git',
			'branch': 'develop'
		},
		{
			'name': 'sociale',
			'git': 'https://github.com/daimagine/sociale.git',
			'branch': 'develop'
		}
	]

def production():
	"""Production environment settings"""
	env.settings = 'production'
	env.user = 'adi'
	env.hosts = ['128.199.193.7']
	env.base_path = '/home/adi/apps/py'
	env.path = env.base_path + '/lannister'
	env.git = 'https://github.com/daimagine/lannister.git'
	env.branch = 'master'
	env.log_env = 'info'
	env.dependencies = [
		{
			'name': 'stark',
			'git': 'https://github.com/daimagine/stark.git',
			'branch': 'master'
		},
		{
			'name': 'sociale',
			'git': 'https://github.com/daimagine/sociale.git',
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
	# restart_worker()

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
			        	sudo('supervisorctl shutdown')
			        	sudo('supervisord -c %(path)s/deployment/supervisor/%(settings)s.conf' % env)
			        	sudo('cp %(path)s/deployment/nginx/%(settings)s.conf /etc/nginx/conf.d/ng_lannister.conf' % env)
			        	sudo('service nginx restart')

def restart_worker():
	"""Restart celery worker"""
	with settings(warn_only=True):
		with prefix('WORKON_HOME=$HOME/.virtualenvs'):
		    with prefix('source /usr/local/bin/virtualenvwrapper.sh'):
		        with cd('%(base_path)s' % env), prefix('workon jualio'):
		        	with prefix('add2virtualenv %(base_path)s' % env):
		        		sudo('celery multi stopwait w1 -A sociale -l %(log_env)s' % env)
		        		sudo('celery multi start w1 -A sociale -l %(log_env)s' % env)
