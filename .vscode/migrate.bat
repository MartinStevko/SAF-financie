@echo off
echo Virtualne prostredie aktivovane

echo Vytvaram nove migracie
py manage.py makemigrations

echo Migrujem databazu
py manage.py migrate

echo Hotovo!
