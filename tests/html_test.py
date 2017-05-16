 #!/usr/bin/ python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append('..')
from pygiftparser import parser as pygift
from src import model
from bs4 import BeautifulSoup

from StringIO import StringIO
import unittest

# Ignore Warning
import logging
logger = logging.getLogger()
logger.setLevel(40)

import yattag

TEST_GIFT_DIR = "./testGIFT/"


class GiftParsingHTMLTestCase(unittest.TestCase):

    def TestUnChoix(self):
        io_gift = StringIO("""
::Pourquoi représenter avec des nombres ?::
Pourquoi faut-il <strong>représenter</strong> les textes, images, sons,
etc, *par* des nombres dans un ordinateur ?
{
~C'est un choix <strong>industriel</strong>.#Non, les industriels n'avaient pas le choix.
~Les ordinateurs ont été inventés par des mathématiciens.#Non, les mathématiciens savent manipuler autre chose que des nombres, et les ordinateurs sont le fruit de l'interaction entre de nombreuses sciences.
=Tout ordinateur est fondamentalement une machine qui calcule avec des
nombres.#Oui, comme un ordinateur ne manipule que des nombres,
tout doit être représenté sous forme de nombres être manipulé par un ordinateur.
####Un ordinateur ne manipule que des nombres, tout doit donc être représenté sous forme de nombres pour qu'il puisse le manipuler. }
""")
        questions = pygift.parseFile(io_gift)
        io_gift.close()

        d = yattag.Doc()
        d.asis('<!DOCTYPE html>')
        with d.tag('html'):
            with d.tag('head'):
                d.stag('meta', charset="utf-8")
                d.stag('link', rel="stylesheet", href="../../static/css/bootstrap.min.css")
                d.stag('link', rel="stylesheet", href="../../static/css/modules.css")
                d.stag('link', rel="stylesheet", href="../../static/css/jasny-bootstrap.min.css", media="screen")

        with d.tag('h2'):
            d.text(str(questions[0].answers.__class__))

        for q in questions:
            q.toHTML(d,True)

        for q in questions:
            q.toHTML(d,False)

        #Vérifie qu'une seule question a bien été créée
        self.assertEqual(len(questions),1,"More than one Question for 'Test un choix'")

        # TEST HTML
        soup = BeautifulSoup(d.getvalue(), 'html.parser')
        for i,form in enumerate(soup.find_all('form')):
            self.assertEqual(form.h3['class'][0], u'questiontitle'," Not h3 or not good class for h3")
            for j,div in enumerate(form.find_all('div')):
                if j == 0 :
                    self.assertEqual(div['class'][0], u'questiontext',"Not div or not good class for 1rst div")
                if (j == 1):
                    if (i == 0):
                        self.assertEqual(div['class'][0], u'groupedAnswerFeedback')
                    elif (i == 1):
                        self.assertEqual(div['class'][0], u'groupedAnswer')
                if (j == 2):
                        self.assertEqual(div['class'][0], u'global_feedback')
            self.assertEqual(form.ul['class'][0], u'multichoice')
            nb_li = len(form.find_all('li'))
            self.assertEqual(nb_li,3)


        out =  open(TEST_GIFT_DIR+"simplechoice.html", "w")
        out.write (d.getvalue())
        out.close()

        print("[GiftParsingHTMLTestCase]-- check_single_answer OK --")


    def TestMultiple(self):
        io_gift = StringIO("""
::Parmi ces personnes, nommez-en deux qui sont enterrées dans la Grant's tomb. ::{
   ~%-100%Personne # NOMMEZ EN DEUX
   ~%50%Grant # Et de un
   ~%50%L'épouse de Grant # Et de deux
   ~%-100%Le père de Grant # Perdu !
####C'était Grant ainsi que sa femme
}""")
        questions = pygift.parseFile(io_gift)
        io_gift.close()

        d = yattag.Doc()
        d.asis('<!DOCTYPE html>')
        with d.tag('html'):
            with d.tag('head'):
                d.stag('meta', charset="utf-8")
                d.stag('link', rel="stylesheet", href="../../static/css/bootstrap.min.css")
                d.stag('link', rel="stylesheet", href="../../static/css/modules.css")
                d.stag('link', rel="stylesheet", href="../../static/css/jasny-bootstrap.min.css", media="screen")

        with d.tag('h2'):
            d.text(str(questions[0].answers.__class__))

        for q in questions:
            q.toHTML(d,True)

        for q in questions:
            q.toHTML(d,False)

        self.assertEqual(len(questions),1,"More than one Question for 'TestMultiple'")

        # TEST HTML
        soup = BeautifulSoup(d.getvalue(), 'html.parser')
        for i,form in enumerate(soup.find_all('form')):
            self.assertEqual(form.h3['class'][0], u'questiontitle'," Not h3 or not good class for h3")
            for j,div in enumerate(form.find_all('div')):
                if j == 0 :
                    self.assertEqual(div['class'][0], u'questiontext',"Not div or not good class for 1rst div")
                if (j == 1):
                    if (i == 0):
                        self.assertEqual(div['class'][0], u'groupedAnswerFeedback')
                    elif (i == 1):
                        self.assertEqual(div['class'][0], u'groupedAnswer')
                if (j == 2):
                        self.assertEqual(div['class'][0], u'global_feedback')
            self.assertEqual(form.ul['class'][0], u'multianswer')
            nb_li = len(form.find_all('li'))
            self.assertEqual(nb_li,4)

        out =  open(TEST_GIFT_DIR+"multipleanswer.html", "w")
        out.write (d.getvalue())
        out.close()

        print("[GiftParsingHTMLTestCase]-- check_smultiple_answer OK --")


    def TestSimpleText(self):
        io_gift = StringIO("""
::Le numérique concerne tout le monde::
**Quels étudiants sont concernés par le numérique ?**
Le numérique concerne évidemment les étudiants en informatique et plus généralement les étudiants des filières scientifiques.  Mais vous qui êtes inscrits dans une université de sciences humaines et sociales, êtes-vous concernés ?
Choisissez au moins 3 des domaines suivants et faites des recherches pour voir en quoi ils sont impactés par le numérique : les médias, la santé, l'histoire, la sociologie, la linguistique, les arts, la culture, l'enseignement, l'archéologie.
Faites une synthèse en quelques lignes de vos recherches en précisant les domaines auxquels vous vous êtes intéressés. Indiquez les liens des sites sur lesquels vous avez trouvé ces informations. La liste est non exhaustive et vous pouvez vous intéresser à d'autres domaines.
{####
# Le numérique concerne tout le monde
Ces recherches ont dû vous convaincre, si c'était nécessaire, que le numérique **n'est pas réservé** aux informaticiens, il concerne tout le monde, toutes les disciplines.
S'agissant plus particulièrement des **sciences humaines**, la prise en compte du numérique a fait évoluer les champs disciplinaires pour faire apparaître ce qu'on appelle les **humanités numériques** ( *digital humanities* en anglais).
Voici quelques exemples que nous vous proposons, n'hésitez pas à proposer d'autres exemples dans le forum de discussion :
* Dans les **médias** : nouveau sous-métier de journalisme : les **data-journalistes**
	* [data-visualisation](http://www.lemonde.fr/data-visualisation/)
	* [journalisme de données](http://fr.wikipedia.org/wiki/Journalisme_de_données)
* Dans la **santé** : (imagerie, dossier numérique du patient, ...)
	* [simulation](https://interstices.info/jcms/c_21525/simulation-de-loperation-de-la-cataracte)
* En **histoire, sociologie, linguistique** : *fouille de données*
	* [fouille de données](http://www.youtube.com/watch?feature=player_embedded&v=tp4y-_VoXdA)
* En **art et culture** :
	* [Le Fresnoy](http://www.lefresnoy.net/fr/Le-Fresnoy/presentation)
* Dans l'**enseignement** : (outils numérique d'accompagnement scolaire, MOOC,...):
	* [FUN](https://www.france-universite-numerique-mooc.fr/cours/)
* En fouille archéologique :  une réalisation prestigieuse réalisée à Lille3 :
	* [vase qui parle](http://bsa.biblio.univ-lille3.fr/blog/2013/09/exposition-le-vase-qui-parle-au-palais-des-beaux-arts-de-lille/)
}
""")
        questions = pygift.parseFile(io_gift)
        io_gift.close()

        d = yattag.Doc()
        d.asis('<!DOCTYPE html>')
        with d.tag('html'):
            with d.tag('head'):
                d.stag('meta', charset="utf-8")
                d.stag('link', rel="stylesheet", href="../../static/css/bootstrap.min.css")
                d.stag('link', rel="stylesheet", href="../../static/css/modules.css")
                d.stag('link', rel="stylesheet", href="../../static/css/jasny-bootstrap.min.css", media="screen")

        with d.tag('h2'):
            d.text(str(questions[0].answers.__class__))

        for q in questions:
            q.toHTML(d,True)

        for q in questions:
            q.toHTML(d,False)

        self.assertEqual(len(questions),1,"More than one Question for 'TestSimpleText'")

        # TEST HTML
        soup = BeautifulSoup(d.getvalue(), 'html.parser')
        for i,form in enumerate(soup.find_all('form')):
            self.assertEqual(form.h3['class'][0], u'questiontitle'," Not h3 or not good class for h3")
            for j,div in enumerate(form.find_all('div')):
                if j == 0 :
                    self.assertEqual(div['class'][0], u'questiontext',"Not div or not good class for 1rst div")
                if (j == 1):
                        self.assertEqual(div['class'][0], u'global_feedback')


        out =  open(TEST_GIFT_DIR+"texte.html", "w")
        out.write (d.getvalue())
        out.close()

        print("[GiftParsingHTMLTestCase]-- check_text OK --")

    def TestSimpleText2(self):
        io_gift = StringIO("""
::Le numérique au quotidien::Les microprocesseurs, les ordinateurs ont envahi notre quotidien. Pour chacun des domaines suivants, cherchez des exemples où le numérique a permis des évolutions notables :
- Domotique
- Transports
- Vêtements
- Médical / paramédical
Après avoir effectué vos recherches, copier dans la fenêtre de rendu 1 lien pour au moins 3 des 4 thèmes proposés (un lien par thème).
{####
# le numérique au quotidien
Quelques exemples que nous vous proposons au cas où vous n'auriez rien trouvé, ...
La **domotique** est un domaine en pleine expansion qui vise à équiper numériquement notre maison :
- [nest](https://nest.com/fr/)
- [domotique](http://fr.wikipedia.org/wiki/Domotique)
Pour les **transports**, les ordinateurs de bord sont depuis longtemps présents dans les voitures, de plus en plus ils sont responsables de notre sécurité :
- [electrostabilisateur]( http://fr.wikipedia.org/wiki/electrostabilisateur_programmé)
- [ordinateur de bord](http://fr.wikipedia.org/wiki/Ordinateur_de_bord)
Les **chaussures** : gadget ou réelle innovation ? Ce genre d'objet est de plus en plus présents dans nos vies :
 - [chaussures](http://www.linternaute.com/science/technologie/deja-demain/07/chaussure-intelligente/chaussure-intelligente.shtml)
Les **lentilles pour la vue** ?
 - [lentilles](http://www.zdnet.fr/actualites/google-apres-les-lunettes-connectees-les-lentilles-pour-le-diabete-39797148.htm)
}
""")
        questions = pygift.parseFile(io_gift)
        io_gift.close()

        d = yattag.Doc()
        d.asis('<!DOCTYPE html>')
        with d.tag('html'):
            with d.tag('head'):
                d.stag('meta', charset="utf-8")
                d.stag('link', rel="stylesheet", href="../../static/css/bootstrap.min.css")
                d.stag('link', rel="stylesheet", href="../../static/css/modules.css")
                d.stag('link', rel="stylesheet", href="../../static/css/jasny-bootstrap.min.css", media="screen")

        with d.tag('h2'):
            d.text(str(questions[0].answers.__class__))

        for q in questions:
            q.toHTML(d,True)

        for q in questions:
            q.toHTML(d,False)

        self.assertEqual(len(questions),1,"More than one Question for 'TestSimpleText2'")


        # TEST HTML
        soup = BeautifulSoup(d.getvalue(), 'html.parser')
        for i,form in enumerate(soup.find_all('form')):
            self.assertEqual(form.h3['class'][0], u'questiontitle'," Not h3 or not good class for h3")
            for j,div in enumerate(form.find_all('div')):
                if j == 0 :
                    self.assertEqual(div['class'][0], u'questiontext',"Not div or not good class for 1rst div")
                if (j == 1):
                        self.assertEqual(div['class'][0], u'global_feedback')

        print("[GiftParsingHTMLTestCase]-- check_text OK --")


        out =  open(TEST_GIFT_DIR+"texte2.html", "w")
        out.write (d.getvalue())
        out.close()

    def TestAnswerArea(self):
        #INITIALISATION
        d = yattag.Doc()
        d.asis('<!DOCTYPE html>')
        with d.tag('html'):
            with d.tag('head'):
                d.stag('meta', charset="utf-8")
                d.stag('link', rel="stylesheet", href="../../static/css/bootstrap.min.css")
                d.stag('link', rel="stylesheet", href="../../static/css/modules.css")
                d.stag('link', rel="stylesheet", href="../../static/css/jasny-bootstrap.min.css", media="screen")

# AVEC UNE RÉPONSE SIMPLE
        io_simple = StringIO("""
::first paret of text of Q2::
//comment in Q2
second part of text of Q2
My Question{
=2 =Q2 =Question2
} other part
        """)

        questions = pygift.parseFile(io_simple)
        io_simple.close()

        with d.tag('h2'):
            d.text(str(questions[0].answers.__class__))

        for q in questions:
            q.toHTML(d,True)

        for q in questions:
            q.toHTML(d,False)

        self.assertEqual(len(questions),1,"More than one Question for 'TestAnswerArea 1'")

        # AVEC UNE RÉPONSE AU MILIEU DU TEXTE

        io_in = StringIO("""
blabla {} with tail
""")

        questions = pygift.parseFile(io_in)
        io_in.close()

        with d.tag('h2'):
            d.text(str(questions[0].answers.__class__))

        for q in questions:
            q.toHTML(d,True)

        for q in questions:
            q.toHTML(d,False)

        self.assertEqual(len(questions),1,"More than one Question for 'TestAnswerArea 1'")


        out =  open(TEST_GIFT_DIR+"areaAnswer.html", "w")

        #FERMETURE ET ECRITURE DU FICHIER
        out.write (d.getvalue())
        out.close()

    def TestNumerical(self):

        d = yattag.Doc()
        d.asis('<!DOCTYPE html>')
        with d.tag('html'):
            with d.tag('head'):
                d.stag('meta', charset="utf-8")
                d.stag('link', rel="stylesheet", href="../../static/css/bootstrap.min.css")
                d.stag('link', rel="stylesheet", href="../../static/css/modules.css")
                d.stag('link', rel="stylesheet", href="../../static/css/jasny-bootstrap.min.css", media="screen")

        #NUMERICAL ANSWER
        io_num = StringIO("""
::Num1::
When was Ulysses S. Grant born?{#1822:5}

::Num2::
What is the value of pi (to 3 decimal places)? {#3.141..3.142}.

::Num3::
When was Ulysses S. Grant born? {#
=1822:0
=%50%1822:2
}

::Num4::
1 2 ou 3 ? {#2}
}
        """)


        questions = pygift.parseFile(io_num)
        io_num.close()

        for q in questions:
            with d.tag('h2'):
                d.text(str(questions[0].answers.__class__))
            q.toHTML(d,True)

        for q in questions:
            q.toHTML(d,False)

        out =  open(TEST_GIFT_DIR+"numerical.html", "w")

        #FERMETURE ET ECRITURE DU FICHIER
        out.write (d.getvalue())
        out.close()

    def TestMatch(self):

        d = yattag.Doc()
        d.asis('<!DOCTYPE html>')
        with d.tag('html'):
            with d.tag('head'):
                d.stag('meta', charset="utf-8")
                d.stag('link', rel="stylesheet", href="../../static/css/bootstrap.min.css")
                d.stag('link', rel="stylesheet", href="../../static/css/modules.css")
                d.stag('link', rel="stylesheet", href="../../static/css/jasny-bootstrap.min.css", media="screen")

        io_match = StringIO("""
::Match::
Match the following countries with their corresponding capitals. {
=Canada -> Ottawa
=Italy -> Rome
=Japan -> Tokyo
=India -> New Delhi
}
        """)
        questions = pygift.parseFile(io_match)
        io_match.close()

        with d.tag('h2'):
            d.text(str(questions[0].answers.__class__))

        for q in questions:
            q.toHTML(d,True)

        for q in questions:
            q.toHTML(d,False)

        out =  open(TEST_GIFT_DIR+"match.html", "w")

        #FERMETURE ET ECRITURE DU FICHIER
        out.write (d.getvalue())
        out.close()


    def TestMatch(self):

        d = yattag.Doc()
        d.asis('<!DOCTYPE html>')
        with d.tag('html'):
            with d.tag('head'):
                d.stag('meta', charset="utf-8")
                d.stag('link', rel="stylesheet", href="../../static/css/bootstrap.min.css")
                d.stag('link', rel="stylesheet", href="../../static/css/modules.css")
                d.stag('link', rel="stylesheet", href="../../static/css/jasny-bootstrap.min.css", media="screen")

        io_match = StringIO("""
::Les normes et leurs sigles::
**Classez ces modes de connexion du plus lent au plus rapide.**
3G,4G,H+,Edge
{
=3G -> 2
=4G -> 4
=H+ -> 3
=E (Edge) -> 1
####
## Les normes et leurs sigles
- Les modes de connexion du plus lent au plus rapide.
    - E (Edge) aussi appelé 2G, lent. Ce mode de connexion permet à peine de lire ses mails. Il ne permet pas une navigation fluide sur le Web.
    - 3G (3ème génération) permet de faire des recherches et de surfer sans trop attendre.
    - H+, est une amélioration de la 3G. il est plus rapide que le wifi si les connexions sont optimales. Et l'accès à la musique en ligne où aux vidéos peut être envisagé.
    - 4G, plus rapide que le wifi si les connexions sont optimales. À condition bien sûr que cette connexion soit de bonne qualité ("plusieurs petites briques"), l'accès à internet est alors très fluide, et les jeux en ligne, les vidéos en streaming ou le téléchargement de gros fichiers devient possible.
Notez bien que pour pouvoir bénéficier d'une connexion 4G, il faut :
 - que cette connexion soit disponible là où vous vous trouvez,
 - que votre smartphone soit équipé d'une antenne 4G, c'est loin d'être le cas sur tous les modèles y compris sur des appareils récents.
 }
        """)

        questions = pygift.parseFile(io_match)
        io_match.close()

        with d.tag('h2'):
            d.text(str(questions[0].answers.__class__))

        for q in questions:
            q.toHTML(d,True)

        for q in questions:
            q.toHTML(d,False)

        out =  open(TEST_GIFT_DIR+"minMaxListing.html", "w")

        #FERMETURE ET ECRITURE DU FICHIER
        out.write (d.getvalue())
        out.close()


    def runTest(self):
        try :
            os.makedirs(TEST_GIFT_DIR)
        except :
            pass
        self.TestUnChoix()
        self.TestMultiple()
        self.TestSimpleText()
        self.TestSimpleText2()
        self.TestMatch()
        self.TestAnswerArea()
        self.TestNumerical()
        self.TestMinMaxListing()

# class GiftParsingEDXTestCase(unittest.TestCase):


# Main
if __name__ == '__main__':
    unittest.main(verbosity=1)
