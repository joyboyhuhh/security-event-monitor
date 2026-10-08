const byId = id => document.getElementById(id);
const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function getJson(path){const response=await fetch(path);if(!response.ok)throw new Error(`Request failed: ${path}`);return response.json()}
function shortDate(value){return new Date(value).toLocaleDateString(undefined,{month:'short',day:'numeric',timeZone:'UTC'})}
async function loadDashboard(){
  try{
    const [stats,alerts,events,ips,timeline]=await Promise.all([getJson('/api/stats'),getJson('/api/alerts?limit=8'),getJson('/api/events?limit=12'),getJson('/api/top-ips'),getJson('/api/timeline')]);
    byId('total-events').textContent=stats.total_events;byId('total-alerts').textContent=stats.total_alerts;byId('high-severity').textContent=stats.high_severity;byId('unique-ips').textContent=stats.unique_ips;byId('alert-count').textContent=`${stats.medium_severity} medium · ${stats.high_severity} high`;
    byId('alerts').innerHTML=alerts.length?alerts.map(a=>`<article class="alert-item ${escapeHtml(a.severity)}"><h3>${escapeHtml(a.alert_type)} <span class="meta">${escapeHtml(a.severity)}</span></h3><p>${escapeHtml(a.description)}</p><div class="meta"><span>${escapeHtml(a.source_ip)}</span><span>${shortDate(a.timestamp)}</span></div></article>`).join(''):'<div class="empty">No alerts yet. Run the detector to analyze imported logs.</div>';
    byId('events').innerHTML=events.map(e=>`<tr><td>${escapeHtml(new Date(e.timestamp).toLocaleString(undefined,{timeZone:'UTC'}))}</td><td>${escapeHtml(e.source_ip)}</td><td>${escapeHtml(e.username)}</td><td>${escapeHtml(e.event_type)}</td><td class="status">${escapeHtml(e.status)}</td><td>${escapeHtml(e.resource||'—')}</td></tr>`).join('')||'<tr><td colspan="6" class="empty">No events loaded.</td></tr>';
    const max=Math.max(1,...ips.map(x=>x.event_count));byId('top-ips').innerHTML=ips.map(x=>`<div class="ip-row"><div>${escapeHtml(x.source_ip)}<div class="ip-track"><div class="ip-fill" style="width:${x.event_count/max*100}%"></div></div></div><span class="ip-n">${x.event_count}</span></div>`).join('')||'<div class="empty">No source IPs.</div>';
    const shown=timeline.slice(-10), peak=Math.max(1,...shown.map(x=>x.event_count));byId('timeline').innerHTML=shown.map(x=>`<div class="day"><div class="bar-pair"><div class="bar" title="${x.event_count} events" style="height:${Math.max(3,x.event_count/peak*100)}%"></div><div class="bar alert" title="${x.alert_count} alerts" style="height:${Math.max(3,x.alert_count/peak*100)}%"></div></div><label>${shortDate(x.date)}</label></div>`).join('')||'<div class="empty">No timeline data.</div>';
  }catch(error){byId('alerts').innerHTML=`<div class="empty">Could not load dashboard data. ${escapeHtml(error.message)}</div>`}
}
loadDashboard();
