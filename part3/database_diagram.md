```mermaid
erDiagram
    USER {
        string id
        string first_name
        string last_name
        string email
        string password
        boolean is_admin
    }
    PLACE {
        string id
        string title
        string description
        float price
        float latitude
        float longitude
        string owner_id
    }
    REVIEW {
        string id
        string text
        int rating
        string user_id
        string place_id
    }
    AMENITY {
        string id
        string name
    }
    PLACE_AMENITY {
        string place_id
        string amenity_id
    }

    USER ||--o{ PLACE : owns
    USER ||--o{ REVIEW : writes
    PLACE ||--o{ REVIEW : receives
    PLACE ||--o{ PLACE_AMENITY : has
    AMENITY ||--o{ PLACE_AMENITY : is
```
