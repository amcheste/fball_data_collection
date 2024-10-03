CREATE TABLE positions (
    id INT PRIMARY KEY NOT NULL,
    name VARCHAR(255),
    abbreviation VARCHAR(10)
);

CREATE TABLE teams (
    id INT PRIMARY KEY NOT NULL,
    name VARCHAR(255),
    abbreviation VARCHAR(10),
    location VARCHAR(255)
);

CREATE TABLE players(
    id INT PRIMARY KEY NOT NULL,
    name VARCHAR(255),
    weight FLOAT,
    height FLOAT,
    experience INT,
    active BOOLEAN,
    status VARCHAR(255),
    position INT,
    age INT,
    team INT
);