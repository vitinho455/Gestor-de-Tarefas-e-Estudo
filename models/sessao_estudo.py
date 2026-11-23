"""Módulo que define a classe SessaoEstudo."""

from typing import Optional

from .atividade import Atividade
from .disciplina import Disciplina


class SessaoEstudo(Atividade):
    """Representa uma sessão de estudo estruturada em blocos Pomodoro."""

    def __init__(
        self,
        atividade_id: int,
        titulo: str,
        topico: str,
        descricao: str = "",
        prioridade: str = "Média",
        disciplina: Optional[Disciplina] = None,
        pomodoros: int = 2,
        duracao_pomodoro: int = 25,
        incluir_revisao: bool = False,
    ) -> None:
        """Inicializa uma sessão de estudo validando tópico e configuração Pomodoro."""
        super().__init__(
            atividade_id=atividade_id,
            titulo=titulo,
            descricao=descricao,
            prioridade=prioridade,
            disciplina=disciplina,
        )
        self._topico: str = self._validar_texto_nao_vazio(topico, "Tópico da sessão de estudo")
        self._pomodoros: int = self._validar_inteiro_minimo(
            pomodoros,
            "Quantidade de pomodoros",
            minimo=1,
        )
        self._duracao_pomodoro: int = self._validar_inteiro_minimo(
            duracao_pomodoro,
            "Duração do pomodoro",
            minimo=5,
        )
        self._incluir_revisao: bool = bool(incluir_revisao)

    @property
    def topico(self) -> str:
        """Retorna o tópico principal da sessão de estudo."""
        return self._topico

    @property
    def pomodoros(self) -> int:
        """Retorna a quantidade de pomodoros planejados."""
        return self._pomodoros

    @property
    def duracao_pomodoro(self) -> int:
        """Retorna a duração de cada pomodoro em minutos."""
        return self._duracao_pomodoro

    @property
    def incluir_revisao(self) -> bool:
        """Indica se a sessão inclui tempo extra de revisão."""
        return self._incluir_revisao

    def tipo(self) -> str:
        """Retorna o tipo da atividade."""
        return "Sessão de Estudo"

    def calcular_tempo_estimado(self) -> int:
        """Calcula o tempo total com pomodoros, pausas, revisão e subtarefas."""
        return (
            self._pomodoros * self._duracao_pomodoro
            + (self._pomodoros - 1) * 5
            + (15 if self._incluir_revisao else 0)
            + self.tempo_subtarefas()
        )

    def resumo(self) -> str:
        """Retorna um resumo legível da sessão de estudo."""
        status = "[x]" if self.concluida else "[ ]"
        partes = [
            f"[Estudo] {status} {self.titulo}",
            f"Tópico: {self.topico}",
            f"{self.pomodoros} pomodoros",
        ]
        if self.disciplina is not None:
            partes.append(f"Disciplina: {self.disciplina}")
        partes.append(f"{self.calcular_tempo_estimado()} min")
        return " | ".join(partes)
