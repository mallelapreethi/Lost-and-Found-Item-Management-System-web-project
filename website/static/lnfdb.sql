create database lnfdb;
use lnfdb;
create table roles(roleid numeric(10) primary key NOT NULL, rolename varchar(20) NOT NULL);
insert into roles(roleid, rolename)values('2301', 'User'), ('2302', 'Admin');
select * from roles;
desc roles;

create table Users(userid numeric(10) primary key, passwd varchar(8) NOT NULL, 
fullname varchar(80) NOT NULL, createdby numeric(10) , createdtime datetime, updatedby numeric(10), updatedtime datetime, 
roleid numeric(10) NOT NULL, email varchar(60) NOT NULL, contactno bigint NOT NULL, foreign key(roleid) references roles(roleid)
, check(length(contactno) = 10));
select * from Users;
insert into Users(userid, passwd, fullname, createdby, createdtime, updatedby, updatedtime, roleid, email, contactno) 
values(9211521, '12345678','ADMIN', NULL, NULL, NULL, NULL, 2302, '9211521@security.nitandhra.ac.in', 7093624733),
(421213, '87654321', 'MALLLELA PREETHI', 9211521, '2023-03-15 09:00:00', NULL, NULL, 2301, '421213@student.nitandhra.ac.in', 9493121575),
(621272, '23456789', 'VUCHA SUMASREE', 9211521, '2023-03-15 09:00:00', NULL, NULL, 2301, '621272@student.nitandhra.ac.in', 8317603488),
(1234567, 'nitaplnf', 'SAROJINI', 9211521, '2023-03-15 09:00:00', NULL, NULL, 2301, '1234567@faculty.nitandhra.ac.in', 6305419533),
(2342132, '21345678', 'MANJULA', 9211521, '2023-03-15 09:00:00', NULL, NULL, 2302, '2342132@caretaker.nitandhra.ac.in', 9704916830);
select * from Users;
create table locations(locationid numeric primary key NOT NULL, location varchar(30) NOT NULL);
insert into locations(locationid, location )values(2001, 'srk'), (2002, 'mmm'), (2003, 'gym'), (2004,  'library'), (2005, 'Girl\'s hostel'),
(2006, 'Boy\'s hostel'), (2007, 'Frontgate'), (2008, 'Backgate'), (2009, 'Ground'), (2010, 'Vista'), (2011, 'Canteen'),
(2012, 'Facultyresidence@girls hostel'), (2013, 'Facultyresidence@boyshostel'),(2014, 'Guesthouse'), (2015, 'Sportscomplex');
select * from locations;
create table cctv(video_id int auto_increment primary key NOT NULL, video_name varchar(20), locationid numeric NOT NULL, dateofvideo date NOT NULL, 
starttime time , endtime time , video_link varchar(360) NOT NULL , foreign key(locationid) references locations(locationid));
insert into cctv(video_name, locationid, dateofvideo, starttime, endtime, video_link) values ("srk", 2001, '2023-04-03', '10:00:00',
 '10:00:06', "website/static/videos/input_video1.mp4"); 
insert into cctv(video_name, locationid, dateofvideo, starttime, endtime, video_link) values (NULL, 2003, '2023-04-03', '10:00:00',
 '10:00:06', "website/static/videos/input_video1.mp4"); 
select * from cctv;

create table lostobinfo(lostid int primary key auto_increment, object varchar(200) NOT NULL, size varchar(7), brand varchar(200), 
color varchar(10), lostdate date NOT NULL, locationid numeric, reportedby numeric(10) NOT NULL, reportedtime datetime NOT NULL, updatedby numeric(10),
updatedtime datetime, objstatus varchar(10) NOT NULL default 'Not Found',losttime time NOT NULL,
description varchar(400) NOT NULL, remarks varchar(400), foreign key(reportedby) references Users(userid), foreign key(locationid) references locations(locationid));
select * from lostobinfo;


create table foundobinfo(foundid int primary key auto_increment , object varchar(200) NOT NULL, size varchar(7), brand varchar(200),
 color varchar(10),founddate date NOT NULL, foundtime time NOT NULL, description varchar(400), remarks varchar(400), 
 locationid numeric NOT NULL, collectfrom varchar(100) NOT NULL, reportedby numeric(10) NOT NULL,
reportedtime datetime NOT NULL, updatedby numeric, updatedtime datetime, objstatus varchar(20) NOT NULL default "not returned", 
returnedto numeric(10),returnedtime datetime, returnedby numeric(10), foreign key(reportedby) references Users(userid), 
foreign key(locationid) references locations(locationid), foreign key(returnedto) references Users(userid), 
foreign key(returnedby) references Users(userid));
select * from foundobinfo;
