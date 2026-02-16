# Категоризация веб-страниц

#### You:
Помоги мне исследовать следующий вопрос. Я хочу построить категоризацию веб-страниц, то есть их следующим. Мне нужно парсить интернет. Я хочу у себя в БД хранить категорию страницы. Что мне приходит в голову? Это может быть, например, страница с продуктом, где описан конкретный продукт. Это может быть, например, статья, какая-нибудь там, например, медиа-статья, да, то есть, где что записывается. Это может быть пост в Твиттере. Это может быть, например, еще какой-нибудь информационный ресурс, например, магазин, например, тех главных страниц магазина. В общем, суть в том, что наверняка кто-то уже пытался категоризировать виды страниц, и мне нужно, чтобы ты попробовал найти подобные категоризации. Может быть, есть какие-нибудь научные публикации или что-то в этом духе. То есть это может быть таксономия, это может быть онтология, это может быть просто иерархическая категоризация или еще что-то в этом духе. Попробуй найти это на английском языке.

#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
\[Unsupported Content]


#### ChatGPT:
Ниже — несколько **реально существующих** “категоризаций типов страниц” (taxonomies/ontologies), которые можно использовать как основу для хранения *категории страницы* в БД. Я специально искал именно **page-type / genre / functional type** (а не только тематику “sports/news”), потому что у тебя примеры — “product page”, “article”, “homepage”, “tweet”.

## 1) Schema.org: онтология “что это за страница” (page type + entity type)

Это, по сути, самый практичный готовый “словарь типов страниц”, потому что:

- он массово используется в разметке сайтов (JSON-LD/microdata),
- и у него есть **подтипы WebPage**, которые прямо соответствуют “типам страниц” (item page, search results, profile и т.д.). citeturn1search4turn1search0

**Подтипы WebPage (примеры):**

- `ItemPage` — страница про один объект (товар/пост/фото/статья и т.п.) citeturn1search4
- `CollectionPage` — страница-коллекция (категория, листинг) citeturn0search3turn1search4
- `ProfilePage` — профиль пользователя citeturn1search4
- `SearchResultsPage` — страница результатов поиска citeturn1search4
- `FAQPage`, `ContactPage`, `AboutPage`, `CheckoutPage` и т.д. citeturn1search4turn1search8

Плюс отдельно (не как subtype WebPage) есть “сущности”, которые часто являются *главным объектом страницы*: например `Product`, `Article/NewsArticle`, `SocialMediaPosting` (пост), `WebSite` и т.п. citeturn0search31turn0search10turn0search28

**Как ложится на твои примеры**

- “страница с продуктом” → `ItemPage` + `mainEntity: Product`
- “медиа-статья” → `ItemPage` + `mainEntity: Article/NewsArticle`
- “пост в Твиттере” → `ItemPage` + `mainEntity: SocialMediaPosting`
- “главная магазина” → `WebPage` (homepage) + `isPartOf: WebSite` (+ часто `Organization` как main entity)
- “категория/листинг магазина” → `CollectionPage` или `ProductCollection` (если размечено как коллекция продуктов) citeturn0search19turn0search3

## 2) Research line: “Web page genre / document type” (научные таксономии жанров страниц)

В академике это обычно называется **genre-based web page classification** (жанр/тип страницы, в отличие от topic/subject). Хорошая отправная точка:

- обзор/глава “Web Page Classification” прямо разделяет subject-based vs genre-based подходы. citeturn0search14turn0search4
- классическая работа про “page and link classifications / genres” (Haas & Grams, 1998) — один из ранних систематизаторов “типов” веб-ресурсов. citeturn1search3turn1search34
- работы Santini про определение жанров веб-страниц (genre identification). citeturn1search14turn1search7
- есть и прикладные статьи/датасеты “Web page genre classification”, где вводят верхнеуровневые жанры и поджанры. citeturn0search17turn0search23turn0search29

**Плюс этого направления**: можно найти именно “жанры страниц” вроде *homepage, product page, forum, news article* и т.д.\
**Минус**: таксономии часто разные от статьи к статье (нет одного “де-факто стандарта”, как schema.org).

## 3) AdTech стандарт: IAB Content Taxonomy (скорее “о чём контент”, но часто используется совместно с page-type)

IAB Tech Lab Content Taxonomy — стандартная “общая речь” для классификации контента страницы для contextual targeting / brand safety. citeturn0search2turn0search15\
Это **не** “тип страницы” в смысле “product vs listing vs profile”, но очень полезно как **вторая ось**: *тематика/контент*.

Если тебе нужно хранить **категорию** страницы для аналитики/таргетинга — IAB часто берут как “topic taxonomy”, а page-type делают отдельно. citeturn0search2turn0search6

## 4) News-индустрия: IPTC Media Topics (тематика новостей)

Если у тебя много “статей/медиа”, IPTC Media Topics — широко используемая и поддерживаемая таксономия (обновляется регулярно, >1200 терминов). citeturn1search1turn1search9\
Опять же: это **topic taxonomy**, но для новостей очень “канонично”.

## 5) Практическая индустриальная “landing page type”

В прикладных/рекламных системах встречается поле **landing page type** с примерами вроде: *news article, product page, forum, home-page*. citeturn0search1\
Это полезно как подсказка, что “page type” часто держат отдельно от “topic”.

---

# Рекомендация для твоей БД: 2–3 оси вместо одной “категории”

Чтобы не застрять в бесконечном споре “статья vs блог-пост vs пресс-релиз vs лонгрид”, обычно делают так:

1. **Functional Page Type (page kind)** — лучше всего базироваться на Schema.org WebPage subtypes (плюс расширения)\
   Примеры: `ItemPage / CollectionPage / ProfilePage / SearchResultsPage / FAQPage / CheckoutPage / …` citeturn1search4

2. **Main Entity Type (что за объект на странице)** — Product / Article / SocialMediaPosting / Organization / … citeturn0search31turn0search10

3. (опционально) **Topic taxonomy** — IAB или IPTC (для новостей) citeturn0search2turn1search1

Если хочешь, я в следующем сообщении предложу:

- компактный “минимальный” список page types (15–30 типов), покрывающий веб+RSS+соцсети+e-commerce,
- и правила/сигналы извлечения (schema.org разметка, DOM-паттерны, URL-шаблоны, OpenGraph, метаданные), чтобы это можно было реально классифицировать в пайплайне.


#### You:
Я хочу, чтобы ты продолжил изучать этот вопрос и искать подходящий материал.

#### ChatGPT:
Я продолжил поиск и нашёл несколько **довольно “канонических”** линий работ, где прямо предлагаются **инвентари/таксономии “типов веб‑страниц”** (чаще это называется *web genre*, *functional genre*, *register*, иногда *page type*) + есть датасеты с уже размеченными страницами.

Ниже — то, что выглядит наиболее пригодным именно под вашу задачу “парсить интернет → положить в БД категорию страницы”.

---

## 1) Самый полезный обзор, который “собирает поле в одно место”

**T. Kuzman, N. Ljubešić — “Automatic genre identification: a survey” (Language Resources & Evaluation / Springer).**\
Это именно обзор по автоматическому определению жанров/типов текстов и веб‑страниц: что такое жанр/регистр, почему разметка сложная (гибридность страниц и т.п.), какие есть схемы разметки и датасеты (KI‑04, SANTINIS, 20‑Genre, CORE, HGC, KRYS I, Syracuse и др.). citeturn6search6turn5view1

Почему важно: если вам нужно “найти существующие категоризации”, то этот обзор — практически карта всей области с указанием **наборов ярлыков** и **корпусов**. citeturn5view0turn6search6

---

## 2) Академические “палитры жанров/типов веб‑страниц”, которые можно взять как есть

### 2.1 Genre‑KI‑04 (один из самых прикладных для “типа страницы”)

**Genre‑KI‑04 (web genre corpus 2004)** — датасет на **1239 HTML‑документов** с разметкой в **8 жанров**, опубликован на Zenodo (от Webis / Univ. Paderborn). citeturn8view0

Сами 8 жанров и распределение (прямо в описании датасета):

- **Articles** (127)
- **Discussion** (127)
- **Download** (152)
- **Help** (140)
- **Link lists** (208)
- **Portrait (non private)** (179)
- **Portrait (private)** (131)
- **Shop** (175) citeturn8view0

Почему это очень близко к вашей задаче:

- “страница товара/магазина” → **Shop**
- “статья/медиа” → **Articles**
- “форум/обсуждение/комменты” → **Discussion**
- “страница помощи/FAQ/документация” → **Help**
- “каталог ссылок/директория” → **Link lists**
- “профиль/страница персоны/компании” → **Portrait**
- “скачать файл/дистрибутив” → **Download**

Отдельно удобно, что этот набор ярлыков изначально делался как “полезные жанры для пользователя/поиска” (bottom‑up через user study — это тоже обсуждается в обзоре). citeturn6search6turn6search8

---

### 2.2 7‑Web Genre Collection (Santini) — “веб‑специфичные” типы

Набор, который часто упоминают как **SANTINIS / 7‑Web Genre Collection**: **1400 страниц**, **7 жанров**, причём жанры сформулированы как “типично вебовые”:\
**Blog, e‑Shop, FAQs, Online Newspaper Front Page, List, Personal Home Page, Search Page**. citeturn6search6turn6search10

Это хорошо ложится на: блог‑посты/ленты, витрины магазинов, страницы поиска, списки/листинги, домашние страницы.

---

### 2.3 20‑Genre Collection (MGC / Vidulin et al.) — широкая палитра (в т.ч. “error page”)

Ещё один очень известный корпус: **1539 страниц**, **20 жанров**, допускается **multi‑label** (страница может принадлежать нескольким жанрам). Набор жанров включает, например:\
**Blog, Commercial/Promotional, Community, Entertainment, Error message, FAQ, Gateway, Index, Journalistic, Official, Personal, Scientific, Shopping, User Input** и др. citeturn6search6turn3search21

Это полезно, если вам нужны “технические” типы вроде **Error message**, **Gateway**, **Index**, **User Input** (формы/ввод) и т.п., которые часто встречаются при реальном краулинге.

---

### 2.4 CORE (Corpus of Online Registers of English) — “большая” современная таксономия регистров

Если вам нужна схема, которая масштабируется на “весь веб” и даёт более лингвистически устойчивые классы, есть **CORE**:

- В работах по CORE говорится о **≈50k документов** и таксономии, покрывающей **8 главных регистров + десятки субрегистров**. citeturn7search12
- В одном из недавних описаний CORE‑схема формулируется как 8 основных классов:\
  **How‑to/Instructional, Informational Description, Informational Persuasion, Interactive Discussion, Lyrical, Narrative, Opinion, Spoken**. citeturn7search4
- Есть публичная реплика датасета/сплитов на GitHub (TurkuNLP/CORE-corpus). citeturn7search1

Важно: CORE — это скорее “регистр/тип текста”, а не “шаблон страницы” (PDP/PLP). Но для задач “статья vs инструкция vs обсуждение vs мнение” — очень сильная база.

---

### 2.5 Functional Genre Classification (Sharoff) — 7 сверх‑крупных функциональных классов

Есть подход, который сознательно жертвует детализацией ради “покрытия всего”: **7 macro‑genres**:\
**Discussion, Information, Instruction, Propaganda, Recreation, Regulation, Reporting**. citeturn5view0turn6search6

Если вам важно иметь **малое число стабильных категорий** в БД, это прям кандидат.

---

### 2.6 Leeds Web Genre Corpus и “краудсорс‑инвентари”

В статье про краудсорсинг жанров есть полезная сводка того, какие наборы ярлыков встречаются и насколько они покрывают веб. Там же описываются категории вроде **company/business homepage, educational organization homepage, personal blog/diary, online shops** и т.д. citeturn4search5turn6search7

---

## 3) “Онтологии/стандарты в самом HTML”, которые можно извлекать при парсинге (и это тоже категоризация)

Это особенно практично: вместо (или до) ML‑классификации вы можете **считать тип прямо из разметки страницы**, если сайт её ставит.

### 3.1 Schema.org как онтология типов страниц и типов контента

Schema.org даёт сразу два измерения, которые вам полезны:

**A) Тип WebPage (шаблон/роль страницы):**\
у `WebPage` есть подтипы вроде **ItemPage, CollectionPage, ProfilePage, SearchResultsPage, FAQPage, QAPage** и др. citeturn9search9turn9search2turn9search3

**B) Тип контента (CreativeWork):**

- `SocialMediaPosting` прямо говорит: “пост в соцсеть, включая tweets …” citeturn9search0
- Есть `Blog`, `BlogPosting`, `DiscussionForumPosting`, и т.д. citeturn9search8turn9search5turn9search10

Для вашей постановки это почти идеально:

- “пост в Твиттере” → `SocialMediaPosting` citeturn9search0
- “страница конкретного товара” → часто моделируют как `ItemPage` + внутри сущность `Product` (в schema‑экосистеме это стандартный паттерн) citeturn9search9
- “страница поиска” → `SearchResultsPage` citeturn9search2
- “FAQ” → `FAQPage` citeturn9search3

### 3.2 Open Graph protocol (og:type)

Open Graph тоже задаёт тип объекта через `og:type`. В “global types” есть, например, **article**, **book**, а также вертикали для video/music и пр. citeturn2view1

Это менее детально, чем schema.org, но часто проще извлечь (meta‑теги).

---

## 4) Отдельная ветка: “page types” для e‑commerce (PDP/PLP/checkout) — чаще из аналитики и clickstream

В академической маркетинговой/кликстрим‑литературе встречается очень прагматичная типизация страниц магазина. Например, в статье про типы визитов (buying/searching/browsing/knowledge-building) явно говорится о полезности **labeling pages as category pages and/or product pages**. citeturn4search16

И пара “индустриальных” источников, которые прямо фиксируют стандартный набор page types (полезно как *де‑факто* таксономия в реальных системах):

- В документации Monetate (персонализация/эксперименты) перечисляют ключевые page types: **home, index, search, product detail, cart, checkout, purchase confirmation**. citeturn12search22
- В Salesforce B2C Commerce встречается закреплённая терминология **PLP (product listing page)** и **PDP (product detail page)**. citeturn12search7

Это не “онтология для всего веба”, но если у вас много e‑commerce, это даёт простой и очень понятный слой категорий.

---

## 5) Концептуальная рамка, которая объясняет “почему типизация веба сложная”

В классических работах по *cybergenre* веб‑жанр описывают через тройку **⟨content, form, functionality⟩**, где “functionality” — то, что даёт среда (интерактивность, генерация страниц и т.п.), и предлагают таксономический взгляд на эволюцию жанров. citeturn10view0turn3search15

Практический смысл для вас: даже если вы строите “типы страниц”, у вас неизбежно будут:

- гибридные страницы (несколько функций),
- нестабильность шаблонов,
- “виртуальные”/динамически генерируемые страницы,
  и многие академические схемы поэтому поддерживают **multi‑label** или иерархии. citeturn5view1turn6search6

---

## Что из найденного ближе всего к вашей задаче (если цель — хранить 1–3 категории на страницу)

Если вы хотите максимально “прикладную” классификацию под веб‑парсинг, я бы смотрел на это как на 2 слоя (оба можно положить в БД):

1. **Page role / template layer (что это за страница как страница)**\
   Лучше всего для этого подходит **schema.org `WebPage` subtypes** (ItemPage / CollectionPage / SearchResultsPage / ProfilePage / FAQPage / QAPage …). citeturn9search9turn9search2turn9search3

2. **Content/genre layer (какой “жанр/функция текста/контента”)**\
   Тут варианты:

- компактно и функционально: **Sharoff FGC (7 macro‑genres)** citeturn5view0turn6search6
- богаче и ближе к “веб‑типам”: **KI‑04 (8 жанров)** citeturn8view0
- ещё богаче и multi‑label: **20‑Genre (MGC)** citeturn6search6turn3search21
- “большой современный стандарт де‑факто для регистров”: **CORE** citeturn7search12turn7search4

---

## Если хотите, могу продолжить в следующем шаге (без доп. вопросов с вашей стороны)

Могу:

- собрать **“кросс‑таблицу соответствий”** между: Schema.org WebPage‑типами ↔ KI‑04 ↔ 7‑Web Genres ↔ 20‑Genre (чтобы вы могли выбрать единый внутренний taxonomy);
- или подобрать **ещё 5–10 датасетов/схем**, но уже *не* жанровых, а именно **“webpage template / page type classification”** (homepage vs category/listing vs detail vs search vs profile vs thread etc.) — это отдельный пласт работ (часто вокруг DOM‑структуры и URL‑паттернов), просто он обычно хуже “канонизирован”, чем жанры.

Скажите только, какой уклон вам важнее: **универсальная схема для всего веба** или **максимально точная схема для e‑commerce/контента/соцсетей**.
