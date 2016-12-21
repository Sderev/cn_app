Administration de la plateforme Esc@pad
=======================================


## Administration via l'interface web


L'interface d'administration d'Escapad, accessible à [`http://escapad.univ-lille3.fr/admin`](http://escapad.univ-lille3.fr/admin) comprend 2 applications principales:

- Authentification et Autorisation
- Escapad et la gestion des Repository


### Ajout d'un compte utilisateur et gestion des droits

Voyons comment ajouter un compte d'utilisateur disposant simplement des droits nécessaires pour **ajouter** et **modifier** un dépôt.

- Sous la bannière de l'application "Authentification et Autorisation", cliquez sur "Utilisateurs"
- Cliquez sur "Ajouter un utilisateur"
- donnez lui un nom et un mot de passe, par exemple "escapadeur/abcdefgh" et validez en cliquant sur "Enregistrer et continuer les modifications"
- vous arrivez sur la page de modification de l'utilisateur "escapadeur"
- cochez la case "Statut équipe" qui permet à cet utilisateur de se loguer sur l'interface d'administration d'Escapad
- Ensuite au niveau de la rubrique "Permission de l'utilisateur", ajoutez les 2 permissions "Can add repository" et "Can change repository":
    - en les sélectionnant depuis la zone "permissions disponibles",
    - puis en cliquant sur la flèche "￫ Choisir" qui a pour effet de déplacer les permissions sélectionnées dans la zone "Choix des permissions de l'utilisateur" (en cas d'ajout involontaire l'opération inverse est possible en cliquant sur "￩ Enlever")
- cliquez enfin sur "ENREGISTRER"

Le compte ainsi paramétré pourra 1) accéder à l'interface d'admin et donc voir la liste des dépôts ainsi que la fiche détaillée de chaque dépôt, 2) ajouter un dépôt, et 3) modifier la "branche par défaut" de tous les dépôts.

### Gestion des dépôts "Repository"

En cliquant sur "Repository" depuis l'acueuil d'Escapad, on arrive sur la page listant tous les dépôts, avec le lien "build" pour générer et le lien "visit" pour visiter la version mini-site web de chaque dépôt de cours. Depuis cette page 3 actions d'administration sont possibles:
- en cliquant sur "Ajouter Repository", on arrive sur le formulaire permettant de créer un nouveau dépôt simplement en ajoutant le lien "git" de ce dépôt.
- pour supprimer un dépôt, cochez la case devant le nom de ce dépôt, et dans la liste "Action", sélectionnez l'action "Supprimer les repositorys sélectionnés", puis faites "Envoyer". Un écran vous demande de confirmer, cliquez sur "oui je suis sûr"
- en cliquant sur le nom d'un dépôt, on arrive sur la fiche détaillée d'un dépôt. A noter que l'url git n'est plus modifiable une fois le dépôt créé, et que seul la branche par défaut est modifiable.

## Administration sur le serveur escapad

### Se connecter

```
$ ssh escapad@escapad.univ-lille3.fr
```
Ensuite une fois logué, se placer dans le dossier `cnapp`:
```
escapad@escapad:~$ cd cnapp/
escapad@escapad:~$ pwd (pour savoir où je suis)
/home/escapad/cnapp
```

Ce dossier contient 3 sous-dossiers ayant les droits suivants:
```
escapad@escapad:~/cnapp$ ll
total 12
drwxr-xr-x 13 escapad  www-data 4096 nov.  30 17:26 cn_app
drwxr-xr-x  6 escapad  escapad  4096 sept.  5 12:55 cnapp_env
drwxrwxr-x  3 www-data escapad  4096 déc.  15 16:49 data
```

- `cn_app` contient le code
- `cnapp_env` contient les binaires du virtualenv, i.e de l'environnement Python avec toutes les dépendences
- `data` contient les données:
    - `db.sqlite3` le fichier de base de données en SQLite
    - `debug.log` le fichier de log Django (différent du fichier de log du script `cnExport` lui placé dans `cn_app/logs`)
    - `repo-data` dossier ou sont synchronisés et générés les dépôts de cours
```
ll data/
total 376
-rwxrwxr-x 1 www-data escapad  82944 déc.  15 16:49 db.sqlite3
-rwxrwxr-x 1 www-data escapad 286345 déc.  15 16:49 debug.log
drwxrwxr-x 4 www-data escapad   4096 sept. 22 17:24 repo-data
```

### Activer l'environnement

Depuis le dossier `cnapp`:
```
escapad@escapad:~/cnapp$ source cnapp_env/bin/activate
(cnapp_env)escapad@escapad:~/cnapp$
```

NB : **(cnapp_env)** devant `escapad@escapad:` montre que l'environnement est activé

### Mettre à jour le code

```
(cnapp_env)escapad@escapad:~/cnapp$ cd cn_app/
(cnapp_env)escapad@escapad:~/cnapp/cn_app$ git status
    Sur la branche develop
    Votre branche est à jour avec 'origin/develop'.
    rien à valider, la copie de travail est propre
(cnapp_env)escapad@escapad:~/cnapp/cn_app$ git pull origin develop
    Depuis https://github.com/CultureNumerique/cn_app
     * branch            develop    -> FETCH_HEAD
    Already up-to-date.
(cnapp_env)escapad@escapad:~/cnapp/cn_app$
```

### Créer un user admin

En Django == superuser

En étant dans `cn_app` et avec l'env activé:
```
(cnapp_env)escapad@escapad:~/cnapp/cn_app$  ./manage.py createsuperuser
Username (leave blank to use 'escapad'): numerix
Email address:
Password:
Password (again):
Superuser created successfully.

```

### Copier en local un export web et le zipper

#### Trouver sur escapad le dossier:

```
(cnapp_env)escapad@escapad:~/cnapp$ cd data/repo-data/sites/
(cnapp_env)escapad@escapad:~/cnapp/data/repo-data/sites$ ll
  total 80
  drwxr-xr-x 4 www-data www-data 4096 nov.  16 14:45 framagit_org__escapad__course_template_git
  drwxr-xr-x 8 www-data www-data 4096 sept. 27 08:22 framagit_org__tommasi__cn_modules_git
  drwxr-xr-x 4 www-data www-data 4096 sept. 30 12:46 github_com__alainpreux__al1kb-test_git
   ....
```
Ensuite copier le chemin vers le dossier choisi:
```
$ cd github_com__alainpreux__al1kb-test_git/
$ pwd
/home/escapad/cnapp/data/repo-data/sites/github_com__alainpreux__al1kb-test_git
```

#### Le copier en local avec scp

Se placer sur le dossier cible en local:

```
$ cd /tmp/
$ mkdir exportWeb
$ cd exportWeb/
```

La commande suit le schéma:
```
scp -r login@nom_du_serveur:/chemin/vers/dossier /chemin/dossier/local/cible/
```

Pour notre dossier exemple:
```
$ scp -r escapad@escapad.univ-lille3.fr:/home/escapad/cnapp/data/repo-data/sites/github_com__alainpreux__al1kb-test_git .
```

Le dossier est donc copié localement:
```
flimpens@U201609120:/tmp/exportWeb$ ll
total 28
drwxr-xr-x  4 flimpens presidence  4096 déc.  16 11:40 ./
drwxrwxrwt 21 root     root       16384 déc.  16 11:39 ../
drwxr-xr-x  4 flimpens presidence  4096 déc.  16 11:40 github_com__alainpreux__al1kb-test_git/
drwxr-xr-x  8 flimpens presidence  4096 déc.  15 17:24 github_com__culturenumerique__cn_modules_git/
flimpens@U201609120:/tmp/exportWeb$
```

Pour zipper le dossier:
```
$ zip -r nom_fichier.zip dossier_a_zipper/

soit dans notre cas:

$ zip -r al1kb_test.zip github_com__alainpreux__al1kb-test_git/
```

## Mise à jour de la documentation

### Structuration

La documentation est générée avec [Sphinx](http://www.sphinx-doc.org) et l'utilisation d'un parser additionnel, Recommonmark, pour le support des fichiers markdown (voir les explications [ici](http://searchvoidstar.tumblr.com/post/125486358368/making-pdfs-from-markdown-on-readthedocsorg-using)).

Ensuite les étapes sont:

- installation des dépendances : les librairies nécessaires sont intégrées dans le fichier `requirements.txt` situé à la racine du code source, et sont donc installées par la commande `pip install - r requirements.txt` si vous ne l'avez pas déjà exécutée.
- par ailleurs les fichiers de configuration de Sphinx sont intégrés dans le code source: `Makefile` à utilser tel quel, et le `conf.py.template` à modifier de la façon suivante:
    - placez-vous dans le dossier `documentation` de votre installation
    - copier le fichier `conf.py.template` en nommant la copie `conf.py` et y modifier le chemin absolu (vers ligne 21) vers le dossier `src` du code source d'Esc@pad (utilisé pour l'autodocumentation du module `src/model.py`)
    - les autres éléments pour le parsing du markdown sont déjà ajoutés.

Le dossier `documentation/_build` est lié à un alias dans la configuration Apache qui sert ce dossier à l'adresse `escapad.univ-lille3.fr/documentation`

### Régénérer la documentation

La structure de la documentation est définie dans le fichier `documentation/index.rst` qui permet d'inclure les autres fichiers en tant que section simplement en ajoutant leur nom à la suite de la commande  sans préciser leur suffixe.

Pour mettre à jour la documentation

- connecter vous en ssh sur le serveur escapad
- activer l'environnement
- `$ cd documentation`
- `$ make html` permet alors de régénérer la documentation dans le dossier `_build`. En cas de doute, ne pas hésiter à effacer le dossier `_build`
