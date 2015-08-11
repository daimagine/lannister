# Copyright 2014-2015 Clione Software and Havas Worldwide London
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import logging
import logging.config


__env__ = os.getenv('DEPLOYMENT_TARGET', 'dev')
__version__ = '1'
__codename__ = 'Lannister'
__status__ = 'alpha'
__docs__ = 'http://docs.jualio.com/api/v1/docs.html'

if __env__ == 'production':
    from .production import *

elif __env__ == 'staging':
    from .staging import *

else:
    from .development import *

def env():
	return __env__

# setting log
print(LOGGING_CONFIG)
logging.config.dictConfig(LOGGING_CONFIG)	