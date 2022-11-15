use metadata;
CREATE TABLE vehicle(
    vehicle  varchar(50) not null,
    model    varchar(50),
    make   INT,
    date_created timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(vehicle)
) ENGINE=INNODB;
CREATE TABLE files_inprocess(
    file_id INT NOT NULL AUTO_INCREMENT,
    file_name  varchar(50) not null,
    vehicle varchar(50),
    processed BOOLEAN,
    date_created timestamp DEFAULT CURRENT_TIMESTAMP,
    date_updated timestamp ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY(file_id),
  CONSTRAINT file_name_uniq_index UNIQUE (file_name)
) ENGINE=INNODB;
CREATE TABLE files_failed(
    file_id INT NOT NULL AUTO_INCREMENT,
    file_name  varchar(50) not null,
    vehicle varchar(50),
    processed BOOLEAN,
    date_created timestamp DEFAULT CURRENT_TIMESTAMP,
    date_updated timestamp ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY(file_id),
  CONSTRAINT file_name_uniq_index UNIQUE (file_name)
) ENGINE=INNODB;
CREATE TABLE metadata(
    id INT NOT NULL ,
    metadata  json ,
  PRIMARY KEY(id)
) ENGINE=INNODB;
 CREATE TABLE upload_failure_log (
  id INT NOT NULL AUTO_INCREMENT,
  file_id INT NOT NULL,
  exit_status tinyint(1) DEFAULT NULL,
  stdout VARCHAR(250),
  stderr VARCHAR(250),
  date_created timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE=InnoDB;
