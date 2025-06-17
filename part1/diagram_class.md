## :jigsaw: Diagramme de classes — Projet HBnB
```mermaid
---
config:
  theme: default
---
classDiagram
    class BaseModel {
        - id
        + created_at
        + updated_at
    }
    class User {
        - last_name
        + first_name
        - email
        - password
        + admin
        + create_user()
        + update_user()
        + delete_user()
        - authenticate()
    }
    class Place {
        - owner
        + title
        + description
        + price
		+ max_person
        + localisation (longitude/latitude)
        + contact
        + list_amenities
        + create_place()
        + update_place()
        + delete_place()
        + list_place
        }
    class Review {
        + user_id
        + place_id
        + rating
        + comment
        + create_review()
        + update_review()
        + delete_review()
        + list_reviews_by_place()
    }
    class Amenity {
        + name
        + description
        + create_amenity()
        + update_amenity()
        + delete_amenity()
        + list_amenities()
    }
    %% inherits
    User --|> BaseModel : inherits from
    Place --|> BaseModel : inherits from
    Review --|> BaseModel : inherits from
    Amenity --|> BaseModel : inherits from
    %% Relations
    User "1" --> "0..*" Place : has
    User "1" --> "0..*" Review : write
    Place "1" --> "0..*" Review : receives
    Place "0..*" --> "0..*" Amenity : include
```
