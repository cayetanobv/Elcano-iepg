/*

  Drop variable schema.

*/

\i 00-config.sql
\c :dbname :user :host :port

begin;

drop schema varengine cascade;

commit;
