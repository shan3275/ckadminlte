# Create dummy secrey key so we can use sessions
SECRET_KEY = 'Kstr)P(O*I&U^YOK'

# Create in-memory database
DATABASE_HOST = '127.0.0.1'
DATABASE = 'dydb'
DATABASE_CK_TB = 'cktb'
DATABASE_USER_TB = 'users'
DATABASE_PASSWORD = 'haiyao'
DATABASE_FILE = 'sample_db.sqlite'
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:'+DATABASE_PASSWORD+'@'+DATABASE_HOST+':3306/'+DATABASE
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask-Security config
SECURITY_URL_PREFIX = "/admin"
SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
SECURITY_PASSWORD_SALT = "ATGUOHAELKiubahiughaerGOJAEGj"

# Flask-Security URLs, overridden because they don't put a / at the end
SECURITY_LOGIN_URL = "/login/"
SECURITY_LOGOUT_URL = "/logout/"
SECURITY_REGISTER_URL = "/register/"

SECURITY_POST_LOGIN_VIEW = "/admin/"
SECURITY_POST_LOGOUT_VIEW = "/admin/"
SECURITY_POST_REGISTER_VIEW = "/admin/"

# Flask-Security features
SECURITY_REGISTERABLE = True
SECURITY_SEND_REGISTER_EMAIL = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
