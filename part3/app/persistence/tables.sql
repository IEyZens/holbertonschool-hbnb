-- HBnB Database Schema - Complete Table Creation and Initial Data Script
-- Task: SQL Scripts for Table Generation and Initial Data

-- Create User table
CREATE TABLE IF NOT EXISTS User (
    id CHAR(36) PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255),
    is_admin BOOLEAN DEFAULT FALSE
);

-- Create Place table
CREATE TABLE IF NOT EXISTS Place (
    id CHAR(36) PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    price DECIMAL(10, 2),
    latitude FLOAT,
    longitude FLOAT,
    owner_id CHAR(36),
    FOREIGN KEY (owner_id) REFERENCES User(id)
);

-- Create Review table
CREATE TABLE IF NOT EXISTS Review (
    id CHAR(36) PRIMARY KEY,
    text TEXT,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    user_id CHAR(36),
    place_id CHAR(36),
    FOREIGN KEY (user_id) REFERENCES User(id),
    FOREIGN KEY (place_id) REFERENCES Place(id),
    UNIQUE (user_id, place_id)
);

-- Create Amenity table
CREATE TABLE IF NOT EXISTS Amenity (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) UNIQUE
);

-- Create Place_Amenity table (Many-to-Many relationship)
CREATE TABLE IF NOT EXISTS Place_Amenity (
    place_id CHAR(36),
    amenity_id CHAR(36),
    PRIMARY KEY (place_id, amenity_id),
    FOREIGN KEY (place_id) REFERENCES Place(id),
    FOREIGN KEY (amenity_id) REFERENCES Amenity(id)
);

-- ============================================================================
-- INITIAL DATA INSERTION
-- ============================================================================

-- Insert Administrator User
-- ID: 36c9050e-ddd3-4c3b-9731-9f487208bbc1 (fixed as required)
-- Password: admin1234 (hashed with bcrypt)
INSERT INTO User (
    id,
    first_name,
    last_name,
    email,
    password,
    is_admin
) VALUES (
    '36c9050e-ddd3-4c3b-9731-9f487208bbc1',
    'Admin',
    'HBnB',
    'admin@hbnb.io',
    '$2b$12$FERzQoUTR3zKwPa0ZsX5yuIv5eFW6rPF3zSuPH2Q1RB4ph.6s7hZW',
    TRUE
);

-- Insert Initial Amenities with UUID4 values
INSERT INTO Amenity (id, name) VALUES
    ('550e8400-e29b-41d4-a716-446655440000', 'WiFi'),
    ('550e8400-e29b-41d4-a716-446655440001', 'Swimming Pool'),
    ('550e8400-e29b-41d4-a716-446655440002', 'Air Conditioning');
