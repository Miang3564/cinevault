from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Your TMDB Read Access Token (Bearer Token)
TMDB_BEARER_TOKEN = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI0ZGIzM2U4NWMxNDg1ODk0ZmVlYTA1NTUyOTNmM2VlOCIsIm5iZiI6MTc5NDgwODE5NC4wMzUsInN1YiI6IjZhZmE5OTgyZDgzNzUyMjE1YjZkMDlmZiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.x0ZHKTZZ9NHYuWb4Ie6rDPrqK7xnSvISHCdfTyWqtFs'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search_movie():
    raw_query = request.form.get('movie_name') or request.args.get('movie_name', '')
    query_lower = raw_query.lower().strip()
    
    # Smart Category Mapping
    if 'bollywood' in query_lower:
        search_queries = ['Pathaan', 'Jawan', 'Animal', 'Stree 2', 'Dangal', '3 Idiots', 'Tiger 3', 'Gadar 2']
    elif 'hollywood' in query_lower:
        search_queries = ['Inception', 'Avatar', 'Interstellar', 'The Dark Knight', 'Oppenheimer', 'Gladiator II', 'Deadpool']
    elif 'tollywood' in query_lower or 'south' in query_lower:
        search_queries = ['K.G.F', 'Pushpa', 'RRR', 'Salaar', 'Baahubali', 'Devara']
    elif 'dubbed' in query_lower or 'hindi' in query_lower:
        search_queries = ['Avengers', 'Spider-Man', 'John Wick', 'Fast X', 'Aquaman']
    elif 'web series' in query_lower or 'series' in query_lower:
        search_queries = ['Mirzapur', 'Sacred Games', 'The Family Man', 'Asur', 'Panchayat', 'Stranger Things']
    else:
        search_queries = [raw_query] if raw_query else ['Trending']
        
    movies = []
    seen_ids = set()
    
    if TMDB_BEARER_TOKEN:
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {TMDB_BEARER_TOKEN}"
        }
        
        for q in search_queries:
            if not q:
                continue
            url = "https://api.themoviedb.org/3/search/movie"
            params = {'query': q}
            
            try:
                response = requests.get(url, headers=headers, params=params)
                data = response.json()
                for item in data.get('results', []):
                    movie_id = item.get('id')
                    if movie_id not in seen_ids:
                        seen_ids.add(movie_id)
                        movie_title = item.get('title', '')
                        poster_path = item.get('poster_path')
                        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
                        
                        formatted_title_for_yt = movie_title.replace(' ', '+')
                        trailer_url = f"https://www.youtube.com/results?search_query={formatted_title_for_yt}+official+trailer"
                        
                        movies.append({
                            'id': movie_id,
                            'title': movie_title,
                            'overview': item.get('overview'),
                            'release_date': item.get('release_date', 'N/A'),
                            'vote_average': item.get('vote_average', 'N/A'),
                            'poster': poster_url,
                            'trailer': trailer_url
                        })
            except Exception as e:
                print(f"Error occurred: {e}")

    return render_template('results.html', movie=raw_query, movies=movies)

@app.route('/watch/<int:movie_id>')
def watch_movie(movie_id):
    return render_template('player.html', movie_id=movie_id)

if __name__ == '__main__':
    app.run(debug=True)