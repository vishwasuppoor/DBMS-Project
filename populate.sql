CREATE TABLE user (
	type ENUM("admin", "owner", "visitor"), 
	password CHAR(44), 
	email VARCHAR(100) NOT NULL UNIQUE, 
	username VARCHAR(100) NOT NULL UNIQUE, 

	PRIMARY KEY(email)
) ENGINE = InnoDB;

CREATE TABLE property (
	address VARCHAR(100), 
	size NUMERIC(8, 5), 
	zip VARCHAR(5), 
	id INT NOT NULL UNIQUE AUTO_INCREMENT, 
	type ENUM("farm", "orchard", "garden"), 
	is_public BOOLEAN, 
	owned_by VARCHAR(100), 
	approved_by VARCHAR(100), 
	city VARCHAR(100), 
	is_commercial BOOLEAN, 
	name VARCHAR(100) NOT NULL UNIQUE, 
	
	FOREIGN KEY (owned_by) REFERENCES user(email) 
		ON UPDATE CASCADE 
		ON DELETE CASCADE, 

	FOREIGN KEY (approved_by) REFERENCES user(email) 
		ON UPDATE CASCADE 
		ON DELETE SET NULL, 

	PRIMARY KEY(id)
) ENGINE = InnoDB;

ALTER TABLE property AUTO_INCREMENT=10001;

CREATE TABLE item (
	category ENUM("animal", "fruit", "nut", "flower", "vegetable"), 
	approved_by VARCHAR(100), 
	name VARCHAR(100) NOT NULL UNIQUE, 

	FOREIGN KEY (approved_by) REFERENCES user(email) 
		ON UPDATE CASCADE 
		ON DELETE SET NULL, 
		
	PRIMARY KEY(name)
) ENGINE = InnoDB;

CREATE TABLE has (
	property_id INT NOT NULL, 
	item_name VARCHAR(100) NOT NULL, 

	FOREIGN KEY (property_id) REFERENCES property(id) 
		ON UPDATE CASCADE 
		ON DELETE CASCADE, 

	FOREIGN KEY (item_name) REFERENCES item(name) 
		ON UPDATE CASCADE 
		ON DELETE CASCADE, 

	PRIMARY KEY(property_id, item_name)
) ENGINE = InnoDB;

CREATE TABLE visits (
	property_id INT NOT NULL, 
	user_email VARCHAR(100) NOT NULL, 
	rating NUMERIC(5, 0), 
	date DATE, 

	FOREIGN KEY (property_id) REFERENCES property(id) 
		ON UPDATE CASCADE 
		ON DELETE CASCADE, 

	FOREIGN KEY (user_email) REFERENCES user(email) 
		ON UPDATE CASCADE 
		ON DELETE CASCADE, 

	PRIMARY KEY(property_id, user_email)
) ENGINE = InnoDB;
