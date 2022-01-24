from typing import Dict, Any

# This is a dictionary where things can be stored
# between imports in a controlled way. It's one of the few
# things that get imported early on in the ourkvm startup sequence.
storage: Dict[str, Any] = {
	'LOG_PATH' : './'
}