"""
Crypto & Currency Live Dashboard
- Fetches coins in 2 batches to avoid CoinGecko rate limits
- Charts only render after data is loaded
- Refresh every 5 minutes to stay comfortably within free tier limits
"""

import threading
import webbrowser
import time
import sys
from datetime import datetime

def _ensure(pkg, import_name=None):
    import importlib
    name = import_name or pkg
    try:
        return importlib.import_module(name)
    except ImportError:
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", pkg, "-q"], check=True)
        return importlib.import_module(name)

_server_thread = None
_server_running = False
_server_port = 7788

HTML_DASHBOARD = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Live Crypto Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  :root{--bg:#0a0e1a;--card:#111827;--border:#1f2937;--accent:#6366f1;--green:#10b981;--red:#ef4444;--text:#f1f5f9;--muted:#94a3b8;}
  *{margin:0;padding:0;box-sizing:border-box;}
  body{background:var(--bg);color:var(--text);font-family:'Segoe UI',system-ui,sans-serif;min-height:100vh;}
  header{display:flex;align-items:center;justify-content:space-between;padding:16px 32px;background:var(--card);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:100;}
  .logo{font-size:1.35rem;font-weight:700;}.logo span{color:var(--accent);}
  .status-bar{display:flex;align-items:center;gap:12px;font-size:.83rem;color:var(--muted);}
  .dot{width:8px;height:8px;border-radius:50%;background:var(--green);animation:pulse 1.5s infinite;}
  @keyframes pulse{0%,100%{opacity:1;transform:scale(1);}50%{opacity:.5;transform:scale(1.4);}}
  #countdown{background:var(--accent);color:#fff;padding:3px 12px;border-radius:20px;font-size:.78rem;font-weight:600;min-width:54px;text-align:center;}
  #api-status{font-size:.75rem;padding:3px 10px;border-radius:20px;background:#1e293b;}
  .tabs{display:flex;padding:0 32px;background:var(--card);border-bottom:1px solid var(--border);}
  .tab{padding:13px 22px;cursor:pointer;font-size:.88rem;font-weight:500;color:var(--muted);border-bottom:3px solid transparent;transition:all .2s;}
  .tab.active{color:var(--accent);border-bottom-color:var(--accent);}
  .ticker-wrap{overflow:hidden;background:#0d1321;border-bottom:1px solid var(--border);padding:8px 0;}
  .ticker-inner{display:flex;gap:40px;animation:ticker 40s linear infinite;white-space:nowrap;}
  @keyframes ticker{0%{transform:translateX(0);}100%{transform:translateX(-50%);}}
  .ticker-item{display:inline-flex;align-items:center;gap:8px;font-size:.83rem;}
  .ticker-sym{font-weight:700;color:var(--text);}.ticker-price{color:var(--muted);}
  main{padding:24px 32px;max-width:1400px;margin:0 auto;}
  .section{display:none;}.section.active{display:block;}
  .stats-row{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:24px;}
  @media(max-width:800px){.stats-row{grid-template-columns:repeat(2,1fr);}}
  .stat-card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:18px 20px;}
  .stat-card .label{font-size:.72rem;color:var(--muted);text-transform:uppercase;letter-spacing:.8px;margin-bottom:8px;}
  .stat-card .value{font-size:1.35rem;font-weight:700;}
  .up{color:var(--green);}.down{color:var(--red);}.neutral{color:var(--muted);}
  .crypto-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px;}
  .crypto-card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:18px;transition:transform .15s,border-color .2s;}
  .crypto-card:hover{transform:translateY(-2px);border-color:var(--accent);}
  .crypto-card.flash-green{animation:fG .5s;}
  .crypto-card.flash-red{animation:fR .5s;}
  @keyframes fG{0%,100%{background:var(--card);}50%{background:#064e3b44;}}
  @keyframes fR{0%,100%{background:var(--card);}50%{background:#7f1d1d44;}}
  .ch{display:flex;align-items:center;gap:10px;margin-bottom:12px;}
  .ci{width:38px;height:38px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.78rem;font-weight:700;flex-shrink:0;}
  .cn{font-weight:700;font-size:.95rem;}.cs{font-size:.74rem;color:var(--muted);text-transform:uppercase;}
  .cp{font-size:1.45rem;font-weight:700;margin-bottom:5px;}
  .cm{display:flex;gap:12px;font-size:.77rem;color:var(--muted);}
  .badge{padding:2px 7px;border-radius:20px;font-size:.72rem;font-weight:600;margin-left:auto;}
  .bu{background:#064e3b;color:var(--green);}.bd{background:#7f1d1d;color:var(--red);}
  .spark{margin-top:10px;height:46px;}
  .chart-grid{display:grid;grid-template-columns:2fr 1fr;gap:18px;margin-bottom:18px;}
  @media(max-width:900px){.chart-grid{grid-template-columns:1fr;}}
  .chart-card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:20px;}
  .chart-title{font-size:.9rem;font-weight:600;margin-bottom:14px;color:var(--muted);}
  .chart-wrapper{position:relative;}
  .no-data{display:flex;align-items:center;justify-content:center;color:var(--muted);font-size:.85rem;position:absolute;top:0;left:0;right:0;bottom:0;}
  .cur-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px;}
  @media(max-width:700px){.cur-grid{grid-template-columns:1fr;}}
  .cur-card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:22px;}
  .cur-title{font-weight:700;margin-bottom:16px;}
  .cur-row{display:flex;gap:8px;align-items:center;margin-bottom:10px;}
  .cur-row input,.cur-row select{flex:1;background:#1e293b;border:1px solid var(--border);border-radius:8px;padding:9px 12px;color:var(--text);font-size:.9rem;outline:none;}
  .cur-row input:focus,.cur-row select:focus{border-color:var(--accent);}
  .swap-btn{background:var(--accent);border:none;color:#fff;padding:9px 14px;border-radius:8px;cursor:pointer;font-weight:600;}
  .conv-result{background:#1e293b;border-radius:10px;padding:14px;text-align:center;font-size:1.2rem;font-weight:700;color:var(--green);margin-top:4px;}
  .rates-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:8px;}
  .rate-chip{background:#1e293b;border-radius:8px;padding:10px 12px;}
  .rate-pair{font-size:.72rem;color:var(--muted);font-weight:600;margin-bottom:3px;}
  .rate-val{font-size:.95rem;font-weight:700;}
  .loading{text-align:center;padding:50px;color:var(--muted);}
  .spinner{width:36px;height:36px;border:3px solid var(--border);border-top-color:var(--accent);border-radius:50%;animation:spin .8s linear infinite;margin:0 auto 12px;}
  @keyframes spin{to{transform:rotate(360deg);}}
  ::-webkit-scrollbar{width:5px;}::-webkit-scrollbar-track{background:var(--bg);}::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px;}
</style>
</head>
<body>
<header>
  <div class="logo">Live <span>Crypto</span> Dashboard</div>
  <div class="status-bar">
    <div class="dot"></div>
    <span>LIVE</span>
    <span id="api-status" style="color:var(--muted)">Connecting...</span>
    <span id="last-updated"></span>
    <span id="countdown">--</span>
  </div>
</header>
<div class="ticker-wrap"><div class="ticker-inner" id="ticker"><span style="color:var(--muted);padding:0 20px">Loading ticker...</span></div></div>
<div class="tabs">
  <div class="tab active" onclick="showTab('crypto',this)">Crypto Prices</div>
  <div class="tab" onclick="showTab('charts',this)">Charts</div>
  <div class="tab" onclick="showTab('currency',this)">Currency</div>
</div>
<main>
  <div id="tab-crypto" class="section active">
    <div class="stats-row">
      <div class="stat-card"><div class="label">Total Market Cap</div><div class="value" id="s-mcap">--</div></div>
      <div class="stat-card"><div class="label">24h Volume</div><div class="value" id="s-vol">--</div></div>
      <div class="stat-card"><div class="label">Gainers / Losers</div><div class="value" id="s-gl">--</div></div>
      <div class="stat-card"><div class="label">BTC Dominance</div><div class="value" id="s-dom">--</div></div>
    </div>
    <div class="crypto-grid" id="crypto-grid"><div class="loading"><div class="spinner"></div>Fetching all 10 coins...</div></div>
  </div>
  <div id="tab-charts" class="section">
    <div class="chart-grid">
      <div class="chart-card">
        <div class="chart-title">Price History - top 5 coins (each refresh = 1 data point)</div>
        <div class="chart-wrapper" style="height:280px"><canvas id="priceChart"></canvas><div class="no-data" id="price-nodata">Waiting for first data fetch...</div></div>
      </div>
      <div class="chart-card">
        <div class="chart-title">Market Cap Distribution</div>
        <div class="chart-wrapper" style="height:280px"><canvas id="pieChart"></canvas><div class="no-data" id="pie-nodata">Waiting for first data fetch...</div></div>
      </div>
    </div>
    <div class="chart-card">
      <div class="chart-title">24h Price Change % - all 10 coins</div>
      <div class="chart-wrapper" style="height:220px"><canvas id="barChart"></canvas><div class="no-data" id="bar-nodata">Waiting for first data fetch...</div></div>
    </div>
  </div>
  <div id="tab-currency" class="section">
    <div class="cur-grid">
      <div class="cur-card">
        <div class="cur-title">Currency Converter</div>
        <div class="cur-row"><input type="number" id="conv-amount" value="100" oninput="convert()"/><select id="conv-from" onchange="convert()"></select></div>
        <div class="cur-row"><button class="swap-btn" onclick="swapCurrencies()">Swap</button><select id="conv-to" onchange="convert()"></select></div>
        <div class="conv-result" id="conv-result">Enter an amount above</div>
      </div>
      <div class="cur-card">
        <div class="cur-title">Live Rates (base: USD)</div>
        <div class="rates-grid" id="rates-grid"><div class="loading"><div class="spinner"></div></div></div>
      </div>
    </div>
  </div>
</main>
<script>
var cryptoData=[], currencyRates={}, priceHistory={};
var priceChart=null, pieChart=null, barChart=null;
var countdownVal=300, countdownTimer=null, fetchInProgress=false;

var REFRESH_SECS = 300; // 5 minutes

var BATCH1=['bitcoin','ethereum','solana','binancecoin','ripple'];
var BATCH2=['cardano','avalanche-2','polkadot','dogecoin','chainlink'];
var CURRENCIES=['EUR','GBP','JPY','INR','CAD','AUD','CHF','CNY','SGD','AED','KRW','BRL'];

function setStatus(msg,color){var e=document.getElementById('api-status');e.textContent=msg;e.style.color=color||'var(--muted)';}

function fmtCountdown(s){
  if(s<=0)return '...';
  var m=Math.floor(s/60);
  var sec=s%60;
  return m+'m '+String(sec).padStart(2,'0')+'s';
}

async function fetchBatch(ids){
  var url='https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids='+ids.join(',')+'&order=market_cap_desc&sparkline=true&price_change_percentage=1h,24h,7d';
  var r=await fetch(url);
  if(!r.ok)throw new Error('HTTP '+r.status);
  return r.json();
}

async function fetchCrypto(){
  try{
    setStatus('Fetching batch 1...','var(--muted)');
    var b1=await fetchBatch(BATCH1);
    await new Promise(function(res){setTimeout(res,1500);});
    setStatus('Fetching batch 2...','var(--muted)');
    var b2=await fetchBatch(BATCH2);
    var all=[].concat(b1,b2);
    if(!all.length)throw new Error('empty');
    cryptoData=all;
    setStatus('OK - '+all.length+' coins','var(--green)');
    renderCrypto();
    updateCharts();
    updateTicker();
  }catch(e){
    setStatus('Rate limited - will retry in 5 min','var(--red)');
    console.warn('CoinGecko:',e.message);
  }
}

async function fetchCurrency(){
  try{
    var r=await fetch('https://api.frankfurter.app/latest?from=USD&to='+CURRENCIES.join(','));
    if(!r.ok)throw new Error('HTTP '+r.status);
    var d=await r.json();
    currencyRates=Object.assign({},d.rates,{USD:1});
    renderRates();populateSelects();convert();
  }catch(e){console.warn('Frankfurter:',e.message);}
}

function fmt(n){
  if(n==null)return '--';
  if(Math.abs(n)>=1e12)return '$'+(n/1e12).toFixed(2)+'T';
  if(Math.abs(n)>=1e9)return '$'+(n/1e9).toFixed(2)+'B';
  if(Math.abs(n)>=1e6)return '$'+(n/1e6).toFixed(2)+'M';
  return '$'+n.toLocaleString();
}
function fmtP(p){
  if(!p&&p!==0)return '--';
  if(p<0.001)return '$'+p.toFixed(8);
  if(p<0.01)return '$'+p.toFixed(6);
  if(p<1)return '$'+p.toFixed(4);
  return '$'+p.toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2});
}
function chgSpan(v){
  if(v==null)return '<span class="neutral">--</span>';
  var c=v>0?'up':'down';
  return '<span class="'+c+'">'+(v>0?'+':'')+v.toFixed(2)+'%</span>';
}
function hsl(s){
  var h=0;for(var i=0;i<s.length;i++)h=s.charCodeAt(i)+((h<<5)-h);
  return 'hsl('+((h%360+360)%360)+',60%,52%)';
}

function renderCrypto(){
  if(!cryptoData.length)return;
  var tm=cryptoData.reduce(function(a,c){return a+(c.market_cap||0);},0);
  var tv=cryptoData.reduce(function(a,c){return a+(c.total_volume||0);},0);
  var g=cryptoData.filter(function(c){return c.price_change_percentage_24h>0;}).length;
  document.getElementById('s-mcap').textContent=fmt(tm);
  document.getElementById('s-vol').textContent=fmt(tv);
  document.getElementById('s-gl').innerHTML='<span class="up">'+g+'</span> / <span class="down">'+(cryptoData.length-g)+'</span>';
  document.getElementById('s-dom').textContent=tm>0?((cryptoData[0].market_cap/tm)*100).toFixed(1)+'%':'--';

  var grid=document.getElementById('crypto-grid');
  if(grid.querySelector('.loading'))grid.innerHTML='';

  cryptoData.forEach(function(coin){
    if(!priceHistory[coin.id])priceHistory[coin.id]=[];
    priceHistory[coin.id].push(coin.current_price);
    if(priceHistory[coin.id].length>30)priceHistory[coin.id].shift();

    var existing=grid.querySelector('[data-id="'+coin.id+'"]');
    var oldPrice=existing?parseFloat(existing.dataset.price):null;
    var flash=oldPrice?(coin.current_price>oldPrice?' flash-green':coin.current_price<oldPrice?' flash-red':''):'';
    var chg24=coin.price_change_percentage_24h||0;
    var sym=coin.symbol.toUpperCase();
    var badge=chg24>=0
      ?'<span class="badge bu">+'+chg24.toFixed(2)+'%</span>'
      :'<span class="badge bd">'+chg24.toFixed(2)+'%</span>';

    var card='<div class="crypto-card'+flash+'" data-id="'+coin.id+'" data-price="'+coin.current_price+'">'
      +'<div class="ch"><div class="ci" style="background:'+hsl(coin.id)+'">'+sym.slice(0,3)+'</div>'
      +'<div><div class="cn">'+coin.name+'</div><div class="cs">'+sym+'</div></div>'+badge+'</div>'
      +'<div class="cp">'+fmtP(coin.current_price)+'</div>'
      +'<div class="cm"><span>MCap: '+fmt(coin.market_cap)+'</span><span>Vol: '+fmt(coin.total_volume)+'</span></div>'
      +'<div class="cm" style="margin-top:3px"><span>1h: '+chgSpan(coin.price_change_percentage_1h_in_currency)+'</span><span>7d: '+chgSpan(coin.price_change_percentage_7d_in_currency)+'</span></div>'
      +'<div class="spark"><canvas id="sp-'+coin.id+'"></canvas></div></div>';

    if(existing)existing.outerHTML=card;
    else grid.insertAdjacentHTML('beforeend',card);

    var sp=document.getElementById('sp-'+coin.id);
    if(sp&&coin.sparkline_in_7d&&coin.sparkline_in_7d.prices.length){
      var prices=coin.sparkline_in_7d.prices;
      var col=chg24>=0?'#10b981':'#ef4444';
      new Chart(sp,{type:'line',data:{labels:prices.map(function(_,i){return i;}),datasets:[{data:prices,borderColor:col,borderWidth:1.5,fill:true,backgroundColor:col+'22',pointRadius:0,tension:.4}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{enabled:false}},scales:{x:{display:false},y:{display:false}}}});
    }
  });
  document.getElementById('last-updated').textContent=new Date().toLocaleTimeString();
}

function updateCharts(){
  if(!cryptoData.length)return;
  var hasHistory=cryptoData.slice(0,5).some(function(c){return (priceHistory[c.id]||[]).length>0;});
  document.getElementById('price-nodata').style.display=hasHistory?'none':'flex';

  var lineDatasets=cryptoData.slice(0,5).map(function(coin){
    return{label:coin.name,data:(priceHistory[coin.id]||[]).slice(),borderColor:hsl(coin.id),backgroundColor:hsl(coin.id)+'33',tension:.4,pointRadius:2,fill:false,borderWidth:2};
  });
  var lineLabels=Array.from({length:30},function(_,i){return String(i+1);});
  var lineOpts={responsive:true,maintainAspectRatio:false,plugins:{legend:{labels:{color:'#94a3b8',boxWidth:10,font:{size:11}}}},scales:{x:{ticks:{color:'#475569',maxTicksLimit:10},grid:{color:'#1f2937'}},y:{ticks:{color:'#475569'},grid:{color:'#1f2937'}}}};
  if(!priceChart){priceChart=new Chart(document.getElementById('priceChart'),{type:'line',data:{labels:lineLabels,datasets:lineDatasets},options:lineOpts});}
  else{priceChart.data.datasets=lineDatasets;priceChart.update('none');}

  document.getElementById('pie-nodata').style.display='none';
  var pieData=cryptoData.slice(0,7).map(function(c){return c.market_cap||0;});
  var pieLabels=cryptoData.slice(0,7).map(function(c){return c.name;});
  var pieColors=pieLabels.map(function(n){return hsl(n.toLowerCase().replace(/ /g,'-'));});
  if(!pieChart){pieChart=new Chart(document.getElementById('pieChart'),{type:'doughnut',data:{labels:pieLabels,datasets:[{data:pieData,backgroundColor:pieColors,borderColor:'#0a0e1a',borderWidth:2}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{color:'#94a3b8',boxWidth:10,padding:8,font:{size:11}}}}}});}
  else{pieChart.data.datasets[0].data=pieData;pieChart.update('none');}

  document.getElementById('bar-nodata').style.display='none';
  var barLabels=cryptoData.map(function(c){return c.symbol.toUpperCase();});
  var barData=cryptoData.map(function(c){return parseFloat((c.price_change_percentage_24h||0).toFixed(2));});
  var barColors=barData.map(function(v){return v>=0?'#10b981':'#ef4444';});
  if(!barChart){barChart=new Chart(document.getElementById('barChart'),{type:'bar',data:{labels:barLabels,datasets:[{label:'24h %',data:barData,backgroundColor:barColors,borderRadius:5}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{ticks:{color:'#94a3b8'},grid:{color:'#1f2937'}},y:{ticks:{color:'#94a3b8'},grid:{color:'#1f2937'}}}}});}
  else{barChart.data.labels=barLabels;barChart.data.datasets[0].data=barData;barChart.data.datasets[0].backgroundColor=barColors;barChart.update('none');}
}

function updateTicker(){
  if(!cryptoData.length)return;
  var items=cryptoData.concat(cryptoData).map(function(c){
    var chg=c.price_change_percentage_24h||0;
    var cls=chg>=0?'up':'down';
    return '<span class="ticker-item"><span class="ticker-sym">'+c.symbol.toUpperCase()+'</span><span class="ticker-price">'+fmtP(c.current_price)+'</span><span class="'+cls+'">'+(chg>=0?'+':'')+chg.toFixed(2)+'%</span></span>';
  }).join('');
  document.getElementById('ticker').innerHTML=items;
}

function renderRates(){
  document.getElementById('rates-grid').innerHTML=CURRENCIES.map(function(cur){
    return '<div class="rate-chip"><div class="rate-pair">USD to '+cur+'</div><div class="rate-val">'+(currencyRates[cur]||'--')+'</div></div>';
  }).join('');
}
function populateSelects(){
  var all=Object.keys(currencyRates).sort();
  ['conv-from','conv-to'].forEach(function(id,i){
    var sel=document.getElementById(id);var cur=sel.value;
    sel.innerHTML=all.map(function(c){return '<option value="'+c+'"'+(c===(cur||(i===0?'USD':'INR'))?' selected':'')+'>'+c+'</option>';}).join('');
  });
}
function convert(){
  var amt=parseFloat(document.getElementById('conv-amount').value)||0;
  var from=document.getElementById('conv-from').value;
  var to=document.getElementById('conv-to').value;
  if(!currencyRates[from]||!currencyRates[to]){document.getElementById('conv-result').textContent='--';return;}
  var res=amt*(currencyRates[to]/currencyRates[from]);
  document.getElementById('conv-result').textContent=amt.toLocaleString()+' '+from+' = '+res.toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:4})+' '+to;
}
function swapCurrencies(){
  var f=document.getElementById('conv-from'),t=document.getElementById('conv-to');
  var tmp=f.value;f.value=t.value;t.value=tmp;convert();
}

function showTab(name,el){
  document.querySelectorAll('.section').forEach(function(s){s.classList.remove('active');});
  document.querySelectorAll('.tab').forEach(function(t){t.classList.remove('active');});
  document.getElementById('tab-'+name).classList.add('active');
  el.classList.add('active');
  if(name==='charts'){setTimeout(function(){if(priceChart)priceChart.resize();if(pieChart)pieChart.resize();if(barChart)barChart.resize();},50);}
}

function startCountdown(secs){
  clearInterval(countdownTimer);
  countdownVal=secs;
  document.getElementById('countdown').textContent=fmtCountdown(countdownVal);
  countdownTimer=setInterval(function(){
    countdownVal--;
    document.getElementById('countdown').textContent=fmtCountdown(countdownVal);
    if(countdownVal<=0){clearInterval(countdownTimer);if(!fetchInProgress)doFetch();}
  },1000);
}

async function doFetch(){
  fetchInProgress=true;
  await fetchCrypto();
  fetchInProgress=false;
  startCountdown(REFRESH_SECS);
}

(async function(){
  await fetchCurrency();
  await doFetch();
})();
</script>
</body>
</html>"""


def _build_app():
    _ensure("flask")
    from flask import Flask, Response
    import logging
    app = Flask(__name__)
    app.logger.disabled = True
    logging.getLogger('werkzeug').setLevel(logging.ERROR)

    @app.route("/")
    def index():
        return Response(HTML_DASHBOARD, mimetype="text/html")

    @app.route("/health")
    def health():
        return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

    return app


def _run_server(port):
    global _server_running
    app = _build_app()
    _server_running = True
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


def run(command="start", port=None):
    global _server_thread, _server_running, _server_port

    port = int(port or _server_port)
    cmd  = str(command).strip().lower()

    if cmd in ("start","launch","open","run"):
        if _server_running and _server_thread and _server_thread.is_alive():
            url = "http://localhost:{}".format(port)
            webbrowser.open(url)
            return "Dashboard already running -> {}\nOpened in browser.".format(url)

        _server_port  = port
        _server_thread = threading.Thread(target=_run_server, args=(port,), daemon=True)
        _server_thread.start()
        time.sleep(1.8)

        url = "http://localhost:{}".format(port)
        try: webbrowser.open(url); opened = True
        except: opened = False

        return (
            "Live Crypto & Currency Dashboard launched!\n\n"
            "  URL    -> {}\n"
            "  Port   -> {}\n"
            "  Browser-> {}\n\n"
            "Refresh interval: every 5 minutes (rate-limit safe)\n"
            "Countdown shown in header as mm:ss\n\n"
            "Use 'stop' to shut down."
        ).format(url, port, "Opened automatically" if opened else "Open manually at URL above")

    elif cmd == "status":
        alive = _server_running and _server_thread and _server_thread.is_alive()
        return "RUNNING -> http://localhost:{}".format(_server_port) if alive else "STOPPED | Use 'start' to launch."

    elif cmd in ("stop","kill","shutdown"):
        _server_running = False
        return "Dashboard server stopped."

    else:
        return "Commands: start [port] | status | stop"
