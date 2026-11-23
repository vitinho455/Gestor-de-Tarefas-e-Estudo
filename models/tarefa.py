"""Módulo que define a classe Tarefa."""

from typing import Optional

from .atividade import Atividade
from .disciplina import Disciplina


class Tarefa(Atividade):
    """Representa uma tarefa concreta com prazo e duração base."""

    def __init__(
        self,
        atividade_id: int,
        titulo: str,
        descricao: str = "",
        prioridade: str = "Média",
        disciplina: Optional[Disciplina] = None,
        prazo: str = "",
        minutos_base: int = 30,
    ) -> None:
        """Inicializa uma tarefa validando minutos base e prazo."""
        super().__init__(
            atividade_id=atividade_id,
            titulo=titulo,
            descricao=descricao,
            prioridade=prioridade,
            disciplina=disciplina,
        )
        if not isinstance(prazo, str):
            raise ValueError("Prazo da tarefa deve ser uma string.")
        self._prazo: str = prazo.strip()
        self._minutos_base: int = self._validar_inteiro_minimo(
            minutos_base,
            "Minutos base da tarefa",
            minimo=0,
        )

    @property
    def prazo(self) -> str:
        """Retorna o prazo informado para a tarefa."""
        return self._prazo

    @property
    def minutos_base(self) -> int:
        """Retorna a duração base estimada em minutos."""
        return self._minutos_base

    def tipo(self) -> str:
        """Retorna o tipo da atividade."""
        return "Tarefa"

    def calcular_tempo_estimado(self) -> int:
        """Calcula o tempo total somando minutos base e subtarefas."""
        return self._minutos_base + self.tempo_subtarefas()

    def resumo(self) -> str:
        """Retorna um resumo legível da tarefa."""
        status = "[x]" if self.concluida else "[ ]"
        partes = [f"[Tarefa] {status} {self.titulo}"]
        if self.disciplina is not None:
            partes.append(f"Disciplina: {self.disciplina}")
        if self.prazo:
            partes.append(f"Prazo: {self.prazo}")
        partes.append(f"{self.calcular_tempo_estimado()} min")
        return " | ".join(partes)
