Contribuer au code d'Esc@pad
============================

Cette section est dédiée aux contributeurs du code d'Escapad et décrit les besoins prioritaires déjà identifiés.
Au 15 décembre 2016, Esc@pad a atteint son premier objectif: faire la preuve du concept d'une chaine éditoriale intégrée permettant de créer à partir d'un fichier source en format texte un contenu pédagogique riche disponible en plusieurs formats (Web, EDX, Moodle). Les besoins prioritaires se décomposent pour l'instant en 3 grands catégories (détaillés ci-après à la suite de l'architecture globale du code)


Architecture
------------

Le code d'Escapad est décomposé comme suit:

- le parser, qui consiste en un script ``cnExport.py`` qui se base sur un modèle (``model.py``) pour générer les différents exports.
- l'application Web qui exécute le script du parser via les modules Django situé dans les dossiers:
    - cn_app : paramètres globaux
    - escapad : la "sous-application" qui gère les dépôts


Couverture de tests
--------------------

La stratégie de tests présente différent aspects:

1. le test du parsing des fichiers de code source de cours qui aboutit à la construction d'un modèle de cours (cf :class:`model.Module`); dans ce cas on compare les objets générés avec un objet de contrôl sérialisé (`tests.config.json`)
2. le test de la génération des exports Web (cf :mod:`cnExport`), IMS-CC (:mod:`toIMS`), et EDX (:mod:`toEDX`); ici ce seront les archives générés qui seront comparés avec des archives de contrôle.
3. le test des web services développés en Django: dans ce cas il s'agit de contrôler la manipulation des fichiers et l'exécution des appels web.
4. enfin, une stratégie de test plus granulaire qui consiste à tester chaque méthode séparemment en vérifiant la cohérence des entrées et sorties (WIP).

Pour lancer les tests:

- ``$ cd tests``
- ``$ python tests.py``


Tests globaux controllant le résultat
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ce type de test est développé dans le module :mod:`tests`:

- les tests écrits utilisent le framework de test Python `UnitTest <https://docs.python.org/2/library/unittest.html>`_
- le fichier ``module_test.md`` est le fichier source de test
- le fichier ``tests.config.json`` est chargé comme objet de contrôle

Le test :class:`tests.ModuleParsingTestCase` récupère d'un côté l'objet sérialisé de contrôle, de l'autre parse le fichier de test pour produire un objet `Module` de test (cf :func:`tests.setUp`). La correspondance entre les champs est ensuite comparée dans la fonction :func:`tests.runTest`, en prenant soin de comparer de manière progressive, en comparant d'abord simplement le nombre de sections, puis en comparant l'exact identité de l'objet de test et de l'objet de contrôle.

Ajouter des tests
~~~~~~~~~~~~~~~~~

Le test :class:`tests.HtmlGenerationTestCase` (en cours) vise quant à lui à comparer un export web de contrôle avec un export web généré à partir du fichier source de test. Pour développer un nouveau test, il est possible de définir des sous-classes de :class:`tests.ModuleParsingTestCase`, ce qui permet de réutiliser le mécanisme de lancement du test (setUp).

Tests unitaires au niveau des méthodes du parser
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Un autre type de test doit être développé pour permettre de vérifier le bon fonctionnement du parsing à partir de la formalisation du bon déroulement de chaque étape du parsing au niveau des méthodes des classes définies dans ``src/model.py``.



Documentation des tests
~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: tests
    :members:





Amélioration du parser
----------------------

Il s'agit ici de consolider le code de la partie parser (cf dossier `src`) selon différents aspects:
- intégrer la librairie [pygiftparser](https://github.com/mtommasi/pygiftparser) afin de remplacer `fromGIFT.py` pour le parsing du GIFT.
- étendre la librairie [pygiftparser](https://github.com/mtommasi/pygiftparser) pour augmenter la couverture de la spécification GIFT (aujourd'hui partielle)
- proposer une version du script `cnExport.py` pour produire un site mono-module sans page d'accueil
- homégénéiser et factoriser le code de génération des archives:
  - passer la génération de l'IMS-CC via un template Jinja2 (comme pour le web et EDX)
  - coder en objet ces "Exporters" qui peuvent se décliner en IMSExporter, WebExporter, etc.


Améliorer application Web (sous Django)
---------------------------------------

Enrichir les fonctionalités, en particulier du côté de l'application web en Django (contenue dans les sous-dossiers `cn_app` et `escapad`):

- proposer une version sans persistence et sans Git et prenant directement un seul fichier markdown:
    - un formulaire prenant un fichier markdown en entrée, plus qqs champs calqués sur les options de `src/cnExport.py` (le script exécuté)
    - validation
    - création d'un dossier temporaire et upload du fichier à l'intérieur
    - génération du site en mode mono-module sans page d'accueil
    - compression en zip du dossier compilé
    - renvoi à l'usager du zip
    - effacement du dossier temporaire
- passer en web service la version ci-avant
- développer une interface HTML5 permettant d'écrire du markdown+ gift avec panel de rendu reprenant l'export web des modules (épuré ?)
- coloration syntaxique du GIFT
- etc. etc. :)
