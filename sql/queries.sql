
-- (1)
insert into user(email, uname, nickname, password) values
('dsalomon@nyu.edu', 'dms833', 'dov', 'password123');

-- (1.1)
insert into wsmember(wsname, uname) values
('job', 'dms833');

-- (2)
insert into channel(wsname, chname, owner, chtype) values
('job', 'random', 'dms833', 'public');

-- (3)
select wsname, uname
from wsmember
where admin;

-- (4)
select chname, invitee
from channel join invitation using(wsname, chname)
where wsname = 'baseball'
and chtype = 'public'
and timestampdiff(day, invited, current_timestamp()) >= 5
-- this subquery is just a sanity check that the
-- user hasn't been added to be a channel member
-- without deleting the invitation
and (wsname, chname, invitee) not in (
    select wsname, chname, member
    from chmember
);

-- (5)
select msgid, content
from message
where wsname = 'job'
and chname = 'general'
order by posted;

-- (6)
select msgid, content
from message
where sender = 'george';

-- (7)
select msgid, content
from message join chmember using(wsname, chname)
where chmember.member = 'george'
and content like '%perpendicular%';

-- vim: ft=sql:et:ts=4:sts=4:sw=4
