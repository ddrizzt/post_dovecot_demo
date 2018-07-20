DROP TABLE IF exists `virtual_domains`;
CREATE TABLE `virtual_domains` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF exists `virtual_aliases`;
CREATE TABLE `virtual_aliases` (
  `id` int(11) NOT NULL auto_increment,
  `domain_id` int(11) NOT NULL,
  `source` varchar(100) NOT NULL,
  `destination` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF exists `virtual_users`;
CREATE TABLE `virtual_users` (
  `id` int(11) NOT NULL auto_increment,
  `domain_id` int(11) NOT NULL,
  `password` varchar(106) NOT NULL,
  `email` varchar(100) NOT NULL,
  `uid` int(11) NOT NULL,
  `gid` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `virtual_domains`
  (`id` ,`name`)
VALUES
  ('1', '[DOMAIN]'),
  ('2', 'localhost.[DOMAIN]');

INSERT INTO `virtual_users`
  (`id`, `domain_id`, `password` , `email`, `uid`, `gid`)
VALUES
  ('1', '1', ENCRYPT('guest123', CONCAT('$6$', SUBSTRING(SHA(RAND()), -16))), 'guest@[DOMAIN]', 2100, 2100),
  ('2', '1', ENCRYPT('kevin123', CONCAT('$6$', SUBSTRING(SHA(RAND()), -16))), 'kevin@[DOMAIN]', 2101, 2101),
  ('3', '1', ENCRYPT('eric123', CONCAT('$6$', SUBSTRING(SHA(RAND()), -16))), 'eric@[DOMAIN]', 2102, 2102),
  ('4', '1', ENCRYPT('tom123', CONCAT('$6$', SUBSTRING(SHA(RAND()), -16))), 'tom@[DOMAIN]', 2103, 2103),
  ('5', '1', ENCRYPT('jason123', CONCAT('$6$', SUBSTRING(SHA(RAND()), -16))), 'jason@[DOMAIN]', 2104, 2104),
  ('6', '1', ENCRYPT('peter123', CONCAT('$6$', SUBSTRING(SHA(RAND()), -16))), 'peter@[DOMAIN]', 2105, 2105);


/**
 Tables to maintain the heartbeat info from dovecot director and backend.
 */
DROP TABLE IF exists `backend_director_ips`;
CREATE TABLE `backend_director_ips` (
  `type` varchar(10) NOT NULL, /* director or backend */
  `local_ip4` varchar(25) NOT NULL,
  `public_dns` varchar(100) NOT NULL,
  `private_dns` varchar(100) NOT NULL,
  `status` int NOT NULL, /* 1 OK, 2 NOT OK */
  `updated_at` timestamp NOT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`type`, `local_ip4`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


/**
 This table store the current SaltMaster monitor status for dovecot cluster
 */
DROP TABLE IF exists `backend_director_monitoring`;
CREATE TABLE `backend_director_monitoring` (
  `type` varchar(10) NOT NULL, /* director or backend */
  `local_ip4` varchar(25) NOT NULL,
  `public_dns` varchar(100) NOT NULL,
  `private_dns` varchar(100) NOT NULL,
  `status` int NOT NULL, /* 1: OK and under monitoring, 2: NOT OK will be kicked from the cluster, 3: Kicked from the cluster, 0: New cluster, will be added to cluster. */
  `updated_at` timestamp NOT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`type`, `local_ip4`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
