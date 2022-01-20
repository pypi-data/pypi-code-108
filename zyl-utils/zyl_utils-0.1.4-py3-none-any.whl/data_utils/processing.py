import pandas as pd


class Processor:
    def __init__(self):
        pass

    @staticmethod
    def split_data_evenly(data, num) -> list:
        """
            split_data_evenly,顺序均分数据，遵循最后一份最少的原则
        Args:
            data: may be list,dataframe,tuple... should have __len__
            num: the number of sub_data

        Returns:
            list of sub_data
        """
        data_length = len(data)
        step = int(data_length / num)
        other_data = data_length % num

        if data_length <= num:
            print('Warning: data_length <= data_num')
            return data
        if other_data == 0:
            return [data[i:i + step] for i in range(0, data_length, step)]
        else:
            first_part_data = [data[i:i + step + 1] for i in range(0, int((step + 1) * other_data), step + 1)]
            second_part_list = [data[i:i + step] for i in range(int((step + 1) * other_data), data_length, step)]
            first_part_data.extend(second_part_list)
            return first_part_data

    @staticmethod
    def split_train_eval(data: pd.DataFrame, max_eval_size=5000):
        """
        切分训练集和评估集
        Args:
            data: pd.DataFrame
            max_eval_size: 评估集最大size

        Returns:
            train,eval
        """
        from sklearn.utils import resample
        raw_data = resample(data, replace=False)
        cut_point = min(max_eval_size, int(0.2 * len(raw_data)))
        eval_df = raw_data[0:cut_point]
        train_df = raw_data[cut_point:]
        return train_df, eval_df

    @staticmethod
    def two_classification_sampling(train_df: pd.DataFrame, column='labels', neg_label='|', mode='up_sampling'):
        """
        训练集二分类采样:上采样和下采样
        Args:
            train_df: pd.DataFrame
            column: the column to sampling
            neg_label: neg_label
            mode:up_sampling/down_sampling

        Returns:
            data: pd.DataFrame
        """
        import pandas as pd
        from sklearn.utils import resample
        negative_df = train_df[train_df[column] == neg_label]
        neg_len = negative_df.shape[0]
        positive_df = train_df[train_df[column] != neg_label]
        pos_len = positive_df.shape[0]
        if neg_len > pos_len:
            if mode == 'down_sampling':
                down_sampling_df = resample(negative_df, replace=False, n_samples=pos_len, random_state=242)
                train_df = pd.concat([positive_df, down_sampling_df], ignore_index=True)
            else:
                up_sampling_df = resample(positive_df, replace=True, n_samples=(neg_len - pos_len), random_state=242)
                train_df = pd.concat([train_df, up_sampling_df], ignore_index=True)
        elif neg_len < pos_len:
            if mode == 'down_sampling':
                down_sampling_df = resample(positive_df, replace=False, n_samples=neg_len, random_state=242)
                train_df = pd.concat([down_sampling_df, negative_df], ignore_index=True)
            else:
                up_sampling_df = resample(negative_df, replace=True, n_samples=(pos_len - neg_len), random_state=242)
                train_df = pd.concat([train_df, up_sampling_df], ignore_index=True)
        train_df = resample(train_df, replace=False)
        return train_df

    @staticmethod
    def remove_some_model_files(model_args):
        """
        simple-transformer 根据模型参数自动删除模型相关文件
        Args:
            model_args: simple-transformer的args

        Returns:

        """
        import os
        if os.path.isdir(model_args.output_dir):
            cmd = 'rm -rf ' + model_args.output_dir.split('outputs')[0] + 'outputs/'
            os.system(cmd)
        if os.path.isdir(model_args.output_dir.split('outputs')[0] + '__pycache__/'):
            cmd = 'rm -rf ' + model_args.output_dir.split('outputs')[0] + '__pycache__/'
            os.system(cmd)
        if os.path.isdir(model_args.output_dir.split('outputs')[0] + 'cache/'):
            cmd = 'rm -rf ' + model_args.output_dir.split('outputs')[0] + 'cache/'
            os.system(cmd)

    @staticmethod
    def save_dataframe_to_excel(dataframe, excel_path, sheet_name='default'):
        """
        df添加sheet
        Args:
            dataframe: df
            excel_path: path
            sheet_name: sheet

        Returns:

        """
        try:
            from openpyxl import load_workbook
            book = load_workbook(excel_path)
            writer = pd.ExcelWriter(excel_path, engine='openpyxl')
            writer.book = book
        except:
            writer = pd.ExcelWriter(excel_path, engine='openpyxl')

        dataframe.to_excel(writer, sheet_name=sheet_name, index=False)
        writer.save()


if __name__ == '__main__':
    print(Processor.split_data_evenly([0, 2, 3, 4, 5], 3))
