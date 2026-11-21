# Study-Flow — Diagrama de Classes (UML)

> **Nível 1** — Modelagem do domínio da aplicação.

O diagrama abaixo representa as principais entidades do Study-Flow, seus atributos, métodos e relacionamentos.

```mermaid
classDiagram
    direction TB

    class Usuario {
        -UUID id
        -String nome
        -String email
        -String senhaHash
        -DateTime dataCadastro
        +cadastrar() void
        +autenticar(email, senha) bool
        +atualizarPerfil(nome, email) void
        +alterarSenha(senhaAtual, novaSenha) void
    }

    class Disciplina {
        -UUID id
        -String nome
        -String professor
        -String cor
        -String descricao
        +calcularHorasEstudadas() int
        +listarTarefasPendentes() List~Tarefa~
    }

    class Tarefa {
        -UUID id
        -String titulo
        -String descricao
        -DateTime dataEntrega
        -Prioridade prioridade
        -StatusTarefa status
        -DateTime dataCriacao
        -DateTime dataConclusao
        +atualizarStatus(status) void
        +concluir() void
        +estaAtrasada() bool
        +calcularProgresso() float
    }

    class Subtarefa {
        -UUID id
        -String titulo
        -bool concluida
        +alternarConclusao() void
    }

    class Etiqueta {
        -UUID id
        -String nome
        -String cor
    }

    class PlanoEstudo {
        -UUID id
        -String titulo
        -Date dataInicio
        -Date dataFim
        +adicionarBloco(bloco) void
        +removerBloco(bloco) void
        +calcularCargaSemanal() int
    }

    class BlocoEstudo {
        -UUID id
        -DiaSemana diaSemana
        -Time horaInicio
        -Time horaFim
        +duracaoMinutos() int
    }

    class SessaoEstudo {
        -UUID id
        -DateTime inicio
        -DateTime fim
        -int duracaoMinutos
        -TipoSessao tipo
        -String anotacoes
        +iniciar() void
        +pausar() void
        +finalizar() void
    }

    class Meta {
        -UUID id
        -String descricao
        -PeriodoMeta periodo
        -int alvoMinutos
        -Date dataInicio
        -Date dataFim
        +calcularProgresso() float
        +foiAtingida() bool
    }

    class Lembrete {
        -UUID id
        -DateTime dataHora
        -String mensagem
        -bool enviado
        +agendar() void
        +enviar() void
        +cancelar() void
    }

    class Relatorio {
        -Date periodoInicio
        -Date periodoFim
        +horasPorDisciplina() Map
        +taxaConclusaoTarefas() float
        +metasAtingidas() int
        +exportar(formato) File
    }

    class Prioridade {
        <<enumeration>>
        BAIXA
        MEDIA
        ALTA
        URGENTE
    }

    class StatusTarefa {
        <<enumeration>>
        PENDENTE
        EM_ANDAMENTO
        CONCLUIDA
        CANCELADA
    }

    class TipoSessao {
        <<enumeration>>
        POMODORO
        LIVRE
    }

    class PeriodoMeta {
        <<enumeration>>
        DIARIA
        SEMANAL
        MENSAL
    }

    class DiaSemana {
        <<enumeration>>
        SEGUNDA
        TERCA
        QUARTA
        QUINTA
        SEXTA
        SABADO
        DOMINGO
    }

    %% Relacionamentos do Usuário
    Usuario "1" *-- "0..*" Disciplina : possui
    Usuario "1" *-- "0..*" Tarefa : gerencia
    Usuario "1" *-- "0..*" Etiqueta : cria
    Usuario "1" *-- "0..*" PlanoEstudo : elabora
    Usuario "1" *-- "0..*" SessaoEstudo : registra
    Usuario "1" *-- "0..*" Meta : define
    Usuario "1" ..> Relatorio : gera

    %% Tarefas
    Disciplina "0..1" o-- "0..*" Tarefa : agrupa
    Tarefa "1" *-- "0..*" Subtarefa : contém
    Tarefa "0..*" -- "0..*" Etiqueta : classificada por
    Tarefa "1" *-- "0..*" Lembrete : dispara

    %% Planejamento e estudo
    PlanoEstudo "1" *-- "1..*" BlocoEstudo : composto por
    BlocoEstudo "0..*" --> "1" Disciplina : referencia
    SessaoEstudo "0..*" --> "0..1" Disciplina : sobre
    SessaoEstudo "0..*" --> "0..1" Tarefa : vinculada a
    Meta "0..*" --> "0..1" Disciplina : foca em

    %% Enumerações
    Tarefa ..> Prioridade
    Tarefa ..> StatusTarefa
    SessaoEstudo ..> TipoSessao
    Meta ..> PeriodoMeta
    BlocoEstudo ..> DiaSemana
```

## Descrição das classes

| Classe | Responsabilidade |
|---|---|
| **Usuario** | Estudante que utiliza a plataforma; dono de todos os dados. |
| **Disciplina** | Matéria/assunto de estudo (ex.: Cálculo I, Inglês). Agrupa tarefas e sessões. |
| **Tarefa** | Atividade com prazo e prioridade (trabalho, prova, exercício, leitura). |
| **Subtarefa** | Item de checklist dentro de uma tarefa, usado para medir o progresso. |
| **Etiqueta** | Marcador livre para classificar e filtrar tarefas. |
| **PlanoEstudo** | Cronograma de estudos válido por um período. |
| **BlocoEstudo** | Horário fixo do cronograma (dia da semana + intervalo) ligado a uma disciplina. |
| **SessaoEstudo** | Registro de tempo efetivamente estudado (livre ou Pomodoro). |
| **Meta** | Objetivo de tempo de estudo por período (diária, semanal, mensal). |
| **Lembrete** | Notificação agendada relacionada a uma tarefa. |
| **Relatorio** | Consolida dados de sessões, tarefas e metas para acompanhamento do desempenho. |

## Legenda dos relacionamentos

| Símbolo | Significado |
|---|---|
| `*--` | **Composição** — a parte não existe sem o todo (ex.: Subtarefa sem Tarefa). |
| `o--` | **Agregação** — a parte pode existir sem o todo (ex.: Tarefa sem Disciplina). |
| `-->` | **Associação direcionada** — uma classe referencia a outra. |
| `--` | **Associação** — relação entre as classes nos dois sentidos (N:N entre Tarefa e Etiqueta). |
| `..>` | **Dependência** — uma classe usa a outra (ex.: Relatório gerado sob demanda). |
