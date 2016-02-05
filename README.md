=============
Elcano - IEPG
=============

The Elcano [Global Presence Index](http://www.globalpresence.realinstitutoelcano.org) is an annual measurement of the projection in the world of 90 countries based on three dimensions: Economic, Military, Soft.

This is a project from [Elcano Royal Institute](http://www.realinstitutoelcano.org) of strategic and international studies and [Geographica](https://geographica.gs). 

# Tech overview 
This project is a web platform composed by 3 APIs developed in Python (Flask) at the server side. At client side it uses a HTML application who uses [Backbone JS](http://backbonejs.org).

To deploy and develop it uses [Docker](https://www.docker.com).

# How to prepare the environment

Install [Docker]https://docs.docker.com/engine/installation/) - 1.8+ and [docker-compose](https://docs.docker.com/compose/install/) 1.5.2+

Create the data containers. Please, make your self a favor and don't use local volumes.
```
docker create --name elcano_iepg_pgdata -v /data debian /bin/true
docker create --name elcano_iepg_redisdata -v /data debian /bin/true
docker create --name elcano_iepg_mediadata -v /media debian /bin/true
```

Create a config file
```
cp config.sample.env config.env
```

Adapt this config with your own data.

Set the environment variables 
```
source config.env
```

Import the database
```
docker-compose -f docker-compose.dev.yml up -d pgsql

docker exec elcanoiepg_pgsql_1 psql -U postgres -c  "CREATE USER $POSTGRES_USER with password '$POSTGRES_PASSWORD'"
docker exec elcanoiepg_pgsql_1 psql -U postgres -c  "CREATE DATABASE $POSTGRES_DB with owner $POSTGRES_USER"
docker exec -i elcanoiepg_pgsql_1 psql -U postgres -d $POSTGRES_DB < <dumpfile.sql>
```

Build the image for API.
```
docker build -t geographica/elcano_iepg_api www-srv
```

Set your local domain. add to /etc/hosts
```
echo 127.0.0.1 'dev.elcano-iepg.geographica.gs dev.explora.elcano-iepg.geographica.gs dev.backend.elcano-iepg.geographica.gs' >> /etc/hosts

If you run on OSX:
echo $(docker-machine ip default) 'dev.elcano-iepg.geographica.gs dev.explora.elcano-iepg.geographica.gs dev.backend.elcano-iepg.geographica.gs' >> /etc/hosts
```

Start
```
docker-compose -f docker-compose.dev up
```

Propagate the data from Postgres to REDIS.

```
docker exec elcanoiepg_api_backend_1 python updatecache.py 
```

Prepare clients. TODO: we need to use the latest version of [Sting](https://github.com/GeographicaGS/Sting) to be able to read data of environment values (config.env) inside config.js files.
```
cp www/src/explora/js/config.changes.js www/src/explora/js/config.js
cp www/src/frontend/js/config.changes.js www/src/frontend/js/config.js
cp www/src/backend/js/config.changes.js www/src/backend/js/config.js
```

# Dev environment
To start the application, once you've installed everything. Just type.
```
source config.env
docker-compose -f docker-compose.dev up
```

# Scripts

Update application from XLSX. From www-srv/src/data_calculus/year2015.xlsx it updates de PostgreSQL and REDIS. It also makes a backup of the iepg_data schema of PostgreSQL.
```
docker exec elcanoiepg_api_backend_1 python flux_updatewholeapp.py 
```
RUN calculus engine XLSX to XLSX. From www-srv/src/data_calculus/year2015.xlsx, it generates the engine output at www-srv/src/data_calculus/calculus2015.xlsx.
```
docker exec elcanoiepg_api_backend_1 python flux_xlsxtoxlsx.py 
```
Update REDIS from PostgreSQL
```
docker exec elcanoiepg_api_backend_1 python updatecache.py 
```

# Manager.sh
At production and staging we use manager.sh to start, stop and refresh the servers.

###Refresh
It recreates the container, it's mandatory if you're uploading a new version.
```
./manager.sh refresh <environment>

# Staging example
./manager.sh refresh staging
```

###Restart
It restart the containers.
```
./manager.sh restart <environment>
```

###Buildapps
It compile the frontend apps.
```
./manager.sh buildapps <environment>
```

