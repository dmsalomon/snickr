
create database snickr;
use snickr

create table user (
	uname varchar(64) not null,
	nickname varchar(64),
	email varchar(255) not null,
	password varchar(255) not null,
	ucreated timestamp default current_timestamp,
	primary key(uname)
);

create table workspace (
	wsname varchar(64) not null,
	description text,
	wscreated timestamp default current_timestamp,
	primary key(wsname)
);

create table wsmember (
	wsname varchar(64) not null,
	uname varchar(64) not null,
	wsadded timestamp not null default current_timestamp,
	admin boolean not null default false,
	primary key(wsname, uname),
	foreign key(wsname) references workspace(wsname),
	foreign key(uname) references user(uname)
);

create table channel (
	wsname varchar(64) not null,
	chname varchar(64) not null,
	owner varchar(64) not null,
	chtype enum ('public', 'private', 'direct') not null,
	chcreated timestamp not null default current_timestamp,
	primary key(wsname, chname),
	foreign key(wsname, owner) references wsmember(wsname, uname)
);

create table chmember (
	wsname varchar(64) not null,
	chname varchar(64) not null,
	member varchar(64) not null,
	chadded timestamp not null default current_timestamp,
	primary key(wsname, chname, member),
	foreign key(wsname, chname) references channel(wsname, chname),
	foreign key(wsname, member) references wsmember(wsname, uname)
);

create table invitation (
	wsname varchar(64) not null,
	chname varchar(64) not null,
	invitee varchar(64) not null,
	invited timestamp not null default current_timestamp,
	primary key(wsname, chname, invitee),
	foreign key(wsname, chname) references channel(wsname, chname),
	foreign key(wsname, invitee) references wsmember(wsname, uname)
);

create table message (
	msgid int unsigned auto_increment not null,
	wsname varchar(64) not null,
	chname varchar(64) not null,
	sender varchar(64) not null,
	content text not null,
	posted timestamp not null default current_timestamp,
	primary key(msgid),
	foreign key(wsname, chname, sender) references chmember(wsname, chname, member)
);

-- vim: ft=sql:et:ts=2:sts=2:sw=2
