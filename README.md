# This is a Terminal App
做`Python`開發嘅 IT狗有福了，【Terminal版】香港最大頂級`扮工Mode`不正式地上線了！

![Capture](https://user-images.githubusercontent.com/22520563/206911572-3a93e7f2-60da-4d5a-be24-a8035b8baff9.PNG)

## 安裝
> :warning: `Python >= 3.7` 需要
```bash
pip install -U https://github.com/NewJerseyStyle/LIHKGApp/releases/latest/download/lihkg-0.2-py2.py3-none-any.whl
```

## 運行
```bash
python -m lihkg
```

## Development
### Installation
```bash
git clone https://github.com/NewJerseyStyle/LIHKGApp.git
cd LIHKGApp
git checkout develop
pip install -r requirements.txt
python lihkg.py
```

### Build release
```bash
python setup.py bdist_wheel --universal
```

## Knwon issues
- Only threads in category 5 is showing
- Runs on single thread that UI freeze during network requests
- Image not showing in post
- URLs in post cannot be clicked

### 加速開發
買份沙爹牛畀樓豬，用金錢的味道鞭策樓豬快手修補以上問題。

<a href="https://www.buymeacoffee.com/mercyReleaser"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a Satay beef noodle&emoji=🍜&slug=mercyReleaser&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff" /></a>
