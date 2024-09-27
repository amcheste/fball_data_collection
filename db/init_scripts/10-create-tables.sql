CREATE TABLE positions (
    id INT PRIMARY KEY NOT NULL,
    name VARCHAR(255),
    abbreviation VARCHAR(10)
);

CREATE TABLE teams (
    id INT PRIMARY KEY NOT NULL,
    name VARCHAR(255) NOT NULL,
    abbreviation VARCHAR(10) NOT NULL,
    location VARCHAR(255) NOT NULL
);

CREATE TABLE players(
    id INT PRIMARY KEY NOT NULL,
    name VARCHAR(255) NOT NULL,
    weight FLOAT NOT NULL,
    height FLOAT NOT NULL,
    experience INT NOT NULL,
    active BOOLEAN NOT NULL,
    status VARCHAR(255) NOT NULL,
    position INT NOT NULL,
    age INT,
    team INT
);


SELECT id FROM positions;