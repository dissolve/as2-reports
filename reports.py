import os
import urllib2
import json
from bs4 import BeautifulSoup, Tag
from markdown2 import Markdown, markdown_path

def init(features):
  page = BeautifulSoup("""<!doctype html>
<html>
  <head>
    <title>AS2 implemented features</title>
    <style type=\"text/css\">
      html { font-family: Arial }
      td, th {
        padding: 0.3em; margin: 0;
        border: 1px solid silver;
        text-align: center;
      }
      .zero { background-color: #FF8166; }
      .one { background-color: #FFAC66; }
      .two { background-color: #FFC966; }
      .three { background-color: #98FAA6; }
      .four { background-color: #44D55F; }
    </style>
  </head>
  <body>
    <h1>AS2 implemented features</h1>
    <p>This summary was generated by parsing the markdown of the <a href="https://github.com/w3c/activitystreams/tree/master/implementation-reports">implementation reports</a>. Improvements welcome; <a href="https://github.com/rhiaro/as2-reports">source</a> (Python).</p>
    <p><em>Currently this list includes extension properties in the AS2 namespace (AP) mixed in. TODO: filter them out somehow.</em></p>
    <table></table>
  </body>
</html>""", 'html.parser')

  page = list_features(page, features)
  return page

def list_features(page, features):

  first = add_row(page)
  add_col(page, first, "th", "Feature / Implementation")
  for f in features:
    r = add_row(page)
    add_col(page, r, "th", f)

  return page

def get_features():
  request = urllib2.Request("https://www.w3.org/ns/activitystreams", headers={"Accept" : "application/ld+json"})
  contents = urllib2.urlopen(request).read()
  l = json.loads(contents)["@context"].keys()
  l.remove("xsd")
  l.remove("@vocab")
  l.remove("id")
  l.remove("type")
  l.remove("ldp")
  l.remove("orderedItems")
  return sorted(l)

def add_row(page):
  table = page.table
  row = page.new_tag("tr")
  table.append(row)

  return row

def add_col(page, row, tag, string):
  cell = page.new_tag(tag)
  cell.append(string)
  row.append(cell)

  return row

def parse_reports():

  features = get_features()
  page = init(features)
  rows = page.table.find_all('tr')
  row = 0
  first = rows[row]

  path = os.getcwd()+"/activitystreams/implementation-reports/"

  for filename in os.listdir(path):
    row = 0
    if filename != "template.md":
      html = markdown_path(path+filename)
      soup = BeautifulSoup(html, 'html.parser')

      imp_name = soup.h1.string
      print imp_name + "\n"
      imp_info = soup.h1.find_next_sibling('ul')
      imp_li = imp_info.find_all('li')
      imp_infos = {}
      for i in imp_li:
        inf = i.string.split(": ")
        imp_infos[inf[0]] = inf[1]

      if imp_infos['Application role'].strip() == "publisher":
        role = "P"
      elif imp_infos['Application role'].strip() == "consumer":
        role = "C"
      elif imp_infos['Application role'].strip() == "both":
        role = "PC"
      else:
        role = "X"

      # imp_header = "<a href=\"%s\" title=\"%s\">%s</a>" % (imp_infos['Main URL'], imp_infos['Version'], imp_name)
      # imp_header_ele = BeautifulSoup(imp_header, 'html.parser')
      # print imp_header_ele
      add_col(page, first, "th", imp_name)

      if(row < len(features)):
        for f in features:
          row = row + 1
          next_row = rows[row]
          if(is_implemented(f, soup)):
            add_col(page, next_row, "td", role)
          else:
            add_col(page, next_row, "td", "")
  first = True
  for r in rows:
    if first:
        first = False
    else:
      r = color_row(r)

  return page

def is_implemented(feature, implementation_soup):
  
  classes = implementation_soup.find_all('h3')
  properties = implementation_soup.find_all('li')

  for c in classes:
    if c.string == feature:
      answer = c.next_sibling
      if answer == "\n":
        answer = answer.next_sibling
      
      try:
        if answer and answer.string[15] == "y":
          return True
        else:
          return False
      except IndexError:
        print answer
        pass

  for p in properties:
    try:
      answer = p.string.split(": ")
      if answer[0] == feature:
        if answer[1] and answer[1][0] == "y":
          return True
        else:
          return False
    except AttributeError:
      print "(fail)"

def color_row(row):
  c = 0
  p = 0
  cells = row.find_all("td")
  for cell in cells:
    if cell.string == "PC":
      c = c + 1
      p = p + 1
    elif cell.string == "C":
      c = c + 1
    elif cell.string == "P":
      p = p + 1
      
  row["class"] = "zero"

  i = 0
  if c > 1:
    i = i + 2
  else:
    i = i + c

  if p > 1:
    i = i + 2
  else:
    i = i + p
      
  if i == 0 :
    row["class"] = "zero"
  elif i == 1:
    row["class"] = "one"
  elif i == 2:
    row["class"] = "two"
  elif i == 3:
    row["class"] = "three"
  elif i == 4:
    row["class"] = "four"

  return row

def write(html):
  if not os.path.exists(os.getcwd()+"/out"):
    os.makedirs(os.getcwd()+"/out")

  with open(os.getcwd()+"/out/reports.html", "w+") as the_file:
    the_file.write(html)

page = parse_reports()
write(page.prettify())
