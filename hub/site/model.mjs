export const esc = (v='') => String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const safeURL=v=>{try{const u=new URL(v);return ['https:','http:'].includes(u.protocol)?u.href:null}catch{return null}};
export function bytes(n, digits=1){if(!Number.isFinite(n))return '—';if(n===0)return '0 Б';const i=Math.min(4,Math.floor(Math.log(Math.abs(n))/Math.log(1024)));return (n/1024**i).toLocaleString('ru',{maximumFractionDigits:digits})+' '+['Б','КиБ','МиБ','ГиБ','ТиБ'][i]}
export function when(v,full=false){if(!v)return 'Неизвестно';const d=new Date(v);if(Number.isNaN(d.valueOf()))return String(v);return new Intl.DateTimeFormat('ru',{day:'2-digit',month:'2-digit',...(full?{year:'numeric'}:{}),hour:'2-digit',minute:'2-digit',timeZone:'UTC'}).format(d)+' UTC'}
export const kindLabels={game:'Игра',site:'Сайт',app:'Приложение',bot:'Бот',agents:'ИИ-агент',infra:'Инфраструктура',service:'Сервис',services:'Сервисы',platform:'Платформа',archive:'Архив',idea:'Идея / архив',tool:'Инструмент',admin:'Панель управления',content:'Контент и медиа'};
export function validateSnapshot(d){
 const numeric=(v,nullable=false)=> (nullable&&(v===null||v===undefined))||(typeof v==='number'&&Number.isFinite(v)&&v>=0);
 const bad=()=>{throw Error('Некорректные числовые показатели или идентификаторы снимка.')};

 if(!d||d.version!==1||!Array.isArray(d.repos)||!d.links?.groups||!d.servers||!Array.isArray(d.graph?.nodes)||!Array.isArray(d.graph?.edges))throw Error('Нужен полный снимок Vovan OS версии 1. Выберите snapshot.json или экспорт из панели.');
 if(d.repos.length>2000||d.graph.nodes.length>10000||d.graph.edges.length>100000)throw Error('Снимок слишком большой.');
 for(const r of d.repos)if(typeof r.name!=='string'||!numeric(r.size_kib))throw Error('Некорректный репозиторий.');
 for(const [id,g] of Object.entries(d.links.groups)){
  if(!/^[\w.-]+$/.test(id)||!g||typeof g.name!=='string')throw Error('Некорректная карточка проекта.');
  for(const field of ['services','docker','domains','databases','timers','paths'])if(g[field]!=null&&(!Array.isArray(g[field])||g[field].some(x=>typeof x!=='string')))throw Error('Некорректный список '+field);
 }
 for(const [serverId,s] of Object.entries(d.servers)){
  if(!/^[\w-]+$/.test(serverId))bad();

  if(!s.host||!Array.isArray(s.services)||!Array.isArray(s.databases)||!Array.isArray(s.host.disks)||!Array.isArray(s.docker))throw Error('Некорректная структура сервера.');
  const h=s.host;
  if(!numeric(h.cpus)||!h.cpus||!numeric(h.ram_total)||!h.ram_total||!numeric(h.ram_available)||!numeric(h.uptime_s)||!Array.isArray(h.load)||h.load.length!==3||h.load.some(v=>!numeric(v)))bad();
  for(const disk of h.disks)if(!numeric(disk.size)||!disk.size||!numeric(disk.used)||!numeric(disk.avail)||typeof disk.mount!=='string')bad();
  for(const service of s.services)if(typeof service.name!=='string'||typeof service.state!=='string'||!numeric(service.memory,true)||!numeric(service.restarts,true))bad();
  for(const app of s.apps||[])if(!numeric(app.size,true))bad();
  for(const backup of s.backups||[])if(!numeric(backup.size,true)||!numeric(backup.files,true))bad();
  for(const db of s.databases){
   if(!numeric(db.size,true))bad();
   for(const table of db.tables||[])if(typeof table.table!=='string'||!numeric(table.rows,true))bad();
if(db.tables!=null&&!Array.isArray(db.tables))throw Error('Некорректная схема базы.');for(const t of db.tables||[])if(!Array.isArray(t.columns))throw Error('Некорректные поля таблицы.');}
 }
 if(d.catalog){
  if(!Array.isArray(d.catalog.projects)||d.catalog.projects.length>3000)throw Error('Некорректный каталог проектов.');
  const ids=new Set();
  for(const p of d.catalog.projects){
   if(!p||typeof p.id!=='string'||!/^[-\w.]+$/.test(p.id)||ids.has(p.id)||typeof p.name!=='string'||typeof p.category!=='string'||typeof p.status!=='string')throw Error('Некорректный проект каталога.');
   ids.add(p.id);
   if(!numeric(p.size_total,true))bad();
   for(const k of ['repos','folders','services','docker','domains','databases','problems'])if(!Array.isArray(p[k]))throw Error('В каталоге отсутствует '+k);
   for(const f of p.folders)if(typeof f.path!=='string'||!/^[-\w]+$/.test(f.server)||!numeric(f.size,true))bad();
   for(const db of p.databases)if(typeof db.name!=='string'||!numeric(db.tables,true)||!numeric(db.rows,true))bad();
   for(const r of p.repos)if(typeof r.name!=='string'||!numeric(r.size,true))bad();
  }
 }
 const ids=new Set();for(const n of d.graph.nodes){if(typeof n.id!=='string'||typeof n.type!=='string'||typeof n.label!=='string'||ids.has(n.id))throw Error('Некорректные узлы графа.');ids.add(n.id)}
 for(const e of d.graph.edges)if(!ids.has(e.from)||!ids.has(e.to))throw Error('Связь ссылается на отсутствующий узел.');
 return d;
}
export function model(d,custom=[]){
 const services=Object.entries(d.servers).flatMap(([server,s])=>s.services.map(v=>({...v,server,collected:s.collected_at})));
 const containers=Object.entries(d.servers).flatMap(([server,s])=>s.docker.map(v=>({...v,server})));
 const repoMap=new Map(d.repos.map(r=>[r.name,r]));
 let projects=Object.entries(d.links.groups).map(([id,g])=>({id,...g,repoInfo:repoMap.get(g.repo)}));
 const mapped=new Set(projects.map(p=>p.repo));
 for(const r of d.repos)if(!mapped.has(r.name))projects.push({id:'repo-'+r.name,name:r.name,repo:r.name,kind:/assistant|orion/.test(r.name)?'agents':/twitch/.test(r.name)?'bot':/airrock/.test(r.name)?'site':r.size_kib===0?'idea':'archive',confidence:'unknown',note:d.links.repos_without_runtime?.[r.name]||r.description,repoInfo:r});
 if(d.catalog){
  projects=d.catalog.projects.map(c=>({id:c.id,name:c.name,kind:c.category,note:c.note,repo:c.repos[0]?.name,repoInfo:repoMap.get(c.repos[0]?.name),server:[...new Set([...c.folders,...c.services,...c.docker].map(f=>f.server).filter(Boolean))].join('+'),services:c.services.map(s=>s.name),docker:c.docker.map(s=>s.name),domains:c.domains.map(s=>s.name),databases:c.databases.map(db=>db.engine==='sqlite'?db.name:db.engine+':'+db.name),paths:c.folders.map(f=>f.path),confidence:'catalog',catalog:c}));
 }
 for(const p of custom)projects.push({...p,local:true});
 for(const p of projects){
  p.matchedServices=services.filter(s=>(p.services||[]).includes(s.name)&&String(p.server||'').split('+').includes(s.server));
  p.matchedContainers=containers.filter(c=>(p.docker||[]).includes(c.name)&&String(p.server||'').split('+').includes(c.server));
  const states=[...p.matchedServices.map(s=>s.state==='active'),...p.matchedContainers.map(c=>/^Up\b/i.test(c.status))];
  const expected=(p.services||[]).length+(p.docker||[]).length;
  p.status=states.length?states.every(Boolean)&&states.length>=expected?'active':states.some(Boolean)?'partial':'inactive':'unknown';
  if(p.catalog)p.status=({running:'active',live:'live',stopped:'stopped','repo-only':'repo-only',lost:'lost',idea:'idea',empty:'empty'})[p.catalog.status]||'unknown';
 }
 const databases=Object.entries(d.servers).flatMap(([server,s])=>s.databases.map((db,i)=>({...db,server,id:server+'-'+i,name:db.database||db.path?.split('/').pop()||db.container,system:db.database==='postgres',tables:db.tables||[]})));
 const timers=Object.entries(d.servers).flatMap(([server,s])=>(s.timers||[]).map(t=>({...t,server})));
 let apps=Object.entries(d.servers).flatMap(([server,s])=>(s.apps||[]).map(t=>({...t,server})));
 if(d.catalog)apps=[...new Map(d.catalog.projects.flatMap(p=>p.folders.map(f=>({...f,name:f.package||f.path?.split('/').pop()||p.name,projectId:p.id,stack:f.stack||[]}))).map(f=>[f.server+':'+f.path,f])).values()];
 const graph=buildGraph(d);
 return {projects,services,containers,databases,timers,apps,graph,activeServices:services.filter(s=>s.state==='active').length};
}

// Keep infrastructure evidence intact; project links come from the newer canonical catalogue.
export function buildGraph(d){
 if(!d.catalog)return d.graph;
 const nodes=d.graph.nodes.filter(n=>n.type!=='project').map(n=>({...n}));
 const edges=d.graph.edges.filter(e=>!e.from.startsWith('project:')&&!e.to.startsWith('project:')).map(e=>({...e}));
 for(const p of d.catalog.projects)nodes.push({id:'project:'+p.id,type:'project',label:p.name,kind:p.category,status:p.status,note:p.note});
 const ids=new Set(nodes.map(n=>n.id));const seen=new Set(edges.map(e=>[e.from,e.to,e.kind].join('|')));
 const add=(from,to,kind)=>{const key=[from,to,kind].join('|');if(ids.has(from)&&ids.has(to)&&!seen.has(key)){seen.add(key);edges.push({from,to,kind})}};
 for(const p of d.catalog.projects){
  const from='project:'+p.id;
  for(const s of p.services)add(from,`service:${s.server}:${s.name}`,'has');
  for(const c of p.docker)add(from,`docker:${c.server}:${c.name}`,'has');
  for(const domain of p.domains)add(from,'domain:'+domain.name,'uses');
  for(const db of p.databases)if(db.doc)add(from,'db:'+db.doc.split('/').pop().replace(/\.md$/,''),'uses');
  if(p.parent)add('project:'+p.parent,from,'contains');
 }
 return {...d.graph,nodes,edges};
}
