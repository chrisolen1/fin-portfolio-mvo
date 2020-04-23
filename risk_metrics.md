risk\_metrics
================

``` r
riskScripts <- "/Users/chrisolen/Documents/uchicago_courses/deep_learning_and_image_recognition/finance/fin-portfolio-mvo/risk_scripts"
source(paste(riskScripts,"RMfit.R",sep="/"))
source(paste(riskScripts,"RMeasure.R",sep="/"))
source(paste(riskScripts,"Hill.R",sep="/"))
source(paste(riskScripts,"SimGarcht.R",sep="/"))
library(fGarch)
```

    ## Loading required package: timeDate

    ## Loading required package: timeSeries

    ## Loading required package: fBasics

``` r
library(ellipse)
```

    ## 
    ## Attaching package: 'ellipse'

    ## The following object is masked from 'package:graphics':
    ## 
    ##     pairs

### Read in portfolio asset and macroeconomic data:

``` r
econ = c('CHNGDP','USGDP','EZGDP','US_UNEMP')

shock = c('CHNGDP_Shock','USGDP_Shock','EZGDP_Shock','US_UNEMP_Shock')

finstruments = c('UST_10YR','USFFR','USDRMB','CRUDOIL','CFE_VIX','USDEUR','UST_2YR',
             'SP500_GSCI','USDOIS','UIVE_SP500VALUEETF','USDJPY','USDGBP')

assets = c('VNQ_VANGREALEST','EMB_USDEMRGBOND','LQD_CORPBOND',
            'MUB_MUNIBOND','SHY_1-3USTR','VIG_VANGDIV','IVV_SP500','EEM_MSCIEMERGING',
            'XLE_ENERGYSPDR','EFA_MSCIEAFE','TIP_TIPSBOND')

dataPath = "/Users/chrisolen/Documents/uchicago_courses/deep_learning_and_image_recognition/finance/fin-portfolio-mvo/data"
dat = read.csv(paste(dataPath,"data_cleaned.csv",sep="/"), header=TRUE)
head(dat)
```

    ##        date UST_10YR UIVE_SP500VALUEETF VNQ_VANGREALEST USFFR
    ## 1  1/8/2008   3.8389              74.28         55.4900  4.27
    ## 2  1/9/2008   3.7899              72.72         56.4700  4.26
    ## 3 1/10/2008   3.8858              72.72         57.3400  4.26
    ## 4 1/11/2008   3.8065              73.57         57.3500  4.23
    ## 5 1/14/2008   3.7893              73.95         57.1101  4.24
    ## 6 1/15/2008   3.6995              73.10         55.9500  4.24
    ##   EMB_USDEMRGBOND LQD_CORPBOND MUB_MUNIBOND SHY_1.3USTR  USDJPY  USDGBP
    ## 1         102.197      106.270       101.85       82.66 0.91798 1.97279
    ## 2         102.120      106.050       102.11       82.62 0.90921 1.95768
    ## 3         102.210      105.738       101.96       82.62 0.91370 1.96169
    ## 4         101.838      106.510       102.09       82.85 0.91882 1.95715
    ## 5         102.190      106.070       102.55       82.88 0.92349 1.95273
    ## 6         102.360      106.640       103.11       82.95 0.93523 1.95762
    ##   VIG_VANGDIV IVV_SP500 USDRMB CRUDOIL CFE_VIX EEM_MSCIEMERGING   USDEUR
    ## 1       53.72    139.21 7.2657   96.34   24.10          48.2000 0.679833
    ## 2       54.18    141.05 7.2646   95.68   25.00          49.7800 0.682151
    ## 3       54.66    142.04 7.2724   93.72   24.42          50.3667 0.675288
    ## 4       53.90    140.32 7.2635   92.70   25.01          48.9500 0.676567
    ## 5       54.23    141.75 7.2525   94.21   24.99          49.6700 0.672744
    ## 6       53.26    138.24 7.2431   91.91   25.04          47.4233 0.676704
    ##   XLE_ENERGYSPDR SP500_GSCI EFA_MSCIEAFE TIP_TIPSBOND UST_2YR USDOIS
    ## 1          75.85    620.906        26.14       107.03  2.7607  4.059
    ## 2          76.85    616.887        26.48       106.95  2.6785  4.055
    ## 3          76.53    607.434        26.28       106.47  2.7103  3.994
    ## 4          75.60    605.848        25.71       107.26  2.5936  3.873
    ## 5          77.10    615.283        25.91       107.71  2.5764  3.859
    ## 6          73.91    604.946        25.08       108.26  2.5305  3.866
    ##    CHNGDP    USGDP EZGDP US_UNEMP CHNGDP_Shock USGDP_Shock EZGDP_Shock
    ## 1 85399.6 15671.38  2616        5            0           0           0
    ## 2 85399.6 15671.38  2616        5            0           0           0
    ## 3 85399.6 15671.38  2616        5            0           0           0
    ## 4 85399.6 15671.38  2616        5            0           0           0
    ## 5 85399.6 15671.38  2616        5            0           0           0
    ## 6 85399.6 15671.38  2616        5            0           0           0
    ##   US_UNEMP_Shock   VNQ_VOL   EMB_VOL   LQD_VOL   MUB_VOL   VIG_VOL
    ## 1              0 2.2447160 0.2735705 0.3422718 0.1632483 0.5882431
    ## 2              0 1.4362277 0.2342430 0.3458034 0.1242176 0.5063793
    ## 3              0 0.8041952 0.2064263 0.3429531 0.1096814 0.3640330
    ## 4              0 0.8482511 0.1629478 0.3199825 0.1052141 0.3943602
    ## 5              0 0.7911624 0.1565631 0.2861971 0.2664958 0.3584969
    ## 6              5 0.6148116 0.1919239 0.3682836 0.4727367 0.5167011
    ##    IVV_VOL   EEM_VOL   EFA_VOL   XLE_VOL    SHY_VOL    TIP_VOL
    ## 1 2.430027 0.6720562 0.3750067 1.8485183 0.12223339 0.15833509
    ## 2 1.997616 0.7895796 0.3016952 1.7215894 0.07368853 0.03464102
    ## 3 1.117511 0.9867245 0.1288410 0.6377539 0.04449719 0.22821043
    ## 4 1.159634 0.8867787 0.2902068 0.6711408 0.11584472 0.28778464
    ## 5 1.143866 0.8357762 0.3027045 0.6424407 0.12837445 0.45296799
    ## 6 1.517778 1.1325228 0.5452247 1.2982180 0.15404545 0.68887590

### Extract just the portfolio assets, risk free rate, and market indicator:

``` r
cols.use <- names(dat)[names(dat) %in% assets]
risk.free.rate <- "USFFR"
market.indicator <- "UIVE_SP500VALUEETF"
var.explained = 0.8
nDay.forecastHorizon <- 10
full.history <- dat[,c("date",risk.free.rate,market.indicator,cols.use)]
full.history[,"date"] = as.Date(full.history[,"date"], format = "%m/%d/%Y")
head(full.history)
```

    ##         date USFFR UIVE_SP500VALUEETF VNQ_VANGREALEST EMB_USDEMRGBOND
    ## 1 2008-01-08  4.27              74.28         55.4900         102.197
    ## 2 2008-01-09  4.26              72.72         56.4700         102.120
    ## 3 2008-01-10  4.26              72.72         57.3400         102.210
    ## 4 2008-01-11  4.23              73.57         57.3500         101.838
    ## 5 2008-01-14  4.24              73.95         57.1101         102.190
    ## 6 2008-01-15  4.24              73.10         55.9500         102.360
    ##   LQD_CORPBOND MUB_MUNIBOND VIG_VANGDIV IVV_SP500 EEM_MSCIEMERGING
    ## 1      106.270       101.85       53.72    139.21          48.2000
    ## 2      106.050       102.11       54.18    141.05          49.7800
    ## 3      105.738       101.96       54.66    142.04          50.3667
    ## 4      106.510       102.09       53.90    140.32          48.9500
    ## 5      106.070       102.55       54.23    141.75          49.6700
    ## 6      106.640       103.11       53.26    138.24          47.4233
    ##   XLE_ENERGYSPDR EFA_MSCIEAFE TIP_TIPSBOND
    ## 1          75.85        26.14       107.03
    ## 2          76.85        26.48       106.95
    ## 3          76.53        26.28       106.47
    ## 4          75.60        25.71       107.26
    ## 5          77.10        25.91       107.71
    ## 6          73.91        25.08       108.26

``` r
cat("portfolio dimensions:", dim(full.history))
```

    ## portfolio dimensions: 2959 13

### Determine Year(s) of Analysis

``` r
year <- c(2016,2017)
portfolio <- subset(full.history, format(as.Date(date),"%Y")==year)
```

    ## Warning in format(as.Date(date), "%Y") == year: longer object length is not
    ## a multiple of shorter object length

``` r
head(portfolio)
```

    ##            date USFFR UIVE_SP500VALUEETF VNQ_VANGREALEST EMB_USDEMRGBOND
    ## 2013 2016-01-05  0.36              87.68           80.29          105.95
    ## 2015 2016-01-07  0.36              84.98           78.51          105.44
    ## 2017 2016-01-11  0.36              83.79           77.90          105.17
    ## 2019 2016-01-13  0.36              84.21           76.27          104.27
    ## 2021 2016-01-15  0.36              81.12           75.57          103.36
    ## 2023 2016-01-20  0.37              80.02           73.93          103.11
    ##      LQD_CORPBOND MUB_MUNIBOND VIG_VANGDIV IVV_SP500 EEM_MSCIEMERGING
    ## 2013       114.01       110.60       76.97    202.42           31.380
    ## 2015       114.55       111.25       74.64    194.99           29.830
    ## 2017       114.27       111.12       74.03    193.03           29.500
    ## 2019       114.88       111.21       73.25    189.79           29.250
    ## 2021       114.14       111.35       72.62    188.74           28.455
    ## 2023       113.80       111.51       72.10    186.65           28.250
    ##      XLE_ENERGYSPDR EFA_MSCIEAFE TIP_TIPSBOND
    ## 2013          60.53        22.43       110.04
    ## 2015          56.78        21.42       110.30
    ## 2017          54.85        21.34       109.81
    ## 2019          53.66        21.10       110.34
    ## 2021          54.35        20.59       110.24
    ## 2023          51.77        20.34       110.19

### Convert to log returns:

``` r
portfolio.returns <- apply(log(portfolio[,-(1:3)]),2,diff)
head(portfolio.returns)
```

    ##      VNQ_VANGREALEST EMB_USDEMRGBOND LQD_CORPBOND  MUB_MUNIBOND
    ## 2015    -0.022419075    -0.004825214  0.004725245  0.0058598320
    ## 2017    -0.007800052    -0.002563982 -0.002447340 -0.0011692226
    ## 2019    -0.021146277    -0.008594400  0.005324036  0.0008096074
    ## 2021    -0.009220297    -0.008765649 -0.006462340  0.0012580879
    ## 2023    -0.021940679    -0.002421661 -0.002983243  0.0014358793
    ## 2025     0.032994878     0.013869046 -0.002287324 -0.0018850147
    ##       VIG_VANGDIV    IVV_SP500 EEM_MSCIEMERGING XLE_ENERGYSPDR
    ## 2015 -0.030739179 -0.037396472     -0.050656149    -0.06395496
    ## 2017 -0.008206140 -0.010102658     -0.011124335    -0.03458196
    ## 2019 -0.010592169 -0.016927419     -0.008510690    -0.02193434
    ## 2021 -0.008637882 -0.005547791     -0.027555682     0.01277677
    ## 2023 -0.007186322 -0.011135201     -0.007230434    -0.04863378
    ## 2025  0.020862684  0.025600383      0.037517425     0.07388719
    ##      EFA_MSCIEAFE  TIP_TIPSBOND
    ## 2015 -0.046074284  0.0023599902
    ## 2017 -0.003741819 -0.0044523266
    ## 2019 -0.011310205  0.0048149082
    ## 2021 -0.024467519 -0.0009067006
    ## 2023 -0.012216130 -0.0004536588
    ## 2025  0.045178274 -0.0021804315

### Risk Metrics

RiskMetrics assumes that the continuously compounded daily rate of
return \(r_t\) (and therefore the loss variable \(x_t\)) of a portfolio
follows a conditional normal distribution. Such that:
\[x_t|F_{t-1}~N(0,σ_t^2)\] …where \(σ_t^2\) is the conditional variance
of \(x_t\) and it evolves over time according to GARCH(1,1):
\[x_t=µ+σ_t^2 ε_t\] \[σ_t^2=∝σ_{t-1}^2+(1-∝)x_{t-1}^2,1>∝>0\]

Under the GARCH(1,1) model, the conditional variance is proportional to
the time horizon k, such that: \[σ_t^2 [k]=kσ_{t+1}^2\]

VaR given time horizon k and normally distributed loss variable \(z\):
\[VaR_{1-p}=Value of Position×z_{1-p}×√k×σ_{t+1} \]

### Calculate risk metrics via Garch and then RMeasure:

``` r
# fit garch (1,1) with Gaussian innovations to loss variables (xt = -rt)
xt <- -portfolio.returns
gaussianRM.oneDay.95p <- matrix(data=NA,nrow=dim(xt)[2],ncol=2)

for (i in 1:dim(xt)[2]){
  gm <- garchFit(~garch(1,1),data=xt[,i],trace=F) 
  # extract one-day mean and sd from garch
  oneday.mean <- predict(gm,1)[1,1]
  oneday.sd <- predict(gm,1)[1,3]
  rm <- RMeasure(oneday.mean, oneday.sd)
  gaussianRM.oneDay.95p[i,1:2] <- rm$results[1,2:3]
}
```

    ## 
    ##  Risk Measures for selected probabilities: 
    ##       prob        VaR         ES
    ## [1,] 0.950 0.01928979 0.02415199
    ## [2,] 0.990 0.02721965 0.03116269
    ## [3,] 0.999 0.03610819 0.03932970
    ## 
    ##  Risk Measures for selected probabilities: 
    ##       prob         VaR          ES
    ## [1,] 0.950 0.005771062 0.007312303
    ## [2,] 0.990 0.008284700 0.009534582
    ## [3,] 0.999 0.011102228 0.012123397
    ## 
    ##  Risk Measures for selected probabilities: 
    ##       prob         VaR          ES
    ## [1,] 0.950 0.006144043 0.007779392
    ## [2,] 0.990 0.008811163 0.010137363
    ## [3,] 0.999 0.011800729 0.012884249
    ## 
    ##  Risk Measures for selected probabilities: 
    ##       prob         VaR          ES
    ## [1,] 0.950 0.005470459 0.006872980
    ## [2,] 0.990 0.007757856 0.008895242
    ## [3,] 0.999 0.010321791 0.011251048
    ## 
    ##  Risk Measures for selected probabilities: 
    ##       prob        VaR         ES
    ## [1,] 0.950 0.01102661 0.01405371
    ## [2,] 0.990 0.01596356 0.01841841
    ## [3,] 0.999 0.02149737 0.02350301
    ## 
    ##  Risk Measures for selected probabilities: 
    ##       prob        VaR         ES
    ## [1,] 0.950 0.01038318 0.01318099
    ## [2,] 0.990 0.01494619 0.01721510
    ## [3,] 0.999 0.02006085 0.02191458
    ## 
    ##  Risk Measures for selected probabilities: 
    ##       prob        VaR         ES
    ## [1,] 0.950 0.02092967 0.02656343
    ## [2,] 0.990 0.03011787 0.03468662
    ## [3,] 0.999 0.04041690 0.04414961
    ## 
    ##  Risk Measures for selected probabilities: 
    ##       prob        VaR         ES
    ## [1,] 0.950 0.01762274 0.02223599
    ## [2,] 0.990 0.02514657 0.02888772
    ## [3,] 0.999 0.03358001 0.03663657
    ## 
    ##  Risk Measures for selected probabilities: 
    ##       prob        VaR         ES
    ## [1,] 0.950 0.01434683 0.01823896
    ## [2,] 0.990 0.02069458 0.02385095
    ## [3,] 0.999 0.02780977 0.03038855
    ## 
    ##  Risk Measures for selected probabilities: 
    ##       prob         VaR          ES
    ## [1,] 0.950 0.004877305 0.006139507
    ## [2,] 0.990 0.006935853 0.007959446
    ## [3,] 0.999 0.009243273 0.010079560

``` r
colnames(gaussianRM.oneDay.95p) <- c("VaR","ES")
rownames(gaussianRM.oneDay.95p) <- colnames(portfolio.returns)
gaussianRM.oneDay.95p
```

    ##                          VaR          ES
    ## VNQ_VANGREALEST  0.019289792 0.024151993
    ## EMB_USDEMRGBOND  0.005771062 0.007312303
    ## LQD_CORPBOND     0.006144043 0.007779392
    ## MUB_MUNIBOND     0.005470459 0.006872980
    ## VIG_VANGDIV      0.011026606 0.014053705
    ## IVV_SP500        0.010383179 0.013180995
    ## EEM_MSCIEMERGING 0.020929668 0.026563428
    ## XLE_ENERGYSPDR   0.017622737 0.022235986
    ## EFA_MSCIEAFE     0.014346826 0.018238963
    ## TIP_TIPSBOND     0.004877305 0.006139507

``` r
# fit garch (1,1) with Student-t innovations to loss variables (xt = -rt)
xt <- -portfolio.returns
stdRM.oneDay.95p <- matrix(data=NA,nrow=dim(xt)[2],ncol=2)

for (i in 1:dim(xt)[2]){
  gm <- garchFit(~garch(1,1),data=xt[,i],trace=F, cond.dist="std")
  # extract one-day mean and sd from garch
  oneday.mean <- predict(gm,1)[1,1]
  oneday.sd <- predict(gm,1)[1,3]
  # extract dof
  dof <- gm@fit$matcoef[5,1]
  rm <- RMeasure(oneday.mean,oneday.sd,cond.dist="std",df=dof)
  stdRM.oneDay.95p[i,1:2] <- rm$results[1,2:3]
}
```

    ## 
    ##  Risk Measures for selected probabilities: 
    ##       prob        VaR         ES
    ## [1,] 0.950 0.01829354 0.02514817
    ## [2,] 0.990 0.02912088 0.03655948
    ## [3,] 0.999 0.04632864 0.05555660
    ## 
    ##  Risk Measures for selected probabilities: 
    ##       prob         VaR         ES
    ## [1,] 0.950 0.005883172 0.00886219
    ## [2,] 0.990 0.010436839 0.01430353
    ## [3,] 0.999 0.019431082 0.02553716
    ## 
    ##  Risk Measures for selected probabilities: 
    ##       prob         VaR          ES
    ## [1,] 0.950 0.006246502 0.008649417
    ## [2,] 0.990 0.010042481 0.012648226
    ## [3,] 0.999 0.016070124 0.019299467
    ## 
    ##  Risk Measures for selected probabilities: 
    ##       prob         VaR          ES
    ## [1,] 0.950 0.005102979 0.007571002
    ## [2,] 0.990 0.008853961 0.012140221
    ## [3,] 0.999 0.016497727 0.021865216
    ## 
    ##  Risk Measures for selected probabilities: 
    ##       prob         VaR         ES
    ## [1,] 0.950 0.009651058 0.01502393
    ## [2,] 0.990 0.017764243 0.02511634
    ## [3,] 0.999 0.034859691 0.04730726
    ## 
    ##  Risk Measures for selected probabilities: 
    ##       prob         VaR         ES
    ## [1,] 0.950 0.009371828 0.01508296
    ## [2,] 0.990 0.017872252 0.02613697
    ## [3,] 0.999 0.037059584 0.05211729
    ## 
    ##  Risk Measures for selected probabilities: 
    ##       prob        VaR         ES
    ## [1,] 0.950 0.01959802 0.02765189
    ## [2,] 0.990 0.03227254 0.04122437
    ## [3,] 0.999 0.05300713 0.06448349
    ## 
    ##  Risk Measures for selected probabilities: 
    ##       prob        VaR         ES
    ## [1,] 0.950 0.01791390 0.02433936
    ## [2,] 0.990 0.02810046 0.03490227
    ## [3,] 0.999 0.04381205 0.05196534
    ## 
    ##  Risk Measures for selected probabilities: 
    ##       prob        VaR         ES
    ## [1,] 0.950 0.01460483 0.02291179
    ## [2,] 0.990 0.02702941 0.03883321
    ## [3,] 0.999 0.05445105 0.07544904

    ## Warning in sqrt(diag(fit$cvar)): NaNs produced

    ## 
    ##  Risk Measures for selected probabilities: 
    ##       prob         VaR          ES
    ## [1,] 0.950 0.005951319 0.008126699
    ## [2,] 0.990 0.009399362 0.011705332
    ## [3,] 0.999 0.014726405 0.017495840

``` r
colnames(stdRM.oneDay.95p) <- c("VaR","ES")
rownames(stdRM.oneDay.95p) <- colnames(portfolio.returns)
stdRM.oneDay.95p
```

    ##                          VaR          ES
    ## VNQ_VANGREALEST  0.018293540 0.025148168
    ## EMB_USDEMRGBOND  0.005883172 0.008862190
    ## LQD_CORPBOND     0.006246502 0.008649417
    ## MUB_MUNIBOND     0.005102979 0.007571002
    ## VIG_VANGDIV      0.009651058 0.015023926
    ## IVV_SP500        0.009371828 0.015082963
    ## EEM_MSCIEMERGING 0.019598024 0.027651891
    ## XLE_ENERGYSPDR   0.017913896 0.024339359
    ## EFA_MSCIEAFE     0.014604834 0.022911787
    ## TIP_TIPSBOND     0.005951319 0.008126699

### Compare the two one-day risk metrics

``` r
# Gaussian Garch
gaussianRM.oneDay.95p
```

    ##                          VaR          ES
    ## VNQ_VANGREALEST  0.019289792 0.024151993
    ## EMB_USDEMRGBOND  0.005771062 0.007312303
    ## LQD_CORPBOND     0.006144043 0.007779392
    ## MUB_MUNIBOND     0.005470459 0.006872980
    ## VIG_VANGDIV      0.011026606 0.014053705
    ## IVV_SP500        0.010383179 0.013180995
    ## EEM_MSCIEMERGING 0.020929668 0.026563428
    ## XLE_ENERGYSPDR   0.017622737 0.022235986
    ## EFA_MSCIEAFE     0.014346826 0.018238963
    ## TIP_TIPSBOND     0.004877305 0.006139507

``` r
# Student-t Garch
stdRM.oneDay.95p
```

    ##                          VaR          ES
    ## VNQ_VANGREALEST  0.018293540 0.025148168
    ## EMB_USDEMRGBOND  0.005883172 0.008862190
    ## LQD_CORPBOND     0.006246502 0.008649417
    ## MUB_MUNIBOND     0.005102979 0.007571002
    ## VIG_VANGDIV      0.009651058 0.015023926
    ## IVV_SP500        0.009371828 0.015082963
    ## EEM_MSCIEMERGING 0.019598024 0.027651891
    ## XLE_ENERGYSPDR   0.017913896 0.024339359
    ## EFA_MSCIEAFE     0.014604834 0.022911787
    ## TIP_TIPSBOND     0.005951319 0.008126699

### Calculate multi-day risk metrics for garch with Gaussian innovations

``` r
# fit garch (1,1) with Gaussian innovations to loss variables (xt = -rt)
xt <- -portfolio.returns
gaussianRM.multiDay.95p <- matrix(data=NA,nrow=dim(xt)[2],ncol=2)

for (i in 1:dim(xt)[2]){
  gm <- garchFit(~garch(1,1),data=xt[,i],trace=F)
  # recalling that under the GARCH(1,1) model, the conditional variance is proportional to the time horizon k
  multi.day.predictions <- predict(gm,nDay.forecastHorizon)
  mf <- multi.day.predictions$meanForecast 
  merr <- multi.day.predictions$meanError 
  pmean <- sum(mf) 
  pvar <- sum(merr^2) 
  pstd <- sqrt(pvar) 
  rm <- RMeasure(pmean,pstd)
  
  gaussianRM.multiDay.95p[i,1:2] <- rm$results[1,2:3]
}
```

    ## 
    ##  Risk Measures for selected probabilities: 
    ##       prob        VaR         ES
    ## [1,] 0.950 0.06258946 0.07810788
    ## [2,] 0.990 0.08789873 0.10048352
    ## [3,] 0.999 0.11626780 0.12654971
    ## 
    ##  Risk Measures for selected probabilities: 
    ##       prob        VaR         ES
    ## [1,] 0.950 0.02933440 0.03753810
    ## [2,] 0.990 0.04271397 0.04936683
    ## [3,] 0.999 0.05771108 0.06314655
    ## 
    ##  Risk Measures for selected probabilities: 
    ##       prob        VaR         ES
    ## [1,] 0.950 0.01755371 0.02275820
    ## [2,] 0.990 0.02604181 0.03026243
    ## [3,] 0.999 0.03555609 0.03900439
    ## 
    ##  Risk Measures for selected probabilities: 
    ##       prob        VaR         ES
    ## [1,] 0.950 0.01550972 0.01957786
    ## [2,] 0.990 0.02214451 0.02544360
    ## [3,] 0.999 0.02958142 0.03227681
    ## 
    ##  Risk Measures for selected probabilities: 
    ##       prob        VaR         ES
    ## [1,] 0.950 0.03149182 0.04175098
    ## [2,] 0.990 0.04822368 0.05654343
    ## [3,] 0.999 0.06697835 0.07377568
    ## 
    ##  Risk Measures for selected probabilities: 
    ##       prob        VaR         ES
    ## [1,] 0.950 0.03910711 0.05064258
    ## [2,] 0.990 0.05792052 0.06727531
    ## [3,] 0.999 0.07900841 0.08665138
    ## 
    ##  Risk Measures for selected probabilities: 
    ##       prob        VaR         ES
    ## [1,] 0.950 0.06613273 0.08610091
    ## [2,] 0.990 0.09869921 0.11489257
    ## [3,] 0.999 0.13520285 0.14843302
    ## 
    ##  Risk Measures for selected probabilities: 
    ##       prob        VaR         ES
    ## [1,] 0.950 0.05197103 0.06653739
    ## [2,] 0.990 0.07572758 0.08754029
    ## [3,] 0.999 0.10235621 0.11200733
    ## 
    ##  Risk Measures for selected probabilities: 
    ##       prob        VaR         ES
    ## [1,] 0.950 0.04066338 0.05346818
    ## [2,] 0.990 0.06154696 0.07193111
    ## [3,] 0.999 0.08495528 0.09343925
    ## 
    ##  Risk Measures for selected probabilities: 
    ##       prob        VaR         ES
    ## [1,] 0.950 0.01471508 0.01868500
    ## [2,] 0.990 0.02118969 0.02440913
    ## [3,] 0.999 0.02844707 0.03107738

``` r
colnames(gaussianRM.multiDay.95p) <- c("VaR","ES")
rownames(gaussianRM.multiDay.95p) <- colnames(portfolio.returns)
gaussianRM.multiDay.95p
```

    ##                         VaR         ES
    ## VNQ_VANGREALEST  0.06258946 0.07810788
    ## EMB_USDEMRGBOND  0.02933440 0.03753810
    ## LQD_CORPBOND     0.01755371 0.02275820
    ## MUB_MUNIBOND     0.01550972 0.01957786
    ## VIG_VANGDIV      0.03149182 0.04175098
    ## IVV_SP500        0.03910711 0.05064258
    ## EEM_MSCIEMERGING 0.06613273 0.08610091
    ## XLE_ENERGYSPDR   0.05197103 0.06653739
    ## EFA_MSCIEAFE     0.04066338 0.05346818
    ## TIP_TIPSBOND     0.01471508 0.01868500

### Calculate multi-day risk metrics for garch with Student-t innovations

``` r
# We note that the sum of k standardized Student-t distributed random variables is not going to also be distributed as the same standardized Student - unlike in the case of Gaussian innovations. Thus, we need to compute multi-period risk metrics via simulating the garch model:

# fit garch (1,1) with Student-t innovations to loss variables (xt = -rt)
xt <- -portfolio.returns
stdRM.multiDay.95p <- matrix(data=NA,nrow=dim(xt)[2],ncol=2)

for (i in 1:dim(xt)[2]){
  gm <- garchFit(~garch(1,1),data=xt[,i],trace=F, cond.dist="std")
  vol <- volatility(gm)
  alpha1 <- gm@fit$matcoef[3,1]
  omega <- gm@fit$matcoef[2,1]
  alpha1 <- c(omega, alpha1)
  mu <- gm@fit$matcoef[1,1]
  beta1 <- gm@fit$matcoef[4,1]
  dof <- gm@fit$matcoef[5,1]

  # determine the origin of the simulation from the last instance
  orig <- c(xt[length(xt[,i])], vol[length(xt[,i])])
  set.seed(8473625)
  sim <- SimGarcht(h=nDay.forecastHorizon,mu=mu,alpha=alpha1,b1=beta1,df=dof,ini=orig,nter=30000) 
  rr <- sim$rtn

  #VaR
  VaR <- quantile(rr,0.95)
  stdRM.multiDay.95p[i,1] <- VaR
  # ES for p = 0.05 
  idx.p05 <- c(1:30000)[rr > VaR] 
  ES <- mean(rr[idx.p05])
  stdRM.multiDay.95p[i,2] <- ES
  
}
```

    ## Warning in sqrt(diag(fit$cvar)): NaNs produced

``` r
colnames(stdRM.multiDay.95p) <- c("VaR","ES")
rownames(stdRM.multiDay.95p) <- colnames(portfolio.returns)
stdRM.multiDay.95p
```

    ##                         VaR         ES
    ## VNQ_VANGREALEST  0.05477995 0.07434438
    ## EMB_USDEMRGBOND  0.01927750 0.02925309
    ## LQD_CORPBOND     0.01815259 0.02509709
    ## MUB_MUNIBOND     0.01653865 0.02394235
    ## VIG_VANGDIV      0.02747877 0.04341133
    ## IVV_SP500        0.02723590 0.04718163
    ## EEM_MSCIEMERGING 0.05341418 0.08334670
    ## XLE_ENERGYSPDR   0.05583736 0.07293688
    ## EFA_MSCIEAFE     0.03698044 0.06051206
    ## TIP_TIPSBOND     0.01777548 0.02304354

### Compare two multi-day risk metrics

``` r
# Gaussian Garch
gaussianRM.multiDay.95p
```

    ##                         VaR         ES
    ## VNQ_VANGREALEST  0.06258946 0.07810788
    ## EMB_USDEMRGBOND  0.02933440 0.03753810
    ## LQD_CORPBOND     0.01755371 0.02275820
    ## MUB_MUNIBOND     0.01550972 0.01957786
    ## VIG_VANGDIV      0.03149182 0.04175098
    ## IVV_SP500        0.03910711 0.05064258
    ## EEM_MSCIEMERGING 0.06613273 0.08610091
    ## XLE_ENERGYSPDR   0.05197103 0.06653739
    ## EFA_MSCIEAFE     0.04066338 0.05346818
    ## TIP_TIPSBOND     0.01471508 0.01868500

``` r
# Student-t Garch
stdRM.multiDay.95p
```

    ##                         VaR         ES
    ## VNQ_VANGREALEST  0.05477995 0.07434438
    ## EMB_USDEMRGBOND  0.01927750 0.02925309
    ## LQD_CORPBOND     0.01815259 0.02509709
    ## MUB_MUNIBOND     0.01653865 0.02394235
    ## VIG_VANGDIV      0.02747877 0.04341133
    ## IVV_SP500        0.02723590 0.04718163
    ## EEM_MSCIEMERGING 0.05341418 0.08334670
    ## XLE_ENERGYSPDR   0.05583736 0.07293688
    ## EFA_MSCIEAFE     0.03698044 0.06051206
    ## TIP_TIPSBOND     0.01777548 0.02304354
