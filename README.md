# Radar
Robomaster-Radar
update readme

7.6 update
infer_multithtreading results:
同时启用两个docker做推理，大相机7-10fps，另一个小相机13fps（同时做检测GMM和结果解析）
这时CPU占用接近满，GPU占用19-29。

做了profiling发现绝大多数占用计算资源的地方在deploy的predict和prepocess。一个在4ms左右。

如果不进行GMM运算，可以控制采集帧率来减少卡。10 15 15 15

7.7 update
需要修改unpack函数，根据相机设置阈值。
两个docker，资源占用比较高。可以最多两个GMM，两个推理，每个都有十几帧
全部多线程相机，结果只有8fps。为了减少延时必须降低相机的帧率。