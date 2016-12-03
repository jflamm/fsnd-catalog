echo "...removing and re-creating database"
psql -f catalog.sql
echo "...configuring database"
python database_setup.py
echo "...loading database"
python database_populate.py
echo "...done"
