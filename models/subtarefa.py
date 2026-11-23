"""Módulo que define a classe de domínio Subtarefa."""


class Subtarefa:
    """Representa uma etapa componente pertencente a uma atividade."""

    def __init__(
        self,
        titulo: str,
        minutos_estimados: int = 15,
        concluida: bool = False,
    ) -> None:
        """Inicializa uma subtarefa validando título e duração estimada."""
        if not isinstance(titulo, str) or not titulo.strip():
            raise ValueError("Título da subtarefa deve ser uma string não vazia.")
        if (
            isinstance(minutos_estimados, bool)
            or not isinstance(minutos_estimados, int)
            or minutos_estimados < 0
        ):
            raise ValueError("Minutos estimados da subtarefa deve ser um inteiro >= 0.")

        self._titulo: str = titulo.strip()
        self._minutos_estimados: int = minutos_estimados
        self._concluida: bool = bool(concluida)

    @property
    def titulo(self) -> str:
        """Retorna o título da subtarefa."""
        return self._titulo

    @property
    def minutos_estimados(self) -> int:
        """Retorna o tempo estimado em minutos."""
        return self._minutos_estimados

    @property
    def concluida(self) -> bool:
        """Indica se a subtarefa foi concluída."""
        return self._concluida

    def concluir(self) -> None:
        """Marca a subtarefa como concluída."""
        self._concluida = True

    def reabrir(self) -> None:
        """Reabre a subtarefa marcando-a como pendente."""
        self._concluida = False

    def alternar_status(self) -> None:
        """Alterna o status de conclusão da subtarefa."""
        self._concluida = not self._concluida

    def __str__(self) -> str:
        """Retorna a representação legível da subtarefa."""
        return f"[{'x' if self.concluida else ' '}] {self.titulo} ({self.minutos_estimados} min)"

    def __repr__(self) -> str:
        """Retorna a representação técnica da subtarefa."""
        return (
            f"Subtarefa(titulo={self.titulo!r}, "
            f"minutos_estimados={self.minutos_estimados}, concluida={self.concluida})"
        )
