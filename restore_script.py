import boto3
import datetime
import sys
import os
import distutils.dir_util

S3_BUCKET_NAME = 'lynx-backup'
s3_client = boto3.client('s3')

format = '%Y-%m-%d'
backup_suffix = datetime.datetime.now().strftime(format)

try:
    backup_suffix = sys.argv[1]
except IndexError as e:
    print "Manual name not provided... Will backup the latest backup taken on {0} midnight".format(backup_suffix)
else:
    print "Will backup the backups with a prefix {0}".format(backup_suffix)


move_ahead = raw_input('Do you want to proceed? This step will overwrite local DBs and is irreversible! Press Y to continue N to exit : ')
if move_ahead != 'Y':
    print "Exiting.."
    sys.exit()

MYSQL_BACKUP_TO_DOWNLOAD = 'backup.sql{0}'.format(backup_suffix)
MONGO_BACKUP_TO_DOWNLOAD = 'mongo-backup{0}'.format(backup_suffix)
MEDIA_BACKUP_TO_DOWNLOAD = 'media_{0}'.format(backup_suffix)

print MYSQL_BACKUP_TO_DOWNLOAD
print MONGO_BACKUP_TO_DOWNLOAD
print MEDIA_BACKUP_TO_DOWNLOAD

try:
    print "Downloading MYSQL Backup"
    s3_client.download_file(S3_BUCKET_NAME, MYSQL_BACKUP_TO_DOWNLOAD, MYSQL_BACKUP_TO_DOWNLOAD)

    print "Downloading Mongo Backup"
    s3_client.download_file(S3_BUCKET_NAME, MONGO_BACKUP_TO_DOWNLOAD, '{0}.zip'.format(MONGO_BACKUP_TO_DOWNLOAD))
    
    print "Downloading Media Backup"
    s3_client.download_file(S3_BUCKET_NAME, MEDIA_BACKUP_TO_DOWNLOAD, '{0}.zip'.format(MEDIA_BACKUP_TO_DOWNLOAD))

except Exception as e:
    print "Exception occured while fetching the backup from S3, Backup with specified date/name might not be available on S3"
    print "Error : {0}".format(e)
    sys.exit()


MYSQL_BACKUP_PATH = os.path.join(os.getcwd(), MYSQL_BACKUP_TO_DOWNLOAD)
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''
MYSQL_RESTORE_COMMAND = 'mysql --user={0} --password={1} < {2}'.format(MYSQL_USER, MYSQL_PASSWORD, MYSQL_BACKUP_PATH)


MONGO_BACKUP_ZIP_PATH = os.path.join(os.getcwd(), '{0}.zip'.format(MONGO_BACKUP_TO_DOWNLOAD))
import zipfile
MONGO_BACKUP_DIR_PATH = os.path.join(os.getcwd(), 'mongo')
mongo_zipfile = zipfile.ZipFile(MONGO_BACKUP_ZIP_PATH)

print "Extracting mongo backup"
mongo_zipfile.extractall(MONGO_BACKUP_DIR_PATH)

MONGO_RESTORE_COMMAND = 'mongorestore -drop {0}'.format(MONGO_BACKUP_DIR_PATH)


MEDIA_BACKUP_ZIP_PATH = os.path.join(os.getcwd(), '{0}.zip'.format(MEDIA_BACKUP_TO_DOWNLOAD))
MEDIA_BACKUP_DIR_PATH = os.path.join(os.getcwd(), 'media')
media_zipfile = zipfile.ZipFile(MEDIA_BACKUP_ZIP_PATH)

print "Exctracting Media backup"
media_zipfile.extractall(MEDIA_BACKUP_DIR_PATH)


print "BACKUP MYSQL"
os.system(MYSQL_RESTORE_COMMAND)

print "BACKUP MONGO"
os.system(MONGO_RESTORE_COMMAND)

print "Backup MEDIA"
distutils.dir_util.copy_tree(MEDIA_BACKUP_DIR_PATH, '/edx/var/edxapp/media')

