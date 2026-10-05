import streamlit as st
import pandas as pd
import numpy as np
import math

st.set_page_config(page_title='GridPredict Pro', page_icon='⚡', layout='wide', initial_sidebar_state='expanded')

st.markdown('''<style>
:root{--bg:#06101c;--panel:#0c1c2d;--line:#203b55;--text:#edf6ff;--muted:#8ea7bd;--cyan:#36d9ff;--green:#39e58c;--amber:#ffc14d;--red:#ff6075}
[data-testid="stAppViewContainer"]{background:radial-gradient(circle at 20% 0%,#12304b 0%,var(--bg) 42%,#040a11 100%);color:var(--text)}
[data-testid="stSidebar"]{background:#071421;border-right:1px solid var(--line)}
.block-container{max-width:1500px;padding-top:1.1rem}.hero{padding:30px 32px;border:1px solid #24506d;border-radius:24px;background:radial-gradient(circle at 90% 10%,rgba(54,217,255,.18),transparent 30%),linear-gradient(135deg,#102940,#07121e);box-shadow:0 18px 60px #0006;margin-bottom:18px}.kicker{color:var(--cyan);font-weight:800;letter-spacing:.14em;font-size:.78rem}.title{font-size:2.65rem;font-weight:900;margin:5px 0}.sub{color:#b7cadc;max-width:950px}.pill{display:inline-block;padding:6px 11px;border-radius:999px;font-weight:800;font-size:.75rem;margin-top:12px}.ok{color:#61f2aa;background:#39e58c14;border:1px solid #39e58c4d}.warn{color:#ffd477;background:#ffc14d14;border:1px solid #ffc14d4d}.danger{color:#ff8c9a;background:#ff607514;border:1px solid #ff60754d}.card{background:linear-gradient(145deg,#10243a,#091725);border:1px solid #1e3b55;border-radius:17px;padding:16px;min-height:105px}.label{color:var(--muted);font-size:.73rem;text-transform:uppercase;letter-spacing:.08em}.value{font-size:1.65rem;font-weight:850;margin-top:4px}.note{color:var(--muted);font-size:.75rem}.box{border:1px solid #1c3851;border-radius:19px;padding:19px;background:#091827bb;margin:10px 0 18px}.box h3{margin:0 0 4px}.box p{color:var(--muted);font-size:.84rem}.equip{border:1px solid #31536d;border-radius:14px;padding:14px;text-align:center;background:#0b2033;min-height:100px}.equip .icon{font-size:2rem}.equip b{display:block}.equip small{color:var(--muted)}.arrow{font-size:1.7rem;text-align:center;padding-top:28px;color:var(--cyan)}.alert{padding:11px 14px;border-radius:9px;margin:7px 0;border-left:4px solid}.alert.red{background:#ff607510;border-color:var(--red)}.alert.yellow{background:#ffc14d10;border-color:var(--amber)}.alert.blue{background:#36d9ff10;border-color:var(--cyan)}.footer{text-align:center;color:#617b93;padding:28px 0;font-size:.75rem}
</style>''', unsafe_allow_html=True)

D={'plant':'My Industrial Plant','voltage':415.0,'freq':50.0,'phases':3,'tr_kva':500.0,'primary_kv':11.0,'secondary_v':415.0,'z':5.0,'eff':97.0,'load_kw':285.0,'pf':.86,'motor_pct':55.0,'lighting':35.0,'other':60.0,'ambient':32.0,'breaker':800.0,'trip':720.0,'uv':.90,'ov':1.10,'overload':90.0,'tripped':False}
for k,v in D.items(): st.session_state.setdefault(k,v)

def clamp(x,a,b): return max(a,min(b,x))
def calc():
    V=float(st.session_state.voltage); kw=max(float(st.session_state.load_kw),0); pf=clamp(float(st.session_state.pf),.05,1)
    S=kw/pf if pf else 0; q=math.sqrt(max(S*S-kw*kw,0)); I=S*1000/(math.sqrt(3)*V) if V else 0
    load=100*S/max(float(st.session_state.tr_kva),.001)
    eff=clamp(float(st.session_state.eff)-max(load-80,0)*.03,70,99.9)
    qcap=kw*(math.tan(math.acos(pf))-math.tan(math.acos(.95))) if pf<.95 else 0
    fc=(V*V/1000)/max(float(st.session_state.z)/100,.0001); fmva=fc*math.sqrt(3)*V/1e6
    health=100-(25 if load>90 else 10 if load>80 else 0)-(12 if pf<.85 else 5 if pf<.92 else 0)
    if I>float(st.session_state.trip): health-=10
    if st.session_state.tripped: health=30
    return {'V':V,'kw':kw,'pf':pf,'S':S,'q':q,'I':I,'load':load,'eff':eff,'qcap':max(0,qcap),'fc':fc,'fmva':fmva,'health':int(clamp(health,0,100)),'tr_kva':float(st.session_state.tr_kva)}
def state(c): return ('CRITICAL','danger') if st.session_state.tripped or c['health']<45 else ('WARNING','warn') if c['health']<75 or c['load']>85 or c['pf']<.85 else ('HEALTHY','ok')
def card(a,b,c=''): return f'<div class="card"><div class="label">{a}</div><div class="value">{b}</div><div class="note">{c}</div></div>'
def box(title,sub=''): st.markdown(f'<div class="box"><h3>{title}</h3><p>{sub}</p>',unsafe_allow_html=True)
def end(): st.markdown('</div>',unsafe_allow_html=True)

def profile(c):
    shape=np.array([.45,.40,.38,.40,.48,.62,.78,.88,.94,.97,.92,.89,.91,.96,1,.98,.94,.88,.80,.70,.62,.55,.50,.47])
    return pd.DataFrame({'Hour':np.arange(24),'Load_kW':c['kw']*shape})

c=calc(); status,cls=state(c)
with st.sidebar:
    st.markdown('## ⚡ GridPredict Pro'); st.caption('Industrial Electrical Intelligence Console'); st.divider()
    page=st.radio('NAVIGATION',['Command Center','System Configuration','Power & Power Factor','Transformer Lab','Fault & Protection','Load Analytics','Energy & Cost','Engineering Report'],key='nav')
    st.divider(); st.markdown(f'**System:** {st.session_state.plant}')
    st.markdown(f'**Status:** <span class="pill {cls}">{status}</span>',unsafe_allow_html=True)
    if st.session_state.tripped:
        st.error('SIMULATED TRIP ACTIVE')
        if st.button('Reset simulated trip',key='reset_trip'): st.session_state.tripped=False; st.rerun()
    st.divider(); st.caption('Analysis/simulation only. No real breaker, relay or switchgear is controlled.')

st.markdown(f'''<div class="hero"><div class="kicker">INDUSTRIAL ELECTRICAL INTELLIGENCE PLATFORM</div><div class="title">⚡ GridPredict Pro</div><div class="sub">A deep-layer electrical analysis console driven by your own grid, transformer, load and protection data. Monitor, calculate, visualize, simulate and report from one interface.</div><span class="pill {cls}">{status} • {st.session_state.plant}</span></div>''',unsafe_allow_html=True)

if page=='System Configuration':
    st.header('System & Asset Configuration'); st.caption('This is the source-of-truth layer. Every module below reads these values.')
    a,b,c1=st.tabs(['Grid','Transformer','Loads & PF'])
    with a:
        x,y,z=st.columns(3)
        with x: st.text_input('Plant / system name',key='plant'); st.number_input('Nominal voltage (V)',50.,100000.,key='voltage',step=1.)
        with y: st.number_input('Frequency (Hz)',1.,1000.,key='freq',step=.5); st.selectbox('Phases',[1,2,3],key='phases')
        with z: st.number_input('Ambient temperature (°C)',-30.,70.,key='ambient',step=1.)
    with b:
        x,y,z=st.columns(3)
        with x: st.number_input('Transformer rating (kVA)',1.,100000.,key='tr_kva',step=10.); st.number_input('Primary voltage (kV)',.1,500.,key='primary_kv',step=.1)
        with y: st.number_input('Secondary voltage (V)',50.,100000.,key='secondary_v',step=1.); st.number_input('Impedance (%)',.1,30.,key='z',step=.1)
        with z: st.number_input('Rated efficiency (%)',70.,100.,key='eff',step=.1)
    with c1:
        x,y,z=st.columns(3)
        with x: st.number_input('Present active load (kW)',0.,100000.,key='load_kw',step=1.)
        with y: st.slider('Power factor',.50,1.,key='pf',step=.01)
        with z: st.slider('Motor share (%)',0.,100.,key='motor_pct',step=1.)
        x,y,z=st.columns(3)
        with x: st.number_input('Lighting load (kW)',0.,100000.,key='lighting',step=1.)
        with y: st.number_input('Other load (kW)',0.,100000.,key='other',step=1.)
        with z: st.info(f"Calculated apparent power: **{c['S']:.1f} kVA**")
    st.subheader('Protection limits')
    x,y,z,q=st.columns(4)
    with x: st.number_input('Breaker rating (A)',1.,100000.,key='breaker',step=1.)
    with y: st.number_input('Trip setting (A)',1.,100000.,key='trip',step=1.)
    with z: st.slider('UV threshold (p.u.)',.70,1.,key='uv')
    with q: st.slider('OV threshold (p.u.)',1.,1.30,key='ov')
    st.slider('Transformer warning limit (%)',50.,110.,key='overload')
    if st.button('🚀 Apply system model',type='primary',use_container_width=True,key='apply_model'):
        st.success('Model updated. All pages now use the entered values.')
        st.rerun()

elif page=='Command Center':
    st.header('Command Center'); st.caption('The single-screen answer to: what is happening in the electrical system?')
    cols=st.columns(6); vals=[('Voltage',f"{c['V']:.1f} V",f"{st.session_state.freq:.1f} Hz"),('Current',f"{c['I']:.1f} A",f"{c['S']:.1f} kVA"),('Active Power',f"{c['kw']:.1f} kW",'present load'),('PF',f"{c['pf']:.2f}",'cos φ'),('Transformer',f"{c['load']:.1f}%",f"{c['S']:.1f}/{c['tr_kva']:.0f} kVA"),('Health',f"{c['health']}/100",status)]
    for col,v in zip(cols,vals): col.markdown(card(*v),unsafe_allow_html=True)
    box('Electrical Single-Line View','A visual plant path linked to your configured system values.')
    a,b,d,e,f=st.columns([1.3,.3,1.3,.3,1.3])
    a.markdown(f'<div class="equip"><div class="icon">⚡</div><b>UTILITY GRID</b><small>{st.session_state.primary_kv:.1f} kV • {st.session_state.freq:.0f} Hz</small></div>',unsafe_allow_html=True)
    b.markdown('<div class="arrow">→</div>',unsafe_allow_html=True)
    d.markdown(f'<div class="equip"><div class="icon">🔌</div><b>TRANSFORMER</b><small>{c["load"]:.1f}% loaded • {c["tr_kva"] if "tr_kva" in c else st.session_state.tr_kva:.0f} kVA</small></div>',unsafe_allow_html=True)
    e.markdown('<div class="arrow">→</div>',unsafe_allow_html=True)
    f.markdown(f'<div class="equip"><div class="icon">🏭</div><b>PLANT LOAD</b><small>{c["kw"]:.1f} kW • PF {c["pf"]:.2f}</small></div>',unsafe_allow_html=True)
    end()
    l,r=st.columns([1.6,1])
    with l:
        box('24-Hour Load Profile','Industrial demand profile generated from the present load input.'); st.line_chart(profile(c).set_index('Hour'),height=300); end()
    with r:
        box('Load Composition','Motor, lighting and other demand share.'); vals=pd.Series({'Motor':c['kw']*st.session_state.motor_pct/100,'Lighting':min(st.session_state.lighting,c['kw']),'Other':min(st.session_state.other,c['kw'])}); vals=vals[vals>0]; total=vals.sum(); start=0; colors=['#36d9ff','#a98bff','#39e58c']; stops=[]
        for i,v in enumerate(vals):
            endp=start+v/total*100; stops.append(f'{colors[i%3]} {start:.1f}% {endp:.1f}%'); start=endp
        legend=''.join([f'<div style="margin:7px 0"><b>{n}</b> — {v:.1f} kW</div>' for n,v in vals.items()])
        st.markdown(f'<div style="display:flex;gap:22px;align-items:center"><div style="width:170px;height:170px;border-radius:50%;background:conic-gradient({",".join(stops)})"></div><div>{legend}</div></div>',unsafe_allow_html=True); end()
    box('Intelligent Alerts','Rule-based diagnostics using your configured limits.')
    alerts=[]
    if c['load']>100: alerts.append(('red',f'Transformer overload: {c["load"]:.1f}% of rating.'))
    elif c['load']>st.session_state.overload: alerts.append(('yellow',f'Transformer loading {c["load"]:.1f}% exceeds warning limit.'))
    if c['pf']<.85: alerts.append(('red',f'Low PF {c["pf"]:.2f}; reactive demand ≈ {c["q"]:.1f} kVAr.'))
    elif c['pf']<.92: alerts.append(('yellow',f'PF {c["pf"]:.2f} could be improved.'))
    if c['I']>st.session_state.trip: alerts.append(('red',f'Operating current {c["I"]:.1f} A exceeds simulated trip setting {st.session_state.trip:.1f} A.'))
    if c['I']>.9*st.session_state.breaker: alerts.append(('yellow','Current exceeds 90% of breaker rating.'))
    if not alerts: alerts=[('blue','No configured alarm rule is currently active.')]
    for typ,msg in alerts: st.markdown(f'<div class="alert {typ}">{msg}</div>',unsafe_allow_html=True)
    end()

elif page=='Power & Power Factor':
    st.header('Power & Power-Factor Intelligence'); st.caption('See P, Q and S together, then simulate compensation.')
    cols=st.columns(4)
    for col,v in zip(cols,[('Active P',f"{c['kw']:.1f} kW",'real power'),('Reactive Q',f"{c['q']:.1f} kVAr",'reactive demand'),('Apparent S',f"{c['S']:.1f} kVA",'total electrical loading'),('PF',f"{c['pf']:.2f}",'power factor')]): col.markdown(card(*v),unsafe_allow_html=True)
    box('Power Triangle Data','A bar view of active, reactive and apparent power.'); st.bar_chart(pd.DataFrame({'Value':[c['kw'],c['q'],c['S']]},index=['Active kW','Reactive kVAr','Apparent kVA']),height=280); end()
    st.subheader('PF Correction Simulator')
    target=st.slider('Target PF',.80,1.,.95,.01,key='target_pf')
    qcap=c['kw']*(math.tan(math.acos(c['pf']))-math.tan(math.acos(target))) if c['pf']<target else 0
    newS=c['kw']/target; newI=newS*1000/(math.sqrt(3)*c['V']) if c['V'] else 0
    a,b,d=st.columns(3); a.markdown(card('Required compensation',f'{max(0,qcap):.1f} kVAr','estimated capacitor bank'),unsafe_allow_html=True); b.markdown(card('New apparent power',f'{newS:.1f} kVA',f'from {c["S"]:.1f} kVA'),unsafe_allow_html=True); d.markdown(card('New line current',f'{newI:.1f} A',f'from {c["I"]:.1f} A'),unsafe_allow_html=True)
    box('Current vs Corrected'); st.bar_chart(pd.DataFrame({'Current PF':[c['pf']],'Target PF':[target]}).T,height=220); end()

elif page=='Transformer Lab':
    st.header('Transformer Intelligence Lab'); st.caption('Loading, efficiency and operating-envelope visualization.')
    cols=st.columns(4)
    for col,v in zip(cols,[('Rating',f'{st.session_state.tr_kva:.0f} kVA','nameplate'),('Apparent load',f'{c["S"]:.1f} kVA','calculated'),('Loading',f'{c["load"]:.1f}%','of rating'),('Efficiency',f'{c["eff"]:.2f}%','estimated')]): col.markdown(card(*v),unsafe_allow_html=True)
    box('Transformer Status','Visual status changes with calculated loading.')
    icon='🔴' if c['load']>100 else '🟡' if c['load']>85 else '🟢'; width=clamp(c['load'],0,100)
    st.markdown(f'<div style="text-align:center;font-size:4rem">{icon}</div><h2 style="text-align:center">TRANSFORMER</h2><p style="text-align:center">{st.session_state.primary_kv:.1f} kV → {st.session_state.secondary_v:.0f} V</p><div style="height:20px;background:#142a3e;border-radius:20px;overflow:hidden"><div style="height:100%;width:{width:.1f}%;background:linear-gradient(90deg,#39e58c,#ffc14d,#ff6075)"></div></div><p style="text-align:center">{c["load"]:.1f}% loading</p>',unsafe_allow_html=True); end()
    box('Transformer Loading Curve','Explore the operating envelope from light load to overload.')
    demand=np.linspace(1,max(st.session_state.tr_kva*1.25,c['S']*1.25),50); st.line_chart(pd.DataFrame({'Loading_%':100*demand/st.session_state.tr_kva},index=demand),height=300); end()
    if c['load']>100: st.error('Simulated overload condition. Review load transfer, cooling, diversity and protection coordination.')
    elif c['load']>85: st.warning('High transformer loading. Treat this as an engineering screening indicator.')
    else: st.success('Transformer loading is within the configured range.')

elif page=='Fault & Protection':
    st.header('Fault Analysis & Protection Simulator'); st.caption('Educational simulation only — it cannot trip or control real electrical hardware.')
    ft=st.selectbox('Fault / abnormal scenario',['Three-phase fault','L-G fault','L-L fault','L-L-G fault','Overload','Undervoltage','Overvoltage'],key='fault_type')
    mult={'Three-phase fault':1,'L-G fault':.86,'L-L fault':.87,'L-L-G fault':.92}
    if ft in mult:
        fi=c['fc']*mult[ft]; fm=fi*math.sqrt(3)*c['V']/1e6
        cols=st.columns(3); cols[0].markdown(card('Estimated fault current',f'{fi/1000:.2f} kA','simplified estimate'),unsafe_allow_html=True); cols[1].markdown(card('Fault level',f'{fm:.2f} MVA','approximate'),unsafe_allow_html=True); cols[2].markdown(card('Transformer impedance',f'{st.session_state.z:.2f}%','input'),unsafe_allow_html=True)
    else:
        cols=st.columns(3); cols[0].markdown(card('Operating current',f'{c["I"]:.1f} A','calculated'),unsafe_allow_html=True); cols[1].markdown(card('Trip setting',f'{st.session_state.trip:.1f} A','configured'),unsafe_allow_html=True); cols[2].markdown(card('Voltage',f'{c["V"]:.1f} V','configured'),unsafe_allow_html=True)
    trigger=False
    if ft in mult: trigger=True; reason=f'{ft} selected for simulation. Detailed relay coordination requires full network and protection data.'
    elif ft=='Overload': trigger=c['I']>=st.session_state.trip or c['load']>100; reason='Current/transformer loading exceeds the simulated threshold.' if trigger else 'No overload trip condition.'
    elif ft=='Undervoltage': pu=c['V']/st.session_state.secondary_v; trigger=pu<st.session_state.uv; reason=f'Voltage is {pu:.3f} p.u.'
    else: pu=c['V']/st.session_state.secondary_v; trigger=pu>st.session_state.ov; reason=f'Voltage is {pu:.3f} p.u.'
    box('Protection Decision','Transparent rule-based result; no physical control is performed.')
    if trigger:
        st.error('SIMULATED PROTECTION ACTION'); st.write(reason)
        if st.button('⚠️ Simulate breaker trip',type='primary',key='trip_button'): st.session_state.tripped=True; st.rerun()
    else: st.success('No simulated trip condition.'); st.write(reason)
    end()
    box('Breaker Operating Envelope','Current utilization against the configured breaker rating.'); amps=np.linspace(0,max(st.session_state.breaker*1.25,c['I']*1.25,10),60); st.line_chart(pd.DataFrame({'Utilization_%':100*amps/st.session_state.breaker},index=amps),height=280); end()

elif page=='Load Analytics':
    st.header('Load Analytics & Forecasting'); st.caption('Use simulated data or upload your own CSV. Recommended columns: timestamp and load_kw.')
    up=st.file_uploader('Upload historical load CSV',type=['csv'],key='csv_upload')
    data=None
    if up:
        try:
            raw=pd.read_csv(up); cols={str(x).lower().strip():x for x in raw.columns}; lc=next((cols[k] for k in ['load_kw','kw','load','active_power_kw'] if k in cols),None)
            if lc is None: st.error('No load column found. Name one column load_kw, kw, load or active_power_kw.')
            else: data=pd.DataFrame({'Load_kW':pd.to_numeric(raw[lc],errors='coerce')}).dropna().reset_index(drop=True); st.success(f'Loaded {len(data)} observations.')
        except Exception as e: st.error(f'CSV error: {e}')
    if data is None: data=profile(c)[['Load_kW']]; st.info('No CSV uploaded — using a 24-hour profile based on your current load.')
    box('Load Trend','Historical or simulated demand.'); st.line_chart(data,height=320); end()
    peak=float(data.Load_kW.max()); avg=float(data.Load_kW.mean()); low=float(data.Load_kW.min())
    cols=st.columns(4); cols[0].markdown(card('Peak',f'{peak:.1f} kW','maximum'),unsafe_allow_html=True); cols[1].markdown(card('Average',f'{avg:.1f} kW','mean'),unsafe_allow_html=True); cols[2].markdown(card('Minimum',f'{low:.1f} kW','minimum'),unsafe_allow_html=True); cols[3].markdown(card('Peak transformer use',f'{100*peak/st.session_state.tr_kva:.1f}%','screening indicator'),unsafe_allow_html=True)
    box('Simple Transparent Forecast','Rolling average + trend estimator. It is intentionally transparent rather than pretending to be certified AI.')
    horizon=st.slider('Forecast horizon',3,24,8,key='horizon'); n=min(5,len(data)); base=float(data.Load_kW.tail(n).mean()); trend=float(data.Load_kW.tail(min(10,len(data))).mean()-data.Load_kW.head(min(10,len(data))).mean())/max(len(data)-1,1); future=[max(0,base+trend*(i+1)) for i in range(horizon)]; st.line_chart(pd.DataFrame({'Forecast_kW':future},index=np.arange(len(data),len(data)+horizon)),height=280); end()

elif page=='Energy & Cost':
    st.header('Energy, Efficiency & Cost Explorer'); st.caption('Convert operating assumptions into energy and cost estimates.')
    a,b,c1=st.columns(3)
    with a: hrs=st.number_input('Operating hours/day',1.,24.,12.,.5,key='hours_day')
    with b: days=st.number_input('Operating days/month',1,31,26,1,key='days_month')
    with c1: tariff=st.number_input('Tariff (₹/kWh)',0.,100.,8.,.1,key='tariff')
    kwh=c['kw']*hrs*days; cost=kwh*tariff
    cols=st.columns(4)
    for col,v in zip(cols,[('Daily energy',f'{c["kw"]*hrs:.0f} kWh','estimate'),('Monthly energy',f'{kwh:,.0f} kWh','estimate'),('Monthly cost',f'₹{cost:,.0f}','estimate'),('Annualized',f'₹{12*cost:,.0f}','estimate')]): col.markdown(card(*v),unsafe_allow_html=True)
    box('Energy by Load Category','Monthly energy contribution by configured category.'); e=pd.DataFrame({'Monthly_kWh':[c['kw']*st.session_state.motor_pct/100*hrs*days,min(st.session_state.lighting,c['kw'])*hrs*days,min(st.session_state.other,c['kw'])*hrs*days]},index=['Motor','Lighting','Other']); st.bar_chart(e,height=300); end()
    box('What-if Explorer','Change the load multiplier and see the monthly cost move.'); factor=st.slider('Load multiplier',.5,1.5,1.,.01,key='load_multiplier'); st.metric('What-if monthly cost',f'₹{cost*factor:,.0f}',f'{cost*(factor-1):+,.0f} ₹ vs current'); end()

else:
    st.header('Engineering Report & Data Snapshot'); st.caption('A presentation-ready snapshot of the current model.')
    report=pd.DataFrame([('Plant',st.session_state.plant),('Voltage',f'{c["V"]:.2f} V'),('Frequency',f'{st.session_state.freq:.2f} Hz'),('Phases',st.session_state.phases),('Transformer',f'{st.session_state.tr_kva:.2f} kVA'),('Primary',f'{st.session_state.primary_kv:.2f} kV'),('Secondary',f'{st.session_state.secondary_v:.2f} V'),('Impedance',f'{st.session_state.z:.2f}%'),('Active power',f'{c["kw"]:.2f} kW'),('Reactive power',f'{c["q"]:.2f} kVAr'),('Apparent power',f'{c["S"]:.2f} kVA'),('Power factor',f'{c["pf"]:.3f}'),('Current',f'{c["I"]:.2f} A'),('Transformer loading',f'{c["load"]:.2f}%'),('Efficiency',f'{c["eff"]:.2f}%'),('Health',f'{c["health"]}/100'),('Status',status),('Simulated trip','YES' if st.session_state.tripped else 'NO')],columns=['Parameter','Value'])
    st.dataframe(report,use_container_width=True,hide_index=True)
    st.subheader('Recommendations'); rec=[]
    if c['pf']<.95: rec.append(f'Investigate reactive compensation; estimated PF 0.95 requirement ≈ {c["qcap"]:.1f} kVAr.')
    if c['load']>85: rec.append('Review transformer loading, cooling, diversity and load-transfer options.')
    if c['I']>.9*st.session_state.breaker: rec.append('Review feeder/breaker loading and protection coordination.')
    if not rec: rec.append('No major rule-based recommendation was triggered.')
    for r in rec: st.markdown(f'<div class="alert blue">• {r}</div>',unsafe_allow_html=True)
    st.download_button('⬇️ Download CSV engineering snapshot',report.to_csv(index=False).encode(), 'GridPredict_Engineering_Report.csv','text/csv',key='download_report')

st.markdown('<div class="footer">GridPredict Pro • Electrical analysis and simulation platform • Results are engineering estimates and must not be used as a substitute for certified protection studies or real-time control systems.</div>',unsafe_allow_html=True)
