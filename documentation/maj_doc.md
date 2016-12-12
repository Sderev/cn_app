# Mettre à jour la documentation


## Installation

La documentation est générée avec [Sphinx](http://www.sphinx-doc.org) et l'utilisation d'un parser additionnel, Recommonmark, pour le support des fichiers markdown (voir les explications [ici](http://searchvoidstar.tumblr.com/post/125486358368/making-pdfs-from-markdown-on-readthedocsorg-using)). Ensuite les étapes sont:

- installation des dépendances : les librairies nécessaires sont intégrées dans la fichier `requirements.txt` situé à la racine du code source, et sont donc installées par la commande `pip install - r requirements.txt` si vous ne l'avez pas déjà exécutée.
- par ailleurs les fichiers de configuration de Sphinx sont intégré dans le code source: `Makefile` à utilser tel quel, et le `conf.py.template` à modifier de la façon suivante:
    - placez-vous dans le dossier `documentation` de votre installation
    - copier le fichier `conf.py.template` en nommant la copie `conf.py` et modifier y le chemin absolu (vers ligne 21) vers le dossier `src` du code source d'Esc@pad (utilisé pour l'autodocumentation du module `src/model.py`)
    - les autres éléments pour le parsing du markdown sont déjà ajoutés.

Le dossier `documentation/_build` est lié à un alias dans la configuration Apache qui sert ce dossier à l'adresse `escapad.univ-lille3.fr/documentation`

## Régénérer la documentation

La structure de la documentation est définie dans le fichier `documentation/index.rst` qui permet d'inclure les autres fichiers en tant que section simplement en ajoutant leur nom à la suite de la commande  sans préciser leur suffixe.

Pour mettre à jour la documentation:

- `$ cd documentation`
- `$ make html` permet alors de régénérer la documentation dans le dossier `_build`
