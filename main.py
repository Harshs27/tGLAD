import os, sys
# reloads modules automatically before entering the 
# execution of code typed at the IPython prompt.
# sys.path.insert(0, "../..")
# %load_ext autoreload
# %autoreload 2
print(sys.prefix)
import warnings
warnings.filterwarnings('ignore')

import uGLAD.uglad as uG
from uGLAD.uglad_utils import data_processing as dp
from uGLAD.uglad_utils import ggm as ggm
from utils.read_pamap import load_subjects


from tqdm import tqdm
import numpy as np
import json

from sklearn.metrics import accuracy_score

def batch_time_series(df, window_size, batch_size, stride_length):
    # Calculate the number of windows
    num_windows = df.shape[0] // window_size
    # Split the dataframe into windows
    windows = [df.iloc[i:i+window_size,:].values for i in range(0, num_windows*window_size-window_size, stride_length)]

    # # Stack the windows into batches
    ts_batches = [windows[i:i+batch_size] for i in range(0, len(windows), batch_size)]
    return ts_batches


def uglad_res(df):
    model_uGLAD = uG.uGLAD_multitask()  

    batch_size = len(df)

    # Fit to the data
    model_uGLAD.fit(
        df,
        centered=False,
        epochs=2000,
        lr=0.001,
        INIT_DIAG=0,
        L=5,
        verbose=False,
    )
    return model_uGLAD


def get_partial_correlation_from_precision(theta, column_names):
    rho = ggm.get_partial_correlations(theta)
    Gr, _, _ = ggm.graph_from_partial_correlations(
        rho, 
        column_names,
        sparsity=1,
    )
    return Gr

def get_all_edges(column_list):
    edge_lst = column_list
    all_edges = []
    for i in range(len(edge_lst)):
        for j in range(i+1, len(edge_lst)):
            all_edges.append((edge_lst[i], edge_lst[j]))
    return all_edges

def distance_fun(g_correlation_map_0, g_correlation_map_1):
    dist = 0
    for edge1, edge2 in all_edges:
        weight_0 = g_correlation_map_0.get_edge_data(edge1, edge2)['weight'] if g_correlation_map_0.get_edge_data(edge1, edge2) else 0
        weight_1 = g_correlation_map_1.get_edge_data(edge1, edge2)['weight'] if g_correlation_map_1.get_edge_data(edge1, edge2) else 0
        dist += abs(weight_0 - weight_1)
    return dist

def compare_graphs(g_correlation_map):
    m = len(g_correlation_map)
    M = np.zeros((m,m))
    for i in range(m):
        for j in range(m):
            if i == j:
                M[i][j] = 0
            else:
                M[i][j] = distance_fun(g_correlation_map[i], g_correlation_map[j])
    return M   

def distance_graph(g_correlation_map_0, g_correlation_map_1, all_edges):
    dist = 0
    for edge1, edge2 in all_edges:
        weight_0 = g_correlation_map_0.get_edge_data(edge1, edge2)['weight'] if g_correlation_map_0.get_edge_data(edge1, edge2) else 0
        weight_1 = g_correlation_map_1.get_edge_data(edge1, edge2)['weight'] if g_correlation_map_1.get_edge_data(edge1, edge2) else 0
        dist += (weight_0 - weight_1)
    return dist

def get_label(extended_win,thresh_ddg_corr):
    labels = np.ones(len(thresh_ddg_corr))
    for i in range(len(thresh_ddg_corr)):
        if thresh_ddg_corr[i] > 0:
            labels[max(0, i-extended_win): min(len(labels)-1, i+extended_win)] = np.zeros(len(labels[max(0, i-extended_win): min(len(labels)-1, i+extended_win)]))
    return labels


# def accuracy(labels, gt):
#     TP, FP, FN, TN=0,0,0,0
#     for i in range(len(labels)):
#         if gt[i] == labels[i]:
#             TP += 1
#         elif labels[i] == 1 and gt[i] == 0:
#             FP += 1
#         elif labels[i] == 0 and gt[i] == 1:
#             FN += 1
#         else:
#             TN += 1
#     accuracy = (TP + TN)/(TP + FP+ FN +TN)
#     return accuracy


if __name__=="__main__":
    subject_data = 'data/Pamap/Subject101.dat'
    column_list = ['hand_3D_acceleration_16_x', 'hand_3D_acceleration_16_z', 'ankle_3D_gyroscope_x']
    label = 'activity_id'
    start_part, end_part = 76000, 179000
    window_size = 1000
    batch_size = 20
    stride_length = 100
  
    data = load_subjects(subject_data)
    modified_df = data[start_part: end_part]
    df = modified_df[column_list]
    df = df.ffill()
    df = df.bfill()

    ts_batches = batch_time_series(df, window_size, batch_size, stride_length)
    all_edges=get_all_edges(column_list)

    g_correlation_map = {}
    uglad_precision_lst = []
    folder_name = "result"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        
    for i in tqdm(range(len(ts_batches))):
        uglad_i = uglad_res(ts_batches[i])
        for j in range(uglad_i.precision_.shape[0]):
            g_correlation = get_partial_correlation_from_precision(uglad_i.precision_[j], column_list)
            g_correlation_map[len(g_correlation_map)] = g_correlation
            uglad_precision_lst.append(uglad_i.precision_[j]) 
            np.save(f"result/uglad_precision_lst_{batch_size}_{window_size}.npy", uglad_precision_lst)    
    M = compare_graphs(g_correlation_map)
    np.save(f"result/matrix_res_{batch_size}_{window_size}.npy", M)
    
    
    g_correlation_map = {}
    gt = (modified_df['activity_id'].values > 0)*1.0
    for i in (range(len(uglad_precision_lst))):
        g_correlation = get_partial_correlation_from_precision(uglad_precision_lst[i], column_list)
        g_correlation_map[len(g_correlation_map)] = g_correlation
    all_edges = get_all_edges(column_list)
    dg_corr= [distance_graph(g_correlation_map[i], g_correlation_map[i-1], all_edges) for i in range(1, len(g_correlation_map))]

    scaled_dg_corr = np.array(dg_corr).repeat(stride_length,axis=0)

    ddg_corr = np.array([abs(scaled_dg_corr[i] - scaled_dg_corr[i-1]) for i in range(1, len(scaled_dg_corr))])

    thresh_ddg_corr = (np.array(ddg_corr) > 0.5) * np.array(ddg_corr)
    extended_win = window_size
    labels = get_label(extended_win, thresh_ddg_corr)
    performance = {"batch_size":batch_size, "window_size":window_size, "accuracy":accuracy_score(gt[:len(labels)], labels)}
    with open("result/logs.json", "w") as f:
        json.dump(performance, f)


 



            

