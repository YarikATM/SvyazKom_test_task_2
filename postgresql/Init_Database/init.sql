create table location_data
(
  id serial not null primary key,
  --
  lac integer,
  cellid integer,
  eci integer,
  note varchar(200),
  --
  check ( (lac is not null and eci is null) or (lac is null and cellid is null and eci is not null) )
);