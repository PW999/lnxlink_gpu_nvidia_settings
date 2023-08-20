import os
import re
import logging
from shutil import which

GPU_ID=0
GPU_QUERY_NAME=1
GPU_NAME=2
IGNORE_WARNINGS = []
'''
    A list of metric names for which we don't want to log a warning everytime it fails.
    This list will be automatically filled in once failures are detected.
'''
METRICS_DATA = {
    'GPUCoreTemp': {
        'regex': re.compile("\s+Attribute 'GPUCoreTemp' \(.*\): (?P<data>\d+)\.")
    }, 
    'GPUUtilization': {
        'regex': re.compile("\s+Attribute 'GPUUtilization' \(.*\): graphics=(?P<data>\d+),.*")
    },
    'UsedDedicatedGPUMemory': {
        'regex': re.compile("\s+Attribute 'UsedDedicatedGPUMemory' \(.*\): (?P<data>\d+)\.")
    },
    'TotalDedicatedGPUMemory' : {
        'regex': re.compile("\s+Attribute 'TotalDedicatedGPUMemory' \(.*\): (?P<data>\d+)\.")
    }
}

logger = logging.getLogger("lnxlink")

class Addon():

    def __init__(self, lnxlink):
        """Setup addon, discover all GPUs"""
        self.name = 'GPU'
        if which("nvidia-settings") is None:
            logger.warning("nvidia-settings was not found on the PATH")
        self.gpu_ids = self.__get_gpus()

        if len(self.gpu_ids) == 0:
            logger.warning("No GPU's detected by nvidia-settings")

    def __get_gpus(self):
        """Returns a tuple with GPU_ID (number), GPU_QUERY_NAME ([gpu:X]) and GPU_NAME (e.g. NVIDIA GeForce GTX 770)"""
        gpus_raw = os.popen(f'{which("nvidia-settings")} -q gpus').read()
        return re.findall("\s+\[([0-9+])\] .*(\[.*\]) \((.*)\)", gpus_raw)

    def __generate_nvidia_settings_cmd(self, gpu_query_name: str):
        """Generates the command for nvidia-settings to query all GPU data (non terse to make sure we don't mix metrics)"""
        cmd = f'{which("nvidia-settings")}'
        for metric_name in METRICS_DATA.keys():
            cmd += f' -q \'{gpu_query_name}/{metric_name}\''
        return cmd

    def __get_metrics(self, gpu_query_name: str):
        """Uses a single nvidia-settings call to get the metrics defined in METRICS_DATA"""
        metrics = {}

        metrics_raw = os.popen(self.__generate_nvidia_settings_cmd(gpu_query_name)).read()
        for metric_name, data in METRICS_DATA.items():
            match = data['regex'].search(metrics_raw)
            if match:
                metrics[metric_name] = float(match.group('data'))
            else:
                metrics[metric_name] = 0
                if metric_name not in IGNORE_WARNINGS:
                    logger.warning(f'No match found for metric {metric_name}')
                    IGNORE_WARNINGS.append(metric_name) # if this fails once, it'll probably always fail, don't log this every time
        return metrics

    def get_info(self):
        gpus = {}
        for gpu in self.gpu_ids:
            gpu_id = gpu[GPU_ID]
            metrics = self.__get_metrics(gpu[GPU_QUERY_NAME])
            gpus[f"nvidia_{gpu_id}"] = {
                "name": gpu[GPU_NAME],
                "Memory usage": float(round(100 * (metrics['UsedDedicatedGPUMemory']/metrics['TotalDedicatedGPUMemory']) , 0)),
                "load": min(100, round(metrics['GPUUtilization'], 1)),
                "Temperature": metrics['GPUCoreTemp'],
            }
        return gpus

    def exposed_controls(self):
        discovery_info = {}
        for gpu in self.gpu_ids:
            gpu_id = gpu[GPU_ID]
            discovery_info[f"GPU NVIDIA {gpu_id}"] = {
                "type": "sensor",
                "icon": "mdi:expansion-card-variant",
                "unit": "%",
                "state_class": "measurement",
                "value_template": f"{{{{ value_json.nvidia_{gpu_id}.load }}}}",
                "attributes_template": f"{{{{ value_json.nvidia_{gpu_id} | tojson }}}}",
                "enabled": True,
            }
        return discovery_info
