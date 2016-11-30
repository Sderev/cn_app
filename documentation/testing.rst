Couverture de tests
===================

Dans cette section nous abordons les tests unitaires développés afin de pérenniser et rendre plus efficace le développement des fonctionnalités d'Esc@pad.


Principes et usage des tests développés
---------------------------------------

La stratégie de tests présente différent aspects:

1. le test du parsing des fichiers de code source de cours qui aboutit à la construction d'un modèle de cours (cf :class:`model.Module`); dans ce cas on compare les objets générés avec un objet de contrôl sérialisé (`tests.config.json`)
2. le test de la génération des exports Web (cf :mod:`cnExport`), IMS-CC (:mod:`toIMS`), et EDX (:mod:`toEDX`); ici ce seront les archives générés qui seront comparés avec des archives de contrôle.
3. le test des web services développés en Django: dans ce cas il s'agit de contrôler la manipulation des fichiers et l'exécution des appels web.
4. enfin, une stratégie de test plus granulaire qui consiste à tester chaque méthode séparemment en vérifiant la cohérence des entrées et sorties (WIP).


Développer / écrire de nouveaux tests
-------------------------------------

Tests opérationnels
~~~~~~~~~~~~~~~~~~~

Le point 1 de la section précédente (test du parsing) est développé dans le module :mod:`tests`:

- les tests écrits utilisent le framework de test Python `UnitTest <https://docs.python.org/2/library/unittest.html>`_
- le fichier ``module_test.md`` est le fichier source de test
- le fichier ``tests.config.json`` est chargé comme objet de contrôle

Le test :class:`tests.ModuleParsingTestCase` récupère d'un côté l'objet sérialisé de contrôle, de l'autre parse le fichier de test pour produire un objet `Module` de test (cf :func:`tests.setUp`). La correspondance entre les champs est ensuite comparée dans la fonction :func:`tests.runTest`, en prenant soin de comparer de manière progressive, en comparant d'abord simplement le nombre de sections, puis en comparant l'exact identité de l'objet de test et de l'objet de contrôle.

Ajouter des tests
~~~~~~~~~~~~~~~~~

Le test :class:`tests.HtmlGenerationTestCase` (en cours) vise quant à lui à comparer un export web de contrôle avec un export web généré à partir du fichier source de test. Pour développer un nouveau test, il est possible de définir des sous-classes de :class:`tests.ModuleParsingTestCase`, ce qui permet de réutiliser le mécanisme de lancement du test (setUp). 

Documentation des tests
-----------------------

.. automodule:: tests
    :members:
