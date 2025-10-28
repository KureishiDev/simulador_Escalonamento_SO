import tkinter as tk
from gui import AppGUI

if __name__ == "__main__":

    root = tk.Tk()  # cria a janela
    app = AppGUI(root)
    app.start()  # inicializa a janela e espera interacao com botoes
