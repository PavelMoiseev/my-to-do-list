CREATE TABLE IF NOT EXISTS mainmenu (
id integer PRIMARY KEY AUTOINCREMENT,
title text NOT NULL,
url text NOT NULL,
UNIQUE  (title, url)
);

INSERT OR IGNORE INTO mainmenu (title, url)
VALUES
("Регистрация", "/register"),
("Авторизация", "/login"),
("Главная страница", "/");

CREATE TABLE IF NOT EXISTS users (
user_id integer PRIMARY KEY AUTOINCREMENT,
name text NOT NULL,
email text NOT NULL,
psw text NOT NULL,
avatar BLOB DEFAULT NULL,
time integer NOT NULL
);

CREATE TABLE IF NOT EXISTS todo (
todo_id integer PRIMARY KEY AUTOINCREMENT,
user_id integer NOT NULL,
title text NOT NULL,
is_complete BLOB DEFAULT NULL,
FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE CASCADE
);
