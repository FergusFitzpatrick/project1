CREATE TABLE books(
    id SERIAL PRIMARY KEY,
    isbn VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    year INTEGER NOT NULL
);

CREATE TABLE users(
    id SERIAL PRIMARY KEY,
    firstname VARCHAR NOT NULL,
    lastname VARCHAR NOT NULL,
    username VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    password VARCHAR(255) NOT NULL,
    UNIQUE(username)
);

CREATE TABLE reviews (
  id SERIAL PRIMARY KEY,
  review VARCHAR NOT NULL,
  books_id INTEGER REFERENCES books,
  user_id INTEGER REFERENCES users,
  rating INTEGER NOT NULL
);
