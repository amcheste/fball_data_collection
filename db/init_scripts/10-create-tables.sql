CREATE TABLE positions (
    id INT PRIMARY KEY NOT NULL,
    name VARCHAR(255),
    abbreviation VARCHAR(10),
    url VARCHAR(255) NOT NULL
);

CREATE TABLE teams (
    id INT PRIMARY KEY NOT NULL,
    name VARCHAR(255),
    abbreviation VARCHAR(10),
    location VARCHAR(255),
    url VARCHAR(255) NOT NULL
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
    team INT,
    url VARCHAR(255) NOT NULL
);

CREATE TYPE commands AS ENUM ('DISCOVER', 'COLLECT');
CREATE TYPE data_types AS ENUM('positions', 'teams', 'players');
CREATE TYPE status AS ENUM ('ACCEPTED', 'IN_PROGRESS', 'COMPLETED', 'FAILED');

CREATE TABLE tasks(
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    command commands NOT NULL,
    data_type data_types NOT NULL,
    status status NOT NULL DEFAULT 'ACCEPTED',
    time_created timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    time_modified timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- TODO make one table and add a column for data type?
CREATE TABLE position_collection(
    id INT PRIMARY KEY NOT NULL,
    task_id uuid REFERENCES tasks(id),
    url VARCHAR(255) NOT NULL,
    status status NOT NULL DEFAULT 'ACCEPTED'
);

CREATE TABLE team_collection(
    id INT PRIMARY KEY NOT NULL,
    task_id uuid REFERENCES tasks(id),
    url VARCHAR(255) NOT NULL,
    status status NOT NULL DEFAULT 'ACCEPTED'
);

CREATE TABLE player_collection(
    id INT PRIMARY KEY NOT NULL,
    task_id uuid REFERENCES tasks(id),
    url VARCHAR(255) NOT NULL,
    status status NOT NULL DEFAULT 'ACCEPTED'
);

CREATE TABLE player_stats(
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(), -- is this needed?
    --player_id INT REFERENCES players(id),
    player_id INT NOT NULL,
    season_id INT NOT NULL,
    type VARCHAR(255) NOT NULL,
    category VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    value FLOAT NOT NULL,
    perGameValue FLOAT,
    rank INT
);