from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://rachelleondiege:@localhost:5432/example'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Person(db.Model):
    # by default sqlachemy would call this table person (lowercase version of class name)
    __tablename__ = 'persons'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f'<Person ID: {self.id}, name {self.name}>'
# Creates database tables from class if none exist
db.create_all()

@app.route('/')
def index():
  person = Person.query.first()
  return 'Hello ' + person.name + '!'
