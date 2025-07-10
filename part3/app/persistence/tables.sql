CREATE TABLE IF NOT EXISTS User (
    id CHAR(36) PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255),
    is_admin BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Place (
    id CHAR(36) PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    price DECIMAL(10, 2),
    latitude FLOAT,
    longitude FLOAT,
    max_person INT,
    owner_id CHAR(36),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES User (id)
);

CREATE TABLE IF NOT EXISTS Review (
    id CHAR(36) PRIMARY KEY,
    text TEXT,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    user_id CHAR(36),
    place_id CHAR(36),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User (id),
    FOREIGN KEY (place_id) REFERENCES Place (id),
    UNIQUE (user_id, place_id)
);

CREATE TABLE IF NOT EXISTS Amenity (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Place_Amenity (
    place_id CHAR(36),
    amenity_id CHAR(36),
    PRIMARY KEY (place_id, amenity_id),
    FOREIGN KEY (place_id) REFERENCES Place (id),
    FOREIGN KEY (amenity_id) REFERENCES Amenity (id)
);

INSERT INTO
    User (
        id,
        email,
        first_name,
        last_name,
        password,
        is_admin
    )
VALUES (
        '36c9050e-ddd3-4c3b-9731-9f487208bbc1',
        'admin@hbnb.io',
        'Admin',
        'HBnB',
        '$2a$12$6ZWHgzuFxrBK.MtZPvpa0un.ffOz3kN4Ird/V2wjGWYLNbJbfceqK',
        TRUE
    );

INSERT INTO
    Amenity (id, name)
VALUES (
        '564f7b23-ef41-4142-b53f-55b0a4ebdb36',
        'WiFi'
    ),
    (
        '88e8f136-fbb8-4861-a42f-6b2904854c6c',
        'Swimming Pool'
    ),
    (
        '20825cf0-f620-42c2-bcde-282a2517467c',
        'Air Conditioning'
    );
