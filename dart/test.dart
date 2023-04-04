import "dart:io";

Future main() async {
  var dir = Directory('/sdcard/');

  try {
    var dirList = dir.list();
    await for (FileSystemEntity f in dirList) {
      if (f is File) {
        print(['Found file ${f.path}', await f.stat()]);
      } else if (f is Directory) {
        print(['Found dir ${f.path}', await f.stat()]);
      }
    }
  } catch (e) {
    print(e.toString());
  }
}