UPLOAD_FOLDER      = 'storageFiles'
VERSION            = "1.3.2 beta"
ALLOWED_EXTENSIONS = ['docx', 'pdf', 'xlsx', 'xlsm', 'xls', 'html', 'txt','csv']

import os

path = os.path.join(os.getcwd(), UPLOAD_FOLDER)
