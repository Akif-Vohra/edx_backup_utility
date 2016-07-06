#Step 1 : Generate timestamp
import datetime
import os
import boto3
import zipfile
import shutil
from os.path import expanduser
import sys

HOME = expanduser("~")

format = '%Y-%m-%d'
suffix = datetime.datetime.now().strftime(format)

#Step 2: Take mysql backup
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''
MYSQL_BACKUP_DIR = os.path.join(HOME, 'backups/mysql')

if not os.path.exists(MYSQL_BACKUP_DIR):
    os.makedirs(MYSQL_BACKUP_DIR)


#Check if manual backup name is given
if len(sys.argv) > 1:
    print "Manual name for backup provided : {0}".format(sys.argv[1])
    suffix = sys.argv[1]

MYSQL_BACKUP_FILE_NAME = 'backup.sql{0}'.format(suffix)
MYSQL_BACKUP_NAME = os.path.join(MYSQL_BACKUP_DIR, MYSQL_BACKUP_FILE_NAME)

mysql_command = 'mysqldump --user={0} --password={1} --all-databases > {2} --events'.format(MYSQL_USER, MYSQL_PASSWORD, MYSQL_BACKUP_NAME)
print "Taking MYSQL Backup"
os.system(mysql_command)

#Step 3 : Take mongodump
MONGO_BACKUP_DIR = os.path.join(HOME, 'backups/mongo')

if not os.path.exists(MONGO_BACKUP_DIR):
    os.makedirs(MONGO_BACKUP_DIR)

MONGO_BACKUP_FILE_NAME = 'mongo-backup{0}'.format(suffix)
MONGO_BACKUP_NAME = os.path.join(MONGO_BACKUP_DIR, MONGO_BACKUP_FILE_NAME)
mongo_command = 'mongodump -o {0}'.format(MONGO_BACKUP_NAME)
print "Taking Mongo Backup"
os.system(mongo_command)

#Zip the backup
print "Zip Mongo Backup"
mongo_backup_zip_name = os.path.join(MONGO_BACKUP_DIR, 'MONGO_BACKUP_{0}'.format(suffix))
shutil.make_archive(mongo_backup_zip_name, 'zip', MONGO_BACKUP_NAME)

#Zip Media directory
media_zip_name = '/edx/var/edxapp/media'
MEDIA_ZIP_DIR = os.path.join(HOME, 'backups/media')

if not os.path.exists(MEDIA_ZIP_DIR):
    os.makedirs(MEDIA_ZIP_DIR)

ZIP_FILE = os.path.join(MEDIA_ZIP_DIR, 'media_{0}'.format(suffix))

print "Zip media directory"
shutil.make_archive(ZIP_FILE, 'zip', media_zip_name)

#Step 4 : Send to S3
S3_BUCKET_NAME = 'lynx-backup'
s3_client = boto3.client('s3')

#Upload MYSQL to s3
print "Upload mysql backup to s3 {0}".format(MYSQL_BACKUP_FILE_NAME)
s3_client.upload_file(MYSQL_BACKUP_NAME, S3_BUCKET_NAME, MYSQL_BACKUP_FILE_NAME)

#Upload Mongo to s3
print "Upload Mongo to s3 {0}".format(MONGO_BACKUP_FILE_NAME)
s3_client.upload_file('{0}.zip'.format(mongo_backup_zip_name), S3_BUCKET_NAME, MONGO_BACKUP_FILE_NAME)

#Upload media to s3
print "Upload media backup to s3 media_{0}".format(suffix)
s3_client.upload_file('{0}.zip'.format(ZIP_FILE), S3_BUCKET_NAME, 'media_{0}'.format(suffix))
