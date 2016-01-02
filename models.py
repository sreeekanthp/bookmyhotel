from flask import Flask
from flask.ext.login import UserMixin
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.inspection import inspect
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired

application = Flask(__name__, static_url_path='')
application.secret_key = 'hotelBookingScecretKey'
application.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://booking_user:booking_password@localhost/data_booking'

db = SQLAlchemy(application)


class BaseMixin(db.Model):
    """ Base class for all models, with create, update, delete and serialize functions. """

    __abstract__ = True

    def serialize(self):
        data = {}
        if isinstance(self, Booking):
            hotel = Hotel.query.filter_by(id=self.hotel_id).first()
            data['hotel'] = {c: str(getattr(hotel, c)) for c in inspect(hotel).attrs.keys()}
        data.update({c: str(getattr(self, c)) for c in inspect(self).attrs.keys()})
        return data

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]

    def add(self, obj):
        db.session.add(obj)
        return db.session.commit()

    def update(self):
        return db.session.commit()

    def delete(self, obj):
        db.session.delete(obj)
        return db.session.commit()


class User(UserMixin, BaseMixin):
    """ User model with custom methods for checking hased password,
        generating and verifying auth tokens.
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True)
    realname = db.Column(db.String(50))
    password = db.Column(db.String)
    is_admin = db.Column(db.Boolean, server_default='false')

    def __init__(self, username, realname, password, is_admin=False):
        self.username = username
        self.realname = realname
        self.is_admin = is_admin
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def generate_auth_token(self):
        s = Serializer(application.config['SECRET_KEY'])
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(application.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user

    def __repr__(self):
        return '<Real Name %r>' % self.realname


class Hotel(BaseMixin):
    """ Model for Hotel details. """

    __tablename__ = "hotels"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    country = db.Column(db.String(100))
    zipcode = db.Column(db.String(15))
    nightly_rate = db.Column(db.Float)
    description = db.Column(db.Text)

    def __init__(self, name, address, city, state, country, zipcode, nightly_rate, description):
        self.name = name
        self.address = address
        self.city = city
        self.state = state
        self.country = country
        self.zipcode = zipcode
        self.nightly_rate = nightly_rate
        self.description = description

    def __repr__(self):
        return '<Hotel Name %r>' % self.name


class Booking(BaseMixin):
    """ Model for Booking details."""

    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    check_in = db.Column(db.DATE)
    check_out = db.Column(db.DATE)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    room_preference = db.Column(db.Integer)
    smoking_preference = db.Column(db.Boolean, server_default='false')
    credit_card_number = db.Column(db.String(16))
    credit_card_name = db.Column(db.String(30))
    credit_card_expiry = db.Column(db.DATE)

    def __init__(self, check_in, check_out, hotel_id, room_preference, smoking_preference,
                 credit_card_number, credit_card_name, credit_card_expiry, user_id):
        self.check_in = check_in
        self.check_out = check_out
        self.hotel_id = hotel_id
        self.room_preference = room_preference
        self.smoking_preference = smoking_preference
        self.credit_card_number = credit_card_number
        self.credit_card_name = credit_card_name
        self.credit_card_expiry = credit_card_expiry
        self.user_id = user_id

    def __repr__(self):
        hotel = Hotel.query.filter_by(id=self.hotel_id).first()
        return '<Booking on %r>' % hotel.name
