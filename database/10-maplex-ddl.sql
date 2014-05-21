/*

  Maplex time carto schema DDL.

*/

\i 00-config.sql
\c :dbname :user :host :port

begin;

create schema maplex authorization :user;

create table maplex.geoentity(
  id_geoentity serial,
  description text,
  date_in timestamp,
  date_out timestamp
);

alter table maplex.geoentity
add constraint geoentity_pkey
primary key(id_geoentity);


create table maplex.geometry(
  id_geometry serial,
  description text
);

select addgeometrycolumn(
  'maplex',
  'geometry',
  'geom',
  4326,
  'MULTIPOLYGON',
  2);

alter table maplex.geometry
add constraint geometry_pkey
primary key(id_geometry);

create index geometry_geom_gist
on maplex.geometry
using gist(geom);


create table maplex.geometry_family(
  id_geometry_family serial,
  name varchar(100),
  description text
);

alter table maplex.geometry_family
add constraint geometry_family_pkey
primary key(id_geometry_family);


create table maplex.geoentity_geometry(
  id_geoentity integer,
  id_geometry_family integer,
  id_geometry integer,
  date_in timestamp,
  date_out timestamp
);

alter table maplex.geoentity_geometry
add constraint geoentity_geometry_pkey
primary key(id_geoentity, id_geometry_family, id_geometry);


create table maplex.name(
  id_name serial,
  name varchar(500),
  description text
);

alter table maplex.name
add constraint name_pkey
primary key(id_name);


create table maplex.name_family(
  id_name_family serial,
  name varchar(100),
  description text
);

alter table maplex.name_family
add constraint name_family_pkey
primary key(id_name_family);


create table maplex.geoentity_name(
  id_geoentity integer,
  id_name integer,
  id_name_family integer,
  date_in timestamp,
  date_out timestamp
);

alter table maplex.geoentity_name
add constraint geoentity_name_pkey
primary key(id_geoentity, id_name, id_name_family);


create table maplex.block(
  id_geoentity_block integer,
  id_geoentity_child integer,
  date_in timestamp,
  date_out timestamp
);

alter table maplex.block
add constraint block_pkey
primary key(id_geoentity_block, id_geoentity_child);


-- Foreign keys

alter table maplex.geoentity_name
add constraint geoentity_name_geoentity_fkey
foreign key (id_geoentity) references maplex.geoentity(id_geoentity);

alter table maplex.geoentity_name
add constraint geoentity_name_name_fkey
foreign key (id_name) references maplex.name(id_name);

alter table maplex.geoentity_name
add constraint geoentity_name_name_family_fkey
foreign key (id_name_family) references maplex.name_family(id_name_family);

alter table maplex.block
add constraint block_geoentity_parent_fkey
foreign key (id_geoentity_block) references maplex.geoentity(id_geoentity);

alter table maplex.block
add constraint block_geoentity_child_fkey
foreign key (id_geoentity_child) references maplex.geoentity(id_geoentity);

alter table maplex.geoentity_geometry
add constraint geoentity_geometry_geoentity_fkey
foreign key (id_geoentity) references maplex.geoentity(id_geoentity);

alter table maplex.geoentity_geometry
add constraint geoentity_geometry_geometry_fkey
foreign key (id_geometry) references maplex.geometry(id_geometry);

alter table maplex.geoentity_geometry
add constraint geoentity_geometry_geometry_family_fkey
foreign key (id_geometry_family) references maplex.geometry_family(id_geometry_family);


-- Views

create view maplex.vw__names as
select
  a.id_geoentity as id_geoentity,
  a.description as geoentity_description,
  a.date_in as geoentity_date_in,
  a.date_out as geoentity_date_out,
  b.id_name as id_name,
  b.date_in as name_date_in,
  b.date_out as name_date_out,
  c.name as name,
  c.description as name_description,
  d.id_name_family as id_name_family,
  d.name as name_family,
  d.description as name_family_description
from
  maplex.geoentity a inner join
  maplex.geoentity_name b on
  a.id_geoentity=b.id_geoentity inner join
  maplex.name c on
  b.id_name=c.id_name inner join
  maplex.name_family d on
  b.id_name_family=d.id_name_family;


create view maplex.vw__geometries as
select
  a.id_geoentity as id_geoentity,
  a.description as geoentity_description,
  a.date_in as geoentity_date_in,
  a.date_out as geoentity_date_out,
  b.id_geometry as id_geometry,
  b.date_in as geometry_date_in,
  b.date_out as geometry_date_out,
  d.description as geometry_description,
  c.id_geometry_family as id_geometry_family,
  c.name as name_geometry_family,
  c.description as geometry_family_description,
  d.geom as geom
from
  maplex.geoentity a inner join
  maplex.geoentity_geometry b on
  a.id_geoentity=b.id_geoentity inner join
  maplex.geometry_family c on
  b.id_geometry_family=c.id_geometry_family inner join
  maplex.geometry d on
  b.id_geometry=d.id_geometry;


create view maplex.vw__blocks as
select
  a.id_geoentity as id_geoentity_block,
  a.description as description_block,
  a.date_in as date_in_block,
  a.date_out as date_out_block,
  b.date_in as date_in_membership,
  b.date_out as date_out_membership,
  c.id_geoentity as id_geoentity_child,
  c.description as description_child,
  c.date_in as date_in_child,
  c.date_out as date_out_child
from
  maplex.geoentity a inner join
  maplex.block b on
  a.id_geoentity=b.id_geoentity_block inner join
  maplex.geoentity c on
  b.id_geoentity_child=c.id_geoentity;
  

-- Restore data

\copy maplex.geoentity from 'maplex_geoentity.csv' with delimiter '|' csv header quote '"'

\copy maplex.name_family from 'maplex_name_family.csv' with delimiter '|' csv header quote '"'

\copy maplex.name from 'maplex_name.csv' with delimiter '|' csv header quote '"'

alter sequence maplex.name_id_name_seq restart with 708;

\copy maplex.geometry_family from 'maplex_geometry_family.csv' with delimiter '|' csv header quote '"'

\copy maplex.block from 'maplex_block.csv' with delimiter '|' csv header quote '"'

\copy maplex.geometry from 'maplex_geometry.csv' with delimiter '|' csv header quote '"'

\copy maplex.geoentity_geometry from 'maplex_geoentity_geometry.csv' with delimiter '|' csv header quote '"'

\copy maplex.geoentity_name from 'maplex_geoentity_name.csv' with delimiter '|' csv header quote '"'


commit;
