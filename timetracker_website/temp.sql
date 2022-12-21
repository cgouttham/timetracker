CREATE TABLE Type (
    TypeID int PRIMARY KEY,
    Name varchar(255),
    CreatedTime timestamp default current_timestamp,
    LastUpdatedTime timestamp not null default now() 
);

CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.LastUpdatedTime = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON Type
FOR EACH ROW
EXECUTE procedure trigger_set_timestamp();


CREATE TABLE ActivityGroup (
    ActivityGroupID int PRIMARY KEY,
    Name varchar(255),
    CreatedTime timestamp default current_timestamp,
    LastUpdatedTime timestamp not null default now()
);

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON ActivityGroup
FOR EACH ROW
EXECUTE procedure trigger_set_timestamp();

CREATE TABLE Activity (
    ActivityID int PRIMARY KEY,
    Type int,
    State varchar(255),
    StartDate timestamp default current_timestamp,
    Comment varchar(2048),
    CreatedTime timestamp default current_timestamp,
    LastUpdatedTime timestamp not null default now(),
    CONSTRAINT fk_Type
        FOREIGN KEY(Type)
        REFERENCES Type(TypeID)
        ON DELETE RESTRICT
);

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON Activity
FOR EACH ROW
EXECUTE procedure trigger_set_timestamp();

CREATE TABLE Interval (
    IntervalID int PRIMARY KEY,
    Activity int,
    StartTime timestamp not null,
    EndTime timestamp not null,
    CreatedTime timestamp default current_timestamp,
    LastUpdatedTime timestamp not null default now(), 
    CONSTRAINT fk_Activity
        FOREIGN KEY(Activity)
        REFERENCES Activity(ActivityID)
        ON DELETE CASCADE
);

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON Interval
FOR EACH ROW
EXECUTE procedure trigger_set_timestamp();