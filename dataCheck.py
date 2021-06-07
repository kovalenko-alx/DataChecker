from scipy.stats import ks_2samp
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
from os import listdir
from os.path import isfile, join
import decimal
from kneed import KneeLocator, DataGenerator


def singleDistributionTest(path_in='./data',
                           path_out='./outputs',
                           adjusted_pvalue=False,
                           plot_all=False,
                           plot_legend = False,
                           num_fractions = 10,
                           min_fraction = 0.1
                          ):
    
    """
    Parameters:
    ----------
    path_in : str
        folder path with input data in .csv format, './data', by default
    path_out : str
        folder path with output data images, './otputs' by default 
    adjusted_pvalue : bool
        size adjusted p-value, False by default
    plot_all : bool
        plot all graphs, if False plot mean value only
    num_fractions : integer
        number of interations to create subsets, 10 by default
    min_fraction : float
        minimal size of subset, 0.1 by default
    """
    
    fractions= np.linspace(1.0, min_fraction, num=num_fractions)
    
    mypath = path_in
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    
    datafiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) if f.endswith('.csv')]
    
    print(datafiles)
    
    dfs = []

    for f in datafiles:

        df = pd.read_csv(mypath + '/' + f)
        df = df.dropna()
        df = df.select_dtypes(include=numerics)

        dfs.append(df)

    for idx, df in enumerate(dfs):
        
        p_adjust = 1/(np.sqrt(((len(df) + len(df))/(len(df) * len(df)))))
        
        if len(df) < 5000:
            alpha = 0.05/(np.sqrt(((len(df) + len(df))/(len(df) * len(df)))))
        else:
            alpha = 1.037
            
        stats_fractions = []
        pvals_fractions = []
        ks_vals = []
        pvals_adjusted_fractions = []

        for f in fractions:
            df_frac = df.sample(frac=f)    

            stats = []
            pvals = []
            for c in df.columns:
                kst = ks_2samp(df[c].values, df_frac[c].values, mode='asymp')
                stats.append(kst[0])
                pvals.append(1 - kst[1])
            
            pvals_adj = (0.05*(np.sqrt(((len(df_frac) + len(df))/(len(df_frac) * len(df)))))*p_adjust)

            stats_fractions.append(stats)
            pvals_fractions.append(pvals)
            ks_val = alpha*(np.sqrt(((len(df_frac) + len(df))/(len(df_frac) * len(df)))))
            ks_vals.append(ks_val)
            pvals_adjusted_fractions.append(pvals_adj)
        
        print(pvals_adjusted_fractions)

        stats_fractions = np.asarray(stats_fractions)
        pvals_fractions = np.asarray(pvals_fractions)
        
        if plot_all:

            for i,v in enumerate(df.columns):
                plt.plot(stats_fractions[:, i])
                plt.xticks(range(10), [np.round(f, 1) for f in fractions])
                #plt.hlines(0.05, colors='r', linestyles='dashed', xmin=0.0, xmax=8.0)
                plt.title(datafiles[0])
                if len(df.columns) < 10:
                    plt.legend(df.columns)
            plt.plot(ks_vals, color='r', linestyle = 'dotted')
            plt.savefig(path_out+'/'+datafiles[idx]+' KS stats all'+'.pdf', bbox_inches='tight')
            plt.show()

            for i,v in enumerate(df.columns):
                plt.plot(pvals_fractions[:, i])
                plt.xticks(range(10), [np.round(f, 1) for f in fractions])
                #plt.yscale('log')
                plt.title(datafiles[0])
                if len(df.columns) < 10:
                    plt.legend(df.columns)
            if adjusted_pvalue:
                plt.plot(pvals_adjusted_fractions, colors='r', linestyles='dotted')
            else:
                plt.hlines(0.05, colors='r', linestyles='dotted', xmin=0.0, xmax=9.0)
            plt.savefig(path_out+'/'+datafiles[idx]+' pvals all'+'.pdf', bbox_inches='tight')
            plt.show()

        stats_mean = np.mean(stats_fractions, axis=1)
        pvals_mean = np.mean(pvals_fractions, axis=1)

        plt.plot(stats_mean)
        plt.plot(ks_vals, color='r', linestyle = 'dotted')
        plt.xticks(range(10), [np.round(f, 1) for f in fractions])
        plt.title(datafiles[0] + ' KS stats mean')
        plt.savefig(path_out+'/'+ datafiles[idx]+ ' KS stats mean'+'.pdf', bbox_inches='tight')
        plt.show()
        
        kneedle = KneeLocator(stats_mean, range(10), S=1.0, curve='convex', direction='increasing')
        kneedle.plot_knee_normalized()
        plt.show()

        plt.plot(pvals_mean)
        plt.xticks(range(10), [np.round(f, 1) for f in fractions])
        plt.title(datafiles[0] + ' p-values mean')
        if adjusted_pvalue:
            plt.plot(pvals_adjusted_fractions, colors='r', linestyles='dotted')
        else:
            plt.hlines(0.05, colors='r', linestyles='dotted', xmin=0.0, xmax=9.0)
        plt.savefig(path_out+'/'+datafiles[idx]+' KS stats mean'+'.pdf', bbox_inches='tight')
        plt.show()
        
        kneedle = KneeLocator(pvals_mean, range(10), S=1.0, curve='convex', direction='increasing')
        kneedle.plot_knee_normalized()
        plt.show()
        
        
def doubleDistributionTestTry(df1, df2, iterations=50, path_in='../data', path_out='../outputs'):
    
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    
    df_1 = pd.read_csv(path_in + '/' + df1)
    df_1 = df_1.dropna()
    df_1 = df_1.select_dtypes(include=numerics)
    
    df_2 = pd.read_csv(path_in + '/' + df2)
    df_2 = df_2.dropna()
    df_2 = df_2.select_dtypes(include=numerics)
    
    if len(df1) < len(df2):
        small_df, big_df = df_1, df_2
        
    else:
        small_df, big_df = df_2, df_1
        
    print('small: ', len(small_df))
    print('big: ', len(big_df))
        
    if len(small_df) < 5000:
        alpha = 0.05/(np.sqrt(((len(small_df) + len(small_df))/(len(small_df) * len(small_df)))))
    else:
        alpha = 1.037
        
    stats_fractions = []
    pvals_fractions = []
    ks_vals = []

    for f in range(iterations):
        df_frac = big_df.sample(frac=(len(small_df)/len(big_df)))    

        stats = []
        pvals = []
        for c in big_df.columns:
            kst = ks_2samp(small_df[c].values, df_frac[c].values, mode='asymp')
            
            if kst[1] < 1:
                stats.append(kst[0])
                pvals.append(1 - kst[1])

        stats_fractions.append(np.mean(stats))
        pvals_fractions.append(np.mean(pvals))
        ks_val = alpha*(np.sqrt(((len(small_df) + len(small_df))/(len(small_df) * len(small_df)))))
        ks_vals.append(ks_val)
    
    #return stats_fractions, pvals_fractions

    sns.kdeplot(pvals_fractions)
    plt.title('p-values distribution')
    plt.vlines(0.05, colors='r', linestyles='dotted')
    plt.savefig(path_out+'/P-vals distribution'+'.pdf', bbox_inches='tight')
    plt.show()

    sns.kdeplot(stats_fractions)
    plt.title('KS-stats distribution')
    #plt.vlines(0.05, colors='r', linestyles='dotted')
    plt.savefig(path_out+'/KS-stats distribution'+'.pdf', bbox_inches='tight')
    plt.show()