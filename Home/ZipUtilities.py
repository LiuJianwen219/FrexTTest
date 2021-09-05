# -*- coding: UTF-8 -*-
import zipfile
import os
import zipstream


class ZipUtilities(object):
    zip_file = None

    def __init__(self):
        self.zip_file = zipstream.ZipFile(mode='w', compression=zipstream.ZIP_BZIP2)

    def toZip(self, file, name):
        if os.path.isfile(file):
            self.zip_file.write(file, arcname=os.path.basename(file))
        else:
            self.addFolderToZip(file, name)

    def addFolderToZip(self, folder, name):
        for file in os.listdir(folder):
            full_path = os.path.join(folder, file)
            if os.path.isfile(full_path):
                self.zip_file.write(full_path, arcname=os.path.join(name, os.path.basename(full_path)))
            elif os.path.isdir(full_path):
                self.addFolderToZip(full_path, os.path.join(name, os.path.basename(full_path)))

    def close(self):
        if self.zip_file:
            self.zip_file.close()



# 使用说明：
# utilities = ZipUtilities()
# for file_obj in file_objs:
#    tmp_dl_path = os.path.join(path_to, filename)
#    utilities.toZip(tmp_dl_path, filename)
# #utilities.close()
# response = StreamingHttpResponse(utilities.zip_file, content_type='application/zip')
# response['Content-Disposition'] = 'attachment;filename="{0}"'.format("下载.zip")
# return response