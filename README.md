# Qwen3.8-Flash-Next 双机部署

本项目使用当前仓库的 `dspark` 子模块，以 SGLang 在两台 DGX Spark 上进行 TP=2 部署。外层命令风格与 `../deepseek-flash/deploy.sh` 对齐，但不复用 DeepSeek 的运行时脚本。

## 固定拓扑

- head：`spark-a`，`chan@192.168.2.180`
- worker：`spark-b`，`chan@192.168.2.161`
- 项目源码部署目录：两台机器均为 `/opt/qwen3.8-flash-next`
- 模型目录：两台机器均为 `/opt/models/RadixArk/Qwen3.8-Flash-Next-NVFP4`
- 容器模型目录：`/models/RadixArk/Qwen3.8-Flash-Next-NVFP4`；服务名自动取模型目录相对 `/opt/models` 的路径，即 `RadixArk/Qwen3.8-Flash-Next-NVFP4`
- API：head 的 `0.0.0.0:8888/v1`

本地工作区是源码源。`install` 会先将项目同步到 head 和 worker，再从 head 调用 `dspark/start.sh`。模型不会复制进项目目录；子模块的本地模型模式会把 head 的模型目录断点 rsync 到 worker，并将 `/opt/models` 以只读方式挂载到容器 `/models`，保留作者与模型目录层级。服务名由实际 `MODEL_DIR` 自动生成，不再单独维护别名。

## 前置条件

在执行部署的机器上准备：

- `ssh` 免密登录 `chan@192.168.2.180` 和 `chan@192.168.2.161`
- `rsync`、Python 3、远端 Docker/NVIDIA Container Toolkit
- 两台机器上的模型目录完整，至少包含 `config.json`、`model.safetensors.index.json` 和 safetensors 权重
- 两台 Spark 的 CX7/RoCE 地址、网卡和 HCA 已在远端 `dspark/.env` 中配置，或通过环境变量覆盖；本项目不根据管理网 IP 猜测 fabric 参数

## 命令

```bash
./deploy.sh --doctor                 # 远端双机环境、模型、GPU、RoCE、端口检查
./deploy.sh --install                # 同步源码，同步模型，构建镜像并启动
./deploy.sh --fetch                  # 使用子模块的 download 动作；本地模型已存在时只校验/同步
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

首次安装建议先执行 `doctor`。真正的镜像构建、QSA SM121 fallback、NCCL、NEXTN speculative decoding、模型校验、worker-first 启动和 readiness 等逻辑均位于当前 `dspark/start.sh`，可单独阅读其 `--help` 与 `dspark/README.md`。

## 配置

`config.yaml` 是外层部署 SSOT；其中 `env:` 保存 `dspark/start.sh` 的全部有效环境参数。`deploy.sh --gen-env`/`--install` 由 `program.py` 完整重生成 `dspark/.env`，不会读取或合并旧 `.env`，因此不会出现第二份生效配置。`dspark/.env.example` 仅作为子模块独立运行时的参考模板；shell 环境变量仍可覆盖 `.env` 中的值。

如果远端直接执行子模块：

```bash
cd /opt/qwen3.8-flash-next/dspark
./start.sh doctor
./start.sh serve
./start.sh status
./start.sh smoke
./start.sh stop
```

## 验证边界

本地 `bash -n`、Python 编译和帮助输出只能证明入口没有语法错误；部署完成必须再确认两台容器仍在运行、head `/v1/models` 返回服务模型、`smoke` 成功，以及 head/worker 日志没有启动或 NCCL 错误。
