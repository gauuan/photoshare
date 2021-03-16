CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;
DROP TABLE IF EXISTS Photos CASCADE;
DROP TABLE IF EXISTS Users CASCADE;

CREATE TABLE Users (
    user_id INTEGER NOT NULL AUTO_INCREMENT,
    fname VARCHAR(50) DEFAULT NULL,
    lname VARCHAR(50) DEFAULT NULL,
    DOB DATE DEFAULT NULL,
    gender VARCHAR(50) DEFAULT NULL,
    hometown VARCHAR(50) DEFAULT NULL,
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255) DEFAULT NULL,
    CONSTRAINT users_pk PRIMARY KEY (user_id)
);


CREATE TABLE Photos
(
  photo_id INTEGER NOT NULL AUTO_INCREMENT,
  user_id INTEGER DEFAULT NULL,
  imgdata longblob,
  caption VARCHAR(255) DEFAULT NULL,
  INDEX upicture_id_idx (user_id),
  CONSTRAINT Photos_pk PRIMARY KEY (photo_id)
);

CREATE TABLE Albums
(
	album_id INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
	title VARCHAR(75)  DEFAULT NULL,
	user_id INTEGER DEFAULT NULL, /*change to default null?*/
	date_created DATE DEFAULT(CURRENT_DATE),
	FOREIGN KEY(user_id) REFERENCES
		Users(user_id) ON DELETE CASCADE

);

CREATE TABLE Tags (
	tag_id INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
	tag VARCHAR(50) NOT NULL
);

 CREATE TABLE is_tagged 
 (
        tag_id INTEGER NOT NULL, /*should we change ot tag_id? depeneds if we need <string:tag> or <int:tag_id> constraint*/
        photo_id INTEGER NOT NULL,
        PRIMARY KEY(tag_id, photo_id),
        FOREIGN KEY(tag_id) REFERENCES
            Tags(tag_id),/*if change to tag_id, need to change this*/
        FOREIGN KEY(photo_id) REFERENCES
            Photos(photo_id) ON DELETE CASCADE
    );

CREATE TABLE liked_photos
(
	user_id INTEGER NOT NULL,
	liked_photo INTEGER NOT NULL,
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
	cid INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY, /*required*/
	text VARCHAR(255) NOT NULL, /*required*/
	commenter_id INTEGER NOT NULL, /*required*/
	date_commented DATE DEFAULT(CURRENT_DATE),
	poster_id INTEGER DEFAULT NULL,
	photo_id INTEGER NOT NULL,
	CHECK (commenter_id <> poster_id),
	FOREIGN KEY(commenter_id) REFERENCES
		Users(user_id),
	FOREIGN KEY(poster_id) REFERENCES
		Users(user_id) ON DELETE CASCADE,
	FOREIGN KEY(photo_id) REFERENCES
		Photos(photo_id) ON DELETE CASCADE
);

INSERT INTO Users (email, password) VALUES ('test@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');
