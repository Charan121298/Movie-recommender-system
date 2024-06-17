from flask import render_template, request, jsonify
from app import app 
from app.model import  find_similar_movies

def create_movie_json(movie_titles):
    movies_list = [
        {"title": title, "poster":f"https://via.placeholder.com/250x375?text={title}" }
        for title in movie_titles
    ]
    return movies_list

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    # Get the movie name from the POST request
    movie_name = request.form.get('movie_name')

    # Call the find_similar_movies function
    titles = find_similar_movies(movie_name)

    # Create JSON response
    recommendation = create_movie_json(titles)

    return jsonify(recommendation)

if __name__ == '__main__':
    app.run(debug=True)