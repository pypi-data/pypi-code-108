'''
    前言:
        当前支持开发语言c/c++,python,java, 简易的中文开发例子,和
        当前支持推理引擎tensorflow(v1,v2) onnxruntime tensorrt,fasttext 注:tensorrt 7,8测试通过(建议8),目前tensorrt只支持linux系统
        当前支持多子图,支持图多输入多输出, 支持pb [tensorflow 1,2] , ckpt [tensorflow] , trt [tensorrt] , fasttext
        当前支持fastertransformer pb [32精度 相对于传统tf,加速1.9x] ,安装 pip install tf2pb  , 进行模型转换
        tf2pb pb模型转换参考: https://pypi.org/project/tf2pb
        模型加密参考test_aes.py,目前支持tensorflow 1 pb模型 , onnx模型 , tensorrt fasttext模型加密
        推荐环境ubuntu系列 centos7 centos8 windows系列
        python (test_py.py) , c语言 (test.c) , java语言包 (nn_sdk.java)
        更多使用参见: https://github.com/ssbuild/nn-sdk

    python 推理demo
    config 字段介绍:
        aes: 加密参考test_aes.py
        engine: 推理引擎 0: tensorflow , 1: onnx , 2: tensorrt 3: fasttext
        log_level: 日志类型 0 fatal , 2 error , 4 warn, 8 info , 16 debug
        model_type: tensorflow 模型类型, 0 pb format , 1 ckpt format
        fastertransformer:  fastertransformer算子选项, 参考 https://pypi.org/project/tf2pb
        ConfigProto: tensorflow 显卡配置
        device_id: GPU id
        engine_version: 推理引擎主版本 tf 0,1  tensorrt 7 或者 8 , fasttext 0需正确配置
        graph: 多子图配置 
            node: 例子: tensorflow 1 input_ids:0 ,  tensorflow 2: input_ids , onnx: input_ids
            dtype: 节点的类型根据模型配置，对于c++/java支持 int int64 long longlong float double str
            shape:  尺寸维度
    更新详情:
    2022-01-21 modify define graph shape contain none and modity demo note.
    2022-01-13 remove a deprecationWarning in py>=3.8
    2022-01-04 modity a tensorflow 2 infer dtype bug
    2021-12-09 graph data_type 改名 dtype , 除fatal info err debug 增加warn
    2021-11-25 修复nn-sdk非主动close, close小bug.
    2021-10-21 修复fastext推理向量维度bug
    2021-10-16 优化 c++/java接口,可预测动态batch
    2021-10-07 增加 fasttext 向量和标签推理
'''
