-- MySQL dump 10.13  Distrib 5.7.24, for osx10.14 (x86_64)
--
-- Host: localhost    Database: dydb
-- ------------------------------------------------------
-- Server version	5.7.24

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
) ENGINE=MyISAM AUTO_INCREMENT=18556 DEFAULT CHARSET=utf8;
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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `custb`
--

LOCK TABLES `custb` WRITE;
/*!40000 ALTER TABLE `custb` DISABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grptb`
--

LOCK TABLES `grptb` WRITE;
/*!40000 ALTER TABLE `grptb` DISABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ordtb`
--

LOCK TABLES `ordtb` WRITE;
/*!40000 ALTER TABLE `ordtb` DISABLE KEYS */;
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
INSERT INTO `roles_users` VALUES (1,1),(1,2),(2,1);
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
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `suptb`
--

LOCK TABLES `suptb` WRITE;
/*!40000 ALTER TABLE `suptb` DISABLE KEYS */;
/*!40000 ALTER TABLE `suptb` ENABLE KEYS */;
UNLOCK TABLES;

--
=======
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
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

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
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'Admin',NULL,'admin','$pbkdf2-sha512$25000$LYUQQuhday1lDCGktNaasw$kVOLgqvN1C9RO2WPG8SDuzicJVxe/dYenMLVJLjitGHa2C87vAZxO5k4DN9hJxoS7Koa9ZUEhUrUlrlUYAG3Zw',1,NULL),(2,'Harry','Brown','harry.brown@example.com','$pbkdf2-sha512$25000$Z4wxRkjpfa/1ntNaC.F8bw$M0GWNVZTEn4RUhCSJFhw3lk96xlRD/ixtrApL6kd9/tMAUxL2UX58yhbjFhOUULq.XgbYSwyCAPP4XsnDGRrQA',1,NULL);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `userid` mediumint(8) unsigned NOT NULL AUTO_INCREMENT COMMENT '用户id',
  `companyid` mediumint(9) NOT NULL DEFAULT '0' COMMENT '公司id',
  `pid` mediumint(9) NOT NULL DEFAULT '0' COMMENT '父id',
  `username` char(20) NOT NULL DEFAULT '' COMMENT '用户名',
  `password` char(32) NOT NULL DEFAULT '' COMMENT '密码',
  `nickname` char(20) NOT NULL DEFAULT '' COMMENT '昵称',
  `regdate` int(10) unsigned NOT NULL COMMENT '注册时间',
  `lastdate` int(11) NOT NULL DEFAULT '0' COMMENT '最后一次登录时间',
  `regip` char(15) NOT NULL DEFAULT '' COMMENT '注册ip',
  `lastip` char(15) NOT NULL DEFAULT '' COMMENT '最后一次登录ip',
  `loginnum` smallint(5) unsigned NOT NULL DEFAULT '0' COMMENT '登录次数',
  `email` char(32) NOT NULL DEFAULT '' COMMENT '邮箱',
  `mobile` char(11) NOT NULL DEFAULT '' COMMENT '手机号码',
  `islock` tinyint(1) unsigned NOT NULL DEFAULT '0' COMMENT '是否锁定',
  `vip` tinyint(1) unsigned NOT NULL DEFAULT '0' COMMENT '是否会员',
  `overduedate` int(11) NOT NULL DEFAULT '0' COMMENT '账户过期时间',
  `status` tinyint(1) unsigned NOT NULL DEFAULT '0' COMMENT '状态-用于软删除',
  PRIMARY KEY (`userid`),
  UNIQUE KEY `username` (`username`),
  KEY `email` (`email`) USING BTREE
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,0,0,'shan275','dc483e80a7a0bd9ef71d8cf973673924','欧耶山哥',1468038500,1473161010,'127.0.0.1','192.168.0.128',28,'shan275@163.com','15915492613',0,0,0,0),(2,0,0,'roy','dc483e80a7a0bd9ef71d8cf973673924','SuperRoy',1468038500,1473161010,'127.0.0.1','192.168.0.128',28,'shan275@163.com','15915492613',0,0,0,0);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;


/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-05-23  3:15:12

