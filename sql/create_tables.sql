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


create table engine(
    id enum('') not null primary key,
    maintenance_message_html text not null default ''
);
insert into engine values();

create table user_roles(
    id int not null auto_increment primary key,
    identifier varchar(255) unique not null,
    name varchar(255) unique not null
);
create table users(
    id int not null auto_increment primary key,
    role int not null,
    created timestamp not null default current_timestamp,
    registered timestamp null,
    last_logged_in timestamp null,
    remote_address varchar(255) not null,
    name varchar(255) unique default null, -- godville.net name, null means anonymous
    password varchar(255) not null,
    unique key(remote_address, id),
    unique key(remote_address, name, created),
    foreign key(role) references user_roles(id)
);
create table user_registrations(
    user int not null primary key,
    created timestamp not null default current_timestamp,
    last_checked timestamp null,
    godname varchar(255) not null,
    secret varchar(255) not null,
    foreign key(user) references users(id)
);
create table user_actions(
    id int not null auto_increment primary key,
    identifier varchar(255) unique not null,
    description text not null
);
create table user_roles_and_actions(
    role int not null,
    action int not null,
    is_allowed bool,
    primary key(role, action),
    foreign key(role) references user_roles(id),
    foreign key(action) references user_actions(id)
);

create table contests(
    id int not null auto_increment primary key,
    godville_topic_id int unique not null,
    identifier varchar(255) unique not null,
    name varchar(255) unique not null,
    prix_character_html varchar(255) not null,
    pagelist_suffix text not null
);
create table leagues(
    id int not null auto_increment primary key,
    identifier varchar(255) unique not null
);
create table contest_rounds(
    id int not null auto_increment primary key,
    contest int not null,
    league int not null,
    next int unique default null,
    upper int default null,
    description text null,
    foreign key(contest) references contests(id),
    foreign key(league) references leagues(id),
    foreign key(next) references contest_rounds(id),
    foreign key(upper) references contest_rounds(id)
);
create table contest_stages(
    id int not null auto_increment primary key,
    priority varchar(255) unique not null,
    identifier varchar(255) unique not null,
    description text not null
);
create table tenses(
    id int not null primary key,
    identifier varchar(255) unique not null,
    description text not null
);
create table contest_rounds_and_stages(
    contest int not null,
    round int not null,
    stage int not null,
    begins datetime not null,
    ends datetime not null,
    tense int null,
    primary key(round, stage),
    unique key(contest, stage, begins),
    unique key(contest, stage, ends),
    unique key(tense, contest, stage),
    foreign key(round, contest) references contest_rounds(id, contest),
    foreign key(stage) references contest_stages(id),
    foreign key(tense) references tenses(id)
);

create table contests_and_users(
    contest int not null,
    user int not null,
    role int not null,
    primary key(contest, user),
    foreign key(contest) references contests(id),
    foreign key(user) references users(id),
    foreign key(role) references user_roles(id)
);

create table nomination_sources(
    id int not null auto_increment primary key,
    is_unique bool not null,
    identifier varchar(255) unique not null,
    description text not null,
    unique key(is_unique, id)
);
create table contest_categories(
    id int not null auto_increment primary key,
    contest int not null,
    nomination_source int not null,
    priority varchar(255) not null,
    name varchar(255) unique not null,
    description text not null,
    unique key(contest, priority),
    key(contest, nomination_source),
    foreign key(contest) references contests(id),
    foreign key(nomination_source) references nomination_sources(id)
);

create table ideabox_sections(
    id int not null auto_increment primary key,
    priority varchar(255) unique not null,
    identifier varchar(255) unique not null,
    godville_section_name varchar(255) not null,
    godville_subsection_name varchar(255) default null,
    short_name varchar(255) unique not null,
    prefix varchar(255) unique default null,
    unique key(godville_section_name, godville_subsection_name)
);
create table ideabox_stages(
    id int not null auto_increment primary key,
    priority varchar(255) unique not null,
    identifier varchar(255) unique not null,
    google_docs_name varchar(255) unique not null,
    name varchar(255) unique not null,
    clarification varchar(255) default null
);
create table masterpieces(
    id int not null auto_increment primary key,
    google_docs_index int default null,
    contest int not null,
    user int not null,
    published timestamp null,
    added timestamp not null default current_timestamp,
    ideabox_section int not null,
    ideabox_stage int not null,
    author varchar(255) default null,
    content text not null,
    authors_explanation text not null default '',
    user_comment text not null default '',
    key(google_docs_index),
    unique key(contest, content(255), authors_explanation(255)),
    foreign key(contest) references contests(id),
    foreign key(user) references users(id),
    foreign key(ideabox_section) references ideabox_sections(id),
    foreign key(ideabox_stage) references ideabox_stages(id)
);

create table nominations(
    contest_round int not null,
    contest_category int not null,
    masterpiece int not null,
    user int not null,
    added timestamp not null default current_timestamp,
    primary key(contest_round, contest_category, masterpiece),
    unique key(contest_round, user, masterpiece, contest_category),
    foreign key(contest_round) references contest_rounds(id),
    foreign key(masterpiece) references masterpieces(id),
    foreign key(contest_category) references contest_categories(id),
    foreign key(user) references users(id)
);
create table votes(
    contest_round int not null,
    contest_category int not null,
    user int not null,
    masterpiece int not null,
    added timestamp not null default current_timestamp,
    primary key(contest_round, contest_category, user),
    foreign key(contest_round) references contest_rounds(id),
    foreign key(contest_category) references contest_categories(id),
    foreign key(user) references users(id),
    foreign key(masterpiece) references masterpieces(id),
    foreign key(contest_round, contest_category, masterpiece)
        references nominations(contest_round, contest_category, masterpiece)
);
create table round_results(
    contest_round int not null,
    contest_category int not null,
    masterpiece int not null,
    registered_score int not null,
    score float not null,
    primary key(contest_round, contest_category, masterpiece),
    foreign key(contest_round) references contest_rounds(id),
    foreign key(contest_category) references contest_categories(id),
    foreign key(masterpiece) references masterpieces(id)
);
create unique index results_idx on
    round_results(contest_round, contest_category, score desc, registered_score desc, masterpiece);
create table round_winners(
    contest_round int not null,
    contest_category int not null,
    masterpiece int not null,
    primary key(contest_round, contest_category, masterpiece),
    foreign key(contest_round) references contest_rounds(id),
    foreign key(contest_category) references contest_categories(id),
    foreign key(masterpiece) references masterpieces(id)
);

create table notifications(
    id int not null auto_increment primary key,
    added timestamp not null default current_timestamp,
    description text not null
);
create table notifications_and_contests(
    notification int not null,
    contest int not null,
    html text not null,
    primary key(notification, contest),
    foreign key(notification) references notifications(id),
    foreign key(contest) references contests(id)
);
create table notifications_dismissed_by_users(
    notification int not null,
    user int not null,
    added timestamp not null default current_timestamp,
    primary key(notification, user),
    foreign key(notification) references notifications(id),
    foreign key(user) references users(id)
);

