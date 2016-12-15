Contribuer au code d'Esc@pad
============================

Cette section est dédiée aux contributeurs du code d'Escapad et décrit les besoins prioritaires déjà identifiés

Au 15 décembre 2016, Esc@pad a atteint son premier objectif: faire la preuve du concept d'une chaine éditoriale intégrée permettant de créer à partir d'un fichier source en format texte un contenu pédagogique riche disponible en plusieurs formats (Web, EDX, Moodle). Les besoins prioritaires se décomposent pour l'instant en 2 grands catégories détaillés ci-après (et constituent en quelques sortes 2 thèmes principaux selon lesquels le travail de développement peut s'articuler).

## Amélioration du parser et tests

Il s'agit ici de consolider le code de la partie parser (cf dossier `src`).

En premier lieu, il faut étendre la couverture de tests sur ce module parser, cf chapitre [développement des tests Escapad](testing.html).

Ensuite le code du parser lui-même peut être amélioré selon différents aspects:
- intégrer la librairie [pygiftparser](https://github.com/mtommasi/pygiftparser) afin de remplacer `fromGIFT.py` pour le parsing du GIFT.
- étendre la librairie [pygiftparser](https://github.com/mtommasi/pygiftparser) pour augmenter la couverture de la spécification GIFT (aujourd'hui partielle)
- proposer une version du script pour produire un site mono-module sans page d'accueil
- homégénéiser et factoriser le code de génération des archives:
  - passer la génération de l'IMS-CC via un template Jinja2 (comme pour le web et EDX)
  - coder en objet ces "Exporters" qui peuvent se décliner en IMSExporter, WebExporter, etc.


## Fonctionnalités appli Web

Enrichir les fonctionalités, en particulier du côté de l'application web en Django (contenue dans les sous-dossiers `cn_app` et `escapad`):

- proposer une version sans persistence et monofichier du parsing:
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
