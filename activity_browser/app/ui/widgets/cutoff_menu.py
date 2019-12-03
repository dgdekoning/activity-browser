# -*- coding: utf-8 -*-
from typing import Union

from PySide2.QtCore import Qt, Signal, Slot
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QRadioButton, QSlider, \
    QLabel, QLineEdit, QPushButton
from PySide2.QtGui import QIntValidator, QDoubleValidator
from math import log10

from activity_browser.app.ui.style import vertical_line


class CutoffMenu(QWidget):
    slider_change = Signal()

    def __init__(self, parent_widget, cutoff_value=0.01, limit_type="percent"):
        super(CutoffMenu, self).__init__()
        self.parent = parent_widget
        self.cutoff_value = cutoff_value
        self.limit_type = limit_type
        self.make_layout()
        self.connect_signals()

    def connect_signals(self):
        # Cut-off types
        self.cutoff_type_topx.clicked.connect(self.cutoff_type_topx_check)
        self.cutoff_type_relative.clicked.connect(self.cutoff_type_relative_check)
        self.cutoff_slider_lft_btn.clicked.connect(self.cutoff_increment_left_check)
        self.cutoff_slider_rght_btn.clicked.connect(self.cutoff_increment_right_check)

        # Cut-off log slider
        self.cutoff_slider_log_slider.valueChanged.connect(
            lambda: self.cutoff_slider_relative_check("sl"))
        self.cutoff_slider_line.textChanged.connect(
            lambda: self.cutoff_slider_relative_check("le"))
        # Cut-off slider
        self.cutoff_slider_slider.valueChanged.connect(
            lambda: self.cutoff_slider_topx_check("sl"))
        self.cutoff_slider_line.textChanged.connect(
            lambda: self.cutoff_slider_topx_check("le"))

    @Slot(name="incrementLeftCheck")
    def cutoff_increment_left_check(self):
        """ Move the slider 1 increment when left button is clicked. """
        if self.cutoff_type_relative.isChecked():
            num = int(self.cutoff_slider_log_slider.value())
            self.cutoff_slider_log_slider.setValue(num + 1)
        else:
            num = int(self.cutoff_slider_slider.value())
            self.cutoff_slider_slider.setValue(num - 1)

    @Slot(name="incrementRightCheck")
    def cutoff_increment_right_check(self):
        """ Move the slider 1 increment when right button is clicked. """
        if self.cutoff_type_relative.isChecked():
            num = int(self.cutoff_slider_log_slider.value())
            self.cutoff_slider_log_slider.setValue(num - 1)
        else:
            num = int(self.cutoff_slider_slider.value())
            self.cutoff_slider_slider.setValue(num + 1)

    @Slot(name="relativeCheck")
    def cutoff_type_relative_check(self):
        """ Set cutoff to process that contribute #% or more. """
        self.cutoff_slider_slider.setVisible(False)
        self.cutoff_slider_log_slider.blockSignals(True)
        self.cutoff_slider_slider.blockSignals(True)
        self.cutoff_slider_line.blockSignals(True)
        self.cutoff_slider_unit.setText("%  of total")
        self.cutoff_slider_min.setText("100%")
        self.cutoff_slider_max.setText("0.001%")
        self.limit_type = "percent"
        self.cutoff_slider_log_slider.blockSignals(False)
        self.cutoff_slider_slider.blockSignals(False)
        self.cutoff_slider_line.blockSignals(False)
        self.cutoff_slider_log_slider.setVisible(True)

    @Slot(name="topXCheck")
    def cutoff_type_topx_check(self):
        """ Set cut-off to the top # of processes. """
        self.cutoff_slider_log_slider.setVisible(False)
        self.cutoff_slider_log_slider.blockSignals(True)
        self.cutoff_slider_slider.blockSignals(True)
        self.cutoff_slider_line.blockSignals(True)
        self.cutoff_slider_unit.setText(" top #")
        self.cutoff_slider_min.setText(str(self.cutoff_slider_slider.minimum()))
        self.cutoff_slider_max.setText(str(self.cutoff_slider_slider.maximum()))
        self.limit_type = "number"
        self.cutoff_slider_log_slider.blockSignals(False)
        self.cutoff_slider_slider.blockSignals(False)
        self.cutoff_slider_line.blockSignals(False)
        self.cutoff_slider_slider.setVisible(True)

    @Slot(str, name="sliderRelativeCheck")
    def cutoff_slider_relative_check(self, editor: str):
        """ With relative selected, change the values for plots and tables to reflect the slider/line-edit. """
        if self.cutoff_type_relative.isChecked():
            self.cutoff_validator = self.cutoff_validator_float
            self.cutoff_slider_line.setValidator(self.cutoff_validator)
            cutoff = float

            # If called by slider
            if editor == "sl":
                self.cutoff_slider_line.blockSignals(True)
                cutoff = abs(self.cutoff_slider_log_slider.log_value)
                self.cutoff_slider_line.setText(str(cutoff))
                self.cutoff_slider_line.blockSignals(False)

            # if called by line edit
            elif editor == "le":
                self.cutoff_slider_log_slider.blockSignals(True)
                if self.cutoff_slider_line.text() == '-':
                    cutoff = 0.001
                    self.cutoff_slider_line.setText("0.001")
                elif self.cutoff_slider_line.text() == '':
                    cutoff = 0.001
                else:
                    cutoff = abs(float(self.cutoff_slider_line.text()))

                if cutoff > 100:
                    cutoff = 100
                    self.cutoff_slider_line.setText(str(cutoff))
                self.cutoff_slider_log_slider.log_value = float(cutoff)
                self.cutoff_slider_log_slider.blockSignals(False)

            self.cutoff_value = (cutoff/100)
            self.slider_change.emit()

    @Slot(str, name="sliderTopXCheck")
    def cutoff_slider_topx_check(self, editor: str):
        """ With top # selected, change the values for plots and tables to reflect the slider/line-edit. """
        if self.cutoff_type_topx.isChecked():
            self.cutoff_validator = self.cutoff_validator_int
            self.cutoff_slider_line.setValidator(self.cutoff_validator)
            cutoff = int

            # If called by slider
            if editor == "sl":
                self.cutoff_slider_line.blockSignals(True)
                cutoff = abs(int(self.cutoff_slider_slider.value()))
                self.cutoff_slider_line.setText(str(cutoff))
                self.cutoff_slider_line.blockSignals(False)

            # if called by line edit
            elif editor == "le":
                self.cutoff_slider_slider.blockSignals(True)
                if self.cutoff_slider_line.text() == '-':
                    cutoff = self.cutoff_slider_slider.minimum()
                    self.cutoff_slider_line.setText(str(self.cutoff_slider_slider.minimum()))
                elif self.cutoff_slider_line.text() == '':
                    cutoff = self.cutoff_slider_slider.minimum()
                else:
                    cutoff = abs(int(self.cutoff_slider_line.text()))

                if cutoff > self.cutoff_slider_slider.maximum():
                    cutoff = self.cutoff_slider_slider.maximum()
                    self.cutoff_slider_line.setText(str(cutoff))
                self.cutoff_slider_slider.setValue(int(cutoff))
                self.cutoff_slider_slider.blockSignals(False)

            self.cutoff_value = int(cutoff)
            self.slider_change.emit()

    def make_layout(self):
        """ Add the cut-off menu to the tab. """
        layout = QHBoxLayout()

        # Cut-off types
        cutoff_type = QVBoxLayout()
        cutoff_type_label = QLabel("Cut-off type")
        self.cutoff_type_relative = QRadioButton("Relative")
        self.cutoff_type_relative.setChecked(True)
        self.cutoff_type_topx = QRadioButton("Top #")

        # Cut-off slider
        cutoff_slider = QVBoxLayout()
        cutoff_slider_set = QVBoxLayout()
        cutoff_slider_label = QLabel("Cut-off level")
        self.cutoff_slider_slider = QSlider(Qt.Horizontal, self)
        self.cutoff_slider_log_slider = LogarithmicSlider(self)
        self.cutoff_slider_log_slider.setInvertedAppearance(True)
        self.cutoff_slider_slider.setMinimum(1)
        self.cutoff_slider_slider.setMaximum(50)
        self.cutoff_slider_slider.setValue(self.cutoff_value)
        self.cutoff_slider_log_slider.log_value = self.cutoff_value
        cutoff_slider_minmax = QHBoxLayout()
        self.cutoff_slider_min = QLabel("100%")
        self.cutoff_slider_max = QLabel("0.001%")
        cutoff_slider_ledit = QHBoxLayout()
        self.cutoff_slider_line = QLineEdit()
        self.cutoff_validator_int = QIntValidator(self.cutoff_slider_line)
        self.cutoff_validator_float = QDoubleValidator(self.cutoff_slider_line)
        self.cutoff_validator = self.cutoff_validator_int
        self.cutoff_slider_line.setValidator(self.cutoff_validator)

        self.cutoff_slider_unit = QLabel("%  of total")

        self.cutoff_slider_lft_btn = QPushButton("<")
        self.cutoff_slider_lft_btn.setMaximumWidth(15)
        self.cutoff_slider_rght_btn = QPushButton(">")
        self.cutoff_slider_rght_btn.setMaximumWidth(15)

        # Assemble types
        cutoff_type.addWidget(cutoff_type_label)
        cutoff_type.addWidget(self.cutoff_type_relative)
        cutoff_type.addWidget(self.cutoff_type_topx)

        # Assemble slider set
        cutoff_slider_set.addWidget(cutoff_slider_label)
        cutoff_slider_set.addWidget(self.cutoff_slider_slider)
        self.cutoff_slider_slider.setVisible(False)
        cutoff_slider_minmax.addWidget(self.cutoff_slider_min)
        cutoff_slider_minmax.addWidget(self.cutoff_slider_log_slider)
        cutoff_slider_minmax.addWidget(self.cutoff_slider_max)
        cutoff_slider_set.addLayout(cutoff_slider_minmax)

        cutoff_slider_ledit.addWidget(self.cutoff_slider_line)
        cutoff_slider_ledit.addWidget(self.cutoff_slider_lft_btn)
        cutoff_slider_ledit.addWidget(self.cutoff_slider_rght_btn)
        cutoff_slider_ledit.addWidget(self.cutoff_slider_unit)
        cutoff_slider_ledit.addStretch(1)

        cutoff_slider.addLayout(cutoff_slider_set)
        cutoff_slider.addLayout(cutoff_slider_ledit)

        # Assemble cut-off menu
        layout.addLayout(cutoff_type)
        layout.addWidget(vertical_line())
        layout.addLayout(cutoff_slider)
        layout.addStretch()

        self.setLayout(layout)


# Logarithmic math refresher:
# BOP Base, Outcome Power;
# log(B)(O) = P --> log(2)(64) = 6  ||  log(10)(1000) = 3
#       B^P = O -->        2^6 = 64 ||           10^3 = 1000

class LogarithmicSlider(QSlider):
    """ Makes a QSlider object that behaves logarithmically.

    This class uses the property `log_value` getter and setter to modify
    the QSlider through the `value` and `setValue` methods.
    """
    def __init__(self, parent=None):
        super().__init__(Qt.Horizontal, parent)
        self.setMinimum(1)
        self.setMaximum(100)

    @property
    def log_value(self) -> Union[int, float]:
        """ Read (slider) value and modify it from
        1-100 to 0.001-100 logarithmically with relevant rounding.
        """
        value = float(self.value())
        log_val = log10(value)
        power = log_val * 2.5 - 3
        ret_val = 10 ** power

        if log10(ret_val) < -1:
            ret_val = round(ret_val, 3)
        elif log10(ret_val) < -0:
            ret_val = round(ret_val, 2)
        elif log10(ret_val) < 1:
            ret_val = round(ret_val, 1)
        else:
            ret_val = int(round(ret_val, 0))
        return ret_val

    @log_value.setter
    def log_value(self, value: float) -> None:
        """ Modify value from 0.001-100 to 1-100 logarithmically and set
        slider to value.
        """
        value = int(float(value) * (10 ** 3))
        log_val = round(log10(value), 3)
        set_val = log_val * 20
        self.setValue(set_val)
