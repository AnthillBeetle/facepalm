create database creogodville default character set utf8;

create user awards@localhost identified by 'password';
grant delete, insert, select, update, create temporary tables
    on creogodville.* to awards@localhost;

-- sudo /etc/init.d/mysql restart

-- use creogodville;
-- set time_zone = '+4:00';

