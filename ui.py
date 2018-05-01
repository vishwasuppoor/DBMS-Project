from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QToolTip,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMenuBar,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QMainWindow,
    QStackedLayout,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
    QLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont

def sorted_items(map):

    s = []

    for k, v in map.items():
        s.append((k, v))

    for k, v in sorted(s, key = lambda v: v[0]):
        yield k, v

class WindowSwitcher(QMainWindow):
    def __init__(self, window_map):
        super().__init__()

        self.__map = window_map

        self.__window_stack = []

        container = QWidget()
        layout = QStackedLayout()
        for name, window in window_map.items():
            layout.addWidget(window)

        layout.setSizeConstraint(QLayout.SetFixedSize)
        container.setLayout(layout)

        self.setCentralWidget(container)
        self.show()

    def __switch(self, name):
        for map_name, widget in self.__map.items():
            if name == map_name:
                widget.show()
                widget.move(0, 0)
                self.setFixedSize(widget.size())
                self.setWindowTitle(widget.title())
                widget.opened()
            else:
                widget.hide()
                widget.closed()

    def back(self):
        self.__window_stack.pop()
        self.__switch(self.__window_stack[-1])

    def __call__(self, name):
        self.__window_stack.append(name)
        self.__switch(name)

class Dialog(QWidget):

    def opened(self):
        for c in self.__open_callbacks:
            c()
        self.update_contents()
        self.__clear()
        self.notify("Update message")
        self.__clear()

    def closed(self):
        pass

    def update_contents(self):
        for c in self.__update_callbacks:
            c()

    def notify(self, msg):
        self.__msg.setText(msg)

    def __clear(self):
        self.__msg.setText("")

    def __init__(self, title, buttons = dict(), fields = dict(), labels = dict(), combos = dict(), field_providers=dict()):
        super().__init__()

        self.__open_callbacks = []

        # Set our title.
        self.__title = title

        # Contains buttons.
        button_box = QVBoxLayout()

        # Contains our comboboxes.
        comb = {k: QComboBox() for k in combos.keys()}

        # Contains forms.
        form_box = QGridLayout()
        form_box.setSpacing(2)

        # Setup buttons.
        for name, callback in sorted_items(buttons):
            button = QPushButton(name)
            button_box.addWidget(button)
            button.resize(button.sizeHint())
            button.clicked.connect(callback)

        self.__update_callbacks = []

        # Setup forms.
        row = 1
        for name, callback in sorted_items(fields):
            form_box.addWidget(QLabel(name), row, 0)
            form = QLineEdit()

            if name in field_providers:
                def up(form, update, callback):
                    val = update(None)
                    form.setText(val)
                    callback(val)

                def addCombo(form, update, callback):
                    self.__open_callbacks.append(lambda: up(form, update, callback))

                addCombo(form, field_providers[name], callback)

            else:

                def up_open(form, callback):
                    form.setText("")
                    callback("")

                def addUpOpen(form, callback):
                    self.__open_callbacks.append(lambda: up_open(form, callback))

                addUpOpen(form, callback)

            form.textChanged.connect(callback)
            form_box.addWidget(form, row, 1)
            form.resize(form.sizeHint())

            row += 1

        for name, pair in sorted_items(combos):
            update, callback = pair
            comb[name].currentTextChanged.connect(callback)
            def up_combo(update, name):
                while comb[name].count() != 0:
                    comb[name].removeItem(0)

                for item in update():
                    comb[name].addItem(item)
                comb[name].resize(comb[name].sizeHint())

            def addUpCombo(update, name):
                self.__update_callbacks.append(lambda: up_combo(update, name))

            addUpCombo(update, name)

        for name, box in sorted_items(comb):
            form_box.addWidget(QLabel(name), row, 0)
            form_box.addWidget(box, row, 1)

            row += 1

        # Setup labels.
        for label, value in sorted_items(labels):
            form_box.addWidget(QLabel(label), row, 0)
            def addLabel(value):
                label = QLabel("N/A")
                form_box.addWidget(label, row, 1)
                label.resize(label.sizeHint())
                self.__update_callbacks.append(lambda: label.setText(str(value())))
            addLabel(value)

            row += 1

        # Setup window layout.
        layout = QVBoxLayout()
        layout.addLayout(form_box)
        layout.addLayout(button_box)
        self.__msg = QLabel(" ")
        layout.addWidget(self.__msg)
        self.setLayout(layout)
        self.show()

    def title(self):
        return self.__title

class TableWidget(QTableWidget):

    def update_contents(self):
        self.__entries = self.__update()
        self.__update_display()

    def __update_display(self):
        to_show = []

        for entry in self.__entries:
            if self.__search_value in entry[self.__search_index]:
                to_show.append(entry)

        self.setSortingEnabled(False)

        row = 0
        self.setRowCount(0)
        for entry in to_show:
            self.setRowCount(row + 1)

            column = 0
            for col in entry:
                self.setItem(row, column, QTableWidgetItem(str(col)))

                column += 1

            row += 1

        self.resize(self.sizeHint())
        self.setSortingEnabled(True)

    def search_by(self, column_index, value):
        self.__search_index = column_index
        self.__search_value = value
        self.__update_display()

    def opened(self):
        self.update_contents()

    def closed(self):
        pass

    def __header(self, index):
        if not self.__headers[index][1]:
            self.setSortingEnabled(False)
            return

        self.setSortingEnabled(True)

    def __init__(self, headers, update):
        super().__init__()

        self.__entries = []
        self.__search_index = 0
        self.__search_value = ""

        self.headers = [name for name, _ in headers]
        self.__headers = headers

        self.__update = update
        self.setColumnCount(len(headers))
        self.setRowCount(0)
        self.setHorizontalHeaderLabels(
            (header for header, sortable in headers)
        )

        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        for name, sortable in headers:
            if not sortable:
                continue

            header = self.horizontalHeader()

            self.horizontalHeader().sectionClicked.connect(self.__header)

class TableDialog(QDialog):

    def update_contents(self):
        for c in self.__update_callbacks:
            c()

        self.__table.update_contents()

    def opened(self):
        for c in self.__open_callbacks:
            c()
        self.update_contents()
        self.__table.update_contents()
        self.__table.resize(self.__table.sizeHint())
        self.__clear()
        self.notify("Update message")
        self.__clear()

    def closed(self):
        pass

    def notify(self, msg):
        self.__msg.setText(msg)

    def __clear(self):
        self.__msg.setText("")

    def row(self):
        rows = self.__table.selectionModel().selectedRows()
        if len(rows) == 0:
            return None
        row = rows[0].row()

        return [
            self.__table.item(row, i).text()
            for i in range(0, len(self.__headers))
        ]

    def headers(self):
        return self.__headers

    def __init__(self,
                 title = None,
                 table = None,
                 populate = None,
                 searchable = True,
                 combos = dict(),
                 fields = dict(),
                 buttons = None):

        super().__init__()

        self.__open_callbacks = []

        self.__update_callbacks = []

        # Contains our comboboxes.
        comb = {k: QComboBox() for k in combos.keys()}

        self.__headers = [
            header
            for header, _
            in table
        ]

        # Set our title.
        self.__title = title

        self.__table = TableWidget(
            table,
            populate
        )

        self.__table.resize(self.__table.sizeHint())

        # Contains buttons.
        button_box = QHBoxLayout()

        # Add buttons.
        for label, callback in sorted_items(buttons):
            button = QPushButton(label)
            button_box.addWidget(button)
            button.resize(button.sizeHint())
            button.clicked.connect(callback)

        self.__update_callbacks = []

        # Setup forms.
        for name, callback in sorted_items(fields):
            form = QLineEdit()

            def up_open(form, callback):
                form.setText("")
                callback("")

            def addUpOpen(form, callback):
                self.__open_callbacks.append(lambda: up_open(form, callback))

            addUpOpen(form, callback)

            form.textChanged.connect(callback)
            button_box.addWidget(form)
            form.resize(form.sizeHint())

        for name, pair in sorted_items(combos):
            update, callback = pair
            comb[name].currentTextChanged.connect(callback)
            def up_combo(update, name):
                while comb[name].count() != 0:
                    comb[name].removeItem(0)

                for item in update():
                    comb[name].addItem(item)
                comb[name].resize(comb[name].sizeHint())

            def addUpCombo(update, name):
                self.__update_callbacks.append(lambda: up_combo(update, name))

            addUpCombo(update, name)

        for name, box in sorted_items(comb):
            button_box.addWidget(box)

        # Add search button if needed.
        if searchable:
            search_field = self.__headers[0]
            search_by = QComboBox()
            search_text = ""
            search_for = QLineEdit()

            def update_search_field(text):
                nonlocal search_field
                search_field = text

            def update_search_text(text):
                nonlocal search_text
                search_text = text

            for field in self.__headers:
                search_by.addItem(field)

            search_for.textChanged.connect(update_search_text)

            search_by.currentTextChanged.connect(update_search_field)
            search = QPushButton("Search")
            button_box.addWidget(search)
            button_box.addWidget(search_for)
            button_box.addWidget(search_by)
            search.clicked.connect(
                lambda:
                self.__table.search_by(
                    self.__headers.index(
                        search_field),
                    search_text
                )
            )
            search.resize(search.sizeHint())

        # Update our table to initially show everything.
        self.__table.search_by(0, "")

        # Setup layout.
        layout = QVBoxLayout()
        layout.addWidget(self.__table)
        layout.addLayout(button_box)
        self.__msg = QLabel(" ")
        layout.addWidget(self.__msg)
        self.setLayout(layout)
        self.show()

    def title(self):
        return self.__title
