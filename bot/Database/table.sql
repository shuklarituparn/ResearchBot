DROP TABLE IF EXISTS telegram_bot_data.users;
CREATE TABLE IF NOT EXISTS telegram_bot_data.users(
  userid bigint PRIMARY KEY,
  usertoken text,
  username varchar(255),
  name varchar (255),
  lastGen timestamp


                                                );


select * from telegram_bot_data.users;