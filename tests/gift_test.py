 #!/usr/bin/ python
# -*- coding: utf-8 -*-

import sys
import html
sys.path.append('..')
from pygiftparser import parser as pygift
from src import model,utils
from collections import namedtuple

from StringIO import StringIO
import unittest
import json


# Ignore Warning
import logging
logger = logging.getLogger()
logger.setLevel(40)

import yattag
import glob

class GiftParsingTestCase(unittest.TestCase):

    def TestDunExemple(self):
        io_gift = StringIO("""
::Pourquoi représenter avec des nombres ?::
[html]<p>Pourquoi faut-il représenter les textes, images, sons,
etc, par des nombres dans un ordinateur ?</p>
{
~<p>C'est un choix industriel.</p>#<p>Non, les industriels n'avaient pas le choix.</p>
~<p>Les ordinateurs ont été inventés par des mathématiciens.</p>#<p>Non, les mathématiciens savent manipuler autre chose que des nombres, et les ordinateurs sont le fruit de l'interaction entre de nombreuses sciences.</p>
=<p>Tout ordinateur est fondamentalement une machine qui calcule avec des
nombres.</p>#<p>Oui, comme un ordinateur ne manipule que des nombres,
tout doit être représenté sous forme de nombres être manipulé par un ordinateur.</p>
####<p>Un ordinateur ne manipule que des nombres, tout doit donc être représenté sous forme de nombres pour qu'il puisse le manipuler.</p> }
""")
        io_modele = StringIO("""
::Pourquoi représenter avec des nombres ?::
[html]<p>Pourquoi faut-il représenter les textes, images, sons,
etc, par des nombres dans un ordinateur ?</p>
{
~<p>C'est un choix industriel.</p>#<p>Non, les industriels n'avaient pas le choix.</p>
~<p>Les ordinateurs ont été inventés par des mathématiciens.</p>#<p>Non, les mathématiciens savent manipuler autre chose que des nombres, et les ordinateurs sont le fruit de l'interaction entre de nombreuses sciences.</p>
=<p>Tout ordinateur est fondamentalement une machine qui calcule avec des
nombres.</p>#<p>Oui, comme un ordinateur ne manipule que des nombres,
tout doit être représenté sous forme de nombres être manipulé par un ordinateur.</p>
####<p>Un ordinateur ne manipule que des nombres, tout doit donc être représenté sous forme de nombres pour qu'il puisse le manipuler.</p> }
```
""")
        questions = pygift.parseFile(io_gift)
        io_gift.close()

        io_none = StringIO("""
# Titre 1
## Titre 2
        """)

        html_src = ''
        d = yattag.Doc()
        d.asis('<!DOCTYPE html>')
        with d.tag('html'):
            with d.tag('head'):
                d.stag('meta', charset="utf-8")
                d.stag('link', rel="stylesheet", href="../static/css/bootstrap.min.css")
                d.stag('link', rel="stylesheet", href="../static/css/modules.css")
                d.stag('link', rel="stylesheet", href="../static/css/jasny-bootstrap.min.css", media="screen")

        for q in questions:
            with d.tag('div', klass='qandcode'):
                q.toHTML(d,True)

        module = model.Module(io_none,"test")
        activity = model.Comprehension(module.sections[0],io_modele)
        activity.toHTML(True)
        # print(sample_activty.sections[0])


        out =  open("test2.html", "w")
        out.write (d.getvalue())
        out.write(activity.html_src)
        out.close()

    def runTest(self):
        self.TestDunExemple()


# Main
if __name__ == '__main__':
    unittest.main(verbosity=1)
