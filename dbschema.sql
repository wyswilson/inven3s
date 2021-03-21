
-- Dumping database structure for inven3s
CREATE DATABASE IF NOT EXISTS `inven3s` /*!40100 DEFAULT CHARACTER SET latin1 */;
USE `inven3s`;

-- Dumping structure for table inven3s.logsapi
CREATE TABLE IF NOT EXISTS `logsapi` (
  `endpoint` varchar(100) NOT NULL,
  `clientip` varchar(100) NOT NULL,
  `eventdate` datetime NOT NULL,
  `browser` varchar(250) DEFAULT NULL,
  `platform` varchar(250) DEFAULT NULL,
  `language` varchar(250) DEFAULT NULL,
  `referrer` varchar(250) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


-- Dumping structure for table inven3s.brands
CREATE TABLE IF NOT EXISTS `brands` (
  `brandid` varchar(10) NOT NULL,
  `brandname` varchar(255) NOT NULL,
  `brandimage` varchar(255) DEFAULT NULL,
  `brandurl` varchar(255) DEFAULT NULL,
  `brandowner` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`brandid`),
  FULLTEXT KEY `FULLTEXT` (`brandname`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- Dumping structure for table inven3s.cities
CREATE TABLE IF NOT EXISTS `cities` (
  `cityid` int(11) NOT NULL AUTO_INCREMENT,
  `cityname` char(35) NOT NULL DEFAULT '',
  `countrycode` char(3) NOT NULL DEFAULT '',
  `district` char(20) NOT NULL DEFAULT '',
  `population` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`cityid`),
  KEY `CountryCode` (`countrycode`),
  CONSTRAINT `cities_ibfk_1` FOREIGN KEY (`countrycode`) REFERENCES `countries` (`countrycode`)
) ENGINE=InnoDB AUTO_INCREMENT=4085 DEFAULT CHARSET=latin1;


-- Dumping structure for table inven3s.countries
CREATE TABLE IF NOT EXISTS `countries` (
  `countrycode` char(3) NOT NULL DEFAULT '',
  `countryname` char(52) NOT NULL DEFAULT '',
  `continent` enum('Asia','Europe','North America','Africa','Oceania','Antarctica','South America','Unavailable') NOT NULL DEFAULT 'Asia',
  `region` char(26) NOT NULL DEFAULT '',
  `surfacearea` float(10,2) NOT NULL DEFAULT '0.00',
  `indyear` smallint(6) DEFAULT NULL,
  `population` int(11) NOT NULL DEFAULT '0',
  `lifeexp` float(3,1) DEFAULT NULL,
  `gnp` float(10,2) DEFAULT NULL,
  `gnpold` float(10,2) DEFAULT NULL,
  `localname` char(45) NOT NULL DEFAULT '',
  `govform` char(45) NOT NULL DEFAULT '',
  `headofstate` char(60) DEFAULT NULL,
  `capital` int(11) DEFAULT NULL,
  `code2` char(2) NOT NULL DEFAULT '',
  PRIMARY KEY (`countrycode`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


-- Dumping structure for table inven3s.inventories
CREATE TABLE IF NOT EXISTS `inventories` (
  `entryid` int(11) NOT NULL AUTO_INCREMENT,
  `userid` varchar(50) NOT NULL,
  `gtin` varchar(20) NOT NULL,
  `retailerid` varchar(50) NOT NULL,
  `dateentry` datetime NOT NULL,
  `itemstatus` varchar(5) NOT NULL DEFAULT 'IN',
  `dateexpiry` date NOT NULL DEFAULT '0000-00-00',
  `quantity` float NOT NULL DEFAULT '1',
  `receiptno` varchar(150) DEFAULT NULL,
  PRIMARY KEY (`entryid`) USING BTREE,
  KEY `FK_inventory_products` (`gtin`),
  KEY `FK_inventory_retailers` (`retailerid`),
  KEY `FK_inventory_users` (`userid`) USING BTREE,
  CONSTRAINT `FK_inventories_products` FOREIGN KEY (`gtin`) REFERENCES `products` (`gtin`),
  CONSTRAINT `FK_inventories_retailers` FOREIGN KEY (`retailerid`) REFERENCES `retailers` (`retailerid`),
  CONSTRAINT `FK_inventories_users` FOREIGN KEY (`userid`) REFERENCES `users` (`userid`)
) ENGINE=InnoDB AUTO_INCREMENT=446905 DEFAULT CHARSET=utf8mb4;


-- Dumping structure for table inven3s.products
CREATE TABLE IF NOT EXISTS `products` (
  `gtin` varchar(20) NOT NULL,
  `productname` varchar(255) NOT NULL,
  `productimage` varchar(255) DEFAULT NULL,
  `brandid` varchar(10) NOT NULL,
  `isperishable` int(11) NOT NULL DEFAULT '0',
  `isedible` int(11) NOT NULL DEFAULT '1',
  PRIMARY KEY (`gtin`),
  KEY `FK_products_brands` (`brandid`),
  FULLTEXT KEY `FULLTEXT` (`gtin`,`productname`),
  CONSTRAINT `FK_products_brands` FOREIGN KEY (`brandid`) REFERENCES `brands` (`brandid`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- Dumping structure for table inven3s.productscandidate
CREATE TABLE IF NOT EXISTS `productscandidate` (
  `gtin` varchar(20) NOT NULL,
  `source` varchar(20) NOT NULL,
  `candidateid` varchar(50) NOT NULL,
  `candidatetitle` varchar(255) NOT NULL,
  `candidateurl` text NOT NULL,
  `candidaterank` int(11) NOT NULL,
  `type` varchar(20) NOT NULL,
  `timestamp` datetime DEFAULT NULL,
  PRIMARY KEY (`gtin`,`candidateid`,`source`),
  FULLTEXT KEY `FULLTEXT` (`candidatetitle`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- Dumping structure for table inven3s.productscategory
CREATE TABLE IF NOT EXISTS `productscategory` (
  `gtin` varchar(20) CHARACTER SET utf8mb4 NOT NULL,
  `category` varchar(200) CHARACTER SET utf8mb4 NOT NULL,
  `confidence` float NOT NULL,
  `status` varchar(10) CHARACTER SET utf8mb4 NOT NULL,
  PRIMARY KEY (`gtin`,`category`),
  CONSTRAINT `FK_productscategory_products` FOREIGN KEY (`gtin`) REFERENCES `products` (`gtin`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


-- Dumping structure for table inven3s.productscategory_top
CREATE TABLE IF NOT EXISTS `productscategory_top` (
  `category` varchar(200) CHARACTER SET utf8mb4 NOT NULL,
  `subcategorycnt` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


-- Dumping structure for table inven3s.productscategory_transpose
CREATE TABLE IF NOT EXISTS `productscategory_transpose` (
  `gtin` varchar(20) CHARACTER SET utf8mb4 NOT NULL,
  `productname` varchar(255) CHARACTER SET utf8mb4 NOT NULL,
  `category1` varchar(200) CHARACTER SET utf8mb4 NOT NULL,
  `category2` varchar(200) CHARACTER SET utf8mb4 DEFAULT NULL,
  PRIMARY KEY (`gtin`),
  CONSTRAINT `FK_productscategory_transpose_products` FOREIGN KEY (`gtin`) REFERENCES `products` (`gtin`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


-- Dumping structure for table inven3s.productsfavourite
CREATE TABLE IF NOT EXISTS `productsfavourite` (
  `gtin` varchar(20) CHARACTER SET utf8mb4 NOT NULL,
  `userid` varchar(50) CHARACTER SET utf8mb4 NOT NULL,
  `favourite` int(11) DEFAULT '0',
  PRIMARY KEY (`gtin`,`userid`),
  CONSTRAINT `FK_productsfavourite_products` FOREIGN KEY (`gtin`) REFERENCES `products` (`gtin`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


-- Dumping structure for table inven3s.productsprice
CREATE TABLE IF NOT EXISTS `productsprice` (
  `gtin` varchar(20) CHARACTER SET utf8mb4 NOT NULL,
  `price` float NOT NULL,
  `timestamp` datetime NOT NULL,
  `date` date NOT NULL,
  `retailer` varchar(100) CHARACTER SET utf8mb4 NOT NULL,
  PRIMARY KEY (`gtin`,`date`,`retailer`),
  CONSTRAINT `FK_productsprice_products` FOREIGN KEY (`gtin`) REFERENCES `products` (`gtin`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


-- Dumping structure for table inven3s.retailers
CREATE TABLE IF NOT EXISTS `retailers` (
  `retailerid` varchar(50) NOT NULL,
  `retailername` varchar(255) NOT NULL,
  `retailercity` int(11) NOT NULL,
  PRIMARY KEY (`retailerid`),
  KEY `FK_retailers_cities` (`retailercity`),
  FULLTEXT KEY `FULLTEXT` (`retailername`),
  CONSTRAINT `FK_retailers_cities` FOREIGN KEY (`retailercity`) REFERENCES `cities` (`cityid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;



-- Dumping structure for table inven3s.users
CREATE TABLE IF NOT EXISTS `users` (
  `userid` varchar(50) NOT NULL,
  `fullname` varchar(250) NOT NULL,
  `email` varchar(100) NOT NULL,
  `passwordhashed` varchar(250) NOT NULL,
  PRIMARY KEY (`userid`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;