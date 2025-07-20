document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('login-form');
  const priceFilter = document.getElementById('price-filter');
  const placeId = getPlaceIdFromURL();
  const reviewForm = document.getElementById('review-form');

  if (loginForm) {
    loginForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      await loginUser(email, password);
    });
  }

  if (priceFilter) {
    loadPriceFilterOptions();
    priceFilter.addEventListener('change', (event) => {
      const selectedPrice = event.target.value;
      const placeCards = document.querySelectorAll('.place-card');
      placeCards.forEach(card => {
        const price = parseInt(card.dataset.price, 10);
        card.style.display = (selectedPrice === 'All' || price <= parseInt(selectedPrice, 10)) ? 'block' : 'none';
      });
    });
  }

  if (placeId && !reviewForm) {
    checkPlaceAuthentication(placeId);
  }

  if (!placeId && !reviewForm) {
    checkAuthentication();
  }

  if (reviewForm) {
    const token = checkReviewAuthentication();
    reviewForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const reviewText = document.getElementById('review').value;
      const rating = document.getElementById('rating').value;
      await submitReview(token, placeId, reviewText, rating);
    });
  }
});

async function loginUser(email, password) {
  const response = await fetch('https://your-api-url/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  if (response.ok) {
    const data = await response.json();
    document.cookie = `token=${data.access_token}; path=/`;
    window.location.href = 'index.html';
  } else {
    alert('Login failed: ' + response.statusText);
  }
}

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

function checkAuthentication() {
  const token = getCookie('token');
  const loginLink = document.getElementById('login-link');
  if (!token) {
    if (loginLink) loginLink.style.display = 'block';
  } else {
    if (loginLink) loginLink.style.display = 'none';
    fetchPlaces(token);
  }
}

function checkPlaceAuthentication(placeId) {
  const token = getCookie('token');
  const addReviewSection = document.getElementById('add-review');
  if (addReviewSection) {
    addReviewSection.style.display = token ? 'block' : 'none';
  }
  fetchPlaceDetails(token, placeId);
}

function checkReviewAuthentication() {
  const token = getCookie('token');
  if (!token) {
    window.location.href = 'index.html';
  }
  return token;
}

async function fetchPlaces(token) {
  const response = await fetch('https://your-api-url/places', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (response.ok) {
    const places = await response.json();
    displayPlaces(places);
  } else {
    console.error('Failed to fetch places');
  }
}

function displayPlaces(places) {
  const placesList = document.getElementById('places-list');
  if (!placesList) return;
  placesList.innerHTML = '';
  places.forEach(place => {
    const card = document.createElement('div');
    card.className = 'place-card';
    card.dataset.price = place.price_per_night;
    card.innerHTML = `
      <h3>${place.name}</h3>
      <p>${place.description}</p>
      <p>Price per night: $${place.price_per_night}</p>
      <button class="details-button">View Details</button>
    `;
    placesList.appendChild(card);
  });
}

function loadPriceFilterOptions() {
  const filter = document.getElementById('price-filter');
  if (!filter) return;
  ['10', '50', '100', 'All'].forEach(value => {
    const option = document.createElement('option');
    option.value = value;
    option.textContent = value;
    filter.appendChild(option);
  });
}

function getPlaceIdFromURL() {
  const params = new URLSearchParams(window.location.search);
  return params.get('id');
}

async function fetchPlaceDetails(token, placeId) {
  const response = await fetch(`https://your-api-url/places/${placeId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (response.ok) {
    const place = await response.json();
    displayPlaceDetails(place);
  } else {
    console.error('Failed to fetch place details');
  }
}

function displayPlaceDetails(place) {
  const section = document.getElementById('place-details');
  if (!section) return;
  section.innerHTML = '';
  const content = document.createElement('div');
  content.className = 'place-info';
  content.innerHTML = `
    <h2>${place.name}</h2>
    <p>${place.description}</p>
    <p><strong>Price:</strong> $${place.price_per_night}</p>
    <p><strong>Amenities:</strong> ${place.amenities.join(', ')}</p>
    <h3>Reviews:</h3>
  `;
  place.reviews.forEach(review => {
    const reviewCard = document.createElement('div');
    reviewCard.className = 'review-card';
    reviewCard.innerHTML = `
      <p><strong>${review.user_name}</strong> (${review.rating}/5)</p>
      <p>${review.comment}</p>
    `;
    content.appendChild(reviewCard);
  });
  section.appendChild(content);
}

async function submitReview(token, placeId, reviewText, rating) {
  const response = await fetch(`https://your-api-url/places/${placeId}/reviews`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      comment: reviewText,
      rating: parseInt(rating, 10)
    })
  });
  if (response.ok) {
    alert('Review submitted successfully!');
    document.getElementById('review-form').reset();
  } else {
    alert('Failed to submit review');
  }
}
