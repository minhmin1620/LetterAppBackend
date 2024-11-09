-- Maria DB Commands

CREATE database AppDevProject;
use AppDevProject

------------------------------------------------
-- Testing Data 
------------------------------------------------

Insert IntO users (user_surname, user_firstname, user_phone_number, user_email, user_password, user_is_active, user_date_of_birth, user_mail_arrival_time, user_create_time)VALUES('Doe', 'John', 'phone#', 'email', 'pass', 1, CURDATE(), CURTIME(), NOW());
Insert users VALUES('Doe', 'Jane', 'phone#', 'email', 'pass', 1, CURDATE(), CURTIME(), NOW());


Insert letters VALUES(1,Now(), 1, 1, 'text', 1, 1, 1);
Insert letters VALUES(Now(), 1, 1, 'text2', 1, 1, 1);
Insert letters VALUES(Now(), 1, 2, 'text3', 1, 1, 1);
Insert letters VALUES(Now(), 1, 2, 'text4', 1, 1, 1);

------------------------------------------------
-- Create tables
------------------------------------------------

drop table users;

Create table users(

    user_id int unsigned not null AUTO_INCREMENT,
    user_surname varchar(50) not null,
    user_firstname varchar(50) not null,
    user_phone_number varchar(10) not null,
    user_email varchar(50) not null,
    user_password varchar(50) not null,
    user_is_active boolean not null,
    user_date_of_birth date not null,
    user_mail_arrival_time time not null,
    user_create_time datetime not null,

    primary key(user_id)

);

--TODO add P.S.
Create table letters(

    letter_id int unsigned not null AUTO_INCREMENT primary key,
    letter_time_sent datetime not null,
    letter_sender_id int unsigned not null,
    letter_recipient_id int unsigned not null,
    letter_message text not null,
    letter_PS text DEFAULT null ,
    letter_design_id int unsigned not null,
    letter_is_read boolean not null,
    letter_is_deleted boolean not null,

    foreign key (letter_sender_id)
        references users(user_id),

    foreign key (letter_recipient_id)
        references users(user_id)

);

Create table drafts(

    draft_id int unsigned not null AUTO_INCREMENT primary key,
    draft_sender_id int unsigned not null,
    draft_recipient varchar(50) not null,
    draft_message text not null,
    draft_design_id int unsigned,

    foreign key (draft_sender_id)
        references users(user_id)

);

------------------------------------------------
-- Show Procedures
------------------------------------------------

select routine_schema as database_name,
       routine_name,
       routine_type as type,
       data_type as return_type,
       routine_definition as definition
from information_schema.routines
where routine_schema not in ('sys', 'information_schema',
                             'mysql', 'performance_schema')
    -- and r.routine_schema = 'database_name' -- put your database name here
order by routine_schema,
         routine_name;

------------------------------------------------
-- Stored Procedures (Letters)
------------------------------------------------

DELIMITER //

-- Get Letters
CREATE PROCEDURE getUserLetters (parameter_user_id int unsigned)

BEGIN

Select * from letters where letters.letter_recipient_id = parameter_user_id;

END;

//

-- Create Letter
CREATE PROCEDURE createLetter (
        parameter_sender_id int unsigned, 
        parameter_recipient_id int unsigned,
        parameter_message text,
        parameter_design_id int unsigned
    )

BEGIN

    INSERT into letters(
        letter_time_sent,
        letter_sender_id,
        letter_recipient_id,
        letter_message,
        letter_design_id,
        letter_is_read,
        letter_is_deleted
    )
    VALUES(
        NOW(), 
        parameter_sender_id, 
        parameter_recipient_id, 
        parameter_message,
        parameter_design_id,
        0,
        0
    );

END;

//

--Add P.S.
CREATE PROCEDURE addPS (parameter_letter_id int unsigned, para_letter_PS text)

BEGIN

UPDATE letters set letters.letter_PS = para_letter_PS where letters.letter_id = parameter_letter_id;

END;

//
-- Read Letter
CREATE PROCEDURE readLetter (parameter_letter_id int unsigned)

BEGIN

UPDATE letters set letters.letter_is_read = 1 where letters.letter_id = parameter_letter_id;

END;

//

-- Delete Letter
CREATE PROCEDURE deleteLetter (parameter_letter_id int unsigned)

BEGIN

UPDATE letters set letters.letter_is_deleted = 1 where letters.letter_id = parameter_letter_id;

END;

//

DELIMITER ;
------------------------------------------------
-- Stored Procedures (User)
------------------------------------------------

-- Get UserByPhoneNumber

DELIMITER //

CREATE PROCEDURE getUserByPhoneNumber(p_phone_number VARCHAR(10))
BEGIN
    SELECT * FROM users WHERE user_phone_number = p_phone_number;

END//

-- Get UserByUsername

CREATE PROCEDURE getUserByUsername(p_email VARCHAR(50))
BEGIN
    SELECT * FROM users WHERE user_email = p_email;
END //

-- Create user

CREATE PROCEDURE addUser(
    p_user_surname VARCHAR(50),
    p_user_firstname VARCHAR(50),
    p_user_phone_number VARCHAR(10),
    p_user_email VARCHAR(50),
    p_user_password VARCHAR(50),
    p_user_date_of_birth DATE
)
BEGIN
    INSERT INTO users (
        user_surname,
        user_firstname,
        user_phone_number,
        user_email,
        user_password,
        user_is_active,
        user_date_of_birth,
        user_mail_arrival_time,
        user_create_time
    )
    VALUES (
        p_user_surname,
        p_user_firstname,
        p_user_phone_number,
        p_user_email,
        p_user_password,
        1,
        p_user_date_of_birth,
        '12:00:00',
        NOW()
    );
END //

DELIMITER ;

------------------------------------------------
-- Stored Procedures (Drafts)
------------------------------------------------

DELIMITER //

CREATE PROCEDURE createDraft(
    parameter_sender_id int unsigned,
    parameter_recipient varchar(50),
    parameter_message text,
    parameter_design_id int unsigned
)
BEGIN
    INSERT INTO drafts(
        draft_sender_id,
        draft_recipient,
        draft_message,
        draft_design_id
    )
    VALUES(
        parameter_sender_id,
        parameter_recipient,
        parameter_message,
        parameter_design_id
    );

END//


CREATE PROCEDURE getUserDrafts(parameter_user_id int unsigned)

BEGIN

SELECT * from drafts where drafts.draft_sender_id = parameter_user_id;

END//


CREATE PROCEDURE deleteDraft(parameter_draft_id int unsigned)

BEGIN

DELETE FROM drafts where drafts.draft_id = parameter_draft_id;

END//

CREATE PROCEDURE editDraft(
    parameter_draft_id int unsigned,
    parameter_recipient varchar(50),
    parameter_message text,
    parameter_design_id int unsigned 
)

BEGIN

UPDATE drafts SET 
    drafts.draft_recipient = parameter_recipient,
    drafts.draft_message = parameter_message,
    drafts.draft_design_id = parameter_design_id

    WHERE drafts.draft_id = parameter_draft_id;

END//