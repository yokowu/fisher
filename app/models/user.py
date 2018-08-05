from sqlalchemy import Column, Integer, String, Boolean, Float
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .base import Base
from app.libs.helper import is_isbn_or_key
from app.models.gift import Gift
from app.models.wish import Wish
from app.spider.yushu_book import YuShuBook
from app import login_manager


class User(UserMixin, Base):
	id = Column(Integer, primary_key=True)
	nickname = Column(String(24), nullable=False)
	phone_number = Column(String(18), unique=True)
	email = Column(String(50), unique=True, nullable=False)
	confirmed = Column(Boolean, default=False)
	beans = Column(Integer, default=0)
	_password = Column('password', String(128), nullable=False)
	send_counter = Column(Integer, default=0)
	receive_counter = Column(Integer, default=0)
	wx_open_id = Column(String(50))
	wx_name = Column(String(32))
	
	@property
	def password(self):
		return self._password
		
	@password.setter
	def password(self, raw):
		self._password = generate_password_hash(raw)
		
	def check_password(self, raw):
		return check_password_hash(self._password, raw)

	def can_save_to_list(self, isbn):
		if is_isbn_or_key(isbn) != 'isbn':
			return False
		yushu_book = YuShuBook()
		yushu_book.search_by_isbn(isbn)
		if not yushu_book.first:
			return False
		gifting = Gift.query.filter_by(uid=self.id, isbn=isbn,
									launched=False).first()
		wishting = Wish.query.filter_by(uid=self.id, isbn=isbn,
									launched=False).first()
		if not gifting and not wishting:
			return True
		else:
			return False
		
		
@login_manager.user_loader
def get_user(uid):
	return User.query.get(int(uid))
