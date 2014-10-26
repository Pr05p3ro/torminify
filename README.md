# torminify
Модуль Tornado Web Framework, позволяющий автомизировать минификацию css и js, легко реализовать асинхронную загрузку скриптов и дополнительных таблиц стилей, а также кэшировать в памяти скомпилированные шаблоны tornado.
С помощью torminify вы сможете добиться максимально возможной скорости загрузки страниц: 
[Demo](http://torminify.fornity.com/)
[PageSpeed Insights](https://developers.google.com/speed/pagespeed/insights/?url=http%3A%2F%2Ftorminify.fornity.com%2F&tab=mobile)
## Возможности:
- отслеживание изменений css, js файлов и шаблонов, автоматическая минификация css и js с помощью yui compressor и google closure compiler
- кэширование шаблонов tornado в памяти. По умолчанию render tornado компилирует шаблон заново на каждый запрос.
- встроенный асинхронный загрузчик javascript с возможностью настройки зависимостей скриптов.
- асинхронный загрузчик css файлов.

## Зависимости:
- pyyaml
- tornado

## Установка:
Выполните 
```
    pip install git+https://github.com/PaulDiakov/torminify
```
Или клонируйте репозитарий
```
    git clone https://github.com/PaulDiakov/torminify
```

В директории **example/** находится пример tornado приложения. Для запуска необходимо переместить директорию **static/** из примера в директорию, доступную веб-серверу, и настроить пути в конфигурации модуля.
В рамках этого туториала предположим, что корневая директория для статики
**/var/www/torminify/**
А приложение находится в директории
**/home/torminify/example/**

Для tornado рекомендуется создавать отдельный домен для статики. Мы будем следовать этому правилу, потому конфигурация для nginx может выглядеть следующим образом:

**/etc/nginx/sites/st1.fornity.com**

```
    server {
    listen 80;
        server_name st1.fornity.com;
        location ^~ / {
            root /var/www/torminify;
    	access_log off;
            expires max;
            add_header Pragma public;
            add_header Cache-Control "public";
        }
    }
```

**/etc/nginx/sites/torminify.fornity.com**

```
    upstream demo {
        server 127.0.0.1:8889;
    }
    
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
```

Импортируйте библиотеку

```
    from torminify.minify import Minify
```

и создайте экземпляр класса 

```
    self.minify = Minify(
    	#Файл с основными настройками модуля
        config='config/minify/minify.yaml',
        #Перечень css, js и шаблонов, изменения в которых будут отслеживаться
        watch='config/minify/watch.yaml',
        #Корневая директория домена со статикой
        web_root='/var/www/torminify-demo/',
        #Служебный файл в котором torminify будет хранить время изменения отслеживаемых файлов
        cache_index='cache/minify_cache.yaml',
        debug=True)
```

Настройте модуль в файле **config/minify/minify.yaml**

```
    ---
    #Если Вы используете отдельный домен для статики - 
    #укажите его или закомментируйте параметр static_domain
    static_domain: http://st1.fornity.com
    
    #Отключите минификацию, чтобы ускорить перезагрузку приложения 
    #во время разработки
    minify_css: True
    minify_js: True

    #Укажите путь к java на вашем сервере 
    #(или просто java, если JAVA_HOME настроена корректно)
    java_path: java
    
    #Укажите пути к yui compressor и google closure compiler
    yui_path: tools/yui.jar
    closure_path: tools/compiler.jar

    #и дополнительные параметры, если необходимо
    #closure_additional_params: --compilation_level ADVANCED_OPTIMIZATIONS
    #yui_additional_params: --line-break 0
    
    #Директории, куда torminify будет сохранять минифицированные файлы 
    #(относительно корневой директории домена со статикой)
    css_min_dir: static/min/
    js_min_dir: static/min/
    
    #Этот файл будет минифицирован 
    #Его содержимое будет помещено в тег <head> 
    #Закоментируйте параметр, если не хотите использовать эту возможность
    css_inlined: static/css/inlined.css
    
    #Асинхронный загрузчик javascript и css. 
    #Этот файл будет минифицирован и встроен в шаблон страницы.
    js_loader: 
        file: config/minify/loader.js
        name: loader
    
    #Директория с шаблонами 
    #(относительно корневой директории Вашего приложения)
    templates_dir: templates/
```

Добавьте в **config/minify/watch.yaml** файлы, изменения в которых должен отслеживать torminify

```
    ---
    #Список таблиц стилей
    css_files:
        - static/css/main.css
    
    #Аналогичный список скриптов
    #Каждый js файл должен иметь имя, путь к файлу относительно корневой директории 
    #домена со статикой и опционально может содержать параметр extends со списком 
    #имен файлов от которого он зависит.
    #Если указаны зависимости - файл будет загружен только после загрузки 
    #всех его зависимостей

    js_files:
        - file: static/js/u.js
          name: u
        - file: static/js/application.js
          name: app
          extends:
              - u
    
    #Список шаблонов, которые должны быть закэшированы в памяти в момент 
    #запуска сервера приложения в целях оптимизации
    preload_templates:
        - index.html
```

Запустите сервер из **example/** как обычно, указав порт, который был задан в upstream в конфиге nginx:

```
    python server.py --port=8889
```

Когда для рендера шаблона используется функция из torminify

```
    self.write(self.minify.render('index.html'))
```

В шаблон передается два дополнительных параметра:

**css_inlined** - содержит минифицированное содержимое inlined.css для вставки в <head>
**css_js_loader** - содержит код асинхронного загрузчика
Пример использования этих переменных Вы можете увидеть в templates/base.html

```
    <!DOCTYPE html>
    <html>
      <head>
        <title>{% block title %}{% end %}Torminify Demo</title>
        <meta 
        	name="viewport" 
        	content="width=device-width, initial-scale=1.0, user-scalable=no" 
        />
        {% if css_inlined != "" %}
        	<style type="text/css">{% raw css_inlined %}</style>
        {% end %}
      </head>
      <body id="app" class="wrap wider">
      	<script>{% raw css_js_loader %}</script>
        {% block body %}{% end %}
      </body>
    </html>
```

Загрузчик добавляет в глобальную область видимости функцию **on**.
Ее назначение - выполнение кода в момент загрузки конкретного js файла.
Тут и найдут применение имена файлов, которые Вы задали в **watch.yaml**

Пример:

```
    <script>
    on("jquery","app",function(){
    	console.log("Эта строка будет выведена после успешной загрузки "+
    				"jquery.js и application.js");
    });
    </script>
```

Так как ранее мы указали для application.js (app) зависимость от jquery.js (jquery) - вы можете передать функции on только зависимость от app:

```
    <script>
    on("app",function(){
    	console.log("Эта строка будет выведена после успешной загрузки "+
    				"jquery.js и application.js");
    });
    </script>
```

Зависимости и функция **on** позволяют загружать файлы асинхронно, сохраняя при этом последовательность загрузки, где это нужно. Плагины jquery не будут загружены до самого jquery, а код, зависящий от конкретных плагинов будет выполнить только после их полной загрузки.