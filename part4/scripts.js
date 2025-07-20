document.addEventListener('DOMContentLoaded', () => {
  // Utilitaire : récupère un cookie par nom
  function getCookie(name) {
    const cookieArr = document.cookie.split(';');
    for (let cookie of cookieArr) {
      const [key, value] = cookie.trim().split('=');
      if (key === name) return value;
    }
    return null;
  }

  // Utilitaire : récupère le place_id depuis l’URL
  function getPlaceIdFromURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get('id');
  }

  // ---------- TÂCHE 1 : LOGIN ----------
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async (event) => {
      event.preventDefault();

      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value.trim();

      if (!email || !password) {
        alert('Please enter both email and password.');
        return;
      }

      try {
        const response = await fetch('http://localhost:5000/api/v1/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });

        if (response.ok) {
          const data = await response.json();
          document.cookie = `token=${data.access_token}; path=/`;
          window.location.href = 'index.html';
        } else {
          const err = await response.json();
          alert(`Login failed: ${err.message || response.statusText}`);
        }
      } catch (error) {
        alert('Network error: ' + error.message);
      }
    });
  }

  // ---------- TÂCHE 2 : INDEX ----------
  const placesList = document.getElementById('places-list');
  const priceFilter = document.getElementById('price-filter');
  const loginLink = document.getElementById('login-link');
  let allPlaces = [];

  if (placesList && priceFilter) {
    const token = getCookie('token');
    if (!token) {
      if (loginLink) loginLink.style.display = 'block';
    } else {
      if (loginLink) loginLink.style.display = 'none';
      fetchPlaces(token);
    }

    async function fetchPlaces(token) {
      try {
        const response = await fetch('http://localhost:5000/api/v1/places', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
          const data = await response.json();
          allPlaces = data;
          displayPlaces(data);
        } else {
          console.error('Failed to fetch places:', response.statusText);
        }
      } catch (err) {
        console.error('Error fetching places:', err.message);
      }
    }

    function displayPlaces(places) {
      placesList.innerHTML = '';
      places.forEach(place => {
        const card = document.createElement('div');
        card.className = 'place-card';
        card.setAttribute('data-price', place.price_per_night);

        card.innerHTML = `
          <h3>${place.name}</h3>
          <p>Price: $${place.price_per_night}/night</p>
          <button class="details-button" onclick="window.location.href='place.html?id=${place.id}'">View Details</button>
        `;

        placesList.appendChild(card);
      });
    }

    priceFilter.addEventListener('change', (e) => {
      const selected = e.target.value;
      const cards = document.querySelectorAll('.place-card');
      cards.forEach(card => {
        const price = parseFloat(card.getAttribute('data-price'));
        if (selected === 'all' || price <= parseFloat(selected)) {
          card.style.display = 'block';
        } else {
          card.style.display = 'none';
        }
      });
    });
  }

  // ---------- TÂCHE 3 : PLACE DETAILS ----------
  const placeDetails = document.getElementById('place-details');
  const reviewsSection = document.getElementById('reviews');
  const addReviewSection = document.getElementById('add-review');

  if (placeDetails && reviewsSection) {
    const token = getCookie('token');
    const placeId = getPlaceIdFromURL();

    if (!placeId) {
      placeDetails.innerHTML = '<p>Missing place ID in URL.</p>';
      return;
    }

    if (addReviewSection) {
      addReviewSection.style.display = token ? 'block' : 'none';
    }

    async function fetchPlaceDetails(placeId, token) {
      try {
        const response = await fetch(`http://localhost:5000/api/v1/places/${placeId}`, {
          headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });
        if (response.ok) {
          const place = await response.json();
          displayPlaceDetails(place);
        } else {
          placeDetails.innerHTML = '<p>Failed to load place details.</p>';
        }
      } catch (error) {
        placeDetails.innerHTML = '<p>Error fetching place details.</p>';
      }
    }

    function displayPlaceDetails(place) {
      placeDetails.innerHTML = `
        <h2>${place.name}</h2>
        <div class="place-info">
          <p><strong>Host:</strong> ${place.owner_name || 'N/A'}</p>
          <p><strong>Price:</strong> $${place.price_per_night}/night</p>
          <p><strong>Description:</strong> ${place.description}</p>
          <p><strong>Amenities:</strong> ${place.amenities.join(', ')}</p>
        </div>
      `;

      reviewsSection.innerHTML = '';
      if (place.reviews && place.reviews.length > 0) {
        place.reviews.forEach(review => {
          const card = document.createElement('div');
          card.className = 'review-card';
          card.innerHTML = `
            <p><strong>${review.user_name}:</strong> ${review.text}</p>
            <p>Rating: ${review.rating}/5</p>
          `;
          reviewsSection.appendChild(card);
        });
      } else {
        reviewsSection.innerHTML = '<p>No reviews yet.</p>';
      }

      const placeName = document.getElementById('place-name');
      if (placeName) placeName.textContent = place.name;
    }

    fetchPlaceDetails(placeId, token);
  }

  // ---------- TÂCHE 4 : ADD REVIEW ----------
  const reviewForm = document.getElementById('review-form');
  const reviewInput = document.getElementById('review');
  const ratingSelect = document.getElementById('rating');

  if (reviewForm && reviewInput && ratingSelect) {
    const token = getCookie('token');
    const placeId = getPlaceIdFromURL();

    if (!token) {
      window.location.href = 'index.html';
      return;
    }

    reviewForm.addEventListener('submit', async (event) => {
      event.preventDefault();

      const reviewText = reviewInput.value.trim();
      const rating = ratingSelect.value;

      if (!reviewText || !rating) {
        alert('Please fill in both review and rating.');
        return;
      }

      try {
        const response = await fetch('http://localhost:5000/api/v1/reviews', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            place_id: placeId,
            text: reviewText,
            rating: parseInt(rating)
          })
        });

        if (response.ok) {
          alert('Review submitted successfully!');
          reviewForm.reset();
        } else {
          const err = await response.json();
          alert(`Failed to submit review: ${err.message || response.statusText}`);
        }
      } catch (error) {
        alert('Network error: ' + error.message);
      }
    });
  }
});
