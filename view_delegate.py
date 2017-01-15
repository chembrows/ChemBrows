#!/usr/bin/python
# coding: utf-8


import os
from PyQt5 import QtCore, QtGui, QtWidgets

# Personal
from functions import prettyDate


class ViewDelegate(QtWidgets.QStyledItemDelegate):

    """
    Personnal delegate to draw thumbnails.
    http://www.siteduzero.com/forum-83-812350-p1-pyqt-inserer-des-images-dans-un-qtableview.html#r7783319

    To draw a picture in a cell:
    http://stackoverflow.com/questions/6464741/qtableview-with-a-column-of-images
    """

    def __init__(self, parent):

        super(ViewDelegate, self).__init__(parent)

        self.parent = parent
        self.DATA_PATH = self.parent.DATA_PATH


    def paint(self, painter, option, index):

        """Method called to draw the content of the cells"""

        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)

        # Constant, proportional to the size of one cell
        DIMENSION = self.parent.styles.ICON_SIZE_SMALL

        # Check if the post is in the to-read list
        waited = index.sibling(index.row(), 0).data() in self.parent.waiting_list.articles

        # Get the read/unread state of an article. Colors the cell
        # if the article is unread
        read = index.sibling(index.row(), 11).data()

        date = index.sibling(index.row(), 4).data()

        # Actions on the title
        if index.column() == 3:

            # http://stackoverflow.com/questions/23802170/word-wrap-with-html-qtabelview-and-delegates

            # Modify the text to display
            # options = QtWidgets.QStyleOptionViewItemV4(option)
            options = QtWidgets.QStyleOptionViewItem(option)
            self.initStyleOption(options, index)

            # If the article is unread, color the background of the cell
            if read == 0:
                grey = False
            else:
                grey = True

            if not grey:
                painter.fillRect(option.rect, QtGui.QColor(231, 231, 231))

            painter.save()

            # Tansform the text into a QDocument
            doc = QtGui.QTextDocument()
            text_option = QtGui.QTextOption(doc.defaultTextOption())

            # Enable word wrap
            text_option.setWrapMode(QtGui.QTextOption.WordWrap)
            doc.setDefaultTextOption(text_option)

            title = options.text
            width_title = painter.fontMetrics().width(title)

            # Check if the width is correct. Useful when the program
            # has nos prefs for the interface
            if options.rect.width() > 0:
                # Cut the title at the end of a word if it is too long
                while width_title / 3 > options.rect.width():
                    title = title.split(' ')[:-1]
                    title = ' '.join(title) + "..."
                    width_title = painter.fontMetrics().width(title)

            journal = index.sibling(index.row(), 5).data()
            date = prettyDate(index.sibling(index.row(), 4).data())

            # Print the infos (formatted)
            adding_infos = ""
            adding_infos += "<br><br>"
            adding_infos += "<b><font color='gray'>Published in: </font></b><i>{0}</i>, {1}".format(journal, date)
            # adding_infos += "<br><br>"
            # adding_infos += "<b><font color='gray'>Hot Paperness: </font></b>"

            # doc.setHtml(options.text + adding_infos)
            doc.setHtml(title + adding_infos)

            font = doc.defaultFont()
            font.setPointSize(self.parent.styles.FONT_SIZE)
            doc.setDefaultFont(font)

            # Set the width of the text = the width of the rect
            doc.setTextWidth(options.rect.width())

            height = doc.documentLayout().documentSize().height()

            if height > options.rect.height() - DIMENSION:
                # doc.setHtml(options.text)
                doc.setHtml(title)
                doc.setTextWidth(options.rect.width())
                height = doc.documentLayout().documentSize().height()

            options.text = ""
            options.widget.style().drawControl(QtWidgets.QStyle.CE_ItemViewItem, options, painter)

            # Do not center the text vertically, causes too much bugs
            painter.translate(options.rect.left(), options.rect.top() + options.rect.height() / 2.5 - height / 2)
            # painter.translate(options.rect.left(), options.rect.top())

            clip = QtCore.QRectF(0, -(options.rect.height() / 2.5 - height / 2), options.rect.width(), options.rect.height())
            # clip = QtCore.QRectF(0, 0, options.rect.width(), options.rect.height())

            # Change the background color of the cell here, won't be
            # possible later
            if option.state & QtWidgets.QStyle.State_Selected:
                painter.fillRect(clip, QtGui.QColor(120, 187, 222))
            elif grey:
                painter.fillRect(clip, QtGui.QColor(231, 231, 231))
            else:
                painter.fillRect(clip, QtGui.QColor(255, 255, 255))

            doc.drawContents(painter, clip)

            painter.restore()

            percentage = index.sibling(index.row(), 1).data()
            if type(percentage) is not float:
                percentage = 0

            # Get the like state of the post
            liked = index.sibling(index.row(), 9).data()

            # Draw peppers. A full pepper if the match percentage
            # of an article is superior to the element of the list.
            # Else, an empty pepper
            nbr_peppers = [20, 40, 60, 80]
            for index, perc in enumerate(nbr_peppers):

                if percentage >= perc:
                    path = os.path.join(self.parent.resource_dir, "images/pepper_full.png")
                else:
                    path = os.path.join(self.parent.resource_dir, "images/pepper_empty.png")

                pixmap = QtGui.QPixmap(path)

                pos_x = option.rect.x() + DIMENSION * 0.5 * index
                pos_y = option.rect.y() + option.rect.height() - DIMENSION * 0.8

                painter.drawPixmap(pos_x, pos_y, DIMENSION * 0.75, DIMENSION * 0.75, pixmap)

            # If the post is liked, display the like star.
            # Else, display the unlike star
            if liked == 1:
                path = os.path.join(self.parent.resource_dir, "images/like.png")
            else:
                path = os.path.join(self.parent.resource_dir, "images/not_like.png")

            pixmap = QtGui.QPixmap(path)

            pos_x = option.rect.x() + option.rect.width() - DIMENSION
            pos_y = option.rect.y() + option.rect.height() - DIMENSION

            painter.drawPixmap(pos_x, pos_y, DIMENSION, DIMENSION, pixmap)

            if waited:
                path = os.path.join(self.parent.resource_dir, "images/unwait.png")
            else:
                path = os.path.join(self.parent.resource_dir, "images/wait.png")

            pixmap = QtGui.QPixmap.fromImage(QtGui.QImage(path))

            pos_x = option.rect.x() + option.rect.width() - 2 * DIMENSION - 5
            pos_y = option.rect.y() + option.rect.height() - DIMENSION

            painter.drawPixmap(pos_x, pos_y, DIMENSION, DIMENSION, pixmap)


        # Thumbnail's index
        elif index.column() == 8:

            painter.fillRect(option.rect, QtGui.QColor(255, 255, 255))

            if type(index.data()) is str and index.data() != "Empty":

                # TODO: check if path exists, else log the problem
                path_photo = os.path.join(self.DATA_PATH,
                                          "graphical_abstracts", index.data())

                if os.path.exists(path_photo):
                    # The photo exists, display it

                    # Load the picture in a QPixmap
                    pixmap = QtGui.QPixmap(path_photo)

                    wcase, hcase = option.rect.width(), option.rect.height()
                    wpix, hpix = pixmap.width(), pixmap.height()

                    # Resize if necessary, and use a smooth transformation
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
                pixmap = QtGui.QPixmap(os.path.join(self.parent.resource_dir, "images/not_available.png"))

                wcase, hcase = option.rect.width(), option.rect.height()
                wpix, hpix = pixmap.width(), pixmap.height()

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
            QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)
