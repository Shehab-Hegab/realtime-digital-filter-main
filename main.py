import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QShortcut
from PyQt5.QtGui import QKeySequence

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import pandas as pd
import numpy as np






# -------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------





class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        try:
            super(MyWindow, self).__init__()
            uic.loadUi('Realtime Digital Filter.ui', self)
            self.showFullScreen()
            self.shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
            self.shortcut.activated.connect(self.browseFile)
            # Initialize the Matplotlib canvas
            self.mpl_canvas = MplCanvas(self, width=5, height=4, dpi=100)
            # Find the widget and add the mpl_canvas to its layout
            unit_circle_widget = self.findChild(QtWidgets.QWidget, 'unit_circle_representation')
            if unit_circle_widget is not None:
                layout = unit_circle_widget.layout()
                if layout is not None:
                    layout.addWidget(self.mpl_canvas)
                else:
                    print("Error: 'unit_circle_representation' does not have a layout.")
            else:
                print("Error: Widget 'unit_circle_representation' not found.")
            # Draw the initial unit circle
            self.draw_unit_circle()
            # Connect the click event
            self.mpl_canvas.mpl_connect('button_press_event', self.on_click)
        except Exception as e:
            print(f"Error in UI initialization: {e}")

        # Correctly connect radio button signals & doubles to their respective methods
        self.radioButtonZero.toggled.connect(self.on_zero_radio_button_toggled)
        self.radioButtonPole.toggled.connect(self.on_pole_radio_button_toggled)
        self.radioButtonDoubleZero.toggled.connect(self.on_double_zero_radio_button_toggled)
        self.radioButtonDoublePole.toggled.connect(self.on_double_pole_radio_button_toggled)
        self.current_mode = None

        # Removing zeros and poles
        self.remove_all_zeros.clicked.connect(self.clear_zeros)
        self.remove_all_poles.clicked.connect(self.clear_poles)
        self.remove_all_zeros_poles.clicked.connect(self.clear_all)

        # Adding Conjugates
        self.conjugateCheckBox.stateChanged.connect(self.toggle_conjugates)
        self.add_conjugates = False






    def keyPressEvent(self, event):
        try:
            if event.key() == Qt.Key_Escape:
                if self.isFullScreen():
                    self.showNormal()
                else:
                    self.showFullScreen()
        except Exception as e:
            print(f"Error during key press event: {e}")






    def browseFile(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(self, "Select CSV File", filter="CSV Files (*.csv)")
            if file_name:
                self.plotCsv(file_name)
        except Exception as e:
            # Handle the error and possibly display a message to the user
            print(f"Error in browsing file: {e}")






    def plotCsv(self, file_path):
        try:
            # Read the CSV file
            data = pd.read_csv(file_path)
            # Clear the previous data
            self.input_signal.clear()
            # Plot the data
            self.input_signal.plot(data.iloc[:, 0], data.iloc[:, 1])  # Modify according to your CSV structure
        except pd.errors.EmptyDataError:
            print("The CSV file is empty.")
        except pd.errors.ParserError:
            print("Error parsing CSV file.")
        except Exception as e:
            print(f"Unexpected error reading file: {e}")





    def draw_unit_circle(self):
        # Clear previous plot
        self.mpl_canvas.axes.cla()

        # Draw unit circle
        theta = np.linspace(0, 2*np.pi, 100)
        self.mpl_canvas.axes.plot(theta, np.ones_like(theta), linestyle='--', color='gray')

        # Redraw the canvas
        self.mpl_canvas.draw()





    def on_click(self, event):
        if event.button == 1:  # Left click
            if event.xdata is not None and event.ydata is not None:
                if self.current_mode == 'Zero':
                    self.add_zero(event.xdata, event.ydata)
                elif self.current_mode == 'Pole':
                    self.add_pole(event.xdata, event.ydata)
                elif self.current_mode == 'DoubleZero':
                    self.add_double_zero(event.xdata, event.ydata)
                elif self.current_mode == 'DoublePole':
                    self.add_double_pole(event.xdata, event.ydata)
        elif event.button == 3:  # Right click
            self.remove_point(event.xdata, event.ydata)

        self.mpl_canvas.draw()





    def remove_point(self, x, y):
        threshold = 0.05  # Define a smaller threshold for precise clicking

        def distance(point):
            return ((point[0] - x) ** 2 + (point[1] - y) ** 2) ** 0.5

        closest_zero_distance = float('inf')
        closest_zero = None
        for zero in self.mpl_canvas.zeros:
            dist = distance(zero)
            if dist < closest_zero_distance:
                closest_zero_distance = dist
                closest_zero = zero

        closest_pole_distance = float('inf')
        closest_pole = None
        for pole in self.mpl_canvas.poles:
            dist = distance(pole)
            if dist < closest_pole_distance:
                closest_pole_distance = dist
                closest_pole = pole

        removed = False
        if closest_zero_distance < threshold:
            self.mpl_canvas.zeros.remove(closest_zero)
            removed = True
        elif closest_pole_distance < threshold:
            self.mpl_canvas.poles.remove(closest_pole)
            removed = True

        if removed:
            self.mpl_canvas.plot_points()  # Redraw the canvas with updated points





    # Adding Zeros & Poles Strategies
    # -------------------------------
    def add_zero(self, x, y):
        self.mpl_canvas.add_zero((x, y))  # Add the first zero
        if self.add_conjugates:
            self.mpl_canvas.add_zero((x, -y))  # Add the conjugate zero

    def add_pole(self, x, y):
        self.mpl_canvas.add_pole((x, y))  # Add the first pole
        if self.add_conjugates:
            self.mpl_canvas.add_pole((x, -y))  # Add the conjugate pole


    def add_double_zero(self, x, y):
        self.mpl_canvas.add_zero((x, y))
        self.mpl_canvas.add_zero((x, -y))  # Add a second zero at the same position

    def add_double_pole(self, x, y):
        self.mpl_canvas.add_pole((x, y))
        self.mpl_canvas.add_pole((x, -y))  # Add a second pole at the same position

    def on_zero_radio_button_toggled(self, checked):
        if checked:
            self.current_mode = 'Zero'

    def on_pole_radio_button_toggled(self, checked):
        if checked:
            self.current_mode = 'Pole'

    def on_double_zero_radio_button_toggled(self, checked):
        if checked:
            self.current_mode = 'DoubleZero'

    def on_double_pole_radio_button_toggled(self, checked):
        if checked:
            self.current_mode = 'DoublePole'





    # Removing Zeros & Poles Strategies
    # ---------------------------------
    def clear_zeros(self):
        self.mpl_canvas.zeros.clear()  # Clear the list of zeros
        self.mpl_canvas.plot_points()  # Re-draw the canvas without zeros

    def clear_poles(self):
        self.mpl_canvas.poles.clear()  # Clear the list of poles
        self.mpl_canvas.plot_points()  # Re-draw the canvas without poles

    def clear_all(self):
        self.mpl_canvas.zeros.clear()  # Clear the list of zeros
        self.mpl_canvas.poles.clear()  # Clear the list of poles
        self.mpl_canvas.plot_points()  # Re-draw the canvas without zeros and poles




    # Adding Conjugate Option
    # -----------------------
    def toggle_conjugates(self, state):
        self.add_conjugates = (state == Qt.Checked)






# -------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------








# ***************************************** Unit Circle Representation *****************************************
# --------------------------------------------------------------------------------------------------------------
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111, projection='polar')
        super(MplCanvas, self).__init__(self.fig)

        self.zeros = []  # List to store zeros
        self.poles = []  # List to store poles





    def add_zero(self, zero):
        self.zeros.append(zero)
        self.plot_points()



    def add_pole(self, pole):
        self.poles.append(pole)
        self.plot_points()



    def plot_points(self):
        self.axes.clear()
        # Plot zeros and poles
        for zero in self.zeros:
            self.axes.plot(zero[0], zero[1], 'o', color='blue')  # Blue for zeros
        for pole in self.poles:
            self.axes.plot(pole[0], pole[1], 'x', color='red')  # Red for poles
        self.draw()






# -------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------






def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.showFullScreen()
    sys.exit(app.exec_())




if __name__ == '__main__':
    main()