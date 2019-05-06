DROP DATABASE IF EXISTS forum;
CREATE DATABASE IF NOT EXISTS forum;
USE forum;


CREATE TABLE posts ( content TEXT,
                     time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     id SERIAL );

