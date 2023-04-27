class FileList():
    def __new__(cls, sd, *args, **kwargs):
        if sd.isremote:
            cls = RemoteFileList
        else:
            cls = LocalFileList
        self = object.__new__(cls)
        return self

    def __init__(self, *args, **kwargs):
        super(FileList, self).__init__()

    
class LocalFileList(FileList):
    def __init__(self, *args, **kwargs):
        super(LocalFileList, self).__init__(*args, **kwargs)


class RemoteFileList(FileList):
    def __init__(self, *args, **kwargs):
        super(RemoteFileList, self).__init__(*args, **kwargs)

    
