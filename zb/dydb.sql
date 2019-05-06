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
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'Admin',NULL,'admin','$pbkdf2-sha512$25000$LYUQQuhday1lDCGktNaasw$kVOLgqvN1C9RO2WPG8SDuzicJVxe/dYenMLVJLjitGHa2C87vAZxO5k4DN9hJxoS7Koa9ZUEhUrUlrlUYAG3Zw',1,NULL),(2,'Harry','Brown','harry.brown@example.com','$pbkdf2-sha512$25000$Z4wxRkjpfa/1ntNaC.F8bw$M0GWNVZTEn4RUhCSJFhw3lk96xlRD/ixtrApL6kd9/tMAUxL2UX58yhbjFhOUULq.XgbYSwyCAPP4XsnDGRrQA',1,NULL);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

