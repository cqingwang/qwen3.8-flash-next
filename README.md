# Qwen3.8-Flash-Next 双机部署

本项目使用当前仓库的 `dspark` 子模块，以官方 `offical/main` 的 vLLM TP2+EP+MTP3 方案在两台 DGX Spark 上部署。外层入口负责同步本地源码和生成 vLLM 配置，不复制模型。

## 固定拓扑

- head：`spark-a`，`chan@192.168.2.180`
- worker：`spark-b`，`chan@192.168.2.161`
- 项目源码部署目录：两台机器均为 `/opt/qwen3.8-flash-next`
- 模型：两台机器均已准备绝对路径 `/opt/models/RadixArk/Qwen3.8-Flash-Next-NVFP4`
- 镜像：两台机器均已准备 `vllm/vllm-openai:qwen38-flash-next`
- API：head 的 `0.0.0.0:8888/v1`

本地工作区是源码源。`install` 会先将项目同步到 head 和 worker，再从 head 调用新 main 的 `dspark/start.sh --launch`；该模式跳过下载和镜像拉取，仅使用 `config.yaml` 配置的绝对模型路径与远端镜像。容器模型路径由 `MODEL_ROOT`/`CONTAINER_MODEL_ROOT` 映射派生。

## 前置条件

在执行部署的机器上准备：

- `ssh` 免密登录 `chan@192.168.2.180` 和 `chan@192.168.2.161`
- `rsync`、Python 3、远端 Docker/NVIDIA Container Toolkit
- 两台机器上的模型目录完整，至少包含 `config.json`、`model.safetensors.index.json` 和 safetensors 权重
- 两台 Spark 的 CX7/RoCE 地址、网卡和 HCA 已在远端 `dspark/.env` 中配置，或通过环境变量覆盖；本项目不根据管理网 IP 猜测 fabric 参数

## 命令

```bash
./deploy.sh --install                # 同步本地源码，停止旧容器并启动已准备好的 vLLM 双机服务
./deploy.sh --restart                # 停止后重新启动
./deploy.sh --stop                   # 停止双机容器
./deploy.sh --status                 # 双机容器、API、GPU 状态
./deploy.sh --live_check             # 转发到 head 做 API 状态检查
./deploy.sh --smoke                  # 执行一次 chat completion
./deploy.sh --logs [head|worker]     # 查看指定节点日志
./deploy.sh --display off|on         # 设置两台机器下次启动的终端/图形 target
./deploy.sh --uninstall              # 停容器并禁用自启，保留源码和模型
./deploy.sh --gen-env                # 生成本地 dspark/.env 拓扑覆盖
./deploy.sh --help
```

真正的镜像、NCCL、PLE patch、worker-first 启动和 readiness 逻辑均位于当前 `dspark/start.sh`；外层部署会调用 `--launch`，不会重新下载模型或拉取已存在的镜像。

## 配置

`config.yaml` 是外层部署 SSOT；其中 `env:` 保存 `dspark/start.sh` 的全部有效环境参数。`deploy.sh --gen-env`/`--install` 由 `program.py` 完整重生成 `dspark/.env`，不会读取或合并旧 `.env`，因此不会出现第二份生效配置。`dspark/.env.sample` 仅作为子模块独立运行时的参考模板；shell 环境变量仍可覆盖 `.env` 中的值。

上下文数值的唯一源头是本文件的 `config.yaml`，`program.py --install`/`--gen-env` 会将其完整生成到 `dspark/.env`。

如果远端直接执行子模块：

```bash
cd /opt/qwen3.8-flash-next/dspark
./start.sh --launch
./stop.sh
```

## 验证边界

本地 `bash -n`、Python 编译和帮助输出只能证明入口没有语法错误；部署完成必须再确认两台容器仍在运行、head `/v1/models` 返回服务模型、`smoke` 成功，以及 head/worker 日志没有启动或 NCCL 错误。
