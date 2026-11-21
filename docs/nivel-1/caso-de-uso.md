# Study-Flow — Diagrama de Casos de Uso

> **Nível 1** — Funcionalidades do sistema e como os atores interagem com elas.

O Mermaid não tem um tipo nativo para diagramas de caso de uso. Por isso, ele foi montado com `flowchart`: os atores ficam fora do retângulo do sistema e os casos de uso aparecem como elipses dentro dele.

```mermaid
flowchart LR
    Visitante(["👤 Visitante"])
    Estudante(["👤 Estudante"])
    Notificador(["⚙️ Serviço de Notificação"])

    subgraph SF["Study-Flow"]
        direction TB

        subgraph CONTA["Conta"]
            UC01(["UC01 · Cadastrar conta"])
            UC02(["UC02 · Fazer login"])
            UC03(["UC03 · Recuperar senha"])
            UC04(["UC04 · Gerenciar perfil"])
        end

        subgraph ORG["Organização"]
            UC05(["UC05 · Gerenciar disciplinas"])
            UC06(["UC06 · Gerenciar tarefas"])
            UC07(["UC07 · Definir prioridade e prazo"])
            UC08(["UC08 · Adicionar subtarefas"])
            UC09(["UC09 · Atribuir etiquetas"])
            UC10(["UC10 · Concluir tarefa"])
            UC11(["UC11 · Filtrar e buscar tarefas"])
        end

        subgraph PLAN["Planejamento"]
            UC12(["UC12 · Montar plano de estudos"])
            UC13(["UC13 · Visualizar agenda / calendário"])
            UC14(["UC14 · Configurar lembretes"])
            UC15(["UC15 · Enviar notificações"])
        end

        subgraph ACOMP["Acompanhamento"]
            UC16(["UC16 · Registrar sessão de estudo"])
            UC17(["UC17 · Usar timer Pomodoro"])
            UC18(["UC18 · Definir metas de estudo"])
            UC19(["UC19 · Visualizar dashboard de progresso"])
            UC20(["UC20 · Gerar relatório de desempenho"])
        end
    end

    %% Visitante
    Visitante --- UC01
    Visitante --- UC02
    Visitante --- UC03

    %% Estudante
    Estudante --- UC04
    Estudante --- UC05
    Estudante --- UC06
    Estudante --- UC10
    Estudante --- UC11
    Estudante --- UC12
    Estudante --- UC13
    Estudante --- UC14
    Estudante --- UC16
    Estudante --- UC18
    Estudante --- UC19
    Estudante --- UC20

    %% Serviço de Notificação
    UC15 --- Notificador

    %% Include / Extend
    UC06 -.->|"«include»"| UC07
    UC08 -.->|"«extend»"| UC06
    UC09 -.->|"«extend»"| UC06
    UC17 -.->|"«extend»"| UC16
    UC14 -.->|"«include»"| UC15
    UC20 -.->|"«include»"| UC19
```

> **Observação:** com exceção de **UC01**, **UC02** e **UC03**, todos os casos de uso exigem que o usuário esteja autenticado (pré-condição: *UC02 · Fazer login*). Essa ligação foi omitida do diagrama para não poluir a leitura.

## Atores

| Ator | Tipo | Descrição |
|---|---|---|
| **Visitante** | Primário | Pessoa ainda não autenticada que pode criar conta, entrar ou recuperar a senha. |
| **Estudante** | Primário | Usuário autenticado que organiza tarefas, planeja e acompanha os estudos. |
| **Serviço de Notificação** | Secundário (sistema) | Serviço externo/agendador que entrega lembretes (e-mail, push, etc.). |

## Descrição dos casos de uso

| ID | Caso de uso | Descrição resumida |
|---|---|---|
| UC01 | Cadastrar conta | Criar conta com nome, e-mail e senha. |
| UC02 | Fazer login | Autenticar-se com e-mail e senha. |
| UC03 | Recuperar senha | Redefinir a senha via link enviado por e-mail. |
| UC04 | Gerenciar perfil | Editar dados pessoais e alterar a senha. |
| UC05 | Gerenciar disciplinas | Criar, editar, listar e excluir disciplinas. |
| UC06 | Gerenciar tarefas | Criar, editar, listar e excluir tarefas, ligadas ou não a uma disciplina. |
| UC07 | Definir prioridade e prazo | Informar a data de entrega e o nível de prioridade da tarefa (obrigatório ao criar). |
| UC08 | Adicionar subtarefas | Quebrar uma tarefa em itens de checklist (opcional). |
| UC09 | Atribuir etiquetas | Classificar a tarefa com etiquetas personalizadas (opcional). |
| UC10 | Concluir tarefa | Marcar a tarefa como concluída e registrar a data de conclusão. |
| UC11 | Filtrar e buscar tarefas | Filtrar por status, prioridade, disciplina, etiqueta ou prazo. |
| UC12 | Montar plano de estudos | Montar um cronograma semanal com blocos de horário por disciplina. |
| UC13 | Visualizar agenda / calendário | Ver tarefas e blocos de estudo em visão diária, semanal ou mensal. |
| UC14 | Configurar lembretes | Agendar avisos antes do prazo de uma tarefa. |
| UC15 | Enviar notificações | O sistema dispara o lembrete na data/hora configurada. |
| UC16 | Registrar sessão de estudo | Marcar o tempo de estudo de uma disciplina ou tarefa. |
| UC17 | Usar timer Pomodoro | Registrar a sessão com ciclos de foco e pausa (opcional). |
| UC18 | Definir metas de estudo | Definir uma meta de tempo diária, semanal ou mensal. |
| UC19 | Visualizar dashboard de progresso | Ver horas estudadas, tarefas pendentes/concluídas e andamento das metas. |
| UC20 | Gerar relatório de desempenho | Gerar e exportar um relatório consolidado de um período. |

## Legenda

| Notação | Significado |
|---|---|
| Linha contínua (`---`) | Associação entre ator e caso de uso. |
| `«include»` | O caso de uso base **sempre** executa o caso incluído. |
| `«extend»` | O caso de uso estendido é **opcional** e acrescenta comportamento ao caso base. |
