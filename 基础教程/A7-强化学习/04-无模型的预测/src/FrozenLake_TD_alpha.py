from concurrent.futures import process
import numpy as np
import Data_FrozenLake as ds
import Algorithm_MRP as algoMRP
import Algorithm_MC as algoMCE
import matplotlib.pyplot as plt
import multiprocessing as mp
import Algorithm_TD as algoTD
import tqdm

def MultipleProcess(repeat, algo_fun, ds, start_state, episodes, alpha, gamma, ground_truth, every_n_episode):
    print(algo_fun)
    pool = mp.Pool(processes=8)
    Errors = []
    Values = []
    results = []
    for i in range(repeat):
        results.append(
            pool.apply_async(
                algo_fun, args=(
                    ds, start_state, episodes, alpha, gamma, ground_truth, every_n_episode,
                )
            )
        )

    pool.close()
    pool.join()
    for i in range(len(results)):
        value, error = results[i].get()
        Values.append(value)
        Errors.append(error)

    #print("每次运行的最终结果:")
    #print(Values)

    # use to draw plot
    mean_errors = np.mean(np.array(Errors), axis=0) 
    # 多次运行的平均值
    final_mean_value = np.mean(np.array(Values), axis=0)
    print("多次运行的平均 V 值:")
    print(np.round(final_mean_value,2).reshape(4,4))

    # 多次运行的平均值误差
    final_mean_value_error = RMSE(final_mean_value, ground_truth)
    print("多次运行的平均值的误差:", final_mean_value_error)

    # 得到多次运行的最终的误差
    final_errors = np.array(Errors)[:,-1]
    # 最终的误差值的平均值
    final_mean_error = np.mean(final_errors)
    # 最终的误差值的方差
    final_var_error = np.var(final_errors)
    print("多次运行的每次误差的平均值:", final_mean_error)
    print("多次运行的每次误差的方差:", final_var_error)

    return mean_errors

def FrozenLake_Matrix(gamma):
    v = algoMRP.Matrix(ds, gamma)
    print("Matrix as Ground Truth")
    print(np.round(np.array(v).reshape(4,4), 2))
    v[2] = 0
    v[8] = 0
    v[10] = 0
    v[15] = 0    
    return v

def RMSE(a, b):
    err = np.sqrt(np.sum(np.square(a - b))/b.shape[0])
    return err


# 不同的alpha取值对算法效果的影响
if __name__=="__main__":
    gamma = 0.9
    ground_truth = FrozenLake_Matrix(gamma)

    episodes = 4000
    repeat = 8
    checkpoint = 10

    alphas = [0.01, 0.02, 0.03, 0.04, 0.05]
    for alpha in alphas:
        mean_errors = MultipleProcess(repeat, algoTD.TD_0, ds.Data_Frozen_Lake(), None, episodes, alpha, gamma, ground_truth, checkpoint)
        plt.plot(mean_errors, label="TD_0 - " + str(alpha))

    plt.grid()
    plt.legend()
    plt.show()
