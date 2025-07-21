/*
  This is a SAMPLE FILE to get you started.
  Please, follow the project instructions to complete the tasks.
*/

document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('login-form');
  const placeId = getPlaceIdFromURL();
  const token = checkAuthentication(placeId);
  const reviewForm = document.getElementById('review-form');

  if (loginForm) {
    loginForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      loginUser(email, password);
    });
  }

  if (reviewForm) {
    reviewForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const reviewText = document.getElementById('review').value;
      const rating = document.getElementById('rating').value;

      if (rating === "select") {
        alert("Please select a valid rating");
        return;
      }

      await submitReview(token, placeId, reviewText, rating);
      await fetchReviews(placeId, token);
    });
  }

  fetchPlaces(getCookie('token'));
});

async function loginUser(email, password) {
  const response = await fetch('http://localhost:5000/api/v1/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
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
  if (parts.length === 2) {
    return parts.pop().split(';').shift();
  }
}

function checkAuthentication(placeId) {
  const token = getCookie('token');
  const addReviewSection = document.getElementById('add-review');

  if (!token) {
    if (addReviewSection) {
      addReviewSection.style.display = 'none';
      window.location.href = 'index.html';
    }
  } else {
    if (addReviewSection) {
      addReviewSection.style.display = 'block';
    }
  }

  return token;
}

async function fetchPlaces(token = null) {
  const response = await fetch('http://localhost:5000/api/v1/places/', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` })
    }
  });

  if (response.ok) {
    const places = await response.json();
    displayPlaces(places);
  } else {
    console.error('Failed to fetch places:', response.statusText);
  }
}

async function fetchPlaceDetails(token, placeId) {
  const response = await fetch(`http://localhost:5000/api/v1/places/${placeId}/`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` })
    }
  });

  if (response.ok) {
    const place = await response.json();
    displayPlaceDetails(place);
    await fetchReviews(placeId, token);
  } else {
    console.error('Failed to fetch place details:', response.statusText);
  }
}

function displayPlaces(places) {
  const placesList = document.getElementById('places-list');
  placesList.innerHTML = '';

  places.forEach(place => {
    const placeCard = document.createElement('div');
    placeCard.classList.add('place-card');
    placeCard.setAttribute('data-price', place.price);

    placeCard.innerHTML = `
      <h3>${place.title}</h3>
      <p>Price per night: $${place.price}</p>
      <button class="details-button">View Details</button>
    `;

    placesList.appendChild(placeCard);
  });
}

function displayPlaceDetails(place) {
  const container = document.getElementById('place-details');
  container.innerHTML = '';

  const name = document.createElement('h2');
  name.textContent = place.title;

  const description = document.createElement('p');
  description.textContent = place.description;

  const price = document.createElement('p');
  price.textContent = `Price per night: $${place.price}`;

  const amenities = document.createElement('ul');
  place.amenities.forEach(am => {
    const li = document.createElement('li');
    li.textContent = am.name;
    amenities.appendChild(li);
  });

  const reviews = document.getElementById('reviews');
  reviews.innerHTML = '';
  if (place.reviews && place.reviews.length > 0) {
    place.reviews.forEach(review => {
      const reviewCard = document.createElement('div');
      reviewCard.classList.add('review-card');
      reviewCard.innerHTML = `
        <p>${review.comment}</p>
        <p>User: ${review.user_name}</p>
        <p>Rating: ${review.rating}</p>
      `;
      reviews.appendChild(reviewCard);
    });
  }

  container.appendChild(name);
  container.appendChild(description);
  container.appendChild(price);
  container.appendChild(amenities);
}

document.getElementById('price-filter').addEventListener('change', (event) => {
  const maxPrice = event.target.value;
  const cards = document.querySelectorAll('.place-card');

  cards.forEach(card => {
    const price = parseFloat(card.getAttribute('data-price'));
    if (maxPrice === 'All' || price <= parseFloat(maxPrice)) {
      card.style.display = 'block';
    } else {
      card.style.display = 'none';
    }
  })
});

function getPlaceIdFromURL() {
  const params = new URLSearchParams(window.location.search);
  return params.get('id');
}

async function submitReview(token, placeId, reviewText, rating) {
  const response = await fetch('http://localhost:5000/api/v1/reviews/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({
      place_id: placeId,
      comment: reviewText,
      rating: rating
    })
  });

  handleResponse(response);
}

async function handleResponse(response) {
  if (response.ok) {
    alert('Review submitted successfully!');
    document.getElementById('review-form').reset();
  } else {
    const error = await response.json();
    alert('Failed to submit review: ' + (error.message || response.statusText));
  }
}

async function fetchReviews(placeId, token) {
  try {
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(`http://localhost:5000/api/v1/places/${placeId}/reviews`, { headers });
    if (!res.ok) throw new Error('Failed to fetch reviews');

    const reviews = await res.json();
    displayReviews(reviews);
  } catch (error) {
    console.error(error);
    alert('Error loading reviews.');
  }
}

function displayReviews(reviews) {
  const reviewsContainer = document.getElementById('reviews');
  reviewsContainer.innerHTML = '';

  if (!reviews || reviews.length === 0) {
    reviewsContainer.textContent = 'No reviews yet.';
    return;
  }

  reviews.forEach(review => {
    const reviewCard = document.createElement('div');
    reviewCard.classList.add('review-card');

    const stars = '⭐'.repeat(review.rating || 0);

    reviewCard.innerHTML = `
      <p>${review.comment || ''}</p>
      <p><strong>User:</strong> ${review.user_name || 'Anonymous'}</p>
      <p><strong>Rating:</strong> ${stars}</p>
    `;

    reviewsContainer.appendChild(reviewCard);
  });
}
