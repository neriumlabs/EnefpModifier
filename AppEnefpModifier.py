import json
import os
from tkinter import *
from tkinter import filedialog as fd

class AppEnefpModifier(Tk):



    def __init__(self):

        super().__init__()

        self.CFG_FILENAME = "AppEnefpModifier.cfg"
        self.app_cfg = []
        self.cfg_file_enefp_in = StringVar()
        self.cfg_folder_enefp_out = StringVar()
        self.cfg_del_pmss = IntVar()
        self.cfg_del_autre = IntVar()
        self.cfg_eqpro_reg = IntVar()
        self.cfg_eqpro_ctr = IntVar()
        self.cfg_cumul_assist = IntVar()
        self.cfg_export_csv = IntVar()
        self.cfg_export_xls = IntVar()
        self.cfg_export_del = IntVar()
        self.cfg_force_date_deb = IntVar()
        self.cfg_force_date_fin = IntVar()
        self.cfg_date_deb = StringVar()
        self.cfg_date_fin = StringVar()

        self.title("MODIFICATIONS FICHIER ENEFP")
        self.resizable(0, 0)

        self.width = 800
        self.height = 250
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.startx = (self.screen_width / 2) - (self.width / 2)
        self.starty = (self.screen_height / 2) - (self.height / 2)
        self.geometry(f"{self.width}x{self.height}+{int(self.startx)}+{int(self.starty)}")
        self.minsize(self.width, self.height)
        ##self.iconbitmap('logo.ico')
        self.config(bg='#336699')

        self.create_widgets()
        ##self.create_config() ## A virer pour fonctionnement normal
        self.load_config()
        ##self.save_config()
        self.show_widgets()



    def create_widgets(self):
        self.frame = Frame(self, width=self.width, height=self.height)
        self.frame1 = LabelFrame(self.frame, text="FICHIER", width=self.width, height=100)
        self.label_enefp_in = Label(self.frame1, text="FICHIER ENEFP ENTREE : ")
        self.label_enefp_out = Label(self.frame1, text="DOSSIER ENEFP SORTIE : ")
        self.entry_enefp_in = Entry(self.frame1, width=100)
        self.entry_enefp_out = Entry(self.frame1, width=100)
        self.button_enefp_in = Button(self.frame1, text="...", command=self._btn_browse_enefp_in)
        self.button_enefp_out = Button(self.frame1, text="...", command=self._btn_browse_enefp_out)
        self.frame2 = LabelFrame(self.frame, text="PARAMETRES", width=self.width, height=150)
        self.cb_del_pmss = Checkbutton(self.frame2, text="Supprimer lignes PMSS", variable=self.cfg_del_pmss, onvalue=1, offvalue=0)
        self.cb_del_autre = Checkbutton(self.frame2, text="Supprimer lignes AUTRE", variable=self.cfg_del_autre, onvalue=1, offvalue=0)
        self.cb_eqpro_reg = Checkbutton(self.frame2, text="Equilibre pro réglementaire", variable=self.cfg_eqpro_reg, onvalue=1, offvalue=0)
        self.cb_eqpro_ctr = Checkbutton(self.frame2, text="Equilibre pro contractuel", variable=self.cfg_eqpro_ctr, onvalue=1, offvalue=0)
        self.cb_cumul_assist = Checkbutton(self.frame2, text="Cumuler assistance", variable=self.cfg_cumul_assist, onvalue=1, offvalue=0)
        self.cb_export_csv = Checkbutton(self.frame2, text="Exporter en CSV", variable=self.cfg_export_csv, onvalue=1, offvalue=0)
        self.cb_export_xls = Checkbutton(self.frame2, text="Exporter en XLS", variable=self.cfg_export_xls, onvalue=1, offvalue=0)
        self.cb_export_del = Checkbutton(self.frame2, text="Exporter DEL", variable=self.cfg_export_del, onvalue=1, offvalue=0)
        self.cb_force_date_deb = Checkbutton(self.frame2, text="Forcer date début", variable=self.cfg_force_date_deb, onvalue=1, offvalue=0)
        self.cb_force_date_fin = Checkbutton(self.frame2, text="Forcer date fin", variable=self.cfg_force_date_fin, onvalue=1, offvalue=0)
        self.entry_date_deb = Entry(self.frame2, justify=CENTER)
        self.entry_date_fin = Entry(self.frame2, justify=CENTER)
        self.frame3 = Frame(self.frame, width=self.width, height=100)
        self.btn_ok = Button(self.frame3, text="Lancer traitements", width=15, padx=5, command=self._btn_ok_click)
        self.btn_quit = Button(self.frame3, text="Quitter", width=15, padx=5, command=self._btn_quit_click)


    def show_widgets(self):
        self.label_enefp_in.grid(row=0, column=0, sticky=W, padx=5, pady=2)
        self.label_enefp_out.grid(row=1, column=0, sticky=W, padx=5, pady=2)
        self.entry_enefp_in.grid(row=0, column=1, sticky=W, pady=2)
        self.entry_enefp_out.grid(row=1, column=1, sticky=W, pady=2)
        self.button_enefp_in.grid(row=0, column=2, sticky=W, padx=5, pady=2)
        self.button_enefp_out.grid(row=1, column=2, sticky=W, padx=5, pady=2)
        self.frame1.grid(row=0, column=0, columnspan=3, sticky=W, padx=5, pady=5)
        self.cb_del_pmss.grid(row=0, column=0, sticky=W, padx=5)
        self.cb_del_autre.grid(row=1, column=0, sticky=W, padx=5)
        self.cb_eqpro_reg.grid(row=0, column=1, sticky=W, padx=5)
        self.cb_eqpro_ctr.grid(row=1, column=1, sticky=W, padx=5)
        self.cb_cumul_assist.grid(row=2, column=1, sticky=W, padx=5)
        self.cb_export_csv.grid(row=0, column=2, sticky=W, padx=5)
        self.cb_export_xls.grid(row=1, column=2, sticky=W, padx=5)
        self.cb_export_del.grid(row=2, column=2, sticky=W, padx=5)
        self.cb_force_date_deb.grid(row=0, column=4, sticky=W, padx=5)
        self.cb_force_date_fin.grid(row=1, column=4, sticky=W, padx=5)
        self.entry_date_deb.grid(row=0, column=5, sticky=W, padx=5)
        self.entry_date_fin.grid(row=1, column=5, sticky=W, padx=5)
        self.frame2.grid(row=1, column=0, columnspan=5, sticky=W, padx=5, pady=5)
        self.btn_ok.grid(row=0, column=0, sticky=N, padx=20, pady=5)
        self.btn_quit.grid(row=0, column=1, sticky=N, padx=20, pady=5)
        self.frame3.grid(row=2, column=0, columnspan=5, sticky=N, padx=5, pady=10)
        self.frame.pack(fill=X)

    def create_config(self):
        self.app_cfg = {
            "file_enefp_input": "C:\\",
            "folder_enefp_output": "C:\\",
            "del_pmss": True,
            "del_autre": True,
            "do_eqpro_reg": False,
            "do_eqpro_ctr": False,
            "cumul_assist": True,
            "export_csv": True,
            "export_xls": False,
            "export_del": False,
            "force_date_deb": True,
            "force_date_fin": True,
            "date_deb": "01/01/2023",
            "date_fin": "31/12/2023"
        }
        with open(self.CFG_FILENAME, "w") as cfg_file:
            json.dump(self.app_cfg, cfg_file)


    def load_config(self):
        if os.path.exists(os.path.join(os.getcwd(), self.CFG_FILENAME)):
            with open(self.CFG_FILENAME, "r") as cfg_file:
                self.app_cfg = json.load(cfg_file)
                self.cfg_file_enefp_in = self.app_cfg["file_enefp_input"]
                self.cfg_folder_enefp_out = self.app_cfg["folder_enefp_output"]
                self.cfg_del_pmss = self.app_cfg["del_pmss"]
                self.cfg_del_autre = self.app_cfg["del_autre"]
                self.cfg_eqpro_reg = self.app_cfg["do_eqpro_reg"]
                self.cfg_eqpro_ctr = self.app_cfg["do_eqpro_ctr"]
                self.cfg_cumul_assist = self.app_cfg["cumul_assist"]
                self.cfg_export_csv = self.app_cfg["export_csv"]
                self.cfg_export_xls = self.app_cfg["export_xls"]
                self.cfg_export_del = self.app_cfg["export_del"]
                self.cfg_force_date_deb = self.app_cfg["force_date_deb"]
                self.cfg_force_date_fin = self.app_cfg["force_date_fin"]
                self.cfg_date_deb = self.app_cfg["date_deb"]
                self.cfg_date_fin = self.app_cfg["date_fin"]
                self.update_widgets()


    def save_config(self):
        self.app_cfg["file_enefp_input"] = self.entry_enefp_in.get()
        self.app_cfg["folder_enefp_output"] = self.entry_enefp_out.get()
        self.app_cfg["del_pmss"] = self.cfg_del_pmss.get()
        self.app_cfg["del_autre"] = self.cfg_del_autre.get()
        self.app_cfg["do_eqpro_reg"] = self.cfg_eqpro_reg.get()
        self.app_cfg["do_eqpro_ctr"] = self.cfg_eqpro_ctr.get()
        self.app_cfg["cumul_assist"] = self.cfg_cumul_assist.get()
        self.app_cfg["export_csv"] = self.cfg_export_csv.get()
        self.app_cfg["export_xls"] = self.cfg_export_xls.get()
        self.app_cfg["export_del"] = self.cfg_export_del.get()
        self.app_cfg["force_date_deb"] = self.cfg_force_date_deb.get()
        self.app_cfg["force_date_fin"] = self.cfg_force_date_fin.get()
        self.app_cfg["date_deb"] = self.entry_date_deb.get()
        self.app_cfg["date_fin"] = self.entry_date_fin.get()
        with open(self.CFG_FILENAME, "w") as cfg_file:
            json.dump(self.app_cfg, cfg_file)


    def update_widgets(self):
        for key, value in self.app_cfg.items():
            if key == 'file_enefp_input':
                self.entry_enefp_in.delete(0, END)
                self.entry_enefp_in.insert(0, value)
            elif key == 'folder_enefp_output':
                self.entry_enefp_out.delete(0, END)
                self.entry_enefp_out.insert(0, value)
            elif key == 'del_pmss' and value == 1:
                self.cb_del_pmss.select()
            elif key == 'del_autre' and value == 1:
                self.cb_del_autre.select()
            elif key == 'do_eqpro_ctr' and value == 1:
                self.cb_eqpro_ctr.select()
            elif key == 'do_eqpro_reg' and value == 1:
                self.cb_eqpro_reg.select()
            elif key == 'cumul_assist' and value == 1:
                self.cb_cumul_assist.select()
            elif key == 'export_csv' and value == 1:
                self.cb_export_csv.select()
            elif key == 'export_xls' and value == 1:
                self.cb_export_xls.select()
            elif key == 'export_del' and value == 1:
                self.cb_export_del.select()
            elif key == 'force_date_deb' and value == 1:
                self.cb_force_date_deb.select()
            elif key == 'force_date_fin' and value == 1:
                self.cb_force_date_fin.select()
            elif key == 'date_deb' and value !="":
                self.entry_date_deb.delete(0, END)
                self.entry_date_deb.insert(0, value)
            elif key == 'date_fin' and value !="":
                self.entry_date_fin.delete(0, END)
                self.entry_date_fin.insert(0, value)


    def _btn_browse_enefp_in(self):
        filetypes = (('Fichier csv', '*.csv'), ('Tous les fichiers', '*.*'))
        filename = fd.askopenfilename(title='Ouvrir un fichier ENEFP', initialdir='/', filetypes=filetypes)
        self.entry_enefp_in.delete(0, END)
        self.entry_enefp_in.insert(0, filename)


    def _btn_browse_enefp_out(self):
        foldername = fd.askdirectory()
        self.entry_enefp_out.delete(0, END)
        self.entry_enefp_out.insert(0, foldername)


    def _btn_ok_click(self):
        print("OK")
        self.save_config()


    def _btn_quit_click(self):
        print("QUITTER")
        self.destroy()








#------------------------------------------------------------------------------#
#------------------------------------------------------------------------------#

if __name__ == '__main__':

    app = AppEnefpModifier()
    app.mainloop()

