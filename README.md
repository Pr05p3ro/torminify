torminify
=========
Возможности:
- отслеживание изменений css, js файлов и шаблонов, автоматическая минификация css и js с помощью yui compressor и google closure compiler
- кэширование шаблонов tornado в памяти. По умолчанию render tornado компилирует шаблон заново на каждый запрос.
- встроенный асинхронный загрузчик javascript с возможностью настройки зависимостей скриптов.
- асинхронный загрузчик css файлов.

Зависимости:
- pyyaml
- tornado

Установка:

Выполните 
pip install torminify
Или клонируйте репозитарий
git clone http://...

В директории example/ находится пример tornado приложения. Для запуска необходимо переместить директорию static/ из примера в директорию, доступную веб-серверу, и настроить пути в конфигурации модуля.
В рамках этого туториала предположим, что корневая директория для статики
/var/www/torminify-demo/
А приложение находится в директории
/home/torminify/example/

Для tornado рекомендуется создавать отдельный домен для статики. Мы будем следовать этому правилу, потому конфигурация для nginx может выглядеть следующим образом:

/etc/nginx/sites/st1.fornity.com

server {
    listen 80;
    server_name st1.fornity.com;
    location ^~ / {
        root /var/www/torminify-demo;
	    access_log off;
        expires max;
        add_header Pragma public;
        add_header Cache-Control "public";
    }
}

/etc/nginx/sites/torminify-demo.fornity.com

server {
    listen 80;
	server_name torminify-demo.fornity.com;

    location / {
        proxy_pass_header Server;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
        proxy_pass http://demo;
    }
}






















