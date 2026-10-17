import pandas as pd, numpy as np, json
d=pd.read_csv('/tmp/w2/out/esg_clean_panel_2000_2022.csv')
raw=pd.read_csv('/tmp/w2/raw/owid-co2-data.csv',usecols=['iso_code','year','gdp'])
raw=raw.rename(columns={'iso_code':'iso3','gdp':'gdp_const'})
d=d.merge(raw,on=['iso3','year'],how='left')
print(d.shape, d.country.nunique())
print('gdp_const coverage 2000/2022:', d[d.year==2000].gdp_const.notna().sum(), d[d.year==2022].gdp_const.notna().sum())
R={}
tot=d.groupby('year').co2_mt.sum()
R['tot2000']=tot[2000]; R['tot2019']=tot[2019]; R['tot2020']=tot[2020]; R['tot2021']=tot[2021]; R['tot2022']=tot[2022]
yoy=tot.pct_change()*100
print(yoy.round(2).to_dict())
print('total',tot.round(0).to_dict())
y=d[d.year==2022].copy()
top=y.sort_values('co2_mt',ascending=False)[['country','co2_mt','co2_per_capita_t','population']].head(12); top['share']=top.co2_mt/y.co2_mt.sum()*100
print(top.round(2)); print('top5 share',top.share.head(5).sum(),'top10',top.share.head(10).sum())
print('median pc',y.co2_per_capita_t.median(),'mean',y.co2_per_capita_t.mean(),'pop-weighted', (y.co2_mt.sum()*1e6/y.population.sum()))
# countries decline 2020
p=d.pivot(index='iso3',columns='year',values='co2_mt')
print('countries with 2020 decline',(p[2020]<p[2019]).sum(),'of',p[2020].notna().sum(),' 2021 rise',(p[2021]>p[2020]).sum(), ' 2022 vs 2019 below', (p[2022]<p[2019]).sum())
# decoupling
g=d.pivot(index='iso3',columns='year',values='gdp_const')
def avg(df,yrs): return df[yrs].mean(axis=1)
co2g=(avg(p,[2020,2021,2022])/avg(p,[2000,2001,2002])-1)*100
gdpg=(avg(g,[2020,2021,2022])/avg(g,[2000,2001,2002])-1)*100
dd=pd.DataFrame({'co2g':co2g,'gdpg':gdpg}).dropna(); dd=dd[p.loc[dd.index,2022]>1]
nm=d.drop_duplicates('iso3').set_index('iso3').country
dd['country']=nm; dd['co2_2022']=p[2022]
print(len(dd)); 
abs_=(dd.gdpg>0)&(dd.co2g<0); rel=(dd.gdpg>0)&(dd.co2g>=0)&(dd.co2g<dd.gdpg)
cpl=(dd.gdpg>0)&(dd.co2g>=dd.gdpg)
print('absolute',abs_.sum(),'relative',rel.sum(),'coupled/worse',cpl.sum(),'gdp decline',(dd.gdpg<=0).sum())
print('share of 2022 emissions in absolute decouplers', dd[abs_].co2_2022.sum()/dd.co2_2022.sum()*100)
print(dd[abs_].sort_values('co2_2022',ascending=False).head(10)[['country','co2g','gdpg','co2_2022']].round(1))
print(dd.loc[['IND','CHN','USA','DEU','BRA','IDN','ZAF','GBR','JPN']][['country','co2g','gdpg']].round(1) if all(i in dd.index for i in ['IND','CHN','USA','DEU','BRA','IDN','ZAF','GBR','JPN']) else dd.loc[[i for i in ['IND','CHN','USA','DEU','BRA','IDN','ZAF','GBR','JPN'] if i in dd.index]][['country','co2g','gdpg']].round(1))
dd.to_csv('out/decoupling.csv')
# India vs peers
for iso in ['IND','CHN','USA','DEU']:
    s=d[d.iso3==iso].set_index('year')
    print(iso, 'pc2000',s.co2_per_capita_t[2000],'pc2022',s.co2_per_capita_t[2022],'renew',s.renewables_share_elec_pct[2000],s.renewables_share_elec_pct[2022],'int',s.co2_intensity_kg_per_usd[2000],s.co2_intensity_kg_per_usd[2022], 'co2',s.co2_mt[2000],s.co2_mt[2022])
w=d.groupby('year').apply(lambda x: x.co2_mt.sum()*1e6/x.population.sum()); print('world pc',w[2000],w[2022])
# renewables change
r=d.pivot(index='iso3',columns='year',values='renewables_share_elec_pct')
dr=(avg(r,[2020,2021,2022])-avg(r,[2000,2001,2002])).dropna()
t=pd.DataFrame({'chg':dr,'r2022':r[2022],'co2':p[2022]}); t['country']=nm; t=t[t.co2>5]
print(t.sort_values('chg',ascending=False).head(8).round(1)); print(t.sort_values('chg').head(6).round(1))
print('median renew 2022',r[2022].median(),'2000',r[2000].median(), 'count up',(dr>0).sum(),'of',len(dr))
print(t.loc[['IND']] if 'IND' in t.index else '')
# income quartiles
y['q']=pd.qcut(y.gdp_per_capita_usd,4,labels=['Q1 lowest','Q2','Q3','Q4 highest'])
q=y.groupby('q',observed=True).agg(n=('iso3','count'),gdppc=('gdp_per_capita_usd','median'),co2pc=('co2_per_capita_t','median'),renew=('renewables_share_elec_pct','median'),epc=('energy_per_capita_kwh','median'),co2=('co2_mt','sum'),pop=('population','sum'))
q['co2_share']=q.co2/q.co2.sum()*100; q['pop_share']=q['pop']/q['pop'].sum()*100
print(q.round(1))
# correlations
c=y[['gdp_per_capita_usd','co2_per_capita_t','energy_per_capita_kwh','renewables_share_elec_pct','co2_intensity_kg_per_usd']].copy()
c['gdp_per_capita_usd']=np.log10(c.gdp_per_capita_usd); c['co2_per_capita_t']=np.log10(c.co2_per_capita_t); c['energy_per_capita_kwh']=np.log10(c.energy_per_capita_kwh)
print(c.corr(method='spearman').round(2))
print('n',c.dropna().shape[0])
# anomalies yoy
d=d.sort_values(['iso3','year']); 
print('flagged jumps',d.flag_co2_jump.sum())
# mean vs median skew
print(y.co2_per_capita_t.describe().round(2))
print('countries above 8t',(y.co2_per_capita_t>8).sum(),' below 2t',(y.co2_per_capita_t<2).sum(),' n',y.co2_per_capita_t.notna().sum())
# 2000-2022 pop-weighted etc. cumulative
print('India share of total 2000',p.loc['IND',2000]/tot[2000]*100,' 2022',p.loc['IND',2022]/tot[2022]*100, 'China 2000',p.loc['CHN',2000]/tot[2000]*100,'2022',p.loc['CHN',2022]/tot[2022]*100)
print('share of increase 2000-2022 from India+China',((p.loc['IND',2022]-p.loc['IND',2000])+(p.loc['CHN',2022]-p.loc['CHN',2000]))/(tot[2022]-tot[2000])*100)
