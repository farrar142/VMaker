pyinstaller --onefile vm.py
rm -f vm.exe
cp dist/vm.exe ./vm.exe
git add . && git commit -m "build" && git push origin master