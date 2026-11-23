"""Ponto de entrada do Gestor de Tarefas e Estudos — POO."""

import tkinter as tk

from services import GestorAtividades
from ui import GestorApp


def main() -> None:
    """Inicializa o gestor, carrega dados iniciais e inicia o loop da GUI."""
    gestor = GestorAtividades()
    gestor.carregar_dados_exemplo()

    root = tk.Tk()
    GestorApp(root, gestor)
    root.mainloop()


if __name__ == "__main__":
    main()
