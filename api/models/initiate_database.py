import os

from sqlalchemy import create_engine
engine = create_engine('postgresql://' + os.getenv("xssh_postgres_username", default="") + ':' + os.getenv("xssh_postgres_password", default="") + '@' + os.getenv("xssh_postgres_hostname", default="") + '/' + os.getenv("xssh_postgres_db", default="") + '?client_encoding=utf8', pool_recycle=60, encoding='utf8')
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from sqlalchemy import Column, Integer, String, func, update, Text, Binary, Boolean, BigInteger, event, select, exc
from sqlalchemy.orm import sessionmaker, scoped_session
Session = scoped_session(sessionmaker(bind=engine))
session = Session()
