import sqlite3, csv, os, datetime, time, logging
from EnefpConstants import *

class DBTools:

    # Constructeur
    def __init__(self, db_file):
        self.connected = False
        self.log = logging.getLogger()
        #self.log.error(f"{self.getDate()} => Instance DBTools créé")
        self.db = db_file
        self.connect()

    # Connexion
    def connect(self):
        self.cnx = sqlite3.connect(self.db)
        self.cur = self.cnx.cursor()
        self.connected = True
        self.isConnected()
        return True

    # Déconnexion
    def disconnect(self):
        if self.isConnected():
            self.cnx.close()
            self.connected = False
            self.isConnected()
        return True

    # Est connecté à la base de données
    def isConnected(self):
        if self.connected:
            ##self.log.error(f"{self.getDate()} => Connecté à {self.db}")
            return True
        else:
            #self.log.error(f"{self.getDate()} => Base non connectée")
            pass
        return False

    # Récupération date et heure
    def getDate(self):
        return datetime.datetime.today().strftime('%d/%m/%Y %H:%M:%S')


    # Exécution requête sql
    def execute_req(self, req):
        if self.isConnected():
            ##self.log.error(f"{self.getDate()} => Exécution requête : {req}")
            try:
                self.cur.execute(req)
                self.cnx.commit()
            except sqlite3.Error as error:
                print(error)
        return True

    # Exécution plusieurs requêtes sql
    def executemany_req(self, req, reader):
        if self.isConnected():
            ##self.log.error(f"{self.getDate()} => Exécution requête : {req}")
            self.cur.executemany(req, reader)
            self.cnx.commit()
        return True

    # Construction requête sql (create, delete, insert)
    def make_req(self, type, table):

        if type == "CREATE":
            req = "CREATE TABLE IF NOT EXISTS " + table["TABLE"] + "("
            for key in table.keys():
                if(key != "TABLE"):
                    req += key + " TEXT,"
            req = req[0:len(req)-1] + ")"

        elif type == "DELETE":
            req = "DELETE FROM " + table["TABLE"]

        elif type == "INSERT":
            req = "INSERT INTO " + table["TABLE"] + "("
            for key in table.keys():
                if(key != "TABLE"):
                    req += key + ","
            req = req[0:len(req)-1] + ") VALUES ("
            for key in table.keys():
                if(key != "TABLE"):
                    req += "?,"
            req = req[0:len(req)-1] + ")"

            ##print(req)

        return req


    #-----------------------------------

    # IMPORT DES DONNEES DANS LA BASE => AJOUTER OPTION TRIM
    def import_data(self, table, path, eraseTableData):

        if self.isConnected():

            # Création table
            self.execute_req(self.make_req("CREATE", table))

            # Effacement table
            if eraseTableData:
                self.execute_req(self.make_req("DELETE", table))

            # Insertion données à partir d'un fichier
            try:
                if os.path.isfile(path):
                    with open(path, newline='', encoding="ANSI") as f:
                        #self.log.error(f"{self.getDate()} => Import données depuis {path}")
                        reader = csv.reader(f, delimiter=';')
                        # TODO => ajouter trim
                        self.executemany_req(self.make_req("INSERT", table), reader)
            except OSError:
                #self.log.error(f"{self.getDate()} => Fichier inexistant [{path}]")
                pass

            # Insertion données à partir d'un dossier
            try:
                if os.path.isdir(path):
                    for r, d, f in os.walk(path):
                        for file in f:
                            if ".csv" in file:
                                with open(os.path.join(r, file), newline='', encoding="ANSI") as f:
                                    #self.log.error(f"{self.getDate()} => Import données depuis {os.path.join(r, file)}")
                                    reader = csv.reader(f, delimiter=';')
                                    # TODO => ajouter trim
                                    self.executemany_req(self.make_req("INSERT", table), reader)
            except OSError:
                #self.log.error(f"{self.getDate()} => Dossier inexistant [{path}]")
                pass


    # EXPORT DES DONNEES DEPUIS LA BASE
    def export_data(self, req, header="", file_out=""):

        if self.isConnected():

            if header != "":
                head = header
            else:
                head = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

            #self.log.error(f"{self.getDate()} => Export données : {req}")
            self.cur.execute(req)
            rows = self.cur.fetchall()
            nbRows = len(rows)

            # Si enregistrements trouvés
            if nbRows > 0:
                #self.log.error(f"{self.getDate()} => Enregistrements trouvés [{nbRows}]")

                # Si fichier sortie renseigné, on écrit le résulat dedans
                if file_out != "":
                    #self.log.error(f"{self.getDate()} => Fichier sortie renseigné")
                    try:
                        with open(file_out, "w", newline = '', encoding="ANSI") as f:
                            #self.log.error(f"{self.getDate()} => Enregistrement fichier résultat")

                            writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_NONE, escapechar='|', quotechar='"')

                            writer.writerow(head)
                            writer.writerows(rows)
                            self.disconnect()
                            return True
                    except OSError:
                        #self.log.error(f"{self.getDate()} => Ecriture résultat impossible [{file_out}]")
                        pass

                # Si fichier sortie non renseigné, on renvoi les rows
                #self.log.error(f"{self.getDate()} => Renvoi rows")
                return rows

            # Si enregistrements non trouvés
            #self.log.error(f"{self.getDate()} => Pas d'enregistrements trouvés [{nbRows}]")
            return False
        return False

###--------------------------------------------------------------------------###
###--------------------------------------------------------------------------###
###--------------------------------------------------------------------------###

# TEST DE LA CLASSE
if(__name__ == "__main__"):
    pass

##    # Connexion à la base (ou création si inexistant)
##    DB_FILE = r"C:\DATA\_in_\_db_\DB_TEST.db"
##    db = DBTools(DB_FILE)
##
##    # Import d'un fichier
##    FILE_BR001_INDIV = r"C:\DATA\_in_\_extractions_\2022-10-17\BR001_INDIV.csv"
##    db.import_data(DICT_BR001_INDIV, FILE_BR001_INDIV, True)
##
##    # Import d'un dossier
##    FOLDER_BF002_CONTRATS   = r"C:\DATA\_in_\_extractions_\BF002\2022-10-18\contrat"
##    db.import_data(DICT_BF002_CONTRATS, FOLDER_BF002_CONTRATS, True)
##
##    # Création d'une requête en passant un dictionnaire
##    dict1 = {"TABLE": "TEST", "cc": "CONTRAT", "ga": "GROUPE_ASSURES"}
##    db.execute_req(db.make_req("CREATE", dict1))
##
##    # Export des données dans fichier
##    req = "SELECT * FROM BR001_INDIV"
##    header = ['OFFRE','PRODUIT','TYPEGT','GARANTIE']
##    file_out = r"C:\DATA\_out_\python\TEST_EXPORT.csv"
##    rows = db.export_data(req, header, file_out)
##
##    # Export des données dans rows
##    # TODO : création requête + passer DICT en paramètre plutôt que Header ?
##    req = "SELECT * FROM BR001_INDIV"
##    header = ['OFFRE','PRODUIT','TYPEGT','GARANTIE']
##    file_out = ""
##    rows = db.export_data(req, header, file_out)
####    for row in rows:
####        print(row)
##
##    # Deconnexion
##    db.disconnect()











