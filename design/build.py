import json, math, textwrap, uuid, html, os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
P=Path(__file__).parent
E=json.loads((P/'github-evidence.json').read_text())
BG='#09121e'; PANEL='#101e2f'; CARD='#172a3e'; WHITE='#e8f1fa'; MUTED='#a4b9ce'; GREEN='#88e0a0'; BLUE='#75c9ef'; PURPLE='#c3a5f4'; AMBER='#ffd080'; LINE='#36546d'
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
fontbold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
F=lambda s:ImageFont.truetype(font,s)
els=[]; boards=[]; cur=None; checks=[]
def base(t,x,y,w,h,**kw):
 d=dict(id=uuid.uuid4().hex[:20],type=t,x=x,y=y,width=w,height=h,angle=0,strokeColor=LINE,backgroundColor='transparent',fillStyle='solid',strokeWidth=1,strokeStyle='solid',roughness=0,opacity=100,groupIds=[],frameId=cur['id'] if cur else None,roundness=None,seed=len(els)+1,version=1,versionNonce=len(els)+100,isDeleted=False,boundElements=None,updated=1791115200000,link=None,locked=False)
 d.update(kw);els.append(d);return d

def rect(x,y,w,h,color=CARD,stroke=LINE):return base('rectangle',x,y,w,h,backgroundColor=color,strokeColor=stroke,roundness={'type':3})
def txt(x,y,s,size=22,color=WHITE,w=1450):
 lines=[]
 for line in s.split('\n'):
  words=line.split(' ');out=''
  for word in words:
   test=(out+' '+word).strip()
   if F(size).getlength(test)>w and out:lines.append(out);out=word
   else:out=test
  lines.append(out)
 value='\n'.join(lines);h=len(lines)*size*1.3
 return base('text',x,y,w,h,strokeColor=color,fontSize=size,fontFamily=2,text=value,originalText=value,textAlign='left',verticalAlign='top',containerId=None,lineHeight=1.3,autoResize=False)
def board(n,title,subtitle):
 global cur
 cur=None;x=((n-1)%3)*1720;y=((n-1)//3)*1280
 fr=base('frame',x,y,1640,1200,name=f'{n:02d} / {title}',strokeColor=LINE)
 cur=fr;boards.append(fr)
 rect(x,y,1640,1200,PANEL)
 txt(x+40,y+32,f'{n:02d}   {title}',36,GREEN,w=1560)
 txt(x+40,y+91,subtitle,19,MUTED,w=1560)
 txt(x+40,y+1157,'VOVAN OS / SENTRA     •     04.10.2026     •     Архитектурный проект, не развёрнутая система',16,MUTED)
 return x,y

def card(x,y,w,h,title,body,color=BLUE,link=None):
 r=rect(x,y,w,h);r['link']=link
 heading=txt(x+20,y+15,title,25,color,w-40)
 body_y=max(y+59,heading['y']+heading['height']+12)
 b=txt(x+20,body_y,body,20,WHITE,w-40)
 size=20
 while b['y']+b['height']>y+h-10 and size>15:
  els.pop();size-=1;b=txt(x+20,body_y,body,size,WHITE,w-40)
 for item in [r,heading,b]:item['groupIds']=[r['id']+'-group']
 heading['link']=link
 checks.append((title,b['y']+b['height']<=y+h-10))
 return r

def arrow(x,y,dx,dy,color=BLUE):
 return base('arrow',x,y,abs(dx),abs(dy),strokeColor=color,strokeWidth=2,points=[[0,0],[dx,dy]],lastCommittedPoint=None,startBinding=None,endBinding=None,startArrowhead=None,endArrowhead='arrow',elbowed=False)

roles={
'Eeklera':('EEKLERA','HTML / CSS / JS','Вариант сайта; _deploy и несколько версий.','Сравнить с eeklera-online; архивировать только после выбора версии.'),
'Eeklera_file':('Knowledge / Archive','Код + медиа + архив ПК','Obsidian, video2md, редизайн и codex.','Выборочный импорт; изолировать секреты; данные вне Git.'),
'Eeklera_new_site':('EEKLERA','HTML / CSS / JS','acting, modeling, blog, media, UI-kit.','Источник нового дизайна; отдельная проверка перед слиянием.'),
'vovan-app':('Social','FastAPI / React / SQLite','Соцсеть: чаты, посты, звонки, игры, роли.','Подключить API, БД и uploads; кандидат основного Social.'),
'lera-app':('EEKLERA Community','FastAPI / React / SQLite','Telegram Mini App: сообщество, платежи, игры.','Сохранить Telegram-вход и уникальные функции; не удалять.'),
'eeklera-site-archive':('Archive','Статика / медиа / SQLite','Исторический сайт и chat.db.','Холодный архив; импорт с происхождением и дедупликацией.'),
'orion':('AI Agents','Node.js / JSON / Obsidian','Агент, память, Moltbook, Telegram, pm2.','Изолированный worker; память в data; облачные вызовы по политике.'),
'lera-assistant':('EEKLERA Assistant','Node.js / Telegram','Gemini, видео, Google, база знаний.','Worker + AI Gateway; доступ к Knowledge по правам.'),
'lera-vault-old':('Knowledge','Markdown / Obsidian','Старый vault и отчёт качества заметок.','Импорт с hash и source; не затирать новые заметки.'),
 'twitch-manager':('Streaming','Node / React / SQLite','Панель агентов Twitch; README отмечает недоделки IRC.','Подключить как разработку; не считать ботами online.'),
'pomoshnik-bot':('Automation','Python / Telegram','Задачи Claude Code, голосовые, Google OAuth.','Адаптер задач и ролей; внешние команды отдельно от импорта.'),
'modbot':('Streaming','Node.js / JSON','Модерация Twitch, команды, таймеры, AI, логи.','Панель Streaming; JSON сначала читать через адаптер.'),
'studio':('Sites','HTML / CSS / JS','Витрина услуг, кейсы, изображения.','Каталог сайтов + независимый деплой.'),
'graph':('Control Center','HTML / JS / graph data','Локальные карты кода 2D/3D.','Вкладка карты; данные из реестра и анализа исходников.'),
'exchange':('Files','Node.js / файлы','Обменник с чатом и передачей файлов.','Встроить в Files; ACL, версии, ссылки на объекты.'),
'auth-gateway':('Identity','Python / nginx auth_request','Старый SSO и файловый портал.','Адаптер на переходный период; целевой OIDC + RBAC.'),
'airrock':('Sites','React / Vite','Лендинг-магазин колонки; демо по README.','Записать как проект; факт публичного запуска проверить.'),
'server-misc':('Control / Mini Apps','Python / Node / HTML','13 папок сервисов со старого сервера.','Каждой папке — свой project_id, parent_id = server-misc.'),
'video2md-phone':('Media / Knowledge','Python / ffmpeg / Termux','Видео → транскрипт → проверка → Obsidian.','Сохранить телефонный узел; импорт результатов в Knowledge.'),
'eeklera-obsidian':('Knowledge','Пустой репозиторий','GitHub size = 0; содержимое не получено.','Карточка planned; реальный vault искать на устройстве.'),
'sentra':('Platform Core','Пустой репозиторий','GitHub size = 0; содержимое не получено.','Предлагаемое место ядра и панели, пока не реализовано.'),
'obsidian-systems':('Knowledge','Пустой репозиторий','GitHub size = 0; содержимое не получено.','Карточка planned; назначение уточнить.'),
'business-ideas':('Ideas','Пустой репозиторий','GitHub size = 0; содержимое не получено.','Карточка идеи; не выдавать за готовый сервис.'),
'eeklera-online':('EEKLERA','HTML / CSS / JS','Снимок основного сайта от 29.09.2026 по README.','Кандидат канонической версии; сверить с текущим сервером.'),
 'terraria-server':('Games','C# / TShock / Docker','Плагины, конфиги, pull-deploy, rollback.','Оставить свой runtime; читать deploy-status и health.'),
'Kabluk':('Games','Worker / D1 / Three.js','Онлайн-город; есть self-host адаптер и локальная SQLite.','Выбрать D1 или self-host как единственный источник записей.')}

x,y=board(1,'Вся система на одном листе','Локальная платформа управления • реальные источники • единый поиск • автономная работа')
card(x+40,y+150,480,220,'ФАКТЫ GITHUB','26 репозиториев доступны\n22 с содержимым / 4 с size = 0\n25 private / 1 public\nСписок и корневые каталоги проверены.',GREEN)
card(x+560,y+150,500,220,'ЧТО ЕЩЁ НЕ ПРОВЕРЕНО','Текущие процессы, домены, серверные БД, объём диска и бэкапы.\nREADME — описание проекта, не мониторинг сервера.',AMBER)
card(x+1100,y+150,500,220,'КАК ЧИТАТЬ КАРТУ','Зелёный: проверенные метаданные.\nГолубой: предлагаемая архитектура.\nФиолетовый: домен / интеграция.\nЖёлтый: ограничения и решения.',PURPLE)
card(x+40,y+430,430,230,'ИСТОЧНИКИ','GitHub • серверы • ноутбук\nТелефон / Obsidian • внешние API\nКод, файлы, БД и статусы\nКаждый факт имеет источник.')
card(x+600,y+425,460,250,'SENTRA / VOVAN OS','Локальная панель + Core API\nРеестр проектов и связей\nПользователи, поиск, задачи\nКаталог файлов и баз',GREEN)
card(x+1180,y+430,420,230,'МОДУЛИ','EEKLERA • Social • Sites\nAI Agents • Streaming • Games\nMini Apps • Knowledge • Files',PURPLE)
arrow(x+470,y+550,130,0);arrow(x+1060,y+550,120,0)
card(x+40,y+745,740,310,'ЛОКАЛЬНО — ПО УМОЛЧАНИЮ','Панель открывается на ПК / в домашней сети.\nPostgreSQL, файлы и поисковый индекс хранятся локально.\nПри появлении сети агент скачивает разрешённые обновления.\nБез интернета доступны последние снимки, заметки и локальные сервисы.\nВнешние AI/API офлайн недоступны — это видно в интерфейсе.')
card(x+820,y+745,780,310,'ЕДИНЫЙ КАТАЛОГ, НЕ ОБЯЗАТЕЛЬНО ЕДИНЫЙ РЕПОЗИТОРИЙ','Начать с подключения существующих репозиториев и сервисов.\nНезавершённые проекты тоже получают карточку и статус.\nПеренос кода в monorepo — отдельный последующий выбор.\nНаличие проекта, его запуск и свежесть данных — разные поля.\nЦифры online, GB и uptime из изображения не используются как факты.',AMBER)

x,y=board(2,'Архитектура и границы доступа','Целевая схема • публичные приложения продолжают жить отдельно от локальной панели')
card(x+40,y+150,420,190,'БРАУЗЕР / УСТРОЙСТВА','ПК, телефон, домашняя LAN\nHTTPS + локальное имя\nУдалённый доступ через VPN')
card(x+570,y+150,470,190,'CONTROL CENTER','Dashboard • проекты • карта\nФайлы • базы • логи • задачи\nСинхронизация • настройки',GREEN)
card(x+1150,y+150,450,190,'IDENTITY / OIDC','Локальный вход работает офлайн\nRBAC + права по project_id\nСвязать внешние аккаунты явно')
arrow(x+460,y+240,110,0);arrow(x+1040,y+240,110,0)
card(x+320,y+430,1000,230,'CORE API / МОДУЛЬНОЕ ЯДРО','Project Registry • Search • Files • Tasks • Notifications\nIntegration Registry • Audit • Sync Scheduler • AI Gateway\nCore хранит каталог и ссылки на данные. Адаптеры знают форматы проектов.\nСекреты доступны только серверной стороне; в UI — ссылки и состояния.')
arrow(x+805,y+340,0,90)
for i,(t,b) in enumerate([
('ЛОКАЛЬНЫЕ ДАННЫЕ','PostgreSQL: каталог, задачи, снимки\nФайловое / S3-совместимое хранилище\nИндекс можно пересоздать'),
('WORKERS / АДАПТЕРЫ','GitHub, SSH/VPN, REST, exports\nVideo2MD, Orion, Telegram, Twitch\nОчередь, retries, лимиты ресурсов'),
('ПУБЛИЧНЫЕ RUNTIME','VPS: сайты, Social, Terraria\nKabluk: D1 или self-host\nЛокально — read-only снимки')]):
 card(x+40+i*530,y+800,500,240,t,b,PURPLE)
 arrow(x+550+i*250,y+660,(x+290+i*530)-(x+550+i*250),140)
txt(x+40,y+1090,'Интернет не получает прямой доступ к локальной БД. Команды управления идут через отдельный контролируемый канал.',20,AMBER)

x,y=board(3,'Как обновлять локальную систему','Загрузка при старте и восстановлении связи • чтение отдельно от деплоя и команд')
steps=[('1 / ОБНАРУЖИТЬ СЕТЬ','Запуск → проверка источников\nПланировщик + кнопка обновить\nНет связи → локальный снимок'),('2 / ЗАБРАТЬ ИЗМЕНЕНИЯ','GitHub API: страницы + ETag\ngit fetch в отдельную копию\nVPS: разрешённый export / API'),('3 / ПРОВЕРИТЬ','Схема, hash, лимиты размера\nКарантин некорректных файлов\nНичего не исполнять при импорте'),('4 / СОХРАНИТЬ','Staging → транзакция → снимок\nsource_id + revision + observed_at\nПовтор не создаёт дубликаты'),('5 / ОБНОВИТЬ ПАНЕЛЬ','Индекс и связи проектов\nПоказать last_success / ошибки\nСохранить предыдущую версию')]
for i,(t,b) in enumerate(steps):
 card(x+40+i*315,y+180,290,250,t,b)
 if i<4:arrow(x+330+i*315,y+305,25,0)
card(x+40,y+490,740,270,'КТО ВЛАДЕЕТ ДАННЫМИ','GitHub — код и метаданные репозитория.\nРабочая БД проекта — пользователи и игровые / бизнес-данные.\nЛокальное ядро — каталог, заметки владельца, история синхронизации.\nФайлы — версии по hash; происхождение сохраняется.\nРедактирование удалённых данных — только через API владельца.')
card(x+820,y+490,780,270,'СБОИ И КОНФЛИКТЫ','Timeout / 429 → backoff с jitter, учёт Retry-After.\nОбрыв сети → продолжить с checkpoint, оставить старый снимок.\nУдаление источника → tombstone, не удалять локальный архив сразу.\nЛокальные изменения кода → отдельная ветка; не делать reset.\nНет доступа → unknown / stale, не «проект удалён».',AMBER)
card(x+40,y+810,740,260,'ПРОФИЛИ ПРИВАТНОСТИ','Строго локальный: исходящие AI-запросы отключены.\nСинхронизация: только выбранные GitHub и серверные источники.\nОблачный AI: отдельный opt-in по проекту и типу данных.\nПубличные сайты не имеют маршрута к локальному storage.\nЛокальный frontend без CDN, аналитики и внешних шрифтов.')
card(x+820,y+810,780,260,'КОМАНДЫ — ОТДЕЛЬНЫЙ ПОТОК','Кнопка → проверка прав → plan → подтверждение опасной операции\n→ очередь → разрешённый серверный runner → audit + результат.\nidempotency_key, срок действия и версия целевого deployment.\nУстаревшую команду после офлайн не выполнять автоматически.\nОбновление каталога само по себе никогда не запускает деплой.',PURPLE)

# Full repository cards: two boards, thirteen each, compact two-column layout
rs=E['repositories']
for bi in range(2):
 x,y=board(4+bi,f'Реестр GitHub / {bi+1} из 2','Все 26 доступных репозиториев • название карточки содержит ссылку на GitHub • назначение справа — предложение')
 for j,r in enumerate(rs[bi*13:(bi+1)*13]):
  col=j%2;row=j//2;xx=x+40+col*790;yy=y+145+row*139
  domain,stack,desc,act=roles[r['name']]
  rr=rect(xx,yy,760,127);rr['link']=r['url']
  txt(xx+14,yy+9,r['name']+'  →  '+domain,21,GREEN,732)
  txt(xx+14,yy+39,f"{r['visibility']}  •  GitHub size {r['size_kib']:,} KiB  •  {stack}",16,MUTED,732)
  txt(xx+14,yy+65,desc+'\n'+act,17,WHITE,732)
 txt(x+40,y+1125,'GitHub size — размер по API, не объём рабочей БД или диска. Runtime всех проектов требует отдельного опроса.',16,AMBER)

x,y=board(6,'Вложенные проекты и сервер без Git','server-misc: 13 каталогов подтверждены • роль описана в README • запуск не проверен')
misc=[('server-admin','Infrastructure','Администрирование сервера → вкладка Servers'),('gate','Infrastructure','Статистика и VPN → инфраструктурный адаптер'),('tasker','Tasks','Доска задач → задачи с project_id'),('team','Tasks / GitHub','Канбан веток → связи Task ↔ Branch'),('bot-panel','Bots','Управление pomoshnik-bot → панель ботов'),('agents','AI Agents','Рабочая область команды → workers и логи'),('bday-quest','Mini Apps / Games','Telegram-квест; quest.db → отдельный модуль'),('linux-academy','Mini Apps / Learn','Уроки и терминал → локальное учебное приложение'),('shopper','Mini Apps / Shop','Python API и data.json → отдельный адаптер'),('shopper-www','Mini Apps / Shop','Витрина → интерфейс Shopper'),('mp3-converter','Media / Forge','mp4 → mp3 → очередь медиаобработки'),('hashtag-tracker','Analytics','Снимки трендов → временные ряды'),('www-misc','Sites / Experiments','Хаб, 3D, колесо, AI-лента → вложенные карточки')]
for i,(n,d,b) in enumerate(misc):
 yy=y+149+i*54
 txt(x+45,yy,n,21,GREEN,300);txt(x+350,yy,d,19,PURPLE,300);txt(x+655,yy,b,19,WHITE,900)
card(x+40,y+900,740,210,'СЕРВЕРНЫЕ ПРОЕКТЫ БЕЗ РЕПОЗИТОРИЯ','Read-only инвентаризация: Docker / systemd / pm2, nginx, пути.\nДля каждого: project_id, host_id, runtime, volumes, DB, endpoint.\nНет Git → source_type=server; maturity=unknown / draft.\nСекреты и содержимое БД не выгружать в общий каталог.')
card(x+820,y+900,780,210,'ГРАНИЦА ПРОВЕРКИ','Доступ к самому серверу в этой работе не выполнялся.\nЧисло текущих процессов и серверных проектов неизвестно.\nИсторические адреса из README не подтверждают текущий хост.\nНовые проекты добавляются без обязательного создания Git-репозитория.',AMBER)

x,y=board(7,'Модель данных и владельцы записей','Целевая логическая модель • PostgreSQL для ядра • базы приложений подключаются постепенно')
entities=[('PROJECT','id PK • parent_id FK → PROJECT\nname • domain • maturity\nrepository_id? • owner_id\nplanned / development / archived'),('REPOSITORY / SOURCE','repo_id PK • provider_id UNIQUE\nurl • visibility • branch • head_sha\nsource_id PK • type • project_id FK\nrevision • observed_at • freshness'),('HOST / SERVICE','host_id PK • name • environment\nservice_id PK • project_id FK\nhost_id FK • runtime • endpoint\nhealth_status • last_seen'),('DATASET / OBJECT','dataset_id PK • project_id FK\nowner_service_id • engine • locator\nobject_id PK • hash • version\nsource_id FK • ACL • sensitivity'),('SYNC_RUN / SNAPSHOT','run_id PK • source_id FK • cursor\nstarted_at • last_success • error\nsnapshot_id PK • revision • hash\nUNIQUE(source_id, revision)'),('TASK / DEPLOYMENT / AUDIT','task_id PK • project_id FK • status\ndeploy_id • service_id • commit\naudit_id • actor • action • result\nidempotency_key • timestamp')]
for i,(t,b) in enumerate(entities):card(x+40+(i%3)*530,y+160+(i//3)*305,500,255,t,b)
for i in range(3):arrow(x+290+i*530,y+415,0,50)
card(x+40,y+810,740,285,'СХЕМЫ И ДОСТУП','core: users, identities, roles, projects, sources, tasks, audit.\nknowledge: documents, versions, chunks, citations, entities, edges.\nmonitoring: observations, sync_runs, health, deployments.\nПозже: social / streaming / ai / games — только после миграции.\nFK внутри владельца данных; между сервисами — устойчивые ID.\nСвязь аккаунтов по подтверждению, не по совпадению nickname.')
card(x+820,y+810,780,285,'СУЩЕСТВУЮЩИЕ БАЗЫ НЕ СЛИВАТЬ ВСЛЕПУЮ','vovan.db / lera.db • Twitch data.sqlite • quest.db\nModBot JSON • Orion memory • Kabluk D1 или SQLite\nИзначально: read-only экспорт + ссылка на источник.\nSQLite копировать через backup API, учитывая WAL; не живой файл.\nМиграция: mapping ID → dry run → counts / FK / hashes → cutover.\nОдна authoritative БД на домен; без двустороннего слияния SQL.',AMBER)

x,y=board(8,'Файлы, знания и достоверность','От исходного видео или заметки до проверяемого факта • данные вне репозитория платформы')
flow=[('ИСТОЧНИКИ','Eeklera_file • lera-vault-old\nlera-assistant/data • Orion\nТелефон / Video2MD / uploads'),('IMMUTABLE RAW','Исходный файл + sha256\nДата импорта + source + revision\nВерсии, ACL и путь в storage'),('ОБРАБОТКА','Текст / OCR / транскрипт\nChunks + ссылки + таймкоды\nAI-выводы помечать как generated'),('ПРОВЕРКА / ПОИСК','reviewed / unreviewed / rejected\nПолнотекстовый поиск + граф\nОтвет содержит ссылку на оригинал')]
for i,(t,b) in enumerate(flow):
 card(x+40+i*395,y+170,370,255,t,b)
 if i<3:arrow(x+410+i*395,y+297,25,0)
card(x+40,y+490,740,305,'DATA / НА ДИСКЕ ИЛИ NAS','repositories/ — отдельные read-only кэши Git\nraw/ — неизменённые импорты, раздельно по источникам\nmedia/ • uploads/ • video2md/ • orion-memory/\ndatabases/ — рабочие volumes и согласованные exports\nquarantine/ — спорные или отклонённые объекты\nbackups/ — локальные снимки; ещё одна копия на другом носителе')
card(x+820,y+490,780,305,'НЕ ПОДМЕНЯТЬ ФАКТЫ ГЕНЕРАЦИЕЙ','Отделять сказанную цитату от AI-интерпретации.\nКаждый фрагмент: source, document_version, page / timecode.\nПоиск выполняет ACL-фильтрацию до передачи контекста модели.\nДубликаты по hash объединяют хранение, но сохраняют источники.\nИзменение исходника создаёт новую версию и переиндексацию.\nИндекс / embeddings — производные, их можно пересоздать.',AMBER)
card(x+40,y+850,740,240,'БЭКАП И ВОССТАНОВЛЕНИЕ','Согласованный manifest: версия БД + список объектов + hash.\nШифрованная копия на отдельный диск / NAS, ключ отдельно.\nПроверка восстановления в чистую среду и выборочных файлов.\nПолитику retention / RPO / RTO задать по доступному диску.')
card(x+820,y+850,780,240,'ПЕРЕД ИМПОРТОМ EEKLERA_FILE','README явно сообщает о credentials, session keys, HF token и SSH.\nЗначения ключей не читались и в схему не включены.\nДо подключения: проверить актуальность и отозвать / заменить их;\nсекреты исключить из общего поиска и импорта.\nПереписывание истории — отдельная операция, здесь не выполнялась.',AMBER)

x,y=board(9,'Панель управления / макет','Визуальное направление из твоего изображения: тёмная тема, зелёные акценты, карта в центре')
rect(x+40,y+155,250,945,'#0c1825');txt(x+60,y+179,'VOVAN OS',30,GREEN,220)
txt(x+60,y+250,'Главная\n\nПроекты\n\nAI-агенты\n\nСайты и игры\n\nБоты\n\nФайлы\n\nБазы данных\n\nДеплои\n\nЛоги\n\nСинхронизация',22,WHITE,215)
rect(x+315,y+155,1285,65);txt(x+335,y+174,'Поиск по проектам, файлам и задачам…                         Локально  •  Синхронизировать',22,MUTED,1245)
for i,(t,b) in enumerate([('GitHub','26 доступно'),('Содержимое','22 репозитория'),('Нулевой размер','4 репозитория'),('Runtime','Не проверен')]):
 card(x+315+i*325,y+245,310,130,t,b,GREEN if i<3 else AMBER)
rect(x+315,y+400,860,450);txt(x+340,y+420,'Карта системы',27,WHITE,800)
card(x+585,y+555,310,150,'SENTRA','Реестр + связи + поиск',GREEN)
for xx,yy,t in [(x+340,y+490,'EEKLERA'),(x+910,y+490,'Social'),(x+340,y+690,'Games'),(x+910,y+690,'AI / Bots')]:card(xx,yy,235,110,t,'Статус: неизвестен',PURPLE)
arrow(x+575,y+545,30,30);arrow(x+910,y+545,-30,30);arrow(x+575,y+740,30,-45);arrow(x+910,y+740,-30,-45)
card(x+1200,y+400,400,205,'Git / обновления','Источник: GitHub API\nПоследний импорт: 04.10.2026\nHead SHA — после синхронизации\nНе показывать выдуманные коммиты')
card(x+1200,y+625,400,225,'Состояние источников','VPS: не подключён\nЛокальные БД: не подключены\nОблачные API: не проверены\nOnline / offline / stale отдельно',AMBER)
card(x+315,y+880,625,220,'Проекты','EEKLERA   •   Social   •   Kabluk   •   Terraria\nOrion   •   Sites   •   Streaming   •   Mini Apps\nФильтры: домен / зрелость / runtime / источник\nКарточка → обзор, данные, код, логи, задачи')
card(x+965,y+880,635,220,'Задачи подключения','1. Инвентаризация текущего сервера\n2. Подключить read-only адаптеры\n3. Проверить базы и backups\nПоказатели GB / uptime появятся после измерений',AMBER)

x,y=board(10,'Карточка проекта и контракт подключения','Один интерфейс для работающего сайта, игры, архива и ещё не запущенной идеи')
card(x+40,y+155,930,220,'KABLUK / КАБЛУКОВСК','Источник: V0van200/Kabluk • назначение: онлайн-город\nREADME: Three.js, Worker/D1; также есть self-host и локальная SQLite\nРепозиторий подтверждён; текущий runtime не проверен\nВкладки: Обзор | Код | Данные | Логи | Деплои | Задачи | Связи',GREEN,'https://github.com/V0van200/Kabluk')
card(x+1010,y+155,590,220,'ДЕЙСТВИЯ','Открыть репозиторий • обновить каталог\nЭкспортировать снимок • посмотреть схему\nДеплой / перезапуск активны только после\nнастройки runner, прав и целевого сервиса.')
card(x+40,y+425,740,460,'PROJECT MANIFEST / ПРЕДЛОЖЕНИЕ','id: kabluk\nname: Каблуковск\ndomain: games\nsources: [github:V0van200/Kabluk]\nruntime: worker-or-self-host\nauthority: выбрать при подключении\ndatasets: [game-db]\nhealth_adapter: не настроен\ncapabilities: [repo.read]\nsecret_refs: []\nНе заполнять вымышленный health URL.')
card(x+820,y+425,780,460,'ЕДИНЫЕ ПОЛЯ ДЛЯ КАЖДОГО ПРОЕКТА','Identity: устойчивый id, имя, домен, parent_id, владелец.\nSources: repository, branch, SHA, server_path / API, observed_at.\nMaturity: idea / planned / development / production / archived.\nRuntime: unknown / online / degraded / offline.\nData: dataset, engine, owner, sensitivity, retention, backup.\nFreshness: live / snapshot / stale, last_success, последняя ошибка.\nRelations: depends_on, derived_from, deploys_to, uses_dataset.\nCapabilities: read, logs, export, deploy, restart — явный список.\nНовое подключение по умолчанию даёт только чтение.')
card(x+40,y+935,1560,170,'ПОЧЕМУ ЭТО РАБОТАЕТ ДЛЯ НЕЗАВЕРШЁННЫХ ПРОЕКТОВ','Даже без Git, домена или процесса карточка хранит замысел, папку, документы, задачи и связи. Поля могут быть unknown.\nДля server-misc/shopper и других подпроектов — свои ID и родитель. Архив остаётся доступен для поиска без запуска сервиса.',PURPLE)

x,y=board(11,'Размещение, репозитории и эксплуатация','Сначала собрать управляющий слой; перенос приложений и баз не является условием первой версии')
card(x+40,y+160,740,380,'ЛОКАЛЬНЫЙ УЗЕЛ / SENTRA','Reverse proxy → UI + Core API\nIdentity → локальный пользователь и роли\nPostgreSQL → каталог, sync, tasks, audit\nStorage → bind mount / NAS, пути вне исходников\nWorkers → GitHub, imports, search, media\nCompose как начальный вариант, лимиты CPU / RAM / disk\nLAN-доступ ограничен firewall; административные порты закрыты\nОтказ WAN не блокирует вход и просмотр локальных данных.')
card(x+820,y+160,780,380,'VPS / ВНЕШНИЕ УЗЛЫ','Существующие сервисы продолжают работу независимо.\nVPS-адаптер отдаёт разрешённые метаданные / snapshots.\nRunner принимает только заранее заданные команды.\nTerraria: сохранить build → save world → restart → rollback.\nKabluk: выбрать D1 или self-host; переносить данные отдельно.\nТелефон: Video2MD экспортирует результат при доступной сети.\nTelegram / Twitch / облачные AI требуют внешнего соединения.')
card(x+40,y+595,740,385,'КОД ПЛАТФОРМЫ / ПРЕДЛОЖЕНИЕ','sentra/\n  apps/control-center\n  services/core-api • sync-worker • identity-adapter\n  packages/schemas • ui • connectors\n  registry/projects • registry/datasets\n  infra/compose • proxy • backup\n  docs/architecture • runbooks • migrations\nРепозитории приложений сначала остаются самостоятельными.\nДанные, ключи, uploads и дампы не входят в этот репозиторий.')
card(x+820,y+595,780,385,'ЖИЗНЕННЫЙ ЦИКЛ РЕЛИЗА','Commit → CI checks → versioned artifact → staging\n→ backup / migration plan → deploy → health → active.\nОшибка → rollback приложения; БД — совместимые миграции\nили восстановление по заранее проверенному плану.\nЛоги по project_id / service_id / run_id, с удалением секретов.\nСигналы: sync age, failed jobs, disk free, backup age, health.\nСроки хранения логов и квоты защищают локальный диск.\nЦентральная панель не должна быть условием работы игр и сайтов.',PURPLE)
txt(x+40,y+1050,'Публичный деплой этой схемой не выполняется. Ни репозитории, ни серверы, ни работающие базы в ходе работы не менялись.',22,AMBER,1560)

x,y=board(12,'Порядок реализации и доказательства','Начальный результат — полезный локальный каталог; перенос данных — после инвентаризации и проверок')
phases=[('01 / ИНВЕНТАРИЗАЦИЯ','Зафиксировать 26 repos и 13 подпроектов; описать текущие VPS и папки без Git.','Готово, когда у каждого объекта есть source и неизвестные поля отмечены.'),('02 / ЛОКАЛЬНЫЙ КАТАЛОГ','UI + Core + PostgreSQL + storage; импорт GitHub и ручные карточки.','Каталог, поиск и вход работают при выключенном интернете.'),('03 / СИНХРОНИЗАЦИЯ','Read-only adapters, snapshots, retry, checkpoints, дата свежести.','Обрыв и повтор импорта не теряют данные и не создают дубликаты.'),('04 / ЗНАНИЯ И ФАЙЛЫ','Разобрать архивы, Video2MD, Orion; версии, hash, ACL, citations.','Поисковый результат ведёт к оригиналу; приватное недоступно чужой роли.'),('05 / ПОДКЛЮЧЕНИЕ RUNTIME','Health и логи; затем runner для выбранных сервисов.','Статусы измеряются; пробный deploy и rollback проверены.'),('06 / КОНСОЛИДАЦИЯ','Выбрать версии EEKLERA; перенести нужные функции и БД по одной.','Сверены ID, counts, файлы и восстановление; архивы сохранены.')]
for i,(t,b,c) in enumerate(phases):card(x+40+(i%2)*790,y+150+(i//2)*225,760,205,t,b+'\nКритерий: '+c)
card(x+40,y+855,740,250,'ИСТОЧНИКИ ЭТОЙ КАРТЫ','GitHub connector: полный список (26 + пустая следующая страница).\nКорневые contents: 22 доступны; 4 без содержимого, size = 0.\n21 README: роли и исторические сведения; Eeklera_new_site — пути.\nСсылки на repos встроены в карточки листов 04–05.\nСнимок метаданных и README: github-evidence.json.',GREEN)
card(x+820,y+855,780,250,'ЧТО НЕ ВЫДАЁТСЯ ЗА ПРОВЕРЕННЫЙ ФАКТ','Проценты дублей 97,5% / 96% и оценка готовности 60–70%\nиз прошлого ответа здесь не подтверждались и не используются.\nСовпадение ряда корневых Git SHA Eeklera / eeklera-online видно;\nвыбор канонической версии требует сверки сервера и изменений.\nЭто архитектура и макет; production-данные и runtime не аудированы.',AMBER)

scene={'type':'excalidraw','version':2,'source':'https://excalidraw.com','elements':els,'appState':{'viewBackgroundColor':BG,'gridSize':None,'scrollX':45,'scrollY':45,'zoom':{'value':0.62}},'files':{}}
(P/'Vovan-OS.excalidraw').write_text(json.dumps(scene,ensure_ascii=False,indent=2))
# Native scene plus portable SVG overview and per-board PDF/PNG, all from the same geometry.
W,H=5080,5040
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="{BG}"/>']
for e in els:
 if e['type']=='frame':continue
 xx,yy,w,h=e['x'],e['y'],e['width'],e['height'];co=e['strokeColor']
 if e['type']=='rectangle':svg.append(f'<rect x="{xx}" y="{yy}" width="{w}" height="{h}" rx="12" fill="{e["backgroundColor"]}" stroke="{co}"/>')
 elif e['type']=='text':
  for j,line in enumerate(e['text'].split('\n')):svg.append(f'<text x="{xx}" y="{yy+e["fontSize"]+j*e["fontSize"]*1.3}" font-family="DejaVu Sans,Arial,sans-serif" font-size="{e["fontSize"]}" fill="{co}">{html.escape(line)}</text>')
 elif e['type']=='arrow':
  dx,dy=e['points'][-1];ex,ey=xx+dx,yy+dy;a=math.atan2(dy,dx)
  svg.append(f'<path d="M{xx},{yy} L{ex},{ey} M{ex-12*math.cos(a-.5)},{ey-12*math.sin(a-.5)} L{ex},{ey} L{ex-12*math.cos(a+.5)},{ey-12*math.sin(a+.5)}" fill="none" stroke="{co}" stroke-width="2"/>')
svg.append('</svg>');(P/'Vovan-OS.svg').write_text('\n'.join(svg))
pdfmetrics.registerFont(TTFont('DV',font));pdf=canvas.Canvas(str(P/'Vovan-OS.pdf'),pagesize=(1640,1200))
thumbs=[]
for b in boards:
 im=Image.new('RGB',(1640,1200),BG);d=ImageDraw.Draw(im)
 pdf.setFillColor(BG);pdf.rect(0,0,1640,1200,fill=1,stroke=0)
 for e in els:
  if e.get('frameId')!=b['id']:continue
  xx,yy=e['x']-b['x'],e['y']-b['y'];w,h=e['width'],e['height'];co=e['strokeColor']
  if e['type']=='rectangle':
   d.rounded_rectangle((xx,yy,xx+w,yy+h),12,fill=e['backgroundColor'],outline=co)
   pdf.setFillColor(e['backgroundColor']);pdf.setStrokeColor(co);pdf.roundRect(xx,1200-yy-h,w,h,12,fill=1,stroke=1)
  elif e['type']=='text':
   size=e['fontSize'];pdf.setFont('DV',size);pdf.setFillColor(co)
   for j,line in enumerate(e['text'].split('\n')):
    ly=yy+j*size*1.3;d.text((xx,ly),line,font=F(size),fill=co);pdf.drawString(xx,1200-ly-size,line)
  elif e['type']=='arrow':
   dx,dy=e['points'][-1];ex,ey=xx+dx,yy+dy;a=math.atan2(dy,dx);pts=[(ex-12*math.cos(a-.5),ey-12*math.sin(a-.5)),(ex,ey),(ex-12*math.cos(a+.5),ey-12*math.sin(a+.5))]
   d.line([(xx,yy),(ex,ey)],fill=co,width=2);d.line(pts,fill=co,width=2)
   pdf.setStrokeColor(co);pdf.line(xx,1200-yy,ex,1200-ey)
   for aa,bb in zip(pts,pts[1:]):pdf.line(aa[0],1200-aa[1],bb[0],1200-bb[1])
  if e.get('link'):pdf.linkURL(e['link'],(xx,1200-yy-h,xx+w,1200-yy),relative=0)
 im.save(P/f'board-{len(thumbs)+1:02d}.png');thumbs.append(im.resize((656,480)));pdf.showPage()
pdf.save()
overview=Image.new('RGB',(2016,1980),BG)
for i,im in enumerate(thumbs):overview.paste(im,((i%3)*680,(i//3)*500))
overview.save(P/'Vovan-OS-preview.png')
registry=[]
for r in rs:
 domain,stack,desc,action=roles[r['name']]
 registry.append({**r,'domain_proposed':domain,'stack_from_readme_or_paths':stack,'description':desc,'integration_proposed':action,'runtime_status':'unknown','evidence':'github-metadata-and-root' if r['size_kib']==0 else 'github-metadata-root-and-readme' if r['name']!='Eeklera_new_site' else 'github-metadata-and-root'})
(P/'project-registry.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2))
assert len(rs)==26 and len(roles)==26
assert len({e['id'] for e in els})==len(els)
assert all(ok for _,ok in checks),[name for name,ok in checks if not ok]
assert all(e.get('frameId') is None or e['frameId'] in {b['id'] for b in boards} for e in els)
print('Created:',len(boards),'boards,',len(els),'editable elements;',len(checks),'cards fit.')
