BookMyHotel
============

Bookmyhotel is a flask web application for searching and booking hotels. This is a python implementation of the revel app https://github.com/revel/samples/tree/master/booking

Technology stack used
--------------------
 - Python3.4
 - Postgresql
 - Flask
 - SQLAlchemy

How to Install
--------------

- Clone the repository

 - git clone https://github.com/sreekanthkaralmanna/bookmyhotel.git

- Create a python3 virtual environment and activate the environment.
	- `virtualenv bookmyhotel`
	- `source bookmyhotel/bin/activate`

- Install requirements.
	- `pip install -r  requirements.txt`

- Update database credentials in `bookmyhotel/models.py` with your postgresql db user, password and db name.

- Create migration files and initialize database
	- `python manage.py db init`
	- `python manage.py db migrate`
	- `python manage.py db upgrade`

- Create a super user. Default username and password will be 'admin' and 'password' respectively. However you can override those values as follows:
	- `python manage.py create_superuser -u <user_name> -p <password>`

- Run application.
	- `python app.py`


User Roles
----------
There will be two types of users in the application.

 - Admin user (created by `python manage.py create_superuser` command)
 - Application user

Only admin user will have the privilege to create hotels.


Public APIs
----------

- POST /api/users - API to create a user.

> Input - { 	username: 'username', 	password: 'password', 	realname:
> 'realname' }
> 
> Output - { 	'token': 'authentication_token' }

- POST /api/login - API to login a user.

> Input - { 	username: 'username', 	password: 'password', }
> 
> Output - { 	'token': 'authentication_token' }


- GET /api/bookings/ - API to get the list of bookings.
   Note: API header mush have Authorization token.

> Output - List of bookings

- POST /api/bookings/ - API to get the list of bookings.
   Note: API header mush have Authorization token.

> Input - { 	'hotel_id': 1, 	'user_id': 1, 	'check_in': '2016-09-09',
> 	'check_out': '2016-09-10', 	'room_preference': 1,
> 	'smoking_preference': true, 	'credit_card_number':
> '1234567891234567', 	'credit_card_name': 'John Smith',
> 	'credit_card_expiry': '2016-09-09' }
> 
> Output - { 	'booking_id': 1 }

- GET /api/hotels/ - API to get the list of hotels.

> Output - List of hotels


- POST /api/hotels/ - API to get the list of bookings.
Note: API header mush have Authorization token for admin user.

> Input - { 	'name': 'Burj Khalifa', 	'description': 'Spired 828-meter
> skyscraper with a viewing deck, restaurant, hotel and offices and
> 11-hectare park.', 	'address': '1 Sheikh Mohammed bin Rashid Blvd -
> Dubai', 	'city': 'Dubai', 	'state': 'Duabi', 	'country': 'United Arab
> Emirates', 	'zipcode': '323232', 	'nightly_rate': 1000, }
> 
> Output - { 	'hotel_id': 1 }


- DELETE /api/bookings/<int:booking_id> - API to delete a booking
Note: API header mush have Authorization token.


- GET /api/hotels/<int:hotel_id> - API to get the details of a hotel

> Output - { 	'id': 1 	'name': 'Burj Khalifa', 	'description': 'Spired
> 828-meter skyscraper with a viewing deck, restaurant, hotel and
> offices and 11-hectare park.', 	'address': '1 Sheikh Mohammed bin
> Rashid Blvd - Dubai', 	'city': 'Dubai', 	'state': 'Duabi', 	'country':
> 'United Arab Emirates', 	'zipcode': '323232', 	'nightly_rate': 1000, }






