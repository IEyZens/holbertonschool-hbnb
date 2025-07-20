
# HBnB - Part 4: Simple Web Client (HTML5, CSS3 & JS)

> **Frontend Interface for HBnB Clone**
> Dynamic web client using vanilla JavaScript, HTML5 & CSS3 to consume the RESTful API with JWT-based authentication.

![HTML5](https://img.shields.io/badge/HTML5-Markup-orange)
![CSS3](https://img.shields.io/badge/CSS3-Styling-blue)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow)
![Frontend](https://img.shields.io/badge/Frontend-VanillaJS-lightgrey)
![License](https://img.shields.io/badge/license-Holberton-lightgrey)

---

## 📑 Table of Contents

- [📘 Overview](#-overview)
- [🏗️ Project Structure](#-project-structure)
- [⚙️ Technologies](#-technologies)
- [🚀 Getting Started](#-getting-started)
- [🧠 Functionality Summary](#-functionality-summary)
- [📄 Pages & Behavior](#-pages--behavior)
- [📚 Resources](#-resources)
- [👥 Author](#-author)
- [📄 License](#-license)

---

## 📘 Overview
This is **Part 4** of the HBnB project, focused on the **Frontend Web Client**. It connects to the RESTful API developed in previous parts and provides a user-friendly interface to interact with places, reviews, and authentication features.

Features implemented in this phase:
- **Modern JavaScript Frontend**: Full SPA-like behavior using DOM manipulation.
- **Authentication with JWT**: Login flow managed client-side with token saved in cookies.
- **Dynamic Rendering**: Places are fetched from the API and rendered dynamically.
- **Review Submission**: Logged-in users can post reviews, including ratings.
- **Data Filtering**: Price filter implemented on the home page.
- **Page Navigation**: Supports multiple views: place list, place detail, login, and add-review.



This is **Part 4** of the HBnB project. It introduces a complete frontend using:

- Plain **HTML5/CSS3/JavaScript** (no frameworks)
- **JWT authentication** stored in cookies
- **Fetch API** to interact with backend endpoints
- Dynamic DOM rendering, form handling and validation

All frontend behavior is in a single JavaScript file (`scripts.js`). Pages dynamically load and interact with the backend.

---

## 🏗️ Project Structure

```
part4/
├── app/                            # Backend Flask application (same as part3)
│   ├── api/                        # RESTful API with Flask-RESTx
│   │   └── v1/
│   │       ├── auth.py             # JWT login endpoints
│   │       ├── users.py, places.py, reviews.py, amenities.py, etc.
│   ├── models/                     # SQLAlchemy models
│   ├── services/                   # Business logic (Facade pattern)
│   └── persistence/                # Database repositories
│
├── instance/
│   └── development.db              # SQLite DB
│
├── doc_images/                     # Documentation screenshots
│   ├── img_index.png
│   ├── img_place.png
│   ├── img_place_review.png
│   └── img_review.png
│
├── images/                         # UI icons and logo
│   ├── icon.png
│   ├── logo.png
│   ├── icon_bath.png
│   ├── icon_bed.png
│   └── icon_wifi.png
│
├── tests/                          # Backend unit and integration tests
│   └── test_*.py                   # Covers all resources
│
├── add_review.html                 # Page to add a new review
├── index.html                      # Homepage (place list + filter)
├── login.html                      # JWT login form
├── place.html                      # View place details and reviews
├── config.py                       # Environment config for backend
├── database_diagram.md             # Optional ER diagram
├── README.md                       # Project documentation (this file)
├── requirements.txt                # Python dependencies for backend
├── run.py                          # Flask entry point
├── scripts.js                      # Main frontend logic (event handlers, fetch requests)
└── styles.css                      # Styling for all frontend pages
```

---

## ⚙️ Technologies
- **HTML5 & CSS3** — page layout and visual design.
- **JavaScript ES6+** — dynamic behavior and API interaction.
- **Fetch API** — used to communicate with the backend.
- **Cookie-based Auth** — stores JWT securely in cookies.
- **Responsive Design** — built to display well on desktop and mobile.



- **HTML5**: semantic markup
- **CSS3**: custom styling
- **JavaScript (ES6)**: DOM interaction and Fetch API
- **Cookies**: store JWT token
- **REST API**: consumes Flask endpoints from part3

---

## 🚀 Getting Started
### 1. Clone the repository

```bash
git clone https://github.com/IEyZens/holbertonschool-hbnb.git
cd holbertonschool-hbnb/part4
```

### 2. Launch the backend

Make sure your Flask API (from Part 3) is running:

```bash
cd ../part3
python run.py
```

### 3. Open the frontend

Open `index.html` in your browser (e.g. Chrome):

```bash
open index.html
# or right-click > "Open with browser"
```

Make sure the API is running on `http://localhost:5000`.



1. Run the backend (from part3)
```bash
python run.py
# API: http://localhost:5000/api/v1/
```

2. Open `index.html` in browser (via Live Server or file://)

> ⚠️ For full functionality (especially auth), a local HTTP server is required (e.g. `Live Server` in VSCode).

---

## 🧠 Functionality Summary

| Page           | Description                                   |
|----------------|-----------------------------------------------|
| `login.html`   | Login form, stores JWT in cookie              |
| `index.html`   | Lists all places (GET /places)                |
|                | Filter by max price (client-side)             |
| `place.html`   | Detailed view of a place and its reviews      |
|                | Adds review if logged in                      |
| `add_review.html` | Dedicated page to submit a review (with rating) |

---

## 📄 Pages & Behavior

### 🔐 `login.html`

- Submits credentials via POST `/login`
- On success: JWT stored as `token` in cookie, redirect to `index.html`

### 🏠 `index.html`

- Checks for `token` cookie
- If present → fetches `/places` with Authorization header
- Places displayed as `.place-card` dynamically
- Filter updates visible cards (JS-only)

### 🏡 `place.html?id=<uuid>`

- Gets `id` from query string
- Fetches `/places/<id>` and loads place + reviews
- If token present: shows review form

### ✍️ `add_review.html?id=<uuid>`

- Loads place name dynamically
- Submits new review via POST `/reviews`
- Requires JWT (`Authorization: Bearer` header)

---

## 📚 Resources
- [MDN JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
- [MDN Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [HTML Living Standard](https://html.spec.whatwg.org/)
- [CSS Tricks](https://css-tricks.com/)
- [JWT Introduction](https://jwt.io/introduction/)



- [MDN Web Docs - Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [MDN Web Docs - Working with Forms](https://developer.mozilla.org/en-US/docs/Learn/Forms)
- [MDN Web Docs - JavaScript Cookies](https://developer.mozilla.org/en-US/docs/Web/API/Document/cookie)

---

## 👥 Author

Developed by Thomas Roncin — Holberton School Toulouse.

---

## 📄 License

Licensed under Holberton School Terms of Service.
For more information, visit [holbertonschool.com](https://www.holbertonschool.com/terms-of-service).
