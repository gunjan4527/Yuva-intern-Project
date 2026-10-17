import pandas as pd, numpy as np, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch
O='/tmp/w3/final/'
BLUE,ORG,AQUA,YEL='#2a78d6','#eb6834','#1baf7a','#eda100'; GRAY='#b9b8b3'; INK='#0b0b0b'; INK2='#52514e'; GRID='#e4e3df'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.edgecolor':GRID,'axes.labelcolor':INK2,'xtick.color':INK2,'ytick.color':INK2,'text.color':INK,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white','axes.facecolor':'white'})
def style(ax,gridx=False,gridy=True):
    ax.spines['left'].set_color(GRID); ax.spines['bottom'].set_color(GRID)
    if gridy: ax.yaxis.grid(True,color=GRID,lw=0.7); 
    if gridx: ax.xaxis.grid(True,color=GRID,lw=0.7)
    ax.set_axisbelow(True)
def save(fig,name): fig.savefig(O+name,dpi=200,bbox_inches='tight',facecolor='white'); plt.close(fig)
d=pd.read_csv('/tmp/w2/out/esg_clean_panel_2000_2022.csv')
raw=pd.read_csv('/tmp/w2/raw/owid-co2-data.csv',usecols=['iso_code','year','gdp']).rename(columns={'iso_code':'iso3','gdp':'gdp_const'})
d=d.merge(raw,on=['iso3','year'],how='left')
S={}
p=d.pivot(index='iso3',columns='year',values='co2_mt'); nm=d.drop_duplicates('iso3').set_index('iso3').country
tot=p.sum(); y22=d[d.year==2022].set_index('iso3')
S['tot']={int(k):float(v) for k,v in tot.items()}
# FIG1 line total
fig,ax=plt.subplots(figsize=(6.8,3.2)); yrs=tot.index; ax.plot(yrs,tot.values/1000,color=BLUE,lw=2)
ax.set_ylabel('CO2 emissions (billion tonnes)'); ax.set_ylim(20,40); ax.set_xlim(2000,2023.2); style(ax)
for yr,lab,dy in [(2009,'2009: global financial\ncrisis, -1.6%',-4.2),(2020,'2020: COVID-19,\n-4.2%',-4.2)]:
    ax.plot(yr,tot[yr]/1000,'o',color=ORG,ms=6,mec='white',mew=1.5,zorder=5); ax.annotate(lab,(yr,tot[yr]/1000),(yr,tot[yr]/1000+dy),ha='center',fontsize=8,color=INK2,arrowprops=dict(arrowstyle='-',color=GRAY,lw=0.8))
ax.annotate(f'{tot[2000]/1000:.1f}',(2000,tot[2000]/1000),(2000.2,tot[2000]/1000+1.1),fontsize=8.5,color=INK)
ax.annotate(f'{tot[2022]/1000:.1f}',(2022,tot[2022]/1000),(2021.1,tot[2022]/1000+1.3),fontsize=8.5,color=INK)
save(fig,'fig1_total.png')
# FIG2 top10 bar
t=y22.sort_values('co2_mt',ascending=False).head(10)
fig,ax=plt.subplots(figsize=(6.8,3.6)); cols=[BLUE if i=='IND' else GRAY for i in t.index]
ax.barh(t.country[::-1],t.co2_mt[::-1]/1000,color=cols[::-1],height=0.62); style(ax,gridx=True,gridy=False); ax.set_xlabel('CO2 emissions in 2022 (billion tonnes)')
for i,(c,v) in enumerate(zip(t.country[::-1],t.co2_mt[::-1]/1000)): ax.text(v+0.15,i,f'{v:.2f}',va='center',fontsize=8.5,color=INK)
ax.set_xlim(0,13.2); save(fig,'fig2_top10.png')
S['top10']=[(r.country,float(r.co2_mt)) for r in t.itertuples()]
# FIG3 donut
sh={'China':y22.loc['CHN','co2_mt'],'United States':y22.loc['USA','co2_mt'],'India':y22.loc['IND','co2_mt']}; rest=y22.co2_mt.sum()-sum(sh.values())
vals=list(sh.values())+[rest]; labs=list(sh.keys())+['Rest of world\n(189 countries)']; tt=sum(vals)
fig,ax=plt.subplots(figsize=(5.6,3.6)); w,_=ax.pie(vals,colors=[BLUE,ORG,AQUA,GRAY],startangle=90,counterclock=False,wedgeprops=dict(width=0.38,edgecolor='white',linewidth=2))
import math
for wi,v,l in zip(w,vals,labs):
    a=math.radians((wi.theta1+wi.theta2)/2); x,yv=math.cos(a),math.sin(a)
    ax.annotate(f'{l}\n{v/tt*100:.1f}%',(x*0.81,yv*0.81),(x*1.42,yv*1.28),ha='center',va='center',fontsize=9,color=INK,arrowprops=dict(arrowstyle='-',color=GRAY,lw=0.8))
ax.text(0,0,f'{tt/1000:.1f}\nbillion t',ha='center',va='center',fontsize=10,color=INK); ax.set_aspect('equal'); save(fig,'fig3_share.png')
S['share']={k:float(v/tt*100) for k,v in zip(['China','United States','India','Rest'],vals)}
# FIG4 per capita lines
wp=d.groupby('year').apply(lambda x:x.co2_mt.sum()*1e6/x.population.sum())
fig,ax=plt.subplots(figsize=(6.8,3.4))
for iso,c,lab in [('USA',AQUA,'United States'),('CHN',ORG,'China'),('IND',BLUE,'India')]:
    s=d[d.iso3==iso].set_index('year').co2_per_capita_t; ax.plot(s.index,s.values,color=c,lw=2); ax.text(2022.25,s[2022]-(0.5 if iso=='IND' else 0),f'{lab} {s[2022]:.1f}',color=INK,va='center',fontsize=8.5)
ax.plot(wp.index,wp.values,color=INK2,lw=1.4,ls=(0,(4,3))); ax.text(2022.25,wp[2022]+0.6,f'192-country avg {wp[2022]:.1f}',color=INK2,va='center',fontsize=8)
ax.set_ylabel('CO2 per person (tonnes)'); ax.set_xlim(2000,2028); ax.set_xticks([2000,2005,2010,2015,2020]); ax.set_ylim(0,24); style(ax); save(fig,'fig4_percapita.png')
S['wp']={2000:float(wp[2000]),2022:float(wp[2022])}
# FIG5 decoupling scatter
dd=pd.read_csv('/tmp/w3/final/decoupling.csv',index_col=0)
XL,YL=520,520
inside=dd[(dd.gdpg<=XL)&(dd.co2g<=YL)]; outside=len(dd)-len(inside)
fig,ax=plt.subplots(figsize=(6.8,4.4)); ax.scatter(inside.gdpg,inside.co2g,s=16,color=GRAY,alpha=0.85,edgecolor='white',linewidth=0.5,zorder=2)
for iso,c,lab,off,ha in [('IND',BLUE,'India',(-7,9),'right'),('CHN',ORG,'China',(8,6),'left'),('USA',AQUA,'United States',(8,-12),'left')]:
    r=dd.loc[iso]; ax.scatter(r.gdpg,r.co2g,s=64,color=c,edgecolor='white',linewidth=1.5,zorder=4); ax.annotate(lab,(r.gdpg,r.co2g),textcoords='offset points',xytext=off,fontsize=8.5,color=INK,ha=ha)
ax.plot([-100,YL],[-100,YL],color=INK2,lw=0.9,ls=(0,(4,3)),zorder=1); ax.axhline(0,color=INK2,lw=0.9,zorder=1)
ax.text(XL-8,-92,'Points below the solid line: absolute decoupling (GDP up, CO2 down)',ha='right',va='bottom',fontsize=8,color=INK2)
ax.set_xlabel('Change in real GDP, 2000-02 to 2020-22 (%)'); ax.set_ylabel('Change in CO2 emissions (%)'); ax.set_xlim(-60,XL); ax.set_ylim(-100,YL); style(ax,gridx=True)
ax.text(0.01,0.99,f'{outside} of {len(dd)} countries lie beyond the axes\n(very fast growth from a low base)',transform=ax.transAxes,va='top',fontsize=7.8,color=INK2); save(fig,'fig5_decoupling.png')
S['dec_outside']=int(outside); S['dec_n']=int(len(dd))
# FIG6 renewables dumbbell
r=d.pivot(index='iso3',columns='year',values='renewables_share_elec_pct'); a0=r[[2000,2001,2002]].mean(axis=1); a1=r[[2020,2021,2022]].mean(axis=1)
sel=['CHN','USA','IND','RUS','JPN','DEU','BRA','IDN','ZAF','GBR']; sel=sorted(sel,key=lambda i:a1[i])
fig,ax=plt.subplots(figsize=(6.8,3.9))
for i,iso in enumerate(sel):
    ax.plot([a0[iso],a1[iso]],[i,i],color=GRAY,lw=2.5,zorder=1)
    ax.scatter(a0[iso],i,s=46,color='#9ec5f4',edgecolor='white',linewidth=1.2,zorder=3); ax.scatter(a1[iso],i,s=46,color=BLUE if iso!='IND' else '#0d366b',edgecolor='white',linewidth=1.2,zorder=3)
    ax.text(max(a0[iso],a1[iso])+2.2,i,f'{a1[iso]:.0f}%',va='center',fontsize=8.5,color=INK)
ax.set_yticks(range(len(sel))); ax.set_yticklabels([nm[i] for i in sel]); ax.set_xlabel('Renewables share of electricity generation (%)'); ax.set_xlim(0,100); style(ax,gridx=True,gridy=False)
ax.legend(handles=[plt.Line2D([],[],marker='o',ls='',color='#9ec5f4',label='2000-02 average'),plt.Line2D([],[],marker='o',ls='',color=BLUE,label='2020-22 average')],frameon=False,loc='lower right',fontsize=8); save(fig,'fig6_renewables.png')
S['ren']={nm[i]:(float(a0[i]),float(a1[i])) for i in sel}
# FIG7 hist
pc=y22.co2_per_capita_t.dropna(); fig,ax=plt.subplots(figsize=(6.8,3.2)); bins=np.logspace(np.log10(0.05),np.log10(40),28)
ax.hist(pc,bins=bins,color=BLUE,edgecolor='white',linewidth=1); ax.set_xscale('log'); ax.set_xticks([0.1,0.3,1,3,10,30]); ax.set_xticklabels(['0.1','0.3','1','3','10','30'])
ax.set_xlabel('CO2 per person in 2022 (tonnes, log scale)'); ax.set_ylabel('Number of countries'); style(ax)
ax.axvline(pc.median(),color=INK,lw=1.4); ax.axvline(pc.mean(),color=ORG,lw=1.8); ax.axvline(y22.loc['IND','co2_per_capita_t'],color=AQUA,lw=1.8,ls=(0,(3,2)))
ax.legend(handles=[plt.Line2D([],[],color=INK,lw=1.4,label=f'Median {pc.median():.1f} t'),plt.Line2D([],[],color=ORG,lw=1.8,label=f'Mean {pc.mean():.1f} t'),plt.Line2D([],[],color=AQUA,lw=1.8,ls=(0,(3,2)),label=f'India {y22.loc["IND","co2_per_capita_t"]:.1f} t')],frameon=False,loc='upper left',fontsize=8.5)
save(fig,'fig7_hist.png')
# FIG8 heatmap
y=d[d.year==2022].copy(); cc=y[['gdp_per_capita_usd','co2_per_capita_t','energy_per_capita_kwh','renewables_share_elec_pct','co2_intensity_kg_per_usd']].dropna(); cc=cc[(cc>0).all(axis=1)]
cc2=cc.copy(); 
for c in ['gdp_per_capita_usd','co2_per_capita_t','energy_per_capita_kwh']: cc2[c]=np.log10(cc2[c])
cm_=cc2.corr(method='spearman'); n=len(cc2)
labs=['GDP per\ncapita','CO2 per\ncapita','Energy\nper capita','Renewable\nshare','CO2 per $\nof GDP']
cmap=LinearSegmentedColormap.from_list('div',[ '#e34948','#f0efec','#2a78d6'])
fig,ax=plt.subplots(figsize=(6.0,4.6)); im=ax.imshow(cm_.values,cmap=cmap,vmin=-1,vmax=1)
ax.set_xticks(range(5)); ax.set_xticklabels(labs,fontsize=8); ax.set_yticks(range(5)); ax.set_yticklabels(labs,fontsize=8); ax.tick_params(length=0)
for i in range(5):
    for j in range(5): ax.text(j,i,f'{cm_.values[i,j]:.2f}',ha='center',va='center',fontsize=9,color='white' if abs(cm_.values[i,j])>0.7 else INK)
for s in ax.spines.values(): s.set_visible(False)
cb=fig.colorbar(im,ax=ax,fraction=0.046,pad=0.03); cb.set_label('Spearman correlation',fontsize=8); cb.outline.set_visible(False); save(fig,'fig8_heat.png')
S['corr']=cm_.round(2).to_dict(); S['corr_n']=n
# FIG9 income quartile grouped
y['q']=pd.qcut(y.gdp_per_capita_usd,4,labels=['Lowest\nquarter','Second','Third','Highest\nquarter'])
q=y.groupby('q',observed=True).agg(co2=('co2_mt','sum'),pop=('population','sum'),n=('iso3','count'),pc=('co2_per_capita_t','median'),ren=('renewables_share_elec_pct','median'),gdppc=('gdp_per_capita_usd','median'))
q['co2s']=q.co2/q.co2.sum()*100; q['pops']=q['pop']/q['pop'].sum()*100
fig,ax=plt.subplots(figsize=(6.8,3.4)); x=np.arange(4); w=0.36
b1=ax.bar(x-w/2-0.01,q.pops,w,color=BLUE,label='Share of population',zorder=3); b2=ax.bar(x+w/2+0.01,q.co2s,w,color=ORG,label='Share of CO2 emissions',zorder=3)
for b in list(b1)+list(b2): ax.text(b.get_x()+b.get_width()/2,b.get_height()+0.8,f'{b.get_height():.0f}%',ha='center',fontsize=8.5,color=INK)
ax.set_xticks(x); ax.set_xticklabels(q.index); ax.set_xlabel('Countries grouped in four equal-sized income bands (GDP per person, 2022)'); ax.set_ylabel('Share of 192-country total (%)'); ax.set_ylim(0,58); style(ax); ax.legend(frameon=False,fontsize=8.5,loc='upper left'); save(fig,'fig9_income.png')
S['q']=q.reset_index().astype({'q':str}).to_dict('records')
# FIG10 yoy bars
yo=(tot.pct_change()*100).dropna(); fig,ax=plt.subplots(figsize=(6.8,3.0)); cols=[ORG if v<0 else GRAY for v in yo.values]
ax.bar(yo.index,yo.values,color=cols,width=0.7,zorder=3); ax.axhline(0,color=INK2,lw=0.9); ax.set_ylabel('Year-on-year change (%)'); style(ax)
for yr in (2009,2020,2021): ax.text(yr,yo[yr]+(0.3 if yo[yr]>0 else -0.35),f'{yo[yr]:+.1f}%',ha='center',va='bottom' if yo[yr]>0 else 'top',fontsize=8,color=INK)
ax.set_xticks(range(2001,2023,3)); ax.set_ylim(-5.5,7); save(fig,'fig10_yoy.png')
S['yoy']={int(k):float(v) for k,v in yo.items()}
# stats for text
S['cagr']={}
S['hist']={'median':float(pc.median()),'mean':float(pc.mean()),'n_gt8':int((pc>8).sum()),'n_lt2':int((pc<2).sum()),'n':int(len(pc)),'max':float(pc.max()),'max_c':str(y22.loc[pc.idxmax(),'country'])}
json.dump(S,open(O+'stats.json','w'),indent=1,default=str)
print(q.round(1).to_string()); print(cm_.round(2).to_string()); print(S['hist'], n)
