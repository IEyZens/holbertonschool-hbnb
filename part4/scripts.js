/*
  This is a SAMPLE FILE to get you started.
  Please, follow the project instructions to complete the tasks.
*/

let allPlaces = [];

document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('login-form');
  const priceFilter = document.getElementById('price-filter');

  if (loginForm) {
    loginForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      loginUser(email, password);
    });
  }

  document.getElementById('price-filter').addEventListener('change', (event) => {
    const selectedValue = event.target.value;

    if (selectedValue === 'All') {
      displayPlaces(allPlaces);
    } else {
      const maxPrice = parseInt(selectedValue);
      const filtered = allPlaces.filter(place => place.price <= maxPrice);
      displayPlaces(filtered);
    }
  });

  ['10', '50', '100', 'All'].forEach(value => {
    const option = document.createElement('option');
    option.value = value;
    option.textContent = value;
    priceFilter.appendChild(option);
  });

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

  if (!token) {
    loginLink.style.display = 'block';
  } else {
    loginLink.style.display = 'none';
    fetchPlaces(token);
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
  const response = await fetch('http://127.0.0.1:5000/api/v1/places', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + token
    },
  });

  if (response.ok) {
    const data = await response.json();
    allPlaces = data;
    displayPlaces(allPlaces);
  } else {
    alert('Fetch failed: ' + response.statusText);
  }
}

function displayPlaces(places) {
  const placesList = document.getElementById('places-list');
  placesList.innerHTML = '';

  places.forEach(element => {
    const variable = element;
    const card = document.createElement('div');
    const name = document.createElement('h3');
    const price = document.createElement('p');
    const details = document.createElement('button');

    card.classList.add('place-card');
    name.textContent = element.name;
    price.textContent = `Price: $${element.price}`;

    details.classList.add('details-button');
    details.textContent = 'View Details';

    card.appendChild(name);
    card.appendChild(price);
    card.appendChild(details);

    placesList.appendChild(card);
  });
}
