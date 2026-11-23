"""Módulo que define a classe de domínio Disciplina."""


def _validar_texto_nao_vazio(valor: str, campo: str) -> str:
    """Valida que um campo textual é uma string não vazia após strip."""
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{campo} deve ser uma string não vazia.")
    return valor.strip()


class Disciplina:
    """Representa uma disciplina acadêmica associada a atividades."""

    def __init__(self, codigo: str, nome: str) -> None:
        """Inicializa uma disciplina com código normalizado em maiúsculas e nome."""
        self._codigo: str = _validar_texto_nao_vazio(codigo, "Código da disciplina").upper()
        self._nome: str = _validar_texto_nao_vazio(nome, "Nome da disciplina")

    @property
    def codigo(self) -> str:
        """Retorna o código identificador da disciplina."""
        return self._codigo

    @property
    def nome(self) -> str:
        """Retorna o nome da disciplina."""
        return self._nome

    def __str__(self) -> str:
        """Retorna a representação legível da disciplina."""
        return f"{self.codigo} - {self.nome}"

    def __repr__(self) -> str:
        """Retorna a representação técnica da disciplina."""
        return f"Disciplina(codigo={self.codigo!r}, nome={self.nome!r})"

    def __eq__(self, other: object) -> bool:
        """Compara duas disciplinas pelo código."""
        if not isinstance(other, Disciplina):
            return NotImplemented
        return self.codigo == other.codigo

    def __hash__(self) -> int:
        """Retorna o hash baseado no código da disciplina."""
        return hash(self.codigo)
