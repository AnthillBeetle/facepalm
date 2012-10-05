--- Copyright 2012 Anthill Beetle

--- This file is part of Facepalm web-engine.

--- Facepalm web-engine is free software: you can redistribute it and/or modify
--- it under the terms of the GNU General Public License as published by
--- the Free Software Foundation, either version 3 of the License, or
--- (at your option) any later version.

--- Facepalm web-engine is distributed in the hope that it will be useful,
--- but WITHOUT ANY WARRANTY; without even the implied warranty of
--- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
--- GNU General Public License for more details.

--- You should have received a copy of the GNU General Public License
--- along with Facepalm web-engine. If not, see <http://www.gnu.org/licenses/>.


create database creogodville default character set utf8;

create user awards@localhost identified by 'password';
grant delete, insert, select, update, create temporary tables
    on creogodville.* to awards@localhost;

-- sudo /etc/init.d/mysql restart

-- use creogodville;
-- set time_zone = '+4:00';

