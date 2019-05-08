
drop database if exists snickr;
source schema.sql;
use snickr;

insert into user(uname, nickname, email, password) values
('george', 'George', 'george@nyu.edu', sha2('password', 256)),
('john', 'John', 'john@nyu.edu', sha2('password', 256)),
('james', 'James', 'james@nyu.edu', sha2('password', 256)),
('har', 'Harriet', 'har@nyu.edu', sha2('password', 256)),
('sam', 'Samantha', 'sam@nyu.edu', sha2('password', 256)),
('dorothy', 'Dorothy', 'dorothy@nyu.edu', sha2('password', 256)),
('jen', 'Jennifer', 'jen@nyu.edu', sha2('password', 256)),
('trisha', 'Trish', 'trish@nyu.edu', sha2('password', 256));

insert into workspace(wsname, description) values
('job', 'Work'),
('baseball', 'Play');

insert into wsmember(wsname, uname, admin) values
('job', 'george', true),
('job', 'john', false),
('job', 'james', false),
('job', 'har', false),
('job', 'sam', true),

('baseball', 'george', false),
('baseball', 'har', false),
('baseball', 'sam', true),
('baseball', 'trisha', true),
('baseball', 'dorothy', false);

insert into channel(wsname, chname, owner, chtype) values
('job', 'general', 'george', 'public'),
('job', 'managers', 'sam', 'private'),

('baseball', 'general', 'sam', 'public'),
('baseball', 'pitchers', 'har', 'private');

insert into chmember(wsname, chname, member) values
('job', 'general', 'george'),
('job', 'general', 'john'),
('job', 'general', 'james'),
('job', 'general', 'har'),
('job', 'general', 'sam'),

('job', 'managers', 'george'),
('job', 'managers', 'sam'),
('job', 'managers', 'har'),

('baseball', 'general', 'george'),
('baseball', 'general', 'har'),
('baseball', 'general', 'sam'),
('baseball', 'general', 'trisha'),

('baseball', 'pitchers', 'har'),
('baseball', 'pitchers', 'trisha');

insert into invitation(wsname, chname, invitee, invited) values
('baseball', 'pitchers', 'george', timestamp('2019-03-01')),
('baseball', 'general', 'dorothy', timestamp('2019-02-01')),
('job', 'managers', 'john', current_timestamp());

insert into message(wsname, chname, sender, content) values
('job', 'general', 'har', 'When is the staff meeting?'),
('job', 'general', 'george', 'In 10 minutes.'),
('job', 'general', 'sam', 'That is perpendicular'),

('job', 'managers', 'george', 'What is happening at the staff meeting?'),

('baseball', 'general', 'sam', 'When is the game?'),
('baseball', 'general', 'trisha', 'Next sunday!'),

('baseball', 'pitchers', 'trisha', 'Are you pitching on Sunday?'),
('baseball', 'pitchers', 'har', 'I will pitch perpendicular');

-- vim: ft=sql:et:ts=2:sts=2:sw=2
