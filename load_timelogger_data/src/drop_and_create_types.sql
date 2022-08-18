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