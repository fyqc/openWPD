# (免)登录下载微博图片 ![](https://img.shields.io/badge/python-3.8+-blue.svg)  (No) Login to download Weibo images


批量下载微博用户图片 (CLI)  
Batch Download Weibo User Images (CLI)

## 致谢 Acknowledgments


根源自多年不更新的 Python 项目 [https://github.com/nondanee/weiboPicDownloader](https://github.com/nondanee/weiboPicDownloader/blob/dev/weiboPicDownloader.py)  
Rooted in a Python project that hasn't been updated in years [https://github.com/nondanee/weiboPicDownloader](https://github.com/nondanee/weiboPicDownloader/blob/dev/weiboPicDownloader.py) 

感谢原作者 nondance  
Thanks to the original author, nondance

## openWPD与原代码相比的改进之处  Improvements of openWPD over the original code

+ 修复了失效的图片下载功能
+ Fixed broken image download function    
+ 对原先的代码添加了注释，改变了if代码的结构，通过适量添加变量以增加程序的可读性、可维护性与稳定性
+ Added comments to the original code, changed the structure of the if code, and added variables to increase the readability, maintainability, and stability of the program.
+ 摒弃对Python2与非Windows平台的支持
+ Dropped support for Python2 and non-Windows platforms.
+ 引入了Python3的新特性
+ Introduced new features in Python 3.
+ 大幅减少了库的引用和依赖
+ Significantly reduced library references and dependencies
+ 精简了README文件数量
+ Streamlined the number of README files

## 依赖  Dependencies

```
$ pip install requests
```

## 使用  Usage Instructions

必需参数（任选一）

- `-u user` 用户（昵称或 id）
- `-f file` 用户列表文件（昵称或 id，一个用户占一行）

可选参数

- `-d directory` 图片保存路径（默认值：`./weiboPic`）
- `-s size` 线程池大小（默认值：`20`）
- `-r retry` 最大重试次数（默认值：`2`）
- `-i interval` 请求间隔（默认值：`1`，单位：秒）
- `-c cookie` 登录凭据 (需要 cookie 中的 `SUB` 值)
- `-b boundary` 微博 mid/bid 或日期范围（格式：`id:id` 两者之间，`:id` 之前，`id:` 之后，`id` 指定，`:` 全部）
- `-n name` 命名模板 (标识符: `url`、`index`、`type`、`mid`、`bid`、`date`、`text`、`name`，类似 ["f-Strings"](https://www.python.org/dev/peps/pep-0498/#abstract) 语法)
- `-v` 同时下载秒拍视频
- `-o` 重新下载已保存的文件（默认跳过）

  
```
$ python openwpd.py -h
usage: openwpd [-h] (-u user [user ...] | -f file [file ...])
                          [-d directory] [-s size] [-r retry] [-i interval]
                          [-c cookie] [-b boundary] [-n name] [-v] [-o]

optional arguments:
  -h, --help          show this help message and exit
  -u user [user ...]  specify nickname or id of weibo users
  -f file [file ...]  import list of users from files
  -d directory        set picture saving path
  -s size             set size of thread pool
  -r retry            set maximum number of retries
  -i interval         set interval for feed requests
  -c cookie           set cookie if needed
  -b boundary         focus on weibos in the id range
  -n name             customize naming format
  -v                  download videos together
  -o                  overwrite existing files
```

### 如何从浏览器中取得 `SUB` 的值（以 Chrome 举例）  

1. 转到 https://m.weibo.cn 并登录
2. 右键检查 > Application > Cookies > https://m.weibo.cn
3. 双击 `SUB` 所在行并右键拷贝它的值
4. 将 `SUB` 的值粘贴到命令行窗口，以 `-c <value>` 的方式运行程序


### How to get the value of `SUB` from a browser (Chrome for example)
1. Go to https://m.weibo.cn and log in
2. Right click Check > Application > Cookies > https://m.weibo.cn
3. Double-click on the line where `SUB` is located and right-click to copy its value.
4. Paste the value of `SUB` into a command line window and run the program with `-c <value>`.
