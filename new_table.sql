CREATE TABLE ONION_ADDRS (
    id int(11) NOT NULL AUTO_INCREMENT,
    onion_addr varchar(16) NOT NULL UNIQUE,
    scanned tinyint(1) NOT NULL DEFAULT 0,
    active tinyint(1) NOT NULL DEFAULT 0,
    PRIMARY KEY (id)
) ENGINE=InnoDB
