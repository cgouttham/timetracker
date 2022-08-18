DROP TABLE Type CASCADE;

CREATE TABLE Type (
    Guid uuid PRIMARY KEY,
    ParentGuid uuid,
    Name varchar(50),
    CreatedTime timestamp default current_timestamp,
    LastUpdatedTime timestamp not null default now(),
    IsActivityGroup bool not null default false,
    Deleted bool not null default false
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
    Guid varchar(50) PRIMARY KEY,
    ActivityGuid varchar(50),
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
