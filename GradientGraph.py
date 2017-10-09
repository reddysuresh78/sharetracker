import pandas as pd
import matplotlib.pyplot as plt



feature_importances_ = [0.04822394, 0.01788222, 0.12163172, 0.01265418, 0.05038396, 0.00981092
    , 0.01796845, 0.01612578, 0.00459073, 0., 0.00083516, 0.00923418
    , 0.00176909, 0.00552193, 0.05559564, 0.01406513, 0.03223659, 0.
    , 0.04771776, 0.02465013, 0.05743572, 0.03623587, 0.00277283, 0.
    , 0.02181068, 0.00152486, 0.00666549, 0.02268651, 0.01048459, 0.03229212
    , 0.0057987, 0.00919204, 0.01462403, 0.01783307, 0.14140787, 0.06085282
    , 0.00666683, 0.00728946, 0., 0.00090207, 0.00081402, 0.00481077
    , 0.0009191, 0.01204129, 0.00121248, 0., 0.00868428, 0.00257924
    , 0.00764833, 0.01083692, 0.00192231, 0.0011582, 0., 0., 0., 0., 0.]

predictors = ['ps_ind_01', 'ps_ind_02_cat', 'ps_ind_03', 'ps_ind_04_cat', 'ps_ind_05_cat', 'ps_ind_06_bin',
              'ps_ind_07_bin', 'ps_ind_08_bin', 'ps_ind_09_bin', 'ps_ind_10_bin', 'ps_ind_11_bin', 'ps_ind_12_bin',
              'ps_ind_13_bin', 'ps_ind_14', 'ps_ind_15', 'ps_ind_16_bin', 'ps_ind_17_bin', 'ps_ind_18_bin', 'ps_reg_01',
              'ps_reg_02', 'ps_reg_03', 'ps_car_01_cat', 'ps_car_02_cat', 'ps_car_03_cat', 'ps_car_04_cat',
              'ps_car_05_cat', 'ps_car_06_cat', 'ps_car_07_cat', 'ps_car_08_cat', 'ps_car_09_cat', 'ps_car_10_cat',
              'ps_car_11_cat', 'ps_car_11', 'ps_car_12', 'ps_car_13', 'ps_car_14', 'ps_car_15', 'ps_calc_01',
              'ps_calc_02', 'ps_calc_03', 'ps_calc_04', 'ps_calc_05', 'ps_calc_06', 'ps_calc_07', 'ps_calc_08',
              'ps_calc_09', 'ps_calc_10', 'ps_calc_11', 'ps_calc_12', 'ps_calc_13', 'ps_calc_14', 'ps_calc_15_bin',
              'ps_calc_16_bin', 'ps_calc_17_bin', 'ps_calc_18_bin', 'ps_calc_19_bin', 'ps_calc_20_bin']

feat_imp = pd.Series(feature_importances_, predictors).sort_values(ascending=False)
feat_imp.plot(kind='bar', title='Feature Importances')
plt.ylabel('Feature Importance Score')
plt.show()