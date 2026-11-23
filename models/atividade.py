"""Módulo que define a classe abstrata Atividade."""

from abc import ABC, abstractmethod
from typing import Optional

from .disciplina import Disciplina
from .subtarefa import Subtarefa


class Atividade(ABC):
    """Classe base abstrata para atividades acadêmicas e tarefas."""

    PRIORIDADES_VALIDAS: tuple[str, ...] = ("Baixa", "Média", "Alta")

    def __init__(
        self,
        atividade_id: int,
        titulo: str,
        descricao: str = "",
        prioridade: str = "Média",
        disciplina: Optional[Disciplina] = None,
    ) -> None:
        """Inicializa os atributos comuns de uma atividade e sua lista de subtarefas."""
        self._id: int = self._validar_inteiro_minimo(atividade_id, "ID da atividade", minimo=0)
        self._titulo: str = self._validar_texto_nao_vazio(titulo, "Título da atividade")

        if not isinstance(descricao, str):
            raise ValueError("Descrição da atividade deve ser uma string.")
        self._descricao: str = descricao.strip()

        if not isinstance(prioridade, str) or prioridade not in self.PRIORIDADES_VALIDAS:
            validas = ", ".join(self.PRIORIDADES_VALIDAS)
            raise ValueError(f"Prioridade inválida: {prioridade!r}. Valores aceitos: {validas}.")
        self._prioridade: str = prioridade

        self._concluida: bool = False
        self._disciplina: Optional[Disciplina] = None
        self.disciplina = disciplina
        self._subtarefas: list[Subtarefa] = []

    @staticmethod
    def _validar_texto_nao_vazio(valor: str, campo: str) -> str:
        """Valida que o valor é uma string não vazia após strip."""
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError(f"{campo} deve ser uma string não vazia.")
        return valor.strip()

    @staticmethod
    def _validar_inteiro_minimo(valor: int, campo: str, minimo: int = 0) -> int:
        """Valida que o valor é um int (não bool) maior ou igual ao mínimo."""
        if isinstance(valor, bool) or not isinstance(valor, int) or valor < minimo:
            raise ValueError(f"{campo} deve ser um inteiro >= {minimo}.")
        return valor

    @property
    def id(self) -> int:
        """Retorna o identificador único da atividade."""
        return self._id

    @property
    def titulo(self) -> str:
        """Retorna o título da atividade."""
        return self._titulo

    @property
    def descricao(self) -> str:
        """Retorna a descrição da atividade."""
        return self._descricao

    @property
    def prioridade(self) -> str:
        """Retorna a prioridade da atividade."""
        return self._prioridade

    @property
    def concluida(self) -> bool:
        """Indica se a atividade foi concluída."""
        return self._concluida

    @property
    def disciplina(self) -> Optional[Disciplina]:
        """Retorna a disciplina associada à atividade, se houver."""
        return self._disciplina

    @disciplina.setter
    def disciplina(self, valor: Optional[Disciplina]) -> None:
        """Associa uma disciplina à atividade ou remove a associação (None)."""
        if valor is not None and not isinstance(valor, Disciplina):
            raise TypeError("Disciplina deve ser uma instância de Disciplina ou None.")
        self._disciplina = valor

    @property
    def subtarefas(self) -> tuple[Subtarefa, ...]:
        """Retorna uma tupla imutável com as subtarefas da atividade."""
        return tuple(self._subtarefas)

    def adicionar_subtarefa(self, titulo: str, minutos_estimados: int = 15) -> Subtarefa:
        """Instancia e adiciona uma nova subtarefa por composição."""
        subtarefa = Subtarefa(titulo=titulo, minutos_estimados=minutos_estimados)
        self._subtarefas.append(subtarefa)
        return subtarefa

    def remover_subtarefa(self, indice: int) -> None:
        """Remove a subtarefa no índice informado, rejeitando índices negativos ou inválidos."""
        if isinstance(indice, bool) or not isinstance(indice, int):
            raise IndexError("Índice da subtarefa deve ser um inteiro válido.")
        if indice < 0 or indice >= len(self._subtarefas):
            raise IndexError(f"Índice de subtarefa inválido: {indice}.")
        del self._subtarefas[indice]

    def tempo_subtarefas(self) -> int:
        """Retorna a soma dos minutos estimados de todas as subtarefas."""
        return sum(subtarefa.minutos_estimados for subtarefa in self._subtarefas)

    def concluir(self) -> None:
        """Marca a atividade como concluída."""
        self._concluida = True

    def reabrir(self) -> None:
        """Reabre a atividade marcando-a como pendente."""
        self._concluida = False

    def alternar_status(self) -> None:
        """Alterna o status de conclusão da atividade."""
        self._concluida = not self._concluida

    @abstractmethod
    def tipo(self) -> str:
        """Retorna o nome do tipo concreto da atividade."""

    @abstractmethod
    def calcular_tempo_estimado(self) -> int:
        """Calcula o tempo total estimado em minutos."""

    @abstractmethod
    def resumo(self) -> str:
        """Retorna uma string resumida com os dados da atividade."""

    def __str__(self) -> str:
        """Retorna o resumo formatado da atividade."""
        return self.resumo()
