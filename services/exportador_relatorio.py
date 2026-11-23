"""Módulo responsável pela exportação textual de relatórios de atividades."""

from pathlib import Path

from models import Atividade


class ExportadorRelatorio:
    """Serviço sem estado para geração e salvamento de relatórios em texto.

    Mantém apenas relação de Dependência com ``Atividade`` e
    ``GestorAtividades``, sem armazenar instâncias em atributos.
    """

    def gerar_relatorio(self, atividades: list[Atividade]) -> str:
        """Monta um relatório textual em português usando polimorfismo."""
        total = len(atividades)
        concluidas = sum(1 for atividade in atividades if atividade.concluida)
        pendentes = total - concluidas
        tempo_total = sum(
            atividade.calcular_tempo_estimado() for atividade in atividades
        )

        linhas: list[str] = [
            "=" * 70,
            "RELATÓRIO DE ATIVIDADES E ESTUDOS",
            "=" * 70,
            "Resumo Quantitativo:",
            f"  Total de atividades: {total}",
            f"  Concluídas: {concluidas}",
            f"  Pendentes: {pendentes}",
            f"  Tempo total estimado: {tempo_total} min",
            "-" * 70,
        ]

        if not atividades:
            linhas.append("Nenhuma atividade encontrada para exibir no relatório.")
            linhas.append("=" * 70)
            return "\n".join(linhas)

        linhas.append("Detalhamento das Atividades:")
        for indice, atividade in enumerate(atividades, start=1):
            status = "Concluída" if atividade.concluida else "Pendente"
            disciplina_texto = (
                f"{atividade.disciplina.codigo} - {atividade.disciplina.nome}"
                if atividade.disciplina is not None
                else "Sem disciplina"
            )
            tempo_atividade = atividade.calcular_tempo_estimado()

            linhas.append("")
            linhas.append(f"{indice}. {atividade.resumo()}")
            linhas.append(
                f"   ID: {atividade.id} | Tipo: {atividade.tipo()} | "
                f"Status: {status} | Prioridade: {atividade.prioridade} | "
                f"Disciplina: {disciplina_texto} | Tempo estimado: {tempo_atividade} min"
            )
            if atividade.descricao:
                linhas.append(f"   Descrição: {atividade.descricao}")

            subtarefas = atividade.subtarefas
            if subtarefas:
                linhas.append(f"   Subtarefas ({len(subtarefas)}):")
                for subtarefa in subtarefas:
                    marcador = "x" if subtarefa.concluida else " "
                    linhas.append(
                        f"     - [{marcador}] {subtarefa.titulo} "
                        f"({subtarefa.minutos_estimados} min)"
                    )
            else:
                linhas.append("   Subtarefas: Nenhuma")

        linhas.append("")
        linhas.append("=" * 70)
        return "\n".join(linhas)

    def salvar_txt(self, atividades: list[Atividade], caminho: str) -> str:
        """Gera o relatório, garante o diretório pai e salva em UTF-8."""
        if isinstance(caminho, Path):
            caminho_texto = str(caminho).strip()
        elif isinstance(caminho, str):
            caminho_texto = caminho.strip()
        else:
            raise ValueError("O caminho do arquivo deve ser uma string válida.")

        if not caminho_texto:
            raise ValueError("O caminho do arquivo não pode ser vazio.")

        path = Path(caminho_texto)
        path.parent.mkdir(parents=True, exist_ok=True)
        conteudo = self.gerar_relatorio(atividades)
        path.write_text(conteudo, encoding="utf-8")
        return str(path)
