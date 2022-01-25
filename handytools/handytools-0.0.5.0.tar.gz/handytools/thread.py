import math
from multiprocessing import Pool
from tqdm.std import tqdm
from functools import partial


class MultiProcess(object):
    def __init__(self, *args):
        super(MultiProcess, self).__init__(*args)

    def execute(self, function, batch_data: list, i: int, kwargs):
        """execute function

        Args:
            function ([type]): a function contains two parameters: data(list), **kwargs:(dict)
            batch_data (list): a list of data
            i (int): thread index
            kwargs (dict): a dict of parameters

        Returns:
            output (list): a list of results
        """
        results = []
        inside_batch = kwargs.get("inside_batch", 1)
        for idx in tqdm(range(math.ceil(len(batch_data)/inside_batch)), desc="%d is processing..." % i):
            cur_batch = batch_data[idx*inside_batch:(idx+1)*inside_batch]
            kwargs["i"] = i
            result = function(cur_batch, **kwargs)
            del kwargs["i"]
            results.append(result)
        return results

    def apply_async(self, function, data: list, process_num=10, **kwargs):
        """apply asynchronous thread to process data

        Args:
            function ([type]): a function contains two parameters: data:list, **kwargs:dict
            data (list): a list of data
            process_num (int, optional): threed num. Defaults to 10.


        Returns:
            output (list): a list of results

        >>> def get_num(data, **kwargs):
                return [data[0][-1]]*2
        >>> data = ["今天是星期%d" % (i+1) for i in range(7)]*2
        >>> multi_process = MultiProcess()
        >>> output = multi_process.apply_async(get_num, data, process_num=10)
        >>> print(output)
        [['1', '1'], ['2', '2'], ['3', '3'], ['4', '4'], ['5', '5'], ['6', '6'], ['7', '7'], ['1', '1'], ['2', '2'], ['3', '3'], ['4', '4'], ['5', '5'], ['6', '6'], ['7', '7']]
        """
        pool = Pool(process_num)
        output_pool, output = [], []
        batch_size = math.ceil(len(data)/process_num)
        for i in range(process_num):
            batch_datum = data[i*batch_size:(i+1)*batch_size]
            output_pool.append(pool.apply_async(
                func=self.execute, args=(function, batch_datum, i, kwargs)))
        for i in output_pool:
            output.extend(i.get())
        return output

    def map(self, function, data, process_num=10, **kwargs):
        """synchronization multi-thread to process data

        Args:
            function ([type]): a function contains two parameters: data(single data), **kwargs:dict
            data (list): a list of data
            process_num (int, optional): threed num. Defaults to 10.

        Returns:
            output (list): a list of results

        >>> def get_num(data, **kwargs):
                return data[-1]
        >>> multi_process = MultiProcess()
        >>> output = multiprocessfun.map(function=get_num, data=data, process_num=10)
        >>> print(output)
        ['1', '2', '3', '4', '5', '6', '7', '1', '2', '3', '4', '5', '6', '7']
        """
        pool = Pool(process_num)
        #'Ordered results using pool.map() --- will block till complete:'
        output = pool.map(partial(function, **kwargs), data)
        return output

    def destory(self):
        self.pool.close()
        self.pool.join()


if __name__ == '__main__':
    def get_num(data, **kwargs):
        return data[-1]

    multiprocessfun = MultiProcess()
    data = ["今天是星期%d" % (i+1) for i in range(7)]*2
    output = multiprocessfun.map(
        function=get_num, data=data, process_num=10)
    print(output)
