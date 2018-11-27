import ConfigParser
from ConfigParser import SafeConfigParser
try:
    config = SafeConfigParser()
    config.read('.env')
    if not config.has_section('main'):
        raise ConfigParser.NoSectionError('main')
except IOError:
    print "INITIATEDB: Error reading .env, have you created one? (Hint: Try running ./generate_config.py)"
    exit()

from sqlalchemy import create_engine
engine = create_engine('postgresql://' + config.get('main', "xssh_postgres_username") + ':' + config.get('main', "xssh_postgres_password") + '@' + config.get('main', "xssh_postgres_hostname") + '/' + config.get('main', "xssh_postgres_db") + '?client_encoding=utf8', pool_recycle=60, encoding='utf8')
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from sqlalchemy import Column, Integer, String, func, update, Text, Binary, Boolean, BigInteger, event, select, exc
from sqlalchemy.orm import sessionmaker, scoped_session
Session = scoped_session(sessionmaker(bind=engine))
session = Session()
