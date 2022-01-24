from setuptools import setup, find_packages  # 这个包没有的可以pip一下

setup(
    name="CSUMMDET",  # 这里是pip项目发布的名称
    version="1.0.23",  # 版本号，数值大的会优先被pip
    keywords=["pip"],
    description="person or car",
    license="MIT Licence",
    author="csu_ywj",
    packages=find_packages(),
    data_files=["mmdet/ops/dcn/deform_conv_cuda.cpython-36m-x86_64-linux-gnu.so",
                "mmdet/ops/dcn/deform_pool_cuda.cpython-36m-x86_64-linux-gnu.so",
                "mmdet/ops/masked_conv/masked_conv2d_cuda.cpython-36m-x86_64-linux-gnu.so",
                "mmdet/ops/nms/nms_cpu.cpython-36m-x86_64-linux-gnu.so",
                "mmdet/ops/nms/nms_cuda.cpython-36m-x86_64-linux-gnu.so",
                "mmdet/ops/nms/soft_nms_cpu.cpython-36m-x86_64-linux-gnu.so",
                "mmdet/ops/roi_align/roi_align_cuda.cpython-36m-x86_64-linux-gnu.so",
                "mmdet/ops/roi_pool/roi_pool_cuda.cpython-36m-x86_64-linux-gnu.so",
                "mmdet/ops/sigmoid_focal_loss/sigmoid_focal_loss_cuda.cpython-36m-x86_64-linux-gnu.so"],
    include_package_data=True,
    platforms="any",
)