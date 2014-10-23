(function (window) {
  var contains = function (a, obj) {
      var i = a.length;
      while (i--)
          if (a[i] === obj) return true;
      return false
  };
  var ul = function () {};
  var tasks = [];
  var loading = [];
  var loaded = [];
  var allReady = false;
  ul.initTasks = function () {
      var initTask = true;
      for (var i in tasks) {
          if (!tasks[i].started) {
              if (tasks[i].ev.length > 0)
                  for (var j in tasks[i].ev) {
                      var check = contains(loaded, tasks[i].ev[j]);
                      if (!check) {
                          initTask = false;
                          break
                      }
                  } else if (!allReady) initTask = false;
              if (initTask) {
                  tasks[i].task();
                  tasks[i].started = true
              }
          }
      }
  };
  ul.appendJS = function (config) {
      ul.initTasks();
      for (var i in config) {
          var s = config[i];
          var readyForLoad = true;
          if (s["extends"])
              for (var ex in s["extends"]) {
                  var check = contains(loaded, s["extends"][ex]);
                  if (!check) {
                      readyForLoad = false;
                      break
                  }
              }
          if (s["js"] && ((!s["extends"] || readyForLoad) && !contains(loading, s["name"]))) {
              var el = document.createElement("script");
              if (!s['version']) {
                  el.src = s["js"];
              } else {
                  el.src = s['js']+'?'+s['version'];
              }

              el.data_name = s["name"];
              loading.push(s["name"]);
              el.onload = el.onerror = function () {
                  if (!this.executed) {
                      this.executed = true;
                      loaded.push(this.data_name);
                      if (config.length == loaded.length) allReady = true;
                      ul.appendJS(config);
                  }
              };
              el.onreadystatechange = function () {
                  var self = this;
                  if (this.readyState == "complete" || this.readyState == "loaded") setTimeout(function () {
                      self.onload();
                  }, 0)
              };
              document.getElementsByTagName("head")[0].appendChild(el)
          }
      }
  };

  ul.cb = function() {
    var styles = ["css_str_placeholder"];

    for (var f in styles) {
      var l = document.createElement('link'); l.rel = 'stylesheet';
      l.href = styles[f];
      document.getElementsByTagName("head")[0].appendChild(l)
    }

    var config=["js_str_placeholder"];ul.appendJS(config);
  };

  ul.init = function() {
    if (window.addEventListener) {
      window.addEventListener("load", ul.cb, false);
    } else if (window.attachEvent) {
      window.attachEvent("onload", ul.cb);
    } else {
      window.onload = ul.cb;
    }
  }

  var on = function () {
      var ev = [];
      for (var i = 0, len = arguments.length; i < len; i++) {
          if (typeof(arguments[i]) !== "function") {
            ev.push(arguments[i]);
          } else { 
            tasks.push({
              "ev": ev,
              "task": arguments[i]
            });
          }
      }

      ul.initTasks()
  };
  window.ul = ul;
  window.on = on
})(window);

ul.init();