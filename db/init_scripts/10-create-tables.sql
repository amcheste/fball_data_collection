CREATE TABLE positions (
    id INT PRIMARY KEY NOT NULL,
    name VARCHAR(255) NOT NULL,
    abbreviation VARCHAR(10) NOT NULL
);

CREATE TABLE teams (
    id INT PRIMARY KEY NOT NULL,
    name VARCHAR(255) NOT NULL,
    abbreviation VARCHAR(10) NOT NULL,
    location VARCHAR(255) NOT NULL
);