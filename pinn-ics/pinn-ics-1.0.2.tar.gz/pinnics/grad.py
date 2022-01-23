import tensorflow as tf


class Grad:
    output_key = 'u_'

    def __init__(self, var_type):
        self._fir_grad = set()
        self._sec_grad = set()
        self._result_dict = dict()
        self._var_type = var_type

    def var(self, *char_lst):
        return self._var_type(*char_lst)
    
    def _get_result_key(self, char):
        return f"{self.output_key}{'_'.join(char)}"

    def __call__(self):
        try:
            return self._result_dict[f"{self.output_key}"]
        except:
            return tf.constant(0., dtype=tf.float32)

    def diff(self, *char):
        len_char = len(char)
        key = self._get_result_key(char)

        if key in self._result_dict.keys():
            return self._result_dict[key]
        elif len_char == 1:
            self._fir_grad.add(char)
            return tf.constant(0., dtype=tf.float32)
        elif len_char == 2:
            self._fir_grad.add(char[:1])
            self._sec_grad.add(char)
            return tf.constant(0., dtype=tf.float32)

    def cal_grad(self, model):
        self.reset() 
        
        with tf.GradientTape(persistent=True) as tape_sec:
            sec_watch = {chars: self.var(chars[1]) for chars in self._sec_grad}
            tape_sec.watch([data for data in sec_watch.values()])
            with tf.GradientTape(persistent=True) as tape_fir:
                fir_watch = {chars: self.var(chars[0]) for chars in self._fir_grad}
                tape_fir.watch([data for data in fir_watch.values()])
                input_var = self._var_type()
                output = model(input_var)
                self._result_dict[self.output_key] = output

            for char, data in fir_watch.items():
                key = self._get_result_key(char)
                grad = tape_fir.gradient(output, data)
                self._result_dict[key] = grad
            
        for char, data in sec_watch.items():
            source_key = self._get_result_key(char[:1])
            key = self._get_result_key(char)
            source = self._result_dict[source_key] 
            grad = tape_sec.gradient(source, data)
            self._result_dict[key] = grad

        del tape_fir
        del tape_sec

    def reset(self):
        self._result_dict = dict()
