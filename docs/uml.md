# Diagrama de Classes UML 2.5 — Study-Flow (POO em Python)

Arquitetura em camadas (`models` · `services` · `ui`) evidenciando **Herança**, **Polimorfismo**, **Composição**, **Associação** e **Dependência**.

## Diagrama de Classes (`classDiagram`)

```mermaid
classDiagram
    direction TB

    class GestorApp {
        <<ui/app_gui.py>>
        +tk.Tk root
        +GestorAtividades gestor
        +ttk.Treeview tree
        +GestorApp(root: tk.Tk, gestor: GestorAtividades)
        +atualizar_lista() None
    }

    class ExportadorRelatorio {
        <<services/exportador_relatorio.py>>
        +gerar_relatorio(atividades: list~Atividade~) str
        +salvar_txt(atividades: list~Atividade~, caminho: str) str
    }

    class GestorAtividades {
        <<services/gestor_atividades.py>>
        -list~Disciplina~ _disciplinas
        -list~Atividade~ _atividades
        -int _proximo_id
        +GestorAtividades()
        +cadastrar_disciplina(codigo: str, nome: str) Disciplina
        +listar_disciplinas() list~Disciplina~
        +buscar_disciplina(codigo: str) Optional~Disciplina~
        +remover_disciplina(codigo: str) bool
        +adicionar_tarefa(titulo, ..., prazo, minutos_base) Tarefa
        +adicionar_sessao_estudo(titulo, topico, ..., pomodoros) SessaoEstudo
        +listar_atividades(apenas_pendentes, codigo_disciplina, tipo) list~Atividade~
        +buscar_atividade(atividade_id: int) Optional~Atividade~
        +remover_atividade(atividade_id: int) bool
        +alternar_conclusao(atividade_id: int) bool
        +calcular_tempo_total(apenas_pendentes: bool = False) int
        +gerar_relatorio(exportador: ExportadorRelatorio) str
        +exportar_relatorio_txt(exportador: ExportadorRelatorio, caminho: str) str
        +carregar_dados_exemplo() None
    }

    class Atividade {
        <<abstract>>
        +tuple~str~ PRIORIDADES_VALIDAS$
        -int _id
        -str _titulo
        -str _descricao
        -str _prioridade
        -bool _concluida
        -Optional~Disciplina~ _disciplina
        -list~Subtarefa~ _subtarefas
        +Atividade(atividade_id, titulo, descricao, prioridade, disciplina)
        +id() int
        +titulo() str
        +descricao() str
        +prioridade() str
        +concluida() bool
        +disciplina() Optional~Disciplina~
        +subtarefas() tuple~Subtarefa~
        +adicionar_subtarefa(titulo: str, minutos_estimados: int = 15) Subtarefa
        +remover_subtarefa(indice: int) None
        +tempo_subtarefas() int
        +concluir() None
        +reabrir() None
        +alternar_status() None
        +tipo()* str
        +calcular_tempo_estimado()* int
        +resumo()* str
        +__str__() str
    }

    class Subtarefa {
        <<models/subtarefa.py>>
        -str _titulo
        -int _minutos_estimados
        -bool _concluida
        +Subtarefa(titulo: str, minutos_estimados: int = 15, concluida: bool = False)
        +titulo() str
        +minutos_estimados() int
        +concluida() bool
        +concluir() None
        +reabrir() None
        +alternar_status() None
        +__str__() str
        +__repr__() str
    }

    class Disciplina {
        <<models/disciplina.py>>
        -str _codigo
        -str _nome
        +Disciplina(codigo: str, nome: str)
        +codigo() str
        +nome() str
        +__str__() str
        +__repr__() str
        +__eq__(other: object) bool
        +__hash__() int
    }

    class Tarefa {
        <<models/tarefa.py>>
        -str _prazo
        -int _minutos_base
        +Tarefa(atividade_id, titulo, descricao, prioridade, disciplina, prazo, minutos_base)
        +prazo() str
        +minutos_base() int
        +tipo() str
        +calcular_tempo_estimado() int
        +resumo() str
    }

    class SessaoEstudo {
        <<models/sessao_estudo.py>>
        -str _topico
        -int _pomodoros
        -int _duracao_pomodoro
        -bool _incluir_revisao
        +SessaoEstudo(atividade_id, titulo, topico, ..., pomodoros, duracao, revisao)
        +topico() str
        +pomodoros() int
        +duracao_pomodoro() int
        +incluir_revisao() bool
        +tipo() str
        +calcular_tempo_estimado() int
        +resumo() str
    }

    GestorApp "1" --> "1" GestorAtividades : utiliza (Associação)
    GestorApp ..> ExportadorRelatorio : «dependência»
    GestorAtividades ..> ExportadorRelatorio : «dependência» (parâmetro)
    ExportadorRelatorio ..> Atividade : «dependência»
    GestorAtividades "1" --> "0..*" Atividade : gerencia
    GestorAtividades "1" --> "0..*" Disciplina : cadastra (Associação)
    Atividade "0..*" --> "0..1" Disciplina : associação
    Atividade "1" *-- "0..*" Subtarefa : compõe
    Atividade <|-- Tarefa : Herança + Polimorfismo
    Atividade <|-- SessaoEstudo : Herança + Polimorfismo

    classDef ui fill:#1d4ed8,stroke:#1e3a8a,color:#ffffff
    classDef servicos fill:#0f766e,stroke:#134e4a,color:#ffffff
    classDef abstrato fill:#4338ca,stroke:#312e81,color:#ffffff
    classDef concreto fill:#334155,stroke:#0f172a,color:#ffffff

    class GestorApp:::ui
    class GestorAtividades:::servicos
    class ExportadorRelatorio:::servicos
    class Atividade:::abstrato
    class Tarefa:::concreto
    class SessaoEstudo:::concreto
    class Subtarefa:::concreto
    class Disciplina:::concreto
```

> **Notação:** `-` indica atributo privado encapsulado (exposto via `@property`), `+` indica membro público, `$` indica atributo de classe e `*` indica método abstrato (`@abstractmethod`) sobrescrito polimorficamente pelas subclasses.

## Visão Geral da Arquitetura em Camadas

| Camada | Classes |
| :--- | :--- |
| **UI** (`ui/`) | `GestorApp` (Tkinter/ttk) — interação e atualização reativa |
| **Services** (`services/`) | `GestorAtividades` e `ExportadorRelatorio` |
| **Domínio abstrato** (`models/`) | `Atividade` (ABC) + métodos abstratos |
| **Domínio concreto** (`models/`) | `Tarefa`, `SessaoEstudo`, `Subtarefa` e `Disciplina` |

## Legenda dos 5 Pilares e Relações POO

| Conceito | Notação | Aplicação no sistema |
| :--- | :---: | :--- |
| **Herança** | `<\|--` | `Tarefa` e `SessaoEstudo` estendem `Atividade` (ABC). |
| **Polimorfismo** | `*` (abstract) | `tipo()`, `calcular_tempo_estimado()` e `resumo()` são sobrescritos pelas subclasses. |
| **Composição** | `*--` | `Subtarefa` pertence à `Atividade` e morre com ela. |
| **Associação** | `-->` | `Atividade` e `Disciplina` possuem ciclos de vida independentes. |
| **Dependência** | `..>` | `ExportadorRelatorio` é usado apenas via parâmetro. |
