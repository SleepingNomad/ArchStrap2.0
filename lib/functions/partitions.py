from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

import os

def add_partitions(combo_box: QComboBox):
    partitions = []

    # NVMe Partitionen abrufen
    nvme_partitions = [filename for filename in os.listdir('/dev') if filename.startswith('nvme0n1')]
    partitions.extend(nvme_partitions)

    # SATA Partitionen abrufen
    sata_partitions = [filename for filename in os.listdir('/dev') if filename.startswith('sda')]
    partitions.extend(sata_partitions)

    # Partitionen umdrehen
    partitions.reverse()

    # Partitionen zur ComboBox hinzufügen
    combo_box.addItems(partitions)