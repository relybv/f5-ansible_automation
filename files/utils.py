from logging.handlers import SysLogHandler
import logging
import configargparse
import sys

def initargs(): 
    parser = configargparse.ArgParser(description='This script read from configuration database and add citrix customers to F5 load balencer(s).')
    parser.add_argument('--config',is_config_file=True,help='config file path',env_var='F5_CONGIG',required=False)
    parser.add_argument('--verbose',help='add verbose messages',env_var='F5_VERBOSE',action='store_true')
    parser.add_argument('--logdest',help='path or (default) console',env_var='F5_LOGDEST',default='console')
    parser.add_argument('--noop',help='no operation',env_var='F5_NOOP',action='store_true')
    parser.add_argument('--f5host',help='F5 host to override host from database',env_var='F5_HOST',default='undef')
    parser.add_argument('--f5hostha',help='F5 HA host to override host from database',env_var='F5_HOSTHA',default='undef')
    parser.add_argument('--dbip',help='database serverip address',env_var='F5_DBIP',default='127.0.0.1')
    parser.add_argument('--dbuser',help='database user',env_var='F5_DBUSER',required=True)
    parser.add_argument('--dbpasswd',help='database password',env_var='F5_DBPASSWD',required=True)
    parser.add_argument('--db',help='database',env_var='F5_DB',default='f5')
    parser.add_argument('--lbuser',help='loadbalancer user',env_var='F5_LBUSER',required=True)
    parser.add_argument('--lbpasswd',help='loadbalancer password',env_var='F5_LBPASSWD',required=True)
    parser.add_argument('--delete',help='delete resources marked in database',env_var='F5_DELETE',action='store_true')
    parser.add_argument('--posttests',help='execute post tests, combine with --noop to execute post test only',env_var='F5_POSTTESTS',action='store_true')
    parser.add_argument('--all',help='deploy all entries in db',env_var='F5_ALL',action='store_true')
    parser.add_argument('--planned',help='deploy planned changes',env_var='F5_PLANNED',action='store_true',default=True)
    parser.add_argument('--list',help='used by ansible',action='store_true')
    return parser

def initlogger(args):
    logger = logging.getLogger()
    format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger.removeHandler(sys.stdout)
    ch = logging.StreamHandler(sys.stderr)
    ch.setFormatter(format)
    logger.addHandler(ch)
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARN)

    if args.logdest != 'console':
        fh = handlers.RotatingFileHandler(args.logdest, maxBytes=(1048576*5), backupCount=7)
        fh.setFormatter(format)
        logger.addHandler(fh)
    return logger

