-- MySQL dump 10.13  Distrib 5.7.10, for osx10.9 (x86_64)
--
-- Host: localhost    Database: dydb
-- ------------------------------------------------------
-- Server version	5.7.10

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
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '用户id',
  `uid` mediumint(8) unsigned NOT NULL DEFAULT '0' COMMENT '用户id',
  `nickname` char(20) NOT NULL DEFAULT '' COMMENT '昵称',
  `password` char(32) NOT NULL DEFAULT '' COMMENT '密码',
  `grp` char(32) NOT NULL DEFAULT 'G0',
  `ratio` float NOT NULL DEFAULT '1',
  `regdate` int(10) unsigned NOT NULL COMMENT '注册时间',
  `lastdate` int(11) NOT NULL DEFAULT '0' COMMENT '最后一次更新时间',
  `colddate` int(11) NOT NULL DEFAULT '0' COMMENT '冷却时间',
  `lastip` char(15) NOT NULL DEFAULT '' COMMENT '最后一次取用ip',
  `usednum` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '取用次数',
  `cookie` text NOT NULL COMMENT 'cookie',
  `update_fail` int(10) unsigned NOT NULL DEFAULT '0' COMMENT 'cookie 更新失败次数',
  `old` tinyint(1) DEFAULT '0' COMMENT '账号熟悉，1表示旧账号，0表示新账号',
  PRIMARY KEY (`id`),
  UNIQUE KEY `nickname` (`nickname`) USING BTREE
) ENGINE=MyISAM AUTO_INCREMENT=10726 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cktb`
--

LOCK TABLES `cktb` WRITE;
/*!40000 ALTER TABLE `cktb` DISABLE KEYS */;
/*!40000 ALTER TABLE `cktb` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `custb`
--

DROP TABLE IF EXISTS `custb`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `custb` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `ctime` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `note` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `custb`
--

LOCK TABLES `custb` WRITE;
/*!40000 ALTER TABLE `custb` DISABLE KEYS */;
INSERT INTO `custb` VALUES (2,'小哥','2019-05-23 04:56:00','客户小哥'),(3,'roy','2019-05-23 08:42:00','roy');
/*!40000 ALTER TABLE `custb` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `grptb`
--

DROP TABLE IF EXISTS `grptb`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `grptb` (
  `id` int(1) NOT NULL AUTO_INCREMENT,
  `name` varchar(20) NOT NULL,
  `supplier` varchar(20) DEFAULT NULL,
  `ltime` timestamp NULL DEFAULT NULL,
  `ltask` int(11) DEFAULT NULL,
  `ctime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `utime` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `ttime` timestamp NULL DEFAULT NULL,
  `number` int(1) DEFAULT NULL,
  `active` int(11) DEFAULT NULL,
  `rratio` float DEFAULT NULL,
  `cratio` float unsigned DEFAULT '1',
  `rrenqi` int(11) DEFAULT NULL,
  `crenqi` int(11) DEFAULT NULL,
  `note` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grptb`
--

LOCK TABLES `grptb` WRITE;
/*!40000 ALTER TABLE `grptb` DISABLE KEYS */;
INSERT INTO `grptb` VALUES (33,'111','德山',NULL,NULL,'2019-05-23 06:35:23',NULL,NULL,10725,NULL,1,NULL,10725,NULL,'测试账号');
/*!40000 ALTER TABLE `grptb` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ordtb`
--

DROP TABLE IF EXISTS `ordtb`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ordtb` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `custom` varchar(255) DEFAULT NULL,
  `platform` varchar(255) DEFAULT NULL,
  `room_id` varchar(255) DEFAULT NULL,
  `order_type` varchar(255) DEFAULT NULL,
  `renqi` int(11) DEFAULT NULL,
  `income` int(11) DEFAULT NULL,
  `ctime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `sdate` date DEFAULT NULL,
  `edate` date DEFAULT NULL,
  `note` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ordtb`
--

LOCK TABLES `ordtb` WRITE;
/*!40000 ALTER TABLE `ordtb` DISABLE KEYS */;
INSERT INTO `ordtb` VALUES (4,NULL,'小哥','小哥','douyu','118087','renqi',1000,0,'2019-05-23 04:58:05','2019-05-23','2019-05-23','2222');
/*!40000 ALTER TABLE `ordtb` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role`
--

DROP TABLE IF EXISTS `role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role`
--

LOCK TABLES `role` WRITE;
/*!40000 ALTER TABLE `role` DISABLE KEYS */;
INSERT INTO `role` VALUES (1,'user',NULL),(2,'superuser',NULL);
/*!40000 ALTER TABLE `role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles_users`
--

DROP TABLE IF EXISTS `roles_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `roles_users` (
  `user_id` int(11) DEFAULT NULL,
  `role_id` int(11) DEFAULT NULL,
  KEY `user_id` (`user_id`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `roles_users_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
  CONSTRAINT `roles_users_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles_users`
--

LOCK TABLES `roles_users` WRITE;
/*!40000 ALTER TABLE `roles_users` DISABLE KEYS */;
INSERT INTO `roles_users` VALUES (1,1),(1,2),(2,1),(27,1);
/*!40000 ALTER TABLE `roles_users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `suptb`
--

DROP TABLE IF EXISTS `suptb`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `suptb` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` char(20) NOT NULL,
  `ctime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `note` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `suptb`
--

LOCK TABLES `suptb` WRITE;
/*!40000 ALTER TABLE `suptb` DISABLE KEYS */;
INSERT INTO `suptb` VALUES (5,'德山','2019-05-23 04:29:00','测试供应商');
/*!40000 ALTER TABLE `suptb` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `task`
--

DROP TABLE IF EXISTS `task`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `task` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT 'id',
  `user_id` mediumint(8) unsigned NOT NULL DEFAULT '0' COMMENT '用户id',
  `task_id` char(32) NOT NULL DEFAULT '' COMMENT '任务ID',
  `effective` mediumint(8) unsigned NOT NULL DEFAULT '0' COMMENT '任务有效的标志位，0表示无效，1表示有效',
  `reset_done` mediumint(8) unsigned NOT NULL DEFAULT '0' COMMENT '任务开始前，重置ck标志位',
  `submit_time` char(32) NOT NULL DEFAULT '' COMMENT '任务提交时间',
  `begin_timestamp` int(10) unsigned NOT NULL COMMENT '任务开始的时间戳',
  `total_time` mediumint(8) unsigned NOT NULL DEFAULT '0' COMMENT '任务总时间，单位为分钟',
  `last_time_from` mediumint(8) unsigned NOT NULL DEFAULT '0' COMMENT '任务持续开始时间，单位为分钟',
  `last_time_to` mediumint(8) unsigned NOT NULL DEFAULT '0' COMMENT '任务持续结束时间，单位为分钟',
  `time_gap` mediumint(8) unsigned NOT NULL DEFAULT '0' COMMENT '放量时间间隔，单位为秒',
  `gap_num` mediumint(8) unsigned NOT NULL DEFAULT '0' COMMENT '放量间隔次数',
  `user_num` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '需求终端用户数量',
  `req` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '已经请求任务的终端用户数量',
  `ck_req` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '已经请求的ck的终端用户数量',
  `ck_url` char(128) NOT NULL DEFAULT '' COMMENT '获取ck的url链接',
  `room_url` char(128) NOT NULL DEFAULT '' COMMENT '房间url链接',
  `content` char(255) NOT NULL DEFAULT '' COMMENT '组装返回给终端的任务内容',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `task`
--

LOCK TABLES `task` WRITE;
/*!40000 ALTER TABLE `task` DISABLE KEYS */;
INSERT INTO `task` VALUES (1,0,'user000000',1,0,'05-05 21:56:15',1554472571,30,23,25,6,100,10000,0,0,'http://47.244.4.117:8200/useradmin/cookie?user=0&id=user000000','https://www.douyu.com/657158','<t a=\"1800|20\" flash=\"1\" isBoot=\"0\" ckul=http://47.244.4.117:8200/useradmin/cookie?user=0&id=user000000 s=https://www.douyu.com/657158><p a=\"1380,1500|0|0|5\" /></t>'),(2,0,'user000000',1,0,'05-05 22:17:29',1554473845,30,23,25,6,100,10000,0,0,'http://47.244.4.117:8200/useradmin/cookie?user=0&id=user000000','https://www.douyu.com/657158','<t a=\"1800|20\" flash=\"1\" isBoot=\"0\" ckul=http://47.244.4.117:8200/useradmin/cookie?user=0&id=user000000 s=https://www.douyu.com/657158><p a=\"1380,1500|0|0|5\" /></t>'),(3,0,'user000003',1,0,'05-22 12:04:40',1553054668,30,23,25,6,100,10000,0,0,'http://47.244.4.117:8200/useradmin/cookie?user=0&id=user000003','https://www.douyu.com/657158','<t a=\"1800|20\" flash=\"1\" isBoot=\"0\" ckul=http://47.244.4.117:8200/useradmin/cookie?user=0&id=user000003 s=https://www.douyu.com/657158><p a=\"1380,1500|0|0|5\" /></t>'),(4,0,'user000001',1,0,'05-22 12:04:15',1555905851,30,23,25,6,100,10000,0,0,'http://47.244.4.117:8200/useradmin/cookie?user=0&id=user000001','https://www.douyu.com/657158','<t a=\"1800|20\" flash=\"1\" isBoot=\"0\" ckul=http://47.244.4.117:8200/useradmin/cookie?user=0&id=user000001 s=https://www.douyu.com/657158><p a=\"1380,1500|0|0|5\" /></t>'),(5,0,'user000002',1,0,'05-22 12:04:21',1558238656,30,23,25,6,100,10000,0,0,'http://47.244.4.117:8200/useradmin/cookie?user=0&id=user000002','https://www.douyu.com/657158','<t a=\"1800|20\" flash=\"1\" isBoot=\"0\" ckul=http://47.244.4.117:8200/useradmin/cookie?user=0&id=user000002 s=https://www.douyu.com/657158><p a=\"1380,1500|0|0|5\" /></t>'),(6,0,'user000000',1,0,'05-22 12:04:09',1558325070,30,23,25,6,100,10000,0,0,'http://47.244.4.117:8200/useradmin/cookie?user=0&id=user000000','https://www.douyu.com/657158','<t a=\"1800|20\" flash=\"1\" isBoot=\"0\" ckul=http://47.244.4.117:8200/useradmin/cookie?user=0&id=user000000 s=https://www.douyu.com/657158><p a=\"1380,1500|0|0|5\" /></t>'),(7,0,'user000003',1,0,'05-22 12:17:46',1557980260,30,23,25,6,100,10000,0,0,'http://47.244.4.117:8200/useradmin/cookie?user=0&id=user000003','https://www.douyu.com/657158','<t a=\"1800|20\" flash=\"1\" isBoot=\"0\" ckul=http://47.244.4.117:8200/useradmin/cookie?user=0&id=user000003 s=https://www.douyu.com/657158><p a=\"1380,1500|0|0|5\" /></t>'),(8,0,'user000002',1,0,'05-22 12:17:32',1558239448,30,23,25,6,100,10000,0,0,'http://47.244.4.117:8200/useradmin/cookie?user=0&id=user000002','https://www.douyu.com/657158','<t a=\"1800|20\" flash=\"1\" isBoot=\"0\" ckul=http://47.244.4.117:8200/useradmin/cookie?user=0&id=user000002 s=https://www.douyu.com/657158><p a=\"1380,1500|0|0|5\" /></t>'),(9,0,'user000001',1,0,'05-22 12:17:26',1558325842,30,23,25,6,100,10000,0,0,'http://47.244.4.117:8200/useradmin/cookie?user=0&id=user000001','https://www.douyu.com/657158','<t a=\"1800|20\" flash=\"1\" isBoot=\"0\" ckul=http://47.244.4.117:8200/useradmin/cookie?user=0&id=user000001 s=https://www.douyu.com/657158><p a=\"1380,1500|0|0|5\" /></t>');
/*!40000 ALTER TABLE `task` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `first_name` varchar(255) DEFAULT NULL,
  `last_name` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `confirmed_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'Admin',NULL,'admin','$pbkdf2-sha512$25000$LYUQQuhday1lDCGktNaasw$kVOLgqvN1C9RO2WPG8SDuzicJVxe/dYenMLVJLjitGHa2C87vAZxO5k4DN9hJxoS7Koa9ZUEhUrUlrlUYAG3Zw',1,NULL),(2,'Harry','Brown','harry.brown@example.com','$pbkdf2-sha512$25000$Z4wxRkjpfa/1ntNaC.F8bw$M0GWNVZTEn4RUhCSJFhw3lk96xlRD/ixtrApL6kd9/tMAUxL2UX58yhbjFhOUULq.XgbYSwyCAPP4XsnDGRrQA',1,NULL),(27,'Cooper','Liu','shan275@163.com','$pbkdf2-sha512$25000$eS8l5BwDQChFqHXu/b937g$teflVtioqMnUgL0kuIUrcOExl0PhmTnZltu8TKEdiqEPIGrH4c47LUdIGw8AElP43OY.nSAVl0u86Sjv/bEPDQ',1,'2019-05-23 16:20:00');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-05-24 11:13:57
