# HBnB - Part 3: RESTful API with Flask & SQLAlchemy

> Clean architecture API with Flask, SQLAlchemy repository, and layered design (User, Place, Review, Amenity)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-RESTx-success)
![License](https://img.shields.io/badge/license-Holberton-lightgrey)
[![Swagger UI](https://img.shields.io/badge/Swagger-UI-yellowgreen)](http://127.0.0.1:5000/)

## 📑 Table of Contents

- [📘 Overview](#-overview)
- [🏗️ Project Structure](#-project-structure)
- [⚙️ Technologies](#-technologies)
- [🚀 Getting Started](#-getting-started)
- [⚙️ Configuration](#-configuration)
- [🧠 Core Business Models](#-core-business-models)
- [🔌 API Endpoints](#-api-endpoints)
- [✅ Validation](#-validation)
- [🧪 Testing](#-testing)
- [👥 Authors](#-authors)
- [📄 License](#-license)

## 📘 Overview

This is the third part of the **HBnB full-stack project**, focusing on a RESTful API using Flask, Flask-RESTx, and SQLAlchemy for persistent storage. The API follows a clean, layered architecture and supports operations on four main entities: `User`, `Place`, `Review`, and `Amenity`.

The codebase is organized into three main layers:

- **Presentation**: RESTful API endpoints using Flask-RESTx
- **Business Logic**: entity models and validation
- **Persistence**: SQLAlchemy ORM with repository pattern

The project uses the **Facade design pattern** to centralize business logic and coordinate between layers.

## 🏗️ Project Structure

```
part3/
├── app/                        # Main application package
│   ├── __init__.py             # Initializes Flask app and registers namespaces
│   ├── extensions.py           # Flask extensions (db, bcrypt, jwt)
│   ├── api/                    # Presentation layer (RESTful API)
│   │   ├── v1/
│   │   │   ├── users.py        # Endpoints for User CRUD operations
│   │   │   ├── places.py       # Endpoints for Place CRUD operations
│   │   │   ├── reviews.py      # Endpoints for Review CRUD + delete
│   │   │   ├── amenities.py    # Endpoints for Amenity CRUD operations
│   │   │   ├── admin_users.py  # Admin endpoints for users
│   │   │   ├── admin_places.py # Admin endpoints for places
│   │   │   ├── admin_reviews.py# Admin endpoints for reviews
│   │   │   ├── admin_amenities.py # Admin endpoints for amenities
│   │   │   └── auth.py         # Authentication endpoints
│   ├── models/                 # Business logic and domain entities
│   │   ├── base_model.py       # BaseModel: shared UUID, timestamps, update()
│   │   ├── user.py             # User entity with validation
│   │   ├── place.py            # Place entity with owner, amenities, reviews
│   │   ├── review.py           # Review entity linked to User and Place
│   │   └── amenity.py          # Amenity entity
│   ├── services/               # Application layer using Facade pattern
│   │   ├── facade.py           # HBnBFacade: central coordinator for logic & data access
│   └── persistence/            # Persistence layer (SQLAlchemy repositories)
│       ├── repository.py       # Generic SQLAlchemy repository
│       └── user_repository.py  # User-specific repository
├── instance/
│   └── development.db          # SQLite database (for development)
├── tests/                      # Unit and integration tests
│   ├── test_base_model.py      # Tests for BaseModel functionality
│   ├── test_users_api.py       # API tests: /users
│   ├── test_places_api.py      # API tests: /places
│   ├── test_reviews_api.py     # API tests: /reviews
│   ├── test_amenities_api.py   # API tests: /amenities
│   ├── test_user_model.py      # Model tests: User
│   ├── test_place_model.py     # Model tests: Place
│   ├── test_review_model.py    # Model tests: Review
│   └── test_amenity_model.py   # Model tests: Amenity
├── config.py                   # App config classes: Config, DevelopmentConfig, ENV loading
├── run.py                      # Entry point to launch the Flask app
├── requirements.txt            # Project dependencies (Flask, Flask-RESTx, SQLAlchemy, etc.)
└── README.md                   # Project documentation
```

## ⚙️ Technologies

- Python 3.8+ — backend language
- Flask — lightweight WSGI web application framework
- Flask-RESTx — extension for building RESTful APIs with Swagger support
- SQLAlchemy — ORM for database persistence
- Flask-JWT-Extended — authentication and authorization
- UUID — unique identifiers for all objects

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/IEyZens/holbertonschool-hbnb.git
cd holbertonschool-hbnb/part3
```

### 2. Set up virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

_On Windows: `venv\Scripts\activate`_

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 3.5 (Optional) Create a `.env` file

If needed, create a `.env` file to store environment variables such as:

```env
SECRET_KEY=my-secret-key
FLASK_ENV=development
DATABASE_URL=sqlite:///instance/development.db
```

### 4. Run the application

```bash
python run.py
```

Access the API at: http://127.0.0.1:5000/

## ⚙️ Configuration

The app uses a `config.py` file to manage environment settings.

Default configuration:

- `DEBUG`: `True` (development mode)
- `SECRET_KEY`: Read from environment or fallback default
- `SQLALCHEMY_DATABASE_URI`: SQLite by default

You can override these by creating a `.env` file or setting environment variables before running `run.py`.

## 🧠 Core Business Models

All entities inherit from `BaseModel`, which provides:

- `id` (UUID or integer)
- `created_at`, `updated_at` (timestamps)
- `update(data)` — applies dictionary updates and refreshes `updated_at`

### User

- `first_name`, `last_name`, `email` (unique), `is_admin`, `password` (hashed)
- Relationships: `places` (owned), `reviews` (authored)

### Place

- `title`, `description`, `price`, `latitude`, `longitude`, `max_person`
- `owner` (User)
- `amenities`: list of Amenity
- `reviews`: list of Review

### Review

- `text`, `rating` (1–5)
- Linked to `user` and `place`

### Amenity

- `name` only (e.g., "Wi-Fi", "Parking")

## 🔌 API Endpoints

**Base path:** `/api/v1/`

---

### 🧑 Users

| Method | Endpoint      | Description    |
| ------ | ------------- | -------------- |
| POST   | `/users/`     | Create a user  |
| GET    | `/users/<id>` | Get user by ID |
| GET    | `/users/`     | List all users |
| PUT    | `/users/<id>` | Update a user  |

---

### 🛏️ Amenities

| Method | Endpoint          | Description        |
| ------ | ----------------- | ------------------ |
| POST   | `/amenities/`     | Create amenity     |
| GET    | `/amenities/`     | List all amenities |
| GET    | `/amenities/<id>` | Get amenity by ID  |
| PUT    | `/amenities/<id>` | Update amenity     |

---

### 🏡 Places

| Method | Endpoint       | Description                              |
| ------ | -------------- | ---------------------------------------- |
| POST   | `/places/`     | Create place                             |
| GET    | `/places/`     | List all places                          |
| GET    | `/places/<id>` | Get place with owner, amenities, reviews |
| PUT    | `/places/<id>` | Update place                             |

---

### ✍️ Reviews

| Method | Endpoint                     | Description              |
| ------ | ---------------------------- | ------------------------ |
| POST   | `/reviews/`                  | Create review            |
| GET    | `/reviews/`                  | List all reviews         |
| GET    | `/reviews/<id>`              | Get review by ID         |
| PUT    | `/reviews/<id>`              | Update review            |
| DELETE | `/reviews/<id>`              | Delete review            |
| GET    | `/places/<place_id>/reviews` | List reviews for a place |

---

### 🔐 Auth & Admin

- `/auth/login` — Obtain JWT token
- `/admin/*` — Admin-only endpoints for managing users, places, reviews, amenities

## ✅ Validation

All entities include built-in validation rules to ensure data integrity:

- ✔️ Required fields (e.g. `first_name`, `email`, `price`)
- ❌ Rejects invalid email format
- ❌ Rejects out-of-bound coordinates (lat: -90 to 90, long: -180 to 180)
- ❌ Rejects invalid ratings (must be 1–5)
- ❌ Password must be at least 8 characters

## 🧪 Testing

### 🔹 Manual testing (via cURL)

```bash
curl -X POST http://127.0.0.1:5000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{"first_name": "Alice", "last_name": "Smith", "email": "alice@example.com", "password": "supersecret"}'
```

### 🔹 Interactive testing (Swagger UI)

Explore the API via [Swagger UI](http://127.0.0.1:5000/)

### 🔹 Automated unit tests (pytest)

```bash
pytest tests/
```

Or with unittest:

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

### 🔹 Bonus: JSON Response Example

```json
{
  "id": "12df1f4c-e2b1-4a89-b3c2-b77a4e6b5f56",
  "first_name": "Alice",
  "last_name": "Smith",
  "email": "alice@example.com"
}
```

## 👥 Authors

Project developed by Thomas Roncin of Holberton School as part of the HBnB full-stack curriculum.

See [official part3 documentation](https://github.com/Holberton-Uy/hbnb-doc/tree/main/part3) for more.

## 📄 License

This project is for educational purposes and licensed under the Holberton School Terms of Use.
See [Holberton School’s License Policy](https://www.holbertonschool.com/terms-of-service) for more.
