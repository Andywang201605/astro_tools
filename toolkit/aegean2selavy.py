### convert aegean fits output to selavy format output
### author: Ziteng Wang (ziteng.wang@sydney.edu.au)

import pandas as pd
from pandas import DataFrame, Series
from astropy.table import Table
from tabulate import tabulate

def _num2chr(num):
    '''
    Convert a number into character. i.e.: 1 -> a
    '''
    assert (num >= 0 and num < 26), 'The number should between 0 and 25 (inclusive)'
    return chr(num+97)

def _create_idcols(df, prefix=''):
    '''
    Create island_id and component_id columns based on the aegean dataframe
    
    Params:
    ----------
    df: pandas.DataFrame
        DataFrame that stores the measurements from aegean
    prefix: str. Default: an empty string
        The prefix in these two columns
        
    Returns:
    ---------
    island_id: pandas.series.Series
        A dataframe column of island id
    componene_id: pandas.series.Series
        A dataframe column of component id
    '''
    if ('island' not in df) or ('source' not in df):
        raise ValueError("Please check your input dataframe. Column island and source are needed!")
        
    island_id = df['island'].apply(lambda x:f'{prefix}_island_{x}')
    component_id = df.apply(lambda x:'{}_component_{}{}'.format(prefix, x['island'], _num2chr(x['source'])),
                            axis=1,
                           )
    
    return island_id.rename('island_id'), component_id.rename('component_id')

def _make_name(ra_str, dec_str):
    '''
    make source name based on the ra_str and dec_str
    NOTE: there might be an error for source whose dec is close to 0
    '''
    if isinstance(ra_str, bytes):
        ra_str = ra_str.decode('utf-8')
    if isinstance(dec_str, bytes):
        dec_str = dec_str.decode('utf-8')
        
    ### check +/-
    if dec_str[0] == '-':
        sign = '-'
        dec_str = dec_str[1:]
    else:
        sign = '+'
        
    ra_split = ra_str.split(':')
    dec_split = dec_str.split(':')
    
    return 'B{}{}{}{}{}'.format(ra_split[0], ra_split[1], sign,
                                dec_split[0], dec_split[1],
                              )

def _create_namecol(df):
    '''
    Create component_name column based on the aegean dataframe
    '''
    if ('ra_str' not in df) or ('dec_str' not in df):
        raise ValueError("Please check your input dataframe. Column ra_str and dec_str are needed!")
        
    component_name = df.apply(lambda x:_make_name(x['ra_str'], x['dec_str']), 
                              axis=1,
                             )
    
    return component_name.rename('component_name')

def _create_coordcol(df):
    '''
    Create coordinates columns based on the aegean dataframe
    '''
    if ('ra_str' not in df) or ('dec_str' not in df) or ('ra' not in df) or ('dec' not in df):
        raise ValueError("Please check your input dataframe. Columns for coordinate are needed!")
        
    ra_hms = df['ra_str'].apply(lambda x:x.decode('utf-8'))
    dec_dms = df['dec_str'].apply(lambda x:x.decode('utf-8'))
    
    return (ra_hms.rename('ra_hms_cont'), 
            dec_dms.rename('dec_dms_cont'), 
            df['ra'].rename('ra_deg_cont'), 
            df['dec'].rename('dec_deg_cont'),
           )

def _create_siblingcol(df):
    '''
    Create has_siblings column
    '''
    return df['island'].duplicated().astype(int).rename('has_siblings')

def _create_flagcol(df):
    '''
    Create flag_c4 column
    '''
    return df['flags'].astype(bool).astype(int).rename('flag_c4')

def _convert2selavydf(df, prefix=''):
    '''
    Convert aegean dataframe into selavy dataframe
    '''
    series = []
    
    series.extend(_create_idcols(df, prefix))
    series.append(_create_namecol(df))
    series.extend(_create_coordcol(df))
    
    ### convert other columns
    series.append(df['err_ra'].rename('ra_err'))
    series.append(df['err_dec'].rename('dec_err'))
    series.append(Series([1300.]*len(df), name='freq'))
    series.append(df['peak_flux'].rename('flux_peak')*1e3)
    series.append(df['err_peak_flux'].rename('flux_peak_err')*1e3)
    series.append(df['int_flux'].rename('flux_int')*1e3)
    series.append(df['err_int_flux'].rename('flux_int_err')*1e3)
    series.append(df['a'].rename('maj_axis'))
    series.append(df['b'].rename('min_axis'))
    series.append(df['pa'].rename('pos_ang'))
    series.append(df['err_a'].rename('maj_axis_err'))
    series.append(df['err_b'].rename('min_axis_err'))
    series.append(df['err_pa'].rename('pos_ang_err'))
    series.append(Series([-99.]*len(df), name='maj_axis_deconv'))
    series.append(Series([-99.]*len(df), name='min_axis_deconv'))
    series.append(Series([-99.]*len(df), name='pos_ang_deconv'))
    series.append(Series([-0.]*len(df), name='maj_axis_deconv_err'))
    series.append(Series([-0.]*len(df), name='min_axis_deconv_err'))
    series.append(Series([-0.]*len(df), name='pos_ang_deconv_err'))
    series.append(Series([-99.]*len(df), name='chi_squared_fit'))
    series.append(Series([-99.]*len(df), name='rms_fit_gauss'))
    series.append(Series([-0.]*len(df), name='spectral_index'))
    series.append(Series([-99.]*len(df), name='spectral_curvature'))
    series.append(Series([-0.]*len(df), name='spectral_index_err'))
    series.append(Series([-0.]*len(df), name='spectral_curvature_err'))
    series.append(df['local_rms'].rename('rms_image')*1e3)
    
    series.append(_create_siblingcol(df))
    series.append(Series([0]*len(df), name='fit_is_estimate'))
    series.append(Series([1]*len(df), name='spectral_index_from_TT'))
    series.append(_create_flagcol(df))
    
    series.append(Series(['']*len(df), name='comment'))
    
    return pd.concat(series, axis=1)

def _selavydf_addrow(df):
    '''
    As in selavy there is one more row for unit, we just add this row mannually
    '''
    rowdf = DataFrame([['--']*len(df.columns)], columns=df.columns)
    
    return pd.concat([rowdf, df])

def to_fwf(df):
    '''
    Convert the dataframe into a string, with fwf format
    
    Adapted from: https://stackoverflow.com/a/35974742
    '''
    content = tabulate(df.values.tolist(), list(df.columns), tablefmt="plain")
    return content

def _writefile(content, fname):
    with open(fname, 'w') as fp:
        fp.write(content)
        
def aegean2selavy(aegeanfitspath, selavypath, prefix=''):
    '''
    Convert aegean fits output to selavy format
    
    Params:
    ----------
    aegeanfitspath: str
        The path where the aegean output file stores
    selavypath: str
        The path where the converted selavy file stores
    prefix: str. Default: an empty string
        The prefix in island_id and component_id
    '''
    sourcedf = Table.read(outputpath).to_pandas()
    selavydf = _convert2selavydf(sourcedf, prefix=prefix)
    selavydf = _selavydf_addrow(selavydf)
    _writefile(to_fwf(selavydf), selavypath)
    
