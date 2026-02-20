# Программное управление состоянием и переходами для AI‑агентов в 2025–2026 гг.

## Исполнительное резюме

Этот документ — полный перевод на русский язык ранее предоставленного англоязычного технического отчёта о том, как современные “агентные” системы (AI‑agents) управляют **состоянием (state)** и **переходами (transitions)** в рамках формализованных процессов: от графовых оркестраторов (stateful graphs / state machines) до платформ **устойчивого выполнения (durable execution)** и разработческих агентных пайплайнов, где **артефактное состояние (artifact state)** реализуется через Git‑ветки и pull request. Перевод датирован **19 февраля 2026**.

Ключевой вывод отчёта: для сценариев вроде “work3 создаёт своё состояние при первом входе, сохраняет его в ходе стадии, затем делает merge в main и очищает work3” наиболее надёжно работают системы, где переходы описаны **кодом и/или схемой workflow**, а состояние закрепляется через **чекпойнты (checkpoints)** или журнал событий (**event history**), чтобы агент мог “понять, что происходит” не из длинного контекста, а через быстрый запрос к авторитетному источнику состояния (checkpoint history / workflow queries). (См. ссылки на первичные источники в тексте: GitHub‑репозитории, официальные docs, а также материалы о безопасности и исследованиях.)

Ниже приведён перевод с сохранением структуры, ссылок‑цитирований, дат и идентификаторов (например, `work3`, `get_state_history`, `@persist`, `TemporalAgent`). URL‑адреса сохранены без изменений. Иллюстрации из оригинала включены как изображения с теми же ссылками.

## Постановка задачи и что именно означает «state» в вашем примере

Ваш пример про `work3` — это скорее не про «память чата», а про **долговременно и программно контролируемый процесс выполнения**: агент входит в чётко определённую стадию, инициализирует специфичное для стадии состояние при первом входе, изменяет это состояние во времени, а затем выполняет явный переход (например, «готово к merge в main») с очисткой («удалить work3»). Это та же базовая задача, которую много лет решали движки воркфлоу и библиотеки оркестрации машин состояний — но она снова стала центральной в «агентном» мире, потому что LLM делает ветвление более динамичным, а вызовы инструментов (tool calls) более склонными к сбоям. ([agentic-design.ai](https://agentic-design.ai/patterns/workflow-orchestration/stateful-graph-workflows?utm_source=chatgpt.com))

Удобная декомпозиция “state” для агентных систем (которая напрямую ложится на вашу аналогию с ветками `work3`) выглядит так:

- **Состояние процесса/воркфлоу (workflow/process state)**: «На каком шаге/стадии я нахожусь, какие охранные условия (guard conditions) позволяют перейти дальше, какой следующий шаг?» Именно этот слой делает переходы явными и машинно‑проверяемыми. ([agentic-design.ai](https://agentic-design.ai/patterns/workflow-orchestration/stateful-graph-workflows?utm_source=chatgpt.com))  
- **История выполнения / аудит‑трейл (execution history / audit trail)**: «Что произошло, в каком порядке, и какие решения действительно были приняты?» Это и позволяет ответить на «что происходит?» парой команд — запросив снапшоты или журнал событий. ([docs.temporal.io](https://docs.temporal.io/workflow-execution/event?utm_source=chatgpt.com))  
- **Рабочая память / память знаний (working memory / knowledge memory)**: факты и резюме, переносимые между шагами (краткосрочно) или между запусками (долгосрочно). Это полезно, но само по себе редко гарантирует корректные переходы или возобновляемость после отказов. ([docs.langchain.com](https://docs.langchain.com/oss/python/langgraph/add-memory?utm_source=chatgpt.com))  
- **Артефактное состояние (artifact state)**: файлы, патчи, результаты тестов, PR, ветки — то есть конкретные объекты, которые создаются, пока `work3` активно. В инженерных сценариях Git и PR‑инструментирование часто становятся хранилищем артефактного состояния. ([docs.github.com](https://docs.github.com/copilot/using-github-copilot/coding-agent/asking-copilot-to-create-a-pull-request?utm_source=chatgpt.com))  

Рост популярности «агентов, которые реально делают вещи» (например, OpenClaw) — одна из причин, почему эта тема стала срочной: таким системам часто нужно уметь останавливаться, возобновляться, разветвляться и аккуратно отслеживать результаты инструментов, учетные данные и решения. ([reuters.com](https://www.reuters.com/business/openclaw-founder-steinberger-joins-openai-open-source-bot-becomes-foundation-2026-02-15/?utm_source=chatgpt.com))

Ниже — краткая сравнительная таблица (добавлена для удобства; формулировки опираются на те же источники, что и основной текст).

| Проект | Подход к состоянию (state) | Механизм персистентности | Примечания |
|---|---|---|---|
| entity["organization","LangGraph","stateful agent graphs"] | Граф/машина состояний со state‑объектом и шагами | Checkpointer, история чекпойнтов, `thread` | Поддержка пауз/возобновления и “time travel” ([github.com](https://github.com/langchain-ai/langgraph?utm_source=chatgpt.com), [docs.langchain.com](https://docs.langchain.com/oss/python/langgraph/persistence?utm_source=chatgpt.com)) |
| entity["company","Microsoft Agent Framework","agent workflow framework"] | Типобезопасные workflow‑графы + сессии | Сессии, чекпойнты, маршрутизация событий | Смещение от message‑orchestration к typed workflow ([learn.microsoft.com](https://learn.microsoft.com/en-us/agent-framework/overview/?utm_source=chatgpt.com)) |
| entity["company","Temporal","durable workflow engine"] | Durable execution: детерминированный workflow + Activities | Event History, replay, Queries/Signals/Updates | Сильная возобновляемость/аудит; требует дисциплины детерминизма ([docs.temporal.io](https://docs.temporal.io/workflow-execution/event?utm_source=chatgpt.com)) |
| entity["organization","Restate","durable execution platform"] | Durable execution с объектным/сессионным state | Журналирование шагов и state‑обновлений | Акцент на single‑writer и scoped state ([docs.restate.dev](https://docs.restate.dev/foundations/key-concepts?utm_source=chatgpt.com)) |
| entity["organization","Inngest","durable functions platform"] | Durable functions: шаги, ожидания, ретраи | Идентификация шагов, восстановление step‑state | Длинные “wait”, ретраи; step IDs и версионирование ([github.com](https://github.com/inngest/inngest?utm_source=chatgpt.com)) |
| entity["organization","LlamaIndex","llm data framework"] | Workflows + `Context` как state | Сохранение/восстановление контекста | `Context` можно переносить между запусками ([developers.llamaindex.ai](https://developers.llamaindex.ai/python/llamaagents/workflows/managing_state/?utm_source=chatgpt.com)) |
| entity["organization","CrewAI","agent orchestration framework"] | Flows со flow‑state | Декоратор `@persist`, memory‑механизмы | Явный state как «каркас» flow ([docs.crewai.com](https://docs.crewai.com/en/guides/flows/mastering-flow-state?utm_source=chatgpt.com)) |

## Графовые оркестраторы и workflow‑state machines

Значимый класс проектов решает вашу задачу ( **программные переходы + персистентный state** ) через моделирование выполнения как **графа/машины состояний**, где **объект состояния** передаётся между узлами/шагами и может чекпойнтиться.

### LangGraph‑подобные графы с чекпойнтами

LangGraph позиционируется как оркестрация для долгоживущих, stateful‑агентов, и его базовый механизм “state” — это **слой персистентности**, реализованный через **checkpointers**. При настройке checkpointer сохраняет чекпойнт состояния графа на каждом “super‑step”, храня чекпойнты под концепцией “thread”, чтобы можно было получить состояние после выполнения. Это напрямую включает такие возможности, как **human-in-the-loop**, **устойчивость к сбоям (fault tolerance)** и **“time travel”** (форк от предыдущих чекпойнтов). ([github.com](https://github.com/langchain-ai/langgraph?utm_source=chatgpt.com))

Две детали особенно важны для вашего требования “`work3` создаёт состояние на первом входе и хранит его на протяжении стадии”:

- **Семантика interrupt/pause (прерывания/паузы)**: выполнение можно остановить в заданных точках, сохранить state и ждать неопределённо долго до возобновления — делая “stage gates” (ворота стадий) первоклассной конструкцией, а не набором “if”‑ов. ([docs.langchain.com](https://docs.langchain.com/oss/python/langgraph/interrupts?utm_source=chatgpt.com))  
- **Запрашиваемая история (queryable history)**: можно получить полную историю state для thread через `get_state_history`, возвращающую упорядоченные снапшоты (практически: “покажи, что происходит” как простой запрос). ([docs.langchain.com](https://docs.langchain.com/oss/python/langgraph/persistence?utm_source=chatgpt.com))  

Экосистема LangGraph всё чаще трактует “state” как то, что можно сохранять в стандартные бэкенды (например, интеграции с Redis для персистентности чекпойнтов или других внешних хранилищ). Это важно, если вы хотите, чтобы state переживал деплой и падения. ([redis.io](https://redis.io/blog/langgraph-redis-build-smarter-ai-agents-with-memory-persistence/?utm_source=chatgpt.com))

### Microsoft Agent Framework: workflow‑графы и сессии

В более новой Microsoft Agent Framework явно продвигаются **Workflows** как графовая оркестрация с **типобезопасной маршрутизацией**, **чекпойнтингом** и поддержкой human-in-the-loop. Дополнительно это сочетается с **управлением состоянием через сессии (sessions)** и наблюдаемостью. ([learn.microsoft.com](https://learn.microsoft.com/en-us/agent-framework/overview/?utm_source=chatgpt.com))

“Session” здесь очень близка к вашему “состоянию `work3`, появляющемуся при первом входе”: когда воркфлоу преобразуется в агента, фреймворк создаёт **сессию для управления состоянием разговора и чекпойнтами**, маршрутизирует входные сообщения через стартовый executor и переводит события воркфлоу в ответы агента. ([learn.microsoft.com](https://learn.microsoft.com/en-us/agent-framework/user-guide/workflows/as-agents?utm_source=chatgpt.com))

Это часть более широкого сдвига в стеке Microsoft: материалы по миграции подчёркивают, что Agent Framework центрируется вокруг типизированной, графовой модели воркфлоу по сравнению с message‑centric оркестрацией в прежних паттернах AutoGen. ([learn.microsoft.com](https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/?utm_source=chatgpt.com))

### Облачные state machines как явная оркестрация

Если вы хотите, чтобы переходы были не просто программными, но ещё и **аудируемыми и визуально обозримыми**, до сих пор актуальны облачные сервисы воркфлоу вроде AWS Step Functions. Amazon прямо описывает Step Functions как координатор для многошаговых генеративных AI‑воркфлоу (включая параллелизацию вызовов моделей и интеграцию RAG‑паттернов). ([aws.amazon.com](https://aws.amazon.com/blogs/machine-learning/orchestrate-generative-ai-workflows-with-amazon-bedrock-and-aws-step-functions/?utm_source=chatgpt.com))

В контексте “агент + процесс” это часто привлекательно, потому что Step Functions заставляет именовать состояния и переходы — создавая встроенную ясность (“на каком шаге мы?”), даже если внутренние решения агента трудно интерпретировать. ([dev.to](https://dev.to/aws-builders/beyond-chatbots-building-autonomous-multi-agent-workflows-with-amazon-bedrock-and-step-functions-472d?utm_source=chatgpt.com))

![Image](https://miro.medium.com/0%2AmKVqwu_istd7rtJv.jpg)

![Image](https://miro.medium.com/v2/resize%3Afit%3A1400/1%2AsviMdjT488Qof01H-nUu6g.png)

![Image](https://d2908q01vomqb2.cloudfront.net/1b6453892473a467d07372d45eb05abc2031647a/2022/10/27/3-3.png)

![Image](https://docs.aws.amazon.com/images/step-functions/latest/dg/images/state-machine-conceptual-jsonata.png)

## Durable execution как “слой состояния” для агентов

Второй кластер проектов подходит к вашему вопросу с другой стороны: вместо “агент‑фреймворк добавляет state” они считают, что **state — это инфраструктурный примитив**. Такие системы обычно дают durable log/history, replay, ретраи и долгоживущие pause/resume — так что агент становится участником воркфлоу, а не рантаймом‑воркфлоу.

### Temporal: детерминированные воркфлоу + replay по Event History

Модель Temporal строится вокруг **durable execution**: система добавляет события в **Event History** для отслеживания прогресса, что позволяет восстановиться после падений и продолжить выполнение, не теряя уже завершённых результатов. ([docs.temporal.io](https://docs.temporal.io/workflow-execution/event?utm_source=chatgpt.com))

Для агентных систем Temporal подчёркивает ключевую идею: при восстановлении после сбоя воркфлоу “replay‑ит” прогресс, вместо того чтобы просить LLM заново принимать прошлые решения; воркфлоу использует Event History как запись о том, что уже произошло, и может продолжить точно с места остановки. ([temporal.io](https://temporal.io/blog/of-course-you-can-build-dynamic-ai-agents-with-temporal?utm_source=chatgpt.com))

Temporal также хорошо отвечает на вашу потребность “состояние можно понять парой команд”:

- Он трактует воркфлоу как **stateful‑сервис**, который может получать сообщения (Queries, Signals, Updates), где Queries используются для чтения состояния, а Signals/Updates — для изменения поведения. ([docs.temporal.io](https://docs.temporal.io/develop/python/message-passing?utm_source=chatgpt.com))  
- Его документация и модель сообщений напрямую связывают “workflow state” с replay‑историей: результаты запросов (query) должны опираться на детерминированный replay уже выполненных шагов. ([community.temporal.io](https://community.temporal.io/t/workflow-query-can-query-worker-different-from-the-worker-executing-activity/10698?utm_source=chatgpt.com))  

Существуют и agent‑ориентированные интеграции, показывающие Temporal как практичный “state engine” для агентов. Например, PydanticAI описывает обёртку `TemporalAgent`, где I/O‑работа (запросы к модели, tool calls) выносится в activities, а детерминированный workflow‑код остаётся replay‑совместимым. ([ai.pydantic.dev](https://ai.pydantic.dev/durable_execution/temporal/?utm_source=chatgpt.com))

### Restate, DBOS, Resonate, Inngest: durable execution становится «товарным» примитивом

Заметный тренд 2024–2026 годов — появление множества платформ durable execution помимо Temporal, которые прямо позиционируются как примитивы state/transition для воркфлоу и агентов:

- **Restate** описывает durable execution как способ реализовать согласованные машины состояний, session‑state или agent context/memory; подчёркивается, что обновления state журналируются вместе с шагами выполнения и имеют область видимости по workflow/object с гарантией single‑writer. ([docs.restate.dev](https://docs.restate.dev/foundations/key-concepts?utm_source=chatgpt.com))  
- **DBOS** документирует модель воркфлоу, где прерванное выполнение восстанавливается с последнего завершённого шага, чтобы упростить надёжные фоновые задачи и AI‑агентов. ([docs.dbos.dev](https://docs.dbos.dev/python/tutorials/workflow-tutorial?utm_source=chatgpt.com))  
- **Resonate** описывает checkpoint/replay как механизм durable execution (возобновление после падения/рестарта процесса хоста). ([docs.resonatehq.io](https://docs.resonatehq.io/evaluate/how-it-works?utm_source=chatgpt.com))  
- **Inngest** продвигает “durable functions” как замену очередям/states/scheduling; многошаговые функции поддерживают ожидание (часами и даже до года), step‑ретраи и условное выполнение, а также трактуют steps как дискретные единицы, доступные для ретраев/дебага/восстановления. Также используются step IDs для мемоизации step‑state между версиями. ([github.com](https://github.com/inngest/inngest?utm_source=chatgpt.com))  

Этот класс решений напрямую совпадает с вашей интуицией: если переходы и состояние обслуживает durable execution engine, агент может быть “в курсе”, где он находится, читая авторитетный workflow‑state/history, а не реконструируя происходящее из длинных логов чата.

Реальный компромисс — ограничения, связанные с replay‑долговечностью (например, детерминированность workflow логики и аккуратная работа с недетерминированными операциями), которые обычно решаются через паттерн “вынести I/O в activities/steps”. ([docs.temporal.io](https://docs.temporal.io/encyclopedia/event-history/event-history-go?utm_source=chatgpt.com))

## Фреймворки с «встроенными» Flows/Workflows и сохраняемым контекстом

Третий кластер находится между “agent frameworks” и “workflow engines”: фреймворки, которые явно добавляют workflow‑state, персистентность и pause/resume внутрь самого фреймворка.

### LlamaIndex Workflows: `Context` как state между шагами и запусками

В LlamaIndex Workflows используется объект `Context` для хранения состояния внутри и между запусками. Документация показывает, что можно создать Context для воркфлоу, передать его в `.run()` и при необходимости сохранить/восстановить для персистентности между запусками. ([developers.llamaindex.ai](https://developers.llamaindex.ai/python/framework/understanding/agent/state/?utm_source=chatgpt.com))

Это хорошо ложится на вашу идею “state в `work3` создаётся при первом входе”: Context может быть контейнером для данных конкретной стадии, счётчиков, частичных результатов и флагов “готово/не готово”, переживающих границы шагов (и потенциально границы запусков). ([developers.llamaindex.ai](https://developers.llamaindex.ai/python/llamaagents/workflows/managing_state/?utm_source=chatgpt.com))

### CrewAI Flows: явный flow‑state + декоратор персистентности

Документация CrewAI Flows делает управление состоянием явным понятием: flow‑state описывается как “бэкбон” для сложных воркфлоу, позволяющий удерживать контекст и делиться данными между шагами. ([docs.crewai.com](https://docs.crewai.com/en/guides/flows/mastering-flow-state?utm_source=chatgpt.com))

Существенно для вашего вопроса то, что CrewAI включает явный механизм персистентности через декоратор `@persist`, который описывается как обеспечивающий автоматическое сохранение состояния между рестартами или разными исполнениями воркфлоу. ([docs.crewai.com](https://docs.crewai.com/en/concepts/flows?utm_source=chatgpt.com))

CrewAI также различает “state процесса/воркфлоу” и “memory” в классическом смысле: при включённой памяти framework автоматически извлекает факты из результатов задач, сохраняет, а затем подгружает релевантный контекст перед каждой задачей. ([docs.crewai.com](https://docs.crewai.com/en/concepts/memory?utm_source=chatgpt.com))

### AutoGen: лёгкая оркестрация, где state часто «растекается в сообщения»

Microsoft AutoGen популяризировал multi‑agent оркестрацию через message passing, но в обсуждениях проекта подчёркивается ограничение: как только вы вводите ретраи, условные ветвления или долгоживущие задачи, “контекст” расползается по обмену сообщениями и прикладному коду, а не концентрируется в одном структурированном state‑объекте. ([github.com](https://github.com/microsoft/autogen/discussions/7144?utm_source=chatgpt.com))

Это ровно та причина, по которой многие команды переходят на графовые/state‑machine модели (в стиле LangGraph или Agent Framework), когда важны программные переходы и надёжный чекпойнтинг. ([learn.microsoft.com](https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/?utm_source=chatgpt.com))

### OpenAI Swarm: обучает handoffs, но не даёт durable state

Репозиторий OpenAI Swarm заявляет цель как лёгкую, управляемую и тестируемую координацию через Agents и handoffs. ([github.com](https://github.com/openai/swarm?utm_source=chatgpt.com))  
Однако в обсуждениях сообщества про Swarm прямо отмечается, что он практически целиком client‑side и не хранит персистентное состояние между вызовами, что подчёркивает: Swarm в первую очередь образовательный, а не “state engine”. ([community.openai.com](https://community.openai.com/t/openai-swarm-for-agents-and-agent-handoffs/976579?utm_source=chatgpt.com))

## Code‑агенты и Git/PR как «состояния работы», отображаемые на ветки и pull request

Ваше “`work3` → merge в `main` → удалить `work3`” естественно ложится и на **developer‑ориентированных агентов**, где Git становится первоклассной “машиной артефактного состояния”.

### GitHub‑нативные агенты и PR‑воркфлоу

Документация GitHub для coding agent описывает сценарий, где агент создаёт новую ветку от базовой ветки, затем пушит изменения в pull request, направленный на эту ветку. ([docs.github.com](https://docs.github.com/copilot/using-github-copilot/coding-agent/asking-copilot-to-create-a-pull-request?utm_source=chatgpt.com))  
В блоге GitHub это позиционируется как работа “напрямую внутри pull request workflow”, где агент автоматизирует создание ветки, коммитов и ревью, и действия остаются залогированными и видимыми — то есть выполнение агента экстернализируется в артефакт (PR) на границе между “в процессе” и “готово”. ([github.blog](https://github.blog/ai-and-ml/github-copilot/github-copilot-coding-agent-101-getting-started-with-agentic-workflows-on-github/?utm_source=chatgpt.com))

### OpenHands и класс инструментов SWE-agent

OpenHands даёт гайды по GitHub‑воркфлоу (например, для автоматизации PR‑review). Примеры GitHub‑воркфлоу явно опираются на разрешения GitHub Actions, позволяющие создавать и approve pull requests — превращая PR в границу между “work in progress” и “ready to merge”. ([docs.openhands.dev](https://docs.openhands.dev/sdk/guides/github-workflows/pr-review?utm_source=chatgpt.com))

SWE-agent аналогично фокусируется на том, чтобы взять issue и сформировать pull request; даже в демонстрационных пайплайнах “inference” создаёт PR, а дальнейшие шаги его оценивают. ([github.com](https://github.com/SWE-agent/SWE-agent?utm_source=chatgpt.com))  
Также материалы AWS документируют “remote SWE agents”, которые автономно создают pull requests — демонстрируя, насколько распространённым стал паттерн “ветка/PR как state”. ([github.com](https://github.com/aws-samples/remote-swe-agents?utm_source=chatgpt.com))

### Стратегии ветвления для параллельных агентов

Некоторые вендоры теперь документируют явные branching‑стратегии для параллельной агентной работы: например, “скользящая” интеграционная ветка с подветками на каждого агента, затем PR в интеграционную ветку перед merge в main — что снова отражает staged‑работу как Git‑нативный процесс. ([tessl.io](https://tessl.io/blog/use-automated-parallel-ai-agents-for-massive-refactors/?utm_source=chatgpt.com))

## Конкретный архитектурный паттерн для “work3 state → merge → cleanup”

Ниже — паттерн реализации, который повторяется в проектах выше, в терминах вашего примера. Ключевая идея: **агент не должен “угадывать” переходы**. Переходы — это **описанное кодом** правило, а состояние хранится в системе, созданной для возобновляемости и аудитируемости.

### Определяйте state как типизированный объект, а не как «неявный контекст»

В графовых/state‑machine‑оркестраторах “work3 state” — это структурированный объект, который несут между steps (nodes/executors) и чекпойнтят. Модель персистентности LangGraph строится вокруг чекпойнтинга состояния графа по `thread`, а паттерны “time travel” явно опираются на получение checkpoint и state history по `thread_id`. ([docs.langchain.com](https://docs.langchain.com/oss/python/langgraph/persistence?utm_source=chatgpt.com))  
Microsoft Agent Framework подчёркивает типобезопасность и валидацию в воркфлоу — по сути это та же рекомендация: переходы должны переносить типизированные сообщения/состояние по ребрам графа, а не “свободные” blobs. ([learn.microsoft.com](https://learn.microsoft.com/en-us/agent-framework/workflows/?utm_source=chatgpt.com))

### Сделайте “первый вход создаёт state” явным переходом (шагом инициализации)

Практически это означает моделировать “войти в `work3`” как переход, который:

1. Создаёт workflow session/thread (или использует существующий).
2. Инициализирует `work3`‑поля в state (например, имя ветки, baseline commit SHA, критерии приемки).
3. Фиксирует переход в истории (чекпойнт или event log).

Это естественно для checkpointed state graphs (чекпойнт на вход/выход узла) ([docs.langchain.com](https://docs.langchain.com/oss/python/langgraph/persistence?utm_source=chatgpt.com)) и для durable execution engines (добавить событие/журналируемый шаг, который становится replay‑истиной). ([docs.temporal.io](https://docs.temporal.io/workflow-execution/event?utm_source=chatgpt.com))

### Дайте “статус за две команды” через state/history queries, а не через разбор логов

Есть два устойчивых механизма:

- **Список истории чекпойнтов** (графовые системы): LangGraph предоставляет `get_state_history` для получения снапшотов по thread, а схемы “time travel” используют эту историю, чтобы находить checkpoint IDs. ([docs.langchain.com](https://docs.langchain.com/oss/python/langgraph/persistence?utm_source=chatgpt.com))  
- **Запросы к workflow‑состоянию** (durable engines): Temporal трактует воркфлоу как stateful‑сервис с Queries/Signals/Updates и хранит Event History как авторитетную запись для replay и реконструкции состояния. ([docs.temporal.io](https://docs.temporal.io/develop/python/message-passing?utm_source=chatgpt.com))  

Иными словами, “статус” должен быть query‑эндпоинтом поверх авторитетного state (плюс, опционально, короткое резюме из последних чекпойнтов/событий), а не LLM‑промптом, который заново интерпретирует сырой лог.

### Гейтите merge/cleanup охранными условиями (guard conditions) и, при необходимости, человеческим подтверждением

Если “merge в `main`” — это переход, он должен быть защищён проверками (тесты прошли, линтер прошёл, критерии приемки выполнены). В durable engines типичный паттерн — останавливать воркфлоу для human approval и затем возобновлять строго с точки остановки; в материалах Temporal pause/resume для human-in-the-loop обсуждается как первоклассная практика. ([temporal.io](https://temporal.io/blog/build-resilient-agentic-ai-with-temporal?utm_source=chatgpt.com))

Далее “cleanup” (удаление ветки/рабочего пространства) становится финальным переходом, который фиксируется, чтобы система могла доказать, что он произошёл (или безопасно ретраить его). Этот принцип “фиксировать переходы так, чтобы их можно было однозначно ретраить” — одна из причин существования durable execution logs. ([docs.temporal.io](https://docs.temporal.io/workflow-execution/event?utm_source=chatgpt.com))

## Безопасность и пробелы исследований

### Примечание по безопасности: персистентный state часто включает учётные данные и authority инструментов

Поскольку state агента может содержать API keys, auth tokens, полномочия инструментов и контекст локального выполнения, команды безопасности всё чаще трактуют агентные деплои как высокорисковую поверхность атаки. CrowdStrike, например, описывает развёртывания OpenClaw как новую поверхность атаки, требующую видимости в процесс выполнения и использование инструментов; другие материалы подчёркивают корпоративные запреты из‑за киберрисков. ([crowdstrike.com](https://www.crowdstrike.com/en-us/blog/what-security-teams-need-to-know-about-openclaw-ai-super-agent/?utm_source=chatgpt.com))  
Это важно для дизайна: “state” — не только удобство, но и чувствительные данные, которые нужно защищать при персистентном хранении.

### Открытые пробелы и активные направления исследований

Несмотря на множество инженерных решений, остаются пробелы — особенно вокруг агентов, которые **программно** понимают и соблюдают переходы.

Один живой исследовательский трек — **автоматическая генерация машин состояний для multi‑agent систем**. ICML 2025 poster “MetaAgent” предлагает строить multi‑agent системы на основе конечных автоматов (finite state machines), где FSM управляет действиями и переходами, и заявляет улучшения по сравнению с другими методами автоматического дизайна. ([openreview.net](https://openreview.net/forum?id=vOxaD3hhPt&noteId=riY7ty98U1&utm_source=chatgpt.com))

На системной стороне появляются работы про **рантаймы обслуживания агентов**, которые отделяют спецификацию воркфлоу от исполнения и предоставляют управляемые state‑слои. Например, работа 2026 года “Nalar” описывает serving‑фреймворк с managed state layer, который отделяет логическое состояние от физического размещения и поддерживает безопасное переиспользование/миграцию и согласованное поведение ретраев — по сути формализуя “state как сервис рантайма”. ([arxiv.org](https://arxiv.org/abs/2601.05109?utm_source=chatgpt.com))

Ещё один тренд — **ограничения воспроизводимости**: в воркфлоу‑интенсивных доменах исследователи продвигают структурированные схемы действий, детерминированные политики выполнения и трекинг происхождения (provenance), чтобы сделать действия аудируемыми и replay‑проверяемыми (например, R‑LAM). ([arxiv.org](https://arxiv.org/abs/2601.09749?utm_source=chatgpt.com))

Наконец, durable workflows создают постоянное инженерное напряжение, напрямую относящееся к вашему требованию “агент помнит `work3`”: replay‑долговечность навязывает ограничения на детерминизм/иммутабельность и требует аккуратно обрабатывать недетерминированные операции (LLM calls, HTTP, randomness). Платформы durable execution подробно описывают эти ограничения и рекомендуют разделять workflow‑логику и side‑effect‑шаги (activities/steps), чтобы сохранить replay‑совместимость. ([docs.restate.dev](https://docs.restate.dev/develop/java/durable-steps?utm_source=chatgpt.com))

**Глоссарий терминов (перевод — оригинал):**

- Воркфлоу / рабочий процесс — workflow  
- Чекпойнт / контрольная точка — checkpoint  
- Устойчивое (долговечное) выполнение — durable execution  
- История событий — event history  
- Сессия — session  
- Тред — thread  
- Контекст — context  
- Артефактное состояние — artifact state  
- Человек‑в‑контуре — human-in-the-loop  
- Охранные условия — guard conditions