<h1 align="center">GooseGooseDuckHelper</h1>

## 使用指南

### 安装

1.使用打包版本（仅支持非房主）

```
https://wwul.lanzoue.com/inzYj0lxlxla
```

2.使用源码版本

```
拉取代码并安装依赖
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple numpy opencv-python Pillow PyAutoGUI pypiwin32 pywin32
```
**如果是房主 需要将isHost设置为1**

### 运行

1. 窗口化游戏并调整分辨率至 1280x720
2. 确保当前在大厅中（准备界面）或者在游戏内
3. 运行run.py或run.exe
4. 在1秒内切回游戏
5. 中途不要切出游戏，想关闭则直接ctrl+c或者右上角叉

### 推荐使用方法

#### 单人

- 找一个仅做任务的房开启程序即可

#### 多人

- 房主将isHost设置为1

推荐设置：

- 地图为地下室

- 6人以上（1个掉线仍可开游戏）
 
- 关闭随机出生位置

- 任务数量设置为少

## 特点

1. 支持普通模式地下室地图自动做任务
2. 自动寻路目前不会卡住

## 存在问题

1. 钓鱼任务失败率高
2. 三张牌蒙特只会固定选最左边的牌
3. 这两个任务失败率高，可能会导致弹出挂机提示，需要手动恢复
4. 如果有人开饭，不会自动跳过，结束后出生在随机位置会导致卡死
5. 游戏断线后无法自动重连
6. 鸭、中立或者死后不会自动做伪装任务只会随机走动
7. 走路控制不够精准，容易卡顿或绕圈 

以上问题导致效率大概只有手动的一半

## 交流群

[![交流群](https://i.328888.xyz/2023/01/27/jiJ8L.png)](https://i.328888.xyz/2023/01/27/jiJ8L.png)


## Development
地图存储在map.txt

第一行为点数n，边数m

下面n行描述点的id和点的x,y坐标

接下来m行描述边连接的两个点编号

[![Development](https://i.328888.xyz/2023/01/27/jie8N.png)](https://imgloc.com/i/jie8N)