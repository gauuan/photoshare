CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;
DROP TABLE IF EXISTS Photos CASCADE;
DROP TABLE IF EXISTS Users CASCADE;

CREATE TABLE Users 
(
    user_id INTEGER AUTO_INCREMENT,
    fname VARCHAR(50) NOT NULL,
    lname VARCHAR(50) NOT NULL,
    DOB DATE NOT NULL,
    gender VARCHAR(50),
    hometown VARCHAR(50),
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255),
    CONSTRAINT users_pk PRIMARY KEY (user_id)
);


CREATE TABLE Photos
(
  photo_id INTEGER AUTO_INCREMENT,
  user_id INTEGER,
  imgdata longblob,
  caption VARCHAR(255),
  INDEX upicture_id_idx (user_id),
  CONSTRAINT Photos_pk PRIMARY KEY (photo_id)
);

CREATE TABLE Albums
(
	album_id INTEGER PRIMARY KEY,
	title VARCHAR(75),
	user_id INTEGER NOT NULL,
	date_created DATE,
	FOREIGN KEY(user_id) REFERENCES
		Users(user_id) ON DELETE CASCADE

);

CREATE TABLE Tags 
(
	tag_id INTEGER PRIMARY KEY,
	tag VARCHAR(50)
);

CREATE TABLE is_tagged 
(
 	tag INTEGER,
    picture_id INTEGER NOT NULL,
    PRIMARY KEY(tag, picture_id),
    FOREIGN KEY(tag) REFERENCES
    Tags(tag_id),
    FOREIGN KEY(picture_id) REFERENCES
    	Photos(photo_id) ON DELETE CASCADE
);

CREATE TABLE liked_photos
(
	user_id INTEGER,
	liked_photo INTEGER,
	PRIMARY KEY(user_id, liked_photo),
	FOREIGN KEY(user_id) REFERENCES
		Users(user_id),
	FOREIGN KEY(liked_photo) REFERENCES
		Photos(photo_id)
);

 

CREATE TABLE are_friends
(
	user_id INTEGER NOT NULL,
	friend_id INTEGER NOT NULL,
	PRIMARY KEY(user_id, friend_id),
	FOREIGN KEY(user_id) REFERENCES
	Users(user_id),
	FOREIGN KEY(friend_id) REFERENCES
	Users(user_id),
	CHECK (user_id <> friend_id)
);

CREATE TABLE Comments
(
	cid INTEGER PRIMARY KEY,
	text VARCHAR(255),
	commenter_id INTEGER NOT NULL,
	poster_id INTEGER NOT NULL,
	picture_id INTEGER NOT NULL,
	CHECK (commenter_id <> poster_id),
	FOREIGN KEY(commenter_id) REFERENCES
		Users(user_id),
	FOREIGN KEY(poster_id) REFERENCES
		Users(user_id) ON DELETE CASCADE,
	FOREIGN KEY(picture_id) REFERENCES
		Photos(photo_id) ON DELETE CASCADE
);

INSERT INTO Users (email, password) VALUES ('test@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');
