from sqlalchemy import Column, String, Integer, Boolean

from database import Base

class Accounts(Base):
	__tablename__="accounts"

	#username, posts, followers, following, private, bio_tag, external_url, verified
	username=Column(String,primary_key=True, index=True)
	posts=Column(Integer)
	followers=Column(Integer)
	following=Column(Integer)
	private=Column(Boolean)
	bio_tag=Column(Boolean)
	verified=Column(Boolean)


