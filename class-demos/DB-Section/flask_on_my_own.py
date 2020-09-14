from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://rachelleondiege:@localhost:5432/example'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f'<User ID: {self.id}, Name: {self.name}>'

db.create_all()

@app.route('/')
def index():
  user = User.query.first()


  one = User.query.filter(User.name == 'jesse').all()
  two = User.query.filter(User.name.like('%a%')).all()
  three =  User.query.limit(2).all()
  four = User.query.filter(User.name.ilike('%e%'))
  five = User.query.filter(User.name == 'bob').count()

  return 'Hello ' + user.name + '!'
  # + '\n1: ' + one +'\n2: ' + two +'\n3: ' + three + '\n4: ' + four + '\n5: ' + five
