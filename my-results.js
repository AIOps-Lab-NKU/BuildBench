(() => {
  'use strict';
  if (location.hostname.endsWith('.github.io')) {
    location.replace('https://matrix.cstcloud.cn/build-bench/my-results.html'+location.search);
    return;
  }
  const find = key => document.querySelector('[data-own-'+key+']');
  const t = text => window.BuildBenchI18n?.t(text) || text;
  const hours = seconds => (Math.round(seconds/36)/100).toFixed(2);
  const million = n => (Math.round(n/10000)/100).toFixed(2);
  const tokens = n => Number(n).toLocaleString(window.BuildBenchI18n?.getLanguage()==='zh'?'zh-CN':'en');
  const arch = value => ({x86_64:'AMD64',amd64:'AMD64',aarch64:'ARM64',arm64:'ARM64',riscv64:'RISC-V'}[value] || value);
  const migration = item => arch(item.source_arch)+' → '+arch(item.target_arch);
  const difficulty = value => t({easy:'Easy',medium:'Medium',hard:'Hard'}[value] || value);
  const status = value => t({succeeded:'Passed',failed:'Build failed',timeout:'Timed out',agent_error:'Agent error',invalid_patch:'Invalid patch',no_fix:'No fix',unresolvable:'Unresolvable',completed:'Completed',not_run:'Not run',not_started:'Not run',skipped:'Not run'}[value] || value || '—');
  const date = value => value ? new Intl.DateTimeFormat(window.BuildBenchI18n?.getLanguage()==='zh'?'zh-CN':'en',{dateStyle:'medium',timeStyle:'short',timeZone:'Asia/Shanghai'}).format(new Date(value)) : '—';
  let report;
  const node = (tag,text,className='') => {const element=document.createElement(tag);element.textContent=text;element.className=className;return element;};
  async function request(path) {
    const response=await fetch(window.BuildBenchAuth?.apiUrl(path) || path,{credentials:'same-origin',cache:'no-store',headers:{Accept:'application/json'}});
    if(!response.ok){const error=new Error(String(response.status));error.status=response.status;throw error;}
    return response.json();
  }
  function save(name,content,type) {
    const url=URL.createObjectURL(new Blob([content],{type}));
    const link=node('a','');link.href=url;link.download=name;document.body.append(link);link.click();link.remove();URL.revokeObjectURL(url);
  }
  function metric(label,value,suffix='') {
    const container=document.createElement('div');container.append(node('dt',t(label)));
    const dd=node('dd',value);if(suffix)dd.append(node('small',suffix));container.append(dd);return container;
  }
  function breakdownTable(target,groups,heading) {
    target.replaceChildren();
    const head=document.createElement('tr');
    [heading,'Cases','Cases passed','Pass rate','Weighted score'].forEach(label=>head.append(node('th',t(label))));target.append(head);
    for(const [key,items] of groups){const passed=items.filter(item=>item.status==='succeeded').length;const row=document.createElement('tr');
      [key,items.length,passed,(passed/items.length*100).toFixed(1)+'%',items.reduce((sum,item)=>sum+item.points,0)].forEach(value=>row.append(node('td',value)));target.append(row);}
  }
  function optionList(select,options) {
    const selected=select.value;select.replaceChildren();
    for(const [value,label] of options){const option=node('option',label);option.value=value;select.append(option);}
    if(options.some(([value])=>value===selected))select.value=selected;
  }
  function render() {
    if(!report)return;
    const summary=report.summary;
    find('loading').hidden=true;find('report').hidden=false;find('login').hidden=true;
    find('team').textContent=summary.team;
    find('agent').textContent=report.agent.name+' · v'+report.agent.version+' · '+report.agent.model+' · '+summary.institutions.join('；');
    find('identity').textContent=t('Final submission')+': '+report.submission_id+'  |  '+t('Evaluation')+': '+report.evaluation_id;
    find('download').textContent=t('Download full report (JSON)');
    find('summary').replaceChildren(metric('Weighted score',summary.weighted_score,'/ '+summary.max_points),metric('Pass rate',(summary.pass_rate*100).toFixed(1)+'%'),metric('Cases passed',summary.passed,'/ '+summary.total),metric('Rank',summary.rank));
    find('usage').replaceChildren(metric('Agent (h)',hours(summary.agent_seconds)),metric('Build (h)',hours(summary.build_seconds)),metric('Input (M)',million(summary.input_tokens)),metric('Output (M)',million(summary.output_tokens)),metric('Cached input (M)',million(summary.cached_tokens)),metric('Easy / Medium / Hard passes',summary.easy+' / '+summary.medium+' / '+summary.hard));
    find('times').textContent=t('Started')+': '+date(report.started_at)+'  |  '+t('Finished')+': '+date(report.finished_at)+'  '+t('(Beijing time)');
    find('breakdown-heading').textContent=t('Summaries by architecture and difficulty');
    find('arch-title').textContent=t('Architecture directions');find('difficulty-title').textContent=t('Difficulty levels');
    const migrations=[...new Set(report.cases.map(migration))];
    breakdownTable(find('arch'),migrations.map(key=>[key,report.cases.filter(item=>migration(item)===key)]),'Architecture');
    breakdownTable(find('difficulty'),['easy','medium','hard'].map(key=>[difficulty(key),report.cases.filter(item=>item.difficulty===key)]),'Difficulty');
    find('cases-heading').textContent=t('Per-case results');
    find('search').placeholder=t('Search package or case ID');
    find('search').setAttribute('aria-label',t('Search package or case ID'));
    find('status').setAttribute('aria-label',t('Result filter'));
    find('migration').setAttribute('aria-label',t('Architecture filter'));
    find('level').setAttribute('aria-label',t('Difficulty filter'));
    optionList(find('status'),[['all',t('All results')],['passed',t('Passed')],['failed',t('Not passed')]]);
    optionList(find('migration'),[['all',t('All architectures')],...migrations.map(value=>[value,value])]);
    optionList(find('level'),[['all',t('All difficulties')],...['easy','medium','hard'].map(value=>[value,difficulty(value)])]);
    const tableHead=document.createElement('tr');
    ['Case','Package','Architecture','Difficulty','Result','Points','Agent (s)','Build (s)','Input tokens','Output tokens','Details'].forEach(label=>tableHead.append(node('th',t(label))));
    find('cases-head').replaceChildren(tableHead);
    find('note').textContent=t('All values use the final effective attempt for each case. Cached tokens are included in input. Log downloads contain the complete original file.');
    find('empty').textContent=t('No matching cases.');
    renderCases();
  }
  function renderCases() {
    if(!report)return;
    const term=find('search').value.trim().toLocaleLowerCase(), filter=find('status').value, direction=find('migration').value, level=find('level').value;
    const cases=report.cases.filter(item=>[item.package,item.case_id].join(' ').toLocaleLowerCase().includes(term)
      &&(filter==='all'||(filter==='passed')===(item.status==='succeeded'))&&(direction==='all'||migration(item)===direction)&&(level==='all'||item.difficulty===level));
    find('cases').replaceChildren();
    for(const item of cases){const row=document.createElement('tr');row.append(node('td',String(item.ordinal).padStart(3,'0')));
      const name=node('td','');name.append(node('strong',item.package),node('small',item.source_version));row.append(name);
      row.append(node('td',migration(item)),node('td',difficulty(item.difficulty)));
      const result=node('td','');result.append(node('span',status(item.status),'own-status'+(item.status==='succeeded'?' success':'')));row.append(result);
      [item.points+' / '+item.max_points,item.agent_seconds,item.build_seconds,tokens(item.input_tokens),tokens(item.output_tokens)].forEach(value=>row.append(node('td',value)));
      const action=node('td','');const button=node('button',t('View'),'own-case-button');button.type='button';button.addEventListener('click',()=>showCase(item));action.append(button);row.append(action);find('cases').append(row);}
    find('empty').hidden=cases.length>0;
    find('count').textContent=t('Showing cases')+' '+cases.length+' / '+report.cases.length;
  }
  async function log(item,kind) {
    const pre=find('log');pre.hidden=false;pre.textContent=t('Loading log…');find('log-note').textContent='';
    const path='/api/formal-results/'+encodeURIComponent(report.evaluation_id)+'/cases/'+item.ordinal+'/logs/'+kind;
    try{const result=await request(path);pre.textContent=result.content;find('log-note').textContent=result.truncated?t('Showing the end of the log. Download the complete file for all output.'):t('Complete log shown.');}
    catch(error){pre.textContent=t('The log is not available.');}
  }
  function showCase(item) {
    find('dialog-title').textContent=String(item.ordinal).padStart(3,'0')+' · '+item.package;
    find('detail').replaceChildren(node('p',item.case_id,'own-detail-id'));
    const grid=node('dl','','own-detail-grid');
    const fields=[['Result',status(item.status)],['Difficulty',difficulty(item.difficulty)],['Points',item.points+' / '+item.max_points],['Architecture',migration(item)],['Source version',item.source_version],['Build exit code',item.build_exit_code??'—'],['Agent status',status(item.agent_status)],['Validator status',status(item.validator_status)],['Total time (s)',item.duration_seconds],['Agent (s)',item.agent_seconds],['Build (s)',item.build_seconds],['Input tokens',tokens(item.input_tokens)],['Output tokens',tokens(item.output_tokens)],['Cached input tokens',tokens(item.cached_tokens)],['Started',date(item.started_at)],['Finished',date(item.finished_at)]];
    for(const [label,value]of fields){const field=node('div','');field.append(node('dt',t(label)),node('dd',value));grid.append(field);}
    find('detail').append(grid);
    if(item.message)find('detail').append(node('p',item.message,'own-message'));
    find('log-actions').replaceChildren();find('log').hidden=true;find('log').textContent='';find('log-note').textContent='';
    for(const kind of item.available_logs){const view=node('button',t(kind==='build'?'View build log':'View validator log'),'own-case-button');view.type='button';view.addEventListener('click',()=>log(item,kind));
      const download=node('a',t(kind==='build'?'Download build log':'Download validator log'),'formal-download');download.href=window.BuildBenchAuth.apiUrl('/api/formal-results/'+encodeURIComponent(report.evaluation_id)+'/cases/'+item.ordinal+'/logs/'+kind+'?download=1');find('log-actions').append(view,download);}
    if(!item.available_logs.length)find('log-note').textContent=t('No build log was produced for this case.');
    find('dialog').showModal();
  }
  find('download').addEventListener('click',()=>save('buildbench-my-final-report.json',JSON.stringify(report,null,2),'application/json;charset=utf-8'));
  for(const key of ['search','status','migration','level'])find(key).addEventListener(key==='search'?'input':'change',renderCases);
  find('close').addEventListener('click',()=>find('dialog').close());
  window.addEventListener('buildbench:languagechange',()=>{find('dialog').close();render();});
  request('/api/formal-results').then(value=>{report=value;render();}).catch(error=>{
    find('loading').hidden=true;
    if(error.status===401||error.status===403)find('login').hidden=false;
    else{find('error').hidden=false;find('error').textContent=t(error.status===404?'Your team does not have a released formal report yet.':'The report could not be loaded. Please try again later.');}
  });
})();
