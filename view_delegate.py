#!/usr/bin/python
# coding: utf-8


import os
from PyQt4 import QtCore, QtGui

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

        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)

        # Get the read/unread state of an article. Colors the cell
        # if the article is unread
        read = index.sibling(index.row(), 12).data()
        if read == 0:
            grey = False
        else:
            grey = True


        # # If the data are not complete (i.e 'verif' is False), color red
        # verif = index.sibling(index.row(), 11).data()
        # if verif == 0:
            # red = True

        date = index.sibling(index.row(), 4).data()

        # Actions on the title
        if index.column() == 3:

            # http://stackoverflow.com/questions/23802170/word-wrap-with-html-qtabelview-and-delegates

            # Modify the text to display
            options = QtGui.QStyleOptionViewItemV4(option)
            self.initStyleOption(options, index)

            painter.save()

            # Tansform the text into a QDocument
            doc = QtGui.QTextDocument()
            text_option = QtGui.QTextOption(doc.defaultTextOption())

            # Enable word wrap
            text_option.setWrapMode(QtGui.QTextOption.WordWrap)
            doc.setDefaultTextOption(text_option)

            journal = index.sibling(index.row(), 5).data()
            date = prettyDate(index.sibling(index.row(), 4).data())

            # Print the infos (formatted)
            adding_infos = ""
            adding_infos += "<br><br>"
            adding_infos += "<b><font color='gray'>Published in: </font></b><i>{0}</i>, {1}".format(journal, date)
            adding_infos += "<br><br>"
            adding_infos += "<b><font color='gray'>Hot Paperness: </font></b>"

            doc.setHtml(options.text + adding_infos)

            # Set the width of the text = the width of the rect
            doc.setTextWidth(options.rect.width())

            height = doc.documentLayout().documentSize().height()

            if height > options.rect.height():
                doc.setHtml(options.text)
                doc.setTextWidth(options.rect.width())
                height = doc.documentLayout().documentSize().height()

            options.text = ""
            options.widget.style().drawControl(QtGui.QStyle.CE_ItemViewItem, options, painter)

            # Center the text vertically
            height = doc.documentLayout().documentSize().height()
            painter.translate(options.rect.left(), options.rect.top() + options.rect.height() / 2.5 - height / 2)

            clip = QtCore.QRectF(0, 0, options.rect.width(), options.rect.height())
            doc.drawContents(painter, clip)

            painter.restore()

            percentage = index.sibling(index.row(), 1).data()
            if type(percentage) is not float:
                percentage = 0

            # Get the like state of the post
            liked = index.sibling(index.row(), 9).data()

            # Constant, proportional to the size of one cell
            DIMENSION = options.rect.width() * 0.05
            # DIMENSION = 35

            # Draw peppers. A full pepper if the match percentage
            # of an article is superior to the element of the list.
            # Else, an empty pepper
            nbr_peppers = [15, 30, 45, 70]
            for index, perc in enumerate(nbr_peppers):

                if percentage >= perc:
                    path = "./images/pepper_full.png"
                else:
                    path = "./images/pepper_empty.png"

                # pixmap = QtGui.QPixmap.fromImage(QtGui.QImage(path))
                pixmap = QtGui.QPixmap(path)
                # pixmap = pixmap.scaled(DIMENSION, DIMENSION, QtCore.Qt.IgnoreAspectRatio,  QtCore.Qt.SmoothTransformation)

                pos_x = option.rect.x() + DIMENSION * 4 + DIMENSION * 0.5 * index
                pos_y = option.rect.y() + option.rect.height() - DIMENSION * 0.8

                painter.drawPixmap(pos_x, pos_y, DIMENSION * 0.7, DIMENSION * 0.7, pixmap)

            # If the post is liked, display the like star.
            # Else, display the unlike star
            if liked == 1:
                path = "./images/like.png"
            else:
                path = "./images/not_like.png"

            pixmap = QtGui.QPixmap.fromImage(QtGui.QImage(path))

            pos_x = option.rect.x() + option.rect.width() - DIMENSION
            pos_y = option.rect.y() + option.rect.height() - DIMENSION

            painter.drawPixmap(pos_x, pos_y, DIMENSION, DIMENSION, pixmap)

            # A picture to display the read/unread state
            if read:
                pixmap = QtGui.QPixmap.fromImage(QtGui.QImage("./images/unread.png"))
                # pixmap = QtGui.QPixmap.fromImage(QtGui.QImage("./images/read_full.png"))
                painter.drawPixmap(pos_x - DIMENSION, pos_y, DIMENSION, DIMENSION, pixmap)
            else:
                pixmap = QtGui.QPixmap.fromImage(QtGui.QImage("./images/read.png"))
                # pixmap = QtGui.QPixmap.fromImage(QtGui.QImage("./images/read_empty.png"))
                painter.drawPixmap(pos_x - DIMENSION, pos_y, DIMENSION, DIMENSION, pixmap)

            if not grey:
                painter.fillRect(option.rect, QtGui.QColor(231, 231, 231, 80))


        # Thumbnail's index
        elif index.column() == 8:

            if type(index.data()) is str and index.data() != "Empty":
                path_photo = "./graphical_abstracts/" + index.data()
                # self.parent.l.debug(path_photo)

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
                # The picture doesn't exist: display a "not available image"
                pixmap = QtGui.QPixmap("./images/not_available.png")

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
