# ydlbq
#### Generates a **youtube-dl** command that downloads a given YouTube video in its best quality, hence the name `youtube-dl best quality == ydlbq`



### Usage

```bash
cd src
chmod u+x ydlbq.py
./ydlbq <URL>
```    

Or you can just run it via calling the interpreter explicitly:    

```bash
python ydlbq.py https://www.youtube.com/watch?v=4PBqpX0_UOc
```

### Some examples: [tests.md](docs/tests.md)


### __IMPORTANT__   

**The repository for the `youtube-dl` project is currently under lockdown!!** This means we won't receive any new updates for a while, and I'm currently facing some periodic communication anomalies with the servers of **youtube.com** that cause `youtube-dl` to fail which makes my script fail.   


E.q:

![h.png](docs/images/youtube-dl_bug_BE_ADVISED.png)

## **To circumvent this anomaly one must run the script multiple times**