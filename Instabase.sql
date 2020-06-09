
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

#Show the variabels of the table
DESCRIBE insta_train;

#Export to csv
SELECT * FROM insta_train 
INTO OUTFILE 'C:/Users/herte/cp104/ws/Instabot/src/InstaData.csv' 
FIELDS ENCLOSED BY '"' 
TERMINATED BY ';'
ESCAPED BY '"'
LINES TERMINATED BY '\r\n';

SELECT * FROM insta_train
WHERE username='gackt___u';

