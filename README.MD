# LNXLink gpu_nvidia_settings

This module for [LNXLink](https://github.com/bkbilly/lnxlink) is a drop-in replacement for the bundeled GPU module.
It uses `nvidia-settings` instead of `nvidia-smi` which might give better results on some (older) Nvidia GPUs.

## How to use
You'll only need [gpu_nvidia_settings.py](gpu_nvidia_settings.py). There's no limitations on where you place the file,
it might depend on where and how you've installed [LNXLink](https://github.com/bkbilly/lnxlink), but it'll work fine
even if you place it somewhere in your home directory.

Edit your LNXLink configuration file (see [Config file location](https://bkbilly.gitbook.io/lnxlink/setup)) and add the following configuration:

```yaml
custom_modules:
  - <PATH_TO_THE_MODULE>/gpu_nvidia_settings.py

```

If you manually defined which modules LNXLink should use, make sure to remove `gpu` from the list. If instead you've loaded all modules by default,
add the following lines to your LNKLink configuration:

```yaml
exclude:
 - gpu
```

# Troubleshooting
Check if nvidia-settings can detect your GPU:

```shell
nvidia-settings -q 'gpus'
```

The output should look something like this:

```
1 GPU on PWManjaro:0

    [0] PWManjaro:0[gpu:0] (NVIDIA GeForce GTX 770)

      Has the following names:
        GPU-0
```

Using the gpu id (`[gpu:0]`) you can query the metrics from nvidia-settings using the following command

```shell
nvidia-settings -q '[gpu:0]/GPUUtilization' -q '[gpu:0]/GPUCoreTemp' -q '[gpu:0]/UsedDedicatedGPUMemory' -q '[gpu:0]/TotalDedicatedGPUMemory'
```

The output should look something like this:

```
  Attribute 'GPUUtilization' (PWManjaro:0[gpu:0]): graphics=1, memory=1, video=0, PCIe=0

  Attribute 'GPUCoreTemp' (PWManjaro:0[gpu:0]): 38.
    'GPUCoreTemp' is an integer attribute.
    'GPUCoreTemp' is a read-only attribute.
    'GPUCoreTemp' can use the following target types: X Screen, GPU.

  Attribute 'UsedDedicatedGPUMemory' (PWManjaro:0[gpu:0]): 775.
    'UsedDedicatedGPUMemory' is an integer attribute.
    'UsedDedicatedGPUMemory' is a read-only attribute.
    'UsedDedicatedGPUMemory' can use the following target types: GPU.

  Attribute 'TotalDedicatedGPUMemory' (PWManjaro:0[gpu:0]): 1991.
    'TotalDedicatedGPUMemory' is an integer attribute.
    'TotalDedicatedGPUMemory' is a read-only attribute.
    'TotalDedicatedGPUMemory' can use the following target types: GPU.

```

You can also check the logs of LNXLink to further troubleshoot issues
```shell
journalctl --user -u lnxlink 
```