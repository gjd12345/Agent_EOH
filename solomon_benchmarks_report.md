# Solomon Benchmarks 基准运行记录（Archive_extracted）

## 1. 数据集与输入

- 数据集目录：`C:\Users\24294\.trae\Agent_EOH\solomon_benchmarks`
- 本次实际跑的输入（程序读入的 JSON）目录：`C:\Users\24294\.trae\Agent_EOH\Archive_extracted\solomon_benchmark`
  - 文件模式：`rc1*.json`（本次实际包含 rc101–rc108）
- 批跑脚本： [run_benchmarks.py](file:///c:/Users/24294/.trae/Agent_EOH/Archive_extracted/run_benchmarks.py)
- 可执行程序入口： [main.go](file:///c:/Users/24294/.trae/Agent_EOH/Archive_extracted/main.go)
- 路径/时间窗求解逻辑： [routing.go](file:///c:/Users/24294/.trae/Agent_EOH/Archive_extracted/routing.go)

## 2. 运行环境

- Go：`go1.25.0 windows/amd64`
- Python：`3.14.2`
- 工作目录：`C:\Users\24294\.trae\Agent_EOH\Archive_extracted`

## 3. 运行命令

在 `C:\Users\24294\.trae\Agent_EOH\Archive_extracted` 下执行：

```bash
go build -o mainbin.exe main.go routing.go
python run_benchmarks.py
```

单个实例调试示例：

```bash
./mainbin.exe ./solomon_benchmark/rc102.json 1000000
```

## 4. 关键修改（为保证可编译 & 可批跑）

### 4.1 修复 `GenRoute()` 缺失导致的编译错误

现象：

- `go build` 报错：`dispatch.Assigns[ii].GenRoute undefined`
- 触发点：在插单/移单后需要重新生成路径（例如 [main.go:L345-L402](file:///c:/Users/24294/.trae/Agent_EOH/Archive_extracted/main.go#L345-L402) 中的多处调用）

处理：

- 在 `Assign` 上补齐 `GenRoute()` 方法（负责：
  1) 重算 `ReqCode`；
  2) 调用 `RoutingTS` 得到 `RoutingResult`；
  3) 设置下一站 `NextSta` 与到达时间 `NextTime`）
- 实现位置： [main.go:L107-L125](file:///c:/Users/24294/.trae/Agent_EOH/Archive_extracted/main.go#L107-L125)

### 4.2 修复批跑时 `StaIndexes` 越界导致的运行崩溃

现象：

- `rc102.json` 等实例会 panic：
  - `panic: runtime error: index out of range [8] with length 8`
  - 栈指向 `Assign.AddShip()` 写入 `StaIndexes[StaIndexesLen]`（见 [main.go:L201-L227](file:///c:/Users/24294/.trae/Agent_EOH/Archive_extracted/main.go#L201-L227)）

原因：

- `StaIndexes` 数组长度由 `MAXSHIPS` 控制，但原值为 8，批跑实例插入订单数超过 8 会越界。

处理：

- 将 `MAXSHIPS` 调整为 64： [main.go:L21-L29](file:///c:/Users/24294/.trae/Agent_EOH/Archive_extracted/main.go#L21-L29)

## 5. 基准输出与结果汇总

### 5.1 输出文件

- 汇总输出（CSV 格式 `filename,cost`）：
  - [final_result.txt](file:///c:/Users/24294/.trae/Agent_EOH/Archive_extracted/final_result.txt)
- 程序在 stdout 最后会打印 `final cost <number>`：
  - 代码位置： [main.go:L888-L915](file:///c:/Users/24294/.trae/Agent_EOH/Archive_extracted/main.go#L888-L915)

### 5.2 本次运行结果（rc101–rc108）

| instance | final cost |
|---|---:|
| rc101.json | -2 |
| rc102.json | 173.7608984602312 |
| rc103.json | 167.9299465653859 |
| rc104.json | 110.93088947284846 |
| rc105.json | 226.13088578474796 |
| rc106.json | -2 |
| rc107.json | 241.51765762472294 |
| rc108.json | 121.31592276570288 |

## 6. 备注

- `rc101.json` 与 `rc106.json` 出现 `final cost = -2`，表示当前求解流程在这两个实例下最终汇总结果为负值；若需要进一步定位（不可行约束/路线为空/累计里程转移等），可针对这两个实例单独开启更多运行输出并分析 `Assign`/`Dispatch` 的状态变化路径。

