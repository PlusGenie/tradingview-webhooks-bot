# settings
import uuid
import os

LOG_LOCATION = 'components/logs/log.log'
LOG_LIMIT = 100

# ensure log file exists
try:
    open(LOG_LOCATION, 'r')
except FileNotFoundError:
    open(LOG_LOCATION, 'w').close()

# DO NOT CHANGE
VERSION_NUMBER = '0.5'


# if key file exists, read key, else generate key and write to file
# WARNING: DO NOT CHANGE KEY ONCE GENERATED (this will break all existing events)
try:
    UNIQUE_KEY = os.environ.get('TVWB_UNIQUE_KEY', '').strip()
    if not UNIQUE_KEY:
        with open('.keyfile', 'r') as key_file:
            UNIQUE_KEY = key_file.read().strip()
    else:
        # "Replace the saved key with the one from the environment."
        with open('.keyfile', 'w') as key_file:
            key_file.write(UNIQUE_KEY)
except FileNotFoundError:
    UNIQUE_KEY = str(uuid.uuid4())
    with open('.keyfile', 'w') as key_file:
        try:
            key_file.write(UNIQUE_KEY)
        except IOError as e:
            print(f"Error writing to .keyfile: {e}")
