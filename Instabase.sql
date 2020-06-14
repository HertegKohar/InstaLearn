
CREATE TABLE insta_train(
	username VARCHAR(30) PRIMARY KEY,
	posts INT,
	followers INT,
	following INT,
	private BOOLEAN,
	bio_tag BOOLEAN,
	external_url BOOLEAN,
	verified BOOLEAN
	);

SHOW TABLES;

#View all rows
SELECT * FROM insta_train;

#Count the rows
SELECT COUNT(*) FROM insta_train;

#Show the variables of the table
DESCRIBE insta_train;




