// HBnB Project JavaScript - Complete functionality for all tasks
// Tasks 1-4: Login, Places List, Place Details, Add Review

// Configuration - Update this URL to match your API
const API_BASE_URL = 'http://localhost:5000/api/v1';

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Get a cookie value by name
 * @param {string} name - Cookie name
 * @returns {string|null} - Cookie value or null if not found
 */
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    return parts.pop().split(';').shift();
  }
  return null;
}

/**
 * Set a cookie
 * @param {string} name - Cookie name
 * @param {string} value - Cookie value
 * @param {number} days - Expiration in days
 */
function setCookie(name, value, days = 7) {
  const expires = new Date();
  expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
  document.cookie = `${name}=${value}; expires=${expires.toUTCString()}; path=/`;
}

/**
 * Delete a cookie
 * @param {string} name - Cookie name
 */
function deleteCookie(name) {
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
}

/**
 * Extract place ID from URL parameters
 * @returns {string|null} - Place ID or null
 */
function getPlaceIdFromURL() {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get('id');
}

/**
 * Show a message to the user
 * @param {string} elementId - ID of the message element
 * @param {string} message - Message to display
 * @param {boolean} isError - Whether it's an error message
 */
function showMessage(elementId, message, isError = false) {
  const element = document.getElementById(elementId);
  if (element) {
    element.textContent = message;
    element.style.color = isError ? 'red' : 'green';
    element.classList.remove('hidden');
    element.style.display = 'block';

    // Auto-hide after 5 seconds
    setTimeout(() => {
      element.classList.add('hidden');
      element.style.display = 'none';
    }, 5000);
  }
}

/**
 * Generate star rating display
 * @param {number} rating - Rating from 1-5
 * @returns {string} - Star string
 */
function generateStars(rating) {
  const fullStars = '★'.repeat(Math.floor(rating));
  const emptyStars = '☆'.repeat(5 - Math.floor(rating));
  return fullStars + emptyStars;
}

// =============================================================================
// TASK 1: AUTHENTICATION FUNCTIONS
// =============================================================================

/**
 * Login user via API
 * @param {string} email - User email
 * @param {string} password - User password
 */
async function loginUser(email, password) {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, password })
    });

    if (response.ok) {
      const data = await response.json();
      // Store JWT token in cookie
      setCookie('token', data.access_token);
      // Redirect to main page
      window.location.href = 'index.html';
    } else {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = errorData.message || 'Login failed. Please check your credentials.';
      showMessage('error-message', errorMessage, true);
    }
  } catch (error) {
    console.error('Login error:', error);
    showMessage('error-message', 'Network error. Please try again later.', true);
  }
}

/**
 * Check if user is authenticated and update UI accordingly
 * @returns {string|null} - JWT token or null
 */
function checkAuthentication() {
  const token = getCookie('token');
  const loginLink = document.getElementById('login-link');

  if (loginLink) {
    if (!token) {
      loginLink.style.display = 'block';
      loginLink.textContent = 'Login';
      loginLink.href = 'login.html';
      loginLink.onclick = null;
    } else {
      loginLink.style.display = 'block';
      loginLink.textContent = 'Logout';
      loginLink.href = '#';
      loginLink.onclick = (e) => {
        e.preventDefault();
        logout();
      };
    }
  }

  return token;
}

/**
 * Logout user
 */
function logout() {
  deleteCookie('token');
  window.location.href = 'index.html';
}

// =============================================================================
// TASK 2: PLACES LIST FUNCTIONS
// =============================================================================

/**
 * Fetch places from API
 * @param {string|null} token - JWT token for authentication
 */
async function fetchPlaces(token = null) {
  try {
    const headers = {
      'Content-Type': 'application/json'
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/places/`, {
      method: 'GET',
      headers: headers
    });

    if (response.ok) {
      const places = await response.json();
      displayPlaces(places);
    } else {
      console.error('Failed to fetch places:', response.statusText);
      const placesContainer = document.getElementById('places-container');
      if (placesContainer) {
        placesContainer.innerHTML = '<p>Failed to load places. Please try again later.</p>';
      }
    }
  } catch (error) {
    console.error('Error fetching places:', error);
    const placesContainer = document.getElementById('places-container');
    if (placesContainer) {
      placesContainer.innerHTML = '<p>Network error. Please check your connection.</p>';
    }
  }
}

/**
 * Display places in the DOM
 * @param {Array} places - Array of place objects
 */
function displayPlaces(places) {
  const placesContainer = document.getElementById('places-container');
  if (!placesContainer) return;

  placesContainer.innerHTML = '';

  if (!places || places.length === 0) {
    placesContainer.innerHTML = '<p>No places available at the moment.</p>';
    return;
  }

  places.forEach(place => {
    const placeCard = document.createElement('div');
    placeCard.className = 'place-card';
    placeCard.dataset.price = place.price_per_night || 0;

    placeCard.innerHTML = `
            <h3>${place.name || 'Unnamed Place'}</h3>
            <p>${place.description || 'No description available'}</p>
            <div class="price">$${place.price_per_night || 0}/night</div>
            <p><strong>Location:</strong> ${place.city || 'Unknown'}</p>
            <a href="place.html?id=${place.id}" class="details-button">View Details</a>
        `;

    placesContainer.appendChild(placeCard);
  });
}

/**
 * Load price filter options
 */
function loadPriceFilterOptions() {
  const priceFilter = document.getElementById('price-filter');
  if (!priceFilter) return;

  // Only load if not already loaded
  if (priceFilter.children.length <= 1) {
    const options = [
      { value: 'All', text: 'All prices' },
      { value: '10', text: 'Up to $10' },
      { value: '50', text: 'Up to $50' },
      { value: '100', text: 'Up to $100' }
    ];

    priceFilter.innerHTML = '';
    options.forEach(option => {
      const optionElement = document.createElement('option');
      optionElement.value = option.value;
      optionElement.textContent = option.text;
      priceFilter.appendChild(optionElement);
    });
  }
}

/**
 * Filter places by price (client-side)
 * @param {string} selectedPrice - Selected price filter value
 */
function filterPlacesByPrice(selectedPrice) {
  const placeCards = document.querySelectorAll('.place-card');

  placeCards.forEach(card => {
    const price = parseInt(card.dataset.price, 10) || 0;

    if (selectedPrice === 'All' || price <= parseInt(selectedPrice, 10)) {
      card.style.display = 'block';
    } else {
      card.style.display = 'none';
    }
  });
}

// =============================================================================
// TASK 3: PLACE DETAILS FUNCTIONS
// =============================================================================

/**
 * Fetch place details from API
 * @param {string} token - JWT token
 * @param {string} placeId - Place ID
 */
async function fetchPlaceDetails(token, placeId) {
  try {
    const headers = {
      'Content-Type': 'application/json'
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/places/${placeId}`, {
      method: 'GET',
      headers: headers
    });

    if (response.ok) {
      const place = await response.json();
      displayPlaceDetails(place);
      // Also fetch reviews for this place
      fetchPlaceReviews(token, placeId);
    } else {
      console.error('Failed to fetch place details:', response.statusText);
      document.getElementById('place-name').textContent = 'Failed to load place details';
    }
  } catch (error) {
    console.error('Error fetching place details:', error);
    document.getElementById('place-name').textContent = 'Error loading place details';
  }
}

/**
 * Display place details in the DOM
 * @param {Object} place - Place object
 */
function displayPlaceDetails(place) {
  // Update place name
  const placeNameElement = document.getElementById('place-name');
  if (placeNameElement) {
    placeNameElement.textContent = place.name || 'Unknown Place';
  }

  // Update place description
  const placeDescriptionElement = document.getElementById('place-description');
  if (placeDescriptionElement) {
    placeDescriptionElement.textContent = place.description || 'No description available';
  }

  // Update place price
  const placePriceElement = document.getElementById('place-price');
  if (placePriceElement) {
    placePriceElement.textContent = `$${place.price_per_night || 0}/night`;
  }

  // Update host information
  const placeHostElement = document.getElementById('place-host');
  if (placeHostElement) {
    if (place.owner) {
      placeHostElement.textContent = `${place.owner.first_name || ''} ${place.owner.last_name || ''}`.trim() || 'Unknown Host';
    } else {
      placeHostElement.textContent = 'Unknown Host';
    }
  }

  // Display amenities
  const amenitiesList = document.getElementById('amenities-list');
  if (amenitiesList) {
    amenitiesList.innerHTML = '';

    if (place.amenities && place.amenities.length > 0) {
      place.amenities.forEach(amenity => {
        const li = document.createElement('li');
        li.textContent = amenity.name || 'Unknown amenity';
        amenitiesList.appendChild(li);
      });
    } else {
      const li = document.createElement('li');
      li.textContent = 'No amenities listed';
      amenitiesList.appendChild(li);
    }
  }
}

/**
 * Fetch reviews for a place
 * @param {string} token - JWT token
 * @param {string} placeId - Place ID
 */
async function fetchPlaceReviews(token, placeId) {
  try {
    const headers = {
      'Content-Type': 'application/json'
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/places/${placeId}/reviews`, {
      method: 'GET',
      headers: headers
    });

    if (response.ok) {
      const reviews = await response.json();
      displayReviews(reviews);
    } else {
      console.error('Failed to fetch reviews:', response.statusText);
    }
  } catch (error) {
    console.error('Error fetching reviews:', error);
  }
}

/**
 * Display reviews in the DOM
 * @param {Array} reviews - Array of review objects
 */
function displayReviews(reviews) {
  const reviewsContainer = document.getElementById('reviews-container');
  if (!reviewsContainer) return;

  reviewsContainer.innerHTML = '';

  if (!reviews || reviews.length === 0) {
    reviewsContainer.innerHTML = '<p>No reviews yet. Be the first to review!</p>';
    return;
  }

  reviews.forEach(review => {
    const reviewCard = document.createElement('div');
    reviewCard.className = 'review-card';

    const rating = review.rating || 0;
    const userName = review.user ?
      `${review.user.first_name || ''} ${review.user.last_name || ''}`.trim() || 'Anonymous' :
      'Anonymous';

    reviewCard.innerHTML = `
            <div class="rating">${generateStars(rating)}</div>
            <div class="user">${userName}</div>
            <p>${review.text || 'No comment provided'}</p>
        `;

    reviewsContainer.appendChild(reviewCard);
  });
}

/**
 * Check authentication for place details page
 * @param {string} placeId - Place ID
 */
function checkPlaceAuthentication(placeId) {
  const token = checkAuthentication();
  const addReviewSection = document.getElementById('add-review');

  // Show/hide add review form based on authentication
  if (addReviewSection) {
    if (!token) {
      addReviewSection.style.display = 'none';
    } else {
      addReviewSection.style.display = 'block';
    }
  }

  // Fetch place details regardless of authentication status
  fetchPlaceDetails(token, placeId);
}

// =============================================================================
// TASK 4: ADD REVIEW FUNCTIONS
// =============================================================================

/**
 * Submit a review for a place
 * @param {string} token - JWT token
 * @param {string} placeId - Place ID
 * @param {string} reviewText - Review text
 * @param {number} rating - Rating (1-5)
 */
async function submitReview(token, placeId, reviewText, rating) {
  try {
    const response = await fetch(`${API_BASE_URL}/places/${placeId}/reviews`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        text: reviewText,
        rating: parseInt(rating, 10)
      })
    });

    if (response.ok) {
      // Show success message
      showMessage('success-message', 'Review submitted successfully!', false);

      // Clear the form
      const reviewForm = document.getElementById('review-form');
      if (reviewForm) {
        reviewForm.reset();
      }

      // If on place details page, refresh reviews
      if (window.location.pathname.includes('place.html')) {
        setTimeout(() => {
          fetchPlaceReviews(token, placeId);
        }, 1000);
      }

      // If on add_review.html, redirect to place details after delay
      if (window.location.pathname.includes('add_review.html')) {
        setTimeout(() => {
          window.location.href = `place.html?id=${placeId}`;
        }, 2000);
      }
    } else {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = errorData.message || 'Failed to submit review';
      showMessage('error-message', errorMessage, true);
    }
  } catch (error) {
    console.error('Error submitting review:', error);
    showMessage('error-message', 'Network error. Please try again later.', true);
  }
}

/**
 * Check authentication for review pages and redirect if not authenticated
 * @returns {string|null} - JWT token or null
 */
function checkReviewAuthentication() {
  const token = checkAuthentication();

  // If not authenticated, redirect to index page
  if (!token) {
    window.location.href = 'index.html';
    return null;
  }

  // If on add_review.html, try to fetch place name for page title
  if (window.location.pathname.includes('add_review.html')) {
    const placeId = getPlaceIdFromURL();
    if (placeId) {
      fetchPlaceNameForReview(token, placeId);
    }
  }

  return token;
}

/**
 * Fetch place name for review page title
 * @param {string} token - JWT token
 * @param {string} placeId - Place ID
 */
async function fetchPlaceNameForReview(token, placeId) {
  try {
    const response = await fetch(`${API_BASE_URL}/places/${placeId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    });

    if (response.ok) {
      const place = await response.json();
      const titleElement = document.getElementById('place-title');
      if (titleElement) {
        titleElement.textContent = `Review for: ${place.name || 'Unknown Place'}`;
      }
    }
  } catch (error) {
    console.error('Error fetching place name:', error);
  }
}

// =============================================================================
// MAIN EVENT LISTENERS AND INITIALIZATION
// =============================================================================

/**
 * Main initialization when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', () => {
  // Get current page elements
  const loginForm = document.getElementById('login-form');
  const priceFilter = document.getElementById('price-filter');
  const reviewForm = document.getElementById('review-form');
  const placeId = getPlaceIdFromURL();

  // =============================================================================
  // LOGIN PAGE HANDLING (login.html)
  // =============================================================================
  if (loginForm) {
    loginForm.addEventListener('submit', async (event) => {
      event.preventDefault();

      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;

      if (email && password) {
        await loginUser(email, password);
      } else {
        showMessage('error-message', 'Please fill in all fields', true);
      }
    });
  }

  // =============================================================================
  // PLACES LIST PAGE HANDLING (index.html)
  // =============================================================================
  if (priceFilter) {
    // Load price filter options
    loadPriceFilterOptions();

    // Add event listener for price filtering
    priceFilter.addEventListener('change', (event) => {
      filterPlacesByPrice(event.target.value);
    });
  }

  // =============================================================================
  // REVIEW FORM HANDLING (place.html and add_review.html)
  // =============================================================================
  if (reviewForm) {
    const token = checkReviewAuthentication();

    if (token) {
      reviewForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        // Get review text from either textarea
        const reviewText = document.getElementById('review')?.value ||
          document.getElementById('review-text')?.value || '';

        const rating = document.getElementById('rating')?.value || '';

        if (placeId && reviewText.trim() && rating) {
          await submitReview(token, placeId, reviewText.trim(), rating);
        } else {
          showMessage('error-message', 'Please fill in all fields', true);
        }
      });
    }
  }

  // =============================================================================
  // PAGE-SPECIFIC INITIALIZATION
  // =============================================================================

  // Place details page (place.html)
  if (placeId && !reviewForm) {
    checkPlaceAuthentication(placeId);
  }
  // Index page (index.html) - load places
  else if (!placeId && !reviewForm && !loginForm && priceFilter) {
    const token = checkAuthentication();
    fetchPlaces(token);
  }
  // Other pages - just check authentication for navigation
  else if (!loginForm) {
    checkAuthentication();
  }

  // Redirect to index if on add_review.html without place ID
  if (window.location.pathname.includes('add_review.html') && !placeId) {
    window.location.href = 'index.html';
  }
});
