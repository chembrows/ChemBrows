#!/usr/bin/python
# coding: utf-8


class MyStyles():

    """Class to handle the styling of the program"""

    # Double { for placeholders
    # http://stackoverflow.com/questions/9623134/python-format-throws-keyerror

    def __init__(self, app):

        self.font = app.font()

        screen_rect = app.desktop().screenGeometry()
        self.height = screen_rect.height()

        # Scale by screen resolution: HD or not
        if self.height >= 900:
            self.FONT_SIZE = 12
            self.DIMENSION = 40
            self.ICON_SIZE_BIG = 36
            self.ICON_SIZE_SMALL = 30
            self.RADIUS = 18
        else:
            self.FONT_SIZE = 8
            self.DIMENSION = 30
            self.ICON_SIZE_BIG = 27
            self.ICON_SIZE_SMALL = 23
            self.RADIUS = 12


    def styleToolbar(self):

        """Define the style for the toolbar"""

        stylesheet = """
            QPushButton[accessibleName="toolbar_text_button"]
            {{
                background: #EF4C39;
                color: white;
                border-radius: {2}px;
                padding: {4}px;
                font-weight: bold;
                margin-left: {3}px;
                margin-right: {3}px;
            }}

            QPushButton[accessibleName="toolbar_round_button"]
            {{
                border: 0px;
                margin-top: {3}px;
                max-width: {0}px;
                max-height: {0}px;
                min-width: {0}px;
                min-height: {0}px;
                background: transparent;
                margin-left: {2}px;
            }}

            QLineEdit
            {{
                margin-left: {3}px;
                margin-top: {3}px;
            }}

            QPushButton[accessibleName="toolbar_round_button"]:pressed
            {{
                background: white;
                border-radius: {1}px;
            }}
        """

        stylesheet = stylesheet.format(self.DIMENSION, self.DIMENSION / 2,
                                       self.DIMENSION / 4, self.DIMENSION / 8,
                                       self.DIMENSION / 5)

        return stylesheet


    def styleGeneral(self):

        """Define the general style"""

        stylesheet = """
            QToolBar, QScrollArea, QTabWidget, QSplitter, .QWidget
            {
                background: #726E73;
                border: 0px;
            }

            QLabel
            {
                color: white
            }

            QWidget
            {
                font-size: FONT_SIZEpt
            }
        """

        stylesheet = stylesheet.replace('FONT_SIZE', str(self.FONT_SIZE))

        return stylesheet


    def styleButtons(self):

        """Define the style for the buttons"""

        stylesheet = """
            QPushButton[accessibleName="round_button_article"]
            {{
                border: 0px;
                margin-top: {2}px;
                max-width: {0}px;
                max-height: {0}px;
                min-width: {0}px;
                min-height: {0}px;
                background: transparent;
            }}

            QPushButton[accessibleName="round_button_article"]:pressed
            {{
                background: white;
                border-radius: {4}px;
            }}

            QPushButton[accessibleName="button_text_left"]
            {{
                background: grey;
                color: white;
                border-radius: {1}px;
                padding: {3}px;
                margin-left: {1}px;
                margin-right: {1}px;
            }}

            QPushButton[accessibleName="button_text_left"]:checked
            {{
                background: #EF4C39;
            }}
        """

        # Scale from ICON_SIZE_BIG, not from dimension, otherwiser the blank
        # around the button_pressed is too wide
        stylesheet = stylesheet.format(self.ICON_SIZE_BIG, self.DIMENSION / 4,
                                       self.DIMENSION / 8, self.DIMENSION / 5,
                                       self.RADIUS)

        return stylesheet


if __name__ == '__main__':
    from PyQt4 import QtGui
    import sys

    app = QtGui.QApplication(sys.argv)
    test = MyStyles(app)
    print(test.styleToolbar())
