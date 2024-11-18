# Nếu sử dụng ssh thì

git clone git@gitlab.com:python6843439/ecommerce_django.git

# Nếu sử dụng https thì

git clone https://gitlab.com/python6843439/ecommerce_django.git

cd ecommerce_django

python -m venv virt
.\virt\Scripts\activate # Trên Windows

# hoặc

source virt/bin/activate # Trên MacOS/Linux

pip install -r requirements.txt

# Run project

Tạo mới, áp dụng sự thay đổi cho cơ sở dữ liệu: python manage.py migrate
Run server: python manage.py runserver

# Phần admin

# Create admin: python manage.py createsuperuser

# example

Username: admin
admin@gamil.com
password:admin

# dumpdata để tạo một file backup chứa dữ liệu từ database

python manage.py dumpdata > data.json

# loaddata để import dữ liệu từ file data.json này vào cơ sở dữ liệu của họ

python manage.py loaddata data.json

# db

python manage.py makemigrations
python manage.py migrate

Tạo app mới: python manage.py startapp polls

# Tạo requirements.txt
.\virt\Scripts\activate
pip freeze > requirements.txt

# Kiểm tra các package đã cài đặt
pip freeze

# build mysql
mysql -h autorack.proxy.rlwy.net -P 54411 -u root -p railway < backup.sql

# connect mysql
mysql -h autorack.proxy.rlwy.net -P 54411 -u root -p railway

# xem tất cả các bảng trong database
SHOW TABLES;

# xem dữ liệu trong bảng
SELECT * FROM auth_user;

# xem chi tiết cấu trúc của bảng 
DESCRIBE auth_user;

# deploy


#   e c o m m e r _ d j a n g o 
 
 