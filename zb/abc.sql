-- MySQL dump 10.14  Distrib 5.5.60-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: DYDB
-- ------------------------------------------------------
-- Server version	5.5.60-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `cktb`
--

DROP TABLE IF EXISTS `cktb`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cktb` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `nn` varchar(60) NOT NULL,
  `pwd` varchar(20) NOT NULL,
  `attr` varchar(10) NOT NULL,
  `level` int(3) DEFAULT NULL,
  `bind` varchar(10) NOT NULL,
  `vaild` varchar(20) NOT NULL,
  `cookie` text NOT NULL,
  `signup_date` date DEFAULT NULL,
  `signup_time` time DEFAULT NULL,
  `update_date` date DEFAULT NULL,
  `update_time` time DEFAULT NULL,
  `first_r_ip` varchar(20) DEFAULT NULL,
  `first_r_loc` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cktb`
--

LOCK TABLES `cktb` WRITE;
/*!40000 ALTER TABLE `cktb` DISABLE KEYS */;
INSERT INTO `cktb` VALUES (9,'甜乚心FG少女','sel81563','New',5,'有','有效','dy_did=81f0af294dd4d7e4f3f18ead00001501;acf_ccn=0f61fb5d309181aa6aa1f4cb7219b77a;PHPSESSID=leju1vm24g46e4kk6i5cd7lt41;acf_auth=e944TE028bhJru7Y%2FPJz97bj85ADWYq39nbRBQg28Fkx4xlB24Tjg9%2BgwKtsSYTB5oYgA8IlXNY%2BHd5RaUtd%2FxeAaooqkUVx5H9ceX2LvqrduOrvxKLa2HI;wan_auth37wan=49b547be1235Zldnb5PsdeXsearejhQRuHM1dQ0O7f9C%2FcSGlg9jbGJMsYPXrjTpJqZSSuxy%2BzpyJsi7L5cIZx55OQsHw7P5ABE5hje0bbAjXSflyXw;acf_uid=224242904;acf_username=224242904;acf_nickname=%E7%94%9C%E4%B9%9A%E5%BF%83FG%E5%B0%91%E5%A5%B3;acf_own_room=0;acf_groupid=1;acf_phonestatus=1;acf_avatar=https%3A%2F%2Fapic.douyucdn.cn%2Fupload%2Favatar%2Fdefault%2F03_;acf_ct=0;acf_ltkid=28566031;acf_biz=1;acf_stk=fb8388e3033b3959;acf_devid=de5dc8112942b23c903ee4639f7b9be6','2019-01-04','09:08:06','2019-01-03','10:11:12',NULL,NULL),(10,'xiao','nps46955','Old',8,'无','无效','134dfdv32fdvfdfd','2019-01-02','15:02:03','2019-01-07','14:26:54',NULL,NULL),(11,'甜乚心FG少女','sel81563','New',2,'无','有效','dy_did=81f0af294dd4d7e4f3f18ead00001501;acf_ccn=0f61fb5d309181aa6aa1f4cb7219b77a;PHPSESSID=leju1vm24g46e4kk6i5cd7lt41;acf_auth=e944TE028bhJru7Y%2FPJz97bj85ADWYq39nbRBQg28Fkx4xlB24Tjg9%2BgwKtsSYTB5oYgA8IlXNY%2BHd5RaUtd%2FxeAaooqkUVx5H9ceX2LvqrduOrvxKLa2HI;wan_auth37wan=49b547be1235Zldnb5PsdeXsearejhQRuHM1dQ0O7f9C%2FcSGlg9jbGJMsYPXrjTpJqZSSuxy%2BzpyJsi7L5cIZx55OQsHw7P5ABE5hje0bbAjXSflyXw;acf_uid=224242904;acf_username=224242904;acf_nickname=%E7%94%9C%E4%B9%9A%E5%BF%83FG%E5%B0%91%E5%A5%B3;acf_own_room=0;acf_groupid=1;acf_phonestatus=1;acf_avatar=https%3A%2F%2Fapic.douyucdn.cn%2Fupload%2Favatar%2Fdefault%2F03_;acf_ct=0;acf_ltkid=28566031;acf_biz=1;acf_stk=fb8388e3033b3959;acf_devid=de5dc8112942b23c903ee4639f7b9be6','2019-01-04','09:08:06','2019-01-03','10:11:12',NULL,NULL),(12,'开车老司机YZ','nps46955','Old',10,'有','无效','dy_did=3289f9f884d9a8569aa8efb500001501;acf_ccn=9c77baed195a1e8b0c0cf6c62a6fd7a0;PHPSESSID=rs0pk28fje6f3q9atcjiq2veq5;acf_auth=283eHOqKcbFr7sovvrcAMA0%2FsrFmjlLY61NHdJJ9CfEgAtKy2ZwtMe7mi3jyqBCu4YqIIMWNP8ioXCI6leJmpqQvw%2B%2B1ZoKF5sBi%2BVl%2BKMDlcOHDzNKZoqI;wan_auth37wan=8d1abf005ba3QGu%2BP4s8vCvIRkterBAUhtfekTNa%2BksfZprZgbIMoN7pVD4GzGEGO2O6SjpjovoVsXuxzJhArtEeYYAzsyBoIKyK5L3Z2pefQulIves;acf_uid=224243244;acf_username=224243244;acf_nickname=%E5%BC%80%E8%BD%A6%E8%80%81%E5%8F%B8%E6%9C%BAYZ;acf_own_room=0;acf_groupid=1;acf_phonestatus=1;acf_avatar=https%3A%2F%2Fapic.douyucdn.cn%2Fupload%2Favatar%2Fdefault%2F07_;acf_ct=0;acf_ltkid=40623626;acf_biz=1;acf_stk=098c8ac2ce9299b4;acf_devid=6d5e77da4a0e2aaa5595bc67771f3ca8','2019-01-02','15:02:03','2019-01-01','18:01:22',NULL,NULL),(13,'gao','123456','',NULL,'','','134dfdv32fdvfdfd',NULL,NULL,NULL,NULL,NULL,NULL),(14,'bao','123456','',NULL,'','','134dfdv32fdvfdfd','2019-01-06','17:12:15',NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `cktb` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-01-08 16:41:37
