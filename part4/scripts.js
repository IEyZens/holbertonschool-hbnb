document.addEventListener('DOMContentLoaded', () => {
  const API_BASE_URL = 'http://localhost:5000/api/v1';

  function getCookie(name) {
    const cookieArr = document.cookie.split(';');
    for (let cookie of cookieArr) {
      const [key, value] = cookie.trim().split('=');
      if (key === name) return value;
    }
    return null;
  }

  function getPlaceIdFromURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get('id');
  }

  function authHeaders(token) {
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    };
  }

  // Loader show/hide
  function showLoader() {
    const loader = document.getElementById('loader');
    if (loader) loader.style.display = 'block';
  }

  function hideLoader() {
    const loader = document.getElementById('loader');
    if (loader) loader.style.display = 'none';
  }

  // Show error message visibly or alert fallback
  function showError(message) {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
      errorDiv.textContent = message;
    } else {
      alert(message);
    }
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
        showLoader();
        const response = await fetch(`${API_BASE_URL}/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });
        hideLoader();

        if (response.ok) {
          const data = await response.json();
          document.cookie = `token=${data.access_token}; path=/`;
          window.location.href = 'index.html';
        } else {
          const err = await response.json();
          alert(`Login failed: ${err.message || response.statusText}`);
        }
      } catch (error) {
        hideLoader();
        alert('Network error: ' + error.message);
      }
    });
  }

  // ---------- TÂCHE 2 : INDEX ----------
  const placesList = document.getElementById('places-list');
  const priceFilter = document.getElementById('price-filter');
  const loginLink = document.getElementById('login-link');

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
        showLoader();
        const response = await fetch(`${API_BASE_URL}/places`, {
          headers: authHeaders(token)
        });
        hideLoader();

        if (response.ok) {
          const data = await response.json();
          displayPlaces(data);
        } else {
          showError('Failed to fetch places: ' + response.statusText);
        }
      } catch (err) {
        hideLoader();
        showError('Error fetching places: ' + err.message);
      }
    }

    function displayPlaces(places) {
      placesList.innerHTML = '';

      if (places.length === 0) {
        placesList.innerHTML = '<p class="empty-message">No places found.</p>';
        return;
      }

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
          card.style.opacity = '1';
          card.style.pointerEvents = 'auto';
          card.style.transition = 'opacity 0.3s ease';
        } else {
          card.style.opacity = '0';
          card.style.pointerEvents = 'none';
          card.style.transition = 'opacity 0.3s ease';
        }
      });

      const visibleCards = Array.from(cards).filter(card => card.style.opacity === '1');
      if (visibleCards.length === 0) {
        placesList.innerHTML = '<p class="empty-message">No places found for this price filter.</p>';
      } else {
        const errorDiv = document.getElementById('error-message');
        if (errorDiv) errorDiv.textContent = '';
      }
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
        showLoader();
        const response = await fetch(`${API_BASE_URL}/places/${placeId}`, {
          headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });
        hideLoader();

        if (response.ok) {
          const place = await response.json();
          displayPlaceDetails(place);
        } else {
          placeDetails.innerHTML = '<p>Failed to load place details.</p>';
        }
      } catch (error) {
        hideLoader();
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
    }

    fetchPlaceDetails(placeId, token);
  }

  // ---------- TÂCHE 4 : ADD REVIEW ----------
  const reviewForm = document.getElementById('review-form');
  const reviewInput = document.getElementById('review');
  const ratingSelect = document.getElementById('rating');

  function appendReview(review) {
    const reviewsSection = document.getElementById('reviews');
    if (!reviewsSection) return;

    const card = document.createElement('div');
    card.className = 'review-card';
    card.innerHTML = `
      <p><strong>${review.user_name}:</strong> ${review.text}</p>
      <p>Rating: ${review.rating}/5</p>
    `;
    reviewsSection.appendChild(card);
  }

  if (reviewForm && reviewInput && ratingSelect) {
    const token = getCookie('token');
    const placeId = getPlaceIdFromURL();

    if (!token) {
      window.location.href = 'index.html';
      return;
    }

    if (!placeId) {
      alert('Missing place ID.');
      return;
    }

    reviewForm.addEventListener('submit', async (event) => {
      event.preventDefault();

      const submitButton = reviewForm.querySelector('button[type="submit"]');
      submitButton.disabled = true;

      const reviewText = reviewInput.value.trim();
      const rating = parseInt(ratingSelect.value, 10);

      if (!reviewText || !rating || rating < 1 || rating > 5) {
        alert('Please fill in both review and select a valid rating (1 to 5).');
        submitButton.disabled = false;
        return;
      }

      try {
        showLoader();
        const response = await fetch(`${API_BASE_URL}/reviews`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            place_id: placeId,
            text: reviewText,
            rating: rating
          })
        });
        hideLoader();

        if (response.ok) {
          const newReview = await response.json();
          alert('Review submitted successfully!');
          reviewForm.reset();
          appendReview(newReview);
        } else {
          const err = await response.json();
          alert(`Failed to submit review: ${err.message || response.statusText}`);
        }
      } catch (error) {
        hideLoader();
        alert('Network error: ' + error.message);
      } finally {
        submitButton.disabled = false;
      }
    });
  }
});
