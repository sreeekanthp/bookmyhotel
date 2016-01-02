import datetime
import json
import flask.ext.login as flask_login

from flask import request, render_template, send_from_directory,\
    redirect, url_for, session, jsonify, abort, make_response
from functools import wraps
from werkzeug.security import generate_password_hash

from models import application, User, Hotel, Booking


login_manager = flask_login.LoginManager()
login_manager.login_view = "home"
login_manager.init_app(application)


def requires_auth(f):
    """ Login decorator for user authentication with token. """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token:
            user = User.verify_auth_token(token)
            if not user:
                return make_response(jsonify({'error': 'Unauthorized access'}), 403)
            return f(*args, **kwargs)
        return make_response(jsonify({'error': 'Unauthorized access'}), 403)
    return decorated


def requires_admin_auth(f):
    """ Returns user if logged in user is an admin """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not flask_login.current_user.is_admin:
            return False
        return f(*args, **kwargs)
    return decorated


@application.errorhandler(404)
def not_found(error):
    """ Returns 404 Not Found error. """

    return make_response(jsonify({'error': 'Not found'}), 404)


def validate_date(date_text):
    """ Function to validate date and returns a datetime object."""

    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")


def validate_credit_card_number(number):
    """ Luhn algorithm to validate credit card number """

    r = [int(ch) for ch in str(number)][::-1]
    return (sum(r[0::2]) + sum(sum(divmod(d * 2, 10)) for d in r[1::2])) % 10 == 0


# API Views starts

@application.route('/api/get_token', methods=['GET'])
def get_token_from_session():
    """ Retrives the token from session. """

    token = session['token']
    return jsonify({'token': token.decode('ascii')})


@application.route('/api/login', methods=['POST'])
def api_login():
    """ Logins the user and save the token in session to reuse in the apis. """

    username = request.json.get('username')
    password = request.json.get('password')
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return make_response(jsonify({'error': 'Invalid username or password'}), 400)
    token = user.generate_auth_token()
    flask_login.login_user(user)
    session['token'] = token
    return jsonify({'token': token.decode('ascii')})


@application.route('/api/users', methods=['POST'])
def api_create_user():
    """ Creates a new user, with sign up and login the user. """

    username = request.json.get('username')
    password = request.json.get('password')
    realname = request.json.get('realname')
    if username is None or password is None or realname is None:
        abort(400)  # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        return make_response(jsonify({'error': 'User with this username already exists'}), 400)  # existing user
    user = User(username, realname, password, False)
    user.add(user)
    flask_login.login_user(user)
    token = user.generate_auth_token()
    session['token'] = token
    return jsonify({'token': token.decode('ascii')})


@application.route('/api/change_password', methods=['POST'])
@requires_auth
def api_change_password():
    """ Changes the password of the user. """

    password = request.json.get('password')
    token = request.headers['Authorization']
    user = User.verify_auth_token(token)
    user.password = generate_password_hash(password)
    user.update()
    return jsonify({'user': user.id})


@application.route('/api/bookings/', methods=['GET', 'POST'])
@requires_auth
def api_bookings():
    """ Creates the booking for user on selected hotel;
        Returns the list of bookings for the user.
    """

    if request.method == 'POST':
        errors = {}
        if not request.json:
            abort(400)

        # Validate required fields.
        for field in ['hotel_id', 'check_in', 'check_out', 'room_preference', 'smoking_preference', 'credit_card_number', 'credit_card_name', 'credit_card_expiry']:
            if not request.json.get(field):
                errors[field] = 'This field is required'

        # Validate field value
        if not ('hotel_id' not in errors and Hotel.query.filter_by(id=request.json['hotel_id'])):
            errors['hotel_id'] = 'No hotels found with the given id'
        if not ('check_in' not in errors and validate_date(request.json['check_in'])):
            errors['check_in'] = 'Incorrect data format, should be YYYY-MM-DD'
        if not ('check_out' not in errors and validate_date(request.json['check_out'])):
            errors['check_out'] = 'Incorrect data format, should be YYYY-MM-DD'
        if not ('credit_card_expiry' not in errors and validate_date(request.json['credit_card_expiry'])):
            errors['credit_card_expiry'] = 'Incorrect data format, should be YYYY-MM-DD'
        if not ('room_preference' not in errors and request.json['room_preference'] in ["1", "2", "3"]):
            errors['room_preference'] = 'Select a value between 1 to 3'
        if not ('smoking_preference' not in errors and isinstance(request.json['smoking_preference'], bool)):
            errors['smoking_preference'] = 'Value should be either true or false'
        if not ('credit_card_number' not in errors and validate_credit_card_number(request.json['credit_card_number'])):
            errors['credit_card_number'] = 'Invalid credit card number'

        if errors:
            return make_response(jsonify({'error': errors}), 400)
        booking = Booking(request.json['check_in'],
                          request.json['check_out'],
                          request.json['hotel_id'],
                          request.json['room_preference'],
                          request.json['smoking_preference'],
                          request.json['credit_card_number'],
                          request.json['credit_card_name'],
                          request.json['credit_card_expiry'],
                          request.json['user_id'])
        booking.add(booking)
        return make_response(jsonify({'booking_id': booking.id}), 201)
    else:
        token = request.headers['Authorization']
        user = User.verify_auth_token(token)
        bookings = Booking.query.filter_by(user_id=user.id).all()
        return json.dumps(Booking.serialize_list(bookings))


@application.route('/api/hotels/', methods=['GET', 'POST'])
@requires_auth
def api_hotels():
    """ Hotels list view. If the user is admin user, will allow to create new hotels. """

    if request.method == 'POST':
        token = request.headers['Authorization']
        user = User.verify_auth_token(token)
        if not user.is_admin:  # If the user is not admin, raise error
            return make_response(jsonify({'error': 'Unauthorized access'}), 403)

        errors = {}
        if not request.json:
            return make_response(jsonify({'error': 'No data found'}), 400)

        # Validate required fields.
        for field in ['name', 'address', 'city', 'state', 'country', 'zipcode', 'nightly_rate', 'description']:
            if not request.json.get(field):
                errors[field] = 'This field is required'

        # Validate field value
        try:
            float(request.json['nightly_rate'])
        except:
            errors['nightly_rate'] = 'Invalid nightly rate'
        if errors:
            return make_response(jsonify({'error': errors}), 400)

        hotel = Hotel(request.json['name'],
                      request.json['address'],
                      request.json['city'],
                      request.json['state'],
                      request.json['country'],
                      request.json['zipcode'],
                      request.json['nightly_rate'],
                      request.json['description'])
        hotel.add(hotel)
        return make_response(jsonify({'hotel': hotel.id}), 201)
    else:
        return json.dumps(Hotel.serialize_list(Hotel.query.all()))


@application.route('/api/bookings/<int:booking_id>', methods=['DELETE'])
@requires_auth
def delete_booking(booking_id):
    """ Delete an existing booking. """

    if not Booking.query.filter_by(id=booking_id).all():
        abort(404)
    booking = Booking.query.filter_by(id=booking_id).first()
    booking.delete(booking)
    return jsonify({}), 201


@application.route('/api/hotels/<int:hotel_id>', methods=['GET'])
def get_hotel(hotel_id):
    """ Get details of a hotel with the given id."""

    if not Hotel.query.filter_by(id=hotel_id).all():
        abort(404)
    hotel = Hotel.query.filter_by(id=hotel_id).first()
    return jsonify({'result': hotel.serialize()})

# API Views ends


# Application views starts

@login_manager.user_loader
def get_user(ident):
    return User.query.get(int(ident))


@application.route('/logout')
def logout():
    """ Logout the user and remove the token from session."""

    flask_login.logout_user()
    session['token'] = ''
    return redirect(url_for('home'))


@application.route('/')
def home():
    """ Serves login page if user is not authenticated else
        the home page, listing the hotels.
    """

    if flask_login.current_user.is_authenticated:
        return render_template('home.html')
    return render_template('index.html')


@application.route('/bookings', strict_slashes=False)
@flask_login.login_required
def bookings():
    """Serves the user bookings list. """

    return render_template('bookings.html')


@application.route('/bookings/<int:booking_id>', strict_slashes=False)
@flask_login.login_required
def get_booking_detail(booking_id):
    """ Fetches the specific booking with id. """
    return render_template('bookings.html', booking_id=booking_id)


@application.route('/book_hotel/<int:hotel_id>')
@flask_login.login_required
def book_hotel(hotel_id):
    """ Serves the hotel booking page. """
    return render_template('bookhotel.html', hotel_id=hotel_id, user_id=flask_login.current_user.id)


@application.route('/create_hotel')
@requires_admin_auth
@flask_login.login_required
def hotel_create():
    """ Serves the hotel create page for admin. """

    return render_template('hotelcreate.html')


@application.route('/hotels/<int:hotel_id>')
@flask_login.login_required
def get_hotel_detail(hotel_id):
    """ Fetches the hotel details with id. """

    return render_template('hoteldetail.html', hotel_id=hotel_id)


@application.route('/static/<path:path>')
def send_js(path):
    """ Serves static files. """
    return send_from_directory('static', path)


if __name__ == '__main__':
    application.run(debug=True)
