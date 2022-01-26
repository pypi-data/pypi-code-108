import pathlib
import tempfile
import json
import logging
import re
import glob
from typing import Dict
from .qemu import QMP
from .environment import load_conf
from ..helpers.logger import log

def take_snapshot(config :pathlib.Path) -> None:
	job_running = True

	def parse_job(qmp :QMP, json_data :Dict[str, Dict[str, str]]) -> None:
		nonlocal job_running

		log(f"drive-mirror job status changed: {json_data!r}", level=logging.DEBUG)
		if 'data' not in json_data or 'status' not in json_data["data"]:
			return

		if json_data["data"]["status"] == "ready":
			log(f"drive-mirror status is set to ready, committing to the new block device!", level=logging.INFO, fg="yellow")
			qmp.send(bytes(json.dumps({
				"execute": "block-job-complete",
				"arguments": {
					"device": json_data["data"]["id"]
				}
			}), 'UTF-8'))
		elif json_data["data"]["status"] == "concluded":
			job_running = False
		elif json_data["data"]["status"] == "aborting":
			raise SystemError(f"Could not complete snapshot: {json_data}")

	configuration = load_conf(config)

	log(f"Preparing snapshot for machine configuration {config}")

	for obj in configuration["pcie_slave_devices"]:
		blockdevice = obj[1]

		if 'format=qcow2' in blockdevice:
			info = re.findall('file=.*?,|id=.*$', blockdevice)
			if not len(info) == 2:
				raise ValueError(f"Could not locate file=  and id= for blockdevice: {blockdevice}")

			blockdevice_path, blockdevice_id = pathlib.Path(info[0].split('=', 1)[1]), info[1].split('=', 1)[1]

			highest_snap_id = -1
			for filename in glob.glob(f"{blockdevice_path.parent}/{blockdevice_path.stem}-snap*.qcow2"):
				if int(found_id := filename[len(f"{blockdevice_path.parent}/{blockdevice_path.stem}-snap"):].rsplit('.')[0]) > highest_snap_id:
					highest_snap_id = int(found_id)

			highest_snap_id += 1

			with QMP(pathlib.Path(f"{tempfile.gettempdir()}/{config.stem}.qmp")) as qmp:
				qmp.register('JOB_STATUS_CHANGE', parse_job)

				qmp.send(bytes(json.dumps({
					"execute": "drive-mirror",
					"arguments": {
						"device": blockdevice_id,
						"job-id": f"mirror-{blockdevice_id}",
						"target": f"{blockdevice_path.parent}/{blockdevice_path.stem}-snap{highest_snap_id}.qcow2",
						"sync": "full"
					}
				}), 'UTF-8'))

				while qmp.poll() and job_running:
					qmp.recv()

					# qmp.send(bytes(json.dumps({
					# 	"execute": "query-block-jobs",
					# 	"arguments": {}
					# }), 'UTF-8'))

				log(f"drive-mirror is fnished and new block device backing file is {blockdevice_path.parent}/{blockdevice_path.stem}-snap{highest_snap_id}.qcow2", level=logging.INFO, fg="green")