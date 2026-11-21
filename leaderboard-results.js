(() => {
  'use strict';
  const body = document.querySelector('[data-board-body]');
  const state = document.querySelector('[data-board-status]');
  const table = document.querySelector('[data-board-table]');
  const search = document.querySelector('[data-board-search]');
  const download = document.querySelector('[data-board-download]');
  const empty = document.querySelector('[data-board-empty]');
  const count = document.querySelector('[data-board-count]');
  const t = text => window.BuildBenchI18n?.t(text) || text;
  let data;
  let failed = false;
  const number = n => Number(n).toFixed(2);
  const hours = seconds => (Math.round(seconds / 36) / 100).toFixed(2);
  function cell(tag, value, className, label) {
    const el = document.createElement(tag);
    el.className = className;
    if (tag === 'th') el.scope = 'row';
    if (label) el.dataset.label = t(label);
    if (value !== null) el.textContent = value;
    return el;
  }
  function render() {
    if (failed) {
      state.hidden = false;
      state.textContent = t('Results could not be loaded. Please refresh the page.');
      return;
    }
    if (!data) return;
    const term = search.value.trim().toLocaleLowerCase();
    const visible = data.entries.filter(row => [row.team,...row.institutions].join(' ').toLocaleLowerCase().includes(term));
    body.replaceChildren();
    for (const entry of visible) {
      const row = document.createElement('tr');
      row.append(cell('td', String(entry.rank).padStart(2,'0'), 'formal-rank'));
      row.append(cell('th', entry.team, 'formal-team'));
      const institution = cell('td',null,'formal-institution');
      entry.institutions.forEach(name => institution.append(cell('span',name,'')));
      row.append(institution);
      row.append(cell('td',entry.score,'formal-numeric formal-score','Weighted score'));
      row.append(cell('td',(entry.pass_rate*100).toFixed(1)+'%','formal-numeric formal-rate','Pass rate'));
      const passed = cell('td',null,'formal-numeric formal-cases','Cases passed');
      const detail = document.createElement('div');
      detail.append(cell('span',entry.passed+' / '+entry.total,'formal-passed'));
      detail.append(cell('span',t('E')+' '+entry.easy+' · '+t('M')+' '+entry.medium+' · '+t('H')+' '+entry.hard,'formal-breakdown'));
      passed.append(detail);
      row.append(passed);
      row.append(cell('td',hours(entry.agent_seconds),'formal-numeric','Agent (h)'));
      row.append(cell('td',hours(entry.build_seconds),'formal-numeric','Build (h)'));
      row.append(cell('td',number(entry.input_tokens/1e6),'formal-numeric','Input (M)'));
      row.append(cell('td',number(entry.output_tokens/1e6),'formal-numeric','Output (M)'));
      row.append(cell('td',number(entry.cached_tokens/1e6),'formal-numeric formal-cached','Cached input (M)'));
      body.append(row);
    }
    table.hidden = false;
    state.hidden = true;
    empty.hidden = visible.length !== 0;
    count.textContent = window.BuildBenchI18n?.getLanguage() === 'zh' ? '显示 '+visible.length+' / '+data.total_teams+' 支队伍' : 'Showing '+visible.length+' of '+data.total_teams+' teams';
  }
  search.addEventListener('input',render);
  window.addEventListener('buildbench:languagechange',render);
  download.addEventListener('click',() => {
    if (!data) return;
    const headers = ['Rank','Team','Institution','Weighted score','Pass rate','Cases passed','Easy passes','Medium passes','Hard passes','Agent (h)','Build (h)','Input tokens','Output tokens','Cached input tokens'];
    const rows = data.entries.map(row => [row.rank,row.team,row.institutions.join('; '),row.score,(row.pass_rate*100).toFixed(1)+'%',row.passed,row.easy,row.medium,row.hard,hours(row.agent_seconds),hours(row.build_seconds),row.input_tokens,row.output_tokens,row.cached_tokens]);
    const quote = value => '"'+String(value).replaceAll('"','""')+'"';
    const csv = '\ufeff'+[headers.map(t),...rows].map(row=>row.map(quote).join(',')).join('\r\n')+'\r\n';
    const url = URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));
    const link = document.createElement('a');
    link.href=url;
    link.download='buildbench-final-results.csv';
    document.body.append(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  });
  fetch('leaderboard-results.json?v=20261121-2')
    .then(response => {if(!response.ok) throw new Error('Results unavailable'); return response.json();})
    .then(value => {data=value;download.disabled=false;render();})
    .catch(() => {failed=true;render();});
})();
