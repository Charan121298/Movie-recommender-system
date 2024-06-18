import numpy as np
import os
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import process
from sklearn.decomposition import TruncatedSVD
from sklearn.neighbors import NearestNeighbors

def find_similar_movies(title_name, k=10):
    # Read data
    current_dir = os.path.dirname(__file__)
    
    ratingsPath = os.path.join(current_dir, 'dataset', 'ratings.csv')
    moviesPath = os.path.join(current_dir, 'dataset', 'movies.csv')
    
    ratings = pd.read_csv(ratingsPath)
    movies = pd.read_csv(moviesPath)

    # Compute statistics
    movie_stats = ratings.groupby('movieId')['rating'].agg(['count', 'mean'])
    c = movie_stats['count'].mean()
    m = movie_stats['mean'].mean()

    def bayesian_avg(ratings):
        bayesian_avg = (c * m + ratings.sum()) / (c + ratings.count())
        return round(bayesian_avg, 3)

    movies['genres'] = movies['genres'].apply(lambda x: x.split("|"))

    # Create a sparse matrix
    def create_matrix(df):
        n_users = df["userId"].nunique()
        n_movies = df["movieId"].nunique()

        user_mapper = dict(zip(np.unique(df["userId"]), list(range(n_users))))
        movie_mapper = dict(zip(np.unique(df["movieId"]), list(range(n_movies))))
        inv_user_mapper = dict(zip(list(range(n_users)), np.unique(df["userId"])))
        inv_movie_mapper = dict(zip(list(range(n_movies)), np.unique(df["movieId"])))

        user_index = [user_mapper[i] for i in df["userId"]]
        movie_index = [movie_mapper[i] for i in df["movieId"]]

        Matrix = csr_matrix((df["rating"], (user_index, movie_index)), shape=(n_users, n_movies))

        return Matrix, user_mapper, movie_mapper, inv_user_mapper, inv_movie_mapper

    Matrix, user_mapper, movie_mapper, inv_user_mapper, inv_movie_mapper = create_matrix(ratings)

    # Find similar neighbors
    def find_neighbors(movie_id, Matrix, movie_mapper, inv_movie_mapper, k, metric="cosine"):
        Matrix = Matrix.T
        neighborsID = []

        movieInd = movie_mapper[movie_id]
        movieVec = Matrix[movieInd]

        if isinstance(movieVec, (np.ndarray)):
            movieVec = movieVec.reshape(1, -1)

        KNN = NearestNeighbors(n_neighbors=k + 1, algorithm="brute", metric=metric)
        KNN.fit(Matrix)

        neighbors = KNN.kneighbors(movieVec, return_distance=False)

        # Skip the first neighbor if it's the same movie
        for i in range(1, k + 1):
            n = neighbors[0, i]
            neighborsID.append(inv_movie_mapper[n])

        return neighborsID

    # One-hot encoding genres
    genres = set(g for G in movies["genres"] for g in G)

    for g in genres:
        movies[g] = movies.genres.transform(lambda x: int(g in x))

    movieGenres = movies.drop(columns=["movieId", "title", "genres"])

    cosineSim = cosine_similarity(movieGenres, movieGenres)

    # FuzzyWuzzy finder function
    def finder(titleName):
        allTitles = movies["title"].tolist()
        title = process.extractOne(titleName, allTitles)[0]
        movieIds = dict(zip(movies["title"], list(movies["movieId"])))
        movieId = movieIds[title]
        return movieId

    # SVD for dimensionality reduction
    SVD = TruncatedSVD(n_components=20, n_iter=10)
    Q = SVD.fit_transform(Matrix.T)

    # Mapping movie IDs to titles
    movieTitles = dict(zip(movies["movieId"], movies["title"]))

    # Initialize variables
    suggestions = []
    movieTitle = None
    movieId = None

    try:
        movieId = finder(title_name)
        similarMovies = find_neighbors(movieId, Q.T, movie_mapper, inv_movie_mapper, metric="cosine", k=k)
        movieTitle = movieTitles[movieId]
        for i in similarMovies:
            suggestions.append(movieTitles[i])
    except KeyError as e:
        print("KeyError")
        # Handle exception (e.g., return error message)
    except IndexError as e:
        print("IndexError")
        # Handle exception (e.g., return error message)
    except Exception as e:
        print("ExceptionError")
        # Handle exception (e.g., return error message)
    return suggestions
print(find_similar_movies("Jumnamji"))