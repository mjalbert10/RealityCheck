import json
import os
from dotenv import load_dotenv
from flask import Flask

load_dotenv()
from flask_cors import CORS
from models import db, Episode, Review
from routes import register_routes

# src/ directory and project root (one level up)
current_directory = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_directory)

# Serve React build files from <project_root>/frontend/dist
app = Flask(__name__,
    static_folder=os.path.join(project_root, 'frontend', 'dist'),
    static_url_path='')
CORS(app)

# Configure SQLite database - using 3 slashes for relative path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database with app
db.init_app(app)

# Register routes
register_routes(app)

# Function to initialize database, change this to your own database initialization logic
def init_db():
    with app.app_context():
        db.create_all()
        
        if Episode.query.count() == 0:
            json_file_path = os.path.join(current_directory, 'init.json')
            with open(json_file_path, 'r') as file:
                data = json.load(file)
                
                for show in data:  # flat array, no key needed
                    episode = Episode(
                        id=show['id'],
                        title=show['name'],        # TMDB uses 'name'
                        descr=show['overview']     # TMDB uses 'overview'
                    )
                    db.session.add(episode)
                    
                    review = Review(
                        id=show['id'],
                        imdb_rating=show['vote_average']  # TMDB uses 'vote_average'
                    )
                    db.session.add(review)
            
            db.session.commit()
            print("Database initialized with reality show data")

init_db()

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)
