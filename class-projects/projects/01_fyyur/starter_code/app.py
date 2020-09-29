#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import sys
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy, get_debug_queries
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
from dataclasses import dataclass
# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_image_link = db.Column(db.String(500))
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)

    # def __repr__(self):
    #     return f'<Show - id: {self.id}, venue_id: {self.venue_id}, artist_id: {self.artist_id}>'


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String())
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(120))
    show = db.relationship('Show', backref='venue', lazy=True)

    # def __repr__(self):
    #     return f'<Venue - id: {self.id} Name: {self.name}, City: {self.city} >'

@dataclass
class Artist(db.Model):
    __tablename__ = 'artists'
    id: int
    name: str
    address: str
    city: str
    phone: str
    genres: str
    facebook_link: str

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String())
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    show = db.relationship('Show', backref='artist', lazy=True)

    # def __repr__(self):
    #     return f'<Artist - id: {self.id} Name: {self.name} Genres: {self.genres}>'


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

def format_shows(shows):
    formatted = []
    for show in shows:
        print(show[1].name)
        sys.stdout.flush()
        formatted.append({
            "venue_id": show[1].id,
            "venue_name": show[1].name,
            "venue_image_link": show[1].image_link,
            "start_time": str(show[0].start_time)
        })

    return formatted
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

    venues = Venue.query.order_by(Venue.state, Venue.city).all()
    shows = Show.query.with_entities(func.count(Show.venue_id), Show.venue_id).filter(Show.start_time > datetime.now()).group_by(Show.venue_id).group_by(Show.id).all()

    data = [];
    cityStateIndex = {}

    # dictionary key with citystate keeps tack of index
    # if key doesn't exist add new field to data list and dic (based off length)
    # Once it citystate index exists then add the venue informatiom
    # search for upcoming show count
    for v in venues:
        indexKey = v.city+v.state
        if indexKey not in cityStateIndex:
            cityStateIndex[indexKey] = len(data);
            data.append({"city":v.city, "state": v.state,"venues": [{}]});

        # find num show first
        numComingShows = 0
        for s in shows:
            if s.venue_id == v.id:
                print(s[1])
                sys.stdout.flush()
                numComingShows = s[1]



        data[cityStateIndex[indexKey]]['venues'].append({"id": v.id, "name": v.name, "num_upcoming_shows": numComingShows,})


    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # Search on Venues with partial string search. Ensure it is case-insensitive.

    term = request.form.get('search_term', '')
    match = Venue.query.filter(Venue.name.ilike("%"+term+"%")).all()
    response = {
        "count": len(match),
        "data": match
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id

    venue = Venue.query.filter(Venue.id == venue_id).one()
    comingShows = Show.query.join(Artist).filter(Show.start_time > datetime.now()).filter(Show.venue_id == venue_id).add_entity(Artist).all()
    pastShows = Show.query.join(Artist).filter(Show.start_time < datetime.now()).filter(Show.venue_id == venue_id).add_entity(Artist).all()

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.website,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": format_shows(pastShows),
        "upcoming_shows": format_shows(comingShows),
        "past_shows_count": len(pastShows),
        "upcoming_shows_count": len(comingShows),
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # insert form data as a new Venue record in the db, instead
    try:
        venue = Venue(name=request.form['name'], city=request.form['city'],
                      state=request.form['state'], address=request.form['address'],
                      phone=request.form['phone'], genres=request.form['genres'],
                      facebook_link=request.form['facebook_link'])
        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        # On unsuccessful db insert, flash an error instead.
        flash('There was an issue posting your venue.')
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():

    artists = Artist.query.all()
    return render_template('pages/artists.html', artists=Artist.query.all())


@app.route('/artists/search', methods=['POST'])
def search_artists():
    term = request.form.get('search_term', '')
    match = Artist.query.filter(Artist.name.ilike("%"+term+"%")).all()
    response = {
        "count": len(match),
        "data": match
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

    artist = Artist.query.filter(Artist.id == artist_id).one()
    comingShows = Show.query.join(Venue).filter(Show.start_time > datetime.now()).filter(Show.artist_id == artist_id).add_entity(Venue).all()
    pastShows = Show.query.join(Venue).filter(Show.start_time < datetime.now()).filter(Show.artist_id == artist_id).add_entity(Venue).all()

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "image_link": artist.image_link,
        "past_shows": format_shows(pastShows),
        "upcoming_shows": format_shows(comingShows),
        "past_shows_count": len(pastShows),
        "upcoming_shows_count": len(comingShows),
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.filter(Artist.id == artist_id).one()

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

    try:
        artist = Artist.query.get(artist_id)

        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.genres = request.form['genres']
        artist.facebook_link  = request.form['facebook_link']

        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully updated!')
    except:
        db.session.rollback()
        sucess = False
        print(sys.exc_info())
        sys.stdout.flush()
        flash('Artist ' + request.form['name'] + ' was NOT updated.')
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.filter(Venue.id == venue_id).one()

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    try:
        venue = Venue.query.get(venue_id)

        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        venue.genres = request.form['genres']
        venue.facebook_link  = request.form['facebook_link']

        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
    except:
        db.session.rollback()
        sucess = False
        print(sys.exc_info())
        sys.stdout.flush()
        flash('Venue ' + request.form['name'] + ' was NOT updated.')
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    try:
        # ImmutableMultiDict([('name', 'The Maxtastics'), ('city', 'Pflug'), ('state', 'AL'), ('phone', '33333333333'), ('genres', 'Classical'), ('facebook_link', 'face.com')])
        artist = Artist(name=request.form['name'], city=request.form['city'],
                        state=request.form['state'], phone=request.form['phone'],
                        genres=request.form['genres'], facebook_link=request.form['facebook_link'])
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        # On unsuccessful db insert, flash an error instead.
        flash('There was an issue listing your artist.')
    finally:
        db.session.close()
    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = [{
        "venue_id": 1,
        "venue_name": "The Musical Hop",
        "artist_id": 4,
        "artist_name": "Guns N Petals",
        "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "start_time": "2019-05-21T21:30:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 5,
        "artist_name": "Matt Quevedo",
        "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
        "start_time": "2019-06-15T23:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-01T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-08T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-15T20:00:00.000Z"
    }]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    try:
        show = Show(artist_id=request.form['artist_id'],
                    venue_id=request.form['venue_id'],
                    start_time=request.form['start_time'])
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        # On unsuccessful db insert, flash an error instead.
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
