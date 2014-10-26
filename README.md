Module for Tornado Web Framework, designed to automate minification of css and js files, implement easily asynchronous loading of scripts and additional stylesheets, and cache compiled tornado templates in memory.
With torminify you can achieve the maximum possible speed of page loading:

[Demo](http://torminify.fornity.com/) 

[PageSpeed Insights](https://developers.google.com/speed/pagespeed/insights/?url=http%3A%2F%2Ftorminify.fornity.com%2F&tab=mobile) 

Any questions? Follow me on twitter: [@pauldiakov](http://twitter.com/pauldiakov) 

## Features: 
- Track changes in css, js files and templates, automatic minification of css and js using yui compressor and google closure compiler 
- Caching tornado templates in memory. By default tornado render compiles templates anew on each request. 
- Built-in asynchronous javascript loader with customizable scripts dependency. 
- Asynchronous loader for css files. 

## Dependencies: 
- pyyaml 
- tornado 

## Installation: 
Run
```
pip install git+https://github.com/PaulDiakov/torminify
```
Or clone the repository
```
git clone https://github.com/PaulDiakov/torminify
```

In the directory **example/** there is an example of tornado application. At first you need to move the directory **static/** from example to the directory accessible for web server and configure the path in module configuration. 
In this tutorial we assume that the root directory for the static domain is  
**/home/torminify/example/static/** 
And the application root directory is 
**/home/torminify/example/** 

It is recommended to create a separate cookie-less domain for static files. We will follow this rule. Nginx configuration might look like this: 

**/etc/nginx/sites/st1.fornity.com** 

```
server {
listen 80;
    server_name st1.fornity.com;
    location ^~ / {
        root /home/torminify/example/static/;
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

Import library

```
from torminify.minify import Minify
```

and create an instance of the class 

```
self.minify = Minify(
	#Файл с основными настройками модуля
    config='config/minify/minify.yaml',
    #Перечень css, js и шаблонов, изменения в которых будут отслеживаться
    watch='config/minify/watch.yaml',
    #Корневая директория домена со статикой
    web_root='/home/torminify/example/static/',
    #Служебный файл в котором torminify будет хранить 
    #время изменения отслеживаемых файлов
    cache_index='cache/minify_cache.yaml',
    debug=True)
```

Configure the module in file **config/minify/minify.yaml**

```
---
# If you use a separate domain for static - 
# specify static_domain or comment it out 
static_domain: http://st1.fornity.com

# Disable Minification to accelerate application restart 
# during development 
minify_css: True
minify_js: True

# Specify java path on your server 
# (or "java", if JAVA_HOME is set correctly) 
java_path: java

# Specify path to yui compressor and google closure compiler 
yui_path: tools/yui.jar
closure_path: tools/compiler.jar

# and additional parameters, if necessary 
#closure_additional_params: --compilation_level ADVANCED_OPTIMIZATIONS
#yui_additional_params: --line-break 0

# Directory where torminify will save minified files 
# (relative to the root directory of the statics domain) 
css_min_dir: min/
js_min_dir: min/

# This file will be minified 
# Its content will be placed in the <head> tag 
# Comment out css_inlined if you do not want to use this feature 
css_inlined: css/inlined.css

# Asynchronous javascript and css loader. 
# This file will be minified and embedded into the page template. 
js_loader: 
    file: config/minify/loader.js
    name: loader

# Directory with templates 
# (relative to the root directory of your application) 
templates_dir: templates/
```

Add to **config/minify/watch.yaml** files, changes in which torminify should track

```
---
# List of stylesheets
css_files:
    - css/main.css

# A similar list of scripts 
# Each js file must have a name, file path relative to 
# root directory of the statics domain and optionaly 
# can contain parameter "extends" - names of current file dependencies
# If specified, file will be loaded only after 
# load of all its dependencies. 

js_files:
    - file: js/u.js
      name: u
    - file: js/application.js
      name: app
      extends:
          - u

# List of templates which should be cached in memory 
# when application's server starts 
preload_templates:
    - index.html
```

Start the server from **example/** as usual, 
specify the port that was used in nginx configuration file: 

```
python server.py --port=8889
```

When torminify built in function is used to render template, two additional parameters are passed:

```
self.write(self.minify.render('index.html'))
```
**css_inlined** - contains minified inlined.css content
**css_js_loader** - contains the code of the asynchronous loader 
You can see example of usage in templates/base.html

```
<!DOCTYPE html>
<html>
  <head>
    <title>{% block title %}{% end %}Torminify Demo</title>
    <meta 
    	name="viewport" 
    	content="width=device-width,initial-scale=1.0,user-scalable=no" 
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

The loader adds function **on** into global scope. 
It can execute code when specific js files are loaded. 
Here you can use file names, specified in **watch.yaml** 

```
<script>
on("jquery","app",function(){
	console.log("This line will be displayed after a successful load of "+
				"jquery.js and application.js");
});
</script>
```

Earlier we set for application.js (app) dependence on jquery.js (jquery), so now you can use callback like this: 

```
<script>
on("app",function(){
	console.log("This line will be displayed after a successful load of "+
				"jquery.js and application.js");
});
</script>
```

Dependencies and function **on** allows you to load files asynchronously, saving the boot order where it is needed. For example, jQuery plugins will not be loaded before jQuery and the code that depends on the particular plugin will run only after its successful load.