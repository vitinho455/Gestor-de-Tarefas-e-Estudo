"""Testes unitários e de integração do Gestor de Tarefas e Estudos (POO)."""

from __future__ import annotations

from pathlib import Path
import tempfile
import tkinter as tk
from tkinter import ttk
import unittest

from models import Atividade, Disciplina, SessaoEstudo, Subtarefa, Tarefa
from services import ExportadorRelatorio, GestorAtividades
from ui import GestorApp


def _encontrar_widgets(widget: tk.Misc, tipo: type[tk.Misc]) -> list[tk.Misc]:
    """Percorre recursivamente os descendentes de um widget Tkinter."""
    encontrados: list[tk.Misc] = []
    for filho in widget.winfo_children():
        if isinstance(filho, tipo):
            encontrados.append(filho)
        encontrados.extend(_encontrar_widgets(filho, tipo))
    return encontrados


class TestHerancaEPolimorfismo(unittest.TestCase):
    """Valida classe abstrata, herança e comportamento polimórfico."""

    def test_atividade_abstrata_nao_pode_ser_instanciada(self) -> None:
        with self.assertRaises(TypeError):
            Atividade(1, "Atividade genérica")  # type: ignore[abstract]

    def test_heranca_subclasses_de_atividade(self) -> None:
        disciplina = Disciplina("POO101", "Programação Orientada a Objetos")
        tarefa = Tarefa(
            atividade_id=1,
            titulo="Implementar modelos",
            descricao="Criar classes do domínio",
            prioridade="Alta",
            disciplina=disciplina,
            prazo="2026-12-10",
            minutos_base=40,
        )
        sessao = SessaoEstudo(
            atividade_id=2,
            titulo="Estudar abstração",
            topico="Classes abstratas e interfaces",
            prioridade="Média",
            disciplina=disciplina,
            pomodoros=2,
            duracao_pomodoro=25,
            incluir_revisao=True,
        )

        self.assertTrue(issubclass(Tarefa, Atividade))
        self.assertTrue(issubclass(SessaoEstudo, Atividade))
        self.assertIsInstance(tarefa, Atividade)
        self.assertIsInstance(sessao, Atividade)
        self.assertEqual(Atividade.PRIORIDADES_VALIDAS, ("Baixa", "Média", "Alta"))
        self.assertEqual(tarefa.id, 1)
        self.assertEqual(tarefa.prazo, "2026-12-10")
        self.assertEqual(tarefa.minutos_base, 40)
        self.assertEqual(sessao.topico, "Classes abstratas e interfaces")
        self.assertEqual(sessao.pomodoros, 2)
        self.assertEqual(sessao.duracao_pomodoro, 25)
        self.assertTrue(sessao.incluir_revisao)

    def test_polimorfismo_em_lista_mista(self) -> None:
        disciplina = Disciplina("BD201", "Banco de Dados")
        tarefa = Tarefa(
            atividade_id=1,
            titulo="Lista de SQL",
            prioridade="Média",
            disciplina=disciplina,
            prazo="2026-12-05",
            minutos_base=30,
        )
        tarefa.adicionar_subtarefa("Resolver consultas JOIN", 20)

        sessao = SessaoEstudo(
            atividade_id=2,
            titulo="Revisão Normalização",
            topico="1FN, 2FN e 3FN",
            prioridade="Alta",
            disciplina=disciplina,
            pomodoros=3,
            duracao_pomodoro=25,
            incluir_revisao=True,
        )
        sessao.adicionar_subtarefa("Mapear exemplos", 10)

        atividades: list[Atividade] = [tarefa, sessao]

        tipos = [a.tipo() for a in atividades]
        tempos = [a.calcular_tempo_estimado() for a in atividades]
        resumos = [a.resumo() for a in atividades]

        self.assertEqual(tipos, ["Tarefa", "Sessão de Estudo"])
        # Tarefa: 30 + 20 = 50
        # SessaoEstudo: 3*25 + (3-1)*5 + 15 (revisão) + 10 (subtarefa) = 75 + 10 + 15 + 10 = 110
        self.assertEqual(tempos, [50, 110])

        self.assertIn("[Tarefa]", resumos[0])
        self.assertIn("[ ]", resumos[0])
        self.assertIn("Lista de SQL", resumos[0])
        self.assertIn("BD201", resumos[0])
        self.assertIn("2026-12-05", resumos[0])
        self.assertIn("50 min", resumos[0])

        self.assertIn("[Estudo]", resumos[1])
        self.assertIn("[ ]", resumos[1])
        self.assertIn("Revisão Normalização", resumos[1])
        self.assertIn("1FN, 2FN e 3FN", resumos[1])
        self.assertIn("3 pomodoros", resumos[1])
        self.assertIn("BD201", resumos[1])
        self.assertIn("110 min", resumos[1])

        tarefa.concluir()
        self.assertIn("[x]", tarefa.resumo())
        self.assertEqual(str(tarefa), tarefa.resumo())

        tarefa.reabrir()
        self.assertIn("[ ]", tarefa.resumo())
        tarefa.alternar_status()
        self.assertTrue(tarefa.concluida)
        tarefa.alternar_status()
        self.assertFalse(tarefa.concluida)


class TestComposicaoSubtarefas(unittest.TestCase):
    """Valida composição forte entre Atividade e Subtarefa."""

    def test_ciclo_de_vida_subtarefas_e_tempo(self) -> None:
        tarefa = Tarefa(1, "Projeto Final", minutos_base=45)
        sub1 = tarefa.adicionar_subtarefa("Planejar arquitetura", 15)
        sub2 = tarefa.adicionar_subtarefa("Escrever testes", 25)

        self.assertIsInstance(sub1, Subtarefa)
        self.assertIsInstance(tarefa.subtarefas, tuple)
        self.assertEqual(len(tarefa.subtarefas), 2)
        self.assertEqual(tarefa.tempo_subtarefas(), 40)
        self.assertEqual(tarefa.calcular_tempo_estimado(), 85)

        self.assertFalse(sub1.concluida)
        self.assertEqual(str(sub1), "[ ] Planejar arquitetura (15 min)")
        sub1.alternar_status()
        self.assertTrue(sub1.concluida)
        self.assertEqual(str(sub1), "[x] Planejar arquitetura (15 min)")
        sub1.reabrir()
        self.assertFalse(sub1.concluida)
        sub1.concluir()
        self.assertTrue(sub1.concluida)

        tarefa.remover_subtarefa(0)
        self.assertEqual(tarefa.subtarefas, (sub2,))
        self.assertEqual(tarefa.tempo_subtarefas(), 25)
        self.assertEqual(tarefa.calcular_tempo_estimado(), 70)

    def test_remover_subtarefa_indice_invalido_ou_negativo_lanca_index_error(self) -> None:
        sessao = SessaoEstudo(1, "Estudo Dirigido", "Grafos")
        sessao.adicionar_subtarefa("Ler capítulo 1", 20)

        with self.assertRaises(IndexError):
            sessao.remover_subtarefa(-1)
        with self.assertRaises(IndexError):
            sessao.remover_subtarefa(1)
        with self.assertRaises(IndexError):
            sessao.remover_subtarefa(99)
        with self.assertRaises(IndexError):
            sessao.remover_subtarefa(True)  # type: ignore[arg-type]

        self.assertEqual(len(sessao.subtarefas), 1)

    def test_remover_atividade_elimina_subtarefas_compostas_do_gestor(self) -> None:
        gestor = GestorAtividades()
        tarefa = gestor.adicionar_tarefa("Trabalho POO", minutos_base=30)
        tarefa.adicionar_subtarefa("Subtarefa A", 15)
        tarefa.adicionar_subtarefa("Subtarefa B", 25)

        self.assertEqual(gestor.calcular_tempo_total(), 70)
        self.assertTrue(gestor.remover_atividade(tarefa.id))
        self.assertFalse(gestor.remover_atividade(tarefa.id))
        self.assertIsNone(gestor.buscar_atividade(tarefa.id))
        self.assertEqual(gestor.listar_atividades(), [])
        self.assertEqual(gestor.calcular_tempo_total(), 0)


class TestAssociacaoDisciplina(unittest.TestCase):
    """Valida associação independente entre Atividade e Disciplina."""

    def test_disciplina_normalizacao_igualdade_e_hash(self) -> None:
        d1 = Disciplina(" poo101 ", "  Programação Orientada a Objetos  ")
        d2 = Disciplina("POO101", "Outro Nome")

        self.assertEqual(d1.codigo, "POO101")
        self.assertEqual(d1.nome, "Programação Orientada a Objetos")
        self.assertEqual(str(d1), "POO101 - Programação Orientada a Objetos")
        self.assertEqual(d1, d2)
        self.assertEqual(hash(d1), hash(d2))

    def test_remover_atividade_preserva_disciplina_no_gestor(self) -> None:
        gestor = GestorAtividades()
        disc = gestor.cadastrar_disciplina("POO101", "Programação Orientada a Objetos")
        tarefa = gestor.adicionar_tarefa("Diagrama UML", disciplina=disc)

        self.assertTrue(gestor.remover_atividade(tarefa.id))
        self.assertIsNone(gestor.buscar_atividade(tarefa.id))
        self.assertEqual(gestor.buscar_disciplina("POO101"), disc)
        self.assertEqual(gestor.listar_disciplinas(), [disc])

    def test_remover_disciplina_desassocia_atividades_sem_apagar(self) -> None:
        gestor = GestorAtividades()
        disc = gestor.cadastrar_disciplina("EST301", "Estrutura de Dados")
        tarefa = gestor.adicionar_tarefa("Árvores AVL", disciplina=disc)
        sessao = gestor.adicionar_sessao_estudo("Revisão Hash", "Tabelas Hash", disciplina=disc)

        self.assertTrue(gestor.remover_disciplina("est301"))
        self.assertFalse(gestor.remover_disciplina("est301"))
        self.assertIsNone(gestor.buscar_disciplina("EST301"))

        atividades = gestor.listar_atividades()
        self.assertEqual(len(atividades), 2)
        self.assertIsNone(tarefa.disciplina)
        self.assertIsNone(sessao.disciplina)

        # Associação também pode ser alterada pelo setter de disciplina
        nova_disc = gestor.cadastrar_disciplina("ALG102", "Algoritmos")
        tarefa.disciplina = nova_disc
        self.assertEqual(tarefa.disciplina, nova_disc)
        with self.assertRaises(TypeError):
            tarefa.disciplina = "ALG102"  # type: ignore[assignment]
        tarefa.disciplina = None
        self.assertIsNone(tarefa.disciplina)


class TestDependenciaExportadorRelatorio(unittest.TestCase):
    """Valida relação de dependência entre GestorAtividades e ExportadorRelatorio."""

    def test_gerar_e_exportar_relatorio_sem_armazenar_exportador(self) -> None:
        gestor = GestorAtividades()
        gestor.carregar_dados_exemplo()
        exportador = ExportadorRelatorio()

        self.assertFalse(
            any(isinstance(valor, ExportadorRelatorio) for valor in gestor.__dict__.values())
        )

        relatorio = gestor.gerar_relatorio(exportador)
        self.assertIsInstance(relatorio, str)
        self.assertTrue(len(relatorio.strip()) > 0)
        for atividade in gestor.listar_atividades():
            self.assertIn(atividade.titulo, relatorio)

        with tempfile.TemporaryDirectory() as tmp_dir:
            caminho_destino = Path(tmp_dir) / "relatorios" / "saida.txt"
            caminho_retornado = gestor.exportar_relatorio_txt(exportador, str(caminho_destino))
            arquivo = Path(caminho_retornado)
            self.assertTrue(arquivo.exists())
            conteudo = arquivo.read_text(encoding="utf-8")
            self.assertEqual(conteudo, relatorio)

        # Dependência transitória: GestorAtividades não armazena ExportadorRelatorio em __dict__
        self.assertFalse(
            any(isinstance(valor, ExportadorRelatorio) for valor in gestor.__dict__.values())
        )
        # ExportadorRelatorio não armazena estado de atividades ou gestor
        self.assertFalse(
            any(
                isinstance(valor, (GestorAtividades, Atividade))
                for valor in exportador.__dict__.values()
            )
        )

    def test_relatorio_lista_vazia(self) -> None:
        exportador = ExportadorRelatorio()
        texto = exportador.gerar_relatorio([])
        self.assertIsInstance(texto, str)
        self.assertTrue(len(texto.strip()) > 0)


class TestFiltrosValidacoesEExemplo(unittest.TestCase):
    """Valida filtros de listagem, validações de entrada e dados de exemplo."""

    def test_filtros_e_tempo_total(self) -> None:
        gestor = GestorAtividades()
        poo = gestor.cadastrar_disciplina("POO101", "POO")
        bd = gestor.cadastrar_disciplina("BD201", "Banco de Dados")

        t1 = gestor.adicionar_tarefa("Exercício 1", disciplina=poo, minutos_base=30)
        t2 = gestor.adicionar_tarefa("Exercício 2", disciplina=bd, minutos_base=40)
        s1 = gestor.adicionar_sessao_estudo(
            "Estudo POO",
            "Herança",
            disciplina=poo,
            pomodoros=2,
            duracao_pomodoro=25,
            incluir_revisao=False,
        )  # 55 min

        self.assertTrue(gestor.alternar_conclusao(t1.id))
        self.assertFalse(gestor.alternar_conclusao(9999))
        self.assertTrue(t1.concluida)

        self.assertEqual(gestor.calcular_tempo_total(apenas_pendentes=False), 125)
        self.assertEqual(gestor.calcular_tempo_total(apenas_pendentes=True), 95)

        self.assertEqual(gestor.listar_atividades(apenas_pendentes=True), [t2, s1])
        self.assertEqual(gestor.listar_atividades(codigo_disciplina="POO101"), [t1, s1])
        self.assertEqual(gestor.listar_atividades(codigo_disciplina=" poo101 "), [t1, s1])
        self.assertEqual(gestor.listar_atividades(tipo="Tarefa"), [t1, t2])
        self.assertEqual(gestor.listar_atividades(tipo="Sessão de Estudo"), [s1])
        self.assertEqual(
            gestor.listar_atividades(
                apenas_pendentes=True,
                codigo_disciplina="POO101",
                tipo="Sessão de Estudo",
            ),
            [s1],
        )
        self.assertEqual(gestor.buscar_disciplina(" poo101 "), poo)
        self.assertIsNone(gestor.buscar_disciplina("INEXISTENTE"))
        self.assertEqual(gestor.buscar_atividade(t1.id), t1)
        self.assertIsNone(gestor.buscar_atividade(9999))

    def test_validacoes_value_error(self) -> None:
        gestor = GestorAtividades()
        gestor.cadastrar_disciplina("POO101", "Programação OO")

        with self.assertRaises(ValueError):
            Disciplina("   ", "Nome válido")
        with self.assertRaises(ValueError):
            Disciplina("COD1", "   ")
        with self.assertRaises(ValueError):
            gestor.cadastrar_disciplina(" poo101 ", "Duplicada")

        with self.assertRaises(ValueError):
            Subtarefa("   ")
        with self.assertRaises(ValueError):
            Subtarefa("Subtarefa", -1)
        with self.assertRaises(ValueError):
            Subtarefa("Subtarefa", True)  # type: ignore[arg-type]

        with self.assertRaises(ValueError):
            Tarefa(1, "   ")
        with self.assertRaises(ValueError):
            Tarefa(1, "Título válido", prioridade="Urgente")
        with self.assertRaises(ValueError):
            Tarefa(1, "Título válido", minutos_base=-10)
        with self.assertRaises(ValueError):
            Tarefa(1, "Título válido", minutos_base=False)  # type: ignore[arg-type]

        with self.assertRaises(ValueError):
            SessaoEstudo(2, "Estudo", "   ")
        with self.assertRaises(ValueError):
            SessaoEstudo(2, "Estudo", "Tópico", pomodoros=0)
        with self.assertRaises(ValueError):
            SessaoEstudo(2, "Estudo", "Tópico", pomodoros=True)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            SessaoEstudo(2, "Estudo", "Tópico", duracao_pomodoro=4)
        with self.assertRaises(ValueError):
            SessaoEstudo(2, "Estudo", "Tópico", duracao_pomodoro=True)  # type: ignore[arg-type]

    def test_carregar_dados_exemplo_e_idempotencia(self) -> None:
        gestor = GestorAtividades()
        gestor.carregar_dados_exemplo()

        disciplinas = gestor.listar_disciplinas()
        atividades = gestor.listar_atividades()
        self.assertEqual(len(disciplinas), 3)
        self.assertEqual(len(atividades), 3)
        self.assertTrue(any(isinstance(a, Tarefa) for a in atividades))
        self.assertTrue(any(isinstance(a, SessaoEstudo) for a in atividades))
        self.assertTrue(any(len(a.subtarefas) > 0 for a in atividades))

        # Não duplica caso já existam registros
        gestor.carregar_dados_exemplo()
        self.assertEqual(len(gestor.listar_disciplinas()), 3)
        self.assertEqual(len(gestor.listar_atividades()), 3)


class TestSmokeGUI(unittest.TestCase):
    """Smoke test da interface desktop Tkinter."""

    def test_gestor_app_inicializacao_e_atualizacao(self) -> None:
        try:
            root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest(f"Display Tkinter indisponível neste ambiente: {exc}")

        try:
            root.withdraw()
            gestor = GestorAtividades()
            gestor.carregar_dados_exemplo()

            app = GestorApp(root, gestor)
            root.update_idletasks()

            self.assertIn("Gestor", root.title())
            self.assertEqual(app.var_total.get(), "3")
            self.assertEqual(app.var_pendentes.get(), "3")
            arvores = _encontrar_widgets(root, ttk.Treeview)
            self.assertEqual(len(arvores), 1)
            tree = arvores[0]
            assert isinstance(tree, ttk.Treeview)
            self.assertEqual(len(tree.get_children()), 3)

            gestor.adicionar_tarefa("Nova atividade de teste", minutos_base=20)
            app.atualizar_lista()
            root.update_idletasks()
            self.assertEqual(len(tree.get_children()), 4)
            self.assertEqual(app.var_total.get(), "4")
            self.assertEqual(app.var_pendentes.get(), "4")

            app.var_filtro_tipo.set("Sessão de Estudo")
            app.atualizar_lista()
            root.update_idletasks()
            self.assertEqual(len(tree.get_children()), 1)

            app.var_filtro_tipo.set("Todos")
            app.atualizar_lista()
            root.update_idletasks()
            self.assertEqual(len(tree.get_children()), 4)
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
