# HBnB - Part 2: RESTful API with Flask

> Clean architecture API with Flask, in-memory repository, and layered design (User, Place, Review, Amenity)

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
- [🔮 Future Improvements](#-future-improvements)
- [👥 Authors](#-authors)
- [📄 License](#-license)

## 📘 Overview

This is the second part of the **HBnB full-stack project**, which focuses on building a RESTful web API using Flask and Flask-RESTx. The API follows a clean, layered architecture and supports operations on four main entities: `User`, `Place`, `Review`, and `Amenity`.

The codebase is organized into three main layers:

- **Presentation**: RESTful API endpoints using Flask-RESTx
- **Business Logic**: entity models and validation
- **Persistence**: in-memory data storage with repository pattern

The project adopts the **Facade design pattern** to streamline communication between layers and centralize business logic.

## 🏗️ Project Structure

```
part2/
├── app/                        # Main application package
│   ├── __init__.py             # Initializes Flask app and registers namespaces
│
│   ├── api/                    # Presentation layer (RESTful API)
│   │   ├── __init__.py         # Registers all versioned API namespaces
│   │   └── v1/                 # Version 1 of the API
│   │       ├── __init__.py     # Initializes v1 namespace
│   │       ├── users.py        # Endpoints for User CRUD operations
│   │       ├── places.py       # Endpoints for Place CRUD operations
│   │       ├── reviews.py      # Endpoints for Review CRUD + delete
│   │       └── amenities.py    # Endpoints for Amenity CRUD operations
│
│   ├── models/                 # Business logic and domain entities
│   │   ├── __init__.py         # Initializes models module
│   │   ├── base_model.py       # BaseModel: shared UUID, timestamps, update()
│   │   ├── user.py             # User entity with validation
│   │   ├── place.py            # Place entity with owner, amenities, reviews
│   │   ├── review.py           # Review entity linked to User and Place
│   │   └── amenity.py          # Amenity entity
│
│   ├── services/               # Application layer using Facade pattern
│   │   ├── __init__.py         # Creates singleton `facade` instance
│   │   └── facade.py           # HBnBFacade: central coordinator for logic & data access
│
│   └── persistence/            # In-memory persistence layer
│       ├── __init__.py         # Initializes persistence module
│       └── repository.py       # Repository interface + InMemoryRepository implementation
│
├── tests/                      # Unit and integration tests
│   ├── __init__.py             # Initializes test package
│   ├── test_base_model.py      # Tests for BaseModel functionality
│   ├── test_users_api.py       # API tests: /users
│   ├── test_places_api.py      # API tests: /places
│   ├── test_reviews_api.py     # API tests: /reviews
│   ├── test_amenities_api.py   # API tests: /amenities
│   ├── test_user_model.py      # Model tests: User
│   ├── test_place_model.py     # Model tests: Place
│   ├── test_review_model.py    # Model tests: Review
│   └── test_amenity_model.py   # Model tests: Amenity
│
├── config.py                   # App config classes: Config, DevelopmentConfig, ENV loading
├── run.py                      # Entry point to launch the Flask app
├── requirements.txt            # Project dependencies (Flask, Flask-RESTx, etc.)
└── README.md                   # Project documentation
```

## ⚙️ Technologies

- Python 3.8+ — backend language
- Flask — lightweight WSGI web application framework
- Flask-RESTx — extension for building RESTful APIs with Swagger support
- UUID — unique identifiers for all objects

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/IEyZens/holbertonschool-hbnb.git
cd holbertonschool-hbnb/part2
```

### 2. Set up virtual environment

```
python3 -m venv venv
source venv/bin/activate
```

```
On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 3.5 (Optional) Create a `.env` file

If needed, create a `.env` file to store environment variables such as:

```env
SECRET_KEY=my-secret-key
FLASK_ENV=development
```

### 4. Run the application

```
python run.py
```

Access the API at: http://127.0.0.1:5000/

## ⚙️ Configuration

The app uses a `config.py` file to manage environment settings.

Default configuration:

- `DEBUG`: `True` (development mode)
- `SECRET_KEY`: Read from environment or fallback default

You can override these by creating a `.env` file or setting environment variables before running `run.py`.

## 🧠 Core Business Models

All entities inherit from `BaseModel`, which provides:

- `id` (UUID)
- `created_at`, `updated_at` (timestamps)
- `update(data)` — applies dictionary updates and refreshes `updated_at`

### User

- `first_name`, `last_name`, `email` (unique), `is_admin`

### Place

- `title`, `description`, `price`, `latitude`, `longitude`
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

## ✅ Validation

All entities include built-in validation rules to ensure data integrity:

- ✔️ Required fields (e.g. `first_name`, `email`, `price`)
- ❌ Rejects invalid email format
- ❌ Rejects out-of-bound coordinates (lat: -90 to 90, long: -180 to 180)
- ❌ Rejects invalid ratings (must be 1–5)

## 🧪 Testing

### 🔹 Manual testing (via cURL)

```bash
curl -X POST http://127.0.0.1:5000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{"first_name": "Alice", "last_name": "Smith", "email": "alice@example.com"}'
```

### 🔹 Interactive testing (Swagger UI)

Explore the API via [Swagger UI](http://127.0.0.1:5000/)

### 🔹 Automated unit tests (unittest)

```python
import unittest
from app import create_app

class TestUser(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_user_creation(self):
        res = self.client.post('/api/v1/users/', json={
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com"
        })
        self.assertEqual(res.status_code, 201)
```

### 🔹 Run all tests (project-wide)

This will discover and run all test files inside the `tests/` folder:

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

## 📄 License

This project is for educational purposes and licensed under the Holberton School Terms of Use.\
See [Holberton School’s License Policy](https://www.holbertonschool.com/terms-of-service) for more.
