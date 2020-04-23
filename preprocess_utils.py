import numpy as np
def _getDegrees(root_index, max_degree, orig_df):
    df = orig_df.copy()
    d = []
    df["graph_degree"] = np.nan
    root_profile = df.loc[0,:]
    root_id = root_profile["dest_id"]
    df.loc[0,"graph_degree"] = 0
    
    first = {n for n in root_profile["dest_connected"].split(",")}
    processed = first.copy()
    d.append(first)
    
    for i in range(1, int(max_degree)):
        s = set()
        for p_id in d[i-1]: #previous degree
            profile = df.loc[df.dest_id == p_id, :].iloc[0,:]
            
            df.loc[df.dest_id == p_id, "graph_degree"] = i
            
            connects = profile["dest_connected"]
            if connects:
                s.update({n for n in profile["dest_connected"].split(",") if n not in processed})
        d.append(s)
        
    df.fillna({"graph_degree":i+1}, inplace = True)        
    return df

def _add_missing_pics(orig_df, pic_url = "https://i2.wp.com/molddrsusa.com/wp-content/uploads/2015/11/profile-empty.png.250x250_q85_crop.jpg?ssl=1"):
    return orig_df.fillna({"dest_pic":pic_url})

def preprocess(df, root_index = 0):
    max_degree = df.tree_degree.max()
    filled_df = _add_missing_pics(df)
    return _getDegrees(root_index, max_degree, filled_df)
    
    