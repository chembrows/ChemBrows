#!/usr/bin/python
# -*-coding:Utf-8 -*


"""Module pour modifier le style et la présentation de la vue"""

import sys
import os
from PyQt4 import QtCore, QtGui, QtSql

from functions import prettyDate


class ViewDelegate(QtGui.QStyledItemDelegate):

    """
    Personnal delegate to draw thumbnails.
    http://www.siteduzero.com/forum-83-812350-p1-pyqt-inserer-des-images-dans-un-qtableview.html#r7783319

    To draw a picture in a cell:
    http://stackoverflow.com/questions/6464741/qtableview-with-a-column-of-images
    """


    def __init__(self, parent):

        super(ViewDelegate, self).__init__(parent)

        self.parent = parent


    def paint(self, painter, option, index):

        """Method called to draw the content of the cells"""

        # Bool to color lines
        red = False

        # If the data are not complete (i.e 'verif' is False), color red
        verif = index.sibling(index.row(), 11).data()
        if verif == 0:
            red = True

        # If the post is new, set font to bold
        # new = index.sibling(index.row(), 12).data()
        # font = painter.font()
        # if new == 1:
            # # Set the font to bold w/ 2 different ways.
            # # One for the default painter, and one for the custom painter
            # option.font.setWeight(QtGui.QFont.Bold)
            # font.setBold(True)
        # else:
            # font.setBold(False)
        # painter.setFont(font)

        date = index.sibling(index.row(), 4).data()

        # Percentage column, round the percentage
        if index.column() == 1:

            if red:
                painter.fillRect(option.rect, QtGui.QColor(255, 3, 59, 90))

            percentage = index.model().data(index)

            if type(percentage) is float:
                painter.drawText(option.rect, QtCore.Qt.AlignCenter, str(int(round(percentage, 0))))
            else:
                painter.drawText(option.rect, QtCore.Qt.AlignCenter, str(0))



        # Actions on the title
        elif index.column() == 3:

            # http://stackoverflow.com/questions/23802170/word-wrap-with-html-qtabelview-and-delegates

            # Modify the text to display
            options = QtGui.QStyleOptionViewItemV4(option)
            self.initStyleOption(options, index)

            painter.save()

            # Tansform the text into a QDocument
            doc = QtGui.QTextDocument()
            text_option = QtGui.QTextOption(doc.defaultTextOption())
            text_option.setWrapMode(QtGui.QTextOption.WordWrap)  # Enable word wrap
            doc.setDefaultTextOption(text_option)

            journal = index.sibling(index.row(), 5).data()
            date = prettyDate(index.sibling(index.row(), 4).data())

            percentage = index.sibling(index.row(), 1).data()
            if type(percentage) is float:
                percentage = str(int(round(percentage, 0)))
            else:
                percentage = 0

            adding_infos = ""
            adding_infos += "<br><br>"
            adding_infos += "<b><font color='gray'>Published in: </font></b><i>{0}</i>, {1}".format(journal, date)
            adding_infos += "<br>"
            adding_infos += "<b><font color='gray'>Match: </font></b>{0} %".format(percentage)

            doc.setHtml(options.text + adding_infos)

            # Set the width of the text = the width of the rect
            doc.setTextWidth(options.rect.width())

            height = doc.documentLayout().documentSize().height()

            if height > options.rect.height():
                doc.setHtml(options.text)
                doc.setTextWidth(options.rect.width())
                height = doc.documentLayout().documentSize().height()

                # while doc.documentLayout().documentSize().height() > options.rect.height():

            options.text = ""
            options.widget.style().drawControl(QtGui.QStyle.CE_ItemViewItem, options, painter)

            # Center the text vertically
            height = doc.documentLayout().documentSize().height()
            painter.translate(options.rect.left(), options.rect.top() + options.rect.height() / 2 - height / 2)

            clip = QtCore.QRectF(0, 0, options.rect.width(), options.rect.height())
            doc.drawContents(painter, clip)

            painter.restore()

            new = index.sibling(index.row(), 12).data()


            # Paint a star in the right bottom corner
            # DIMENSION = 40
            DIMENSION = options.rect.width() * 0.07

            # Get the like state of the post
            liked = index.sibling(index.row(), 9).data()

            # If the post is liked, display the like star.
            # Else, display the unlike star
            if liked == 1:
                # path = "./images/glyphicons_049_star.png"
                # path = "./images/full1.png"
                path = "./images/full2.png"
            else:
                # path = "./images/glyphicons_048_dislikes.png"
                # path = "./images/empty1.png"
                path = "./images/empty2.png"

            pixmap = QtGui.QPixmap.fromImage(QtGui.QImage(path))

            pos_x = option.rect.x() + option.rect.width() - DIMENSION
            pos_y = option.rect.y() + option.rect.height() - DIMENSION

            painter.drawPixmap(pos_x, pos_y, DIMENSION, DIMENSION, pixmap)

            if new:
                pixmap = QtGui.QPixmap.fromImage(QtGui.QImage("images/new.png"))
                painter.drawPixmap(pos_x - DIMENSION, pos_y, DIMENSION, DIMENSION, pixmap)
            if red:
                painter.fillRect(option.rect, QtGui.QColor(255, 3, 59, 90))


        # Actions on the date
        elif index.column() == 4:

            if red:
                painter.fillRect(option.rect, QtGui.QColor(255, 3, 59, 90))

            painter.drawText(option.rect, QtCore.Qt.AlignCenter, prettyDate(date))

        # Thumbnail's index
        elif index.column() == 8:

            if type(index.data()) == str and index.data() != "Empty":
                path_photo = "./graphical_abstracts/" + index.data()

                if os.path.exists(path_photo):
                    # --- la photo existe: on l'affiche dans la case -------------

                    # on charge la photo dans un QPixmap
                    pixmap = QtGui.QPixmap(path_photo)

                    wcase, hcase = option.rect.width(), option.rect.height()
                    wpix, hpix =  pixmap.width(), pixmap.height()

                    # redim si nécessaire à la taille de la case sans déformation
                    if wpix != wcase or hpix != hcase:
                        pixmap = pixmap.scaled(wcase, hcase,
                                                 QtCore.Qt.KeepAspectRatio,
                                                 # Better image with smoothing
                                                 QtCore.Qt.SmoothTransformation)
                        wpix, hpix = pixmap.width(), pixmap.height()

                    # Draw the picture at the center
                    x = option.rect.x() + (wcase - wpix) // 2
                    y = option.rect.y() + (hcase - hpix) // 2

                    # Draw in the calculated rectangle
                    painter.drawPixmap(QtCore.QRect(x, y, wpix, hpix), pixmap)

            else:
                # The picture doesn't exist: grey rectangle
                # painter.fillRect(option.rect, QtGui.QColor("green"))
                # painter.fillRect(option.rect, QtGui.QColor(100, 100, 100, 90))

                # pixmap = QtGui.QPixmap("images/censored.jpg")
                pixmap = QtGui.QPixmap("images/not_available.png")

                wcase, hcase = option.rect.width(), option.rect.height()
                wpix, hpix =  pixmap.width(), pixmap.height()

                # redim si nécessaire à la taille de la case sans déformation
                if wpix != wcase or hpix != hcase:
                    pixmap = pixmap.scaled(wcase, hcase,
                                             QtCore.Qt.KeepAspectRatio,
                                             # Better image with smoothing
                                             QtCore.Qt.SmoothTransformation)
                    wpix, hpix = pixmap.width(), pixmap.height()

                # Draw the picture at the center
                x = option.rect.x() + (wcase - wpix) // 2
                y = option.rect.y() + (hcase - hpix) // 2

                # Draw in the calculated rectangle
                painter.drawPixmap(QtCore.QRect(x, y, wpix, hpix), pixmap)


        else:
            # Using default painter
            QtGui.QStyledItemDelegate.paint(self, painter, option, index)

            if red:
                painter.fillRect(option.rect, QtGui.QColor(255, 3, 59, 90))
