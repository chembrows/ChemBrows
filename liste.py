#!/usr/bin/python
# -*-coding:Utf-8 -*

import os
import sys
#import datetime
#import random

from PyQt4 import QtSql

#Modules perso
#from misc import simpleChar, md4Function


def creationBdd(logger):

    """Crée la bdd et ses tables si elle n'existe pas"""

    if os.path.exists("fichiers.sqlite") == False:
        logger.info("La bdd n'existe pas. Création.")

    # On crée une bdd ou on s'y connecte si elle existe
    #bdd = sqlite3.connect("fichiers.sqlite") # ouverture de la base
    #bdd.row_factory = sqlite3.Row # accès aux colonnes par leur nom, pas par leur index

    #c = bdd.cursor() # obtention d'un curseur

    # Création des tables si elles n'existent pas
    #c.execute("CREATE TABLE IF NOT EXISTS videos (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, \
               #name_simple TEXT, vote INTEGER, path TEXT, thumb TEXT, \
               #date TEXT, md4 TEXT, size INTEGER, date_add TEXT, waited INTEGER)")
    #c.execute("CREATE TABLE IF NOT EXISTS tags (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")
    #c.execute("CREATE TABLE IF NOT EXISTS videos_tags (id_tag INTEGER, id_video INTEGER)")
    #c.execute("CREATE TABLE IF NOT EXISTS actors (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, name_simple TEXT)")
    #c.execute("CREATE TABLE IF NOT EXISTS videos_actors (id_actor INTEGER, id_video INTEGER)")

    #bdd.commit()
    #c.close()
    #bdd.close()

    query = QtSql.QSqlQuery("fichiers.sqlite")
    query.exec_("CREATE TABLE IF NOT EXISTS papers (id INTEGER PRIMARY KEY AUTOINCREMENT, percentage_match TEXT, \
                 title TEXT, date TEXT, journal TEXT, abstract TEXT)")



##def effacerBdd(logger):

    ##"""Fonction qui efface le fichier fichiers.sqlite"""

    ##logger.info("Effacement de la bdd")
    ##bdd = sqlite3.connect("fichiers.sqlite") # ouverture de la base
    ##c = bdd.cursor() # obtention d'un curseur
    ##c.execute("DELETE FROM videos")
    ##c.execute("DELETE FROM tags")
    ##c.execute("DELETE FROM videos_tags")
    ##c.execute("DELETE FROM sqlite_sequence") # On efface l'index
    ##c.execute("DELETE FROM actors") # On efface l'index
    ##c.execute("DELETE FROM videos_actors") # On efface l'index
    ##bdd.commit()
    ##c.close()
    ##bdd.close()

    ###On vide le dossier des screenshots
    ##logger.info("Effacement du dossier des screens")
    ##os.chdir('./screens')
    ##for picture in os.listdir('.'):
        ##os.remove(os.path.abspath(picture))

    ##os.chdir(os.path.dirname(sys.argv[0]))


#def effacerFichier(list_vids, logger):

    #"""Fct effaçant un/plusieurs fichiers de la bdd et du disque"""

    ##bdd = sqlite3.connect("fichiers.sqlite") # ouverture de la base
    ##bdd.row_factory = sqlite3.Row # accès aux colonnes par leur nom, pas par leur index

    ##c = bdd.cursor() # obtention d'un curseur

    ##for each_video in list_vids:

        ###On efface ts les tags associés à la vid
        ##tags = obtainTag(each_video)
        ##for each_tag in tags:
            ##removeTag(each_video, each_tag, logger)

        ###On efface ts acteurs associés à la vid
        ##actors = obtainActors(each_video)
        ##for each_actor in actors:
            ##removeActor(each_video, each_actor, logger)

        ##c.execute("SELECT path, thumb FROM videos WHERE id = ?", (each_video,))

        ##donnees = c.fetchone()

        ###On efface physiquement le fichier ds le try
        ##try:
            ###On récupère le path d'origine du fichier,
            ###de la thumb, puis de la mosaïque.
            ##source_path = donnees["path"]
            ##thumb_path = donnees["thumb"]

            ##mosaic_path = thumb_path.replace("_thumb.png", "_mosaic.png")

            ###Avec cette instruction, on récupère le nom du fichier, en enlevant le
            ###chemin absolu. NOTE: liste[-1] donne le dernier item d'une liste !!
            ###TODO: pouvoir définir la poubelle serait bien
            ###TODO: travailler sur la poubelle du disque en question
            ###dest_path = os.path.abspath("/media/data/.Trash-1000/files/" + source_path.split("/")[-1])

            ###On déplace le fichier ds la corbeille, on ne le supprime pas vraiment
            ###On supprime aussi la thumb et la mosaïque
            ###On utilise shutil car il est possible que les fichiers soient sur des
            ###systèmes de fichiers différents. C'est un déplacement, pas un simple
            ###renommage
            ###shutil.move(source_path, dest_path)
            ###shutil.move(thumb_path, os.path.abspath(dest_path + "_thumb.png"))
            ###shutil.move(mosaic_path, os.path.abspath(dest_path + "_mosaic.png"))
            ##logger.info("Effacement physique du fichier {0} et de ses images".format(source_path))
            ##os.remove(source_path)
            ##os.remove(thumb_path)
            ##os.remove(mosaic_path)

        ###TODO: trouver l'exception
        ##except:
            ##logger.error("Erreur lors de l'effacement du fichier, fichier peut-être non accessible")

        ##logger.info("Effacement du fichier {0} de la bdd".format(source_path))
        ###On efface le fichier de la bdd même si le try échoue 
        ##c.execute("DELETE FROM videos WHERE id = ?", (each_video,))
        ##c.execute("DELETE FROM videos_tags WHERE id_video = ?", (each_video,))
        ##c.execute("DELETE FROM videos_actors WHERE id_video = ?", (each_video,))

    ##bdd.commit()
    ##c.close()
    ##bdd.close()


#def deleteFileFromBdd(list_vids, logger):

    #"""Fct effaçant un/plusieurs fichiers de la bdd uniquement"""

    ##bdd = sqlite3.connect("fichiers.sqlite") # ouverture de la base
    ##bdd.row_factory = sqlite3.Row # accès aux colonnes par leur nom, pas par leur index

    ##c = bdd.cursor() # obtention d'un curseur

    ##for each_video in list_vids:

        ###On efface ts les tags associés à la vid
        ##tags = obtainTag(each_video)
        ##for each_tag in tags:
            ##removeTag(each_video, each_tag, logger)

        ###On efface ts acteurs associés à la vid
        ##actors = obtainActors(each_video)
        ##for each_actor in actors:
            ##removeActor(each_video, each_actor, logger)
        ##c.execute("SELECT path, thumb FROM videos WHERE id = ?", (each_video,))

        ##donnees = c.fetchone()

        ###On efface le fichier de la bdd
        ##logger.info("Effacement du fichier {0} de la bdd".format(donnees['path']))
        ##c.execute("DELETE FROM videos WHERE id = ?", (each_video,))
        ##c.execute("DELETE FROM videos_tags WHERE id_video = ?", (each_video,))
        ##c.execute("DELETE FROM videos_actors WHERE id_video = ?", (each_video,))

    ##bdd.commit()
    ##c.close()
    ##bdd.close()


#def verifAccess(path):

    #"""Appelée par view_delegate.py.
    ##Sert à vérifier que le path est accessible"""

    ###On vérifie que le chemin ne soit pas vide
    ###et qu'il est accessible
    ##if path is not None and os.path.exists(path):
        ##return True
    ##else:
        ##return False


#def renameFile(ancien_nom, nouveau_nom, parent_bdd):

    #"""Fct qui renomme un fichier, en bdd d'abord, ac la
    ##mise à jour de name, name_simple et du path, puis physiquement
    ##si le fichier est accessible.
    ##ATTENTION : le nom du fichier n'est pas encore mis à jour dans
    ##la bdd  à l'appel de la fct."""

    ###On ferme ici la connexion à la bdd de la fenêtre principale
    ###car on ne peut pas le faire ailleurs
    ##parent_bdd.close()

    ##bdd = sqlite3.connect("fichiers.sqlite") # ouverture de la base
    ##bdd.row_factory = sqlite3.Row # accès aux colonnes par leur nom, pas par leur index

    ##c = bdd.cursor() # obtention d'un curseur

    ##c.execute("SELECT id, path FROM videos WHERE name = ?", [ancien_nom])

    ##path = c.fetchone()['path']

    ##if path is not None and os.path.exists(path):

        ###TODO: extension .mpeg
        ##allowed_types = ['avi', 'mkv', 'wmv', 'mov', 'mp4', 'm4v', 'mpeg', 'mpg', 'flv']

        ##if nouveau_nom[-3:] not in allowed_types:
            ##extension = ancien_nom.split(".")[-1]
            ##if extension in allowed_types:
                ##nouveau_nom = nouveau_nom + "." + extension
            ##else:
                ##nouveau_nom = ancien_nom


        ###On modifie la dernière partie du path, soit le nom du fichier
        ##new_path = path.split("/")[:-1]
        ##new_path = "/".join(new_path) + "/" + nouveau_nom

        ##try:
            ###On renomme le fichier physiquement
            ##os.renames(path, new_path)

            ###On change le nom, le nom simple, et le path en bdd
            ##c.execute("UPDATE videos SET name = ?, path = ?, name_simple = ? WHERE name = ?", (nouveau_nom, new_path, simpleChar(nouveau_nom), ancien_nom))
            ##print("Nom modifié dans la bdd")
        ##except:
            ##print("Erreur : aucun changement effectué")

    ##else:
        ##print("Erreur : nom non modifié en bdd")

    ##bdd.commit()

    ##c.close()
    ##bdd.close()

    ##parent_bdd.open()


#def listing(list_dossier):

    #"""Retourne 2 listes : la liste des fichiers, et la liste des chemins
    ##des fichiers"""

    ###try:
    ###Voir la doc de os.walk pour ce passage. Cette fction retourne le tuple: (dirpath, dirnames, filenames)
    ###Trouvée sur http://forum.ubuntu-fr.org/viewtopic.php?id=177400

    ###Création de la liste des fichiers
    ##liste = list()
    ###Création de la liste des chemins correspondants aux fichiers
    ##liste_chemins = list()

    ###TODO: si dossier est un fichier, retourner les listes avec un seul
    ###index, pr ne pas avoir à créer une fct d'import de fichier
    ##if type(list_dossier) == str:
        ##list_dossier = [list_dossier]

    ###TODO: fichier de conf avec les fichiers autorisés.
    ###Si ça passe en conf, gérer les pb à la création des thumbs
    ###On définit le type de fichier à lister
    ##allowed_types = ['avi', 'mkv', 'wmv', 'mov', 'mp4', 'm4v', 'mpeg', 'mpg', 'flv']

    ##for each_dossier in list_dossier:
        ##tree = os.walk(each_dossier)
        ##for directory in tree:
            ##os.chdir(directory[0])

            ##for fichier in directory[2]:

                ##extension = fichier.split('.')[-1]

                ###Si l'extension du fichier n'est pas autorisée, 
                ###on ne liste pas le fichier
                ##if extension in allowed_types:
                    ##liste.append(fichier)
                    ##liste_chemins.append(os.path.abspath(fichier))

    ### On se remet dans le répertoire du script
    ##os.chdir(os.path.dirname(sys.argv[0]))
    ###remplissage(liste, liste_chemins)
    ##return liste, liste_chemins

    ##except OSError:
        ##print("Le dossier spécifié n'existe pas, ou n'est pas accessible")


#def verification(options, logger, callback=None):

    #"""Vérifie que les fichiers en bdd sont toujours présents dans
    ##le répertoire d'où ils ont été recensés. Sinon, on update le path
    ##en bdd. Si tous les répertoires surveillés existent et qu'un fichier
    ##en bdd n'est stocké nul part, on le supprime."""

    ###Liste ts les dossiers surveillés dans les préfs
    ##list_to_check = list()

    ###On se met ds le group de conf 'Watching'
    ##options.beginGroup("Watching")
    ###On fait la liste de ttes les clés pr les pathes
    ##pathes = options.allKeys()
    ##if pathes:
        ##for each_key in pathes:
            ###On récupère le path associé à chaque clé, et on l'ajoute à la liste
            ##list_to_check.append(options.value(each_key))
    ##options.endGroup()

    ###On ne peut effacer que si tous les dossiers
    ###surveillés existent
    ##effacer = True
    ##nbr_videos_added = 0
    ##for each_dossier in list_to_check:
        ##if not os.path.exists(each_dossier):
            ##effacer = False
            ##logger.info("Un des répertoires surveillés n'est pas accessible")
        ##nbr_videos_added += importation(each_dossier, logger, callback)

    ##liste, liste_chemins = listing(list_to_check)

    ###On crée un dico ac en clé les md4 des fichiers, en value les paths.
    ###comme ça, on a pas besoin de parcourir les listes, on peut accéder aux
    ###nouveaux paths grâce aux noms des fichiers
    ##dico_path = dict()

    ##for each_path in liste_chemins:
        ##dico_path[md4Function(each_path)] = each_path

    ### On se connecte à la bdd, elle existe forcément
    ##bdd = sqlite3.connect("fichiers.sqlite") # ouverture de la base
    ##bdd.row_factory = sqlite3.Row # accès aux colonnes par leur nom, pas par leur index

    ##c = bdd.cursor() # obtention d'un curseur

    ##c.execute("SELECT md4, path FROM videos")

    ##fichiers_del = 0
    ##fichiers_updated = 0

    ###Pour chaque ligne de la bdd, on vérifie que le path écrit en bdd correspond
    ###à un fichier existant. Sinon, on efface l'entrée de la bdd
    ##for ligne_bdd in c.fetchall():

        ##if effacer and ligne_bdd["md4"] not in dico_path.keys():
            ##c.execute("DELETE FROM videos WHERE md4= ?", (ligne_bdd["md4"],))
            ##logger.info("{0} effacé de la bdd".format(ligne_bdd['path']))
            ##fichiers_del += 1
        ##elif ligne_bdd["md4"] in dico_path.keys() and os.path.exists(ligne_bdd["path"]) == False:
            ##new_name = dico_path[ligne_bdd["md4"]].split("/")[-1]
            ##c.execute("UPDATE videos SET name= ?, name_simple = ?, path= ? WHERE md4= ?",
                    ##(new_name, simpleChar(new_name), dico_path[ligne_bdd["md4"]], ligne_bdd["md4"]))
            ##logger.info("{0} updaté dans la bdd. Dorénavant localisé: {1}".format(ligne_bdd['path'], dico_path[ligne_bdd["md4"]]))
            ##fichiers_updated += 1

    ##logger.info("{0} fichiers ajoutés à la bdd".format(nbr_videos_added))
    ##logger.info("{0} fichier(s) effacé(s)".format(fichiers_del))
    ##logger.info("{0} fichier(s) updaté(s)".format(fichiers_updated))

    ##bdd.commit()
    ##c.close()
    ##bdd.close()


#def importation(dossier, logger, callback=None):

    #"""On remplit la bdd avec les listes liste et liste_chemins.
    ##On vérifie que le fichier à ajouter n'est pas déjà en bdd. Sinon, on l'ajoute.
    ##Accepte aussi un callback en option, pour mettre à jour la progress bar du gui 
    ##lors de l'import"""

    ###On récupère la liste des fichiers et leur emplacement
    ###Uniquement des vidéos avec un type autorisé, la fct de listing
    ###s'occupe de vérifier
    ##logger.info("Importation du dossier {0}".format(dossier))
    ##liste, liste_chemins = listing(dossier)

    ##bdd = sqlite3.connect("fichiers.sqlite") # ouverture de la base
    ##bdd.row_factory = sqlite3.Row # accès aux colonnes par leur nom, pas par leur index

    ##c = bdd.cursor() # obtention d'un curseur

    ##nbr_videos_added = 0

    ###On récupère le nbr de fichiers à importer, pr la progress bar
    ##nbr_max = len(liste)

    ##for name, path in zip(liste, liste_chemins):

        ##md4 = md4Function(path) 

        ### On vérifie que le fichier n'existe pas déjà. Plus d'infos :
        ### http://stackoverflow.com/questions/2440147/how-to-check-the-existence-of-a-row-in-sqlite-with-python
        ##c.execute("SELECT md4 FROM videos WHERE md4= ?", (md4,))

        ###Si le fichier n'est pas présent, on l'ajoute à la bdd
        ###avec ttes les opérations qui vont avec
        ##if c.fetchone() is None:
            ##nbr_videos_added += 1

            ###On génère la miniature et la mosaïque
            ##screen.thumb(path, md4)
            ##screen.caps(path, md4)

            ###On crée des variables, plus lisibles, pr la requête sql
            ##date_modif = datetime.datetime.fromtimestamp(int(os.path.getmtime(path))).strftime('%Y-%m-%d %H:%M:%S')
            ##path_thumb = os.getcwd() + "/screens/{0}_thumb.png".format(md4)
            ##today = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S') 

            ##size = os.path.getsize(path)

            ###On insère aussi le nom sans accent, sans majuscule, dans un champ prévu pour faire les recherches
            ##logger.info("Insertion de {0} dans la bdd".format(path)) 
            ##c.execute("INSERT INTO videos(name, name_simple, path, thumb, date, md4, size, date_add) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                       ##(name, simpleChar(name), path, path_thumb, date_modif, md4, size, today))
        ##else:
            ##logger.debug("Fichier {0} déjà présent en bdd, rien à faire".format(name))

        ###On appelle le callback pr mettre à jour le pourcentage
        ###de la progress bar de la gui, au besoin
        ##if callback != None:
            ##callback((liste.index(name) + 1) * 100 / nbr_max, "({0}/{1})".format(liste.index(name) + 1, nbr_max), name, os.path.dirname(path))

    ### On place le commit en dehors de la boucle, ça va plus vite
    ###EN TEST, sorti le 18/03/12 de la boucle
    ##bdd.commit()
    ##c.close()
    ##bdd.close()

    ##return nbr_videos_added


#def regeneratePictures(logger, list_vids=None):

    #"""Fct qui régénére les images d'une liste de vids passée en paramètre,
    ##ou de tte la bdd si rien n'est passé en paramètre. ATTENTION, 
    ##on supprime ttes les images du dossier screens/ ."""

    ##bdd = sqlite3.connect("fichiers.sqlite") # ouverture de la base
    ##bdd.row_factory = sqlite3.Row # accès aux colonnes par leur nom, pas par leur index

    ##c = bdd.cursor() # obtention d'un curseur

    ##if list_vids:
        ##for each_video in list_vids:
            ##c.execute("SELECT path, thumb FROM videos WHERE id = ?", (each_video,))
            ##data = c.fetchone()

            ##thumb_path = data["thumb"]
            ##mosaic_path = thumb_path.replace("_thumb.png", "_mosaic.png")

            ###On génère la miniature et la mosaïque
            ##logger.info("Régénération des images pour {0}".format(data['path']))
            ##screen.thumb(data['path'], md4Function(data['path']))
            ##screen.caps(data['path'], md4Function(data['path']))
    ##else:
        
        ###On vide le dossier des screenshots
        ##logger.info("Effacement du dossier des screens")
        ##os.chdir('./screens')
        ##for picture in os.listdir('.'):
            ##os.remove(os.path.abspath(picture))
        ##os.chdir(os.path.dirname(sys.argv[0]))

        ##c.execute("SELECT path FROM videos")

        ##logger.info("Régénération de toutes les images")

        ##for ligne_bdd in c.fetchall():
            ###On génère la miniature et la mosaïque
            ##screen.thumb(ligne_bdd['path'], md4Function(ligne_bdd['path']))
            ##screen.caps(ligne_bdd['path'], md4Function(ligne_bdd['path']))

        ##logger.info("Régénération terminée")

    ##c.close()
    ##bdd.close()


#def generatePictures(id_video=None):

    #"""Fct qui génére les images d'une liste de vids passée en paramètre,
    ##ou de tte la bdd si rien n'est passé en paramètre, mais uniquement
    ##si une image n'existe pas déjà."""

    ##bdd = sqlite3.connect("fichiers.sqlite") # ouverture de la base
    ##bdd.row_factory = sqlite3.Row # accès aux colonnes par leur nom, pas par leur index

    ##c = bdd.cursor() # obtention d'un curseur

    ##if id_video:
        ##c.execute("SELECT thumb, path FROM videos WHERE id = ?", (id_video,))
    ##else:
        ##c.execute("SELECT thumb, path FROM videos")

    ##for ligne_bdd in c.fetchall():

        ###On génère la miniature et la mosaïque
        ##if not os.path.exists(ligne_bdd['thumb']):
            ##screen.thumb(ligne_bdd['path'])
            ##print("Génération thumb pour {0}".format(ligne_bdd['path']))
        ##else:
            ##print('Thumb ok pour: ' + ligne_bdd['path'])

        ##if not os.path.exists(ligne_bdd['thumb'].replace("_thumb.png", "_mosaic.png")):
            ##screen.caps(ligne_bdd['path'])
            ##print("Génération mosaïque pour {0}".format(ligne_bdd['path']))
        ##else:
            ##print('Mosaïque ok pour: ' + ligne_bdd['path'])

    ##c.close()
    ##bdd.close()


#def vote(identifiant, logger):

    #"""Fonction pour ajouter un like à un fichier"""

    ##bdd = sqlite3.connect("fichiers.sqlite") # ouverture de la base
    ##bdd.row_factory = sqlite3.Row # accès aux colonnes par leur nom, pas par leur index

    ##c = bdd.cursor() # obtention d'un curseur

    ##c.execute("UPDATE videos SET vote = IFNULL(vote, 0) + 1 WHERE id= ?", (identifiant,))

    ##bdd.commit()

    ##c.close()
    ##bdd.close()


#def addTag(list_vids, list_tags, logger):

    #"""Ajoute tous les tags de list_tags à chaque vid de list_vids. Pour
    ##cela crée un tag dans la table tags, puis établit une relation entre
    ##l'id de la vidéo et l'id du tag créé. Inscrit la correspondance dans
    ##la table videos_tags."""

    ##bdd = sqlite3.connect("fichiers.sqlite") # ouverture de la base
    ##bdd.row_factory = sqlite3.Row # accès aux colonnes par leur nom, pas par leur index

    ##c = bdd.cursor() # obtention d'un curseur

    ###On ajoute le tag transmis à la table tags s'il n'existe pas déjà
    ##for each_tag in list_tags:
        ##c.execute("SELECT * FROM tags WHERE name= ? ", (each_tag,))
        ###On teste si le tag n'est pas un espace en trop
        ###(la chaîne du tag serait donc vide)
        ##if c.fetchone() is None and each_tag:
            ##c.execute("INSERT INTO tags (name) VALUES (?) ", (each_tag,))

    ##for each_video in list_vids:
        ##for each_tag in list_tags:
            ###On récupère l'id du tag pour s'en servir après
            ###On teste si le tag n'est pas un espace en trop
            ###(la chaîne du tag serait donc vide)
            ##if each_tag:
                ##c.execute("SELECT id FROM tags WHERE name= ?", (each_tag,))
                ##id_tag_recupere = c.fetchone()["id"]
            ##else:
                ###Si le tag est vide, on arrête les traitements
                ##continue

            ###On vérifie que le tag à stocker n'est pas déjà associé à la vidéo 
            ##c.execute("SELECT * FROM videos_tags WHERE id_video = ? AND id_tag = ?", (each_video, id_tag_recupere))
            ##if c.fetchone() is None and each_tag:
                ##logger.info("Ajout du tag {0} à la vidéo {1}".format(each_tag, each_video))
                ##c.execute("INSERT INTO videos_tags (id_video, id_tag) VALUES (?, ?)", (each_video, id_tag_recupere))
            ##else:
                ##logger.info("la vidéo {0} a déjà le tag {1}".format(each_video, each_tag))

    ##bdd.commit()
    ##c.close()
    ##bdd.close()


#def addActor(list_vids, name_actor, logger):

    #"""Fct pour ajouter un acteur en bdd. Un seul acteur à la fois."""

    ##bdd = sqlite3.connect("fichiers.sqlite") # ouverture de la base
    ##bdd.row_factory = sqlite3.Row # accès aux colonnes par leur nom, pas par leur index

    ##c = bdd.cursor() # obtention d'un curseur

    ###On vérifie que l'acteur n'est pas déjà en bdd
    ##c.execute("SELECT * FROM actors WHERE name_simple = ? ", (simpleChar(name_actor),))
    ##if c.fetchone() is None:
        ##name_actor = [ each_word.capitalize() for each_word in name_actor.split(" ") ]
        ##name_actor = " ".join(name_actor)
        ##c.execute("INSERT INTO actors (name, name_simple) VALUES (?, ?) ", (name_actor, simpleChar(name_actor)))

    ##bdd.commit()

    ###À chaque vid s'électionnée, on ajoute l'acteur
    ##for each_video in list_vids:
        ###On récupère l'id de l'acteur pour s'en servir après
        ##c.execute("SELECT id, name FROM actors WHERE name_simple= ?", (simpleChar(name_actor),))
        ##data = c.fetchone()
        ##id_actor = data["id"]

        ###On vérifie que l'acteur à stocker n'est pas déjà associé à la vidéo 
        ##c.execute("SELECT * FROM videos_actors WHERE id_video = ? AND id_actor = ?", (each_video, id_actor))
        ##if c.fetchone() is None:
            ##logger.info("{0} associé à la vidéo {1}".format(data["name"], each_video))
            ##c.execute("INSERT INTO videos_actors (id_video, id_actor) VALUES (?, ?)", (each_video, id_actor))
        ##else:
            ##print("Cette vidéo est déjà associée à cet acteur")

    ##bdd.commit()
    ##c.close()
    ##bdd.close()


#def removeTag(id_video, nom_tag, logger):

    #"""Fonction pour enlever un tag à une vidéo donnée.
    ##Si ce tag n'a plus de vidéo associée, on le supprime de 
    ##la bdd"""

    ##bdd = sqlite3.connect("fichiers.sqlite") # ouverture de la base
    ##bdd.row_factory = sqlite3.Row # accès aux colonnes par leur nom, pas par leur index

    ##c = bdd.cursor() # obtention d'un curseur

    ##c.execute("DELETE FROM videos_tags \
                ##WHERE videos_tags.id_tag IN \
                ##(SELECT id FROM tags WHERE tags.name = ?) \
                ##AND videos_tags.id_video = ?", (nom_tag, id_video))

    ###On récupère l'id du tag supprimé
    ##c.execute("SELECT id FROM tags WHERE name = ?", (nom_tag,))
    ##id_del = c.fetchone()[0]

    ##c.execute("SELECT id_video FROM videos_tags WHERE id_tag = ?", (id_del,))

    ###Si aucune vidéo n'est encore associée au tag, on supprime le tag de la bdd
    ##try:
        ##response = c.fetchone()[0]
        ##logger.info("Tag {0} enlevé de la vidéo {1}".format(nom_tag, id_video))
    ##except TypeError:
        ##c.execute("DELETE FROM tags WHERE id = ?", (id_del,))
        ##logger.info("Tag {0} supprimé de la vidéo {1} et de la bdd".format(nom_tag, id_video))

    ##bdd.commit()
    
    ##c.close()
    ##bdd.close()


#def removeActor(id_video, actor, logger):

    #"""Fonction pour enlever un acteur à une vidéo donnée"""

    ##bdd = sqlite3.connect("fichiers.sqlite") # ouverture de la base
    ##bdd.row_factory = sqlite3.Row # accès aux colonnes par leur nom, pas par leur index

    ##c = bdd.cursor() # obtention d'un curseur

    ###On désassocie l'acteur de la vid spécifiée
    ##c.execute("DELETE FROM videos_actors \
                ##WHERE videos_actors.id_actor IN \
                ##(SELECT id FROM actors WHERE actors.name = ?) \
                ##AND videos_actors.id_video = ?", (actor, id_video))

    ###On récupère l'id de l'acteur supprimé ds la table des acteurs
    ##c.execute("SELECT id FROM actors WHERE name = ?", (actor,))
    ##id_del = c.fetchone()[0]

    ###On regarde ds videos_actors si l'acteur est encore associé à une vid
    ##c.execute("SELECT id_video FROM videos_actors WHERE id_actor = ?", (id_del,))

    ###Si aucune vidéo n'est encore associée à l'acteur,
    ###on supprime l'acteur de la bdd
    ##try:
        ##response = c.fetchone()[0]
        ##logger.info("Acteur {0} enlevé de la vidéo {1}".format(actor, id_video))
    ##except TypeError:
        ##c.execute("DELETE FROM actors WHERE id = ?", (id_del,))
        ##logger.info("Acteur {0} supprimé de la vidéo {1} et de la bdd".format(actor, id_video))

    ##bdd.commit()
    
    ##c.close()
    ##bdd.close()


#def bigRemoveTag(nom_tag, logger):

    #"""Fonction qui supprime complètement un tag
    ##à partir de son nom. Supprime aussi les entrées 
    ##des vidéos associées à ce tag"""

    ##bdd = sqlite3.connect("fichiers.sqlite") # ouverture de la base
    ##bdd.row_factory = sqlite3.Row # accès aux colonnes par leur nom, pas par leur index

    ##c = bdd.cursor() # obtention d'un curseur

    ###On récupère l'id tu tag grâce à son nom
    ##c.execute("SELECT id FROM tags WHERE name = ?", (nom_tag,))
    ##id_tag = c.fetchone()["id"]

    ###On delete les entrées dans les tables 'tags' et 'videos_tags'
    ##c.execute("DELETE FROM tags WHERE id = ?", (id_tag,))
    ##c.execute("DELETE FROM videos_tags WHERE id_tag = ?", (id_tag,))

    ##bdd.commit()

    ##logger.info("Tag {0} supprimé définitivement de la bdd".format(nom_tag))

    ##c.close()
    ##bdd.close()


#def bigRemoveActor(actor, logger):

    #"""Fonction qui supprime complètement un tag
    ##à partir de son nom. Supprime aussi les entrées 
    ##des vidéos associées à ce tag"""

    ##bdd = sqlite3.connect("fichiers.sqlite") # ouverture de la base
    ##bdd.row_factory = sqlite3.Row # accès aux colonnes par leur nom, pas par leur index

    ##c = bdd.cursor() # obtention d'un curseur

    ###On récupère l'id tu tag grâce à son nom
    ##c.execute("SELECT id FROM actors WHERE name = ?", (actor,))
    ##id_actor = c.fetchone()["id"]

    ###On delete les entrées dans les tables 'actors' et 'videos_actors'
    ##c.execute("DELETE FROM actors WHERE id = ?", (id_actor,))
    ##c.execute("DELETE FROM videos_actors WHERE id_actor = ?", (id_actor,))

    ##bdd.commit()

    ##logger.info("Acteur {0} définitivement supprimé de la bdd".format(actor))

    ##c.close()
    ##bdd.close()


#def obtainTag(id_video):

    #"""Obtient les tags d'une vidéo passée en paramètre"""

    ##bdd = sqlite3.connect("fichiers.sqlite") # ouverture de la base
    ##bdd.row_factory = sqlite3.Row # accès aux colonnes par leur nom, pas par leur index

    ##c = bdd.cursor() # obtention d'un curseur

    ### On récupère tous les tags associés à une vidéo
    ##c.execute("SELECT tags.name FROM tags \
            ##INNER JOIN videos_tags ON videos_tags.id_tag = tags.id \
            ##WHERE videos_tags.id_video = ?", (id_video,))

    ##data = c.fetchall()

    ##liste_tags = list()

    ##for ligne_bdd in data:
        ##liste_tags.append(ligne_bdd["name"])

    ##c.close()
    ##bdd.close()

    ##return sorted(liste_tags)


#def obtainActors(id_video):

    #"""Obtient les acteurs d'une vid passée en paramètre"""

    ##bdd = sqlite3.connect("fichiers.sqlite") # ouverture de la base
    ##bdd.row_factory = sqlite3.Row # accès aux colonnes par leur nom, pas par leur index

    ##c = bdd.cursor() # obtention d'un curseur

    ### On récupère tous les acteurs associés à une vidéo
    ##c.execute("SELECT actors.name FROM actors \
            ##INNER JOIN videos_actors ON videos_actors.id_actor = actors.id \
            ##WHERE videos_actors.id_video = ?", (id_video,))

    ##data = c.fetchall()

    ##liste_actors = list()

    ##for ligne_bdd in data:
        ##liste_actors.append(ligne_bdd["name"])

    ##c.close()
    ##bdd.close()

    ##return sorted(liste_actors)


#def listeTags():

    #"""Fonction qui retourne la liste des tags déjà utilisés
    ##dans la bdd, tous les tags en somme."""

    ##bdd = sqlite3.connect("fichiers.sqlite") # ouverture de la base
    ##bdd.row_factory = sqlite3.Row # accès aux colonnes par leur nom, pas par leur index

    ##c = bdd.cursor() # obtention d'un curseur

    ##c.execute("SELECT * FROM tags")

    ##data = c.fetchall()

    ##liste_tags = list()

    ##for ligne_bdd in data:
        ##liste_tags.append(str(ligne_bdd["name"]))

    ##c.close()
    ##bdd.close()

    ##return sorted(liste_tags)


#def listeActors():

    #"""Fonction qui retourne la liste des acteurs déjà utilisés
    ##dans la bdd, tous les acteurs en somme."""

    ##bdd = sqlite3.connect("fichiers.sqlite") # ouverture de la base
    ##bdd.row_factory = sqlite3.Row # accès aux colonnes par leur nom, pas par leur index

    ##c = bdd.cursor() # obtention d'un curseur

    ##c.execute("SELECT * FROM actors")

    ##data = c.fetchall()

    ##liste_actors = list()

    ##for ligne_bdd in data:
        ##liste_actors.append(ligne_bdd["name"])

    ##c.close()
    ##bdd.close()

    ##return sorted(liste_actors)


#def searchByTag(liste_tags, AND):

    #"""Fct qui retourne une liste d'id de vids, où chaque vid a ts
    ##les tags de la liste passée en paramètre"""

    ##if not liste_tags:
        ##return

    ##bdd = sqlite3.connect("fichiers.sqlite") # ouverture de la base
    
    ##bdd.row_factory = sqlite3.Row # accès aux colonnes par leur nom, pas par leur index

    ##c = bdd.cursor() # obtention d'un curseur

    ##requete = "SELECT videos.id, videos.name, videos.name_simple, videos.vote, videos.path, videos.thumb, videos.date \
            ##FROM videos INNER JOIN videos_tags ON videos_tags.id_video = videos.id INNER JOIN tags \
            ##ON videos_tags.id_tag = tags.id WHERE"

    ###On ajoute chaque tag de la liste à la requête
    ##for each_tag in liste_tags:
        ##if liste_tags.index(each_tag) == 0:
            ##requete = requete + " tags.name = '" + each_tag + "'"
        ##else:
            ##requete = requete + " OR tags.name = '" + each_tag + "'"

    ##c.execute(requete)

    ##data = c.fetchall()

    ###On compte le nbr d'occurences de chaque id ds la liste.
    ###Si le nbr d'occurences = le nbr de tags total, alors la vid
    ###a ts les tags et on retourne son id
    ##occurences = list()
    ##[ occurences.append(each_line['id']) for each_line in data ]

    ###Si la recherche AND est activée
    ##if AND:
        ##occurences = [ each_id for each_id in occurences if occurences.count(each_id) == len(liste_tags) ] 

    ##occurences = list(set(occurences))

    ##c.close()
    ##bdd.close()

    ##return occurences


#def searchByActor(liste_actors, AND):

    #"""Fct qui retourne une liste d'id de vids, où chaque vid a ts
    ##les acteurs de la liste passée en paramètre"""

    ##if not liste_actors:
        ##return

    ##bdd = sqlite3.connect("fichiers.sqlite") # ouverture de la base
    
    ##bdd.row_factory = sqlite3.Row # accès aux colonnes par leur nom, pas par leur index

    ##c = bdd.cursor() # obtention d'un curseur

    ##requete = "SELECT videos.id, videos.name, videos.name_simple, videos.vote, videos.path, videos.thumb, videos.date \
            ##FROM videos INNER JOIN videos_actors ON videos_actors.id_video = videos.id INNER JOIN actors \
            ##ON videos_actors.id_actor = actors.id WHERE"

    ###On ajoute chaque tag de la liste à la requête
    ##for each_actor in liste_actors:
        ##if liste_actors.index(each_actor) == 0:
            ##requete = requete + " actors.name = \"" + each_actor + "\""
        ##else:
            ##requete = requete + " OR actors.name = \"" + each_actor + "\""

    ##c.execute(requete)

    ##data = c.fetchall()

    ###On compte le nbr d'occurences de chaque id ds la liste.
    ###Si le nbr d'occurences = le nbr de tags total, alors la vid
    ###a ts les tags et on retourne son id
    ##occurences = list()
    ##[ occurences.append(each_line['id']) for each_line in data ]

    ###Si la recherche AND est activée
    ##if AND:
        ##occurences = [ each_id for each_id in occurences if occurences.count(each_id) == len(liste_actors) ] 

    ##occurences = list(set(occurences))

    ##c.close()
    ##bdd.close()

    ##return occurences


#def randomVid(nbr_random=1, weight=False, waiting_list=None, force=10):

    #"""Choisit nbr_random vids au hasard, en pondérant optionellement
    ##les vids avec le nbr de votes * la force. Ne shuffle que les vids
    ##accessibles"""

    ###Liste vid pr les id des vids
    ##liste_id = list()
    ###Liste à retourner
    ##result = list()

    ##bdd = sqlite3.connect("fichiers.sqlite") # ouverture de la base
    ##bdd.row_factory = sqlite3.Row # accès aux colonnes par leur nom, pas par leur index
    ##c = bdd.cursor() # obtention d'un curseur

    ###On sélectionne le couple id/vote
    ##requete = "SELECT id, path, vote, waited FROM videos"

    ##c.execute(requete)

    ##for ligne_bdd in c.fetchall():

        ###Si le fichier est accessible, on peut l'ajouter
        ###à la liste
        ##if verifAccess(ligne_bdd['path']):
            ###Si une vid a un nbr de vote, et si on
            ###doit pondérer

            ##if waiting_list is None or ligne_bdd['id'] not in waiting_list:
                ##if weight and ligne_bdd['vote']:

                    ###On ajoute force fois la vid qu'il y a de votes.
                    ###ex: la vid a 3 votes, force=2, on la met 6 fois dans la liste
                    ##for vid in range(ligne_bdd['vote'] * force):
                        ##liste_id.append(ligne_bdd['id'])

                ##if weight and ligne_bdd['waited']:
                    ##for vid in range(int(ligne_bdd['waited'] * force / 2)):
                        ##liste_id.append(ligne_bdd['id'])

                ##if ligne_bdd['id'] not in liste_id:
                    ##liste_id.append(ligne_bdd['id'])

    ###On crée une variable pr contenir l'id le plus grand
    ##requete = "SELECT MAX(id) FROM videos"
    ##c.execute(requete)
    ##id_max = c.fetchone()[0]

    ###Si le nbr de vid à tirer est plus grand que le nbr
    ###de vids total, on fixe le nbr à tirer au nbr de vids
    ###total, pr éviter une exception
    ##if nbr_random > id_max:
        ##nbr_random = id_max

    ##while len(result) < nbr_random:
        ##index = random.randint(0, len(liste_id) - 1)
        ##result.append(liste_id[index])
        ##liste_id = [value for value in liste_id if value != liste_id[index]]

    ##return result


#if __name__ == "__main__":
    #getData()
    ##pass

