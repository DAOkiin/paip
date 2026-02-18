# Исследование решений для парсинга

#### You:
я хочу запустить сервис для парсинга сайтов и различных источников информации

думаю что нужно сделать в формате пайплайнов данных

у меня будет потребность добавлять туда различные источники информации, вообще любые. веб, RSS, телеграмм, что угодно

наверное они должны быть в виде адаптеров

я хочу чтобы ты сделал исследование существующих решений

мне важно чтобы это был опенсорс, обязательно Пайтон и очень желательно чтобы была связка с temporal

#### ChatGPT:
Чтобы провести исследование максимально точно, уточни, пожалуйста:

1. Какие типы данных или контента ты собираешься парсить (текстовые статьи, видео, файлы и пр.)?
2. Нужно ли поддерживать скрапинг защищённых/авторизованных источников?
3. Какие требования к масштабируемости и отказоустойчивости?
4. Нужна ли интеграция с брокерами сообщений (Kafka, RabbitMQ и пр.)?
5. Нужно ли рассмотреть только решения, которые уже используют Temporal, или достаточно тех, которые можно с ним интегрировать?

Как только уточнишь эти моменты, я начну исследование.


#### You:
вначале только веб, может быть RSS, но далее я буду писать адаптеры для Ютуба, твиттера и любого вида контента 

из коробки защищённые источники не обязательны

требований к масштабируемости нет, но желательно минимальный оверхед на запуск задач 

брокеры не важны

желательно чтобы Temporal уже использовался или мог быть легко встроен в процесс

только опенсорс и только пайтон 

#### ChatGPT:
Отлично. Я подберу опенсорсные Python-решения для построения пайплайнов сбора и парсинга данных с разных источников (веб, RSS, YouTube, Twitter и т.д.), с акцентом на:

- Поддержку или лёгкую интеграцию с Temporal
- Низкий оверхед при запуске задач
- Расширяемость через адаптеры для новых источников
- Python-кодовую базу и активное сообщество

Я изучу библиотеки, фреймворки и готовые проекты, которые могут стать ядром или компонентами твоего сервиса. Вернусь с обзором и сравнением подходящих вариантов.


#### ChatGPT:
# Service for Multi-Source Parsing – Open-Source Python Solutions

## 1. Web Scraping & Crawling Frameworks (Python)

**Scrapy:** The most popular open-source Python framework for web crawling and scraping【24†L19-L27】. Scrapy lets you build *spiders* to fetch webpages and extract data. It’s fast, powerful, and highly customizable【24†L39-L47】. You write Python code to define how to navigate sites and parse content, and Scrapy handles the crawling, requests, throttling, and pipelines for data processing【25†L78-L86】【24†L41-L49】. Scrapy is well-maintained (used by a large community) and suitable for parsing HTML from websites. It doesn’t natively cover RSS or APIs, but you can easily extend it – e.g. use Python’s **feedparser** for RSS feeds within a spider, or call external APIs in parsing logic. New data sources (like different websites) are added by creating new spider classes (in essence, *adapters* for each site). Scrapy has minimal runtime overhead – you can run it on-demand or schedule spiders periodically. While Scrapy doesn’t integrate with Temporal out-of-the-box, you **can** orchestrate Scrapy crawls via external means (for example, invoking `scrapy crawl` from a Temporal activity or scheduling spiders through a Temporal workflow). The lack of native Temporal support means you’d build the glue code, but Scrapy’s robust crawling engine could serve as the data extraction component in a Temporal-managed pipeline.

**Pyspider:** An older but notable open-source Python crawling system with a rich feature set. Pyspider provides a *web UI* for writing and managing crawl scripts, monitoring tasks, and viewing results【27†L47-L55】. It supports multiple databases (MySQL, MongoDB, etc.) and message queues (RabbitMQ, Redis, etc.) for storing data and coordinating tasks【27†L51-L59】. Notably, Pyspider has built-in scheduling: you can mark functions with decorators like `@every(minutes=...)` to run them periodically【27†L73-L81】. It handles task priorities, retries, and even distribution across multiple crawlers【28†L323-L331】【28†L329-L337】. Pyspider can fetch JavaScript-heavy pages (it had support for PhantomJS rendering) and is designed as an all-in-one web scraping service. This means you could potentially ingest web pages and feeds by writing scripts via its UI, and it will handle recurring fetches. However, Pyspider’s development has slowed (last major commits a few years ago), so while it’s **open-source (Apache 2.0)** and still usable (17k+ GitHub stars attesting to its popularity)【28†L176-L184】【28†L320-L329】, you should be mindful of maintenance. Pyspider doesn’t natively know about Temporal, and integrating the two might be complex – Pyspider has its own scheduler and task system. If you prefer Temporal’s reliability, you might instead treat Pyspider as a self-contained service and trigger its API from Temporal workflows. But running Temporal **and** Pyspider might be overkill; they have overlapping responsibilities (both can schedule and retry tasks). In summary, Scrapy or Pyspider are great for web content parsing, with Scrapy being lightweight and code-centric, and Pyspider offering a UI and built-in scheduling.

## 2. Ingestion Frameworks for Various Sources (APIs, Feeds, etc.)

Beyond raw web crawling, there are open-source **data ingestion frameworks** that come with pre-built connectors (adapters) for many sources like APIs, databases, or cloud services. These can save time, especially for sources like YouTube or Twitter where official APIs exist.

**Airbyte (and Airbridge):** Airbyte is an open-source EL(T) platform with hundreds of connectors. Many Airbyte **source connectors** are implemented in Python (following a standard interface), and they cover things like the YouTube Data API, Twitter API, RSS feeds, etc. For example, Airbyte provides a ready YouTube Data API connector【33†L7-L15】 and a Twitter connector【33†L0-L8】. Airbyte typically runs as a standalone service (with a web UI and a scheduler), which might be heavy if you only need a simple pipeline. However, an interesting project called **Airbridge** by OpenBridge wraps Airbyte’s connectors in a more lightweight way. Airbridge orchestrates Airbyte connectors using Python and Docker, allowing you to run pipelines with any of Airbyte’s \~200+ source connectors in your own environment【20†L161-L169】. Essentially, you configure a source (e.g. Twitter API credentials, YouTube API key) and a destination (perhaps a database or file), and Airbridge/Airbyte will handle pulling the data and loading it. This is fully open-source (MIT license for Airbridge)【20†L199-L207】. The downside is the overhead: each connector may run in its own Docker container. If you don’t need a fancy UI, you could invoke these connectors programmatically (Airbyte has an API/CLI), potentially under Temporal’s orchestration (i.e. a Temporal workflow could start an Airbyte sync job and wait for completion). But integrating Temporal here might be non-trivial unless you treat the Airbyte sync as an activity executed externally. If minimal overhead is key and you prefer not to run a heavy service, Airbyte might be more than you need initially.

**Singer & Meltano:** Singer is a specification for data pipeline *taps* (extractors) and *targets* (loaders). There are many open-source Singer **taps** in Python for sources like Twitter, Google Analytics, databases, etc. Meltano is an open-source tool that coordinates Singer taps/targets. For instance, you might use a Singer *tap-twitter* to pull data from Twitter and a Singer *target-sqlite* to store it. Meltano can schedule and run these pipelines via CLI or even integrate with orchestrators like Airflow. All of this is Python-based and open source. The advantage is a rich ecosystem of connectors; the challenge is that Singer taps output data as streams of JSON, which you’d then load somewhere – it’s more of an ETL building block than a ready service. Meltano itself doesn’t incorporate Temporal (it historically used Airflow for scheduling, though newer versions have other options). You could run Meltano CLI commands from Temporal if needed. Again, this might be more moving parts than desired for a simple setup.

**dlt (Data Load Tool by dlt-hub):** A newer open-source Python library, **dlt**, offers a very lightweight way to build data pipelines for various sources. It’s essentially a Python SDK that simplifies extracting data from APIs or other sources and loading it to destinations (like databases or files) with minimal boilerplate【32†L367-L375】. You write normal Python code – e.g., use `requests` or an API client – and hand the data (even messy JSON) to dlt. The library will handle *schema inference, normalization,* and saving to your target (it supports many destinations from DuckDB and Postgres to BigQuery)【32†L374-L382】. For example, you could write a small function to fetch new videos from a YouTube channel via the YouTube API, then call `dlt.pipeline(...).run(data)` to load it into a database or even just keep it in memory. dlt includes conveniences for incremental loads and supports running in various environments (it can be embedded in Airflow or run in a simple script)【32†L389-L397】. Because it’s just Python code, it’s easy to integrate with anything – including Temporal. You could have a Temporal workflow that calls a dlt pipeline function as an activity. Since dlt is relatively lightweight (no always-on server; it runs within your Python process), the overhead is minimal. This might be a great option for building **adapters** for new sources: you get a lot of ETL plumbing done for you (error handling, data typing, etc.) while you focus on calling the source API or parsing data. dlt is fully open-source (MIT) and Python-native【32†L313-L321】. It doesn’t (currently) have built-in Temporal integration, but using it in a Temporal activity is straightforward.

## 3. Workflow Orchestration Engines (for Pipelines)

To manage the *pipeline* aspect – scheduling runs, coordinating multiple steps, and ensuring reliability – **workflow orchestrators** come into play. You specifically mentioned **Temporal**, which is an excellent choice for a durable, code-first orchestrator. Temporal is an open-source workflow engine that allows you to write workflows as code (with a Python SDK available) and it handles scheduling, retries, state tracking, and fault tolerance for you【29†L279-L287】. Temporal’s Python SDK lets you define *Workflows* and *Activities* in pure Python. In your case, an activity might be “fetch data from source X” (e.g. run a web scraper or call an API), another activity could be “process/normalize data” and perhaps another to store or forward the data. The Temporal **workflow** function can orchestrate these calls sequentially or in parallel as needed【29†L279-L287】. A big advantage of Temporal is reliability: if your parsing task fails or the worker crashes, Temporal will transparently retry the activity (according to the retry policy you set)【29†L289-L298】. It can also schedule workflows on a timer (Cron/interval schedules) using its built-in scheduling capabilities【29†L289-L298】, which sounds ideal for periodically parsing feeds or websites.

One thing to note: Temporal does require running a **Temporal server** (either self-hosted or Temporal Cloud). For development you can run a local all-in-one Temporal service, but in production you’d likely run it as a service with a persistence store. This is some overhead, but it’s a one-time setup that then provides a lot of functionality (it replaces the need for a separate message broker, scheduler, cron, etc., since Temporal’s service handles those concerns). Many find that the benefits for long-running, reliable workflows outweigh the initial setup. Temporal is designed for microservice orchestration at scale, but there’s no harm using it for small-scale pipelines too – it will ensure each parse job runs *exactly once or is retried until success* in the face of failures【29†L279-L287】.

**Integration with Temporal:** Currently, few off-the-shelf scraping or ETL tools come pre-integrated with Temporal (Temporal is relatively new in the Python space). However, integrating is usually about calling one from the other. For example, you can call Scrapy by invoking a `CrawlerProcess` in a Temporal activity, or run a Singer tap via subprocess in an activity. Because Temporal workflows are just code, you have a lot of freedom. There has even been a demo of a **“Temporal scraper”** which shows using Temporal to orchestrate a web scraping job in Python【5†L6-L8】 – it’s not a full framework, just an example repository, but it validates that this approach works. In general, you might not find a turnkey solution that *already* has Temporal baked in (aside from more niche projects or internal examples). Instead, you would choose a scraping/data tool and use Temporal to glue them together.

**Other Orchestrators:** For completeness, other open-source Python orchestrators include **Apache Airflow**, **Prefect**, and **Dagster**. Airflow is very mature for scheduling and running tasks but is heavy-weight (it requires a metadata DB, a scheduler, webserver, etc.) and oriented around DAGs of tasks. If you didn’t have the Temporal requirement, Airflow could schedule web scrapers or API pulls (it even has some operators/hooks for common sources). Prefect is a more lightweight Python-native workflow tool (no centralized DB by default, and allows defining flows in code). Dagster is another modern orchestrator with a focus on data assets. All are Python-based and open source to varying degrees. However, since you specifically prefer Temporal, it likely means you value its **durable execution** model (which ensures stateful long-running workflows and easy retries). Temporal contrasts with Airflow by being code-first and highly fault-tolerant – some categorize Temporal as a “data-centric” or event-driven orchestrator where workflows are more dynamic and stateful【38†L163-L171】. Given no strong scalability requirements now and a desire for low overhead, you might also consider **Prefect** as an alternative if Temporal integration proves too much – Prefect can run a simple agent process and orchestrate Python functions on a schedule, with less infra than Airflow. But Prefect would be a plan B if, for some reason, Temporal’s model doesn’t fit, since your preference is clearly Temporal.

## 4. Recommendations and Putting It All Together

You have a few paths to build your parsing service, depending on how much existing infrastructure you want to leverage vs building custom:

- **Using Scrapy (or Pyspider) with Temporal:** You can use Scrapy for the actual data fetching/parsing from websites (and feedparser or custom code for RSS). Scrapy’s output (items) could be handled in an item pipeline or returned to your code. You could wrap the invocation of each spider in a Temporal activity. For example, a Temporal workflow triggers the “crawl website X” activity, which runs a Scrapy spider and returns the scraped data (or writes it to a DB). Then the workflow could trigger the next source, etc., or run them in parallel as separate activities. Temporal would manage scheduling these workflows periodically (say one workflow per source type on a cron schedule). This approach gives you battle-tested scraping and Temporal’s reliability. The trade-off is you’ll need to write some integration code (to call Scrapy programmatically) and run both a Scrapy environment and the Temporal worker.

- **Using a Connector/ETL Library with Temporal:** For sources that have APIs (YouTube, Twitter, etc.), using something like **dlt** or Singer connectors could speed up development. You could implement each new source as a small Python function (adapter) that uses dlt or a Singer tap to pull data. Then call that function in a Temporal activity. For example, an activity “fetch\_latest\_tweets” might internally use a Singer tap for Twitter or a dlt pipeline for Twitter API – either way, it hides the details and just yields data. This would be very plugin-friendly: each new source = new function + maybe a config file for API keys. Temporal can orchestrate calling all these on whatever schedule or trigger you need. This design keeps overhead low (no heavy always-running service for data collection; Temporal workers execute the code on schedule).

- **Standalone Ingestion Service without Temporal (for now):** Since you mentioned Temporal is “very desirable” but not strictly mandatory, note that a tool like **Pyspider** alone could handle scheduling and crawling without an external orchestrator. Similarly, Airbyte/Airbridge could schedule data pulls on their own. If you needed to get something running quickly, you could start with one of those and perhaps integrate Temporal later for additional reliability or complex workflows. For instance, Pyspider could regularly crawl a set of sites (web and RSS) as configured in its UI. However, you’d lose out on Temporal’s exactly-once and fail-safe execution guarantees, and you’d be running a service that might not easily extend to non-web sources (Pyspider is mainly web).

Considering all factors (open source, Python, Temporal integration, minimal overhead), a **hybrid approach** seems promising: **Use Temporal as the backbone** (scheduling & orchestration) and implement source-specific parsing in Python modules that Temporal calls. For web pages, that module can leverage Scrapy or even simple `requests + BeautifulSoup` if the pages are simple. For RSS feeds, it might directly use a feed parser library. For APIs like Twitter/YouTube, it can use their Python SDKs or a tool like dlt to simplify handling authentication/pagination and so on. This way, your system is modular – each adapter is just Python code – and Temporal ties them together into a cohesive pipeline with error handling and retry. Indeed, Temporal’s documentation emphasizes building data pipelines as code and letting Temporal ensure each step runs reliably【29†L279-L287】【29†L285-L293】.

**Open-Source Example:** The “Build a Data Pipeline with Temporal” tutorial (Temporal’s Python SDK example) is a great reference. It shows how to create a workflow that pulls data from a source (in their case, Hacker News API) and processes it, with automatic retries if the source is down【29†L285-L293】. This demonstrates the exact scenario you’re targeting: multiple data sources, periodic execution, and the ability to withstand failures gracefully. Temporal handles the cron-scheduling and makes sure no data pull is missed even if workers restart【29†L289-L298】.

In summary, **existing solutions** you might draw on include:

- *Scrapy* for web scraping needs (open source, Python)【25†L78-L86】,
- *Pyspider* for a web UI and scheduling of crawls if needed【28†L323-L331】,
- *Airbyte/Airbridge or Singer/Meltano* for an expansive set of ready connectors (particularly for non-HTML sources)【20†L165-L173】,
- *dlt (Data Load Tool)* for a lightweight Pythonic pipeline development【32†L374-L382】,
- and *Temporal* itself as the orchestration engine to glue these together reliably.

No single turnkey project currently does “crawl web, RSS, YouTube, Twitter *and* uses Temporal” out of the box – you will likely end up combining pieces. The good news is all the pieces you want are available as open source and Python-based. The integration with Temporal is “easy” in the sense of no technical blockers (Temporal can call any Python code), but it will be up to you to wire it up. Given that Temporal is a key interest, going with its workflow approach from the start is wise – it will provide a solid foundation that scales as you add more sources or need more complex pipelines.

**Sources:**

- Scrapy – open source web crawling framework (Python)【25†L78-L86】【24†L41-L49】
- Pyspider – Python web crawler system with UI, supports scheduling and multiple backends【28†L323-L331】【28†L329-L337】
- Airbridge (Airbyte connectors) – 200+ data source connectors in open source Python/Docker【20†L161-L169】
- dlt (Data Load Tool) – open-source Python library for loading data from various sources (APIs, etc.)【32†L374-L382】【32†L383-L392】
- Temporal Python SDK – enables durable, scheduled workflows for data pipelines【29†L279-L287】【29†L285-L293】


#### You:
Изучи статьи на Medium или каких-то других ресурсах, например, dev.to, которые описывают архитектуру системы для сбора информации, в которой используют Temporal и какие-то другие парсеры. Важно, чтобы это всё было на Python.

#### ChatGPT:
Подтверди, пожалуйста, следующие уточнения для поиска статей:

1. Тебя интересуют **архитектурные статьи** (блогпосты, кейс-стади) на Medium, dev.to и аналогичных ресурсах.
2. Обязательное условие — проект написан на **Python**.
3. В архитектуре должен использоваться **Temporal**.
4. Также должно быть упоминание или использование **парсинга / сбора / агрегации информации** (например, веб-скрапинг, API, RSS и пр.).

Могу ли я также включать статьи, где Temporal используется не только как оркестратор, но и для более широких пайплайнов данных (например, извлечение + трансформация данных)?


#### You:
Всё верно, приступай.

#### ChatGPT:
Отлично, я найду архитектурные статьи и кейс-стади (на Medium, dev.to и аналогичных платформах), где описываются системы сбора информации, использующие Temporal и написанные на Python. Буду обращать внимание на статьи, в которых Temporal применяется как оркестратор для парсинга, извлечения или агрегации данных с разных источников. Вернусь с подборкой материалов и краткими аннотациями к каждой статье.


#### ChatGPT:
# Системы сбора данных на Python с оркестрацией Temporal

## Найденные публикации и их ключевые идеи

1. **Scraping websites with Temporal** (Aurelien Cluzeau). *Личный блог, 2023-04-06*. В этом посте разобрана архитектура простого веб-скрейпера на Python с использованием Temporal. Приведен пример workflow, который последовательно выполняет этапы: загрузка HTML страницы, парсинг заголовка и ссылок, сохранение результата в JSON-файл【5†L45-L53】【5†L121-L129】. Код демонстрирует, как пометить функции как Temporal-workflow и activities, и выполнить их с автоматическими таймаутами и ретраями.\
   **Ключевые идеи и архитектурные элементы:**
   - **Декомпозиция на workflow и активности:** Сбор данных разбит на отдельные *активности* – функции для загрузки страницы, парсинга и сохранения. Workflow orchestrator вызывает их последовательно, обеспечивая детерминированность и автоматические повторные попытки при неудачах【5†L121-L129】. Такой подход упрощает отладку и повторное использование шагов.
   - **Расширяемость через дочерние workflow:** Предлагается улучшение – запускать отдельные *child-workflow* для каждой найденной ссылки (например, рекурсивный обход сайта)【7†L363-L370】. Temporal позволяет порождать дочерние процессы, которые можно отменять вместе с родительским, что полезно для параллельного скрейпинга и контроля глубины обхода.
   - **Управление и контроль выполнения:** Использование *сигналов* Temporal для динамического управления процессом – например, возможность приостановить, возобновить или остановить длительный сбор данных по внешнему сигналу【7†L371-L379】. Также отмечена необходимость соблюдать `robots.txt` и реализовать справедливость сканирования (ограничивать частоту запросов), что можно встроить в логику workflow【7†L365-L373】. Эти элементы повышают надежность и этичность веб-скрейпинга.

2. **A Story of a Million Rows: Building a Lightweight Batch Pipeline with Temporal and DuckDB** (Tal Wanish, Riskified Tech @ Medium, май 2025). Статья описывает реальный кейс обработки данных: необходимо выполнить операцию для миллионов записей (каждая запись запускает сетевой вызов) и обеспечить масштабируемость без сложных фреймворков. Предложенное решение – реализовать конвейер обработки на Temporal (с использованием Python SDK) вместо Apache Spark【21†L55-L64】. Workflow разбит на многоуровневую структуру: главный workflow читает список файлов на S3 и разбивает набор данных на части, для каждой части порождает *child workflow* (Partition Workflow), которые, в свою очередь, параллельно запускают мелкие *Batch-Workflow* на заданное число записей【22†L99-L108】. Такой “скользящий окна” подход ограничивает число одновременных batch-задач и позволяет обрабатывать большие объемы данных эффективно.\
   **Ключевые идеи и архитектурные элементы:**
   - **Иерархия workflow для параллелизма:** Главный workflow порождает дочерние workflows для каждой партии данных, а те — вложенные workflows для пакета записей. Все batch-workflows выполняются параллельно (с ограничением по окну), пока главный процесс ждет их завершения【22†L99-L108】【22†L105-L113】. Эта архитектура позволяет эффективно распараллелить обработку миллионов рядов без перегрузки памяти.
   - **Гибкое ограничение конкуренции:** Используется шаблон *sliding window* – одновременный запуск ограниченного числа Batch-workflow на каждой партиции【22†L105-L113】. Конфигурация размера пакета и окна позволяет настроить баланс между параллелизмом и нагрузкой на внешние сервисы (например, не посылать слишком много запросов сразу).
   - **Изоляция внешних вызовов и надежность:** Каждая существенная операция (чтение Parquet-файла, обработка записи, gRPC вызов внешнего сервиса) выполняется в активности, которая автоматически ретраится при сбоях. Temporal гарантирует, что сбой на середине процесса не заставит перезапускать всё с нуля – упавший workflow можно продолжить с места сбоя без потери состояния【22†L141-L149】【22†L175-L183】. Это обеспечивает устойчивость долгих ETL-процессов.
   - **Наглядность и тестируемость:** Автор отмечает, что благодаря Temporal стало проще отслеживать прогресс и отлаживать пайплайн. Есть упоминание о возможности локально симулировать внешние системы (фейковый gRPC-сервис, эмуляция S3 через `moto`) и использовать встроенный Temporal dev-сервер для интеграционного теста, что подтверждает удобство разработки и тестирования таких workflows【22†L141-L149】【22†L175-L183】.

3. **Temporal + AI Agents: The Missing Piece for Production-Ready Agentic Systems** (Akash Thakur @ dev.to, ноябрь 2025). Статья объясняет основы Temporal и показывает, как он применяется для оркестрации сложных мног шаговых процессов на Python, на примере сценария “интеллектуального агента” (автоматизированный трейдинг, анализ данных и пр.). Рассматриваются базовые понятия Temporal (Workflows, Activities, Workers) и демонстрируется, как **workflow-as-code** упрощает управление длительными задачами в сравнении с традиционными очередями【18†L55-L63】【18†L69-L77】. Приведены шаблоны построения пайплайнов: последовательное выполнение шагов и параллельное, с примерами кода и обсуждением, в каких случаях применять каждый подход.\
   **Ключевые идеи и архитектурные элементы:**
   - **Workflow как долговыполняющий сценарий:** Temporal позволяет описать бизнес-логику pipeline в виде обычной функции Python, которая может выполняться *сколь угодно долго* (даже дни/месяцы) с сохранением своего состояния. В статье подчеркивается, что Workflow код работает так, *как будто сбоев не существует*, благодаря тому что Temporal на уровне движка сохраняет историю выполнения и перезапускает функции после сбоев автоматически【18†L55-L63】【18†L69-L77】.
   - **Activities для внешних операций:** Каждый шаг, взаимодействующий с внешними системами (API, базы данных, сервисы), выносится в отдельную *Activity*. Активности запускаются из workflow и выполняются в рабочих процессах, изолированных от основного потока, с поддержкой авто-ретраев, таймаутов и отмены【18†L119-L128】【18†L131-L139】. В примере показывается activity `fetch_market_data_activity`, которая делает HTTP-запрос к внешнему API и автоматически повторяется Temporal'ом при неудаче【18†L131-L139】【18†L141-L149】. Это гарантирует надежность каждого шага сбора данных.
   - **Последовательные vs. параллельные пайплайны:** Автор демонстрирует два распространенных паттерна. *Последовательный workflow* — когда шаги строго зависят друг от друга и выполняются по цепочке (пример: получить биржевые данные -> провести технический анализ -> оценить риск -> выполнить сделку)【10†L221-L230】【10†L236-L244】. Такой линейный пайплайн проще отлаживать, но длительность равна сумме всех шагов. *Параллельный workflow* — независимые операции выполняются одновременно (например, параллельно запросить данные из нескольких источников) для ускорения результата【10†L276-L284】【10†L289-L297】. Temporal упрощает оба варианта: в коде можно `await` несколько activity-фьючей или запускать дочерние workflows, достигая параллелизма.
   - **Управление отказами и временем:** Показано использование встроенных политик ретраев и таймаутов. Например, в коде workflow задан `RetryPolicy` с экспоненциальным бэкоффом и лимитом попыток для критичного шага【10†L103-L111】. Temporal берет на себя логику повторных запусков неудачных задач, а разработчик может настроить параметры (интервал, число попыток). Также доступны возможности *cron-запуска* или отложенного старта workflows, что полезно для расписаний. Эти механизмы делают сбор данных устойчивым к временным сбоям сервисов.

4. **I built the same pipeline twice – Temporal and Prefect in comparison** (Jarosław Jaszczuk @ CodiLime Blog, январь 2026). В этой статье сравниваются два подхода к оркестрации на Python – Temporal и Prefect – на одном примере: реализован простой файлообрабатывающий конвейер. Сценарий: пользователь загружает файл, он сохраняется локально, после чего оркестратор запускает цепочку задач: определить тип файла, загрузить его копию в облачное хранилище (AWS S3), записать метаданные в базу данных, затем **в зависимости от типа файла** выполнить соответствующий анализ (распознавание текста для документов, анализ изображения или транскрипция аудио), после чего обновить запись в БД результатами, удалить локальный файл и отправить уведомление о готовности【31†L125-L133】【31†L139-L147】. Автор сначала показывает чистую реализацию этих шагов на Python, а затем описывает, как она оборачивается в Temporal Workflow.\
   **Ключевые идеи и архитектурные элементы:**
   - **Workflow код как есть:** Temporal позволяет взять последовательность операций, написанную на Python, и превратить её в надежный workflow практически без изменения самой логики【31†L125-L133】【31†L179-L187】. Все шаги (I/O операции с файлом, S3, БД, внешние API для анализа) становятся активностями, а Temporal обеспечивает, что каждый шаг будет выполнен, даже если процесс упадет на середине. Разработчик может писать бизнес-логику "прямо", а платформа берет на себя заботу о сбоях, ретраях и т.п【31†L189-L197】.
   - **Ветвление внутри workflow:** В примере встроена логика выбора пути в зависимости от типа файла (document/image/audio). Temporal workflows поддерживают обычные условные конструкции Python (if/`match-case`), позволяя в одном workflow оркестрировать разные последовательности шагов【31†L155-L162】. Это удобно для конвейеров с вариативной логикой – не нужно заранее расписываться жесткий DAG, можно прописать условия прямо в коде.
   - **Интеграция разнородных компонентов:** Оркестратор координирует сразу несколько видов сервисов: локальную ФС, облачное хранилище, базу данных, и внешние ML-сервисы. Temporal предлагает механизмы, чтобы каждая такая операция выполнялась один раз и в нужном порядке. Например, запись в БД будет выполнена только один раз, даже если workflow перезапустится, благодаря тому, что Temporal ведет историю и не повторяет завершенные активности после сбоя【31†L119-L127】【31†L189-L197】. Подобная гарантированная семантика (exactly-once для идемпотентных шагов) упрощает создание надежных ETL/обработчиков.
   - **Наблюдаемость и сравнительная простота:** В отличие от самостоятельных скриптов или cron, решение на Temporal дает из коробки мониторинг выполнения и логи для каждой задачи. В статье отмечено, что оба решения – Temporal и Prefect – фокусируются на улучшении опыта разработчика: обеспечивают ретраи, планирование, мониторинг, минимизируя шаблонный код【31†L119-L127】. Temporal, в частности, сохранил свои преимущества надежности (“код, который никогда не падает”【31†L189-L197】), что важно при интеграции множества источников данных. В итоге разработчик получил рабочий прототип пайплайна на Temporal с минимальными усилиями по инфраструктуре.

5. **How Grepsr uses Temporal to deliver scalable and reliable web data** (Subrat Basnet @ Temporal.io Blog, июль 2025). Статья-практический кейс от команды Grepsr – крупной платформы для извлечения данных из веба (web scraping/data extraction). Grepsr обрабатывает свыше **600 миллионов записей ежедневно** с более чем 10 000 источников данных【37†L81-L89】, предоставляя клиентам структурированные данные. В публикации рассказывается, как переход от самописных скриптов, cron-задач и очередей к Temporal позволил масштабировать такие объемы, обеспечивая \~99% надежность доставки данных【37†L133-L141】. Архитектура Grepsr – микросервисы, обрабатывающие разные этапы (краулинг, трансформация, загрузка) в событийной модели; Temporal выступает унифицированным оркестратором поверх них.\
   **Ключевые идеи и архитектурные элементы:**
   - **Проблемы традиционной оркестрации:** При росте нагрузки Grepsr столкнулся с трудностями: сложно отследить сбои в распределенных скриптах, состояние терялось при падениях (приходилось перезапускать сбор с нуля), параллельный запуск множества задач приводил к гонкам, а Cron не давал наблюдаемости и гибкости【37†L99-L107】. Это типичные проблемы при сборе данных на масштаб – отсутствие централизованного контроля и хранения состояния.
   - **Temporal как решение:** Выбор пал на Temporal из-за ряда факторов. **Workflow-as-code:** инженеры описывают workflow сборки данных привычным кодом, вместо громоздких YAML/DAG, что ускоряет разработку и упрощает поддержку【37†L115-L123】. **Автоустойчивость к сбоям:** платформа сама хранит прогресс workflow; если краулер или этап трансформации упал, при следующем запуске Temporal продолжит с места остановки, не теряя уже полученные данные【37†L118-L123】. **Параллелизм и масштабирование:** Temporal изначально спроектирован для тысяч параллельных workflow, что позволило Grepsr безболезненно запустить одновременно огромное количество одновременных сборов данных по разным источникам【37†L121-L127】. **Наблюдаемость:** благодаря веб-интерфейсу Temporal и полной истории событий, команда получила прозрачность – теперь можно в любой момент посмотреть состояние любой задачи, увидеть где произошел сбой, и даже при необходимости повторно проиграть историю выполнения【37†L123-L127】【37†L101-L107】.
   - **Результаты и полезные находки:** После внедрения Temporal надежность и масштабируемость существенно выросли. 99% задач завершаются успешно и в срок даже при отказах узлов или внешних сервисов【37†L133-L141】. Время на выяснение причин инцидентов сократилось на \~60%, т.к. Temporal даёт единое место для логирования и трекинга【37†L133-L141】. Интересно, что появление *workflows* как сущностей изменило и командную культуру: и инженеры, и менеджеры стали оперировать единым понятием “workflow” при планировании и отладке, что улучшило взаимопонимание【37†L139-L148】. Для проектировщиков аналогичных сервисов это пример, как оркестрация через Temporal упрощает поддержку сложных конвейеров сбора данных: система берет на себя управление потоками, а разработчики концентрируются на логике парсинга и доставки данных, не беспокоясь о отказах и масштабировании【37†L115-L123】【37†L118-L127】.


#### You:
в этих статьях описывается архитектура? подготовь техническое описание верхнеуровневой архитектуры(уровень компонентов)

#### ChatGPT:
Ты хочешь, чтобы я составил обобщённую архитектурную схему (на уровне компонентов) на основе всех пяти статей, или тебе нужно описание архитектуры отдельно по каждой статье? Также уточни, в каком формате тебе удобнее — текстовое описание, таблица или архитектурная диаграмма?


#### You:
отдельно по статьям, вместе с плюсами и минусами архитектур

#### ChatGPT:
Хорошо. Я подготовлю по каждой найденной статье отдельное техническое описание архитектуры на уровне компонентов: какие модули/сервисы используются, как взаимодействуют (workflow, activities, парсеры, API, хранилища и т.д.). Для каждой архитектуры опишу её сильные и слабые стороны с учётом масштабируемости, гибкости и применимости к задачам сбора данных.


#### ChatGPT:
## Scraping websites with Temporal (Aurelien Cluzeau)

**Архитектура:** Данный пример – упрощённый веб-скрейпер, использующий Temporal и Python【6†L37-L45】. *Workflow* под названием `CrawlWebsite` выполняет четыре последовательных шага: (1) загрузка HTML страницы по URL, (2) парсинг страницы для извлечения интересующей информации (заголовок и ссылки), (3) сохранение результатов в файл, (4) возврат итоговой структуры с данными【6†L121-L128】. Эти шаги реализованы как *Activity*-функции Temporal. Например, `fetch_page` загружает содержимое страницы через HTTP-клиент `httpx`【26†L231-L239】; `parse_page` разбирает HTML с помощью библиотеки BeautifulSoup, извлекая `<title>` и все ссылки (`<a href>`), приводя относительные URL к абсолютным【26†L257-L262】; `save_page` записывает полученные данные (заголовок и список ссылок) в JSON-файл на диске【26†L264-L271】. Для работы системы разворачивается **Temporal Server** (оркестратор рабочих процессов) и запускается Python-процесс-**Worker**, который регистрирует наш workflow (`CrawlWebsite`) и связанные с ним activity (`fetch_page`, `parse_page`, `save_page`)【26†L299-L307】. Temporal-сервер и воркер обмениваются заданиями через *Task Queue* – при запуске нового workflow через клиент Temporal (в примере – скрипт `run_workflow.py`) запрос попадает на сервер, после чего воркер получает задачи на выполнение activity и исполнения workflow【26†L335-L344】【26†L299-L307】. Архитектура по сути микросервисная: оркестрация вынесена в отдельный сервис (Temporal), а бизнес-логика выполнения инкапсулирована в воркерах. В простом случае всё разворачивается на одной машине (Temporal Server, один воркер и CLI для запуска), но при необходимости можно подключить несколько воркеров (даже специализированных под разные задачи) для параллельной обработки – Temporal распределит задачи между ними【26†L284-L292】. Хранилищем данных в этой реализации служит локальная файловая система (для выходных JSON), но Temporal позволяет легко заменить или добавить другие хранилища, вызывать внешние API и пр., инкапсулируя такие детали внутри activity.

**Плюсы архитектуры:**

- **Масштабируемость:** Благодаря Temporal можно обрабатывать множество страниц параллельно – достаточно запустить больше воркер-процессов или внедрить порождение дочерних workflow для каждой ссылки. Платформа сама позаботится о распределении нагрузки по воркерам и выдерживает горизонтальное масштабирование【26†L284-L292】【11†L69-L77】.
- **Устойчивость к сбоям:** Workflow и шаги (activity) являются *durable* – состояние выполнения автоматически сохраняется, что позволяет переживать перезапуски и сетевые сбои. Если воркер падает или сеть “падает” при загрузке страницы, Temporal возобновит выполнение с последнего шага; неуспешные activity можно автоматически повторить по заданной политике retry【11†L69-L77】【29†L39-L47】.
- **Гибкость расширения:** Архитектура легко расширяется под новые требования. Можно добавлять новые источники данных или этапы обработки, просто реализуя новые activity и вызывая их из workflow. Temporal позволяет запускать дочерние workflow для вложенных задач (например, отдельно обработать каждую найденную ссылку) и управлять ими сигналами, что открывает возможности для более сложного краулинга【26†L365-L373】. Благодаря слабо-связанным компонентам (отдельные функции-activity) модификация одного шага (например, парсинг дополнительной информации из страницы) минимально влияет на остальные.
- **Простота разработки и отладки:** Логика сбора данных описывается последовательно в виде кода workflow, что близко к обычному синхронному сценарию, но при этом выполняется асинхронно и надёжно. Разработчику не нужно вручную писать код для очередей, таймеров, повторных попыток или хранения промежуточного состояния – эти сложности берет на себя Temporal【29†L21-L29】【29†L39-L47】. Отладка упрощается благодаря встроенному UI Temporal, где можно просматривать историю выполнения каждого workflow (включая входы, выходы и ошибки)【6†L99-L107】【6†L109-L117】, что облегчает обнаружение проблем.

**Минусы архитектуры:**

- **Избыточность для простых случаев:** Для тривиальной задачи вроде единоразового парсинга одной страницы использование распределённого workflow-движка может быть излишним. Наличие Temporal вносит накладные расходы – требуется развернуть сервис Temporal, написать дополнительный код (workflow, активности с декораторами) и понимать концепции Durable Execution. Если объём или критичность задачи невелики, более простые решения (скрипт или Cron + requests/BS4) могли бы быть проще в реализации и эксплуатации.
- **Сложность инфраструктуры:** Архитектура подразумевает работу Temporal Cluster (сервер или кластер сервисов Temporal) в дополнение к самому приложению. Это усложняет инфраструктуру: нужно поддерживать работоспособность Temporal-сервера (или платить за Temporal Cloud). Для команды, незнакомой с Temporal, порог входа выше – требуется освоить новые инструменты и подходы.
- **Оверхед по производительности:** Выполнение через Temporal добавляет задержки на постановку задач в очередь, сохранение событий выполнения и т.д. В случае массового мелкого скрейпинга (например, тысяч страниц) overhead на координацию может сказаться на общем времени выполнения по сравнению с монолитным скриптом. Также хранение истории всех событий workflow нагружает бекенд Temporal – потребуется достаточная мощность базы данных Temporal, иначе при очень большом количестве задач возможны просадки производительности.
- **Детерминированность и разделение кода:** При разработке приходится строго разделять логику: внутри workflow запрещены любые недетерминированные операции (ввод-вывод, случайность, внешние вызовы), их нужно выносить в activity. Это требует дисциплины в архитектуре кода. Например, чтобы использовать `opencv` для обработки картинок, его вызовы нельзя напрямую делать в workflow (он запускается внутри Temporal и должен быть чистой функцией) – разработчик вынужден выносить такие вызовы в отдельные активности【29†L61-L69】. В небольшом проекте это усложняет кодовую базу. Кроме того, необходимо тщательно продумывать идемпотентность activity: при сбое и ретрае шаг «сохранить страницу» или аналогичный не должен дублировать изменения (во избежание повторной записи тех же данных и т.п.).

## A Story of a Million Rows: Building a Lightweight Batch Pipeline with Temporal and DuckDB (Tal Wanish, Riskified)

**Архитектура:** Рассматривается архитектура пакетной обработки данных, где на вход подаётся большой набор записей (миллионы строк) из Parquet-файлов в хранилище S3, а для каждой записи нужно выполнить независимый побочный эффект – в реальном случае вызов удалённого gRPC-сервиса【3†L55-L63】【3†L81-L89】. Ключевая идея – разбить эту задачу на иерархию *workflow* процессов в Temporal, чтобы параллелить обработку. Предложенное решение состоит из трех уровней workflow【3†L99-L108】: **Main Workflow** – верхнеуровневый процесс, который получает список путей к `.parquet`-файлам в S3, выясняет размер каждого (количество строк) и делит общий набор записей на логические *partition*-пакеты фиксированного размера. Main Workflow затем запускает параллельно несколько **Partition Workflow** – по одному на каждый пакет записей【3†L99-L108】. Каждый Partition Workflow в свою очередь разбивает свой пакет на более мелкие *batch*-задачи (напр. по N записей) и запускает для каждой из них **Batch Workflow** (эти «внуки» основного процесса выполняются параллельно, но с ограничением на одновременное количество через скользящее окно)【3†L101-L108】【28†L353-L361】. Таким образом, достигается трехуровневая конвейерная обработка: Main расходится на Partition, а те – на Batch, задействуя многочисленные параллельные экземпляры workflows. **Batch Workflow** выполняет непосредственную работу с данными: получает на вход конкретный файл и диапазон строк (offset + limit) для обработки【28†L269-L277】【28†L393-L400】. Внутри Batch workflow происходит чтение соответствующих строк из Parquet-файла (для эффективности используется DuckDB – встраиваемая СУБД, способная быстро выбирать диапазон строк из колонки) и формирование для каждой записи gRPC-вызова во внешнюю систему (например, сервис обогащения данных); после обработки Batch workflow посылает сигнал своему родительскому Partition workflow о завершении задачи【28†L392-L399】. **Partition Workflow** получает такие сигналы от batch-потомков и следит, чтобы одновременно выполнялось не больше заданного числа batch-задач (реализовано через механизм sliding window)【28†L355-L364】【28†L367-L375】. Когда один Batch workflow заканчивается, Partition запускает следующий, пока не обработает все записи своего пакета. Завершив все Batch, Partition workflow сигнализирует о своём завершении основному. **Main Workflow** дожидается окончания всех Partition workflows, после чего агрегирует результаты (либо просто фиксирует успешное завершение всех записей). Взаимодействие с внешними системами сведено к минимуму в рамках самого workflow: Main читает *метаданные* файлов (число строк) – это быстрая операция чтения заголовка Parquet【28†L287-L295】, а полный объём данных читают только Batch workflows, что локализует тяжёлые операции ввода-вывода в мелких параллельных задачах【28†L275-L283】. В окружение системы входят: **хранилище S3** с исходными данными, внешний **gRPC-сервис** (например, OrderService) который вызывается для каждой записи, и **Temporal Cluster**, координирующий работу【3†L142-L149】. На этапе тестирования автор поднимает локально Temporal Server, отдельный процесс Temporal Worker на Python, а также имитированный S3 и тестовый gRPC-сервис【28†L405-L413】 – в продакшене они будут реальными распределёнными сервисами. Форма исполнения распределённая: Temporal-сервер (может быть кластером) выполняет роль оркестратора, а воркеры (можно запустить множество экземпляров) в фоне исполняют код workflow/activities на Python. Код всех workflow и activity реализован в одном кодовом базе (монолите) приложения, но они могут выполняться параллельно на разных узлах благодаря Temporal. Воркеры используют Temporal Python SDK; для организации вычислений применяются библиотеки **DuckDB** (SQL-движок для локальной аналитики по колонкам) – для выборки из Parquet, **Poetry** для управления зависимостями, **protobuf/gRPC** для определения и вызова удалённого сервиса (OrderService).

**Плюсы архитектуры:**

- **Масштабируемость и производительность:** Решение эффективно масштабируется под большой объем данных. Разбиение на Partition и Batch workflow позволяет параллельно обрабатывать множество записей. Например, миллионы строк могут быть распределены на сотни workflow, выполняющихся одновременно. Temporal автоматически обеспечивает распределение задач по воркерам, можно добавить сколько угодно воркер-процессов для горизонтального масштабирования. Ограничение числа параллельных Batch через скользящее окно защищает систему от перегрузки – можно настроить максимальное число одновременных вызовов к внешнему сервису, удерживая баланс между скоростью и нагрузкой【28†L353-L361】. В отличие от монолитного скрипта или тяжелого Spark-джоба, здесь достигается *гранулярный параллелизм*: система ведет себя как распределённый цикл по записям【3†L63-L67】, но с минимальными накладными расходами.
- **Устойчивость к сбоям:** Temporal обеспечивает надежное выполнение каждого шага. Отказ любого отдельного Batch (например, ошибка сети при gRPC-вызове) не прерывает весь конвейер – неудачная задача может быть автоматически повторена или зафейлена изолированно, в то время как другие Batch продолжают работу. Workflow сохраняют прогресс: если воркер или нода падает, незавершенные Partition/Batch будут продолжены другим воркером без потери данных. Таким образом, даже обработка «миллиона строк» гарантированно либо завершится полностью, либо укажет, какие именно записи не обработаны. Temporal ведет полную историю исполнения, что упрощает отладку проблемных записей постфактум.
- **Гибкость и адаптивность:** Компонентный подход (разделение на несколько типов workflow) делает конвейер легко настраиваемым. Размер партиций и батчей задаётся параметрами – можно менять их для оптимизации производительности под разный объём данных без изменения кода【28†L409-L417】. Добавление новых источников данных или этапов обработки также возможно: например, можно вставить дополнительные activity в Batch workflow (для предварительной трансформации данных перед gRPC-вызовом) либо добавить шаги в Partition (например, сортировку данных) – архитектура позволяет расширять функциональность, не переписывая с нуля весь конвейер. Более того, Temporal поддерживает версионирование workflow, что облегчает эволюцию процесса во времени без простоя системы.
- **Проще разработка и поддержка по сравнению с альтернативами:** Автор отмечает, что первоначально рассматривал Apache Spark, но классическая Spark-задача не подходила (нужна построчная обработка с побочными эффектами)【3†L55-L63】. Использование Temporal дало возможность описать логику простым императивным кодом Python (циклы, вызовы функций) внутри workflow, вместо сложного управления распределенными заданиями. Многое из того, что пришлось бы делать вручную (распределение задач по узлам, отслеживание выполнения, повтор попыток при ошибке), Temporal предоставляет “из коробки”. Это облегчает поддержку: разработчики могут сосредоточиться на бизнес-логике (вызове внешнего сервиса для каждой записи), а не на инфраструктурных вопросах надежности. Также, благодаря использованию DuckDB, удалось обойтись без развёртывания тяжелого кластерного хранилища – обработка файлов происходит локально в процессе Python, что упростило архитектуру.

**Минусы архитектуры:**

- **Сложность реализации и понимания:** Несмотря на упрощение по сравнению с Spark, предложенная архитектура остается сложной для реализации с нуля. Многоуровневая структура workflow (основной + десятки дочерних процессов) с координацией через сигналы требует аккуратного проектирования и тестирования. Разработчикам нужно хорошо понимать принципы Temporal (например, использование сигналов для синхронизации параллельных задач【28†L355-L364】) и грамотно управлять контекстом данных (передача offset/limit потомкам, агрегирование результатов и т.д.). Порог входа для новых инженеров, которые будут поддерживать такой конвейер, выше, чем у более последовательных решений.
- **Нагрузка на Temporal Cluster:** При обработке действительно «миллиона» и более записей количество одновременно активных workflow и задач может быть очень большим (каждый Batch – отдельный workflow, их тысячи). Это предъявляет высокие требования к производительности Temporal-сервера и его внутренних хранилищ (например, Cassandra или SQL база для истории). Необходимо следить за масштабированием самого Temporal: добавить достаточное число нод, увеличить квоты на обработку задач и объем хранилища историй. Без должной настройки есть риск, что узким местом станет сам Temporal (в виде увеличения латентности или истощения ресурсов), особенно если конвейер запускается часто или в нескольких экземплярах параллельно.
- **Внешние зависимости и идемпотентность:** Архитектура полагается на внешние системы (S3, OrderService). Если S3 или гRPC-сервис испытывают проблемы (низкая скорость, ошибки), общая производительность конвейера снижается, и время выполнения может затянуться. Более того, вызовы внешнего OrderService для каждой строки – потенциально миллионы запросов – могут выявить ограничения этого сервиса (rate limiting, перегрузка). Нужно заранее продумать стратегию ретраев и аварийных остановок, чтобы не бесконечно повторять неудачные вызовы. Не менее важно обеспечивать идемпотентность: если Batch workflow упал на середине, некоторые вызовы могли дойти до внешнего сервиса. При повторном запуске (retry) те же записи могут отправиться вновь, что без защиты может привести к дублированию побочного эффекта (например, дважды записать ту же информацию). В идеале, внешний сервис или сам workflow должны уметь обнаруживать дубли (для чего Temporal позволяет задавать уникальные Workflow ID и помечать выполненные части). Без такой логики возможны некорректные ситуации при сбоях.
- **Неочевидная отладка и мониторинг прогресса:** По умолчанию, отслеживать прогресс такого конвейера непросто – Temporal UI покажет множество workflow и задач, но общей картины «сколько процентов обработано» нет. Автору пришлось вручную добавлять механизм видимости прогресса (например, учитывать в состояние Partition workflow сколько записей завершено)【28†L359-L367】. Это увеличивает сложность реализации. Аналогично, отладка логики распределенного окна или гонок сигналов может быть нетривиальной – требуются хорошие тесты и понимание concurrency. В случае ошибки, разработчику, возможно, придется анализировать историю events для большого числа workflow, что трудоемко. Таким образом, поддержка системы требует более продвинутых навыков и инструментов, чем у последовательных батч-скриптов.

## Using Temporal with Python (Alexander Thiemann)

**Архитектура:** Автор описывает реализацию сложного многоэтапного пайплайна обработки видео при помощи Temporal【29†L10-L17】. Проект (*vindex.ai*) позволяет пользователям загружать видео, после чего для каждого запускается серия аналитических шагов: извлечение кадров из видео, выделение аудио-дорожки, расшифровка (транскрипция) речи, вычисление различных эмбеддингов (представлений) для индексации содержимого и т.д.【29†L15-L17】. Все эти шаги оркеструются как единый workflow Temporal: для каждого загруженного видео стартует свой экземпляр *Workflow*, который последовательно вызывает серию *Activity*-функций, соответствующих этапам. Например, один шаг может извлекать кадры с помощью утилиты (например, ffmpeg или OpenCV), другой – вызывать сервис распознавания речи (внешний API или локальная ML-модель) для аудио, третий – вычислять эмбеддинги через библиотеку машинного обучения, и т.п. Каждая такая операция инкапсулирована в activity – то есть выполняется вне основного контекста workflow, чтобы обеспечить детерминизм и возможность ретрая. Код организован таким образом, что параметры и результаты каждой activity описываются отдельными Python dataclass (для удобства и совместимости при обновлениях)【29†L75-L84】【29†L85-L93】, а реализация activity помещена в отдельный модуль. Такой подход позволил инъектировать зависимости в activity – например, передать в функцию activity предварительно созданное подключение к базе данных (через пул соединений psycopg)【29†L99-L107】, или настроить клиент к внешнему API – избегая глобальных побочных эффектов в импортируемом коде workflow. Для запуска всей системы в разработке используется **Temporalite** (облегчённый dev-сервер Temporal)【29†L47-L55】, в продакшене это мог быть полноценный Temporal Cluster. Также существует компонент **FastAPI** (или другой веб-сервер), через который приложению подаются задания: при загрузке нового видео бэкенд генерирует событие запуска workflow (через Temporal SDK) с указанием параметров (например, идентификатор пользователя, ссылки на сохранённый файл видео и пр.)【29†L167-L175】. **Temporal Worker** – отдельный фоновый процесс (или несколько, для масштабирования) – регистрирует все workflow и activity нашего приложения и постоянно опрашивает Temporal-сервер на наличие задач【29†L159-L167】【29†L162-L170】. Воркер(ы) выполняют поступающие задачи: запускают код workflow для каждого нового видео и вызывают активности (например, обращение к базе, внешним сервисам) в отдельных потоках исполнения. Общая форма – микросервисная оркестрация: веб-сервис приложения отделён от выполнения долгих фоновых задач (их берёт на себя Temporal-воркер), Temporal-сервер выступает координатором. Технологический стек включает **Python 3.10** (asyncio) с **Temporal Python SDK**, библиотеки для обработки видео и звука (в тексте упомянуты OpenCV, библиотеки для работы с аудио), **psycopg\_pool** для доступа к PostgreSQL (хранение результатов индексации), а также dataclasses, используемые как схема данных для обмена между шагами пайплайна【29†L75-L83】【29†L99-L107】. В примере делается акцент на том, что масштабирование достигается просто запуском дополнительных воркеров без изменения кода – Temporal сам распределит workflow и activity между ними【29†L39-L47】. Также Temporal обеспечивает автоматические повторы неудачных действий, логирование, и интеграцию с внешними системами (например, загрузка/выгрузка файлов из облачного хранилища) через activity.

**Плюсы архитектуры:**

- **Масштабируемость и параллелизм:** Решение легко масштабируется под рост нагрузки. Поскольку каждый загруженный медиафайл обрабатывается своим workflow, достаточно поднять больше воркер-процессов (на том же или на разных серверах), и новые видео будут обрабатываться параллельно【29†L39-L47】. Temporal гарантирует справедливое распределение задач по воркерам. Кроме того, внутри одного workflow можно параллелить независимые шаги – Temporal поддерживает запуск concurrent activities и даже параллельных дочерних workflow. Например, если нужно одновременно извлекать кадры и аудио, можно сделать это через две activity, запущенные параллельно, и собрать результаты – Temporal и Python (asyncio) это позволяют. Таким образом, даже очень длительные или ресурсоемкие этапы (обработка видео, ML-инференс) могут выполняться одновременно, сокращая общую длительность процесса.
- **Устойчивость и надежность выполнения:** Использование Temporal делает долгий процесс обработки медиа устойчивым к сбоям. Если во время обработки видео сервис перезагрузится или упадёт воркер, workflow не потеряет состояние – после восстановления воркер продолжит с последней непройденной activity. Встроенные механизмы ретраев покрывают временные сбои внешних сервисов: например, если не удалось получить результат от сервиса расшифровки речи из-за сети, Temporal может повторить запрос автоматически【29†L39-L47】. Также есть возможность задать специальные политики (например, не ретраить при определённых типах ошибок, чтобы не зациклиться). В итоге каждое загруженное видео либо будет успешно проанализировано полностью, либо в случае постоянных ошибок разработчики чётко увидят, на каком шаге и по какой причине произошёл сбой – благодаря сохранённой истории и логированию Temporal.
- **Гибкость и расширяемость:** Архитектура на основе workflow легко модифицируется под новые требования. Можно добавлять или удалять этапы обработки видео, не затрагивая при этом внешний интерфейс – достаточно поменять реализацию workflow и добавить новые activity. Поскольку входы/выходы шагов определены через датаклассы, эволюция данных тоже упрощается – добавление нового поля (например, нового признака или метаданных) можно сделать необязательным и не сломать старые версии【29†L85-L93】. Temporal допускает версионирование workflow, так что можно обновить логику постепенно. Кроме того, подход с dependency injection в activity облегчает повторное использование компонентов: например, можно иметь одну activity для сохранения результата в БД, и переиспользовать ее в разных workflow. Добавление поддержки новых типов данных (скажем, помимо видео, обрабатывать аудио-файлы или PDF) тоже не потребует перестройки всей системы – достаточно создать новый workflow с нужным набором шагов, используя существующие activity там, где это применимо. Такая модульность повышает гибкость.
- **Удобство разработки и поддержки:** В отличие от традиционного скриптового подхода, где пришлось бы вручную отслеживать состояния или использовать цепочки задач (например, Celery), здесь разработка ощущается более прямой. Код workflow выглядит как обычный последовательный Python-код, что упрощает понимание процесса. Каждый этап изолирован в свою функцию, которую легко тестировать по отдельности. Автор специально разделил описание параметров и реализацию activity по разным модулям, что улучшает структуру проекта и избавляет от лишних зависимостей между компонентами【29†L61-L69】. Это способствует чистоте кода и облегчает сопровождение. Отдельно стоит отметить, что Temporal берет на себя множество рутинных задач – управление потоками, очередями, повторными попытками, таймаутами – позволяя разработчикам концентрироваться на логике анализа медиа【29†L21-L29】. Благодаря этому время разработки сложного пайплайна сокращается, а вероятность ошибок снижается. Также в арсенале появляется мощный инструмент отладки – Temporal Web UI, где можно наблюдать выполнение каждого шага, видеть входные данные и результаты, что значительно упрощает выявление проблем в таком многоступенчатом процессе.

**Минусы архитектуры:**

- **Дополнительная сложность инфраструктуры:** Внедрение Temporal требует развертывания и поддержания отдельного сервиса (или кластера) помимо основного приложения. Для небольших команд или проектов установка и администрирование Temporal может быть нетривиальной задачей. Хотя Temporalite облегчает локальную разработку【29†L47-L55】, в продакшене нужно решать вопросы масштабирования, резервирования и обновления Temporal-сервера. Это увеличивает операционные затраты и усложняет инфраструктуру по сравнению с монолитным приложением, выполняющим все задачи самостоятельно.
- **Оверхед и задержки при оркестрации:** Оркестрация через Temporal неизбежно добавляет некоторую задержку между шагами, что может быть критично в некоторых сценариях. Для большинства задач обработки видео это некритично, однако если бы требовалась ближняя к реальному времени реакция (например, мгновенная обработка стрима), то задержки на постановку задач в очередь, коммуникацию с сервером и сериализацию данных могли бы стать проблемой. В случае данного пайплайна каждая activity – довольно тяжелая операция (секунды или минуты), поэтому накладные \~ десятки миллисекунд Temporal несущественны. Но если шаги станут очень быстрыми, относительный overhead вырастет.
- **Требование идемпотентности и управление побочными эффектами:** Архитектура вынуждает явно учитывать возможное повторное выполнение activity. Например, если шаг сохранения результатов в базу или отправки уведомления выполнился, а потом workflow прервался, при повторном запуске этот шаг может выполниться снова. Разработчикам нужно предусмотреть защиту от дублей (например, использовать уникальные ключи или проверки). В данном случае, например, вставка в PostgreSQL через psycopg могла бы дублироваться при ретраях – это нужно обрабатывать на уровне бизнес-логики или конфигурации Temporal (отключать ретрай для явно идемпотентных операций). Это добавляет сложности и требует тщательного тестирования граничных случаев.
- **Сложность самого приложения увеличивается:** Хотя Temporal снимает нагрузку по обработке с основного сервиса, само приложение становится распределенным, что всегда сложнее для отладки. Разработчикам приходится иметь дело с асинхронностью, декораторами, ограничениями детерминированности (нельзя вызывать произвольный код внутри workflow). Нужны дополнительные усилия, чтобы убедиться, что, например, крупные данные не возвращаются напрямую из activity (что может замедлять систему из-за сериализации) – вместо этого возможно лучше сохранять большие результаты во внешнее хранилище и передавать ссылки. Все эти архитектурные решения ложатся на команду разработчиков. Таким образом, при всех удобствах Temporal, проектирование такого пайплайна требует более высокой квалификации и времени.
- **Необходимость интеграции с существующим кодом:** Для запуска workflow из веб-приложения требуется внедрить клиент Temporal (например, в FastAPI контроллере) и обеспечить связь контекстов. Это немного усложняет код приложения: появляются вызовы к Temporal Client, нужно управлять Workflow ID, обрабатывать ошибки запуска. Кроме того, нужно следить за совместимостью версий SDK, и учитывать, что локально (с Temporalite) и в продакшене (с облачным Temporal) могут быть разные нюансы. В общем, интеграция Temporal добавляет слой в архитектуру, который надо учитывать при разработке и деплое. Несмотря на плюсы, для команды это означает новую зону ответственности.

## Temporal + AI Agents: The Missing Piece for Production-Ready Agentic Systems (Akash Thakur)

**Архитектура:** В этой статье рассматривается применение Temporal для организации *agentic AI* – систем, состоящих из автономных интеллектуальных агентов, выполняющих долгосрочные задачи. В качестве примера приведена архитектура автоматизированного трейдингового бота, где несколько разных «агентов» последовательно анализируют и действуют на основе рыночных данных【30†L1041-L1049】【30†L1059-L1067】. Процесс представляет собой один *Workflow* (например, `AutomatedTradingWorkflow`), внутри которого выполняются шаги-активности, соответствующие ролям агентов. **Шаг 1:** сбор рыночных данных – агент-загрузчик обращается к внешним API бирж, получает котировки и другие данные по заданному финансовому инструменту【30†L1059-L1067】. **Шаг 2:** технический анализ – другой агент вычисляет торговые индикаторы или сигналы на основе собранных данных (может вызывать библиотеку для технического анализа либо сервис с ML-моделью)【30†L1078-L1086】【30†L1083-L1091】. **Шаг 3:** оценка риска – следующий агент анализирует результаты предыдущих шагов и рассчитывает метрику риска сделки (возможно, обращаясь к внешнему риск-сервису или используя правила)【30†L1097-L1105】【30†L1103-L1111】. **Шаг 4:** исполнение сделки – финальный агент, если риск приемлемый, посылает ордер на биржу для выполнения сделки (через брокерское API)【30†L1115-L1123】【30†L1123-L1131】. Каждый из этих этапов реализован как *Activity*, что означает выполнение в отдельном воркер-потоке с возможностью автоматического повторения при неудаче. Во время выполнения workflow Temporal фиксирует важные события: перед началом каждого шага в пример добавляется запись о прогрессе (какой этап запускается) – это сохраняется в состоянии workflow и может быть запрошено для мониторинга【30†L1059-L1067】【30†L1148-L1156】. По завершении всех этапов workflow агрегирует результаты каждого агента и возвращает сводный отчет, включающий финальное состояние (например, статус сделки)【30†L1139-L1144】. Данная архитектура предусматривает **последовательное** выполнение агентов (каждый следующий использует результат предыдущего)【30†L1150-L1157】, однако Temporal позволяет легко реализовать и параллельные паттерны. Статья демонстрирует улучшенную версию: например, можно параллельно опрашивать несколько источников рыночных данных (несколько бирж) и выполнить несколько вариантов анализа одновременно【30†L1158-L1166】【30†L1167-L1175】, используя `asyncio.gather` внутри workflow – Temporal поддерживает подобный фан-аут/фан-ин подход. Таким образом, архитектура может быть настроена как последовательная, параллельная или комбинированная в зависимости от требований. **Компоненты системы:** Temporal-сервер выполняет оркестрацию, множество Python-воркеров запускают код агентов. Обычно разные типы агентов могут быть разнесены по разным *Task Queue* и даже разным воркерам для изоляции – например, одни воркеры могут обрабатывать только запросы к биржевым API, другие – выполнять тяжёлые ML-вычисления, третьи – заниматься отправкой ордеров. Temporal гибко маршрутизирует задачи по очередям; добавление нового типа агента сводится к подключению нового воркера и написанию соответствующей активности. Внешние системы включают: API маркетдат (например, для котировок) – вызывались через HTTP (в примере использована библиотека `requests`)【11†L133-L142】, сервисы или библиотеки для анализа (может быть финансовая библиотека или модель), риск-модели, а также брокерские API для отправки торговых приказов. Данные между шагами передаются в виде словарей Python (или dataclass) внутри workflow, Temporal автоматически сохраняет их в исторii. Общая форма исполнения – микросервисная, распределенная: несколько разнородных сервисов (биржевые API, брокер и т.д.) объединены единым долговременным workflow, который гарантирует, что последовательность шагов будет выполнена целиком, несмотря на сбои. Благодаря Temporal, разработчики могут реализовать *agentic* логику как код, без необходимости самим писать сложный движок управления состоянием агентов【11†L57-L64】.

**Плюсы архитектуры:**

- **Надежность и отказоустойчивость:** Для длительных и сложных процессов, как автономный трейдинг, крайне важно, чтобы ошибки не приводили к остановке всего процесса. Использование Temporal обеспечивает автоматическое восстановление после сбоев – если агент завис или упал по исключению, workflow не потерян: после обработки ошибки или запуска на другом воркере он продолжит с места сбоя. Встроенные механизмы повторных попыток повышают надежность: транзиентные проблемы (временное отсутствие сети, таймаут API) будут преодолены автоматическим ретраем по заданной политике【30†L1050-L1058】【30†L1066-L1074】. Так, агент сбора данных может несколько раз попытаться получить котировки, и только действительно критичный сбой остановит процесс. При этом Temporal позволяет маркировать некоторые ошибки как невосполнимые (например, логическая ошибка “недостаточно средств” для исполнения ордера) – такие не будут ретраиться【30†L1050-L1058】. Все это делает систему устойчивой: она либо успешно доведёт цепочку агентов до конца, либо точно зафиксирует, где и из-за чего остановилась.
- **Контроль и управляемость процесса:** Оркестрация через Temporal дает возможность отслеживать и контролировать выполнение агентов в режиме реального времени. В примере реализованы **Queries** – специальные методы workflow для запроса текущего прогресса и состояния сделки【30†L1023-L1031】【30†L1148-L1156】. Это означает, что в любой момент можно опросить работающий workflow и получить, какой агент сейчас исполняется и какие данные уже собраны. Такая прозрачность крайне полезна для мониторинга долгих процессов (оператор системы всегда знает, что сейчас делает бот) и для отладки. Более того, Temporal позволяет отправлять **Signals** – внешние команды в workflow – например, можно реализовать сигнал для преждевременной остановки торговли или переключения стратегии на лету. Этот уровень контроля практически невозможен в монолитных скриптах, а здесь доступен “из коробки”.
- **Гибкость и масштабируемость:** Данный подход легко адаптируется под различные сценарии. Можно конфигурировать последовательность агентов, добавлять новые этапы (например, дополнительный агент новостей, влияющий на решение) – для этого потребуется лишь написать новую activity и вставить вызов в workflow. Temporal поддерживает композицию workflow: можно один workflow вызывать из другого, реализуя древовидную логику (в статье упоминаются шаблоны Saga, условные выполнения и т.д. для более сложных бизнес-процессов)【12†L23-L31】【12†L41-L49】. Масштабирование достигается за счет параллелизма: если нужно ускорить обработку, независимые шаги (например, сбор данных с разных рынков, анализ разных аспектов) могут выполняться параллельно, как показано в улучшенном примере с параллельным сбором и анализом на нескольких биржах【30†L1160-L1168】【30†L1182-L1190】. Temporal позволит запустить десятки параллельных под-задач и потом удобно собрать результаты. Кроме того, система готова к одновременному ведению нескольких процессов: например, несколько Workflow могут торговать разными инструментами параллельно – нужно только достаточно воркеров; Temporal масштабируется горизонтально для обслуживания множества одновременных потоков【11†L69-L75】.
- **Упрощение разработки сложной логики:** Использование Temporal сильно упрощает реализацию многошагового агентного алгоритма. Разработчику не нужно самостоятельно реализовывать конечный автомат, хранить состояние агента между перезапусками или писать вручную логику планировщика задач. Весь порядок действий описывается в одном месте – внутри workflow, обычным Python-кодом, что облегчает понимание и изменение логики. Temporal берет на себя бо́льшую часть “рутинных” проблем распределенных систем – управление потоками, синхронизацию, обработку таймаутов, логирование каждой операции. Это снижает вероятность ошибок. Как отмечает автор, Temporal абстрагирует сложность распределенной обработки, позволяя сосредоточиться на бизнес-логике агентов【11†L57-L64】. В результате итоговый код более декларативный и чистый, его проще поддерживать. Кроме того, каждый агент как отдельная функция легко тестируется в отрыве от процесса (можно вызывать activity-функцию автономно, передавая ей имитированные данные или заглушки API). Это способствует надежности системы в целом.

**Минусы архитектуры:**

- **Усложнение архитектуры приложения:** Добавление Temporal привносит дополнительный слой сложности. Вместо простой последовательной программы появляется распределенный workflow, требующий развертывания Temporal-сервера и написания кода с учетом его требований (детерминированность, разделение на activity и т.д.). Команде разработчиков необходимо изучить принципы Temporal, что увеличивает время входа. Для небольших проектов агентного AI, возможно, это overkill – если процесс не слишком длинный или критичный, можно было бы обойтись упрощенной оркестрацией. Таким образом, нужно взвешивать выгоду: Temporal серьезно повышает надежность, но цена – усложнение системы.
- **Оверхед и задержки, критичные в реальном времени:** В контексте торговых систем время реакции может быть критичным. Архитектура на Temporal добавляет некоторую фиксированную задержку на каждый шаг (общение с брокером, сохранение состояния и пр.). Для большинства стратегий это приемлемо (они работают в человеко-читаемых масштабах времени – секунды, минуты), но для высокочастотной торговли такая оркестрация могла бы быть слишком медленной. Кроме того, автоматические ретраи, хотя и повышают надежность, могут привести к тому, что решение будет принято с опозданием (например, если несколько попыток получения данных заняли время, рынок мог уйти вперед). В критичных случаях стратегию нужно разрабатывать с учетом возможных задержек или отключать ретраи и использовать альтернативные механизмы.
- **Идемпотентность действий и риски дублирования:** Когда агентов много и они осуществляют побочные действия (особенно последний шаг – исполнение сделки), очень важно предотвращать дублирование при повторных попытках. В Temporal гарантируется выполнение workflow **минимум** один раз, поэтому, если шаг отправки ордера упал не дождавшись ответа, Temporal может запустить его снова, решив, что он не завершился. Без дополнительных мер это чревато повторной отправкой того же ордера. Необходимо проектировать агента исполнения с учетом идемпотентности – например, проверять, не была ли уже отправлена заявка, или использовать внешнюю систему, которая сама отклоняет дубликаты. В общем, разработчики должны быть особо внимательны с шагами, имеющими необратимый эффект. (В примере, кстати, применена проверка `if risk_score < 0.7` – если риск слишком высок, агент исполнения вообще пропускается【30†L1115-L1123】【30†L1131-L1137】, что предотвращает некоторые нежелательные сделки, но не решает проблему возможного дубликата при сбое сети).
- **Зависимость от внешних API и ошибок данных:** Хотя Temporal отлично лечит технические сбои, он не решает проблемы качества данных или логики. Агентная система все так же зависит от корректности внешних данных (котировки, анализ). Если исходные данные неверны или стратегия агента ошибочна, Temporal не предотвратит убытков. Также, при масштабировании до многих одновременных workflow, внешние API (бирж, новостей и др.) могут стать узким местом – нужно контролировать лимиты запросов, возможно, добавлять ограничение частоты вызовов (Temporal signals/queries это позволяют, но нужно дополнительно реализовать). Таким образом, архитектура требует не только технического, но и бизнес-контроля.
- **Общая сложность системы:** Полноценная агентная платформа включает множество частей – помимо самих агентов и Temporal-оркестрации, есть еще мониторинг, управление рисками, интерфейсы пользователя. Внедряя Temporal, добавляется еще один компонент, о котором нужно заботиться. Команде поддержки придется иметь экспертизу и в Temporal тоже (обновления, настройки, мониторинг его состояния). В отладке логики агента разработчик должен просматривать event history и логи воркеров, что сложнее, чем отладка последовательного кода. Не все ошибки легко воспроизвести локально, иногда придется воспроизводить сценарии внутри Temporal. Все это делает цикл разработки и отладки более сложным. Тем не менее, эти минусы компенсируются существенными преимуществами в надежности для тех случаев, где ставки высоки (например, финансовые операции).


#### You:
Мне нужно, чтобы ты, как профессиональный архитектор IT-систем, который умеет работать с архитектурными структурированными описаниями, сделал описание каждого из этих сервисов в структурированном виде, например, двухуровневый или трехуровневый список. Ты сам выберешь, что лучше подойдет. опиши каждый компонент и его ответственность. Мне нужно, чтобы не было лишней информации, чтобы вся информация по структурированным описаниям четко понять. Чтобы списки не были перегружен информацией, но при этом там должна содержаться вся необходимая информация.

#### ChatGPT:
Ниже — **структурированные (2–3 уровня) описания архитектуры на уровне компонентов** для каждой статьи. Для каждого компонента указана **ответственность** (что делает и за что отвечает).

---

## 1) Scraping websites with Temporal (cluzeau.pro) — простой веб‑скрейпер

### Компоненты и ответственность

- **Temporal Server (dev mode)**
  - Хранит состояние и историю выполнения workflow.
  - Распределяет задачи по очередям (task queues) для воркеров. citeturn4view0

- **Workflow Trigger (CLI/скрипт `run_workflow.py`)**
  - Формирует входные параметры задания (URL, output\_dir, id).
  - Стартует workflow через Temporal Client, задавая `workflow_id` и `task_queue`. citeturn4view3turn4view1

- **Worker Process (`run_worker.py`)**
  - Подключается к Temporal Server.
  - Регистрирует workflow и activity, **poll’ит** очередь и исполняет задачи. citeturn4view1

- **Task Queue (`scraper`)**
  - Логическая очередь, через которую Temporal направляет задания воркерам. citeturn4view1

- **Workflow: `CrawlWebsite`**
  - Оркестрирует шаги: **fetch → parse → save → return**.
  - Определяет вход/выход через dataclass‑модели (`CrawlUrl`, `FetchedPage`, `ParsedPage`, `SavePage`, `Output`). citeturn4view4turn3view0turn3view4

- **Activities**
  - `fetch_page`
    - Делает HTTP GET и возвращает HTML (`httpx`). citeturn3view1turn4view4
  - `parse_page`
    - Парсит HTML (`BeautifulSoup`), извлекает title и links, нормализует относительные ссылки. citeturn4view4turn3view1
  - `save_page`
    - Сохраняет результат на диск по рассчитанному пути (`{output_dir}/{id}.json`). citeturn3view4turn4view4

- **Хранилище результата (локальный диск)**
  - Хранит JSON‑артефакт парсинга по `output_dir`. citeturn4view0turn4view4

- **Observability (Temporal Web UI)**
  - Просмотр запусков, входов/выходов, retry, ошибок по event history. citeturn4view0

### Плюсы архитектуры

- Чёткая декомпозиция на шаги (activities) и оркестрацию (workflow). citeturn4view4
- Быстрый старт: dev‑сервер + воркер + CLI. citeturn4view0
- Понятная точка расширения (добавлять activities/child workflows). citeturn4view3

### Минусы архитектуры

- Для простого скрейпинга инфраструктурный оверхед Temporal может быть избыточен.
- Хранилище результата (локальный диск) — узкое место при масштабировании/распределении.

---

## 2) A Story of a Million Rows (Riskified Tech @ Medium) — батч‑пайплайн Parquet→gRPC

### Компоненты и ответственность

- **Temporal Cluster (Server)**
  - Оркестрирует и хранит состояние цепочки Main/Partition/Batch workflows. citeturn5view3turn5view4

- **Worker(ы)**
  - Исполняют workflows и activities.
  - Потенциально разделяются по task queues для контроля ресурсов/throughput. citeturn5view4turn5view5

- **Main Workflow**
  - Получает список/директорию `.parquet`.
  - Читает **метаданные** файлов (кол-во строк) и строит “логические партиции” по `partition_size`.
  - Запускает **Partition Workflow** для каждой партиции и ждёт завершения.
  - Агрегирует прогресс и отдаёт его через workflow query. citeturn5view0turn5view6turn3view6

- **Partition Workflow (child of Main)**
  - Управляет обработкой одной партиции.
  - Запускает **Batch Workflow** батчами по `batch_size`.
  - Ограничивает параллелизм через **sliding window** (`sliding_window_size`), трекает in‑flight/complete. citeturn5view0turn3view5turn5view1

- **Batch Workflow (child of Partition)**
  - Единственный уровень, который читает **фактические данные**.
  - Получает `(file, offset, limit)`, читает записи, формирует payload и вызывает gRPC‑сервис на каждую запись.
  - По завершении сигналит родителю (Partition) о завершении батча. citeturn5view0turn5view1

- **DuckDB Client**
  - Используется в Main (дешёвые метаданные) и в Batch (чтение диапазона строк по offset/limit). citeturn3view7turn5view1

- **Object Storage (S3)**
  - Источник `.parquet` файлов. citeturn5view3turn5view2

- **gRPC Service (в статье — OrderService)**
  - Внешний side-effect на каждую запись (сетевой вызов). citeturn5view3turn5view1

- **Progress/Visibility (Workflow Query)**
  - Main публикует агрегированный прогресс через Temporal query (`get_progress`). citeturn5view6turn3view6

### Плюсы архитектуры

- Иерархия workflow (Main→Partition→Batch) даёт управляемый параллелизм и контроль нагрузки. citeturn5view0turn5view1
- Sliding window защищает внешний gRPC от перегрузки и упрощает throughput‑тюнинг. citeturn5view1turn3view5
- Хорошая наблюдаемость прогресса через query. citeturn5view6

### Минусы архитектуры

- Много сущностей (тысячи batch workflows) → нагрузка на Temporal и усложнение оперирования.
- Требует строгой идемпотентности на стороне gRPC side‑effect (повторы activity/workflow).

---

## 3) Temporal + AI Agents (dev.to) — оркестрация “агентов” как Activities/Workflows

### Компоненты и ответственность

- **Temporal Service (`temporal-server`)**
  - Долговечное выполнение (durable execution), хранение event history, восстановление после сбоев. citeturn2view2

- **Worker Processes**
  - Poll’ят Temporal на задачи.
  - Исполняют workflows и activities.
  - Могут масштабироваться горизонтально и обслуживать несколько очередей. citeturn6view0

- **Task Queue (пример: `trading-queue`)**
  - Канал маршрутизации задач к воркерам для конкретного домена/типа работ. citeturn6view0

- **Workflow слой (оркестратор логики)**
  - **Sequential orchestration**: пошагово вызывает activities, фиксируя порядок/политику retry/timeout. citeturn6view2
  - **Parallel orchestration**: параллельно запускает независимые activities и агрегирует результаты (пример — параллельный сбор данных с разных “бирж” и параллельный анализ). citeturn6view2turn6view4
  - **MultiAgentOrchestrationWorkflow**: запускает несколько “агентов” параллельно (`research/analysis/planning`) и затем вызывает `coordinator_agent_activity` для синтеза результата. citeturn6view2turn6view3
  - **Композиция через child workflows** (примерные паттерны для модульности/саг). citeturn3view8

- **Activities слой (агенты/инструменты)**
  - `fetch_market_data_activity`
    - Делает внешний HTTP/API вызов (в примере через `requests`), допускает retry со стороны Temporal. citeturn3view9turn6view4
  - Другие activity‑шаги (анализ, агрегация сигналов, выполнение действий/сделок) — должны быть **single-purpose**. citeturn6view6turn6view2

- **State & Queries**
  - Workflow хранит состояние (контекст) внутри execution.
  - Доступ к состоянию обеспечивается через workflow queries (read‑only доступ). citeturn6view6

### Плюсы архитектуры

- Хорошо подходит для сложных, долгих, многошаговых процессов с ошибками/ретраями. citeturn2view2turn6view6
- Удобные паттерны параллельного fan‑out/fan‑in для I/O‑шагов. citeturn6view2

### Минусы архитектуры

- Статья даёт архитектурные паттерны, но **не фиксирует конкретную “data ingestion” инфраструктуру** (хранилища/шины/форматы) — это остаётся на проектировщике.
- Нужно отдельно проектировать идемпотентность “действий” (особенно если есть side effects).

---

## 4) I built the same pipeline twice — Temporal и Prefect (CodiLime) — файл‑пайплайн + 2 оркестратора

### Компоненты и ответственность

- **Ingress/Trigger (“новый файл”)**
  - Пользователь загружает файл → файл сохраняется на диске → инициируется запуск пайплайна. citeturn7view0

- **Pipeline Workflow/Flow (бизнес‑логика обработки файла)**
  - Читает файл и определяет тип.
  - Загружает файл в S3.
  - Создаёт/обновляет запись в БД.
  - Ветвится по типу: OCR / image analysis / audio transcription.
  - Завершает: обновление записи, удаление локального файла, отправка уведомления. citeturn7view0turn7view1

- **Вариант A: Temporal orchestration chain**
  - **Temporal Server**
    - Принимает старт workflow от клиента/триггера, ставит задачи в очередь, хранит историю выполнения. citeturn7view1turn7view2
  - **Task Queue**
    - Канал доставки задач воркерам (в примере есть выделение `io-queue` для I/O‑activity). citeturn7view2
  - **Worker**
    - Poll’ит очередь, исполняет workflow и activities. citeturn7view2
  - **Workflow code**
    - Оркестрирует последовательность шагов, вызывает activities с timeout/retry/heartbeat политиками. citeturn7view2
  - **Activities**
    - “read file”, “upload to S3”, “recognize/analyze/transcribe”, “db update”, “notify” — каждая делает одну операцию. citeturn7view2

- **Вариант B: Prefect orchestration chain (для сравнения, из статьи)**
  - **Deployment**
    - Описывает параметры и расписание запуска flow. citeturn7view3
  - **Work Pool**
    - Описывает инфраструктуру, где будут выполняться flow runs. citeturn7view3
  - **Worker**
    - Poll’ит work pool и запускает flow. citeturn7view3
  - **Flow code + Tasks**
    - Flow — общая логика, Tasks — шаги (аналогично activities, но в терминах Prefect). citeturn7view3

- **Внешние зависимости (в обоих вариантах)**
  - **Local Storage**: чтение/удаление исходного файла.
  - **S3**: целевое хранение файла.
  - **Database**: метаданные/результаты.
  - **Processing Services**: OCR / CV‑анализ / ASR.
  - **Notification**: уведомление о готовности. citeturn7view0turn7view1

### Плюсы архитектуры

- Пайплайн чётко выражен как “код процесса” и легко расширяется новыми типами файлов. citeturn7view1turn7view2
- Temporal‑вариант добавляет надёжность через политики retries/timeouts/heartbeats и разнос I/O на отдельную очередь. citeturn7view2

### Минусы архитектуры

- Много внешних side‑effect шагов (S3/DB/уведомления) → нужно проектировать идемпотентность и дедупликацию.
- Две модели оркестрации (Temporal/Prefect) в реальном проекте лучше не смешивать без крайней необходимости.

---

## 5) How Grepsr uses Temporal… (temporal.io blog) — микросервисная платформа web‑data

> Важно: статья описывает подход на уровне платформы; **язык реализации воркеров не указан** (Temporal SDK упоминается в общем виде). citeturn8view0turn8view2

### Компоненты и ответственность

- **Микросервисная event‑driven платформа Grepsr**
  - Набор независимых компонентов “от crawling до data delivery”.
  - Компоненты взаимодействуют событийно; исторически — через cron jobs, кастомные скрипты и message queues. citeturn8view0turn3view12

- **Temporal как оркестратор workflow**
  - **Code‑first workflows**: workflow описываются кодом через Temporal SDK, уменьшая “кастомную оркестрацию”. citeturn8view0turn8view2
  - **Fault tolerance**: сохранение состояния workflow и продолжение “с места падения”. citeturn8view0turn8view2
  - **Native parallelism**: поддержка тысяч параллельных workflow. citeturn8view2

- **Execution layer (Workers)**
  - Исполняют workflow/activities, соответствующие шагам “crawling → processing → delivery”.
  - Масштабируются под нагрузку (на уровне воркеров и микросервисов). *(механика воркеров подразумевается моделью Temporal, детали не раскрыты в статье)* citeturn8view2

- **Observability**
  - Temporal Web UI + Event History как единая точка мониторинга/дебага “каждой data job”. citeturn8view2

### Плюсы архитектуры

- Хорошо работает для сложных пайплайнов из независимых микросервисных шагов (координация, состояние, параллельность). citeturn8view0turn8view2
- Сильная наблюдаемость: “сквозная” трассировка job через историю событий. citeturn8view2

### Минусы архитектуры

- Статья не раскрывает конкретику реализации (типы хранилищ, формат “job”, границы activity, контракт между микросервисами) — это надо спроектировать самостоятельно.
- Как и в любом микросервисном подходе: усложнение эксплуатации, версионирование контрактов, идемпотентность шагов.

---

Если хочешь, следующим шагом я могу:

- сделать **унифицированный “референсный” компонентный шаблон** для твоего сервиса парсинга (Ingress → Temporal → Adapter Activities → Storage → Observability),
- и показать, **как именно организовать “адаптеры источников”** (веб/RSS/Telegram/YouTube) как activities + task queues так, чтобы добавление нового источника было минимальным изменением в коде.
