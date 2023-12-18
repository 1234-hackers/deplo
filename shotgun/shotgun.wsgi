

import sys 
import logging 
  
  
logging.basicConfig(stream=sys.stderr) 
sys.path.insert(0,"/var/www/shotgun/") 
from shotgun  import app as application 
application.secret_key = "ikdkekosodkxk4382idjjx"
