#------------------------------------------------------------------------------#
#                               MODIFICATIONS ENEFP                            #
#                                                                              #
#------------------------------------------------------------------------------#

import sqlite3, csv, os, datetime, time, logging, unicodedata, string
from DBTools import DBTools
from EnefpConstants import *


class EnefpModifier:

    ##DB_FILE = os.path.join(os.getcwd(), "data", "DB_ENEFP.db")
    DB_FILE = r"C:\DATA\_in_\_db_\DB_ENEFP2.db"
    ##DB_FILE = ":memory:"
    FILE_REGLES_CUMUL_ASSIST_PREMIUM  = os.path.join(os.getcwd(), "ENEFP_REGLES_CUMUL_ASSIST_PREMIUM.csv")
    FILE_EXCLUSION_GARANTIES_OPTIONS_PREMIUM  = os.path.join(os.getcwd(), "ENEFP_EXCLUSION_GARANTIES_OPTIONS_PREMIUM.csv")

    TAUX_PMSS = 3666

    ##LOG_NAME = os.path.join(os.getcwd(), "logs", "LOGS_" + datetime.datetime.today().strftime('%Y%m%d_%H%M%S') + ".csv")
    LOG_NAME = r"C:\DATA\_out_\python\LOGS\LOGS_" + datetime.datetime.today().strftime('%Y%m%d_%H%M%S') + ".csv"


    # Constructeur
    def __init__(self, enefp_in, enefp_out, params, verbose):

        self.logger = self.get_logger()
        self.is_load_enefp_file = False
        self.is_load_data = False
        self.verbose = verbose

        self.log("DEBUT")

        try:
            self.db = DBTools(EnefpModifier.DB_FILE)
            self.is_load_enefp_file = self.load_enefp_file(enefp_in)
            self.is_load_data = self.load_data()
        except OSError as err:
            self.log(err)

        # Suppression lignes PMSS PASS
        if params[0]:
            if self.is_load_enefp_file:
                self.del_pxss()

        # Cumul assistance
        if params[1]:
            if self.is_load_enefp_file and self.is_load_data:
                self.cumul_assistance()

        # Export de l'enefp modifié
        self.export_enefp(enefp_out)

        # Actions à faire après tous les traitements
        self.log("FIN")
        self.del_logger() ## Fermeture logger
        self.db.disconnect() ## Fermeture db


    # Récupération logger
    def get_logger(self):
        logging.basicConfig(filename=EnefpModifier.LOG_NAME, encoding='utf-8', level=logging.DEBUG, format='%(asctime)s;%(message)s', datefmt='%d/%m/%Y;%H:%M:%S')
        return logging.getLogger()


    # Suppression logger
    def del_logger(self):
        handlers = self.logger.handlers[:]
        for handler in handlers:
            self.logger.removeHandler(handler)
            handler.close()


    # Affichage log si mode verbeux
    def log(self, log_msg):
        if self.verbose:
            self.logger.error(log_msg)


    # Chargement fichier ENEFP et création base de données
    def load_enefp_file(self, enefp_file):
        try:
            self.db.import_data(DICT_ENEFP, enefp_file, True)
            self.is_load_enefp_file = True
            self.log("ENEFP CHARGE;" + enefp_file)
            return True
        except OSError as err:
            self.log(err)
            self.is_load_enefp_file = False
            return False

    # Si enefp chargé
    def is_load_enefp_file(self):
        return self.is_load_enefp_file

    # Chargement données nécessaires au programme
    def load_data(self):
        try:
            self.db.import_data(DICT_ENEFP_REGLES_CUMUL_ASSIST_PREMIUM, EnefpModifier.FILE_REGLES_CUMUL_ASSIST_PREMIUM, True)
            self.db.import_data(DICT_ENEFP_EXCLUSION_GARANTIES_OPTIONS_PREMIUM, EnefpModifier.FILE_EXCLUSION_GARANTIES_OPTIONS_PREMIUM, True)
            self.is_load_data = True
            self.log("DONNEES NECESSAIRES CHARGEES;" + EnefpModifier.FILE_REGLES_CUMUL_ASSIST_PREMIUM + ";" + EnefpModifier.FILE_EXCLUSION_GARANTIES_OPTIONS_PREMIUM)
            return True
        except OSError as err:
            self.log(err)
            self.is_load_data = False
            return False

    # Si données nécessaires chargées
    def is_load_data(self):
        return self.is_load_data


    # Export de l'ENEFP modifié
    def export_enefp(self, enefp_out):

        self.log("EXPORT ENEFP MODIFIE")

        ##req = "SELECT * FROM ENEFP WHERE ETAT NOT LIKE 'E%' AND ETAT NOT LIKE 'DEL%'"
        req = "SELECT * FROM ENEFP WHERE ETAT NOT LIKE 'E%';"

        # Constitution Header
        header = []
        for val in DICT_ENEFP.values():
            if val != "ENEFP":
                header.append(val)

        rows = self.db.export_data(req, header, enefp_out)


    # Suppression des lignes PxSS
    def del_pxss(self):
        try:
            req = """
                    UPDATE ENEFP SET ETAT = "DEL__PMSS_PASS"
                    WHERE LibelleCodeNature LIKE 'EMP,PMSS%' OR LibelleCodeNature LIKE 'EMP,PASS%';"""
            self.db.execute_req(req)

        except sqlite3.Error as error:
            self.log("ERREUR_FONCTION;del_pxss")


    # Cumul des lignes assistance
    def cumul_assistance(self):

        rows_assist_update = []
        rows_sante_update = []

        regles_cumul = self.get_regles_cumul_assistance_premium()
        exclusion_gt = self.get_exclusion_garanties_options_premium()
        rows_assist = self.get_rows_assist()

        self.log("TRAITEMENT CUMUL ASSISTANCE")
        for row_assist in rows_assist:

            contrat_assist     = row_assist[0]
            option_assist      = row_assist[1]
            population_assist  = row_assist[2]
            elements_assist    = row_assist[3]
            libelle_assist     = row_assist[4]
            montant_assist     = row_assist[5]

            rows_sante = self.get_rows_sante(contrat_assist, option_assist, population_assist)

            is_row_sante_update = False

            for row_sante in rows_sante:

                contrat_sante     = row_sante[0]
                option_sante      = row_sante[1]
                population_sante  = row_sante[2]
                elements_sante    = row_sante[3]
                code_nature_sante = row_sante[4]
                libelle_sante     = row_sante[5]
                taux_sante        = row_sante[6]
                montant_sante     = row_sante[7]

                tab_elems = elements_sante.split("/")

                produit_sante   = tab_elems[0]
                garantie_sante  = tab_elems[1]
                cv_sante        = tab_elems[2]
                formule_sante   = tab_elems[3]

                if garantie_sante[:3] != "PDC" and garantie_sante[:4] != "PPCK" and garantie_sante[:3] != "HDS":

                    if self.test_exclusion_garanties_options_premium(exclusion_gt, garantie_sante) == False:

                        libelle_trans = self.transformation_libelle(libelle_sante)

                        if self.test_cumul_assist(regles_cumul, libelle_trans):

                            tarif_assist_mnt = round(float(montant_assist.replace(",", ".")), 2)
                            tarif_assist_taux = round(tarif_assist_mnt * 100 / EnefpModifier.TAUX_PMSS, 4)
                            debug = ""

                            # Détermintation tarif santé en fonction valeur code nature
                            if code_nature_sante == "18": ## Taux

                                tarif_sante_taux = round(float(taux_sante.replace(",", ".")), 4)
                                tarif = round(tarif_sante_taux + tarif_assist_taux, 4)
                                tarif = self.format_tarif(str(tarif).replace(".", ","), "TAUX")
                                debug = "CUMUL " + str(tarif_sante_taux) + " + " + str(tarif_assist_taux)

                            elif code_nature_sante == "20": ## Montant

                                tarif_sante_mnt = round(float(montant_sante.replace(",", ".")), 2)
                                tarif = round(tarif_sante_mnt + tarif_assist_mnt, 2)
                                tarif = self.format_tarif(str(tarif).replace(".", ","), "MNT")
                                debug = "CUMUL " + str(tarif_sante_mnt) + " + " + str(tarif_assist_mnt)

                            row_sante_update = [tarif, contrat_sante, option_sante, population_sante, elements_sante, code_nature_sante, libelle_sante, debug]
                            rows_sante_update.append(row_sante_update)

                            is_row_sante_update = True

            # Si au moins une ligne santé a été mise à jour
            if is_row_sante_update:
                row_assist_update = [contrat_assist, option_assist, population_assist, elements_assist, libelle_assist]
                rows_assist_update.append(row_assist_update)


        # Mise à jour tarif santé dans base de données
        print("UPDATE TARIF SANTE => " + str(len(rows_sante_update)))
        self.update_tarif_sante(rows_sante_update)

        # Suppression ligne assistance dans base de données
        print("SUPPRESSION LIGNES ASSISTANCE => " + str(len(rows_assist_update)))
        self.update_del_assist(rows_assist_update)


    # Récupération des lignes distinctes contenant une assistance
    def get_rows_assist(self):

        try:
            req = """SELECT DISTINCT
                            Contrat_ReferenceContrat,
                            Option_CodeOption,
                            Population_CodePopulation,
                            MDG_JustificatifElementsCotisation,
                            LibelleCodeNature,
                            BaseMontantSpecifiqueMontant
                         FROM
                            ENEFP
                         WHERE
                            --LibelleCodeNature LIKE '%ASSISTANCE%'
                            LibelleCodeNature LIKE '%FAMILLE RG%' AND BaseMontantSpecifiqueMontant LIKE '%0,44%' -- A supprimer quand correction prod KSE OK
                         ;"""
            self.db.execute_req(req)
            rows = self.db.cur.fetchall()
            self.log("RECUPERATION LIGNES ASSISTANCE;" + str(len(rows)) + " lignes assistance trouvées")
            return rows

        except sqlite3.Error as error:
            self.log("ERREUR_FONCTION;get_rows_assist")


    # Récupération lignes santé selon contrat, option et population
    def get_rows_sante(self, contrat, option, population):

        try:
            req = """SELECT
                        Contrat_ReferenceContrat,
                        Option_CodeOption,
                        Population_CodePopulation,
                        MDG_JustificatifElementsCotisation,
                        ValeurCodeNature,
                        LibelleCodeNature,
                        BaseMontantSpecifiqueTaux,
                        BaseMontantSpecifiqueMontant
                     FROM
                        ENEFP
                     WHERE
                        Contrat_ReferenceContrat = \"""" + contrat + """\"
                        AND Option_CodeOption = \"""" + option + """\"
                        AND Population_CodePopulation = \"""" + population + """\"
                        AND LibelleCodeNature NOT LIKE '%ASSISTANCE%'
                        AND ETAT NOT LIKE 'DEL%'
                     ;"""
            self.db.execute_req(req)
            rows = self.db.cur.fetchall()
            return rows

        except sqlite3.Error as error:
            self.log("ERREUR_FONCTION;get_rows_sante;" + contrat + ";" + option + ";" + population)


    # Récupération règles cumul assistance Premium
    def get_regles_cumul_assistance_premium(self):

        try:
            req = """SELECT * FROM ENEFP_REGLES_CUMUL_ASSIST_PREMIUM;"""
            self.db.execute_req(req)
            rows = self.db.cur.fetchall()
            return rows

        except sqlite3.Error as error:
            self.log("ERREUR_FONCTION;get_regles_cumul_assistance_premium")


    # Récupération exclusion garanties options Premium
    def get_exclusion_garanties_options_premium(self):

        try:
            req = """SELECT * FROM ENEFP_EXCLUSION_GARANTIES_OPTIONS_PREMIUM;"""
            self.db.execute_req(req)
            rows = self.db.cur.fetchall()
            return rows

        except sqlite3.Error as error:
            self.log("ERREUR_FONCTION;get_exclusion_garanties_options_premium")


    # Transformation libellé
    def transformation_libelle(self, libelle):

        libelle_origine = libelle

        # Trim
        libelle = libelle.strip()

        # Passage en majuscule
        libelle = libelle.upper()

        # Suppression des accents
        libelle = self.remove_accents(libelle)

        # Remplacement des espaces par underscore
        libelle = libelle.replace(" ", "_")

        # Suppression de certaines chaînes de texte
        libelle = libelle.replace('EMP,', "")
        libelle = libelle.replace('MNT,', "")
        libelle = libelle.replace('TAUX,', "")
        libelle = libelle.replace('TXEC,', "")
        libelle = libelle.replace('PMSS,', "")
        libelle = libelle.replace('PASS,', "")
        libelle = libelle.replace('_EN_EUROS', "")
        libelle = libelle.replace('_EN_TAUX_DU_PMSS', "")
        libelle = libelle.replace('_RG', "")
        libelle = libelle.replace('_RL', "")
        libelle = libelle.replace('_MSA', "")
        libelle = libelle.replace('_PMSS', "")
        libelle = libelle.replace('FORMULE_SUR_MESURE_BASE_', "")
        libelle = libelle.replace('FORMULE_SUR_MESURE_BASE_2_', "")
        libelle = libelle.replace('FORMULE_SUR_MESURE_BASE_3_', "")
        libelle = libelle.replace('FORMULE_SUR_MESURE_OPTION_', "")
        libelle = libelle.replace('FORMULE_SM_', "")
        libelle = libelle.replace('FORMULE_SM_OPT1', "")
        libelle = libelle.replace('FORMULE_', "")
        libelle = libelle.replace('FOR_SUR_MESU_', "")
        libelle = libelle.replace('_SUR_MESURE_BASE', "")
        libelle = libelle.replace('SUR_MESURE_', "")
        libelle = libelle.replace('_BASE_MNT_', "")
        libelle = libelle.replace('_BASE_2_MNT_', "")
        libelle = libelle.replace('_BASE', "")
        libelle = libelle.replace('BASE_', "")
        libelle = libelle.replace('_BAS', "")
        libelle = libelle.replace('_MONTANT', "")
        libelle = libelle.replace('_MONTAN', "")
        libelle = libelle.replace('_MONTA', "")
        libelle = libelle.replace('_MONT', "")
        libelle = libelle.replace('_MNT_T', "")
        libelle = libelle.replace('_SANTE', "")
        libelle = libelle.replace('_O/O', "")
        libelle = libelle.replace('_EN_O/', "")
        libelle = libelle.replace('_EN_O', "")


        # Split et renvoi du dernier élément si plusieurs éléments
        tab_libelles = libelle.split(",")

        if len(tab_libelles) > 1:
            libelle =  tab_libelles[-1]

        # Gestion IBT001
        if libelle.isdigit():
            libelle = "AGE_PAR_AGE_0_100"

        return libelle


    # Suppression des accents
    def remove_accents(self, chaine):

        ##return ''.join(x for x in unicodedata.normalize('NFKD', chaine) if x in string.ascii_letters).lower()

        alpha_acc_maj   = u"AÀÀÂÂÄÄÅÅÆBCÇÇDEÉÉÈÈÊÊËËFGHIÎÎÏÏJKLMNOÔÔÖÖŒPQRSTUÙÙÛÛÜÜVWXYŸŸZ"
        alpha_maj       = u"AAAAAAAAAÆBCCCDEEEEEEEEEFGHIIIIIJKLMNOOOOOŒPQRSTUUUUUUUVWXYYYZ"
        ##alpha_acc_min   = u"aàÀâÂäÄåÅæbcçÇdeéÉèÈêÊëËfghiîÎïÏjklmnoôÔöÖœpqrstuùÙûÛüÜvwxyÿŸz"
        ##alpha_min       = u"aaaaaaaaaæbcccdeeeeeeeeefghiiiiijklmnoooooœpqrstuuuuuuuvwxyyyz"

        chaine_result = ""

        for car in chaine:
            pos_accent = alpha_acc_maj.find(car)
            if pos_accent >= 0:
                chaine_result += alpha_maj[pos_accent]
            else:
                chaine_result += car

        return chaine_result


    # Test si cumul assistance
    def test_cumul_assist(self, regles_cumul, libelle):

        for row in regles_cumul:
            if row[0] == libelle:
                if row[1] != "":
                    return True
                else:
                    return False
        self.log("LIBELLE NON TROUVE DANS REGLES CUMUL : " + libelle)
        return False


    # Test si garantie option à exclure
    def test_exclusion_garanties_options_premium(self, liste_exclusion, garantie):

        for row in liste_exclusion:
            if row[0] == garantie:
                return True
        return False


    # Mise à jour tarif santé dans base de données
    def update_tarif_sante(self, rows_sante):

        try:
    ##        req = """UPDATE ENEFP SET BaseMontantSpecifiqueMontant = ?
    ##                    WHERE
    ##                        Contrat_ReferenceContrat = ?
    ##                        AND Option_CodeOption = ?
    ##                        AND Population_CodePopulation = ?
    ##                        AND MDG_JustificatifElementsCotisation = ?
    ##                        AND ValeurCodeNature = ?
    ##                        AND LibelleCodeNature = ?
    ##                    ;"""
    ##        db.executemany_req(req, rows_sante)

            self.log("MISE A JOUR TARIFS SANTE")

            for row in rows_sante:

                if row[5] == "18":

                    req = """UPDATE ENEFP SET
                                    BaseMontantSpecifiqueTaux = \"""" + row[0] + """\",
                                    ConditionTarifaire = \"""" + row[7] + """\"
                                WHERE
                                    Contrat_ReferenceContrat = \"""" + row[1] + """\"
                                    AND Option_CodeOption = \"""" + row[2] + """\"
                                    AND Population_CodePopulation = \"""" + row[3] + """\"
                                    AND MDG_JustificatifElementsCotisation = \"""" + row[4] + """\"
                                    AND ValeurCodeNature = \"""" + row[5] + """\"
                                    AND LibelleCodeNature = \"""" + row[6] + """\"
                                ;"""


                elif row[5] == "20":

                    req = """UPDATE ENEFP SET
                                    BaseMontantSpecifiqueMontant = \"""" + row[0] + """\",
                                    ConditionTarifaire = \"""" + row[7] + """\"
                                WHERE
                                    Contrat_ReferenceContrat = \"""" + row[1] + """\"
                                    AND Option_CodeOption = \"""" + row[2] + """\"
                                    AND Population_CodePopulation = \"""" + row[3] + """\"
                                    AND MDG_JustificatifElementsCotisation = \"""" + row[4] + """\"
                                    AND ValeurCodeNature = \"""" + row[5] + """\"
                                    AND LibelleCodeNature = \"""" + row[6] + """\"
                                ;"""

                self.db.execute_req(req)

        except sqlite3.Error as error:
            self.log("ERREUR_FONCTION;update_tarif_sante" + error)


    # Mise à jour tarif santé dans base de données
    def update_del_assist(self, rows_assist):

        self.log("SUPPRESSION LIGNES ASSISTANCE")

        try:
            req = """UPDATE ENEFP SET ETAT = "DEL__ASSIST_PREMIUM"
                        WHERE
                            Contrat_ReferenceContrat = ?
                            AND Option_CodeOption = ?
                            AND Population_CodePopulation = ?
                            AND MDG_JustificatifElementsCotisation = ?
                            AND LibelleCodeNature = ?
                        ;"""
            self.db.executemany_req(req, rows_assist)

        except sqlite3.Error as error:
            self.log("ERREUR_FONCTION;update_del_assist;" + str(error))


    # Formatage du tarif selon son type (montant, taux, coefficient)
    def format_tarif(self, tarif, type):

        if type == "MNT":
            ent_part = 9
            dec_part = 2
        elif type == "TAUX":
            ent_part = 3
            dec_part = 4
        elif type == "COEFF":
            ent_part = 3
            dec_part = 2
        else:
            ent_part = 10
            dec_part = 2

        split_tarif = tarif.split(',')

        tarif = split_tarif[0].zfill(ent_part) + ',' +  split_tarif[1].ljust(dec_part, "0")

        return tarif




#------------------------------------------------------------------------------#
# Test de la classe
if __name__ == '__main__':

    ##ENEFP_IN = r"C:\DATA\_in_\_extractions_\ENEFP\Cumul assistance Premium\TestCumul.csv" ## A garder pour débug et TNR
    ##ENEFP_IN = r"C:\DATA\_in_\_extractions_\ENEFP\Cumul assistance Premium\ENEFPS01_18012023_19_22_10_XDEMANDE_SQUI11.csv" ## 8.14

    ENEFP_IN = "C:\DATA\_in_\_extractions_\ENEFP\Cumul assistance Premium\ENEFPS01_01022023_17_31_21_PROD.csv"


    ENEFP_OUT = r"C:\DATA\_out_\python\ENEFP_CUMUL_ASSISTANCE_PREMIUM_" + datetime.datetime.today().strftime('%Y%m%d_%H%M%S') + ".csv"

    PARAMS = [True, True, True, True, True]

    VERBOSE = True

    EnefpModifs = EnefpModifier(ENEFP_IN, ENEFP_OUT, PARAMS, VERBOSE)

