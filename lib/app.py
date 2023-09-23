import os
import shelve
import shutil
import subprocess
import sys
import time

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

import lib.assets.resource_rc
from lib.functions import validate
from lib.functions.lists import *
from lib.functions.partitions import add_partitions
from lib.window import Ui
from lib.functions.write import write_string_to_line

tempFile = QTemporaryFile()


class MainWindow(QMainWindow, Ui):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
               
        comboboxes = [self.comboBox_language, self.comboBox_timezone, self.comboBox_desktopEnvironment, self.comboBox_displayManager, self.comboBox_kernel]
        dictionarys = [LANGUAGE, TIMEZONE, DESKTOP_ENVIRONMENT, DISPLAY_MANAGER, KERNEL]
        partitions = [self.comboBox_efi, self.comboBox_swap, self.comboBox_root]
        
        for _box, dictionary in zip([ comboboxes[0], comboboxes[2], comboboxes[3], comboboxes[4]],
                                [dictionarys[0], dictionarys[2], dictionarys[3], dictionarys[4]]):
            _box.addItems(dictionary)
            
        comboboxes[1].addItems(dictionarys[1])
        
        for index in comboboxes:
            index.setCurrentIndex(-1)
            
        for _box in [comboboxes[0], comboboxes[1]]:
            _box.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            
        for partition in partitions:
            add_partitions(partition)
            partition.setCurrentIndex(-1)
        
        self.pushButton_start.clicked.connect(lambda: self.mainStacked.setCurrentIndex(1))
        self.pushButton_exit.clicked.connect(lambda: sys.exit(0))
        self.pushButton_next.clicked.connect(lambda: self.mainStacked.setCurrentIndex(2))
        self.pushButton_back.clicked.connect(lambda: self.mainStacked.setCurrentIndex(1))
        

        self.process(comboboxes=comboboxes, combobox_dictionarys=dictionarys, partitions=partitions, checkbox_dictionary=OPTIONALS)


    def process(self, comboboxes: list[QComboBox], combobox_dictionarys: dict, partitions: list[QComboBox], checkbox_dictionary: dict):
        self.lineEdit_username.textChanged.connect(lambda: validate.username(self.lineEdit_username))
        self.lineEdit_hostname.textChanged.connect(lambda: validate.hostname(self.lineEdit_hostname))
        
        self.lineEdit_upasswd.textChanged.connect(lambda: validate.password(self.lineEdit_upasswd))
        self.lineEdit_upasswd_confirm.textChanged.connect(lambda: validate.password_confirm(self.lineEdit_upasswd, self.lineEdit_upasswd_confirm, 1))
        
        self.lineEdit_rpasswd.textChanged.connect(lambda: validate.password(self.lineEdit_rpasswd))
        self.lineEdit_rpasswd_confirm.textChanged.connect(lambda: validate.password_confirm(self.lineEdit_rpasswd, self.lineEdit_rpasswd_confirm, 2))

        comboboxes[0].currentIndexChanged.connect(lambda: validate.environment_setting(comboboxes[0], combobox_dictionarys[0], 1))
        comboboxes[1].currentIndexChanged.connect(lambda: validate.environment_setting(comboboxes[1], None, None))
        comboboxes[2].currentIndexChanged.connect(lambda: validate.environment_setting(comboboxes[2], combobox_dictionarys[2], 2))
        comboboxes[3].currentIndexChanged.connect(lambda: validate.environment_setting(comboboxes[3], combobox_dictionarys[3], 3))
        comboboxes[4].currentIndexChanged.connect(lambda: validate.environment_setting(comboboxes[4], combobox_dictionarys[4], 4))

        partitions[0].currentIndexChanged.connect(lambda: validate.partition(partitions[0], 'EFI', partitions[1], partitions[2]))
        partitions[1].currentIndexChanged.connect(lambda: validate.partition(partitions[1], 'SWAP', partitions[0], partitions[2]))
        partitions[2].currentIndexChanged.connect(lambda: validate.partition(partitions[2], 'ROOT', partitions[0], partitions[1]))
        
        self.pushButton_install.clicked.connect(lambda: self.start_installer(self.checkboxes, OPTIONALS))
        
        self.checkboxes = [
            self.checkBox_chrome, self.checkBox_jdownloader, 
            self.checkBox_openvpn, self.checkBox_trojan, 
            self.checkBox_v2ray, self.checkBox_freenet, 
            self.checkBox_lokinet, self.checkBox_thorium, 
            self.checkBox_tuntox, self.checkBox_wireguard, 
            self.checkBox_httperf, self.checkBox_motrix, 
            self.checkBox_tor, self.checkBox_vegeta, 
            self.checkBox_6tunnel, self.checkBox_aide, 
            self.checkBox_gnupg, self.checkBox_metaplsoit, 
            self.checkBox_ossec, self.checkBox_snort, 
            self.checkBox_tiger, self.checkBox_zeek, 
            self.checkBox_bitwarden, self.checkBox_kgpg, 
            self.checkBox_ngrep, self.checkBox_rootkit, 
            self.checkBox_sshGuard, self.checkBox_wireshark, 
            self.checkBox_clamav, self.checkBox_masshash, 
            self.checkBox_nmap, self.checkBox_scrypt, 
            self.checkBox_steghide, self.checkBox_xplico, 
            self.checkBox_abiword, self.checkBox_gscan2pdf, 
            self.checkBox_onlyoffice, self.checkBox_xmond, 
            self.checkBox_cherrytree, self.checkBox_marktext, 
            self.checkBox_texstudio, self.checkBox_geany, 
            self.checkBox_micro, self.checkBox_tikzit, 
            self.checkBox_birdfont, self.checkBox_figma, 
            self.checkBox_imageMagick, self.checkBox_nomacs, 
            self.checkBox_wifu2x, self.checkBox_blender, 
            self.checkBox_gimp, self.checkBox_impgg, 
            self.checkBox_snappy, self.checkBox_coulr, 
            self.checkBox_gwenview, self.checkBox_inkscape, 
            self.checkBox_synfig, self.checkBox_bazel, 
            self.checkBox_fontManager, self.checkBox_kitty, 
            self.checkBox_miniconda, self.checkBox_okular, 
            self.checkBox_vscode, self.checkBox_cairo, 
            self.checkBox_gparted, self.checkBox_krusader, 
            self.checkBox_meson, self.checkBox_rsync, 
            self.checkBox_xterm, self.checkBox_dolphin, 
            self.checkBox_gradle, self.checkBox_latteDock, 
            self.checkBox_ohMyZsh, self.checkBox_vmware, 
            self.checkBox_neofetch]
        
    def start_installer(self, checkbox_list, checkbox_dictionary):

            validate.get_optional_checkboxes(checkbox_list, checkbox_dictionary, 'OPTIONALS')
            self.hide()
            if self.isHidden():
                self.tempdir = QTemporaryDir()
                self.dst = self.tempdir.path()
                shutil.copyfile('lib/process.sh', f"{self.dst}/install.sh")
                shutil.copyfile('tmp/archlinux-bootstrap-x86_64.tar.gz', f"{self.dst}/archlinux-bootstrap-x86_64.tar.gz")
                with open(f"""{self.dst}/configfile""", 'w') as env:
                    with shelve.open('tmp/settings') as db:
                        for key, value in db.items():
                            if key == 'OPTIONALS':
                                env.write(f"{key}={value}\n")
                            else:
                                env.write(f"{key}='{value}'\n")

                write_string_to_line(f"{self.dst}/install.sh", 4, f"temp={self.tempdir.path()}")
                time.sleep(3)


                os.remove('tmp/settings')
                subprocess.run(['sudo', 'bash', f"{self.dst}/install.sh", '-u'], shell=False)
                sys.exit(0)
