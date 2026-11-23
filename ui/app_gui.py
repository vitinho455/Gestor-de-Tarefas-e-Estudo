"""Interface gráfica desktop (Tkinter/ttk) do Gestor de Tarefas e Estudos."""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Optional

from models import Atividade, Disciplina
from services import ExportadorRelatorio, GestorAtividades


class GestorApp:
    """Aplicação desktop Tkinter para gerenciar atividades acadêmicas e estudos."""

    def __init__(self, root: tk.Tk, gestor: GestorAtividades) -> None:
        """Inicializa a janela principal, estado reativo e componentes da UI."""
        self.root = root
        self.gestor = gestor

        self.root.title("Gestor de Tarefas e Estudos — POO")
        self.root.minsize(920, 560)
        self.root.geometry("980x620")

        self.var_total = tk.StringVar(value="0")
        self.var_concluidas = tk.StringVar(value="0")
        self.var_pendentes = tk.StringVar(value="0")
        self.var_tempo_total = tk.StringVar(value="0")

        self.var_filtro_disciplina = tk.StringVar(value="Todas")
        self.var_filtro_tipo = tk.StringVar(value="Todos")
        self.var_apenas_pendentes = tk.BooleanVar(value=False)
        self.var_detalhes = tk.StringVar(
            value="Selecione uma atividade na tabela para visualizar os detalhes."
        )

        self._mapa_disciplinas_filtro: dict[str, Optional[str]] = {"Todas": None}

        self._configurar_estilo()
        self._construir_interface()
        self.atualizar_lista()

    def _configurar_estilo(self) -> None:
        """Configura tema e estilos visuais padronizados com ttk."""
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        self.root.configure(bg="#F4F6F9")
        style.configure("App.TFrame", background="#F4F6F9")
        style.configure("Title.TLabel", background="#F4F6F9", foreground="#1E293B", font=("Segoe UI", 15, "bold"))
        style.configure("Subtitle.TLabel", background="#F4F6F9", foreground="#475569", font=("Segoe UI", 9))
        style.configure("Card.TFrame", background="#FFFFFF", relief="solid", borderwidth=1)
        style.configure("CardTitle.TLabel", background="#FFFFFF", foreground="#64748B", font=("Segoe UI", 9))
        style.configure("CardValue.TLabel", background="#FFFFFF", foreground="#0F172A", font=("Segoe UI", 16, "bold"))
        style.configure("Treeview", rowheight=26, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
        style.configure("Hint.TLabel", foreground="#475569", font=("Segoe UI", 9))

    def _construir_interface(self) -> None:
        """Monta cabeçalho de métricas, filtros, tabela, detalhes e ações."""
        container = ttk.Frame(self.root, style="App.TFrame", padding=14)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(2, weight=1)

        self._construir_cabecalho(container)
        self._construir_filtros(container)
        self._construir_tabela(container)
        self._construir_barra_detalhes(container)
        self._construir_botoes(container)

    def _construir_cabecalho(self, parent: ttk.Frame) -> None:
        """Cria título da aplicação e cartões dinâmicos de métricas."""
        header = ttk.Frame(parent, style="App.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text="Gestor de Tarefas e Estudos",
            style="Title.TLabel",
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="Organização acadêmica com Herança, Polimorfismo, Composição, Associação e Dependência",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 10))

        cards_frame = ttk.Frame(header, style="App.TFrame")
        cards_frame.grid(row=2, column=0, sticky="ew")

        metricas = [
            ("Total", self.var_total),
            ("Concluídas", self.var_concluidas),
            ("Pendentes", self.var_pendentes),
            ("Tempo Total (min)", self.var_tempo_total),
        ]
        for idx, (titulo, var) in enumerate(metricas):
            cards_frame.columnconfigure(idx, weight=1)
            card = ttk.Frame(cards_frame, style="Card.TFrame", padding=(12, 8))
            pad_right = 0 if idx == len(metricas) - 1 else 8
            card.grid(row=0, column=idx, sticky="ew", padx=(0, pad_right))
            ttk.Label(card, text=titulo, style="CardTitle.TLabel").pack(anchor="w")
            ttk.Label(card, textvariable=var, style="CardValue.TLabel").pack(anchor="w", pady=(2, 0))

    def _construir_filtros(self, parent: ttk.Frame) -> None:
        """Cria a barra de filtros por disciplina, tipo e pendência."""
        frame = ttk.LabelFrame(parent, text="Filtros", padding=(10, 8))
        frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(frame, text="Disciplina:").grid(row=0, column=0, padx=(0, 6))
        self.combo_disciplina = ttk.Combobox(
            frame,
            textvariable=self.var_filtro_disciplina,
            state="readonly",
            width=32,
        )
        self.combo_disciplina.grid(row=0, column=1, padx=(0, 14))
        self.combo_disciplina.bind("<<ComboboxSelected>>", lambda _e: self.atualizar_lista())

        ttk.Label(frame, text="Tipo:").grid(row=0, column=2, padx=(0, 6))
        self.combo_tipo = ttk.Combobox(
            frame,
            textvariable=self.var_filtro_tipo,
            values=("Todos", "Tarefa", "Sessão de Estudo"),
            state="readonly",
            width=18,
        )
        self.combo_tipo.grid(row=0, column=3, padx=(0, 14))
        self.combo_tipo.bind("<<ComboboxSelected>>", lambda _e: self.atualizar_lista())

        self.check_pendentes = ttk.Checkbutton(
            frame,
            text="Apenas pendentes",
            variable=self.var_apenas_pendentes,
            command=self.atualizar_lista,
        )
        self.check_pendentes.grid(row=0, column=4, padx=(0, 14))

        ttk.Button(
            frame,
            text="Limpar filtros",
            command=self._limpar_filtros,
        ).grid(row=0, column=5)

    def _construir_tabela(self, parent: ttk.Frame) -> None:
        """Cria a tabela Treeview para exibição polimórfica das atividades."""
        frame = ttk.Frame(parent, style="App.TFrame")
        frame.grid(row=2, column=0, sticky="nsew", pady=(0, 8))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        colunas = ("id", "tipo", "titulo", "disciplina", "prioridade", "tempo", "status")
        self.tree = ttk.Treeview(
            frame,
            columns=colunas,
            show="headings",
            selectmode="browse",
        )

        config_colunas = [
            ("id", "ID", 55, "center", False),
            ("tipo", "Tipo", 130, "center", False),
            ("titulo", "Título", 260, "w", True),
            ("disciplina", "Disciplina", 190, "w", True),
            ("prioridade", "Prioridade", 90, "center", False),
            ("tempo", "Tempo (min)", 95, "e", False),
            ("status", "Status", 100, "center", False),
        ]
        for col_id, cabecalho, largura, alinhamento, esticar in config_colunas:
            self.tree.heading(col_id, text=cabecalho)
            self.tree.column(col_id, width=largura, anchor=alinhamento, stretch=esticar)

        self.tree.tag_configure("concluida", foreground="#64748B")
        self.tree.bind("<<TreeviewSelect>>", lambda _e: self._atualizar_detalhes())
        self.tree.bind("<Double-1>", self._ao_duplo_clique_tabela)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _construir_barra_detalhes(self, parent: ttk.Frame) -> None:
        """Exibe resumo e detalhes da atividade selecionada na tabela."""
        frame = ttk.LabelFrame(parent, text="Detalhes da Atividade Selecionada", padding=(10, 6))
        frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        frame.columnconfigure(0, weight=1)

        ttk.Label(
            frame,
            textvariable=self.var_detalhes,
            wraplength=880,
            justify="left",
        ).grid(row=0, column=0, sticky="w")

    def _construir_botoes(self, parent: ttk.Frame) -> None:
        """Cria a barra inferior com todos os botões de ação."""
        frame = ttk.Frame(parent, style="App.TFrame")
        frame.grid(row=4, column=0, sticky="ew")

        acoes = [
            ("+ Nova Tarefa", self._abrir_modal_nova_tarefa),
            ("+ Nova Sessão de Estudo", self._abrir_modal_nova_sessao),
            ("Subtarefas", self._abrir_modal_subtarefas),
            ("Concluir / Reabrir", self._alternar_conclusao_selecionada),
            ("Remover", self._remover_atividade_selecionada),
            ("Disciplinas", self._abrir_modal_disciplinas),
            ("Relatório", self._abrir_modal_relatorio),
        ]
        for idx, (texto, comando) in enumerate(acoes):
            pad_right = 0 if idx == len(acoes) - 1 else 6
            btn = ttk.Button(frame, text=texto, command=comando)
            btn.pack(side="left", padx=(0, pad_right))

    def _limpar_filtros(self) -> None:
        """Restaura todos os filtros para o estado inicial e atualiza a lista."""
        self.var_filtro_disciplina.set("Todas")
        self.var_filtro_tipo.set("Todos")
        self.var_apenas_pendentes.set(False)
        self.atualizar_lista()

    def _atualizar_opcoes_disciplina_filtro(self) -> None:
        """Atualiza o Combobox de filtro de disciplinas mantendo seleção válida."""
        disciplinas = self.gestor.listar_disciplinas()
        self._mapa_disciplinas_filtro = {"Todas": None}
        opcoes = ["Todas"]
        for disc in disciplinas:
            rotulo = str(disc)
            self._mapa_disciplinas_filtro[rotulo] = disc.codigo
            opcoes.append(rotulo)

        self.combo_disciplina["values"] = opcoes
        atual = self.var_filtro_disciplina.get()
        if atual not in self._mapa_disciplinas_filtro:
            self.var_filtro_disciplina.set("Todas")

    def _obter_codigo_disciplina_filtro(self) -> Optional[str]:
        """Resolve o código da disciplina selecionada no filtro."""
        selecionado = self.var_filtro_disciplina.get().strip()
        if not selecionado or selecionado == "Todas":
            return None
        if selecionado in self._mapa_disciplinas_filtro:
            return self._mapa_disciplinas_filtro[selecionado]
        return selecionado.split(" - ", 1)[0].strip().upper()

    def atualizar_lista(self) -> None:
        """Atualiza tabela de atividades, filtro de disciplinas e métricas."""
        self._atualizar_opcoes_disciplina_filtro()

        selecao_anterior = self.tree.selection()
        iid_anterior = selecao_anterior[0] if selecao_anterior else None

        codigo_disciplina = self._obter_codigo_disciplina_filtro()
        tipo_selecionado = self.var_filtro_tipo.get().strip()
        tipo = None if not tipo_selecionado or tipo_selecionado == "Todos" else tipo_selecionado
        apenas_pendentes = bool(self.var_apenas_pendentes.get())

        atividades = self.gestor.listar_atividades(
            apenas_pendentes=apenas_pendentes,
            codigo_disciplina=codigo_disciplina,
            tipo=tipo,
        )

        self.tree.delete(*self.tree.get_children())
        for atividade in atividades:
            disciplina_txt = str(atividade.disciplina) if atividade.disciplina else "Sem disciplina"
            status_txt = "Concluída" if atividade.concluida else "Pendente"
            tags = ("concluida",) if atividade.concluida else ("pendente",)
            self.tree.insert(
                "",
                tk.END,
                iid=str(atividade.id),
                values=(
                    atividade.id,
                    atividade.tipo(),
                    atividade.titulo,
                    disciplina_txt,
                    atividade.prioridade,
                    atividade.calcular_tempo_estimado(),
                    status_txt,
                ),
                tags=tags,
            )

        if iid_anterior and self.tree.exists(iid_anterior):
            self.tree.selection_set(iid_anterior)

        todas = self.gestor.listar_atividades()
        total = len(todas)
        concluidas = sum(1 for item in todas if item.concluida)
        pendentes = total - concluidas
        tempo_total = self.gestor.calcular_tempo_total(apenas_pendentes=False)

        self.var_total.set(str(total))
        self.var_concluidas.set(str(concluidas))
        self.var_pendentes.set(str(pendentes))
        self.var_tempo_total.set(str(tempo_total))

        self._atualizar_detalhes()

    def _obter_atividade_selecionada(self, avisar: bool = True) -> Optional[Atividade]:
        """Retorna a atividade selecionada na Treeview ou None."""
        selecao = self.tree.selection()
        if not selecao:
            if avisar:
                messagebox.showwarning(
                    "Nenhuma Seleção",
                    "Selecione uma atividade na tabela primeiro.",
                    parent=self.root,
                )
            return None
        try:
            atividade_id = int(selecao[0])
        except ValueError:
            return None
        return self.gestor.buscar_atividade(atividade_id)

    def _atualizar_detalhes(self) -> None:
        """Atualiza o painel inferior com informações da atividade selecionada."""
        atividade = self._obter_atividade_selecionada(avisar=False)
        if atividade is None:
            self.var_detalhes.set(
                "Selecione uma atividade na tabela para visualizar os detalhes."
            )
            return

        total_subs = len(atividade.subtarefas)
        concluidas_subs = sum(1 for sub in atividade.subtarefas if sub.concluida)
        descricao = atividade.descricao.strip() if atividade.descricao else "Sem descrição"
        self.var_detalhes.set(
            f"{atividade.resumo()}\n"
            f"Descrição: {descricao} | Subtarefas: {concluidas_subs}/{total_subs} concluídas"
        )

    def _ao_duplo_clique_tabela(self, event: tk.Event) -> None:
        """Abre gerenciamento de subtarefas ao dar duplo clique em uma linha."""
        if self.tree.identify_row(event.y):
            self._abrir_modal_subtarefas()

    def _criar_modal(
        self,
        titulo: str,
        largura: int,
        altura: int,
        redimensionavel: bool = False,
    ) -> tk.Toplevel:
        """Cria janela modal padronizada vinculada à janela principal."""
        modal = tk.Toplevel(self.root)
        modal.title(titulo)
        modal.transient(self.root)
        modal.grab_set()
        modal.resizable(redimensionavel, redimensionavel)
        modal.bind("<Escape>", lambda _e: modal.destroy())

        if self.root.winfo_width() > 100 and self.root.winfo_height() > 100:
            pos_x = self.root.winfo_x() + (self.root.winfo_width() - largura) // 2
            pos_y = self.root.winfo_y() + (self.root.winfo_height() - altura) // 2
            modal.geometry(f"{largura}x{altura}+{max(pos_x, 0)}+{max(pos_y, 0)}")
        else:
            modal.geometry(f"{largura}x{altura}")
        return modal

    @staticmethod
    def _converter_inteiro(texto: str, nome_campo: str) -> int:
        """Converte texto de entrada em inteiro ou lança ValueError legível."""
        try:
            return int(texto.strip())
        except ValueError as exc:
            raise ValueError(
                f"O campo '{nome_campo}' deve conter um número inteiro válido."
            ) from exc

    def _criar_campos_atividade_comuns(
        self,
        frame: ttk.Frame,
    ) -> tuple[dict[str, tk.StringVar], dict[str, Optional[Disciplina]], ttk.Entry]:
        """Cria os campos compartilhados por Tarefa e Sessão de Estudo."""
        disciplinas = self.gestor.listar_disciplinas()
        mapa_disciplinas: dict[str, Optional[Disciplina]] = {"Nenhuma": None}
        opcoes_disciplina = ["Nenhuma"]
        for disc in disciplinas:
            rotulo = str(disc)
            mapa_disciplinas[rotulo] = disc
            opcoes_disciplina.append(rotulo)

        vars_comuns = {
            "titulo": tk.StringVar(),
            "descricao": tk.StringVar(),
            "prioridade": tk.StringVar(value="Média"),
            "disciplina": tk.StringVar(value="Nenhuma"),
        }

        ttk.Label(frame, text="Título *:").grid(row=0, column=0, sticky="w", pady=4)
        entry_titulo = ttk.Entry(frame, textvariable=vars_comuns["titulo"], width=40)
        entry_titulo.grid(row=0, column=1, sticky="ew", pady=4)

        ttk.Label(frame, text="Descrição:").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=vars_comuns["descricao"], width=40).grid(
            row=1, column=1, sticky="ew", pady=4
        )

        ttk.Label(frame, text="Prioridade:").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Combobox(
            frame,
            textvariable=vars_comuns["prioridade"],
            values=Atividade.PRIORIDADES_VALIDAS,
            state="readonly",
            width=37,
        ).grid(row=2, column=1, sticky="ew", pady=4)

        ttk.Label(frame, text="Disciplina:").grid(row=3, column=0, sticky="w", pady=4)
        ttk.Combobox(
            frame,
            textvariable=vars_comuns["disciplina"],
            values=opcoes_disciplina,
            state="readonly",
            width=37,
        ).grid(row=3, column=1, sticky="ew", pady=4)

        return vars_comuns, mapa_disciplinas, entry_titulo

    def _abrir_modal_nova_tarefa(self) -> None:
        """Abre modal para criação de uma nova Tarefa."""
        modal = self._criar_modal("Nova Tarefa", 460, 310)
        frame = ttk.Frame(modal, padding=16)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(1, weight=1)

        vars_comuns, mapa_disciplinas, entry_titulo = self._criar_campos_atividade_comuns(frame)
        var_prazo = tk.StringVar()
        var_minutos = tk.StringVar(value="30")

        ttk.Label(frame, text="Prazo (opcional):").grid(row=4, column=0, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=var_prazo, width=40).grid(
            row=4, column=1, sticky="ew", pady=4
        )

        ttk.Label(frame, text="Minutos base *:").grid(row=5, column=0, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=var_minutos, width=40).grid(
            row=5, column=1, sticky="ew", pady=4
        )

        def salvar() -> None:
            try:
                minutos_base = self._converter_inteiro(var_minutos.get(), "Minutos base")
                disciplina = mapa_disciplinas.get(vars_comuns["disciplina"].get())
                self.gestor.adicionar_tarefa(
                    titulo=vars_comuns["titulo"].get(),
                    descricao=vars_comuns["descricao"].get(),
                    prioridade=vars_comuns["prioridade"].get(),
                    disciplina=disciplina,
                    prazo=var_prazo.get(),
                    minutos_base=minutos_base,
                )
            except ValueError as exc:
                messagebox.showerror("Erro ao Criar Tarefa", str(exc), parent=modal)
                return

            modal.destroy()
            self.atualizar_lista()

        botoes = ttk.Frame(frame)
        botoes.grid(row=6, column=0, columnspan=2, sticky="e", pady=(14, 0))
        ttk.Button(botoes, text="Cancelar", command=modal.destroy).pack(side="right", padx=(6, 0))
        ttk.Button(botoes, text="Salvar Tarefa", command=salvar).pack(side="right")

        entry_titulo.focus_set()

    def _abrir_modal_nova_sessao(self) -> None:
        """Abre modal para criação de uma nova Sessão de Estudo."""
        modal = self._criar_modal("Nova Sessão de Estudo", 480, 390)
        frame = ttk.Frame(modal, padding=16)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(1, weight=1)

        vars_comuns, mapa_disciplinas, entry_titulo = self._criar_campos_atividade_comuns(frame)
        var_topico = tk.StringVar()
        var_pomodoros = tk.StringVar(value="2")
        var_duracao = tk.StringVar(value="25")
        var_revisao = tk.BooleanVar(value=False)

        ttk.Label(frame, text="Tópico *:").grid(row=4, column=0, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=var_topico, width=40).grid(
            row=4, column=1, sticky="ew", pady=4
        )

        ttk.Label(frame, text="Pomodoros *:").grid(row=5, column=0, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=var_pomodoros, width=40).grid(
            row=5, column=1, sticky="ew", pady=4
        )

        ttk.Label(frame, text="Duração Pomodoro (min) *:").grid(
            row=6, column=0, sticky="w", pady=4
        )
        ttk.Entry(frame, textvariable=var_duracao, width=40).grid(
            row=6, column=1, sticky="ew", pady=4
        )

        ttk.Checkbutton(
            frame,
            text="Incluir revisão final (+15 min)",
            variable=var_revisao,
        ).grid(row=7, column=1, sticky="w", pady=6)

        def salvar() -> None:
            try:
                pomodoros = self._converter_inteiro(var_pomodoros.get(), "Pomodoros")
                duracao = self._converter_inteiro(var_duracao.get(), "Duração Pomodoro")
                disciplina = mapa_disciplinas.get(vars_comuns["disciplina"].get())
                self.gestor.adicionar_sessao_estudo(
                    titulo=vars_comuns["titulo"].get(),
                    topico=var_topico.get(),
                    descricao=vars_comuns["descricao"].get(),
                    prioridade=vars_comuns["prioridade"].get(),
                    disciplina=disciplina,
                    pomodoros=pomodoros,
                    duracao_pomodoro=duracao,
                    incluir_revisao=bool(var_revisao.get()),
                )
            except ValueError as exc:
                messagebox.showerror(
                    "Erro ao Criar Sessão de Estudo", str(exc), parent=modal
                )
                return

            modal.destroy()
            self.atualizar_lista()

        botoes = ttk.Frame(frame)
        botoes.grid(row=8, column=0, columnspan=2, sticky="e", pady=(14, 0))
        ttk.Button(botoes, text="Cancelar", command=modal.destroy).pack(side="right", padx=(6, 0))
        ttk.Button(botoes, text="Salvar Sessão", command=salvar).pack(side="right")

        entry_titulo.focus_set()

    def _abrir_modal_subtarefas(self) -> None:
        """Abre modal para gerenciar subtarefas da atividade selecionada (Composição)."""
        atividade = self._obter_atividade_selecionada(avisar=True)
        if atividade is None:
            return

        modal = self._criar_modal(f"Subtarefas — {atividade.titulo}", 620, 440, redimensionavel=True)
        frame = ttk.Frame(modal, padding=14)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        ttk.Label(
            frame,
            text=f"{atividade.tipo()}: {atividade.titulo}",
            font=("Segoe UI", 11, "bold"),
        ).grid(row=0, column=0, sticky="w")

        var_resumo_tempo = tk.StringVar()
        ttk.Label(
            frame,
            textvariable=var_resumo_tempo,
            style="Hint.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 8))

        lista_frame = ttk.Frame(frame)
        lista_frame.grid(row=2, column=0, sticky="nsew")
        lista_frame.columnconfigure(0, weight=1)
        lista_frame.rowconfigure(0, weight=1)

        tree_sub = ttk.Treeview(
            lista_frame,
            columns=("indice", "status", "titulo", "minutos"),
            show="headings",
            selectmode="browse",
        )
        tree_sub.heading("indice", text="#")
        tree_sub.heading("status", text="Status")
        tree_sub.heading("titulo", text="Título")
        tree_sub.heading("minutos", text="Tempo (min)")
        tree_sub.column("indice", width=40, anchor="center", stretch=False)
        tree_sub.column("status", width=100, anchor="center", stretch=False)
        tree_sub.column("titulo", width=320, anchor="w", stretch=True)
        tree_sub.column("minutos", width=95, anchor="e", stretch=False)

        scroll = ttk.Scrollbar(lista_frame, orient="vertical", command=tree_sub.yview)
        tree_sub.configure(yscrollcommand=scroll.set)
        tree_sub.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

        def atualizar_subtarefas(selecionar_iid: Optional[str] = None) -> None:
            tree_sub.delete(*tree_sub.get_children())
            for idx, sub in enumerate(atividade.subtarefas):
                status = "Concluída" if sub.concluida else "Pendente"
                tree_sub.insert(
                    "",
                    tk.END,
                    iid=str(idx),
                    values=(idx + 1, status, sub.titulo, sub.minutos_estimados),
                )
            if selecionar_iid and tree_sub.exists(selecionar_iid):
                tree_sub.selection_set(selecionar_iid)
            var_resumo_tempo.set(
                "Composição: subtarefas pertencem à atividade e somam ao tempo estimado "
                f"(Total atual: {atividade.calcular_tempo_estimado()} min)."
            )
            self.atualizar_lista()

        form = ttk.LabelFrame(frame, text="Adicionar Subtarefa", padding=(10, 8))
        form.grid(row=3, column=0, sticky="ew", pady=(10, 8))
        form.columnconfigure(1, weight=1)

        var_sub_titulo = tk.StringVar()
        var_sub_minutos = tk.StringVar(value="15")

        ttk.Label(form, text="Título *:").grid(row=0, column=0, sticky="w", padx=(0, 6))
        entry_sub = ttk.Entry(form, textvariable=var_sub_titulo)
        entry_sub.grid(row=0, column=1, sticky="ew", padx=(0, 10))

        ttk.Label(form, text="Minutos:").grid(row=0, column=2, sticky="w", padx=(0, 6))
        ttk.Entry(form, textvariable=var_sub_minutos, width=8).grid(
            row=0, column=3, sticky="w", padx=(0, 10)
        )

        def adicionar_sub() -> None:
            try:
                minutos = self._converter_inteiro(var_sub_minutos.get(), "Minutos")
                atividade.adicionar_subtarefa(var_sub_titulo.get(), minutos)
            except ValueError as exc:
                messagebox.showerror("Erro ao Adicionar Subtarefa", str(exc), parent=modal)
                return

            var_sub_titulo.set("")
            var_sub_minutos.set("15")
            atualizar_subtarefas()
            entry_sub.focus_set()

        ttk.Button(form, text="Adicionar", command=adicionar_sub).grid(row=0, column=4)
        entry_sub.bind("<Return>", lambda _e: adicionar_sub())

        def alternar_sub() -> None:
            sel = tree_sub.selection()
            if not sel:
                messagebox.showwarning(
                    "Nenhuma Seleção",
                    "Selecione uma subtarefa na lista.",
                    parent=modal,
                )
                return
            idx = int(sel[0])
            atividade.subtarefas[idx].alternar_status()
            atualizar_subtarefas(selecionar_iid=sel[0])

        def remover_sub() -> None:
            sel = tree_sub.selection()
            if not sel:
                messagebox.showwarning(
                    "Nenhuma Seleção",
                    "Selecione uma subtarefa na lista para remover.",
                    parent=modal,
                )
                return
            idx = int(sel[0])
            try:
                atividade.remover_subtarefa(idx)
            except IndexError as exc:
                messagebox.showerror("Erro", str(exc), parent=modal)
                return
            atualizar_subtarefas()

        tree_sub.bind(
            "<Double-1>",
            lambda event: alternar_sub() if tree_sub.identify_row(event.y) else None,
        )

        botoes = ttk.Frame(frame)
        botoes.grid(row=4, column=0, sticky="ew")
        ttk.Button(botoes, text="Alternar Status", command=alternar_sub).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(botoes, text="Remover Subtarefa", command=remover_sub).pack(side="left")
        ttk.Button(botoes, text="Fechar", command=modal.destroy).pack(side="right")

        atualizar_subtarefas()
        entry_sub.focus_set()

    def _alternar_conclusao_selecionada(self) -> None:
        """Alterna o status de conclusão da atividade selecionada."""
        atividade = self._obter_atividade_selecionada(avisar=True)
        if atividade is None:
            return
        self.gestor.alternar_conclusao(atividade.id)
        self.atualizar_lista()

    def _remover_atividade_selecionada(self) -> None:
        """Remove a atividade selecionada destacando a eliminação das subtarefas."""
        atividade = self._obter_atividade_selecionada(avisar=True)
        if atividade is None:
            return

        qtd_subtarefas = len(atividade.subtarefas)
        if qtd_subtarefas > 0:
            aviso_comp = (
                f"Composição: as {qtd_subtarefas} subtarefa(s) vinculada(s) a esta atividade "
                "também serão removidas permanentemente junto com ela."
            )
        else:
            aviso_comp = (
                "Composição: quaisquer subtarefas pertencentes à atividade são "
                "eliminadas junto com ela."
            )

        confirmar = messagebox.askyesno(
            "Confirmar Remoção",
            f"Deseja realmente remover '{atividade.titulo}'?\n\n{aviso_comp}",
            parent=self.root,
        )
        if not confirmar:
            return

        self.gestor.remover_atividade(atividade.id)
        self.atualizar_lista()

    def _abrir_modal_disciplinas(self) -> None:
        """Abre modal para cadastrar e remover disciplinas (Associação)."""
        modal = self._criar_modal("Gerenciar Disciplinas", 540, 400, redimensionavel=True)
        frame = ttk.Frame(modal, padding=14)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        ttk.Label(
            frame,
            text="Associação: ao remover uma disciplina, as atividades continuam no gestor sem disciplina.",
            style="Hint.TLabel",
            wraplength=500,
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        lista_frame = ttk.Frame(frame)
        lista_frame.grid(row=1, column=0, sticky="nsew")
        lista_frame.columnconfigure(0, weight=1)
        lista_frame.rowconfigure(0, weight=1)

        tree_disc = ttk.Treeview(
            lista_frame,
            columns=("codigo", "nome"),
            show="headings",
            selectmode="browse",
        )
        tree_disc.heading("codigo", text="Código")
        tree_disc.heading("nome", text="Nome")
        tree_disc.column("codigo", width=110, anchor="center", stretch=False)
        tree_disc.column("nome", width=360, anchor="w", stretch=True)

        scroll = ttk.Scrollbar(lista_frame, orient="vertical", command=tree_disc.yview)
        tree_disc.configure(yscrollcommand=scroll.set)
        tree_disc.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

        def atualizar_disciplinas() -> None:
            tree_disc.delete(*tree_disc.get_children())
            for disc in self.gestor.listar_disciplinas():
                tree_disc.insert("", tk.END, iid=disc.codigo, values=(disc.codigo, disc.nome))
            self.atualizar_lista()

        form = ttk.LabelFrame(frame, text="Cadastrar Nova Disciplina", padding=(10, 8))
        form.grid(row=2, column=0, sticky="ew", pady=(10, 8))
        form.columnconfigure(3, weight=1)

        var_codigo = tk.StringVar()
        var_nome = tk.StringVar()

        ttk.Label(form, text="Código *:").grid(row=0, column=0, sticky="w", padx=(0, 6))
        entry_codigo = ttk.Entry(form, textvariable=var_codigo, width=12)
        entry_codigo.grid(row=0, column=1, sticky="w", padx=(0, 10))

        ttk.Label(form, text="Nome *:").grid(row=0, column=2, sticky="w", padx=(0, 6))
        entry_nome = ttk.Entry(form, textvariable=var_nome)
        entry_nome.grid(row=0, column=3, sticky="ew", padx=(0, 10))

        def cadastrar() -> None:
            try:
                self.gestor.cadastrar_disciplina(var_codigo.get(), var_nome.get())
            except ValueError as exc:
                messagebox.showerror(
                    "Erro ao Cadastrar Disciplina", str(exc), parent=modal
                )
                return

            var_codigo.set("")
            var_nome.set("")
            atualizar_disciplinas()
            entry_codigo.focus_set()

        ttk.Button(form, text="Cadastrar", command=cadastrar).grid(row=0, column=4)
        entry_nome.bind("<Return>", lambda _e: cadastrar())

        def remover_selecionada() -> None:
            sel = tree_disc.selection()
            if not sel:
                messagebox.showwarning(
                    "Nenhuma Seleção",
                    "Selecione uma disciplina para remover.",
                    parent=modal,
                )
                return
            codigo = sel[0]
            confirmar = messagebox.askyesno(
                "Confirmar Remoção",
                f"Remover a disciplina '{codigo}'?\n\n"
                "As atividades associadas continuarão cadastradas sem disciplina.",
                parent=modal,
            )
            if not confirmar:
                return
            self.gestor.remover_disciplina(codigo)
            atualizar_disciplinas()

        botoes = ttk.Frame(frame)
        botoes.grid(row=3, column=0, sticky="ew")
        ttk.Button(botoes, text="Remover Selecionada", command=remover_selecionada).pack(
            side="left"
        )
        ttk.Button(botoes, text="Fechar", command=modal.destroy).pack(side="right")

        atualizar_disciplinas()
        entry_codigo.focus_set()

    def _abrir_modal_relatorio(self) -> None:
        """Abre modal de relatório usando ExportadorRelatorio por Dependência."""
        exportador = ExportadorRelatorio()
        texto_relatorio = self.gestor.gerar_relatorio(exportador)

        modal = self._criar_modal("Relatório de Atividades", 740, 500, redimensionavel=True)
        frame = ttk.Frame(modal, padding=14)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        ttk.Label(
            frame,
            text="Dependência: relatório gerado sob demanda via ExportadorRelatorio.",
            style="Hint.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        text_frame = ttk.Frame(frame)
        text_frame.grid(row=1, column=0, sticky="nsew")
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        txt = tk.Text(
            text_frame,
            wrap="word",
            font=("Consolas", 10),
            bg="#FFFFFF",
            fg="#0F172A",
            padx=10,
            pady=10,
        )
        txt.insert("1.0", texto_relatorio)
        txt.configure(state="disabled")

        scroll = ttk.Scrollbar(text_frame, orient="vertical", command=txt.yview)
        txt.configure(yscrollcommand=scroll.set)
        txt.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

        def salvar_txt() -> None:
            caminho = filedialog.asksaveasfilename(
                parent=modal,
                title="Salvar Relatório em .txt",
                defaultextension=".txt",
                filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os arquivos", "*.*")],
                initialfile="relatorio_atividades.txt",
            )
            if not caminho:
                return
            try:
                exportador_local = ExportadorRelatorio()
                destino = self.gestor.exportar_relatorio_txt(exportador_local, caminho)
            except (OSError, ValueError) as exc:
                messagebox.showerror(
                    "Erro ao Salvar Relatório",
                    f"Não foi possível salvar o relatório:\n{exc}",
                    parent=modal,
                )
                return
            messagebox.showinfo(
                "Relatório Exportado",
                f"Relatório salvo com sucesso em:\n{destino}",
                parent=modal,
            )

        botoes = ttk.Frame(frame)
        botoes.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        ttk.Button(botoes, text="Salvar .txt", command=salvar_txt).pack(side="left")
        ttk.Button(botoes, text="Fechar", command=modal.destroy).pack(side="right")
