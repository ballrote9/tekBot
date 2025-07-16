from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database.session import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    auth_token = Column(String(64), ForeignKey('about_users.auth_token'), unique=True)
    hash_pass = Column(String(128))
    is_authorized = Column(Boolean)

    user_info = relationship("User_info", foreign_keys=[auth_token], uselist=False)


class User_info(Base):
    __tablename__ = "about_users"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(50))
    mail = Column(String(127), nullable=True)
    office = Column(String(64), nullable=True)
    officephone = Column(String(20), nullable=True)

    username = Column(String(50), nullable=True)
    auth_token = Column(String(64), ForeignKey('users.auth_token'), unique=True)
    
    
class Authorized_users(Base):
    __tablename__ = "Authorized_users"
    
    id = Column(Integer, primary_key=True)
    auth_token = Column(String(64), ForeignKey('users.auth_token'), unique=True)
    
    user = relationship("User", foreign_keys=[auth_token], uselist=False)