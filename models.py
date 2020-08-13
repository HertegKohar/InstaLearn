from sqlalchemy import Column, String, Integer, Boolean

from database import Base


class User(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True, index=True)
    password = Column(String, nullable=False)


class Account(Base):
    __tablename__ = "accounts"

    # username, posts, followers, following, private, bio_tag, external_url, verified
    username = Column(String, primary_key=True, index=True)
    posts = Column(Integer)
    followers = Column(Integer)
    following = Column(Integer)
    private = Column(Boolean)
    bio_tag = Column(Boolean)
    verified = Column(Boolean)

