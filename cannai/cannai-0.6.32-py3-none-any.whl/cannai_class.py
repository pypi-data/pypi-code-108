import matplotlib as mpl
import cloudpickle
import pandas as pd
import warnings
import os, sys
from scipy.spatial import distance
import copy
import datetime
from .model_compare.cal_score import *
from .model_compare.multiclass import *
import xgboost
import torch
import torch.nn as nn_t
import math as math_1
from torch.autograd import Variable
from tensorflow import keras as keras_t
import keras as keras_k
import random

__all__ = ["load_Cclass","Cmodel","multi_Cmodel","train_steps","CE_Cmodel"]

def load_Cclass(set_add):
    with open(set_add + '.pkl', "rb") as f:
        r2 = cloudpickle.load(f)
    return r2

class Cannaibase:
    # get df (and dir) to make cannai class
    def __init__(self, classtype, dirct=None, save_model=False, binary_class = False):
        self.input = None  # define in instance
        self.model_list = []  # list of [model_name,model_output,date,model,input_spfunc,output_spfunc,all_spfunc,evals_result]
        self.model_list_additional = []
        self.model_name_list = []
        self.model_name_list_additional = []
        self.save_fla = False  # if dir is not selected, cannai_model can't be saved
        self.check_save = True # if true, ask about save dir.
        self.check_save_nosave = False
        self.save_mod = False  # if false, trained model doesn't be saved
        self.warn_flag = False  # throw warning between function
        self.answer = None
        self.input_size = None
        self.output_size = None
        self.Cal_s = Cal_trained_score(self)
        self.iscannai = True # used for checking class
        self.out_is_S = False # if output is series, this become True
        self.debug_stack = None #used for debug
        self.target_label = None
        self.addtional_model_kari = True
        if classtype == "c" or classtype == "r" or classtype == "regression" or classtype == "classification":
            cl2 = "r"
        elif classtype == "b" or classtype == "binary_classification":
            cl2 = "b"
        elif classtype == "m" or classtype == "multi_classification" or classtype == "multi":
            cl2 = "m"
        else:
            raise IndexError("classtype does not match")
        self.class_type = cl2
        self.multiclass = multiclass_lib(self)
        self.multiinput = False
        self.multicmod = False
        if dirct is not None:
            self.check_save = False
            if dirct != "":
                self.save_fla = True
                self.save_mod = save_model
                self.dir = dirct
                # if folder doesn't exist, make folder
                if os.path.isdir(dirct) == False: os.mkdir(dirct)

    #save cannai_class: get pickle address
    def save_setting(self, set_add):
        with open(set_add + '.pkl', "wb") as f:
            cloudpickle.dump(self, f)


    def yesno(self):
        while True:
            ans = input()
            if ans == "y":
                return True
            elif ans == "n":
                return False

    def warning_check(self):
        if self.warn_flag:
            self.warn_flag = False
            print("warning occurred. do you want to continue?\n(y/n)")
            ans = self.yesno()
            return ans

        else: return True

    def modelname_to_num(self, key):
        if type(key) == int:
            return [key, False]
        return self.get_id(key)

    def modelname_to_num_add(self, key):
        if type(key) == int:
            return [key , True]
        return self.get_id(key, addtional_model=True)

    def is_df_or_series(self, unknown):
        if (type(unknown) == pd.core.series.Series) or (type(unknown) == pd.core.frame.DataFrame):
            return True
        else: return False

    def __del__(self, inp=None):
        yesno = None
        if (inp is None) and (self.save_mod == False):
            yesno = False
        if inp == "y" or yesno == True:
            self.save_all(None)
        elif inp == "n" or yesno == False:
            self.save_mod = False
        elif (inp is None) and (self.check_save == True):
            while True:
                print("save this model?(y, n)")
                yesno = self.yesno()
                if inp == "y" or yesno == True:
                    self.save_all(None)
                    break
                elif inp == "n" or yesno == False:
                    self.save_mod = False
                    break


        self.model_name_list.pop(inp)

    def save_all(self, inp):
        if self.save_fla: self.save_input()
        if inp is None:
            print("input Cannnai model address")
            inp = input()
        while True:
            try:
                self.save_setting(inp)
            except FileNotFoundError as e:
                sys.stderr.write(e)
                print("input Cannnai model address")
                inp = input()
            except Exception as e:
                sys.stderr.write(e)
            else: break

    def save_input(self):
        pass  # define in instance

    #return length of model_list
    def __len__(self):
        return len(self.model_list)

    def __iadd__(self, other):
        Cn = self + other
        user_ok = self.warning_check()
        if user_ok:
            self = Cn

    # model can be added using + or +=
    def __add__(self, other):
        Cn = copy.deepcopy(self)
        self.warn_flag = False

        if self.input != other.input:
            self.warn_flag = True
            warnings.warn('input data of two cannai model are different\n(input data was set to first one)')

        if other.save_fla: Cn.save_fla = True

        if Cn.save_fla:
            # second one only has directory
            if self.save_fla == False: Cn.dir = other.dir
            # first one only has directory
            elif other.save_fla == False: pass
            # both has directory
            else:
                if self.dir != other.dir:
                    self.warn_flag = True
                    warnings.warn('directory of two cannai model are different\n(directory was set to first one)')

        if self.save_mod != other.save_mod:
            self.warn_flag = True
            warnings.warn('save_model flag of two cannai model are different\n(save_model flag was set to first one)')

        Cn.model_list = self.model_list + other.model_list

        return Cn

    def get_line(self,df,columns_id):
        if type(df) == pd.core.series.Series:
            return df
        elif type(df) == np.ndarray:
            if df.ndim == 1:
                return df
            else:
                return df[columns_id]
        else:
            return df.iloc[:,columns_id]



    def save_model(self, model, m_name):
        if self.save_mod:
            with open(self.dir + m_name + '.pkl', "wb") as f:
                cloudpickle.dump(model, f)

    def save_df(self, df, m_name):
        if self.save_fla:
            with open(self.dir + m_name + '_data.pkl', "wb") as f:
                cloudpickle.dump(df, f)


    def check_num(self, input):
        if (type(input) is int) or (type(input) is float) or (type(input) is np.int) or (
                type(input) is np.float) or (type(input) is np.int32) or (type(input) is np.float32) or (type(input) is np.int64) or (type(input) is np.float64): return True
        else:return False

    def prob_01_2l_to_1l(self, list):
        if self.check_num(list[0]) == True: return list
        if len(list[0]) == 1: return list
        l2 = []
        for l1 in list: l2.append(l1[1])
        return l2

    def output_to_df(self, output):
        if self.answer is not None:
            if self.is_df_or_series(self.answer):
                if self.is_df_or_series(output):
                    if self.out_is_S:
                        output2 = self.prob_01_2l_to_1l(output)
                        df = pd.Series(output2, name=self.answer.name, index=self.answer.index)
                    elif self.class_type == "m":
                        df = pd.DataFrame(output, columns=self.answer.columns)
                    else:
                        df = pd.DataFrame(output, columns=self.answer.columns, index=self.answer.index)

                    if df.shape != self.output_size:
                        raise RuntimeError("size of true-value df is",self.output_size,", but output size of this model is",df.shape)
                elif type(output) is np.ndarray:
                    if output.shape != self.output_size:
                        output = np.squeeze(output)
                        if output.shape != self.output_size:
                            raise RuntimeError("size of true-value df is",self.output_size,", but output size of this model is",output.shape)
                    df = output
            else: df = output

        else:
            warnings.warn('true-value data has not been set')
            df = pd.DataFrame(output)
        return df

    def __contains__(self, item):
        if item in self.model_name_list: return True
        else: return False

    def set_input(self, input):
        pass

    def set_input_base(self, input):
        self.input = input
        self.input_size = input.size

    def set_answer(self, ans_df):
        pass

    def set_answer_base(self, ans_df):
        tsi = type(self.input)
        if (tsi is pd.core.frame.DataFrame) or (tsi is pd.core.series.Series):
            if type(ans_df) is list:
                ans_df = pd.Series(ans_df, name="0")
                warnings.warn('We prefer pd.Series instead of list')
            elif type(ans_df) is np.ndarray:
                ans_df = pd.DataFrame(ans_df)
                warnings.warn('We prefer pd.DataFrame instead of np.ndarray')
            self.answer = ans_df
            if type(ans_df) is pd.core.series.Series:
                self.target_label = self.answer.name
            else:
                self.target_label = self.answer.columns
        else:
            self.answer = ans_df
        self.save_df(ans_df, "t_value")
        self.output_size = ans_df.shape
        if type(self.answer) is pd.core.series.Series: self.out_is_S = True
        else: self.out_is_S = False

    def set_date(self):
        dt_now = datetime.datetime.now()
        return dt_now.strftime('%Y%m%d_%H%M%S')

    def set_mname(self, model_n, ii, target_label):
        cc = 1
        if model_n is None: m_base = "model_"+ target_label + str(ii)
        else: m_base = model_n

        if m_base in self.model_name_list:
            #  model name already exists
            m_base = m_base + "_"

            while True: #find not existing name
                if m_base + str(cc) in self.model_name_list: cc += 1
                else: break

        return m_base

    def add_model_base(self, model, model_n, ii,target_label=None,input_spfunc=None,output_spfunc=None,evals_result=None):
        pass  # define in instance

#get model and model_name
    def add_model(self, model, model_n=None,input_spfunc=None,output_spfunc=None,evals_result=None):
        ii = len(self.model_list)  #ii is id of next model
        sub_ml = self.add_model_base(model, model_n, ii, None,input_spfunc=input_spfunc,output_spfunc=output_spfunc,evals_result = evals_result)
        self.save_df(sub_ml[1], model_n)
        self.model_list.append(sub_ml)
        self.model_name_list.append(sub_ml[0])

    def add_model_nomod(self, output_df, model_n=None,input_spfunc=None,output_spfunc=None,evals_result=None):
        ii = len(self.model_list)  #ii is id of next model
        sub_ml = self.add_model_base_nomod(output_df, model_n, ii, None,input_spfunc=input_spfunc,output_spfunc=output_spfunc,evals_result = evals_result)
        self.save_df(sub_ml[1], model_n)
        self.model_list.append(sub_ml)
        self.model_name_list.append(sub_ml[0])

    def get_id(self, key, addtional_model = False):
        t_it = type(key)

        if self.model_list == []:
            raise Exception("no model inputed")

        if t_it == int:
            return [key, addtional_model]

        if t_it == str:
            if key in self.model_name_list:
                return [self.model_name_list.index(key), False]
            else:
                if key in self.model_name_list_additional:
                    return [self.model_name_list_additional.index(key), True]
                else:
                    raise IndexError(key + ": can not found in models")

        else:
            raise TypeError("key must be int or string, but type of key is " + str(t_it))

    def __delitem__(self, key):
        id, is_additional = self.get_id(key)

        try:
            if is_additional:
                del self.model_list_additional[id]
                del self.model_name_list_additional[id]
            else:
                del self.model_list[id]
                del self.model_name_list[id]
        except IndexError:
            raise IndexError("number of model is " + str(len(self)) + ", but id is " + str(key))

    def __getitem__(self, item):
        id, is_additional = self.get_id(item)

        try:
            if is_additional:
                sub_model = self.model_list_additional[id]
            else:
                sub_model = self.model_list[id]
        except IndexError:
            if self.addtional_model:
                try:
                    sub_model = self.model_list_additional[id]

                except IndexError:
                    raise IndexError("number of model is " + str(len(self)) + ", but id is " + str(item))
                else:
                    return sub_model
            else:
                raise IndexError("number of model is " + str(len(self)) + ", but id is " + str(item))
        else:
            return sub_model

    #undo last trained-model addition
    def undo(self):
        self.model_name_list.pop(-1)
        self.model_list.pop(-1)

    def get_data(self, key,addtional_model=None):
        key2, addtional_model2 = self.modelname_to_num(key)
        if addtional_model == None:
            addtional_model = addtional_model2

        if addtional_model:
            return self.model_list_additional[key2]
        else:
            return self.model_list[key2]

    #throw data list for printing graphs
    def get_datas(self, keys,target_label=None,keys_add=[]):
        dat_list = []
        for key in keys:
            key2, is_additional = self.get_id(key)
            if is_additional:
                dat = self.model_list_additional[key2]
            else:
                dat = self.model_list[key2]
            dat_list.append(dat[1])
        if keys_add != []:
            for key in keys_add:
                key2, is_additional = self.get_id(key)
                if is_additional:
                    dat = self.model_list_additional[key2]
                else:
                    dat = self.model_list[key2]
                dat_list.append(dat[1])
        return dat_list

    # throw model name for printing graphs
    def get_names(self, keys,target_label=None):
        dat_list = []
        for key in keys:
            key2, is_additional = self.get_id(key)
            if is_additional:
                dat = self.model_list_additional[key2]
            else:
                dat = self.model_list[key2]
            dat_list.append(dat[0])
        return dat_list

        # throw model name for printing graphs
    def get_model(self, key,target_label=None):
        key2, is_additional = self.get_id(key)
        if is_additional:
            dat = self.model_list_additional[key2]
        else:
            dat = self.model_list[key2]
        return dat[3]

    # throw label name for printing graphs
    def get_labelname(self, line,target_label=None):
        if type(line) is str: return line
        elif type(line) is int:
            if self.out_is_S:
                if type(self.model_list[0][1]) is np.ndarray:
                    if target_label != None:
                        return target_label
                    else:
                        return "predict"
                else:
                    return self.model_list[0][1].name
            elif type(self.model_list[0][1]) == pd.core.frame.DataFrame:
                return self.model_list[0][1].columns[line]
            else:
                if target_label != None:
                    return target_label
                else:
                    return "predict"

    def get_answer(self, target_label=None, no_multiple_flag=False):
        ans_df = self.get_answer_base(target_label)

        if (no_multiple_flag) and (self.check_df_multiple(ans_df)):
            raise IndexError("please set target_label while using this function")
        return ans_df

    def get_answer_base(self,target_label=None):
        if self.answer is None:
            raise RuntimeError('true-value data has not been set')

        if target_label is None:
            return self.answer

        else: return self.answer[target_label]

    def get_input(self):
        if self.input is None:
            raise RuntimeError('input data has not been set')
        else: return self.input

    def input_convert(self, model):
        if isinstance(model, xgboost.core.Booster):
            return xgboost.DMatrix(self.input)
        else: return self.input

    def check_df_multiple(self, df):
        if (type(df) is not list) and (type(df) is not pd.core.series.Series):
            if type(df) is pd.core.frame.DataFrame:
                if len(df.columns) != 1:
                    return True
            elif type(df) is np.ndarray:
                if df.ndim == 1:
                    return False
                if df.shape[1] != 1:
                    return True

        return False

    #get output from torch NN model
    def NNt_get_output(self, model, imp2):
        imp3 = self.to_ndarray(imp2)
        X_valid_var = Variable(torch.FloatTensor(imp3), requires_grad=False)
        with torch.no_grad():
            test_result = model(X_valid_var)
        output = test_result.data.numpy()
        if self.class_type == "b":
            output = self.output_forbinary(output)
        return output

    def output_forbinary(self, outpu):
        tt = outpu.T[1]
        tmin = tt.min()
        tmax = tt.max()
        haba = tmax - tmin
        tt = tt - tmin
        tt = tt / haba
        return tt

    def to_ndarray(self,imp):
        timp = type(imp)
        if timp is np.ndarray: return imp
        elif self.is_df_or_series(imp): return imp.values
        else:
            raise IndexError("this file type is "+ str(timp) +" , and this can not be converted to ndarray")


class Cmodel(Cannaibase):
    model_list_additional_weight = []

    def save_input(self):
        self.save_df(self.input, "input")

    def set_input(self, input):
        self.set_input_base(input)

    def set_answer(self, ans_df):
        if self.check_df_multiple(ans_df):
            warnings.warn("answer_df must be series or list \n if you want to set multi_line answer, use cannai.multi_Cmodel")
        self.set_answer_base(ans_df)

    def get_output(self, model,input_spfunc=None):
        imp2 = self.input_convert(model)
        if input_spfunc != None:
            imp2 = input_spfunc(imp2)

        mod_cname = model.__class__.__name__
        al_re = False
        if isinstance(model, nn_t.Module):
            output = self.NNt_get_output(model, imp2)
        elif mod_cname == "Sequential":
            output = self.keras_get_output(model, imp2)
        else:
            try:
                output = model.predict_proba(imp2)
                al_re = True
            except:
                output = model.predict(imp2)

        if al_re and self.class_type == "b":
            output = output.T[1]

        return output

    def keras_get_output(self, model, imp):
        output_kari = model.predict(imp, verbose=1)
        output = np.squeeze(output_kari)
        return output

    def add_model_base(self, model, model_n, ii, target_label=None,input_spfunc=None,output_spfunc=None,all_spfunc=None,evals_result=None):
        model_n = self.set_mname(model_n, ii, target_label)
        dat = self.set_date()

        self.save_model(model, model_n)

        output = self.get_output(model,input_spfunc=input_spfunc)

        df = self.output_to_df(output)

        if output_spfunc != None:
            df = output_spfunc(df)

        return [model_n, df, dat,model,input_spfunc,output_spfunc,all_spfunc, evals_result]

    def add_model_base_nomod(self, output_df, model_n, ii, target_label=None,input_spfunc=None,output_spfunc=None,all_spfunc=None,evals_result=None):
        model_n = self.set_mname(model_n, ii, target_label)
        dat = self.set_date()


        output = output_df


        return [model_n, output, dat,"no model",input_spfunc,output_spfunc,all_spfunc, evals_result]

    def combine_models(self, e_score,e_score_key=None, kaisu=500,kaisu2=500,rand_rate=0.1, addition_len=10, save_higher=False):
        if e_score_key == None:
            e_ans_l = self.get_line(self.answer,0)
        else:
            e_ans_l = self.get_line(self.answer,e_score_key)
        sml_len = len(self.model_list)
        all_mod_data = []
        for ism in range(sml_len):
            all_mod_data.append(self.model_list[ism][1])
        model_list_additional_kari = []
        model_list_additional_kari_score = []
        model_list_additional_kari_weight = []
        model_list_additional_kari_group = []
        jyousan = -1 * save_higher
        totyu_len = min(addition_len * 7, int(kaisu2 / 3))
        kaisu0 = kaisu * 3


        for ii in range(sml_len):

            kari_weight = []
            for ism in range(sml_len):
                kka_wi = 0.0
                if ism == ii:
                    kka_wi = 1.0
                kari_weight.append(kka_wi)

            mod_val = all_mod_data[ii]
            if e_score_key == None:
                e_out_l = self.get_line(mod_val, 0)
            else:
                e_out_l = self.get_line(mod_val, e_score_key)

            comv_score = self.Cal_s.cal_score_single_sub(e_score, e_out_l, e_ans_l)
            len_mod_lak = len(model_list_additional_kari)
            new_mod_group = self.model_list[ii]
            jyuni = 0
            if len_mod_lak > 0:
                for iij in range(len_mod_lak):
                    if ((model_list_additional_kari_score[iij] - comv_score) * jyousan) > 0:
                        break
                    else:
                        jyuni += 1

            model_list_additional_kari.insert(jyuni, mod_val)
            model_list_additional_kari_score.insert(jyuni, comv_score)
            model_list_additional_kari_weight.insert(jyuni, kari_weight)
            model_list_additional_kari_group.insert(jyuni, new_mod_group)

        for ii in range(kaisu0):
            print("\rround1: " + str(ii + 1) + "/" + str(kaisu0+1), end="")
            kari_weight = []
            sum_ka_wi = 0.0
            for ism in range(sml_len):
                kka_wi = random.uniform(-0.3, 1.5)
                kari_weight.append(kka_wi)
                sum_ka_wi += kka_wi

            if sum_ka_wi < 0.5:
                continue

            gokei = random.uniform(0.8, 1.3)
            ka_wi_av = sum_ka_wi / gokei
            dat = self.set_date()
            for ism in range(sml_len):
                kari_weight[ism] /= ka_wi_av
            mod_val = all_mod_data[0] * kari_weight[0]
            for ism in range(1,sml_len):
                mod_val += all_mod_data[ism] * kari_weight[ism]
            if e_score_key == None:
                e_out_l = self.get_line(mod_val, 0)
            else:
                e_out_l = self.get_line(mod_val, e_score_key)
            comv_score = self.Cal_s.cal_score_single_sub(e_score,e_out_l, e_ans_l)
            len_mod_lak = len(model_list_additional_kari)
            new_mod_group = ["combine0_" + str(ii), mod_val, dat, "No_model", None, None, None, None]
            jyuni = 0

            model_list_additional_kari.insert(jyuni, mod_val)
            model_list_additional_kari_score.insert(jyuni, comv_score)
            model_list_additional_kari_weight.insert(jyuni, kari_weight)
            model_list_additional_kari_group.insert(jyuni, new_mod_group)


        model_list_additional_kari_weight = np.array(model_list_additional_kari_weight)

        model_list_additional_kari_group_3 = []
        for iia in range(len(model_list_additional_kari)):
            model_list_additional_kari_group_3.append(
                [model_list_additional_kari_score[iia], model_list_additional_kari_group[iia],
                 model_list_additional_kari_weight[iia], model_list_additional_kari[iia]])

        model_list_additional_kari_group_3 = sorted(model_list_additional_kari_group_3, key=lambda x: x[0])

        model_list_additional_kari_group_3 = model_list_additional_kari_group_3[:addition_len]

        model_list_additional_kari_score = []
        model_list_additional_kari_group = []
        model_list_additional_kari_weight = []
        model_list_additional_kari = []
        for iia in range(len(model_list_additional_kari_group_3)):
            model_list_additional_kari_score.append(model_list_additional_kari_group_3[iia][0])
            model_list_additional_kari_group.append(model_list_additional_kari_group_3[iia][1])
            model_list_additional_kari_weight.append(model_list_additional_kari_group_3[iia][2])
            model_list_additional_kari.append(model_list_additional_kari_group_3[iia][3])

        model_list_additional_kari_score2 = copy.deepcopy(model_list_additional_kari_score)
        model_list_additional_kari2 = copy.deepcopy(model_list_additional_kari)
        model_list_additional_kari_weight2 = copy.deepcopy(model_list_additional_kari_weight)
        model_list_additional_kari_group2 = copy.deepcopy(model_list_additional_kari_group)
        print("\n")
        for round_ in range(kaisu2):

            l_modlak = len(model_list_additional_kari)
            for ii in range(l_modlak):
                print("\rround2: step" + str(round_ + 1) + "/" + str(kaisu2 + 1) + ": " + str(ii + 1) + "/" + str(l_modlak + 1), end="")
                kari_weightb = model_list_additional_kari_weight[ii]

                run_again = 0.0

                while (abs(run_again) <= 0.2):
                    ag_flag = False
                    for ism in range(sml_len):
                        if random.random() < rand_rate:
                            chang_val = random.uniform(-0.7, 0.7)
                            kari_weightb[ism] += chang_val
                            run_again += chang_val

                mod_val = all_mod_data[0] * kari_weightb[0]

                for ism in range(1, sml_len):
                    sss_k2 = all_mod_data[ism] * kari_weightb[ism]
                    mod_val += sss_k2
                dat = self.set_date()
                if e_score_key == None:
                    e_out_l = self.get_line(mod_val, 0)
                else:
                    e_out_l = self.get_line(mod_val, e_score_key)
                comv_score = self.Cal_s.cal_score_single_sub(e_score, e_out_l, e_ans_l)
                new_mod_group = ["combine" + str(round_) +"_" + str(ii), mod_val, dat, "No_model", None, None, None, None]
                len_mod_lak = len(model_list_additional_kari2)

                jyuni = 0

                model_list_additional_kari2.insert(jyuni, mod_val)
                model_list_additional_kari_score2.insert(jyuni, comv_score)
                model_list_additional_kari_weight2 = np.insert(model_list_additional_kari_weight2, jyuni, kari_weightb, axis=0)
                model_list_additional_kari_group2.insert(jyuni, new_mod_group)

            model_list_additional_kari = copy.deepcopy(model_list_additional_kari2)
            model_list_additional_kari_score = copy.deepcopy(model_list_additional_kari_score2)
            model_list_additional_kari_weight = copy.deepcopy(model_list_additional_kari_weight2)
            model_list_additional_kari_group = copy.deepcopy(model_list_additional_kari_group2)

            model_list_additional_kari_group_3 = []
            for iia in range(len(model_list_additional_kari)):
                model_list_additional_kari_group_3.append([model_list_additional_kari_score[iia],model_list_additional_kari_group[iia],model_list_additional_kari_weight[iia],model_list_additional_kari[iia]])

            model_list_additional_kari_group_3 = sorted(model_list_additional_kari_group_3, key=lambda x: x[0])

            if ii % 3 == 2:
                we_ba = 0
                weight_base1 = model_list_additional_kari_group_3[0][2]

                for kkk in reversed(range(1,len(model_list_additional_kari_group_3))):
                    karii = model_list_additional_kari_group_3[kkk][2]
                    kyo_nd = distance.euclidean(karii,weight_base1)
                    if kyo_nd < 0.01:
                        we_ba += 1
                        if we_ba % 5 == 4:
                            model_list_additional_kari_group_3.pop(kkk)

                we_ba = 0
                weight_base2 = model_list_additional_kari_group_3[1][2]

                for kkk in reversed(range(1,len(model_list_additional_kari_group_3))):
                    karii = model_list_additional_kari_group_3[kkk][2]
                    kyo_nd = distance.euclidean(karii,weight_base2)
                    if kyo_nd < 0.01:
                        we_ba += 1
                        if we_ba % 5 == 4:
                            model_list_additional_kari_group_3.pop(kkk)

                weight_base3 = model_list_additional_kari_group_3[2][2]

                we_ba = 0
                for kkk in reversed(range(1,len(model_list_additional_kari_group_3))):
                    karii = model_list_additional_kari_group_3[kkk][2]
                    kyo_nd = distance.euclidean(karii,weight_base3)
                    if kyo_nd < 0.01:
                        we_ba += 1
                        if we_ba % 5 == 4:
                            model_list_additional_kari_group_3.pop(kkk)


            model_list_additional_kari_group_3 =  model_list_additional_kari_group_3[:totyu_len]

            model_list_additional_kari_score = []
            model_list_additional_kari_group = []
            model_list_additional_kari_weight = []
            model_list_additional_kari = []
            for iia in range(len(model_list_additional_kari_group_3)):
                model_list_additional_kari_score.append(model_list_additional_kari_group_3[iia][0])
                model_list_additional_kari_group.append(model_list_additional_kari_group_3[iia][1])
                model_list_additional_kari_weight.append(model_list_additional_kari_group_3[iia][2])
                model_list_additional_kari.append(model_list_additional_kari_group_3[iia][3])

        print("\n")

        weight_base1 = model_list_additional_kari_group_3[0][2]
        for kkk in reversed(range(1, len(model_list_additional_kari_group_3))):
            karii = model_list_additional_kari_group_3[kkk][2]
            kyo_nd = distance.euclidean(karii, weight_base1)
            if kyo_nd < 0.01:
                model_list_additional_kari_group_3.pop(kkk)

        weight_base2 = model_list_additional_kari_group_3[1][2]

        for kkk in reversed(range(1, len(model_list_additional_kari_group_3))):
            karii = model_list_additional_kari_group_3[kkk][2]
            kyo_nd = distance.euclidean(karii, weight_base2)
            if kyo_nd < 0.01:
                model_list_additional_kari_group_3.pop(kkk)

        weight_base3 = model_list_additional_kari_group_3[2][2]

        for kkk in reversed(range(1, len(model_list_additional_kari_group_3))):
            karii = model_list_additional_kari_group_3[kkk][2]
            kyo_nd = distance.euclidean(karii, weight_base3)
            if kyo_nd < 0.01:
                model_list_additional_kari_group_3.pop(kkk)

        for mnl in self.model_name_list:
            for cou_ii in range(len(model_list_additional_kari_group_3)):
                if mnl in model_list_additional_kari_group_3[cou_ii][1][0]:
                    model_list_additional_kari_group_3.pop(cou_ii)
                    break

        model_list_additional_kari_group_3 = model_list_additional_kari_group_3[:addition_len]
        model_list_additional_kari_score = []
        model_list_additional_kari_group = []
        model_list_additional_kari_weight = []
        model_list_additional_kari = []
        for iia in range(len(model_list_additional_kari_group_3)):
            model_list_additional_kari_score.append(model_list_additional_kari_group_3[iia][0])
            model_list_additional_kari_group.append(model_list_additional_kari_group_3[iia][1])
            model_list_additional_kari_weight.append(model_list_additional_kari_group_3[iia][2])
            model_list_additional_kari.append(model_list_additional_kari_group_3[iia][3])
        sml_len = len(model_list_additional_kari_group)
        smln = []
        for ism in range(sml_len):
            smln.append(model_list_additional_kari_group[ism][0])
            model_list_additional_kari_group[ism][1] = self.output_to_df(model_list_additional_kari_group[ism][1])
        self.model_name_list_additional = smln
        self.model_list_additional = copy.deepcopy(model_list_additional_kari_group)
        self.model_list_additional_weight = np.concatenate([mskw for mskw in model_list_additional_kari_weight])
        self.model_list_additional_score = copy.deepcopy(model_list_additional_kari_score)

    def print_cobinedmodel_weight(self):
        if self.model_list_additional_weight == []:
            raise RuntimeError("Please run combine_models first")
        else:
            comb_wei = pd.DataFrame(self.model_list_additional_weight.reshape([len(self.model_name_list_additional), len(self.model_name_list)]),
              columns=self.model_name_list,
              index=self.model_name_list_additional)

            print(comb_wei)






class CE_Cmodel(Cmodel):
    group_name_list = []
    num_member = []
    model_groupid = []
    def add_model(self, model,group, model_n=None,input_spfunc=None,output_spfunc=None,all_spfunc=None,evals_result=None):
        ii = len(self.model_list)  #ii is id of next model
        ii2 = len(self.group_name_list) #ii2 is id of next groupname
        if(group == ii2):
            if model_n == None: model_n = "model" + str(group)
            self.group_name_list.append(model_n)
            model_n = model_n + "_0"
            self.num_member.append(1)
        else:
            model_n = self.group_name_list[group] + "_" + str(self.num_member[group])
            self.num_member[group] += 1
        self.model_groupid.append(group)
        sub_ml = self.add_model_base(model, model_n, ii,input_spfunc=input_spfunc,output_spfunc=output_spfunc,all_spfunc=all_spfunc,evals_result = evals_result)
        self.save_df(sub_ml[1], model_n)
        self.model_list.append(sub_ml)
        self.model_name_list.append(sub_ml[0])


class multi_Cmodel(Cmodel):

    model_dict = {"kari_null":[]}
    model_name_dict = {"kari_null":[]}
    kari_label = ""

    def __init__(self, classtype, dirct=None, save_model=True, binary_class=False):
        super().__init__(classtype, dirct=dirct, save_model=save_model, binary_class=binary_class)
        self.multicmod = True

    def overwrite_lists(self,target_label):
        self.model_list = self.model_dict[target_label]
        self.model_name_list = self.model_name_dict[target_label]

    def get_names(self, keys,target_label):
        self.overwrite_lists(target_label)
        return super().get_names(keys)

    def get_datas(self, keys,target_label):
        self.overwrite_lists(target_label)
        return super().get_datas(keys)

    def get_labelname(self, line,target_label):
        self.overwrite_lists(target_label)
        return super().get_labelname(line)

    def get_model(self, key,target_label):
        self.overwrite_lists(target_label)
        return super().get_model(key)

    def search_md(self,target_label):
        if target_label in self.model_dict:
            return self.model_dict[target_label]
        else: return -1

    def set_answer(self, ans_df):
        super().set_answer(ans_df)


    def add_model(self, model,target_label, model_n = None, model_name=None,input_spfunc=None,output_spfunc=None,evals_result=None):
        self.kari_label = target_label
        if model_n != None:
            model_name = model_n
        s_res = self.search_md(target_label)
        if s_res == -1:
            ii = 0
            s_res = []
            s_mn_dic = []
        else:
            ii = len(s_res)  #ii is id of next model
            s_mn_dic = self.model_name_dict[target_label]
        sub_ml = self.add_model_base(model, model_name, ii, target_label,input_spfunc=input_spfunc,output_spfunc=output_spfunc,evals_result=evals_result)
        self.save_df(sub_ml[1], model_name)
        s_res.append(sub_ml)
        self.model_dict[target_label] = s_res
        s_mn_dic.append(sub_ml[0])
        self.model_name_dict[target_label] = s_mn_dic

    def set_answer(self, ans_df):
        if not self.check_df_multiple(ans_df):
                raise IndexError(
                    "answer_df must be multi_line dataframe or ndarray. \n if you want to set series or list, use cannai.Cmodel")
        self.set_answer_base(ans_df)

    def output_to_df(self, output):
        if self.answer is not None:
            if self.is_df_or_series(output):
                output2 = self.prob_01_2l_to_1l(output)
                df = pd.Series(output2, name=self.kari_label, index=self.answer.index)
            else: df = output

        else:
            warnings.warn('true-value data has not been set')
            df = pd.DataFrame(output)
        return df

class Cmodel_notable(Cmodel):
    def save_input(self):
        #with open(self.dir + 'input.pkl', "wb") as f:
        #    cloudpickle.dump(self.input, f)
        self.save_df(self.input, "input")

    def set_input(self, input):
        self.set_input_base(input)

def train_steps(multi_Cmodel):
    pass

def mega_Cmodel(Cannaibase):
    def save_input(self):
        self.save_df(self.input, "input")

