#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from email.headerregistry import Address
import sys
import json

import dateutil.parser
import babel 
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from flask_migrate import Migrate
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)


app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    seeking_venue= db.Column(db.Boolean,default=False,nullable=False)
    seeking_description = db.Column(db.String())
    venues = db.relationship('Venue', secondary='shows')
    shows = db.relationship('Show',backref=('artists'))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'genres': self.genres.split(','),
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'website_link': self.website_link,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description,
        }
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
     
    
    
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    seeking_talent= db.Column(db.Boolean,default=False,nullable=False)
    seeking_description = db.Column(db.String())
    artists = db.relationship('Artist', secondary='shows')
    shows = db.relationship('Show', backref=('venues'))
   
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'address': self.address,
            'phone': self.phone,
            'genres': self.genres.split(','),
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'website_link': self.website_link,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description,
        }

    
    
    
 
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
class Show(db.Model):
  __tablename__='shows'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey(
        'artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey(
        'venue.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)
  venue = db.relationship('Venue')
  artist = db.relationship('Artist')

  def show_artist(self):
        """ Returns a dictinary of artists for the show """
        return {
            'artist_id': self.artist_id,
            'artist_name': self.artist.name,
            'artist_image_link': self.artist.image_link,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S')
        }

  def show_venue(self):
        return {
            'venue_id': self.venue_id,
            'venue_name': self.venue.name,
            'venue_image_link': self.venue.image_link,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S')
        }


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

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
    venues = db.session.query(Venue.city,Venue.state).distinct(Venue.city,Venue.state)

    data = []
    for venue in venues:
        tempo = Venue.query.filter(Venue.state==venue.state).filter(Venue.city==venue.city).all()
        venue_data =[]
        tmp = {}
        prev_city = None
        prev_state = None

        for row in tempo:
           venue_data.append({
                'id': row.id,
                'name': row.name,
                'num_upcoming_shows': len(db.session.query(Show).filter(Show.start_time > datetime.now()).all())
            })
           if row.city == prev_city and row.state == prev_state:
             tmp['venues'].append(venue_data)
           else:
            if prev_city is not None:
              data.append(tmp)
            tmp['city']= venue.city
            tmp['state'] = venue.state
            tmp['venues']=venue_data
        data.append(tmp)
          

           

  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    
    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term')
  venues = Venue.query.filter(
        Venue.name.ilike('%{}%'.format(search_term))).all()

  data = []
  for venue in venues:
        tmp = {}
        tmp['id'] = venue.id
        tmp['name'] = venue.name
        tmp['num_upcoming_shows'] = len(venue.shows)
        data.append(tmp)

  response = {}
  response['count'] = len(data)
  response['data'] = data

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.filter(Venue.id == venue_id).first()

  past = db.session.query(Show).filter(Show.venue_id == venue_id).filter(
        Show.start_time < datetime.now()).join(Artist, Show.artist_id == Artist.id).add_columns(Artist.id, Artist.name, Artist.image_link, Show.start_time).all()

  upcoming = db.session.query(Show).filter(Show.venue_id == venue_id).filter(
        Show.start_time > datetime.now()).join(Artist, Show.artist_id == Artist.id).add_columns(Artist.id, Artist.name,  Artist.image_link,  Show.start_time).all()

  upcoming_shows = []

  past_shows = []

  for i in upcoming:
        upcoming_shows.append({
            'artist_id': i[1],
            'artist_name': i[2],
            'image_link': i[3],
            'start_time': str(i[4])
        })

  for i in past:
        past_shows.append({
            'artist_id': i[1],
            'artist_name': i[2],
            'image_link': i[3],
            'start_time': str(i[4])
        })

  data = venue.to_dict()
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)
  return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
          form = VenueForm()
          if  form.validate_on_submit():
              error = False
              try:
                  venue = Venue()
                  venue.name = request.form['name']
                  venue.city = request.form['city']
                  venue.state = request.form['state']
                  venue.address = request.form['address']
                  venue.phone = request.form['phone']
                  tmp_genres = request.form.getlist('genres')
                  venue.genres = ','.join(tmp_genres)
                  venue.facebook_link = request.form['facebook_link']
                  venue.image_link = request.form['image_link']
                  venue.seeking_talent = request.form.get('seeking_talents')
                  venue.seeking_description = request.form['seeking_description']
                  venue.website_link = request.form['website_link']
                  
                  
                  
                  db.session.add(venue)
                  db.session.commit()
              except:
                  error = True
                  db.session.rollback()
                  print(sys.exc_info())
              finally:
                  db.session.close()
                  if error:
                      flash('An error occured. Venue ' +
                            request.form['name'] + ' Could not be listed!')
                  else:
                      flash('Venue ' + request.form['name'] +
                            ' was successfully listed!')
              return render_template('pages/home.html')
          else:
              for field, message in form.errors.items():
                 flash(field + ' - ' + str(message), 'danger')
                 return render_template('forms/new_venue.html', form=form)
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      

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
  # TODO: replace with real data returned from querying the database
  
  return render_template('pages/artists.html', artists=Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term')
  artists = Artist.query.filter(
        Artist.name.ilike('%{}%'.format(search_term))).all()

  data = []
  for artist in artists:
        tmp = {}
        tmp['id'] = artist.id
        tmp['name'] = artist.name
        tmp['num_upcoming_shows'] = len(artist.shows)
        data.append(tmp)

  response = {}
  response['count'] = len(data)
  response['data'] = data
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.filter(Artist.id == artist_id).first()

    past = db.session.query(Show).filter(Show.artist_id == artist_id).filter(
        Show.start_time < datetime.now()).join(Venue, Show.venue_id == Venue.id).add_columns(Venue.id, Venue.name,
                                                                                             Venue.image_link,
                                                                                             Show.start_time).all()

    upcoming = db.session.query(Show).filter(Show.artist_id == artist_id).filter(
        Show.start_time > datetime.now()).join(Venue, Show.venue_id == Venue.id).add_columns(Venue.id, Venue.name,
                                                                                             Venue.image_link,
                                                                                             Show.start_time).all()

    upcoming_shows = []

    past_shows = []

    for i in upcoming:
        upcoming_shows.append({
            'venue_id': i[1],
            'venue_name': i[2],
            'image_link': i[3],
            'start_time': str(i[4])
        })

    for i in past:
        past_shows.append({
            'venue_id': i[1],
            'venue_name': i[2],
            'image_link': i[3],
            'start_time': str(i[4])
        })

    data = artist.to_dict()
    data['past_shows'] = past_shows
    data['upcoming_shows'] = upcoming_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)
    return render_template('pages/show_venue.html', venue=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm()
  error= False
  if form.validate_on_submit():
        try :
          artist = Artist()
          artist.name = request.form.get('name')
          artist.city = request.form.get('city')
          artist.state = request.form.get('state')
          artist.phone = request.form.get('phone')
          tmp_genres = request.form.getlist('genres')
          artist.genres =','.join(tmp_genres)
          artist.facebook_link = request.form.get('facebook_link')
          artist.image_link = request.form.get('image_link')
          artist.website_link = request.form.get('web_link')
          artist.seeking_venue = request.form.get('looking_venues')
          artist.seeking_description = request.form.get('seeking_description')
          db.session.add(artist)
          db.session.commit()
        except:
          error= True
          db.session.rollback()
          print(sys.exc_info())
        finally:
          db.session.close()
          if error:
            flash('an error occurred. Artist '+ request.form.get('name') +' could not be listed.')
          else:
            flash('Artist '+ request.form['name']+ ' was successfully listed!')
        # on successful db insert, flash success
      
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        return render_template('pages/home.html')
  else: 
    for field, message in form.errors.items():
                 flash(field + ' - ' + str(message), 'danger')
                 return render_template('forms/new_artist.html', form=form)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
   shows = Show.query.all()

   data = []
   for show in shows:
        data.append({
            'venue_id': show.venue.id,
            'venue_name': show.venue.name,
            'artist_id': show.artist.id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': show.start_time.isoformat()
        })

   return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
      try:
        show = Show(
            artist_id=request.form['artist_id'],
            venue_id=request.form['venue_id'],
            start_time=request.form['start_time']
        )
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
      except:
         db.session.rollback()
         flash('An error occurred. Show could not be added')
        
      finally:
         db.session.close()
      return render_template('pages/home.html')

       
  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
       

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
'''if __name__ == '__main__':
    app.run()
'''

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''


