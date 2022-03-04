## This module wraps the URL-matching code used by flask to be
## friendly to symbolic / concolic execution.

import flask
import werkzeug
from . import fuzzy

class SymbolicRule(werkzeug.routing.Rule):
  def __init__(self, string, **kwargs):
    super(SymbolicRule, self).__init__(string, **kwargs)
    self.symvarnames = {}
    for converter, arguments, variable in werkzeug.routing.parse_rule(string):
      if converter is 'path':
        self.symvarnames[variable] = fuzzy.uniqname(variable)

  def match(self, path, method=None):
    # print('match', path, method, 'rule', self.rule)
    orig = super(SymbolicRule, self).match(path, method)

    expectpath = "|"
    res = {v: fuzzy.mk_str(n, orig.get(v, '')) for (v, n) in self.symvarnames.items()}
    for converter, arguments, variable in werkzeug.routing.parse_rule(self.rule):
      if arguments is not None:
        return orig
      if converter is None:
        expectpath += variable
      elif converter is 'path':
        expectpath += res[variable]
        if '/' in res[variable]:
          ## nonsensical assignment of concrete value; fall back to orig
          return orig
      else:
        return orig

    if expectpath == path:
      return res
    else:
      return orig

class SymbolicRequest(flask.Request):
  @werkzeug.utils.cached_property
  def cookies(self):
    hdr = self.environ.get('HTTP_COOKIE', '')
    nameval = hdr.split('=', maxsplit=1)
    if len(nameval) < 2:
      return {}
    else:
      (name, val) = nameval
      return {name: val}

  @werkzeug.utils.cached_property
  def form(self):
    ## Maybe make a concolic_dict() that would eliminate the need
    ## to enumerate all the keys of interest here?
    res = {}
    for k in ('recipient', 'zoobars'):
      if fuzzy.mk_int('form_%s_present' % k, 0) == 0:
        continue
      res[k] = fuzzy.mk_str('form_%s_val' % k, '')
    return res

flask.Flask.url_rule_class = SymbolicRule
flask.Flask.request_class = SymbolicRequest
