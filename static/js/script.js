document.addEventListener('DOMContentLoaded', function () {
    const movieInput = document.getElementById('movieInput');
    const recommendationsDiv = document.getElementById('recommendations');

    function getRecommendations() {
        const movieName = movieInput.value.trim();
        if (!movieName) {
            recommendationsDiv.innerHTML = "Please enter a movie name !"
            return;
        }
        console.log(`Fetching recommendations for: ${movieName}`);

        // Send POST request to Flask backend
        fetch('/recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `movie_name=${encodeURIComponent(movieName)}`
        })
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Received data:', data);
            if (!Array.isArray(data)) {
                console.error('Expected an array but received:', data);
                throw new TypeError('Expected an array but received something else');
            }
            recommendationsDiv.innerHTML = '';  // Clear previous recommendations
            data.forEach(movie => {
                const movieDiv = document.createElement('div');
                movieDiv.classList.add('movie');

                const img = document.createElement('img');
                img.src = movie.poster;
                img.alt = movie.title;

                const title = document.createElement('div');
                title.classList.add('movie-title');
                title.textContent = movie.title;

                movieDiv.appendChild(img);
                movieDiv.appendChild(title);

                recommendationsDiv.appendChild(movieDiv);
            });
        })
        .catch(error => {
            console.error('Error fetching recommendations:', error);
            recommendationsDiv.innerHTML = 'An error occurred while fetching recommendations.';
        });
    }

    // Attach event listener to the button
    const getRecommendationsBtn = document.getElementById('getRecommendationsBtn');
    getRecommendationsBtn.addEventListener('click', getRecommendations);
});
