/*
  This is a SAMPLE FILE to get you started.
  Please, follow the project instructions to complete the tasks.
*/

let allPlaces = [];

document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('login-form');
  const priceFilter = document.getElementById('price-filter');
  const isPlacePage = document.getElementById('place-details');
  const reviewForm = document.getElementById('review-form');
  const logoutLink = document.getElementById('logout-link');

  if (loginForm) {
    loginForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      loginUser(email, password);
    });
  }

  if (priceFilter) {
    priceFilter.addEventListener('change', (event) => {
      const selectedValue = event.target.value;

      if (selectedValue === 'All') {
        displayPlaces(allPlaces);
      } else {
        const maxPrice = parseInt(selectedValue);
        const filtered = allPlaces.filter(place => place.price <= maxPrice);
        displayPlaces(filtered);
      }
    });

    ['All', 10, 50, 100].forEach(value => {
      const option = document.createElement('option');
      option.value = value === 'All' ? 'All' : value;
      option.textContent = value === 'All' ? 'All' : `$${value}`;
      priceFilter.appendChild(option);
    });
  }

  if (isPlacePage) {
    const token = getCookie('token');
    const addReviewSection = document.getElementById('add-review');
    const placeId = getPlaceIdFromURL();

    if (!placeId) {
      console.error("❌ Aucun ID de place dans l'URL.");
      return;
    }

    if (!token) {
      if (addReviewSection) {
        addReviewSection.style.display = 'none';
      }
    } else {
      if (addReviewSection) {
        addReviewSection.style.display = 'block';
        fetchPlaceDetails(token, placeId);
      }
    }
  }
  if (reviewForm) {
    reviewForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const token = getCookie('token');
      const placeId = getPlaceIdFromURL();
      if (!token || !placeId) return;
      try {
        await postReview(token, placeId);
      } catch (err) {
        console.error('❌ Erreur lors de l’ajout de la review:', err);
      }
    });
  }

  if (logoutLink) {
    logoutLink.addEventListener('click', () => {
      document.cookie = 'token=; Max-Age=0; path=/';
      window.location.href = 'index.html';
    });
  }

  checkAuthentication();
});

async function loginUser(email, password) {
  const response = await fetch('http://127.0.0.1:5000/api/v1/auth/login', {
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

function checkAuthentication() {
  const token = getCookie('token');
  const loginLink = document.getElementById('login-link');
  const logoutLink = document.getElementById('logout-link');

  if (loginLink) {
    if (!token) {
      loginLink.style.display = 'block';
      if (logoutLink) {
        logoutLink.style.display = 'none';
      }
    } else {
      loginLink.style.display = 'none';
      if (logoutLink) {
        logoutLink.style.display = 'block'
      }
      fetchPlaces(token);
    }
  } else {
    if (token) {
      fetchPlaces(token);
    }
  }
}

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    return parts.pop().split(';').shift()
  }
}

async function fetchPlaces(token) {
  const response = await fetch('http://127.0.0.1:5000/api/v1/places/', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + token
    },
  });

  if (response.ok) {
    const data = await response.json();
    console.log('Fetched places:', data);
    allPlaces = data;
    displayPlaces(allPlaces);
  } else {
    alert('Fetch failed: ' + response.statusText);
  }
}

function displayPlaces(places) {
  console.log('✅ displayPlaces appelée avec :', places);
  const placesList = document.getElementById('places-list');
  const reviewForm = document.getElementById('review-form');

  if (!placesList) {
    return;
  }
  console.log('📌 placesList trouvé ?', placesList);
  placesList.innerHTML = '';

  if (reviewForm) {
    reviewForm.addEventListener('submit', async (event) => {
      event.preventDefault(); // ⛔ Empêche la redirection
      const reviewText = document.getElementById('review-text').value;
      const rating = parseInt(document.getElementById('review-rating').value);
      const token = getCookie('token');
      const placeId = getPlaceIdFromURL();

      if (!token || !placeId) return;

      await postReview(token, placeId, reviewText, rating);
      await fetchPlaceDetails(token, placeId); // Rafraîchir les reviews
    });
  }

  places.forEach(element => {
    const card = document.createElement('div');
    const name = document.createElement('h3');
    const price = document.createElement('p');
    const details = document.createElement('button');

    card.classList.add('place-card');
    name.textContent = element.title;
    price.textContent = `Price: $${element.price}`;

    details.classList.add('details-button');
    details.textContent = 'View Details';
    details.addEventListener('click', () => {
      window.location.href = `place.html?id=${element.id}`;
    })

    card.appendChild(name);
    card.appendChild(price);
    card.appendChild(details);

    placesList.appendChild(card);
    console.log('➡️ ajout du lieu :', element.title);
  });
}

function getPlaceIdFromURL() {
  const params = new URLSearchParams(window.location.search);
  return params.get('id');
}

async function fetchPlaceDetails(token, placeId) {
  try {
    const response = await fetch(`http://127.0.0.1:5000/api/v1/places/${placeId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      }
    });

    if (response.ok) {
      const place = await response.json();

      console.log('📦 place:', place);

      displayPlaceDetails(place);
    } else {
      alert('Failed to fetch place details: ' + response.statusText);
    }
  } catch (error) {
    console.error('Error: ', error);
    alert('An error occured while fetching place details.');
  }
}

function displayPlaceDetails(place) {
  const detailsSection = document.getElementById('place-info');
  detailsSection.innerHTML = '';

  const name = document.createElement('h3');
  name.textContent = place.title;

  const price = document.createElement('p');
  price.textContent = `Price per night: $${place.price}`;

  const description = document.createElement('p');
  description.textContent = place.description;

  const amenities = document.createElement('ul');
  amenities.textContent = 'Amenities:';
  if (Array.isArray(place.amenities)) {
    place.amenities.forEach(item => {
      const li = document.createElement('li');
      li.textContent = item.name;
      amenities.appendChild(li);
    });
  }

  detailsSection.appendChild(name);
  detailsSection.appendChild(price);
  detailsSection.appendChild(description);
  detailsSection.appendChild(amenities);

  const reviewsSection = document.getElementById('reviews');
  reviewsSection.innerHTML = '';

  if (place.reviews && place.reviews.length > 0) {
    place.reviews.forEach(review => {
      const reviewCard = document.createElement('div');
      reviewCard.classList.add('review-card');

      const user = document.createElement('h4');
      user.textContent = review.user
        ? `User: ${review.user.first_name} ${review.user.last_name}`
        : `User: Unknown`;

      const rating = document.createElement('p');
      rating.textContent = 'Rating: ' + '⭐'.repeat(review.rating);

      const comment = document.createElement('p');
      comment.textContent = review.text;

      reviewCard.appendChild(user);
      reviewCard.appendChild(rating);
      reviewCard.appendChild(comment);

      reviewsSection.appendChild(reviewCard);
    });
  }
}

function updateURLParameter(param, value) {
  const url = new URL(window.location.href);
  url.searchParams.set(param, value);
  window.history.replaceState({}, '', url);
}

async function postReview(token, placeId) {
  const reviewText = document.getElementById('review-text').value;
  const ratingValue = parseInt(document.getElementById('review-rating').value);

  const response = await fetch('http://127.0.0.1:5000/api/v1/reviews/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + token
    },
    body: JSON.stringify({
      text: reviewText,
      rating: ratingValue,
      place_id: placeId
    })
  });

  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.error || 'Erreur inconnue');
  }

  const newReview = await response.json();
  console.log('✅ Review ajoutée :', newReview);

  document.getElementById('review-text').value = '';
  document.getElementById('review-rating').value = '5'; // reset rating

  addReviewToDOM(newReview);
}

function addReviewToDOM(review) {
  const reviewsSection = document.getElementById('reviews');
  const reviewCard = document.createElement('div');
  reviewCard.classList.add('review-card');

  const user = document.createElement('h4');
  user.textContent = review.user
    ? `User: ${review.user.first_name} ${review.user.last_name}`
    : `User: Unknown`;

  const rating = document.createElement('p');
  rating.textContent = 'Rating: ' + '⭐'.repeat(review.rating);

  const comment = document.createElement('p');
  comment.textContent = review.text;

  reviewCard.appendChild(user);
  reviewCard.appendChild(rating);
  reviewCard.appendChild(comment);

  reviewsSection.appendChild(reviewCard);
}
