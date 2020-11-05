-- MySQL dump 10.13  Distrib 8.0.22, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: projectdb
-- ------------------------------------------------------
-- Server version	8.0.22

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `schedule`
--

DROP TABLE IF EXISTS `schedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `schedule` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sid` int DEFAULT NULL,
  `Day` text,
  `Time` text,
  `chkId` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `sid` (`sid`),
  CONSTRAINT `schedule_ibfk_1` FOREIGN KEY (`sid`) REFERENCES `students` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=68 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `schedule`
--

LOCK TABLES `schedule` WRITE;
/*!40000 ALTER TABLE `schedule` DISABLE KEYS */;
INSERT INTO `schedule` VALUES (24,1,'Sunday','23:00-24:00',160),(25,1,'Thursday','04:00-05:00',24),(27,1,'Sunday','14:00-15:00',97),(29,1,'Thursday','14:00-15:00',94),(38,1,'Tuesday','04:00-05:00',22),(40,1,'Wednesday','05:00-06:00',30),(41,1,'Tuesday','05:00-06:00',29),(42,1,'Tuesday','07:00-08:00',43),(43,1,'Wednesday','07:00-08:00',44),(44,1,'Sunday','08:00-09:00',55),(45,1,'Saturday','05:00-06:00',33),(46,1,'Saturday','07:00-08:00',47),(47,1,'Friday','08:00-09:00',53),(48,1,'Friday','09:00-10:00',60),(49,1,'Thursday','10:00-11:00',66),(50,1,'Monday','09:00-10:00',56),(51,1,'Thursday','13:00-14:00',87),(52,1,'Tuesday','15:00-16:00',99),(53,1,'Monday','10:00-11:00',63),(55,1,'Wednesday','11:00-12:00',72),(56,1,'Thursday','11:00-12:00',73),(57,1,'Friday','17:00-18:00',116),(58,1,'Tuesday','19:00-20:00',127),(59,1,'Tuesday','18:00-19:00',120),(60,1,'Wednesday','20:00-21:00',135),(61,1,'Thursday','22:00-23:00',150),(62,1,'Monday','21:00-22:00',140),(63,1,'Thursday','06:00-07:00',38),(64,1,'Thursday','02:00-03:00',10),(65,1,'Wednesday','02:00-03:00',9),(66,1,'Monday','04:00-05:00',21);
/*!40000 ALTER TABLE `schedule` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-11-05 16:44:18
