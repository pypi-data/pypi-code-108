import logging
import time

from spalipy import Spalipy
from test_spalipy import generate_image, generate_mask

fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=fmt, level=logging.INFO)

time.sleep(1)
logging.info("Started")
source_data = generate_image(translate=(20, -20), rotate=60, scale=1.2, seed=1, num_sources=50,)
source_mask = generate_mask()
template_data = generate_image(num_sources=50)
time.sleep(1)
logging.info("Constructing Spalipy")
sp = Spalipy(
    [source_data, source_data, source_data],
    source_mask=[source_mask, source_mask, source_mask],
    template_data=template_data,
    min_n_match=10,
    sub_tile=1,
    spline_order=0,
)
time.sleep(1)
logging.info(f"Make source quadlist")
sp.make_source_quadlist()
time.sleep(1)
logging.info(f"Make template quadlist")
sp.make_template_quadlist()

time.sleep(0.3)
logging.info(f"Fit affine transform")
sp.fit_affine_transform()
time.sleep(0.3)
logging.info(f"Fit spline transform")
sp.fit_spline_transform()

for i in range(3):
    time.sleep(0.5)
    logging.info(f"Transform data {i}")
    sp._transform_data(i)
