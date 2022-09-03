from PyQt5.QtGui import QColor

# Цвета
BLACK = QColor("black")
WHITE = QColor("white")
RED = QColor("red")
GREEN = QColor("green")
GRAY = QColor(192, 192, 192)
DARK_GRAY = QColor(128, 128, 128)
# Фразы для сообщений
CANNOT_ADD = "You cannot add a new row until you input data in last one"
NO_GRAPHS_WITH_NAME = "There are no graphs with this name"
NOT_SELECTED = "You have not selected the graph"
ARE_YOU_SURE = "Are you sure you want to delete"
ALREADY_EXISTS = "Element with this name is already exists"
NOT_NUMBER = "The value in the weight cell must be a number"
NOT_DIF_NODES = "You cannot add an edge between two identical nodes"
NOT_DIF_EDGES = "You cannot add identical ribs in graph"
EMPTY = "Value cannot be empty"
NOT_OPEN = "You have not chosen the graph to open"
ENTER_NODE = "Enter name for node:"
ENTER_GRAPH = "Enter name for graph:"
NOT_CHOSEN_TYPE = "You have not chosen input data type"
NOT_CHOSEN_DEL = "You have not chosen delimiter"
NOT_CHOSEN_FILE = "You have not chosen file to open"
ALERT_CSV = "Attention! If you add data from the table and any graph is opened, all previous data will be deleted. If the data has errors, the corresponding one will not be added. Do you want to accept the changes?"
# Некоторые коды
CHDIR = 'chdir'  # флаг для изменения направления ребра
NWGHT = 'nwght'  # флаг для изменения веса ребра
NTET = 'not_edit_value'  # флаг, делающий элемент недоступным для учета в изменениях
# Для рисования
MAX_CANVAS_SIZE = 25
DEFAULT_DIST = 20
ZOOM_STEP = 1.5
MIN_ZOOM = 0.5
MAX_ZOOM = ZOOM_STEP ** 6
