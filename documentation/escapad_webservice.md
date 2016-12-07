Esc@pad Web Service : Architecture et administration
====================================================


# Architecture



# Administration
L'interface d'administration d'Escapad comprend 2 applications principales:

- Authentification et Autorisation
- Escapad et la gestion des Repository


## Ajout d'un compte utilisateur et gestion des droits

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

## Gestion des dépôts "Repository"

En cliquant sur "Repository" depuis l'acueuil d'Escapad, on arrive sur la page listant tous les dépôts, avec le lien "build" pour générer et le lien "visit" pour visiter la version mini-site web de chaque dépôt de cours. Depuis cette page 3 actions d'administration sont possibles:
- en cliquant sur "Ajouter Repository", on arrive sur le formulaire permettant de créer un nouveau dépôt simplement en ajoutant le lien "git" de ce dépôt.
- pour supprimer un dépôt, cochez la case devant le nom de ce dépôt, et dans la liste "Action", sélectionnez l'action "Supprimer les repositorys sélectionnés", puis faites "Envoyer". Un écran vous demande de confirmer, cliquez sur "oui je suis sûr"
- en cliquant sur le nom d'un dépôt, on arrive sur la fiche détaillée d'un dépôt. A noter que l'url git n'est plus modifiable une fois le dépôt créé, et que seul la branche par défaut est modifiable.
