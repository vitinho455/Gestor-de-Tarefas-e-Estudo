# Gestão de Tarefas e Estudo (POO em Python)

Aplicação desktop em Python puro (apenas biblioteca padrão + `tkinter`/`ttk`) desenvolvida para demonstrar na prática os fundamentos e relacionamentos da **Programação Orientada a Objetos (POO)**: **Herança**, **Polimorfismo**, **Composição**, **Associação**, **Dependência**, **Abstração** e **Encapsulamento**.

---

## Principais Funcionalidades

- Cadastro e remoção de **Disciplinas** (com normalização automática de código e prevenção de duplicidade).
- Criação e gerenciamento polimórfico de **Tarefas** (com prazo e tempo base) e **Sessões de Estudo** (baseadas em técnica Pomodoro e revisão opcional).
- Gerenciamento de **Subtarefas** compostas dentro de cada atividade, somando automaticamente ao tempo estimado.
- Filtros dinâmicos por **Disciplina**, **Tipo de Atividade** e **Status (Apenas pendentes)**, com métricas em tempo real.
- Geração e exportação de **Relatórios em `.txt`** (UTF-8) usando um exportador desacoplado por dependência.
- Carga inicial de **dados de exemplo** para demonstração imediata.

---

## Estrutura de Pastas

```text
Gestor-de-Tarefas-e-Estudo/
├── main.py                         # Ponto de entrada da aplicação desktop
├── README.md                       # Visão geral, comandos e roteiro de vídeo
├── LICENSE                         # Licença CC0 1.0 Universal
├── docs/
│   └── uml.md                      # Diagrama UML detalhado e tabela de conceitos POO
├── models/
│   ├── __init__.py
│   ├── disciplina.py               # Classe Disciplina (Associação)
│   ├── subtarefa.py                # Classe Subtarefa (Composição)
│   ├── atividade.py                # Classe abstrata Atividade (ABC, encapsulamento e composição)
│   ├── tarefa.py                   # Subclasse Tarefa (Herança e Polimorfismo)
│   └── sessao_estudo.py            # Subclasse SessaoEstudo (Herança e Polimorfismo)
├── services/
│   ├── __init__.py
│   ├── exportador_relatorio.py     # Serviço sem estado ExportadorRelatorio (Dependência)
│   └── gestor_atividades.py        # Orquestração de domínio GestorAtividades
├── ui/
│   ├── __init__.py
│   └── app_gui.py                  # Interface gráfica Tkinter/ttk (GestorApp)
└── tests/
    ├── __init__.py
    └── test_gestor.py              # Suíte unittest cobrindo POO, regras e smoke test da GUI
```

---

## Diagrama de Classes UML

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

Para a legenda completa dos pilares POO e da arquitetura em camadas, consulte [docs/uml.md](docs/uml.md).

---

## Como Executar

> Pré-requisito: **Python 3.11+** (testado em Python 3.15, usando somente a biblioteca padrão).

### 1. Executar a aplicação desktop (`Tkinter`)

```bash
python main.py
```

### 2. Executar a suíte de testes automatizados (`unittest`)

```bash
python -m unittest discover -s tests -v
```

---

## Roteiro de Vídeo (YouTube — até 3 minutos)

Use este roteiro enxuto para apresentar o funcionamento do aplicativo, a modelagem UML e os testes dentro de **2 min 45 s a 3 min**:

| Tempo | Bloco | O que mostrar e falar |
| :--- | :--- | :--- |
| **0:00 – 0:25** | **Abertura e Objetivo** | Mostre o título e a estrutura de pastas (`models`, `services`, `ui`, `tests`, `docs`). Explique que o projeto é um **Gestor de Tarefas e Estudos** feito em Python puro com `Tkinter` para demonstrar os 5 pilares/relações de POO. |
| **0:25 – 1:15** | **Demonstração do App (`python main.py`)** | Rode `python main.py`. Mostre os dados iniciais carregados, crie uma **Nova Tarefa** ou **Sessão de Estudo** (Pomodoro + revisão), abra **Subtarefas** para adicionar/concluir itens e mostrar o recálculo imediato de tempo. Aplique filtros (Disciplina, Tipo, Apenas pendentes) e abra **Relatório** para visualizar e salvar em `.txt`. |
| **1:15 – 2:20** | **Arquitetura POO e UML (`docs/uml.md`)** | Exiba o diagrama Mermaid no `README.md` / `docs/uml.md` e faça um tour rápido pelo código: **(1) Herança & Polimorfismo** (`Atividade` abstrata -> `Tarefa` e `SessaoEstudo` sobrescrevendo `calcular_tempo_estimado()` e `resumo()`); **(2) Composição** (`Atividade` cria e destrói `Subtarefa`); **(3) Associação** (remover `Disciplina` preserva atividades com `disciplina = None`); **(4) Dependência** (`GestorAtividades` recebe `ExportadorRelatorio` apenas por parâmetro). |
| **2:20 – 2:55** | **Testes Automatizados e Encerramento** | Rode `python -m unittest discover -s tests -v` no terminal mostrando todos os testes passando (incluindo herança, polimorfismo, composição, associação, dependência e smoke test da GUI). Finalize destacando que a separação em camadas mantém a lógica de negócio 100% independente da interface gráfica. |
