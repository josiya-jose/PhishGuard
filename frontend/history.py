import streamlit as st
import streamlit.components.v1 as components
import requests
import json
from datetime import datetime

BACKEND_URL = "http://127.0.0.1:8000"


def build_history_html(records):
    rows_json = json.dumps(records)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
    font-family: 'DM Sans', sans-serif;
    background: transparent;
    color: #e2d9f3;
    padding: 0 0 30px;
}}

/* ── PAGE TITLE ── */
.page-title {{
    font-family: 'Syne', sans-serif;
    font-size: 26px;
    font-weight: 800;
    color: #fff;
    margin-bottom: 22px;
    letter-spacing: -0.02em;
    text-shadow: 0 2px 20px rgba(167,139,250,0.3);
}}

/* ── FILTER BAR ── */
.filter-bar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
    flex-wrap: wrap;
    gap: 12px;
}}
.tabs {{
    display: flex;
    align-items: center;
    gap: 0;
}}
.tab {{
    font-size: 13px;
    font-weight: 500;
    color: rgba(255,255,255,0.38);
    padding: 6px 18px;
    cursor: pointer;
    border-bottom: 2px solid transparent;
    transition: color 0.2s, border-color 0.2s;
    white-space: nowrap;
    user-select: none;
}}
.tab:hover {{ color: rgba(255,255,255,0.70); }}
.tab.active {{
    color: #a78bfa;
    border-bottom: 2.5px solid #a78bfa;
    font-weight: 600;
}}
.date-range {{
    display: flex;
    align-items: center;
    gap: 8px;
}}
.date-chip {{
    display: flex;
    align-items: center;
    gap: 7px;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 10px;
    padding: 7px 14px;
    font-size: 12px;
    font-weight: 500;
    color: rgba(255,255,255,0.70);
    cursor: pointer;
    backdrop-filter: blur(10px);
    transition: background 0.2s, border-color 0.2s;
}}
.date-chip:hover {{ background: rgba(255,255,255,0.12); border-color: rgba(167,139,250,0.45); }}
.date-chip svg {{ flex-shrink: 0; }}
.date-to {{
    font-size: 12px;
    font-weight: 500;
    color: rgba(255,255,255,0.35);
}}

/* ── TABLE CARD ── */
.table-card {{
    background: rgba(255,255,255,0.055);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.10);
    box-shadow: 0 8px 40px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.10);
    overflow: hidden;
    position: relative;
}}
.table-card::before {{
    content: "";
    position: absolute; top: 0; left: 10%; right: 10%; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(167,139,250,0.5) 50%, transparent);
    pointer-events: none;
}}

/* ── TABLE ── */
table {{
    width: 100%;
    border-collapse: collapse;
}}
thead tr {{
    background: rgba(255,255,255,0.04);
    border-bottom: 1px solid rgba(255,255,255,0.07);
}}
thead th {{
    text-align: left;
    font-size: 11px;
    font-weight: 700;
    color: rgba(255,255,255,0.45);
    letter-spacing: 0.10em;
    text-transform: uppercase;
    padding: 14px 18px;
    white-space: nowrap;
    user-select: none;
}}
thead th.sortable {{ cursor: pointer; }}
thead th.sortable:hover {{ color: rgba(255,255,255,0.80); }}
thead th .sort-icon {{
    display: inline-block;
    margin-left: 4px;
    opacity: 0.40;
    font-size: 10px;
}}
tbody tr {{
    border-bottom: 1px solid rgba(255,255,255,0.055);
    transition: background 0.15s;
    position: relative;
}}
tbody tr:last-child {{ border-bottom: none; }}
tbody tr:hover {{ background: rgba(167,139,250,0.07); }}
tbody tr.selected {{ background: rgba(167,139,250,0.10); }}
tbody td {{
    padding: 13px 18px;
    font-size: 13px;
    color: rgba(255,255,255,0.75);
    vertical-align: middle;
}}

/* ── ID cell ── */
.id-cell {{ font-weight: 700; color: rgba(255,255,255,0.90); font-size: 13px; }}

/* ── Name cell ── */
.name-cell {{
    display: flex;
    align-items: center;
    gap: 9px;
}}
.avatar {{
    width: 32px; height: 32px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea, #764ba2);
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 700; color: #fff;
    flex-shrink: 0;
    overflow: hidden;
    box-shadow: 0 0 8px rgba(124,58,237,0.4);
}}
.avatar img {{ width: 100%; height: 100%; object-fit: cover; }}
.name-text {{ font-weight: 500; color: rgba(255,255,255,0.88); font-size: 13px; }}

/* ── Payment ── */
.payment-cell {{ color: rgba(255,255,255,0.50); font-size: 13px; }}

/* ── Time ── */
.time-cell {{
    display: flex;
    align-items: center;
    gap: 5px;
    color: rgba(255,255,255,0.50);
    font-size: 13px;
}}
.time-icon {{ opacity: 0.45; }}

/* ── Type ── */
.type-delivery {{ color: #f87171; font-weight: 600; font-size: 13px; }}
.type-collection {{ color: rgba(255,255,255,0.65); font-size: 13px; }}

/* ── Status badges ── */
.badge {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 12px;
    font-weight: 600;
    white-space: nowrap;
}}
.badge-dot {{ width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }}
.badge-delivered {{ color: #fbbf24; }}
.badge-delivered .badge-dot {{ background: #fbbf24; box-shadow: 0 0 6px #fbbf24; }}
.badge-collected {{ color: #34d399; }}
.badge-collected .badge-dot {{ background: #34d399; box-shadow: 0 0 6px #34d399; }}
.badge-cancelled {{ color: #f87171; }}
.badge-cancelled .badge-dot {{ background: #f87171; box-shadow: 0 0 6px #f87171; }}

/* ── Total ── */
.total-cell {{ font-weight: 700; color: rgba(255,255,255,0.90); font-size: 13px; }}

/* ── Action menu ── */
.action-wrap {{ position: relative; }}
.action-btn {{
    width: 28px; height: 28px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer;
    color: rgba(255,255,255,0.35);
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 1px;
    transition: background 0.18s, color 0.18s;
    user-select: none;
    line-height: 1;
}}
.action-btn:hover {{ background: rgba(255,255,255,0.10); color: rgba(255,255,255,0.85); }}
.dropdown {{
    display: none;
    position: absolute;
    right: 0; top: 34px;
    background: rgba(30,15,60,0.95);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 12px;
    box-shadow: 0 12px 40px rgba(0,0,0,0.45);
    min-width: 140px;
    z-index: 999;
    overflow: hidden;
    animation: popIn 0.15s ease;
}}
@keyframes popIn {{
    from {{ opacity:0; transform: scale(0.92) translateY(-4px); }}
    to   {{ opacity:1; transform: scale(1) translateY(0); }}
}}
.dropdown.open {{ display: block; }}
.drop-item {{
    padding: 11px 16px;
    font-size: 13px;
    font-weight: 500;
    color: rgba(255,255,255,0.75);
    cursor: pointer;
    transition: background 0.15s;
    display: flex; align-items: center; gap: 8px;
}}
.drop-item:hover {{ background: rgba(255,255,255,0.08); color: #fff; }}
.drop-item.danger {{ color: #f87171; }}
.drop-item.danger:hover {{ background: rgba(248,113,113,0.12); }}

/* ── Empty state ── */
.empty-state {{
    text-align: center;
    padding: 60px 20px;
    color: rgba(255,255,255,0.30);
}}
.empty-icon {{ font-size: 48px; margin-bottom: 12px; opacity: 0.4; }}
.empty-text {{ font-size: 15px; font-weight: 500; }}

/* ── Pagination ── */
.pagination {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 18px;
    border-top: 1px solid rgba(255,255,255,0.06);
    background: rgba(255,255,255,0.025);
}}
.page-info {{ font-size: 12px; color: rgba(255,255,255,0.32); }}
.page-btns {{ display: flex; gap: 6px; }}
.page-btn {{
    width: 28px; height: 28px;
    border-radius: 7px;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 600;
    cursor: pointer;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.10);
    color: rgba(255,255,255,0.45);
    transition: all 0.18s;
}}
.page-btn:hover {{ background: rgba(167,139,250,0.18); color: #fff; border-color: rgba(167,139,250,0.4); }}
.page-btn.active {{ background: linear-gradient(135deg,#7c3aed,#a78bfa); color: #fff; border-color: transparent; box-shadow: 0 0 12px rgba(124,58,237,0.5); }}
</style>
</head>
<body>

<div class="page-title">Scan History</div>

<!-- FILTER BAR -->
<div class="filter-bar">
    <div class="tabs">
        <div class="tab active" onclick="filterTab(this,'all')">All Scans</div>
        <div class="tab" onclick="filterTab(this,'legitimate')">Legitimate</div>
        <div class="tab" onclick="filterTab(this,'phishing')">Phishing</div>
        <div class="tab" onclick="filterTab(this,'suspicious')">Suspicious</div>
    </div>
    <div class="date-range">
        <div class="date-chip">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            <span id="date-from">—</span>
        </div>
        <span class="date-to">To</span>
        <div class="date-chip">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            <span id="date-to">—</span>
        </div>
    </div>
</div>

<!-- TABLE -->
<div class="table-card">
    <table>
        <thead>
            <tr>
                <th class="sortable" onclick="sortTable('id')">ID <span class="sort-icon">↕</span></th>
                <th>URL</th>
                <th>Confidence</th>
                <th class="sortable" onclick="sortTable('time')">Scanned At <span class="sort-icon">↕</span></th>
                <th>Type</th>
                <th>Status</th>
                <th>Risk Score</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody id="tbody">
        </tbody>
    </table>
    <div class="pagination">
        <div class="page-info" id="page-info">Showing 0 of 0</div>
        <div class="page-btns" id="page-btns"></div>
    </div>
</div>

<script>
const allRecords = {rows_json};
let filtered = [...allRecords];
let currentPage = 1;
const perPage = 8;
let activeTab = 'all';
let sortKey = null;
let sortAsc = true;

// Set date range from data
function initDates() {{
    if (!allRecords.length) return;
    const dates = allRecords.map(r => r.scanned_at).filter(Boolean).sort();
    if (dates.length) {{
        document.getElementById('date-from').textContent = formatDate(dates[0]);
        document.getElementById('date-to').textContent   = formatDate(dates[dates.length-1]);
    }}
}}

function formatDate(d) {{
    if (!d) return '—';
    const dt = new Date(d);
    if (isNaN(dt)) return d;
    return dt.toLocaleDateString('en-GB', {{day:'2-digit',month:'short',year:'numeric'}});
}}

function formatTime(d) {{
    if (!d) return '—';
    const dt = new Date(d);
    if (isNaN(dt)) return d;
    return dt.toLocaleDateString('en-GB', {{day:'2-digit',month:'short',year:'numeric'}}) + ' ' +
           dt.toLocaleTimeString('en-GB', {{hour:'2-digit',minute:'2-digit'}});
}}

function minutesSince(d) {{
    if (!d) return '—';
    const dt = new Date(d);
    if (isNaN(dt)) return '—';
    const diff = Math.floor((Date.now() - dt) / 60000);
    if (diff < 60)  return diff + ' min ago';
    if (diff < 1440) return Math.floor(diff/60) + ' hr ago';
    return Math.floor(diff/1440) + ' days ago';
}}

function getInitials(url) {{
    try {{
        const h = new URL(url.startsWith('http') ? url : 'https://' + url).hostname;
        return h.replace('www.','').substring(0,2).toUpperCase();
    }} catch {{ return 'SC'; }}
}}

function getAvatarColor(url) {{
    const colors = [
        'linear-gradient(135deg,#667eea,#764ba2)',
        'linear-gradient(135deg,#f093fb,#f5576c)',
        'linear-gradient(135deg,#4facfe,#00f2fe)',
        'linear-gradient(135deg,#43e97b,#38f9d7)',
        'linear-gradient(135deg,#fa709a,#fee140)',
        'linear-gradient(135deg,#a18cd1,#fbc2eb)',
        'linear-gradient(135deg,#ffecd2,#fcb69f)',
        'linear-gradient(135deg,#84fab0,#8fd3f4)',
    ];
    let hash = 0;
    for (let i = 0; i < url.length; i++) hash = url.charCodeAt(i) + ((hash << 5) - hash);
    return colors[Math.abs(hash) % colors.length];
}}

function statusBadge(prediction, riskLevel) {{
    const p = (prediction||'').toLowerCase();
    const r = (riskLevel||'').toLowerCase();
    if (p === 'phishing' || r.includes('high'))
        return `<span class="badge badge-cancelled"><span class="badge-dot"></span>Phishing</span>`;
    if (p === 'suspicious' || r.includes('medium'))
        return `<span class="badge badge-delivered"><span class="badge-dot"></span>Suspicious</span>`;
    return `<span class="badge badge-collected"><span class="badge-dot"></span>Legitimate</span>`;
}}

function typeCell(prediction) {{
    const p = (prediction||'').toLowerCase();
    if (p === 'phishing') return '<span class="type-delivery">Phishing</span>';
    if (p === 'suspicious') return '<span class="type-delivery">Suspicious</span>';
    return '<span class="type-collection">Legitimate</span>';
}}

function renderTable() {{
    const tbody = document.getElementById('tbody');
    const start = (currentPage - 1) * perPage;
    const page  = filtered.slice(start, start + perPage);

    if (!filtered.length) {{
        tbody.innerHTML = `<tr><td colspan="8">
            <div class="empty-state">
                <div class="empty-icon">🔍</div>
                <div class="empty-text">No scan history found</div>
            </div>
        </td></tr>`;
        document.getElementById('page-info').textContent = 'No results';
        document.getElementById('page-btns').innerHTML = '';
        return;
    }}

    tbody.innerHTML = page.map((r, i) => {{
        const globalIdx = start + i;
        const initials  = getInitials(r.url || '');
        const avatarBg  = getAvatarColor(r.url || '');
        const shortUrl  = (r.url || '').replace(/^https?:\/\/(www\.)?/,'').substring(0,35) + ((r.url||'').length > 40 ? '…' : '');
        const conf      = r.confidence != null ? (parseFloat(r.confidence)*100).toFixed(1)+'%' : '—';
        const rscore    = r.risk_score  != null ? parseFloat(r.risk_score).toFixed(2) : '—';

        return `<tr id="row-${{globalIdx}}">
            <td><span class="id-cell">#${{r.id || (globalIdx+1)}}</span></td>
            <td>
                <div class="name-cell">
                    <div class="avatar" style="background:${{avatarBg}};">${{initials}}</div>
                    <span class="name-text" title="${{r.url || ''}}">${{shortUrl}}</span>
                </div>
            </td>
            <td class="payment-cell">${{conf}}</td>
            <td>
                <div class="time-cell">
                    <svg class="time-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                    ${{minutesSince(r.scanned_at)}}
                </div>
            </td>
            <td>${{typeCell(r.prediction)}}</td>
            <td>${{statusBadge(r.prediction, r.risk_level)}}</td>
            <td class="total-cell">${{rscore}}</td>
            <td>
                <div class="action-wrap">
                    <div class="action-btn" onclick="toggleMenu(${{globalIdx}}, event)">⋮</div>
                    <div class="dropdown" id="drop-${{globalIdx}}">
                        <div class="drop-item" onclick="copyUrl('${{(r.url||'').replace(/'/g,"\\'")}}')" >
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                            Copy URL
                        </div>
                        <div class="drop-item" onclick="viewDetails(${{globalIdx}})">
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                            View Details
                        </div>
                        <div class="drop-item danger" onclick="deleteRow(${{globalIdx}})">
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/></svg>
                            Delete
                        </div>
                    </div>
                </div>
            </td>
        </tr>`;
    }}).join('');

    // pagination
    const total = filtered.length;
    const pages = Math.ceil(total / perPage);
    document.getElementById('page-info').textContent =
        `Showing ${{Math.min(start+1,total)}}–${{Math.min(start+perPage,total)}} of ${{total}}`;

    let btns = '';
    for (let p = 1; p <= pages; p++) {{
        btns += `<div class="page-btn${{p===currentPage?' active':''}}" onclick="goPage(${{p}})">${{p}}</div>`;
    }}
    document.getElementById('page-btns').innerHTML = btns;
}}

function filterTab(el, key) {{
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    el.classList.add('active');
    activeTab = key;
    currentPage = 1;
    applyFilter();
}}

function applyFilter() {{
    filtered = allRecords.filter(r => {{
        if (activeTab === 'all') return true;
        return (r.prediction||'').toLowerCase() === activeTab;
    }});
    renderTable();
}}

function sortTable(key) {{
    if (sortKey === key) sortAsc = !sortAsc;
    else {{ sortKey = key; sortAsc = true; }}
    filtered.sort((a, b) => {{
        let va = key === 'id' ? (a.id||0) : (a.scanned_at||'');
        let vb = key === 'id' ? (b.id||0) : (b.scanned_at||'');
        if (va < vb) return sortAsc ? -1 : 1;
        if (va > vb) return sortAsc ? 1 : -1;
        return 0;
    }});
    renderTable();
}}

function goPage(p) {{ currentPage = p; renderTable(); }}

function toggleMenu(idx, e) {{
    e.stopPropagation();
    document.querySelectorAll('.dropdown').forEach(d => {{
        if (d.id !== 'drop-'+idx) d.classList.remove('open');
    }});
    document.getElementById('drop-'+idx).classList.toggle('open');
}}

document.addEventListener('click', () => {{
    document.querySelectorAll('.dropdown').forEach(d => d.classList.remove('open'));
}});

function copyUrl(url) {{
    navigator.clipboard.writeText(url).catch(()=>{{}});
    document.querySelectorAll('.dropdown').forEach(d => d.classList.remove('open'));
}}

function viewDetails(idx) {{
    const r = filtered[idx];
    alert(`URL: ${{r.url}}\\nPrediction: ${{r.prediction}}\\nConfidence: ${{r.confidence}}\\nRisk Score: ${{r.risk_score}}\\nRisk Level: ${{r.risk_level}}\\nScanned: ${{r.scanned_at}}`);
    document.querySelectorAll('.dropdown').forEach(d => d.classList.remove('open'));
}}

function deleteRow(idx) {{
    if (confirm('Remove this entry from view?')) {{
        filtered.splice(idx, 1);
        if ((currentPage-1)*perPage >= filtered.length && currentPage > 1) currentPage--;
        renderTable();
    }}
    document.querySelectorAll('.dropdown').forEach(d => d.classList.remove('open'));
}}

initDates();
renderTable();
</script>
</body>
</html>"""


def show():
    try:
        st.set_page_config(page_title="PhishGuard – History", layout="wide", initial_sidebar_state="collapsed")
    except:
        pass

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

    [data-testid="stAppViewContainer"],[data-testid="stApp"] { background: transparent !important; }
    header, footer, #MainMenu { visibility: hidden; }
    section[data-testid="stSidebar"] { display: none !important; }
    html, body, .stApp { font-family: 'DM Sans', sans-serif; }

    [data-testid="stAppViewContainer"]::before {
        content: "" !important; position: fixed !important;
        top: 0 !important; left: 0 !important;
        width: 100vw !important; height: 100vh !important; z-index: -999 !important;
        background: linear-gradient(135deg,
            rgba(18,6,45,0.82) 0%,
            rgba(30,10,60,0.78) 35%,
            rgba(45,15,40,0.80) 65%,
            rgba(38,12,18,0.85) 100%) !important;
        pointer-events: none !important;
    }

    .main .block-container {
        padding: 2rem 3rem 2rem 3rem !important;
        max-width: 100% !important;
    }

    /* back button */
    div[data-testid="stButton"] button {
        background: rgba(167,139,250,0.12) !important;
        color: #c4b5fd !important;
        border: 1px solid rgba(167,139,250,0.30) !important;
        border-radius: 22px !important;
        height: 38px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        padding: 0 20px !important;
        backdrop-filter: blur(12px) !important;
        transition: all 0.22s ease !important;
    }
    div[data-testid="stButton"] button:hover {
        background: rgba(167,139,250,0.24) !important;
        box-shadow: 0 0 16px rgba(124,58,237,0.35) !important;
        transform: translateY(-2px) !important;
    }

    div[data-testid="stStatusWidget"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    # ── AUTH ──
    if "user_id" not in st.session_state:
        st.error("Please login first.")
        st.stop()

    # ── BACK BUTTON ──
    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

    # ── FETCH DATA ──
    records = []
    try:
        res = requests.get(
            f"{BACKEND_URL}/scan-history/{st.session_state.user_id}",
            timeout=10
        )
        if res.status_code == 200:
            raw = res.json()
            for i, r in enumerate(raw):
                records.append({
                    "id":          r.get("id", i + 1),
                    "url":         r.get("url", ""),
                    "prediction":  r.get("prediction", ""),
                    "confidence":  r.get("confidence", 0),
                    "risk_score":  r.get("risk_score", 0),
                    "risk_level":  r.get("risk_level", ""),
                    "scanned_at":  r.get("scanned_at", ""),
                })
    except Exception as e:
        st.warning(f"Could not connect to backend: {e}")
        # Use demo data so the UI is still visible
        records = [
            {"id": 1, "url": "https://google.com", "prediction": "Legitimate", "confidence": 0.98, "risk_score": 0.02, "risk_level": "Low Risk",    "scanned_at": "2026-02-26T10:30:00"},
            {"id": 2, "url": "https://phish-login.ru/secure", "prediction": "Phishing",    "confidence": 0.95, "risk_score": 0.95, "risk_level": "High Risk",   "scanned_at": "2026-02-26T11:15:00"},
            {"id": 3, "url": "https://paypal-verify.tk",      "prediction": "Phishing",    "confidence": 0.91, "risk_score": 0.89, "risk_level": "High Risk",   "scanned_at": "2026-02-26T12:00:00"},
            {"id": 4, "url": "https://github.com",             "prediction": "Legitimate", "confidence": 0.99, "risk_score": 0.01, "risk_level": "Low Risk",    "scanned_at": "2026-02-26T13:05:00"},
            {"id": 5, "url": "https://free-iphone15.win",      "prediction": "Suspicious", "confidence": 0.78, "risk_score": 0.65, "risk_level": "Medium Risk", "scanned_at": "2026-02-26T14:20:00"},
            {"id": 6, "url": "https://amazon.com",             "prediction": "Legitimate", "confidence": 0.97, "risk_score": 0.03, "risk_level": "Low Risk",    "scanned_at": "2026-02-26T15:00:00"},
            {"id": 7, "url": "https://login-bankofamerica.xyz","prediction": "Phishing",   "confidence": 0.93, "risk_score": 0.92, "risk_level": "High Risk",   "scanned_at": "2026-02-26T16:10:00"},
            {"id": 8, "url": "https://stackoverflow.com",      "prediction": "Legitimate", "confidence": 0.99, "risk_score": 0.01, "risk_level": "Low Risk",    "scanned_at": "2026-02-26T17:30:00"},
            {"id": 9, "url": "https://discount-deals.biz",     "prediction": "Suspicious", "confidence": 0.72, "risk_score": 0.58, "risk_level": "Medium Risk", "scanned_at": "2026-02-27T08:00:00"},
            {"id": 10,"url": "https://microsoft.com",          "prediction": "Legitimate", "confidence": 0.99, "risk_score": 0.01, "risk_level": "Low Risk",    "scanned_at": "2026-02-27T09:15:00"},
        ]

    # ── RENDER ──
    components.html(build_history_html(records), height=820, scrolling=True)


if __name__ == "__main__":
    show()