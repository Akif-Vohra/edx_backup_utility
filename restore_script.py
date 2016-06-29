import boto3
import datetime
import sys

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


s3_client.download_file(S3_BUCKET_NAME, MYSQL_BACKUP_TO_DOWNLOAD, MYSQL_BACKUP_TO_DOWNLOAD)
s3_client.download_file(S3_BUCKET_NAME, MONGO_BACKUP_TO_DOWNLOAD, MONGO_BACKUP_TO_DOWNLOAD)
s3_client.download_file(S3_BUCKET_NAME, MEDIA_BACKUP_TO_DOWNLOAD, MEDIA_BACKUP_TO_DOWNLOAD)


    
    
