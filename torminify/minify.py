import os
import json
import yaml
from tornado import autoreload
from subprocess import call
from tornado import template
from shutil import copyfile

class Minify:
    version = "0.1.3"

    cache = []
    settings = {
        'java_path': 'java',
        'closure_additional_params': '',
        'yui_additional_params': '',
        'css_inlined': '',
        'css_files': [],
        'js_files': [],
        'yui_path': '',
        'closure_path': '',
        'templates_dir': 'templates/',
        'static_domain': '',
        'minify_css': True,
        'minify_js': True,
        'batch_css': False
    }

    templates = []
    cache_index = ''
    debug = False

    cache_css_inlined = ''
    cache_css_js_loader = ''

    def load_config(self, filename):
        with open(filename, 'r') as f:
            s = yaml.safe_load(f)
            for key,v in s.items():
                self.settings[key] = v

            f.close()

    def before_reload_done(self):
        self.recompile()

    def __init__(self, config, watch, web_root, cache_index, debug=False):
        autoreload.watch(config)
        autoreload.watch(watch)        
        autoreload.add_reload_hook(self.before_reload_done)

        self.log('config '+config)
        self.log('watch '+watch)

        self.load_config(config)
        self.load_config(watch)
        
        if not os.path.exists(os.path.dirname(cache_index)):
            os.makedirs(os.path.dirname(cache_index))

        self.settings['web_root'] = web_root
        self.cache_index = cache_index
        self.debug = debug
        if self.debug:
            self.log("debug is enabled")
            self.log("config used: "+config)
            self.log("web root: "+web_root)
            self.log("cache index: "+cache_index)

        self.cache = self.load_cache()

        if self.settings['css_inlined']!='':
            self.settings['css_files'].append(self.settings['css_inlined'])

        for f in self.settings['css_files']:
            self.log('watch css '+f)
            autoreload.watch(self.get_file_path(f))

        self.settings['js_files'].append(self.settings['js_loader'])

        for f in self.settings['js_files']:
            self.log('watch js ['+f['name']+'] '+f['file'])
            if f['name']!='loader':
                autoreload.watch(self.get_file_path(f['file']))
            else:
                autoreload.watch(f['file'])

        if 'preload_templates' in self.settings:
            loader = template.Loader(self.settings['templates_dir'])

            for f in self.settings['preload_templates']:
                self.log('watch template '+f)
                autoreload.watch(self.settings['templates_dir']+f)
                self.templates.append({'file':f,'template':loader.load(f)})

        if not os.path.exists(os.path.dirname(self.settings['css_min_dir'])):
            os.makedirs(os.path.dirname(self.settings['css_min_dir']))

        if not os.path.exists(os.path.dirname(self.settings['js_min_dir'])):
            os.makedirs(os.path.dirname(self.settings['js_min_dir']))

        self.recompile()

        self.cache_css_inlined = self.get_inlined_css()
        self.cache_css_js_loader = self.get_loader()

    def log(self, msg):
        if self.debug:
            print("torminify: %s" % msg)

    def render(self, template_file, **kwargs):
        for t in self.templates:
            if t['file']==template_file:

                args = {'css_js_loader': self.cache_css_js_loader, 'css_inlined': self.cache_css_inlined, 'compress_whitespace': True}
                
                if kwargs is not None:
                    for key, value in kwargs.items():
                        args[key] = value

                return t['template'].generate(**args)

        return ""

    def recompile(self):
        for f in self.settings['css_files']:
            if os.path.isfile(self.get_file_path(f)):
                stat = os.stat(self.get_file_path(f))
                fileChanged = stat.st_mtime

                newFile = True
                for c in self.cache:
                    if 'file' in c and c['file']==f:
                        newFile = False
                        if fileChanged!=c['changed']:
                            c['changed'] = fileChanged
                            c['version'] = c['version'] + 1

                            self.log(f + " was changed, version " + str(c['version']) )
                            self.minify_css(self.get_file_path(f),c['minified'])

                if newFile:
                    fileDst = self.settings['css_min_dir']+os.path.basename(self.get_file_path(f))
                    self.cache.append({'file':f,'changed':fileChanged,'version':1,'minified':fileDst})

                    self.log("new css: "+f)
                    self.minify_css(self.get_file_path(f), fileDst)

        for f in self.settings['js_files']:
            if (f['name']=='loader' and os.path.isfile(f['file'])) or os.path.isfile(self.get_file_path(f['file'])):
                stat = {}
                if f['name']=='loader':
                    stat = os.stat(f['file'])
                else:
                    stat = os.stat(self.get_file_path(f['file']))

                fileChanged = stat.st_mtime

                newFile = True
                for c in self.cache:
                    if 'file' in c and c['file']==f['file']:
                        newFile = False
                        if fileChanged!=c['changed'] or c['name']!=f['name'] or ('extends' in f and 'extends' in c and c['extends']!=f['extends']):
                            c['changed'] = fileChanged
                            c['version'] = c['version'] + 1
                            c['name'] = f['name']
                            if 'extends' in f:
                                c['extends'] = f['extends']

                            self.log(f['file'] + " was changed, version " + str(c['version']) )
                            if f['name']=='loader':
                                self.minify_js(f['file'],c['minified'])
                            else:
                                self.minify_js(self.get_file_path(f['file']),c['minified'])

                if newFile:
                    fileDst = self.settings['js_min_dir']+os.path.basename(self.get_file_path(f['file']))
                    
                    if 'extends' in f:
                        self.cache.append({'file':f['file'],'name':f['name'],'extends':f['extends'],'changed':fileChanged,'version':1,'minified':fileDst})
                    else:
                        self.cache.append({'file':f['file'],'name':f['name'],'changed':fileChanged,'version':1,'minified':fileDst})    
                    
                    self.log("new js: "+f['file'])
                    if f['name']=='loader':
                        self.minify_js(f['file'],fileDst)
                    else:
                        self.minify_js(self.get_file_path(f['file']),fileDst)

        self.log("done")
        self.save_cache()

    def minify_css(self, fileSrc, fileDst):
        if self.settings['minify_css']:
            call(self.settings['java_path']+" -jar "+self.settings['yui_path']+" "+self.settings['yui_additional_params']+" " + fileSrc + " -o " + self.settings['web_root']+fileDst, shell=True)
        else: 
            copyfile(fileSrc, self.settings['web_root']+fileDst)

    def minify_js(self, fileSrc, fileDst):
        if self.settings['minify_js']:
            call(self.settings['java_path']+" -jar "+self.settings['closure_path']+" "+self.settings['closure_additional_params']+" --js " + fileSrc + " --js_output_file " + self.settings['web_root']+fileDst, shell=True)
        else:
            copyfile(fileSrc, self.settings['web_root']+fileDst)

    def save_cache(self):
        new_cache = []
        for c in self.cache:
            exists = False
            for f in self.settings['css_files']:
                if 'file' in c and c['file']==f and os.path.isfile(self.get_file_path(f)):
                    exists = True 
                    break

            if not exists:
                for f in self.settings['js_files']:
                    if 'file' in c and c['file']==f['file'] and ((f['name']=='loader' and os.path.isfile(f['file'])) or os.path.isfile(self.get_file_path(f['file']))):
                        exists = True 
                        break

            if exists:
                new_cache.append(c)

        self.cache = new_cache

        with open(self.cache_index, 'w') as outfile:
            outfile.write( yaml.dump(self.cache) )
            outfile.close()

    def load_cache(self):
        if os.path.isfile(self.cache_index):
            with open(self.cache_index, 'r') as f:
                j = yaml.safe_load(f)
                f.close()
                return j

        return []

    def get_file_path(self, local_file):
        return self.settings['web_root']+local_file

    def get_inlined_css(self):
        for f in self.cache:
            if f['file']==self.settings['css_inlined'] and os.path.isfile(self.get_file_path(f['minified'])):
                with open (self.get_file_path(f['minified']), "r") as inlined:
                    r = inlined.read().replace('\n', '')
                    inlined.close()
                    return r


        return ""

    def get_js_str(self):
        l = []
        for f in self.cache:
            if 'name' in f and f['file']!=self.settings['js_loader']['file']:
                if 'extends' in f:
                    l.append({
                        'name':f['name'],
                        'extends':f['extends'],
                        'js':self.settings['static_domain']+"/"+f['minified'],
                        'version':f['version']
                    })
                else:
                    l.append({
                        'name':f['name'],
                        'js':self.settings['static_domain']+"/"+f['minified'],
                        'version':f['version']
                    })

        return json.dumps(l)

    def get_css_str(self):
        s = "['"
        for f in self.cache:
            if 'name' not in f and f['file']!=self.settings['css_inlined']:
                if s != "['":
                    s += ",'"
                s += self.settings['static_domain']+"/"+f['minified']+"?"+str(f['version'])+"'"

        return s+"]"

    def get_loader(self):
        s = ""
        for f in self.cache:
            if 'name' in f and f['file']==self.settings['js_loader']['file']:
                with open (self.get_file_path(f['minified']), "r") as loader:
                    s = loader.read().replace('\n', '').replace('["css_str_placeholder"]', self.get_css_str()).replace('["js_str_placeholder"]', self.get_js_str())
                    loader.close()
        return s

    def get_templates(self):
        return self.templates