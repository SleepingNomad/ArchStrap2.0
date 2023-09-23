import re
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import shelve
from typing import List, Dict


def write_to_db(key: str, value) -> None:
    """
    Write the given key-value pair to the database.

    Args:
        key (str): The key to write.
        value (Any): The value to write.

    Returns:
        None
    """
    with shelve.open('tmp/settings') as db:
        db.update({k: None for k, v in db.items() if v in ('', None)})
        db[key] = value
def get_optional_checkboxes(checkboxes: List[QCheckBox], dictionary: Dict[str, str], key: str) -> None:
    """
    Update the function signature with type hints.

    :param checkboxes: List of QCheckBox objects
    :param dictionary: Dictionary with string keys and string values
    :param key: A string representing the key
    """

    checked: List[str] = [checkbox.text() for checkbox in checkboxes if checkbox.isChecked()]

    remove_item_from_checklist(dictionary, checked, 'Miniconda', 'MINICONDA')
    remove_item_from_checklist(dictionary, checked, 'Figma', 'FIGMA')
    remove_item_from_checklist(dictionary, checked, 'Oh-My-Zsh', 'OHMYZSH')

    refactored: List[str] = [dictionary.get(item) for item in checked]

    write_to_db(key, str(refactored).replace('"','').replace('[', '(').replace(']', ')').replace(',',''))
    
def remove_item_from_checklist(dictionary: dict, checked: list, key: str, value_key: str) -> None:
    if key in checked:
        checked.remove(key)
        value = dictionary.get(key)
        write_to_db(value_key, value)

def partition(component_1: QComboBox, partition_1_name: str('efi') or str('swap') or str('root'), component_2: QComboBox, component_3: QComboBox):
    partition_1 = component_1.currentText()
    partition_2 = component_2.currentText()
    partition_3 = component_3.currentText()
    
    if component_1.currentIndex() == -1:
        default_combobox(component_1)
    else:
        if partition_1 == partition_2 or partition_1 == partition_3:
            error_combobox(component_1)
        else:
            default_combobox(component_1)
            write_to_db(f"{partition_1_name}_PARTITION", f"/dev/{partition_1}")

    
def environment_setting(component: QComboBox, dictionary: dict, kind_of_environment: 1|2|3|4 or None):
    item = component.currentText()

    if kind_of_environment is None:
        write_to_db('ENVIRONMENT', item)
        
    else:
        value = dictionary.get(item)
    
        if component.currentIndex() == -1 or value == 1 or value == "":
            match kind_of_environment:
                case 1:
                    error_combobox(component)
                case 2:
                    error_combobox(component)
                case 3:
                    error_combobox(component)
                case 4:
                    error_combobox(component)
        else:
            default_combobox(component)
            match kind_of_environment:
                case 1:
                    write_to_db('LANGUAGE', value)
                    
                case 2:
                    write_to_db('DESKTOP_ENVIRONMENT', value)
                    
                case 3:
                    write_to_db('DISPLAY_MANAGER', value)
                    
                case 4:
                    write_to_db('KERNEL', value)
                    
def username(line_edit: QLineEdit):
    text = line_edit.text()

    if not text.strip():
        default_lineedit(line_edit)
    elif re.match(r"^[a-z][a-zA-Z0-9]{3,12}$", text):
        success_lineedit(line_edit)
        write_to_db('USERNAME', text)
        
    elif len(text) <= 3:
        default_lineedit(line_edit)
    else:
        error_lineedit(line_edit)
def hostname(component: QLineEdit):
    line_edit = component.text()
    pattern_1 = r"^[a-zA-Z0-9](?:[-._]?[a-zA-Z0-9]){3,12}$"
    pattern_2 = r"^\s*$"
    pattern_3 = r"^.{0,3}$"

    if re.match(pattern_1, line_edit):
        success_lineedit(component)
        write_to_db('HOSTNAME', line_edit)
        
    elif re.match(pattern_2, line_edit) or re.match(pattern_3, line_edit):
        default_lineedit(component)
    else:
        error_lineedit(component)
def password(password_input: QLineEdit):
    password = password_input.text()
    
    if len(password) == 0:
        default_lineedit(password_input)
    elif len(password) >= 1 and len(password) <= 16:
        success_lineedit(password_input)
    else:
        error_lineedit(password_input)
def password_confirm(password1: QLineEdit, password2: QLineEdit, kind_of_password: 1|2):
    password_1 = password1.text()
    password_2 = password2.text()   
    
    if len(password_2) == 0:
        default_lineedit(password2)
    elif re.match(password_2, password_1):
        success_lineedit(password2)
        if kind_of_password == 1:
            write_to_db("UPASSWD", password_2)
            
        elif kind_of_password == 2:
            write_to_db("RPASSWD", password_2)
            
        else:
            raise ValueError("Invalid kind of password")
    else:
        error_lineedit(password2) 
def default_combobox(component):
    component.setStyleSheet(
        """
        QComboBox {
            background-image: url(:/input_field.png);
            border: 1px solid gray;
            border-radius: 3px;
            padding: 1px 18px 1px 3px;
            min-width: 6em;
        }
        """
    )
def success_combobox(component: QComboBox):
    component.setStyleSheet(
        "QComboBox {\n"
        "    background-image: url(:/input_field.png);\n"
        "    border: 1px solid;\n"
        "    border-radius: 3px;\n"
        "    padding: 1px 18px 1px 3px;\n"
        "    min-width: 6em;\n"
        "}\n"
    )
def error_combobox(component: QComboBox):
    component.setStyleSheet(
        """
        QComboBox {
            background-image: url(:/input_field_error.png);
            border: 1px solid red;
            border-radius: 3px;
            padding: 1px 18px 1px 3px;
            min-width: 6em;
        }
        """
    )
def default_lineedit(component: QLineEdit):
    component.setStyleSheet("""
        QLineEdit {
            background-image: url(:/input_field.png);
            border: 1px solid gray;
            border-radius: 3px;
        }
    """)
def success_lineedit(component: QLineEdit):
    component.setStyleSheet(
        "QLineEdit {"
        "    background-image: url(:/input_field_success.png);"
        "    border: 1px solid green;"
        "    border-radius: 3px;"
        "}"
    )
def error_lineedit(component: QLineEdit):
    component.setStyleSheet(
        "QLineEdit {\n"
        "    background-image: url(:/input_field_error.png);\n"
        "    border: 1px solid red;\n"
        "    border-radius: 3px;\n"
        "}"
    )
