"""Módulo de serviços para gerenciamento de disciplinas e atividades."""

from typing import Optional

from models import Atividade, Disciplina, SessaoEstudo, Tarefa

from .exportador_relatorio import ExportadorRelatorio


class GestorAtividades:
    """Gerencia disciplinas, atividades polimórficas e geração de relatórios."""

    def __init__(self) -> None:
        self._disciplinas: list[Disciplina] = []
        self._atividades: list[Atividade] = []
        self._proximo_id: int = 1

    def cadastrar_disciplina(self, codigo: str, nome: str) -> Disciplina:
        """Cadastra uma disciplina após validar campos e evitar duplicidade."""
        disciplina = Disciplina(codigo=codigo, nome=nome)
        if self.buscar_disciplina(disciplina.codigo) is not None:
            raise ValueError(
                f"Já existe uma disciplina cadastrada com o código '{disciplina.codigo}'."
            )
        self._disciplinas.append(disciplina)
        return disciplina

    def listar_disciplinas(self) -> list[Disciplina]:
        """Retorna uma cópia da lista de disciplinas cadastradas."""
        return list(self._disciplinas)

    def buscar_disciplina(self, codigo: str) -> Optional[Disciplina]:
        """Busca uma disciplina pelo código normalizado com strip().upper()."""
        if not isinstance(codigo, str):
            return None
        codigo_normalizado = codigo.strip().upper()
        if not codigo_normalizado:
            return None
        for disciplina in self._disciplinas:
            if disciplina.codigo == codigo_normalizado:
                return disciplina
        return None

    def remover_disciplina(self, codigo: str) -> bool:
        """Remove a disciplina e desassocia suas atividades sem removê-las."""
        disciplina = self.buscar_disciplina(codigo)
        if disciplina is None:
            return False

        for atividade in self._atividades:
            if (
                atividade.disciplina is not None
                and atividade.disciplina.codigo == disciplina.codigo
            ):
                atividade.disciplina = None

        self._disciplinas.remove(disciplina)
        return True

    def adicionar_tarefa(
        self,
        titulo: str,
        descricao: str = "",
        prioridade: str = "Média",
        disciplina: Optional[Disciplina] = None,
        prazo: str = "",
        minutos_base: int = 30,
    ) -> Tarefa:
        """Instancia e registra uma nova Tarefa com ID sequencial."""
        tarefa = Tarefa(
            atividade_id=self._proximo_id,
            titulo=titulo,
            descricao=descricao,
            prioridade=prioridade,
            disciplina=disciplina,
            prazo=prazo,
            minutos_base=minutos_base,
        )
        self._atividades.append(tarefa)
        self._proximo_id += 1
        return tarefa

    def adicionar_sessao_estudo(
        self,
        titulo: str,
        topico: str,
        descricao: str = "",
        prioridade: str = "Média",
        disciplina: Optional[Disciplina] = None,
        pomodoros: int = 2,
        duracao_pomodoro: int = 25,
        incluir_revisao: bool = False,
    ) -> SessaoEstudo:
        """Instancia e registra uma nova SessaoEstudo com ID sequencial."""
        sessao = SessaoEstudo(
            atividade_id=self._proximo_id,
            titulo=titulo,
            topico=topico,
            descricao=descricao,
            prioridade=prioridade,
            disciplina=disciplina,
            pomodoros=pomodoros,
            duracao_pomodoro=duracao_pomodoro,
            incluir_revisao=incluir_revisao,
        )
        self._atividades.append(sessao)
        self._proximo_id += 1
        return sessao

    def listar_atividades(
        self,
        apenas_pendentes: bool = False,
        codigo_disciplina: Optional[str] = None,
        tipo: Optional[str] = None,
    ) -> list[Atividade]:
        """Retorna atividades filtradas por pendência, disciplina e tipo."""
        codigo_normalizado = (
            codigo_disciplina.strip().upper()
            if isinstance(codigo_disciplina, str) and codigo_disciplina.strip()
            else None
        )
        tipo_normalizado = (
            tipo.strip().casefold()
            if isinstance(tipo, str) and tipo.strip()
            else None
        )

        filtradas: list[Atividade] = []
        for atividade in self._atividades:
            if apenas_pendentes and atividade.concluida:
                continue
            if codigo_normalizado is not None:
                if (
                    atividade.disciplina is None
                    or atividade.disciplina.codigo != codigo_normalizado
                ):
                    continue
            if tipo_normalizado is not None:
                if atividade.tipo().strip().casefold() != tipo_normalizado:
                    continue
            filtradas.append(atividade)
        return filtradas

    def buscar_atividade(self, atividade_id: int) -> Optional[Atividade]:
        """Localiza uma atividade pelo ID; retorna None se não existir."""
        if isinstance(atividade_id, bool) or not isinstance(atividade_id, int):
            return None
        for atividade in self._atividades:
            if atividade.id == atividade_id:
                return atividade
        return None

    def remover_atividade(self, atividade_id: int) -> bool:
        """Remove a atividade pelo ID e descarta sua composição de subtarefas."""
        atividade = self.buscar_atividade(atividade_id)
        if atividade is None:
            return False
        self._atividades.remove(atividade)
        return True

    def alternar_conclusao(self, atividade_id: int) -> bool:
        """Alterna o status de conclusão da atividade informada pelo ID."""
        atividade = self.buscar_atividade(atividade_id)
        if atividade is None:
            return False
        atividade.alternar_status()
        return True

    def calcular_tempo_total(self, apenas_pendentes: bool = False) -> int:
        """Calcula a soma de minutos estimados das atividades filtradas."""
        atividades = self.listar_atividades(apenas_pendentes=apenas_pendentes)
        return sum(atividade.calcular_tempo_estimado() for atividade in atividades)

    def gerar_relatorio(self, exportador: ExportadorRelatorio) -> str:
        """Gera relatório delegando para um ExportadorRelatorio externo."""
        if exportador is None or not hasattr(exportador, "gerar_relatorio"):
            raise TypeError("É necessário fornecer um ExportadorRelatorio válido.")
        return exportador.gerar_relatorio(self.listar_atividades())

    def exportar_relatorio_txt(
        self, exportador: ExportadorRelatorio, caminho: str
    ) -> str:
        """Salva o relatório em arquivo texto via ExportadorRelatorio."""
        if exportador is None or not hasattr(exportador, "salvar_txt"):
            raise TypeError("É necessário fornecer um ExportadorRelatorio válido.")
        return exportador.salvar_txt(self.listar_atividades(), caminho)

    def carregar_dados_exemplo(self) -> None:
        """Popula 3 disciplinas e 3 atividades iniciais se o gestor estiver vazio."""
        if self._disciplinas or self._atividades:
            return

        poo = self.cadastrar_disciplina("POO101", "Programação Orientada a Objetos")
        bd = self.cadastrar_disciplina("BD201", "Banco de Dados")
        est = self.cadastrar_disciplina("EST301", "Estatística Aplicada")

        tarefa_poo = self.adicionar_tarefa(
            titulo="Trabalho Prático de POO",
            descricao="Aplicar herança, polimorfismo, composição, associação e dependência.",
            prioridade="Alta",
            disciplina=poo,
            prazo="2026-11-30",
            minutos_base=45,
        )
        sub_uml = tarefa_poo.adicionar_subtarefa("Elaborar diagrama UML", 20)
        sub_uml.concluir()
        tarefa_poo.adicionar_subtarefa("Implementar testes unitários", 25)

        sessao_bd = self.adicionar_sessao_estudo(
            titulo="Revisão de Normalização e SQL",
            topico="1FN, 2FN, 3FN e JOINs",
            descricao="Sessão Pomodoro focada para a avaliação da unidade.",
            prioridade="Alta",
            disciplina=bd,
            pomodoros=3,
            duracao_pomodoro=25,
            incluir_revisao=True,
        )
        sessao_bd.adicionar_subtarefa("Resolver exercícios de JOIN", 30)
        sessao_bd.adicionar_subtarefa("Revisar anotações de aula", 15)

        tarefa_est = self.adicionar_tarefa(
            titulo="Lista de Probabilidade Condicional",
            descricao="Resolver os exercícios ímpares do capítulo 4.",
            prioridade="Média",
            disciplina=est,
            prazo="2026-12-05",
            minutos_base=30,
        )
        tarefa_est.adicionar_subtarefa("Revisar teorema de Bayes", 15)
        tarefa_est.adicionar_subtarefa("Conferir gabarito final", 10)
